"""Behaviour of scripts/relativise_lockfiles.py, run on lockfiles in throwaway repos."""

from __future__ import annotations

import hashlib
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "relativise_lockfiles.py"

LINKING = ".claude/skills/ketchup/SKILL.md"
LONG_LINKING = ".claude/skills/poteto-help/references/guide/" + "a-guide-page-with-a-name-long-enough-for-yaml-" * 2 + ".md"
PLAIN = ".claude/skills/plain/SKILL.md"
PLAIN_TEXT = "No links here.\n"


def sha256(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def linking_text(anchor: str) -> str:
    slot = hashlib.sha256(anchor.encode("utf-8")).hexdigest()[:12]
    return f"See [bro](../../../apm_modules/_local/{slot}/p-stack/.apm/skills/bro/SKILL.md).\n"


class RelativiseLockfilesTest(unittest.TestCase):
    def setUp(self) -> None:
        # resolve() because the script resolves its own path, and macOS's temp directory is a symlink.
        self.tmp = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(shutil.rmtree, self.tmp)

    def lay_out_install(self, root: Path) -> Path:
        """Write what `apm install` leaves in packages/default-stack when p-stack is reached through a sibling."""
        (root / "scripts").mkdir(parents=True)
        shutil.copy(SCRIPT, root / "scripts")
        package = root / "packages" / "default-stack"
        anchor = str(root / "packages" / "p-stack")
        files = {LINKING: linking_text(anchor), LONG_LINKING: linking_text(anchor), PLAIN: PLAIN_TEXT}
        for name, text in files.items():
            (package / name).parent.mkdir(parents=True, exist_ok=True)
            (package / name).write_text(text)
        deployments = "".join(
            f"- value: {name}\n  owners:\n  - local:{anchor}\n  content_hash: {sha256(text)}\n"
            for name, text in files.items()
        )
        lockfile = package / "apm.lock.yaml"
        lockfile.write_text(
            "dependencies:\n"
            "- repo_url: _local/p-stack\n"
            f"  anchored_local_path: {anchor}\n"
            "  deployed_file_hashes:\n"
            f"    {LINKING}: {sha256(files[LINKING])}\n"
            f"    ? {LONG_LINKING}\n"
            f"    : {sha256(files[LONG_LINKING])}\n"
            f"    {PLAIN}: {sha256(PLAIN_TEXT)}\n"
            f"deployments:\n{deployments}"
        )
        return lockfile

    def relativise(self, lockfile: Path) -> subprocess.CompletedProcess[str]:
        root = lockfile.parents[2]
        return subprocess.run(
            ["python3", "scripts/relativise_lockfiles.py", str(lockfile)],
            cwd=root,
            capture_output=True,
            text=True,
        )

    def test_lockfiles_from_two_checkout_paths_are_identical(self) -> None:
        first = self.lay_out_install(self.tmp / "one" / "repo")
        second = self.lay_out_install(self.tmp / "two" / "nested" / "repo")
        self.assertEqual(self.relativise(first).returncode, 0)
        self.assertEqual(self.relativise(second).returncode, 0)
        self.assertEqual(first.read_text(), second.read_text())

    def test_linking_files_take_the_hash_under_the_relative_slot_and_others_keep_theirs(self) -> None:
        lockfile = self.lay_out_install(self.tmp / "repo")
        self.relativise(lockfile)
        text = lockfile.read_text()
        relative_hash = sha256(linking_text("../p-stack"))
        self.assertEqual(text.count(relative_hash), 4)
        self.assertEqual(text.count(sha256(PLAIN_TEXT)), 2)
        self.assertNotIn(str(self.tmp), text)

    def test_a_second_run_changes_nothing(self) -> None:
        lockfile = self.lay_out_install(self.tmp / "repo")
        self.relativise(lockfile)
        once = lockfile.read_text()
        self.assertEqual(self.relativise(lockfile).returncode, 0)
        self.assertEqual(lockfile.read_text(), once)

    def test_a_deployed_file_that_is_missing_or_edited_fails_and_leaves_the_lockfile(self) -> None:
        for change in ("delete", "edit"):
            with self.subTest(change=change):
                lockfile = self.lay_out_install(self.tmp / change / "repo")
                before = lockfile.read_text()
                deployed = lockfile.parent / LINKING
                if change == "delete":
                    deployed.unlink()
                else:
                    deployed.write_text("Edited after install.\n")
                result = self.relativise(lockfile)
                self.assertEqual(result.returncode, 1)
                self.assertIn("run apm install again first", result.stderr)
                self.assertEqual(lockfile.read_text(), before)


if __name__ == "__main__":
    unittest.main()
