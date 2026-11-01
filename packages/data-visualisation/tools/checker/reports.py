"""The reports under provenance/, gates F1 to F4 that require them, and the self-check summary."""

from __future__ import annotations

from pathlib import Path

from .model import LOOKUP_PATH, Result, dump_json
from .resource import Resource, need_docs, verdict

COUNTS_START = "<!-- measured-counts:start (written by tools/check.py) -->"
COUNTS_END = "<!-- measured-counts:end -->"
EVIDENCE_CAP = 60


def report_problem(r: Resource, name: str) -> list[str]:
    return [] if name in r.written else [f"provenance/{name} was not written"]


def gate_f1(r: Resource) -> Result:
    rows, problems = r.coverage
    problems = r.missing("book") + report_problem(r, "coverage.json") + list(problems)
    if r.book is not None and not rows:
        problems.append("coverage.json has no entries")
    return verdict(problems, [f"coverage.json maps {len(rows)} entries with level, path and PDF range"])


def gate_f2(r: Resource) -> Result:
    checked, external, dead = r.link_check
    problems = report_problem(r, "reports/links.md") + dead + need_docs(r, list(r.docs.values()), "markdown files")
    return verdict(problems, [f"{checked} links resolve, {external} external links not fetched"])


def gate_f3(r: Resource) -> Result:
    problems = report_problem(r, "reports/orphans.md") + [f"{p}: orphan" for p in r.orphans]
    if "SKILL.md" not in r.docs:
        problems.append("SKILL.md is missing")
    return verdict(problems, [f"0 orphans among {len(r.docs)} files"])


def gate_f4(r: Resource) -> Result:
    problems = report_problem(r, "reports/provenance.md") + need_docs(r, list(r.docs.values()), "markdown files")
    return verdict(problems, ["provenance.md records word counts per kind and the C1 results"])


def write_reports(r: Resource) -> None:
    reports = r.paths.reports
    reports.mkdir(parents=True, exist_ok=True)

    rows, coverage_problems = r.coverage
    missing, unplanned = r.plan_drift
    dump_json(r.paths.provenance / "coverage.json", {
        "entries": rows,
        "problems": coverage_problems + r.missing("book", "plan"),
        "plan_files_missing": missing,
        "files_not_in_plan": unplanned,
    })
    r.written.add("coverage.json")

    checked, external, dead = r.link_check
    lines = ["# Link report", "", "Written by `tools/check.py`. Every relative link and image in the skill, "
             "with `#anchor` fragments checked against `<a id>` anchors.", "",
             f"- Links checked: {checked}", f"- External links (not fetched): {external}", f"- Dead links: {len(dead)}", ""]
    lines += ["## Dead links", ""] + ([f"- {d}" for d in dead] or ["None."])
    (reports / "links.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    r.written.add("reports/links.md")

    lines = ["# Orphan report", "", "Written by `tools/check.py`. Traversal starts at `SKILL.md` and follows "
             f"only `## Children` links; `{LOOKUP_PATH}` is reached but not expanded, so the tree must stand alone.", "",
             f"- Files: {len(r.docs)}", f"- Reachable: {len(r.reachable)}", f"- Orphans: {len(r.orphans)}", "",
             "## Orphans", ""] + ([f"- {p}" for p in r.orphans] or ["None."])
    (reports / "orphans.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    r.written.add("reports/orphans.md")

    table = counts_table(r)
    results = r.verbatim_results
    failed = [(p, b, e) for p, b, e in results if e]
    lines = ["# Provenance report", "", "Written by `tools/check.py`. Words per file kind, frontmatter excluded. "
             "Verbatim counts verbatim blocks; non-book counts hint sections, `[NOT FROM BOOK]` items and code; "
             "summary counts every other paragraph, list item and table row except figure lines.", ""] + table
    lines += ["", "## C1 verbatim check", "", f"- Blocks: {len(results)}", f"- Matched: {len(results) - len(failed)}",
              f"- Failed: {len(failed)}"] + ([""] + [f"- {p}:{b.line}: {e}" for p, b, e in failed] if failed else [])
    (reports / "provenance.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    r.written.add("reports/provenance.md")

    ledger = r.paths.provenance / "fidelity-ledger.md"
    if ledger.is_file():
        text = ledger.read_text(encoding="utf-8")
        block = "\n".join([COUNTS_START, "", "## Measured counts", ""] + table + ["", COUNTS_END])
        if COUNTS_START in text and COUNTS_END in text:
            head, rest = text.split(COUNTS_START, 1)
            text = head + block + rest.split(COUNTS_END, 1)[1]
        else:
            text = text.rstrip("\n") + "\n\n" + block + "\n"
        ledger.write_text(text, encoding="utf-8")


def counts_table(r: Resource) -> list[str]:
    lines = ["| Kind | Files | Verbatim words | Summary words | Non-book words |", "| --- | --- | --- | --- | --- |"]
    for kind, row in sorted(r.kind_counts().items()):
        lines.append(f"| {kind} | {row['files']} | {row['verbatim']:,} | {row['summary']:,} | {row['non-book']:,} |")
    return lines


def fill_referenced_by(r: Resource) -> None:
    if r.figures is None:
        return
    for entry in r.figures:
        entry["referenced_by"] = r.figure_refs.get(entry.get("id"), [])
    dump_json(r.paths.provenance / "figures.json", {"figures": r.figures} if r.figures_wrapped else r.figures)


def judged_summary(reports: Path) -> list[str]:
    """The judge findings behind the NOT-CHECKABLE gates, counted per gate and action."""
    tsvs = sorted((reports / "judge").glob("*.tsv"))
    if not tsvs:
        return ["", "## Judged gates", "", "- No judge records in reports/judge/."]
    counts: dict[tuple[str, str], int] = {}
    for tsv in tsvs:
        for row in tsv.read_text(encoding="utf-8").splitlines()[1:]:
            cells = row.split("\t")
            if len(cells) >= 4:
                key = (cells[0], cells[3].split(":")[0].strip())
                counts[key] = counts.get(key, 0) + 1
    lines = ["", "## Judged gates", "",
             f"Judge records: {len(tsvs)} files in `reports/judge/`; handoff resolutions in `reports/judge-handoffs.tsv`.",
             "", "| Gate | Action | Findings |", "| --- | --- | --- |"]
    lines += [f"| {gate} | {action} | {n} |" for (gate, action), n in sorted(counts.items())]
    return lines


def write_self_check(r: Resource, results: dict[str, Result]) -> None:
    def cell(text: str) -> str:
        return text.replace("|", "\\|")

    lines = ["# Self-check", "", "Written by `tools/check.py`: one row per gate of the build rubric. "
             "NOT-CHECKABLE gates passed their mechanical part and name what a judge must read.", "",
             "| Gate | Status | Evidence |", "| --- | --- | --- |"]
    for gate, result in results.items():
        first = result.evidence[0] if result.evidence else ""
        more = f" (+{len(result.evidence) - 1} more)" if len(result.evidence) > 1 else ""
        lines.append(f"| {gate} | {result.status} | {cell(first)}{more} |")
    for gate, result in results.items():
        lines += ["", f"## {gate} {result.status}", ""]
        lines += [f"- {e}" for e in result.evidence[:EVIDENCE_CAP]]
        if len(result.evidence) > EVIDENCE_CAP:
            lines.append(f"- ... and {len(result.evidence) - EVIDENCE_CAP} more")
    lines += judged_summary(r.paths.reports)
    r.paths.reports.mkdir(parents=True, exist_ok=True)
    (r.paths.reports / "self-check.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
