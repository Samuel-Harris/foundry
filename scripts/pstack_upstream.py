#!/usr/bin/env python3
"""Report and apply upstream pstack changes since the pinned commit.

`packages/pstack/upstream.json` records the upstream repository, the
directory pstack lives in, and the commit the port is based on. The port is
adapted (British English, target-neutral names, a different layout), so an
update is a three-way merge per file: base is the pinned upstream commit,
ours is the local file, theirs is upstream at the target commit.

`status` prints the commits and the per-file plan from the pin to REF
(default: upstream's default branch) plus mapping drift at the pin, and writes
nothing. `sync` applies the plan, leaves conflict markers where edits overlap,
moves the pin to REF, and exits 1 when any file needs a human.
"""

from __future__ import annotations

import argparse
import enum
import fnmatch
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
GIT_TIMEOUT = 300
CONFLICT_MARKER = b"<<<<<<< ours\n"


@dataclass(frozen=True)
class Rule:
    upstream: str
    local: str
    names: tuple[str, ...] = ("*",)
    upstream_suffix: str = ""
    local_suffix: str = ""

    def to_local(self, path: str) -> str | None:
        return self._translate(path, self.upstream, self.upstream_suffix, self.local, self.local_suffix)

    def to_upstream(self, path: str) -> str | None:
        return self._translate(path, self.local, self.local_suffix, self.upstream, self.upstream_suffix)

    def _translate(self, path: str, prefix: str, suffix: str, new_prefix: str, new_suffix: str) -> str | None:
        if not path.startswith(prefix) or not path.endswith(suffix):
            return None
        rest = path[len(prefix) : len(path) - len(suffix)]
        if not any(fnmatch.fnmatchcase(rest + suffix, name) for name in self.names):
            return None
        return new_prefix + rest + new_suffix


POTETO_MODE_TESTS = (
    "check-plan.test.ts", "watch-pr/*.test.ts", "watch-pr/*.test-helper.ts", "watch-pr/types.compile.ts",
)

# First match wins in both directions, so narrower rules precede `skills/`.
RULES = (
    Rule("agents/", ".apm/agents/", upstream_suffix=".md", local_suffix=".agent.md"),
    Rule("docs/guide/", ".apm/skills/poteto-help/references/guide/"),
    Rule("skills/statechart/scripts/test/", "tests/statechart/"),
    Rule("skills/poteto-mode/scripts/", "tests/poteto-mode/", names=POTETO_MODE_TESTS),
    Rule("skills/", ".apm/skills/"),
    Rule("LICENSE", "LICENSE", names=("",)),
)

# Entries ending in `/` cover a directory; the rest are exact paths.
# README.md and .gitignore appear in both: ours are Foundry-specific.
UPSTREAM_ONLY = (
    "automations/", "assets/", "docs/harness/", "plugin.json", ".cursor-plugin/", "README.md", ".gitignore",
    "skills/poteto-mode/scripts/watch-pr/tsconfig.json",  # replaced by tsconfig.poteto-mode.json
)
LOCAL_ONLY = (
    "apm.yml", "apm.lock.yaml", "bun.lock", "package.json", "tsconfig.poteto-mode.json", "upstream.json",
    "README.md", ".gitignore", "tests/statechart/package.json", "tests/statechart/package-lock.json",
)


def listed(path: str, entries: tuple[str, ...]) -> bool:
    return any(path == e or (e.endswith("/") and path.startswith(e)) for e in entries)


def first_match(path: str, translate) -> str | None:
    return next((p for p in (translate(rule, path) for rule in RULES) if p is not None), None)


class Action(enum.Enum):
    MERGE = "merge"
    ADD = "add"
    DELETE = "delete"
    UNMIRRORED = "skip-unmirrored"
    UNMAPPED = "unmapped"


@dataclass(frozen=True)
class Step:
    action: Action
    upstream: str
    local: str | None


def plan(changes: list[tuple[str, str]]) -> list[Step]:
    steps = []
    for status, path in changes:
        local = first_match(path, Rule.to_local)
        if listed(path, UPSTREAM_ONLY):
            steps.append(Step(Action.UNMIRRORED, path, None))
        elif local is None:
            steps.append(Step(Action.UNMAPPED, path, None))
        else:
            action = {"A": Action.ADD, "D": Action.DELETE}.get(status, Action.MERGE)
            steps.append(Step(action, path, local))
    return steps


def git(*args: str, cwd: Path, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, timeout=GIT_TIMEOUT)
    if check and result.returncode:
        sys.exit(f"git {args[0]} failed: {result.stderr.decode().strip()}")
    return result


def out(*args: str, cwd: Path) -> str:
    return git(*args, cwd=cwd).stdout.decode().strip()


@dataclass
class Upstream:
    clone: Path
    path: str
    pin: str
    target: str

    def blob(self, commit: str, path: str) -> bytes:
        return git("cat-file", "blob", f"{commit}:{self.path}/{path}", cwd=self.clone).stdout

    def version(self, commit: str) -> str:
        shown = git("show", f"{commit}:{self.path}/plugin.json", cwd=self.clone, check=False)
        return json.loads(shown.stdout).get("version", "?") if shown.returncode == 0 else "?"

    def changes(self) -> list[tuple[str, str]]:
        diff = out("diff", "--name-status", "--no-renames", self.pin, self.target, "--", self.path, cwd=self.clone)
        return [(line[0], self._relative(line.split("\t", 1)[1])) for line in diff.splitlines()]

    def files(self, commit: str) -> list[str]:
        listing = out("ls-tree", "-r", "--name-only", commit, "--", f"{self.path}/", cwd=self.clone)
        return [self._relative(line) for line in listing.splitlines()]

    def _relative(self, path: str) -> str:
        return path[len(self.path) + 1 :]

    def is_executable(self, path: str) -> bool:
        return out("ls-tree", self.target, "--", f"{self.path}/{path}", cwd=self.clone).startswith("100755")


def resolve(clone: Path, ref: str | None) -> str:
    for candidate in ([ref, f"origin/{ref}"] if ref else ["HEAD"]):
        found = git("rev-parse", "--verify", "--quiet", f"{candidate}^{{commit}}", cwd=clone, check=False)
        if found.returncode == 0:
            return found.stdout.decode().strip()
    sys.exit(f"Cannot resolve {ref!r} in the upstream repository.")


def write(path: Path, data: bytes, executable: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_bytes(data)
    if executable:
        tmp.chmod(0o755)
    os.replace(tmp, path)


def is_text(*blobs: bytes) -> bool:
    try:
        for blob in blobs:
            blob.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return not any(b"\0" in blob for blob in blobs)


def merge(up: Upstream, step: Step, target: Path) -> str:
    base, theirs = up.blob(up.pin, step.upstream), up.blob(up.target, step.upstream)
    if not target.exists():
        return "conflict: local file missing"
    ours = target.read_bytes()
    if ours == theirs:
        return "unchanged"
    if CONFLICT_MARKER in ours:
        return "conflict: unresolved markers from an earlier sync"
    if not is_text(base, ours, theirs):
        if ours != base:
            return "conflict: binary file changed on both sides"
        write(target, theirs)
        return "applied"
    with tempfile.TemporaryDirectory() as tmp:
        base_file, theirs_file = Path(tmp, "base"), Path(tmp, "theirs")
        base_file.write_bytes(base)
        theirs_file.write_bytes(theirs)
        merged = git("merge-file", "-L", "ours", "-L", "upstream-base", "-L", "upstream",
                     str(target), str(base_file), str(theirs_file), cwd=Path(tmp), check=False)
    # merge-file exits with the conflict count, capped at 127; anything else is an error.
    if not 0 <= merged.returncode <= 127:
        raise RuntimeError(merged.stderr.decode())
    return "conflict: overlapping edits marked in file" if merged.returncode else "merged"


def add(up: Upstream, step: Step, target: Path) -> str:
    theirs = up.blob(up.target, step.upstream)
    if target.exists():
        return "unchanged" if target.read_bytes() == theirs else "conflict: local file differs from upstream's new file"
    write(target, theirs, executable=up.is_executable(step.upstream))
    return "applied"


def delete(up: Upstream, step: Step, target: Path) -> str:
    if not target.exists():
        return "unchanged"
    if target.read_bytes() != up.blob(up.pin, step.upstream):
        return "conflict: deleted upstream but adapted locally; kept"
    target.unlink()
    return "applied"


APPLY = {Action.MERGE: merge, Action.ADD: add, Action.DELETE: delete}
REPORTED = {
    Action.UNMIRRORED: "not mirrored; review by hand",
    Action.UNMAPPED: "conflict: no mapping rule; add one to RULES or UPSTREAM_ONLY",
}


def describe(step: Step) -> str:
    return f"{step.action.value:16} {step.upstream}" + (f" -> {step.local}" if step.local else "")


def drift(up: Upstream, package: Path) -> list[str]:
    tracked = set(out("ls-files", "--cached", "--others", "--exclude-standard", cwd=package).splitlines())
    mapped = {p: first_match(p, Rule.to_local) for p in up.files(up.pin) if not listed(p, UPSTREAM_ONLY)}
    problems = [f"local file with no upstream counterpart: {p}" for p in sorted(tracked)
                if p not in LOCAL_ONLY and first_match(p, Rule.to_upstream) is None]
    problems += [f"upstream file with no mapping: {p}" for p, local in mapped.items() if local is None]
    problems += [f"upstream file missing locally: {p}" for p in mapped.values() if p and p not in tracked]
    return problems


def status(up: Upstream, package: Path) -> int:
    print(f"Pinned: {up.pin} (plugin.json {up.version(up.pin)})")
    print(f"Target: {up.target} (plugin.json {up.version(up.target)})")
    steps = plan(up.changes())
    if not steps:
        print("Up to date.")
    else:
        print("\nUpstream commits:")
        print(out("log", "--oneline", f"{up.pin}..{up.target}", "--", up.path, cwd=up.clone))
        print("\nPlanned actions:")
        print("\n".join(describe(s) for s in steps))
    problems = drift(up, package)
    print(f"\nMapping drift at the pinned commit: {len(problems) or 'none'}")
    for problem in problems:
        print(f"  {problem}")
    return 1 if problems else 0


def sync(up: Upstream, package: Path) -> int:
    conflicts = 0
    for step in plan(up.changes()):
        apply = APPLY.get(step.action)
        result = apply(up, step, package / step.local) if apply else REPORTED[step.action]
        conflicts += result.startswith("conflict")
        print(f"{describe(step)}: {result}")
    pin_file = package / "upstream.json"
    pin = json.loads(pin_file.read_text())
    write(pin_file, (json.dumps({**pin, "commit": up.target}, indent=2) + "\n").encode())
    print(f"Pinned upstream at {up.target}; {conflicts} file(s) need a human.")
    return 1 if conflicts else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("status", "sync"))
    parser.add_argument("--package", type=Path, default=REPO_ROOT / "packages" / "pstack")
    parser.add_argument("--ref")
    args = parser.parse_args()
    package = args.package.resolve()
    pin = json.loads((package / "upstream.json").read_text())
    with tempfile.TemporaryDirectory() as tmp:
        clone = Path(tmp, "upstream")
        git("clone", "--filter=blob:none", "--no-checkout", "--quiet", pin["repository"], str(clone), cwd=Path(tmp))
        up = Upstream(clone, pin["path"].strip("/"), resolve(clone, pin["commit"]), resolve(clone, args.ref))
        if git("merge-base", "--is-ancestor", up.pin, up.target, cwd=clone, check=False).returncode:
            sys.exit(f"Target {up.target} does not descend from the pinned commit {up.pin}.")
        return status(up, package) if args.command == "status" else sync(up, package)


if __name__ == "__main__":
    sys.exit(main())
