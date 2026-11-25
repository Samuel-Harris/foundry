from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

from launcher_case import ROADMAP_ID, LauncherTestCase


class RepoTests(LauncherTestCase):
    """A phase in a second repository, started from the feature worktree of the first."""

    def setUp(self) -> None:
        super().setUp()
        self.feature = self.make_feature_worktree()
        self.commit_in(self.feature, relative=f".foundry/feature-roadmaps/{ROADMAP_ID}/README.md")
        self.make_orchestrator()

        other_seed = self.tmp / "other-seed"
        self.other_origin = self.tmp / "other-origin.git"
        self.other = self.tmp / "other"
        self.git("init", "-q", "-b", "trunk", str(other_seed))
        (other_seed / "LIBRARY.md").write_text("library\n")
        self.git("-C", str(other_seed), "add", ".")
        self.git("-C", str(other_seed), "commit", "-q", "-m", "seed")
        self.git("clone", "-q", "--bare", str(other_seed), str(self.other_origin))
        self.git("clone", "-q", str(self.other_origin), str(self.other))
        self.other_seed = other_seed

    def other_worktree(self, name: str) -> Path:
        return Path(f"{self.other}__wt/{name}")

    def launch_phase(self, *args: str) -> subprocess.CompletedProcess:
        return self.launch("--feature", "f", "--role", "phase", "--repo", str(self.other), *args, cwd=self.feature)

    def test_the_first_phase_gets_a_feature_branch_cut_from_the_latest_origin_default(self) -> None:
        self.commit_in(self.other_seed, relative="later.txt")
        self.git("-C", str(self.other_seed), "push", "-q", str(self.other_origin), "trunk")
        latest = self.git("-C", str(self.other_seed), "rev-parse", "HEAD").strip()

        pane, worktree = self.started(self.launch_phase("--phase", "p", "--window", self.window), name="f-phase-p")

        self.assertEqual(Path(worktree), self.other_worktree("f-phase-p"))
        self.assertEqual(self.git("-C", str(self.other_worktree("f")), "rev-parse", "HEAD").strip(), latest)
        self.assertEqual(self.git("-C", worktree, "rev-parse", "HEAD").strip(), latest)
        self.assertEqual(self.git("-C", worktree, "branch", "--show-current").strip(), "f-phase-p")
        self.assertEqual(self.window_of(pane), self.window)
        self.assertEqual(self.tmux("display-message", "-p", "-t", pane, "#{pane_current_path}").strip(), worktree)
        self.assertEqual(self.git("-C", str(self.root), "branch", "--list", "f-phase-p").strip(), "")

    def test_the_prompt_names_the_feature_worktrees_roadmap_and_plan_by_absolute_path(self) -> None:
        self.started(self.launch_phase("--phase", "p", "--window", self.window), name="f-phase-p")

        self.assertEqual(
            self.prompt_of("f-phase-p"),
            f"/sam-mode phase feature=f phase=p update=- roadmap={self.feature}/.foundry/feature-roadmaps/{ROADMAP_ID} plan={self.feature}/.foundry/plans/{ROADMAP_ID}/README.md orchestrator=f-orchestrator",
        )

    def test_a_second_phase_is_cut_from_the_existing_feature_branch(self) -> None:
        self.started(self.launch_phase("--phase", "p", "--window", self.window), name="f-phase-p")
        self.commit_in(self.other_worktree("f"), relative="merged.txt")
        merged = self.git("-C", str(self.other_worktree("f")), "rev-parse", "HEAD").strip()

        _, worktree = self.started(self.launch_phase("--phase", "q", "--window", self.window), name="f-phase-q")

        self.assertEqual(self.git("-C", worktree, "rev-parse", "HEAD").strip(), merged)

    def test_remove_removes_the_worktree_in_the_other_repository(self) -> None:
        self.make_other_phase_worktree()

        result = self.launch_phase("--phase", "p", "--remove")

        self.assertEqual((result.returncode, result.stdout), (0, f"removed f-phase-p worktree={self.other_worktree('f-phase-p')}\n"), result.stderr)
        self.assertFalse(self.other_worktree("f-phase-p").exists())
        self.assertEqual(self.git("-C", str(self.other), "branch", "--list", "f-phase-p").strip(), "f-phase-p")

    def test_remove_refuses_a_branch_not_merged_into_the_other_repositorys_feature_branch(self) -> None:
        worktree = self.make_other_phase_worktree()
        self.commit_in(worktree, relative="work.txt")

        result = self.launch_phase("--phase", "p", "--remove")

        self.assertEqual(result.returncode, 5, result.stderr)
        self.assertIn("not merged into f", result.stderr)
        self.assertTrue(worktree.exists())

    def test_a_repo_naming_the_feature_worktrees_own_repository_changes_nothing(self) -> None:
        _, worktree = self.started(self.launch("--feature", "f", "--role", "phase", "--phase", "p", "--repo", str(self.root), "--window", self.window, cwd=self.feature), name="f-phase-p")

        self.assertEqual(Path(worktree), self.worktree("f-phase-p"))
        self.assertFalse(self.other_worktree("f").exists())
        self.assertIn(f" roadmap=.foundry/feature-roadmaps/{ROADMAP_ID} plan=.foundry/plans/{ROADMAP_ID}/README.md ", self.prompt_of("f-phase-p"))

    def make_other_phase_worktree(self) -> Path:
        for name, base in (("f", "origin/trunk"), ("f-phase-p", "f")):
            self.git("-C", str(self.other), "worktree", "add", "-q", "-b", name, str(self.other_worktree(name)), base)
        return self.other_worktree("f-phase-p")


if __name__ == "__main__":
    unittest.main()
