#!/usr/bin/env python3
"""Record sibling-package paths in lockfiles relative to each package.

APM 0.32.0 relativises a local dependency's identity against the project root
only when the dependency sits inside it. Every Foundry package is its own
project root and its siblings sit beside it, so a transitive sibling is
recorded by absolute checkout path, both as `anchored_local_path` and as
`local:` deployment owners. That leaks the authoring machine's path and makes
every install at another root rewrite the lockfile.

This rewrites those absolute paths to paths relative to the lockfile's
directory, such as `../deep-interview`. Both fields must change together:
`apm audit --ci` rejects a relative owner whose `anchored_local_path` is still
absolute. Paths outside the repository are left alone.

APM also materialises such a dependency under
`apm_modules/_local/<first 12 hex of sha256(anchored_local_path)>/` and
rewrites cross-skill links into that directory, so a deployed file's text, and
its `sha256:` hash in the lockfile, depend on the checkout path too. Each such
hash is replaced with the hash the file has when its links name the directory
of the relative path instead. That reads the deployed files, so run this after
`apm install`, before anything removes them.

Usage: relativise_lockfiles.py LOCKFILE...
Exit status is 0 on success, 1 when a lockfile is missing.
"""

from __future__ import annotations

import hashlib
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ABSOLUTE_PATH = re.compile(r"(?P<key>local:|anchored_local_path: )(?P<path>/\S+)")
ABSOLUTE_ANCHOR = re.compile(r"anchored_local_path: (?P<path>/\S+)")
DEPLOYED_FILE_HASH = re.compile(r"^\s+(?P<file>[^\s:]+): (?P<hash>sha256:[0-9a-f]{64})$", re.MULTILINE)


def relative_to_package(path: Path, package_dir: Path) -> str | None:
    if not path.resolve().is_relative_to(REPO_ROOT):
        return None
    return Path(os.path.relpath(path.resolve(), package_dir)).as_posix()


def relativise(text: str, package_dir: Path) -> str:
    def replace(match: re.Match[str]) -> str:
        relative = relative_to_package(Path(match["path"]), package_dir)
        return match[0] if relative is None else match["key"] + relative

    return ABSOLUTE_PATH.sub(replace, text)


def materialised_dir(anchor: str) -> bytes:
    return f"_local/{hashlib.sha256(anchor.encode('utf-8')).hexdigest()[:12]}/".encode("utf-8")


def rehash_materialised_links(*, text: str, package_dir: Path) -> str:
    renames = {}
    for match in ABSOLUTE_ANCHOR.finditer(text):
        relative = relative_to_package(Path(match["path"]), package_dir)
        if relative is not None:
            renames[materialised_dir(match["path"])] = materialised_dir(relative)

    updated = text
    for match in DEPLOYED_FILE_HASH.finditer(text):
        deployed = package_dir / match["file"]
        if not deployed.is_file():
            continue
        content = deployed.read_bytes()
        renamed = content
        for absolute_dir, relative_dir in renames.items():
            renamed = renamed.replace(absolute_dir, relative_dir)
        if renamed != content:
            updated = updated.replace(match["hash"], "sha256:" + hashlib.sha256(renamed).hexdigest())
    return updated


def main(argv: list[str]) -> int:
    status = 0
    for name in argv:
        lockfile = Path(name)
        if not lockfile.is_file():
            print(f"relativise_lockfiles: {lockfile} not found", file=sys.stderr)
            status = 1
            continue
        text = lockfile.read_text(encoding="utf-8")
        package_dir = lockfile.resolve().parent
        updated = relativise(rehash_materialised_links(text=text, package_dir=package_dir), package_dir)
        if updated != text:
            lockfile.write_text(updated, encoding="utf-8")
    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
