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

APM also materialises such a dependency under `apm_modules/_local/<slot>/`,
where the slot is the first 12 hex digits of the sha256 of
`anchored_local_path`, and rewrites cross-skill links into that directory. A
deployed file's text, and so its hash in `deployed_file_hashes` and in its
deployment's `content_hash`, then depend on the checkout path. Each affected
hash is replaced with the hash the file would have if APM had materialised the
dependency from the relative path. That reads the deployed files, so run this
straight after `apm install`. It fails when a deployed file is missing or no
longer matches its recorded hash, rather than leave a checkout-dependent hash.

Usage: relativise_lockfiles.py LOCKFILE...
Exit status is 0 on success, 1 when a lockfile is missing or its deployed
files do not match it.
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
# YAML writes a key longer than 128 characters in the explicit `? key` / `: value` form.
DEPLOYED_FILE_HASH = re.compile(
    r"^\s+(?:\? (?P<long_file>\S+)\n\s+: |(?P<file>[^\s:?]+): )(?P<hash>sha256:[0-9a-f]{64})$",
    re.MULTILINE,
)
HASH = re.compile(r"sha256:[0-9a-f]{64}")


class StaleDeploymentError(Exception):
    def __init__(self, *, deployed_file: Path) -> None:
        super().__init__("deployed file is missing or does not match the lockfile")
        self.deployed_file = deployed_file


def relative_to_package(*, path: Path, package_dir: Path) -> str | None:
    """Return `path` relative to `package_dir`, or None when it lies outside the repository."""
    if not path.resolve().is_relative_to(REPO_ROOT):
        return None
    return Path(os.path.relpath(path.resolve(), package_dir)).as_posix()


def relativise(text: str, package_dir: Path) -> str:
    def replace(match: re.Match[str]) -> str:
        relative = relative_to_package(path=Path(match["path"]), package_dir=package_dir)
        return match[0] if relative is None else match["key"] + relative

    return ABSOLUTE_PATH.sub(replace, text)


def slot_marker(anchor: str) -> bytes:
    return f"_local/{hashlib.sha256(anchor.encode('utf-8')).hexdigest()[:12]}/".encode("utf-8")


def slot_renames(*, text: str, package_dir: Path) -> dict[bytes, bytes]:
    renames: dict[bytes, bytes] = {}
    for match in ABSOLUTE_ANCHOR.finditer(text):
        relative = relative_to_package(path=Path(match["path"]), package_dir=package_dir)
        if relative is not None:
            renames[slot_marker(match["path"])] = slot_marker(relative)
    return renames


def sha256(content: bytes) -> str:
    return "sha256:" + hashlib.sha256(content).hexdigest()


def rehash_slot_links(*, text: str, renames: dict[bytes, bytes], package_dir: Path) -> str:
    if not renames:
        return text
    new_hashes: dict[str, str] = {}
    for match in DEPLOYED_FILE_HASH.finditer(text):
        name = match["long_file"] or match["file"]
        if name == "content_hash":
            continue
        deployed = package_dir / name
        if not deployed.is_file():
            raise StaleDeploymentError(deployed_file=deployed)
        content = deployed.read_bytes()
        if sha256(content) != match["hash"]:
            raise StaleDeploymentError(deployed_file=deployed)
        renamed = content
        for absolute_slot, relative_slot in renames.items():
            renamed = renamed.replace(absolute_slot, relative_slot)
        if renamed != content:
            new_hashes[match["hash"]] = sha256(renamed)
    return HASH.sub(lambda match: new_hashes.get(match[0], match[0]), text)


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
        renames = slot_renames(text=text, package_dir=package_dir)
        try:
            rehashed = rehash_slot_links(text=text, renames=renames, package_dir=package_dir)
        except StaleDeploymentError as error:
            print(
                f"relativise_lockfiles: {error.deployed_file} is missing or does not match "
                f"{lockfile}; run apm install again first",
                file=sys.stderr,
            )
            status = 1
            continue
        updated = relativise(rehashed, package_dir)
        if updated != text:
            lockfile.write_text(updated, encoding="utf-8")
    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
