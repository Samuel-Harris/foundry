#!/usr/bin/env python3
"""Check, bump and tag per-package versions.

APM 0.32.0 resolves `Samuel-Harris/foundry/packages/<name>#^X.Y.Z` against
lightweight git tags named `<name>--vX.Y.Z`. Every change to a package's
versioned content (`apm.yml`, `.apm/**`, `apm.lock.yaml`) therefore needs a
higher version, so each merge to main can be tagged.

A package's version is the single `version: "X.Y.Z"` line in its `apm.yml`.
Any other form is rejected.

Usage:
  versioning.py check BASE_REF
      Exit 1 when a package changed since merge-base(BASE_REF, HEAD) without
      a higher version.
  versioning.py bump [patch|minor|major] [--base BASE_REF]
      Bump every changed package and every package that depends on one,
      directly or transitively, then regenerate their lockfiles with
      `apm install`. BASE_REF defaults to origin/main. Rerunning is a no-op.
  versioning.py tag
      Create a lightweight `<name>--v<version>` tag at HEAD for every package
      whose tag does not exist locally, and print each new tag name.

Head versions and changes are read from the working tree, which equals HEAD
on a clean checkout. `bump` needs apm-cli 0.32.0 from $APM, .venv-apm/bin/apm
or PATH.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple

import relativise_lockfiles

REPO_ROOT = Path(__file__).resolve().parents[1]
PINNED_APM = "0.32.0"
APM_TARGETS = "cursor,claude,copilot"
APM_TIMEOUT = 300
FIX = "python3 scripts/versioning.py bump"

VERSION_LINE = re.compile(r'^version: "(\d+)\.(\d+)\.(\d+)"$')
ANY_VERSION_LINE = re.compile(r"^version:.*$", re.MULTILINE)
MANIFEST_PATH = re.compile(r"^packages/([^/]+)/apm\.yml$")
VERSIONED_PATH = re.compile(r"^packages/([^/]+)/(?:apm\.yml|apm\.lock\.yaml|\.apm/.+)$")
SIBLING_DEPENDENCY = re.compile(r"^\s*-\s*path:\s*\.\./([^\s/]+)\s*$", re.MULTILINE)


class Version(NamedTuple):
    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def bumped(self, level: str) -> Version:
        if level == "major":
            return Version(self.major + 1, 0, 0)
        if level == "minor":
            return Version(self.major, self.minor + 1, 0)
        return Version(self.major, self.minor, self.patch + 1)


@dataclass(frozen=True)
class PackageState:
    base: Version | None
    head: Version | None
    changed: bool


class VersioningError(Exception):
    pass


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args], capture_output=True, text=True
    )
    if result.returncode != 0:
        raise VersioningError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


def parse_version(manifest: str, where: str) -> Version:
    lines = ANY_VERSION_LINE.findall(manifest)
    match = VERSION_LINE.match(lines[0]) if len(lines) == 1 else None
    if match is None:
        raise VersioningError(
            f'{where}: expected exactly one line of the form version: "X.Y.Z", found {lines!r}'
        )
    return Version(*map(int, match.groups()))


def manifest_file(name: str) -> Path:
    return REPO_ROOT / "packages" / name / "apm.yml"


def head_packages() -> set[str]:
    return {path.parent.name for path in (REPO_ROOT / "packages").glob("*/apm.yml")}


def commit_packages(commit: str) -> set[str]:
    listing = git("ls-tree", "-r", "--name-only", commit, "--", "packages")
    return {m[1] for line in listing.splitlines() if (m := MANIFEST_PATH.match(line))}


def package_states(base_ref: str) -> dict[str, PackageState]:
    merge_base = git("merge-base", base_ref, "HEAD").strip()
    base_names = commit_packages(merge_base)
    head_names = head_packages()
    diff = git("diff", "--no-renames", "--name-only", merge_base, "--")
    changed = {m[1] for line in diff.splitlines() if (m := VERSIONED_PATH.match(line))}

    states = {}
    for name in sorted(base_names | head_names):
        base = None
        if name in base_names:
            path = f"packages/{name}/apm.yml"
            base = parse_version(git("show", f"{merge_base}:{path}"), f"{merge_base[:12]}:{path}")
        head = None
        if name in head_names:
            head = parse_version(manifest_file(name).read_text(encoding="utf-8"), str(manifest_file(name)))
        states[name] = PackageState(base=base, head=head, changed=name in changed)
    return states


def check(states: dict[str, PackageState]) -> int:
    failures = [
        (name, state)
        for name, state in states.items()
        if state.changed and state.base is not None and state.head is not None and state.head <= state.base
    ]
    for name, state in failures:
        print(
            f"versioning: packages/{name} changed but its version did not increase "
            f"(base {state.base}, head {state.head}). Fix: {FIX}",
            file=sys.stderr,
        )
    if failures:
        return 1
    changed = sum(state.changed for state in states.values())
    print(f"versioning: {changed} changed package(s), none without a version bump")
    return 0


def dependents(names: set[str]) -> set[str]:
    depends_on = {
        name: set(SIBLING_DEPENDENCY.findall(manifest_file(name).read_text(encoding="utf-8")))
        for name in head_packages()
    }
    closure = set(names)
    queue = list(names)
    while queue:
        target = queue.pop()
        for name, deps in depends_on.items():
            if target in deps and name not in closure:
                closure.add(name)
                queue.append(name)
    return closure


def resolve_apm() -> str:
    candidates = [os.environ.get("APM"), str(REPO_ROOT / ".venv-apm" / "bin" / "apm"), shutil.which("apm")]
    apm = next((c for c in candidates if c and os.access(c, os.X_OK)), None)
    if apm is None:
        raise VersioningError(f"apm {PINNED_APM} not found (set APM=, create .venv-apm, or put apm on PATH)")
    result = subprocess.run([apm, "--version"], capture_output=True, text=True, timeout=APM_TIMEOUT)
    output = (result.stdout + result.stderr).strip()
    if f"version {PINNED_APM}" not in output:
        raise VersioningError(f"need apm {PINNED_APM}, got: {output or '<no version>'}")
    return apm


def bump(states: dict[str, PackageState], level: str) -> int:
    affected = dependents({name for name, state in states.items() if state.changed})
    to_install = sorted(name for name in affected if states[name].head is not None)
    to_bump = [
        name
        for name in to_install
        if states[name].base is not None and states[name].head <= states[name].base
    ]
    if not to_install:
        print("versioning: nothing to bump")
        return 0
    apm = resolve_apm()

    for name in to_bump:
        old, new = states[name].head, states[name].base.bumped(level)
        path = manifest_file(name)
        text = path.read_text(encoding="utf-8")
        path.write_text(
            ANY_VERSION_LINE.sub(f'version: "{new}"', text, count=1), encoding="utf-8"
        )
        print(f"{name} {old} -> {new}", flush=True)

    for name in to_install:
        print(f"versioning: apm install in packages/{name}", file=sys.stderr, flush=True)
        result = subprocess.run(
            [apm, "install", "--target", APM_TARGETS],
            cwd=REPO_ROOT / "packages" / name,
            stdout=sys.stderr,
            timeout=APM_TIMEOUT,
        )
        if result.returncode != 0:
            raise VersioningError(f"apm install failed in packages/{name}")
    lockfiles = [str(REPO_ROOT / "packages" / name / "apm.lock.yaml") for name in to_install]
    if relativise_lockfiles.main(lockfiles) != 0:
        raise VersioningError("relativise_lockfiles failed")
    if not to_bump:
        print("versioning: nothing to bump")
    return 0


def tag() -> int:
    for name in sorted(commit_packages("HEAD")):
        path = f"packages/{name}/apm.yml"
        version = parse_version(git("show", f"HEAD:{path}"), f"HEAD:{path}")
        tag_name = f"{name}--v{version}"
        exists = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "rev-parse", "--quiet", "--verify", f"refs/tags/{tag_name}"],
            capture_output=True,
        )
        if exists.returncode != 0:
            git("tag", tag_name, "HEAD")
            print(tag_name)
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Check, bump and tag per-package versions.")
    commands = parser.add_subparsers(dest="command", required=True)
    check_parser = commands.add_parser("check", help="fail on a changed package without a higher version")
    check_parser.add_argument("base_ref")
    bump_parser = commands.add_parser("bump", help="bump changed packages and their dependents")
    bump_parser.add_argument("level", nargs="?", choices=["patch", "minor", "major"], default="patch")
    bump_parser.add_argument("--base", default="origin/main")
    commands.add_parser("tag", help="tag every untagged package version at HEAD")
    args = parser.parse_args(argv)

    try:
        if args.command == "check":
            return check(package_states(args.base_ref))
        if args.command == "bump":
            return bump(package_states(args.base), args.level)
        return tag()
    except (VersioningError, subprocess.TimeoutExpired) as error:
        print(f"versioning: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
