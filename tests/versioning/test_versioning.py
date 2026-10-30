"""Behaviour of scripts/versioning.py, driven through its CLI in throwaway repos."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"

APM_STUB = textwrap.dedent(
    """\
    #!/bin/sh
    if [ "$1" = "--version" ]; then
      echo "Agent Package Manager (APM) CLI version 0.32.0"
      exit 0
    fi
    printf 'lockfile written by apm install in %s\\n' "$(basename "$PWD")" > apm.lock.yaml
    """
)


def manifest(name: str, version: str, deps: list[str]) -> str:
    if deps:
        dependencies = "dependencies:\n  apm:\n" + "".join(f"    - path: ../{d}\n" for d in deps)
    else:
        dependencies = "dependencies: {}\n"
    return f'name: {name}\nversion: "{version}"\ndescription: "{name}"\n{dependencies}'


class VersioningTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.repo = self.tmp / "repo"
        (self.repo / "scripts").mkdir(parents=True)
        for script in ("versioning.py", "relativise_lockfiles.py"):
            shutil.copy(SCRIPTS / script, self.repo / "scripts" / script)
        self.write_package("a", "0.1.0", [])
        self.write_package("b", "0.1.0", ["a"])
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.commit("initial")
        self.git("checkout", "-q", "-b", "feature")

        stub = self.tmp / "apm"
        stub.write_text(APM_STUB)
        stub.chmod(0o755)
        self.env = {**os.environ, "APM": str(stub)}

    def write_package(self, name: str, version: str, deps: list[str]) -> None:
        package = self.repo / "packages" / name
        (package / ".apm" / "skills" / name).mkdir(parents=True, exist_ok=True)
        (package / "apm.yml").write_text(manifest(name, version, deps))
        (package / ".apm" / "skills" / name / "SKILL.md").write_text(f"# {name}\n")
        (package / "apm.lock.yaml").write_text("lockfile_version: '1'\n")

    def git(self, *args: str) -> str:
        return subprocess.run(
            ["git", *args], cwd=self.repo, check=True, capture_output=True, text=True
        ).stdout

    def commit(self, message: str) -> None:
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)

    def versioning(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", "scripts/versioning.py", *args],
            cwd=self.repo,
            env=self.env,
            capture_output=True,
            text=True,
        )

    def version_of(self, name: str) -> str:
        text = (self.repo / "packages" / name / "apm.yml").read_text()
        return next(line for line in text.splitlines() if line.startswith("version:"))

    def edit_skill(self, name: str) -> None:
        (self.repo / "packages" / name / ".apm" / "skills" / name / "SKILL.md").write_text(
            f"# {name}\n\nChanged.\n"
        )
        self.commit(f"edit {name}")

    def test_check_fails_when_primitive_changes_without_bump(self) -> None:
        self.edit_skill("a")
        result = self.versioning("check", "main")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("packages/a", result.stderr)
        self.assertIn("base 0.1.0, head 0.1.0", result.stderr)
        self.assertIn("python3 scripts/versioning.py bump", result.stderr)

    def test_check_passes_after_bump(self) -> None:
        self.edit_skill("a")
        self.assertEqual(self.versioning("bump", "--base", "main").returncode, 0)
        self.commit("bump")
        result = self.versioning("check", "main")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_check_ignores_readme_only_change(self) -> None:
        (self.repo / "packages" / "a" / "README.md").write_text("# a\n")
        self.commit("readme")
        result = self.versioning("check", "main")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_check_passes_for_new_package(self) -> None:
        self.write_package("c", "0.1.0", ["a"])
        self.commit("add c")
        result = self.versioning("check", "main")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_check_rejects_unquoted_version(self) -> None:
        manifest_path = self.repo / "packages" / "a" / "apm.yml"
        manifest_path.write_text(manifest_path.read_text().replace('"0.1.0"', "0.1.1"))
        self.commit("unquoted")
        result = self.versioning("check", "main")
        self.assertEqual(result.returncode, 1)
        self.assertIn('version: "X.Y.Z"', result.stderr)

    def test_tag_creates_missing_tags_then_is_a_no_op(self) -> None:
        self.git("tag", "a--v0.1.0")
        first = self.versioning("tag")
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout.splitlines(), ["b--v0.1.0"])
        head = self.git("rev-parse", "HEAD").strip()
        self.assertEqual(self.git("rev-parse", "b--v0.1.0").strip(), head)
        self.assertEqual(self.git("cat-file", "-t", "b--v0.1.0").strip(), "commit")

        second = self.versioning("tag")
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(second.stdout, "")

    def test_bump_rewrites_package_and_dependent_and_is_idempotent(self) -> None:
        self.edit_skill("a")
        first = self.versioning("bump", "minor", "--base", "main")
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertIn("a 0.1.0 -> 0.2.0", first.stdout)
        self.assertIn("b 0.1.0 -> 0.2.0", first.stdout)
        self.assertEqual(self.version_of("a"), 'version: "0.2.0"')
        self.assertEqual(self.version_of("b"), 'version: "0.2.0"')
        self.assertEqual(
            (self.repo / "packages" / "b" / "apm.lock.yaml").read_text(),
            "lockfile written by apm install in b\n",
        )

        tree = self.git("status", "--porcelain") + self.git("diff")
        second = self.versioning("bump", "minor", "--base", "main")
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertNotIn("->", second.stdout)
        self.assertEqual(self.git("status", "--porcelain") + self.git("diff"), tree)

    def test_bump_leaves_unrelated_dependency_alone(self) -> None:
        self.edit_skill("b")
        result = self.versioning("bump", "--base", "main")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), ["b 0.1.0 -> 0.1.1"])
        self.assertEqual(self.version_of("a"), 'version: "0.1.0"')

    def test_bump_refuses_wrong_apm_version(self) -> None:
        stub = self.tmp / "old-apm"
        stub.write_text("#!/bin/sh\necho 'Agent Package Manager (APM) CLI version 0.31.0'\n")
        stub.chmod(0o755)
        self.env["APM"] = str(stub)
        self.edit_skill("a")
        result = self.versioning("bump", "--base", "main")
        self.assertEqual(result.returncode, 1)
        self.assertIn("need apm 0.32.0", result.stderr)
        self.assertEqual(self.version_of("a"), 'version: "0.1.0"')


if __name__ == "__main__":
    unittest.main()
