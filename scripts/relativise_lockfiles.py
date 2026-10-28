#!/usr/bin/env python3
"""Record sibling-package paths in lockfiles relative to each package.

APM 0.32.0 relativises a local dependency's identity against the project root
only when the dependency sits inside it. Every Foundry package is its own
project root and its siblings sit beside it, so a transitive sibling is
recorded by absolute checkout path, both as `anchored_local_path` and as
`local:` deployment owners. That leaks the authoring machine's path and makes
every install at another root rewrite the lockfile.

This rewrites those absolute paths to paths relative to the lockfile's
directory, such as `../explore`. Both fields must change together:
`apm audit --ci` rejects a relative owner whose `anchored_local_path` is still
absolute. Paths outside the repository are left alone.

Usage: relativise_lockfiles.py LOCKFILE...
Exit status is 0 on success, 1 when a lockfile is missing.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ABSOLUTE_PATH = re.compile(r"(?P<key>local:|anchored_local_path: )(?P<path>/\S+)")


def relativise(text: str, package_dir: Path) -> str:
    def replace(match: re.Match[str]) -> str:
        path = Path(match["path"])
        if not path.resolve().is_relative_to(REPO_ROOT):
            return match[0]
        return match["key"] + Path(os.path.relpath(path.resolve(), package_dir)).as_posix()

    return ABSOLUTE_PATH.sub(replace, text)


def main(argv: list[str]) -> int:
    status = 0
    for name in argv:
        lockfile = Path(name)
        if not lockfile.is_file():
            print(f"relativise_lockfiles: {lockfile} not found", file=sys.stderr)
            status = 1
            continue
        text = lockfile.read_text(encoding="utf-8")
        updated = relativise(text, lockfile.resolve().parent)
        if updated != text:
            lockfile.write_text(updated, encoding="utf-8")
    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
