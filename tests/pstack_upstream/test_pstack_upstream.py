# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Behaviour of scripts/pstack_upstream.py against a throwaway upstream repository."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "pstack_upstream.py"
GIT_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "Test",
    "GIT_AUTHOR_EMAIL": "test@example.com",
    "GIT_COMMITTER_NAME": "Test",
    "GIT_COMMITTER_EMAIL": "test@example.com",
}

SKILL = "# Foo\n\nFirst line.\n\nMiddle line.\n\nLast line.\n"
LOCAL_SKILL = SKILL.replace("First line.", "First line, localised.")


def git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, env=GIT_ENV, check=True, capture_output=True, text=True).stdout.strip()


def write_tree(root: Path, files: dict[str, str | None]) -> None:
    for rel, text in files.items():
        path = root / rel
        if text is None:
            path.unlink()
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)


class PstackUpstreamTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.upstream = self.tmp / "upstream"
        self.upstream.mkdir()
        git(self.upstream, "init", "-q", "-b", "main")
        self.base = self.commit_upstream(
            {
                "pstack/skills/foo/SKILL.md": SKILL,
                "pstack/agents/a.md": "agent a\n",
                "pstack/automations/x.md": "automation\n",
                "pstack/plugin.json": json.dumps({"version": "1.0.0"}),
            }
        )
        self.package = self.tmp / "package"
        write_tree(
            self.package,
            {
                ".apm/skills/foo/SKILL.md": LOCAL_SKILL,
                ".apm/agents/a.agent.md": "agent a\n",
                "apm.yml": "name: pstack\n",
                "upstream.json": json.dumps({"repository": str(self.upstream), "path": "pstack", "commit": self.base}),
            },
        )
        git(self.package, "init", "-q")
        git(self.package, "add", "-A")
        git(self.package, "commit", "-qm", "port")

    def commit_upstream(self, files: dict[str, str | None]) -> str:
        write_tree(self.upstream, files)
        git(self.upstream, "add", "-A")
        git(self.upstream, "commit", "-qm", "upstream change")
        return git(self.upstream, "rev-parse", "HEAD")

    def run_script(self, command: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["uv", "run", "--script", str(SCRIPT), command, "--package", str(self.package)],
            env=GIT_ENV,
            capture_output=True,
            text=True,
            timeout=120,
        )

    def pin(self) -> str:
        return json.loads((self.package / "upstream.json").read_text())["commit"]

    def snapshot(self) -> dict[str, bytes]:
        return {str(p.relative_to(self.package)): p.read_bytes() for p in self.package.rglob("*") if p.is_file() and ".git" not in p.parts}

    def test_sync_merges_adds_and_deletes_then_converges(self) -> None:
        target = self.commit_upstream(
            {
                "pstack/skills/foo/SKILL.md": SKILL.replace("Last line.", "Last line, revised upstream."),
                "pstack/skills/bar/SKILL.md": "# Bar\n",
                "pstack/agents/a.md": None,
                "pstack/automations/x.md": "automation, revised\n",
            }
        )

        result = self.run_script("sync")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        skill = (self.package / ".apm/skills/foo/SKILL.md").read_text()
        self.assertIn("First line, localised.", skill)
        self.assertIn("Last line, revised upstream.", skill)
        self.assertEqual((self.package / ".apm/skills/bar/SKILL.md").read_text(), "# Bar\n")
        self.assertFalse((self.package / ".apm/agents/a.agent.md").exists())
        self.assertFalse(any("automation" in p for p in self.snapshot()))
        self.assertEqual(self.pin(), target)

        before = self.snapshot()
        rerun = self.run_script("sync")
        self.assertEqual(rerun.returncode, 0, rerun.stdout + rerun.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_sync_after_a_crash_before_the_pin_moved_converges(self) -> None:
        self.commit_upstream({"pstack/skills/foo/SKILL.md": SKILL.replace("Last line.", "Last line, revised upstream.")})
        self.assertEqual(self.run_script("sync").returncode, 0)
        synced = self.snapshot()
        write_tree(self.package, {"upstream.json": json.dumps({"repository": str(self.upstream), "path": "pstack", "commit": self.base})})

        result = self.run_script("sync")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.snapshot(), synced)

    def test_overlapping_edits_leave_markers_and_still_advance_the_pin(self) -> None:
        target = self.commit_upstream({"pstack/skills/foo/SKILL.md": SKILL.replace("First line.", "First line, rewritten upstream.")})

        result = self.run_script("sync")

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        skill = (self.package / ".apm/skills/foo/SKILL.md").read_text()
        self.assertIn("<<<<<<< ours\nFirst line, localised.", skill)
        self.assertIn("First line, rewritten upstream.\n>>>>>>> upstream", skill)
        self.assertEqual(self.pin(), target)

    def test_status_reports_the_plan_without_writing(self) -> None:
        self.commit_upstream({"pstack/skills/bar/SKILL.md": "# Bar\n", "pstack/automations/x.md": None})

        result = self.run_script("status")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("skills/bar/SKILL.md -> .apm/skills/bar/SKILL.md", result.stdout)
        self.assertIn("skip-unmirrored  automations/x.md", result.stdout)
        self.assertIn("Mapping drift at the pinned commit: none", result.stdout)
        self.assertEqual(git(self.package, "status", "--porcelain"), "")

    def test_status_fails_on_a_local_file_outside_the_mapping(self) -> None:
        write_tree(self.package, {"stray.txt": "stray\n"})

        result = self.run_script("status")

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("local file with no upstream counterpart: stray.txt", result.stdout)


if __name__ == "__main__":
    unittest.main()
