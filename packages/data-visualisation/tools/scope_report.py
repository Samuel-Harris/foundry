"""Run every gate read-only and print only the evidence about one chapter's files.

Chapter writers run this in parallel, so it never writes to the shared
provenance directory: the checker runs against a temporary copy of it.

    uv run tools/scope_report.py 7
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

from check import PACKAGE, run
from checker.model import FAIL
from checker.resource import Paths


def chapter_paths(provenance: Path, chapter: int) -> list[str]:
    plan = json.loads((provenance / "plan.json").read_text(encoding="utf-8"))
    files = [f["path"] for f in plan["files"] if f["chapter"] == chapter]
    cards = [c["path"] for c in plan["idiom_cards"] if c["chapter"] == chapter]
    return files + cards


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("chapter", type=int)
    parser.add_argument("--skill-dir", type=Path, default=PACKAGE / ".apm" / "skills" / "data-visualisation")
    parser.add_argument("--provenance-dir", type=Path, default=PACKAGE / "provenance")
    parser.add_argument("--pages-dir", type=Path, default=PACKAGE / "build" / "pages")
    args = parser.parse_args(argv)

    owned = chapter_paths(args.provenance_dir, args.chapter)
    with tempfile.TemporaryDirectory() as tmp:
        provenance = Path(tmp) / "provenance"
        shutil.copytree(args.provenance_dir, provenance)
        results = run(Paths(args.skill_dir, provenance, args.pages_dir))

    findings = 0
    for gate, result in results.items():
        if result.status != FAIL:
            continue
        lines = [line for line in result.evidence if any(path in line for path in owned)]
        for line in lines:
            print(f"{gate} {line}")
        findings += len(lines)
    missing = [path for path in owned if not (args.skill_dir / path).is_file()]
    for path in missing:
        print(f"MISSING {path}")
    print(f"\nchapter {args.chapter}: {len(owned)} planned files, {len(missing)} missing, {findings} failing evidence lines")
    return 1 if findings or missing else 0


if __name__ == "__main__":
    sys.exit(main())
