"""Behaviour of scripts/relativise_lockfiles.py, run on lockfiles in throwaway repos."""

from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "relativise_lockfiles.py"


def sha256(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def slot(anchor: str) -> str:
    return hashlib.sha256(anchor.encode("utf-8")).hexdigest()[:12]


def linking_skill(anchor: str) -> str:
    return f"See [bro](../../../apm_modules/_local/{slot(anchor)}/p-stack/.apm/skills/bro/SKILL.md).\n"


PLAIN_SKILL = "No links here.\n"


class RelativiseLockfilesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(shutil.rmtree, self.tmp)

    def install(self, root: Path) -> Path:
        """Lay out what `apm install` leaves in packages/default-stack when p-stack is reached transitively."""
        (root / "scripts").mkdir(parents=True)
        shutil.copy(SCRIPT, root / "scripts")
        package = root / "packages" / "default-stack"
        anchor = str(root / "packages" / "p-stack")
        skills = package / ".claude" / "skills"
        (skills / "ketchup").mkdir(parents=True)
        (skills / "plain").mkdir()
        (skills / "ketchup" / "SKILL.md").write_text(linking_skill(anchor))
        (skills / "plain" / "SKILL.md").write_text(PLAIN_SKILL)
        lockfile = package / "apm.lock.yaml"
        lockfile.write_text(
            "dependencies:\n"
            "- repo_url: _local/p-stack\n"
            f"  anchored_local_path: {anchor}\n"
            "local_deployed_file_hashes:\n"
            f"  .claude/skills/ketchup/SKILL.md: {sha256(linking_skill(anchor))}\n"
            f"  .claude/skills/plain/SKILL.md: {sha256(PLAIN_SKILL)}\n"
            "deployments:\n"
            "- value: .claude/skills/ketchup/SKILL.md\n"
            "  owners:\n"
            f"  - local:{anchor}\n"
            f"  content_hash: {sha256(linking_skill(anchor))}\n"
        )
        return lockfile

    def relativise(self, lockfile: Path) -> str:
        script = lockfile.parents[2] / "scripts" / "relativise_lockfiles.py"
        subprocess.run([sys.executable, str(script), str(lockfile)], check=True)
        return lockfile.read_text()

    def test_lockfiles_from_two_checkout_paths_are_identical(self) -> None:
        first = self.relativise(self.install(self.tmp / "one" / "repo"))
        second = self.relativise(self.install(self.tmp / "two" / "nested" / "repo"))
        self.assertEqual(first, second)

    def test_hash_of_a_linking_file_is_the_hash_under_the_relative_slot(self) -> None:
        text = self.relativise(self.install(self.tmp / "repo"))
        self.assertIn("anchored_local_path: ../p-stack\n", text)
        self.assertIn(f"  .claude/skills/ketchup/SKILL.md: {sha256(linking_skill('../p-stack'))}\n", text)
        self.assertIn(f"  content_hash: {sha256(linking_skill('../p-stack'))}\n", text)
        self.assertIn(f"  .claude/skills/plain/SKILL.md: {sha256(PLAIN_SKILL)}\n", text)


if __name__ == "__main__":
    unittest.main()
