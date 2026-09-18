#!/usr/bin/env python3
"""Secret scan over the working tree and packed archives.

Tier 1 requires the scan to cover more than tracked files, so it scans tracked
*and* untracked (unignored) working-tree files — a credential in a
not-yet-committed file is caught — plus every file under `packages/*/dist`.
Archives are scanned member-by-member so a credential cannot hide inside a
bundle that is never extracted by the scan. Files that are unreadable or larger
than `MAX_SCAN_BYTES` are reported as skipped rather than counted as clean.

Exit status is 0 when nothing matches, 1 when a pattern matches.
"""

from __future__ import annotations

import re
import subprocess
import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DIST_GLOB = "packages/*/dist/*.zip"

PATTERNS = (
    ("private-key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("aws-access-key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("github-token", re.compile(r"gh[pousr]_[A-Za-z0-9]{36}")),
    ("slack-token", re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}")),
    ("openai-key", re.compile(r"sk-[A-Za-z0-9]{32,}")),
    ("anthropic-key", re.compile(r"sk-ant-[A-Za-z0-9_-]{20,}")),
    ("google-api-key", re.compile(r"AIza[0-9A-Za-z\-_]{35}")),
)

MAX_SCAN_BYTES = 2_000_000


def scanned_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return [REPO_ROOT / name for name in result.stdout.split("\0") if name]


def scan_text(text: str, label: str, findings: list[str]) -> None:
    for name, pattern in PATTERNS:
        match = pattern.search(text)
        if match:
            findings.append(f"{label}: {name} -> {match.group(0)[:12]}...")


def scan_file(path: Path, findings: list[str], skipped: list[str]) -> None:
    try:
        if path.stat().st_size > MAX_SCAN_BYTES:
            skipped.append(f"{path} (over {MAX_SCAN_BYTES // 1_000_000} MB)")
            return
        scan_text(path.read_text(encoding="utf-8", errors="ignore"), str(path), findings)
    except OSError as error:
        skipped.append(f"{path} ({error})")


def scan_archive(path: Path, findings: list[str], skipped: list[str]) -> None:
    try:
        with zipfile.ZipFile(path) as archive:
            for member in archive.namelist():
                if member.endswith("/"):
                    continue
                with archive.open(member) as handle:
                    data = handle.read(MAX_SCAN_BYTES + 1)
                if len(data) > MAX_SCAN_BYTES:
                    skipped.append(f"{path}::{member} (over {MAX_SCAN_BYTES // 1_000_000} MB)")
                    continue
                scan_text(data.decode("utf-8", errors="ignore"), f"{path}::{member}", findings)
    except (OSError, zipfile.BadZipFile) as error:
        findings.append(f"{path}: unreadable archive ({error})")


def main() -> int:
    findings: list[str] = []
    skipped: list[str] = []
    count = 0

    for path in scanned_files():
        if path.is_file():
            count += 1
            scan_file(path, findings, skipped)

    for archive_path in sorted(REPO_ROOT.glob(DIST_GLOB)):
        count += 1
        scan_archive(archive_path, findings, skipped)

    for dist_dir in sorted(REPO_ROOT.glob("packages/*/dist")):
        for path in sorted(dist_dir.rglob("*")):
            if path.is_file() and path.suffix != ".zip":
                count += 1
                scan_file(path, findings, skipped)

    coverage = f"across {count} working-tree and dist file(s)"
    if skipped:
        coverage += f", {len(skipped)} skipped as unreadable or oversized"

    if findings:
        for finding in findings:
            print(f"[x] {finding}")
        print(f"\n[x] {len(findings)} potential secret(s) {coverage}")
        return 1

    print(f"[+] no secrets detected {coverage}")
    for item in skipped:
        print(f"[!] not scanned: {item}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
