#!/usr/bin/env python3
"""Verify the data-visualisation resource against the build rubric's gates.

Every markdown file under the skill is parsed once into a `Doc` model
(frontmatter, headings, units, verbatim blocks, links, anchors, citations).
The gates in `GATES` read that model and the provenance JSON, and each returns
PASS, FAIL or NOT-CHECKABLE with evidence lines. The script writes:

  provenance/coverage.json            F1
  provenance/reports/links.md         F2
  provenance/reports/orphans.md       F3
  provenance/reports/provenance.md    F4
  provenance/reports/self-check.md    F5
  provenance/figures.json             `referenced_by` filled in
  provenance/fidelity-ledger.md       measured counts under the ledger table

Gates that need judgement (parts of B1 and B4, and B6, C6) run their mechanical
part and otherwise report NOT-CHECKABLE with the files a judge should read.
Exit status is 1 when any gate FAILs, else 0.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Callable

from checker.gates_figures import gate_d1, gate_d2, gate_d3, gate_d4, gate_d5, gate_d6
from checker.gates_fidelity import gate_c1, gate_c2, gate_c3, gate_c4, gate_c5, gate_c6
from checker.gates_hints import gate_e1, gate_e2, gate_e3, gate_e4, gate_e5
from checker.gates_structure import (gate_a1, gate_a2, gate_a3, gate_a4, gate_a5, gate_b1, gate_b2, gate_b3, gate_b4,
                                     gate_b5, gate_b6)
from checker.model import FAIL, HEADING, LINK, LIST_ITEM, NODE_KINDS, NOT_CHECKABLE, PASS, Result, load_docs, resolve
from checker.reports import fill_referenced_by, gate_f1, gate_f2, gate_f3, gate_f4, write_reports, write_self_check
from checker.resource import Paths, Resource

PACKAGE = Path(__file__).resolve().parents[1]

SIZE_FIELD = re.compile(r"(\) · ~)([\d,]+|\?)( words\.)")

GATES: list[tuple[str, Callable[[Resource], Result]]] = [
    ("A1", gate_a1), ("A2", gate_a2), ("A3", gate_a3), ("A4", gate_a4), ("A5", gate_a5),
    ("B1", gate_b1), ("B2", gate_b2), ("B3", gate_b3), ("B4", gate_b4), ("B5", gate_b5), ("B6", gate_b6),
    ("C1", gate_c1), ("C2", gate_c2), ("C3", gate_c3), ("C4", gate_c4), ("C5", gate_c5), ("C6", gate_c6),
    ("D1", gate_d1), ("D2", gate_d2), ("D3", gate_d3), ("D4", gate_d4), ("D5", gate_d5), ("D6", gate_d6),
    ("E1", gate_e1), ("E2", gate_e2), ("E3", gate_e3), ("E4", gate_e4), ("E5", gate_e5),
    ("F1", gate_f1), ("F2", gate_f2), ("F3", gate_f3), ("F4", gate_f4),
]


def write_sizes(skill_dir: Path) -> int:
    docs = load_docs(skill_dir)
    changed = 0
    for doc in docs.values():
        if doc.kind not in NODE_KINDS:
            continue
        path = skill_dir / doc.path
        lines = path.read_text(encoding="utf-8").split("\n")
        section = ""
        for index, line in enumerate(lines):
            heading = HEADING.match(line)
            if heading and len(heading.group(1)) <= 2:
                section = heading.group(2) if len(heading.group(1)) == 2 else ""
                continue
            item = LIST_ITEM.match(line)
            link = LINK.search(line) if section == "Children" and item else None
            if not link:
                continue
            target = docs.get(resolve(doc.path, link.group(3))[0] or "")
            if target is None:
                continue
            updated = SIZE_FIELD.sub(lambda m: f"{m.group(1)}{target.words:,}{m.group(3)}", line, count=1)
            if updated != line:
                lines[index] = updated
                changed += 1
        text = "\n".join(lines)
        if text != path.read_text(encoding="utf-8"):
            path.write_text(text, encoding="utf-8")
    return changed


def run(paths: Paths, sizes: bool = False) -> dict[str, Result]:
    if sizes and paths.skill.is_dir():
        write_sizes(paths.skill)
    resource = Resource(paths)
    fill_referenced_by(resource)
    write_reports(resource)
    results = {gate: check(resource) for gate, check in GATES}
    write_self_check(resource, results)
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--skill-dir", type=Path, default=PACKAGE / ".apm" / "skills" / "data-visualisation")
    parser.add_argument("--provenance-dir", type=Path, default=PACKAGE / "provenance")
    parser.add_argument("--pages-dir", type=Path, default=PACKAGE / "build" / "pages")
    parser.add_argument("--write-sizes", action="store_true", help="rewrite ~N words in every ## Children item first")
    args = parser.parse_args(argv)
    results = run(Paths(args.skill_dir, args.provenance_dir, args.pages_dir), sizes=args.write_sizes)
    for gate, result in results.items():
        first = result.evidence[0] if result.evidence else ""
        print(f"{gate} {result.status:<13} {first}")
    tally = {status: sum(1 for r in results.values() if r.status == status) for status in (PASS, FAIL, NOT_CHECKABLE)}
    print(f"\n{tally[FAIL]} FAIL, {tally[PASS]} PASS, {tally[NOT_CHECKABLE]} NOT-CHECKABLE; "
          f"details in {args.provenance_dir / 'reports' / 'self-check.md'}")
    return 1 if tally[FAIL] else 0


if __name__ == "__main__":
    sys.exit(main())
