"""Gates C1 to C6: verbatim blocks, citations, frontmatter, hint marking and the fidelity ledger."""

from __future__ import annotations

import re
from collections import defaultdict

from .model import (ALL_KINDS, CARD, HINT, LEAF_KINDS, LOOKUP_PATH, NO_BOX, NO_OVERLAP, NOT_CHECKABLE,
                    TABLE_SEPARATOR, WIDE_KINDS, Doc, Result, Unit, fmt_range, int_range)
from .reports import COUNTS_START
from .resource import Resource, need_docs, verdict

LEDGER_HEADER = ["level", "choice", "reason"]
LEDGER_KEYWORDS = {"router": ("router",), "job": ("job-node",), "lookup": ("index-node",),
                   "chapter": ("chapter-node",), "section": ("section-node",)}

PLOTTING_LIBRARY = re.compile(r"\b(?:matplotlib|pyplot|seaborn|plotly|d3|vega(?:-lite)?|ggplot2?)\b|\bplt\.\w", re.I)


def gate_c1(r: Resource) -> Result:
    results = r.verbatim_results
    problems = [f"{path}:{block.line}: {problem}" for path, block, problem in results if problem]
    if r.docs and not results:
        problems.append("no verbatim blocks found; the ledger promises them in leaves and idiom cards")
    problems += need_docs(r, list(r.docs.values()), "markdown files")
    return verdict(problems, [f"{len(results)} verbatim blocks match their cited pages"])


def allowed_spans(r: Resource, doc: Doc, unit: Unit) -> list[tuple[int, int]]:
    spans = []
    if doc.kind in WIDE_KINDS and r.book_pages:
        spans.append((1, r.book_pages))
    elif doc.pdf_pages:
        spans.append(doc.pdf_pages)
    if unit.h2 in ("Related", "Children"):
        spans += [r.docs[l.path].pdf_pages for l in unit.links if l.path in r.docs and r.docs[l.path].pdf_pages]
    return spans


def gate_c2(r: Resource) -> Result:
    problems = r.missing("book") + need_docs(r, list(r.docs.values()), "markdown files")
    cited = 0
    for doc in r.docs.values():
        for unit in doc.units:
            if unit.hint or unit.kind not in ("paragraph", "item", "row") or unit.figure_line:
                continue
            if unit.text in (NO_OVERLAP, NO_BOX):
                continue
            if not unit.citations:
                problems.append(f"{doc.path}:{unit.line}: uncited {unit.kind}: {unit.text[:70]!r}")
                continue
            cited += 1
            spans = allowed_spans(r, doc, unit)
            for c in unit.citations:
                if c.first > c.last or not any(lo <= c.first and c.last <= hi for lo, hi in spans):
                    problems.append(
                        f"{doc.path}:{unit.line}: cites {fmt_range((c.first, c.last))}, outside "
                        f"{' or '.join(fmt_range(s) for s in spans) or 'any known range'}"
                    )
    return verdict(problems, [f"{cited} paragraphs, items and rows cited within range"])


def printed(r: Resource, pdf: int) -> int | None:
    for span in (r.book or {}).get("page_map", []):
        if span.get("from_pdf", 0) <= pdf <= span.get("to_pdf", -1):
            return pdf - span.get("offset", 0)
    return None


def gate_c3(r: Resource) -> Result:
    problems = need_docs(r, list(r.docs.values()), "markdown files")
    notes = []
    ids: dict[str, list[str]] = defaultdict(list)
    plan_kinds = {f["path"]: f.get("kind") for f in r.plan_files} | {c["path"]: CARD for c in r.plan_cards}
    for doc in r.docs.values():
        fm = doc.frontmatter
        if doc.error:
            problems.append(f"{doc.path}: {doc.error}")
            continue
        for key in ("id", "kind", "title", "pdf_pages", "toc", "fidelity"):
            if fm.get(key) in (None, ""):
                problems.append(f"{doc.path}: frontmatter lacks {key}")
        ids[str(doc.id)].append(doc.path)
        if doc.kind not in ALL_KINDS:
            problems.append(f"{doc.path}: unknown kind {doc.kind!r}")
        span = doc.pdf_pages
        if span is None or span[0] < 1 or (r.book_pages and span[1] > r.book_pages):
            problems.append(f"{doc.path}: pdf_pages {fm.get('pdf_pages')!r} is not an in-book [first, last] range")
        chapter_spans = [r.book_chapters[c] for c in sorted(r.chapters(doc)) if c in r.book_chapters]
        if span and doc.kind not in WIDE_KINDS and chapter_spans:
            first, last = min(s[0] for s in chapter_spans), max(s[1] for s in chapter_spans)
            if span[0] < first or span[1] > last:
                problems.append(
                    f"{doc.path}: pdf_pages {list(span)} outside chapter "
                    f"{', '.join(str(c) for c in sorted(r.chapters(doc)))} ({fmt_range((first, last))})"
                )
        if not isinstance(fm.get("toc"), list):
            problems.append(f"{doc.path}: toc is not a list")
        if fm.get("fidelity") not in ("summary", "mixed"):
            problems.append(f"{doc.path}: fidelity must be summary or mixed")
        expected_kind = {"SKILL.md": "router", LOOKUP_PATH: "index-node"}.get(doc.path)
        if doc.path.startswith("references/jobs/"):
            expected_kind = "job-node"
        elif doc.path.startswith("references/idioms/"):
            expected_kind = CARD
        expected_kind = plan_kinds.get(doc.path, expected_kind)
        if expected_kind and doc.kind != expected_kind:
            problems.append(f"{doc.path}: kind {doc.kind} but its path or the plan says {expected_kind}")
        if doc.path == "SKILL.md":
            if fm.get("name") != "data-visualisation" or not fm.get("description"):
                problems.append("SKILL.md: needs name: data-visualisation and a description")
        if doc.kind == CARD:
            if not isinstance(fm.get("boxed"), bool):
                problems.append(f"{doc.path}: boxed must be true or false")
            if not isinstance(fm.get("figures"), list):
                problems.append(f"{doc.path}: figures must be a list")
        if doc.kind in LEAF_KINDS + (CARD,) and span:
            printed_span = int_range(fm.get("printed_pages"))
            if printed_span is None:
                notes.append(f"{doc.path}: no printed_pages (SHOULD)")
            elif r.book and printed_span != (printed(r, span[0]), printed(r, span[1])):
                problems.append(f"{doc.path}: printed_pages {list(printed_span)} disagree with page_map for {list(span)}")
    problems += [f"id {i!r} is used by {', '.join(paths)}" for i, paths in ids.items() if len(paths) > 1]
    return verdict(problems, [
        f"{len(r.docs)} files carry valid metadata; every chapter-bound file's pdf_pages lies within its chapter",
    ] + notes)


def gate_c4(r: Resource) -> Result:
    problems = need_docs(r, list(r.docs.values()), "markdown files")
    for doc in r.docs.values():
        for heading in doc.headings:
            if HINT in heading.title and not (heading.level == 2 and heading.title.endswith(HINT)):
                problems.append(f"{doc.path}:{heading.line}: {HINT} may only end a ## heading")
        for unit in doc.units:
            if unit.kind == "code" and not unit.hint:
                problems.append(f"{doc.path}:{unit.line}: code block outside a {HINT} section")
            library = None if unit.hint or unit.figure_line else PLOTTING_LIBRARY.search(unit.text)
            if library:
                problems.append(f"{doc.path}:{unit.line}: names {library.group(0)!r} outside {HINT} text")
    return verdict(problems, [
        f"{HINT} ends only ## headings; no code block or plotting-library name outside {HINT} text "
        "(figure lines and verbatim blocks are book text)",
    ])


def ledger_table(text: str) -> list[list[str]]:
    """The data rows of the ledger's Level | Choice | Reason table, ignoring every other table."""
    rows, inside = [], False
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")] if line.startswith("|") else None
        if cells is None:
            inside = False
        elif [c.lower() for c in cells] == LEDGER_HEADER:
            inside = True
        elif inside and not TABLE_SEPARATOR.match(line.strip()):
            rows.append(cells)
    return rows


def ledger_kinds(level: str) -> tuple[str, ...]:
    level = level.lower()
    if "lea" in level:
        return LEAF_KINDS
    if "idiom" in level:
        return (CARD,)
    return tuple(kind for word, kinds in LEDGER_KEYWORDS.items() if word in level for kind in kinds)


def ledger_levels(r: Resource) -> tuple[list[tuple[str, str, tuple[str, ...]]], list[str]]:
    """(level, declared fidelity, kinds) per ledger row, and what is wrong with the ledger itself."""
    path = r.paths.provenance / "fidelity-ledger.md"
    if not path.is_file():
        return [], ["provenance/fidelity-ledger.md is missing"]
    text = path.read_text(encoding="utf-8")
    levels, problems = [], []
    for cells in ledger_table(text):
        if len(cells) < 3 or not all(cells[:3]):
            problems.append(f"fidelity-ledger.md: incomplete Level | Choice | Reason row {' | '.join(cells)!r}")
            continue
        declared = next((f for f in ("summary", "mixed") if cells[1].lower().startswith(f)), None)
        if declared is None:
            problems.append(f"fidelity-ledger.md: choice for '{cells[0]}' starts with neither Summary nor Mixed")
            continue
        levels.append((cells[0], declared, ledger_kinds(cells[0])))
    for kind in ALL_KINDS:
        owners = [level for level, _, kinds in levels if kind in kinds]
        if len(owners) != 1:
            problems.append(f"fidelity-ledger.md: {len(owners)} Level | Choice | Reason rows cover {kind}, needs 1")
    if COUNTS_START not in text:
        problems.append("fidelity-ledger.md: measured counts were not written")
    return levels, problems


def gate_c5(r: Resource) -> Result:
    levels, problems = ledger_levels(r)
    problems += need_docs(r, list(r.docs.values()), "markdown files")
    for doc in r.docs.values():
        fidelity = doc.frontmatter.get("fidelity")
        if fidelity == "summary" and doc.verbatims:
            problems.append(f"{doc.path}: fidelity summary but {len(doc.verbatims)} verbatim blocks")
        elif fidelity == "mixed" and not doc.verbatims:
            problems.append(f"{doc.path}: fidelity mixed but no verbatim blocks")
    counts = r.kind_counts()
    for level, declared, kinds in levels:
        if not any(kind in counts for kind in kinds):
            continue
        verbatim = sum(counts[kind]["verbatim"] for kind in kinds if kind in counts)
        summary = sum(counts[kind]["summary"] for kind in kinds if kind in counts)
        if declared == "summary" and verbatim:
            problems.append(f"fidelity-ledger.md: '{level}' declares Summary but has {verbatim:,} verbatim words")
        if declared == "mixed" and not (verbatim and summary):
            problems.append(
                f"fidelity-ledger.md: '{level}' declares Mixed but has {verbatim:,} verbatim and {summary:,} summary words"
            )
    return verdict(problems, [
        "the Level | Choice | Reason table covers every file kind once; each level's measured verbatim and "
        "summary words fit its declared Summary or Mixed choice; each file's fidelity fits its verbatim blocks",
    ])


def gate_c6(r: Resource) -> Result:
    files = r.of_kind(*LEAF_KINDS, CARD)
    units = sum(1 for d in files for u in d.units if not u.hint and u.citations)
    return Result(NOT_CHECKABLE, [
        f"{units} cited summary units across {len(files)} leaves and idiom cards",
        "Judge: compare each cited summary with its cited page text in build/pages and flag any added, "
        "resolved or contradicted claim. Start with references/**/*.md leaves and references/idioms/*.md.",
    ])
