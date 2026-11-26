from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from launcher_case import LAUNCH, STUBS

CLEAN = LAUNCH.parent / "clean-worktree.sh"


@unittest.skipUnless(shutil.which("lsof"), "lsof is not on PATH, so clean-worktree.sh cannot run")
class CleanWorktreeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        bin_dir = self.tmp / "bin"
        bin_dir.mkdir()
        (bin_dir / "docker").symlink_to(STUBS / "docker")
        (self.tmp / "gitconfig").write_text("")
        self.containers = self.tmp / "containers"
        self.containers.write_text("")
        self.docker_log = self.tmp / "docker.log"
        self.docker_log.touch()
        self.env = dict(
            os.environ,
            PATH=f"{bin_dir}:{os.environ['PATH']}",
            HOME=str(self.tmp),
            GIT_CONFIG_GLOBAL=str(self.tmp / "gitconfig"),
            GIT_CONFIG_NOSYSTEM="1",
            GIT_AUTHOR_NAME="Test",
            GIT_AUTHOR_EMAIL="test@example.com",
            GIT_COMMITTER_NAME="Test",
            GIT_COMMITTER_EMAIL="test@example.com",
            STUB_DOCKER_CONTAINERS=str(self.containers),
            STUB_DOCKER_LOG=str(self.docker_log),
        )
        self.root = self.tmp / "repo"
        self.git("init", "-q", "-b", "main", str(self.root))
        (self.root / ".gitignore").write_text(".venvs/\nscratch/\n")
        self.git("-C", str(self.root), "add", ".")
        self.git("-C", str(self.root), "commit", "-q", "-m", "seed")
        self.git("-C", str(self.root), "branch", "f")

    def git(self, *args: str) -> str:
        return subprocess.run(["git", *args], env=self.env, capture_output=True, text=True, check=True, timeout=30).stdout

    def add_worktree(self, path: Path, *, branch: str, base: str = "f") -> Path:
        self.git("-C", str(self.root), "worktree", "add", "-q", "-b", branch, str(path), base)
        return path

    def commit_in(self, worktree: Path, relative: str) -> None:
        (worktree / relative).write_text("x\n")
        self.git("-C", str(worktree), "add", relative)
        self.git("-C", str(worktree), "commit", "-q", "-m", relative)

    def clean(self, worktree: Path, merged_into: str = "f") -> subprocess.CompletedProcess:
        return subprocess.run([str(CLEAN), str(worktree), merged_into], env=self.env, cwd=self.root, capture_output=True, text=True, timeout=60)

    def branches(self) -> list[str]:
        return self.git("-C", str(self.root), "branch", "--format=%(refname:short)").split()

    def assert_refused(self, worktree: Path, reason: str) -> None:
        listed = self.git("-C", str(self.root), "worktree", "list", "--porcelain")
        branches = self.branches()
        result = self.clean(worktree)
        self.assertEqual(result.returncode, 5, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertIn(reason, result.stderr)
        self.assertTrue(worktree.exists())
        self.assertEqual(self.git("-C", str(self.root), "worktree", "list", "--porcelain"), listed)
        self.assertEqual(self.branches(), branches)
        self.assertEqual(self.docker_log.read_text(), "")

    def merge(self, branch: str) -> None:
        self.git("-C", str(self.root), "branch", "-f", "f", branch)

    def test_removes_a_merged_worktree_its_ignored_dependencies_and_its_branch(self) -> None:
        worktree = self.add_worktree(self.tmp / "wt", branch="f-phase-p")
        (worktree / ".venvs" / "pkg").mkdir(parents=True)
        (worktree / ".venvs" / "pkg" / "lib").write_text("x\n")
        self.commit_in(worktree, "work.txt")
        self.merge("f-phase-p")

        result = self.clean(worktree)

        self.assertEqual((result.returncode, result.stdout), (0, f"removed {worktree}\n"), result.stderr)
        self.assertFalse(worktree.exists())
        self.assertNotIn("f-phase-p", self.branches())

    def test_unmerged_commits_are_refused(self) -> None:
        worktree = self.add_worktree(self.tmp / "wt", branch="f-phase-p")
        self.commit_in(worktree, "work.txt")

        self.assert_refused(worktree, "not merged into f")

    def test_commits_on_a_detached_head_are_refused(self) -> None:
        worktree = self.add_worktree(self.tmp / "wt", branch="f-phase-p")
        self.git("-C", str(worktree), "checkout", "-q", "--detach")
        self.commit_in(worktree, "work.txt")

        self.assert_refused(worktree, "HEAD of")

    def test_untracked_files_are_refused(self) -> None:
        worktree = self.add_worktree(self.tmp / "wt", branch="f-phase-p")
        (worktree / "probe.py").write_text("x\n")

        self.assert_refused(worktree, "uncommitted changes")

    def test_a_process_working_in_a_subdirectory_is_refused(self) -> None:
        worktree = self.add_worktree(self.tmp / "wt", branch="f-phase-p")
        (worktree / "sub").mkdir()
        process = subprocess.Popen(["sleep", "60"], cwd=worktree / "sub")
        self.addCleanup(process.wait)
        self.addCleanup(process.kill)

        self.assert_refused(worktree, f"processes {process.pid} ")

    def test_the_main_worktree_is_refused(self) -> None:
        result = self.clean(self.root)

        self.assertEqual(result.returncode, 5, result.stderr)
        self.assertIn("the main worktree", result.stderr)

    def test_a_directory_that_is_not_a_worktree_is_refused(self) -> None:
        other = self.tmp / "other"
        other.mkdir()

        self.assert_refused(other, "not a worktree of this repository")

    def test_removes_a_nested_worktree_of_the_same_repository_first(self) -> None:
        worktree = self.add_worktree(self.tmp / "wt", branch="f-phase-p")
        nested = self.add_worktree(worktree / "scratch" / "review-1", branch="review-1", base="f-phase-p")

        result = self.clean(worktree)

        self.assertEqual((result.returncode, result.stdout), (0, f"removed {nested}\nremoved {worktree}\n"), result.stderr)
        self.assertFalse(worktree.exists())
        self.assertEqual(self.git("-C", str(self.root), "worktree", "list", "--porcelain").count("worktree "), 1)
        self.assertNotIn("review-1", self.branches())

    def test_a_nested_worktree_with_local_only_commits_is_refused(self) -> None:
        worktree = self.add_worktree(self.tmp / "wt", branch="f-phase-p")
        nested = self.add_worktree(worktree / "scratch" / "review-1", branch="review-1", base="f-phase-p")
        self.commit_in(nested, "probe.py")

        self.assert_refused(worktree, f"nested worktree {nested}")

    def test_a_nested_worktree_with_uncommitted_changes_is_refused(self) -> None:
        worktree = self.add_worktree(self.tmp / "wt", branch="f-phase-p")
        nested = self.add_worktree(worktree / "scratch" / "review-1", branch="review-1", base="f-phase-p")
        (nested / "probe.py").write_text("x\n")

        self.assert_refused(worktree, f"uncommitted changes in {nested}")

    def test_another_repository_inside_is_refused(self) -> None:
        worktree = self.add_worktree(self.tmp / "wt", branch="f-phase-p")
        self.git("init", "-q", str(worktree / "scratch" / "probe-repo"))

        self.assert_refused(worktree, "another repository")

    def test_stops_only_the_compose_projects_started_inside_it(self) -> None:
        worktree = self.add_worktree(self.tmp / "wt", branch="f-phase-p")
        (worktree / "services").mkdir()
        Path(f"{worktree}-other").mkdir()
        self.containers.write_text(
            f"wt-a\t{worktree}\n"
            f"wt-a\t{worktree}\n"
            f"wt-b\t{worktree / 'services'}\n"
            f"shared\t{self.root}\n"
            f"sibling\t{worktree}-other\n"
            "\t\n"
        )

        result = self.clean(worktree)

        self.assertEqual((result.returncode, result.stdout), (0, f"stopped wt-a\nstopped wt-b\nremoved {worktree}\n"), result.stderr)
        self.assertEqual(
            self.docker_log.read_text().splitlines(),
            [f"compose -p {project} down --volumes --rmi local --remove-orphans" for project in ("wt-a", "wt-b")],
        )


if __name__ == "__main__":
    unittest.main()
