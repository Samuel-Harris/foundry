#!/usr/bin/env python3
"""Check that the root `apm.yml` deploys every Foundry package exactly once.

The root manifest exists so that `apm install` at the repository root deploys
every package's skills, agents and instructions into this checkout. It lists
only top-level packages, the ones no other package depends on, and reaches the
rest transitively. This script fails when:

  * a listed path is not a directory under `packages/` with an `apm.yml`;
  * a package that ships primitives (anything under `.apm/`) is not reachable
    from the root manifest, so a new package cannot be silently left out;
  * a listed package is also reachable through another listed package. APM
    0.32.0 then records it twice in the root lockfile, and `apm audit --ci`
    fails with `ambiguous resolved_by parent` once that package parents a third.

Meta-packages that ship no primitives of their own, such as `default-stack`,
are not required: everything they install is reached through its own package.

The manifests are parsed with the same `path:` line grammar the pre-commit hook
uses, so the script needs no third-party modules. Exit status is 0 when every
check passes and 1 otherwise.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGES = REPO_ROOT / "packages"
ROOT_PATH = re.compile(r"^\s*-\s*path:\s*\./packages/([a-z0-9-]+)\s*$")
SIBLING_PATH = re.compile(r"^\s*-\s*path:\s*\.\./([a-z0-9-]+)\s*$")


def path_dependencies(manifest: Path, grammar: re.Pattern[str]) -> list[str]:
    lines = manifest.read_text(encoding="utf-8").splitlines()
    return [match.group(1) for line in lines if (match := grammar.match(line))]


def reachable_from(name: str, graph: dict[str, list[str]]) -> set[str]:
    seen: set[str] = set()
    queue = list(graph.get(name, []))
    while queue:
        dep = queue.pop()
        if dep not in seen:
            seen.add(dep)
            queue.extend(graph.get(dep, []))
    return seen


def ships_primitives(package: Path) -> bool:
    apm_dir = package / ".apm"
    return apm_dir.is_dir() and any(path.is_file() for path in apm_dir.rglob("*"))


def main() -> int:
    root_manifest = REPO_ROOT / "apm.yml"
    if not root_manifest.is_file():
        print("check_root_manifest: apm.yml is missing at the repository root")
        return 1

    packages = sorted(path.parent.name for path in PACKAGES.glob("*/apm.yml"))
    graph = {
        name: path_dependencies(PACKAGES / name / "apm.yml", SIBLING_PATH)
        for name in packages
    }
    listed = path_dependencies(root_manifest, ROOT_PATH)
    errors: list[str] = []

    for name in listed:
        if name not in graph:
            errors.append(f"./packages/{name} is listed but has no apm.yml")

    reached: set[str] = set(listed)
    for name in listed:
        transitive = reachable_from(name, graph)
        reached |= transitive
        for other in listed:
            if other in transitive:
                errors.append(
                    f"./packages/{other} is listed but is already reached through "
                    f"{name}; remove it so the root lockfile records it once"
                )

    for name in packages:
        if name not in reached and ships_primitives(PACKAGES / name):
            errors.append(
                f"packages/{name} is not reachable from the root apm.yml; add "
                f"`- path: ./packages/{name}` unless another listed package "
                "depends on it"
            )

    for error in errors:
        print(f"check_root_manifest: {error}")
    if errors:
        return 1
    print(f"check_root_manifest: {len(listed)} listed, {len(reached)} reached")
    return 0


if __name__ == "__main__":
    sys.exit(main())
