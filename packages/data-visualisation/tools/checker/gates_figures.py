"""Gates D1 to D6: figure lines, the figures.json manifest and the extracted image files."""

from __future__ import annotations

import re

from .model import CARD, LEAF_KINDS, Result
from .resource import Resource, need_docs, verdict

FIGURE_KEYS = ("caption", "dpi", "file", "id", "method", "number", "pdf_page", "reason", "referenced_by")
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

FIGURE_ITEM = re.compile(
    r"^!\[Figure (?P<n1>\d+\.\d+)\]\((?P<target>[^)\s]+)\) \*\*Figure (?P<n2>\d+\.\d+)\*\* "
    r"\[p\.(?P<page>\d+)\]\. (?P<caption>.+)$"
)

AUTOLINK = re.compile(r"<(https?://[^>\s]+)>")  # figure_lines.py wraps bare URLs for markdownlint MD034
FIGURE_ID = re.compile(r"^fig-(\d\d)-(\d\d)([a-z])?$")


def gate_d1(r: Resource) -> Result:
    problems = r.missing("book", "figures", "plan")
    figures = {f.get("id"): f for f in r.figures or []}
    if r.book is not None and not (r.book or {}).get("figures"):
        problems.append("book.json lists no figures")
    for doc in r.docs.values():
        for unit in doc.units:
            if not any(l.image for l in unit.links):
                continue
            match = FIGURE_ITEM.match(unit.text) if unit.figure_line else None
            if not match:
                problems.append(f"{doc.path}:{unit.line}: image is not a '## Figures' item with number, page and caption")
                continue
            if match.group("n1") != match.group("n2"):
                problems.append(f"{doc.path}:{unit.line}: alt text and bold label name different figures")
            entry = r.figure_by_file.get(unit.links[0].path)
            if entry is None:
                problems.append(f"{doc.path}:{unit.line}: image {match.group('target')} is not a figure in figures.json")
                continue
            if match.group("n1") != entry.get("number"):
                problems.append(f"{doc.path}:{unit.line}: labelled Figure {match.group('n1')}, but {entry.get('id')} is Figure {entry.get('number')}")
            shown = AUTOLINK.sub(r"\1", match.group("caption"))
            if " ".join(shown.split()) != " ".join(str(entry.get("caption")).split()):
                problems.append(f"{doc.path}:{unit.line}: caption of Figure {match.group('n1')} differs from figures.json")
            if int(match.group("page")) != entry.get("pdf_page"):
                problems.append(f"{doc.path}:{unit.line}: Figure {match.group('n1')} cites p.{match.group('page')}, figures.json says p.{entry.get('pdf_page')}")
    homes = (r.plan or {}).get("figure_homes", {})
    for fig_id, entry in figures.items():
        if not entry.get("file"):
            continue
        refs = r.figure_refs.get(fig_id, [])
        if not any(r.docs[p].kind in LEAF_KINDS + (CARD,) for p in refs):
            problems.append(f"{fig_id}: not referenced by any leaf or idiom card")
        for home in homes.get(fig_id, []) if isinstance(homes, dict) else []:
            if home in r.docs and home not in refs:
                problems.append(f"{home}: plan homes {fig_id} here but the file does not reference it")
    return verdict(problems, [f"{len(r.figure_refs)} figures referenced with matching number, page and caption"])


def gate_d2(r: Resource) -> Result:
    problems = r.missing("book", "figures")
    book = {f.get("id"): f for f in (r.book or {}).get("figures", []) if isinstance(f, dict)}
    seen = set()
    for entry in r.figures or []:
        fig_id = entry.get("id")
        problems += [f"figures.json {fig_id}: lacks {key}" for key in FIGURE_KEYS if key not in entry]
        if fig_id in seen:
            problems.append(f"figures.json: {fig_id} listed twice")
        seen.add(fig_id)
        source = book.get(fig_id)
        if source and (source.get("pdf_page"), source.get("caption")) != (entry.get("pdf_page"), entry.get("caption")):
            problems.append(f"figures.json {fig_id}: page or caption differs from book.json")
        if entry.get("referenced_by") != r.figure_refs.get(fig_id, []):
            problems.append(f"figures.json {fig_id}: referenced_by is stale")
    return verdict(problems, [f"{len(seen)} manifest entries with number, page, file, caption and referencing files"])


def gate_d3(r: Resource) -> Result:
    problems = r.missing("figures")
    for entry in r.figures or []:
        method, dpi = entry.get("method"), entry.get("dpi")
        if entry.get("file"):
            if method not in ("embedded", "crop"):
                problems.append(f"figures.json {entry.get('id')}: file without method embedded or crop")
            if method == "crop" and not (isinstance(dpi, int) and dpi >= 150):
                problems.append(f"figures.json {entry.get('id')}: crop at {dpi} DPI, needs at least 150")
        elif method is not None:
            problems.append(f"figures.json {entry.get('id')}: method {method} but no file")
    return verdict(problems, ["every extracted figure records embedded or a crop of at least 150 DPI"])


def gate_d4(r: Resource) -> Result:
    problems = r.missing("book", "figures")
    listed = {f.get("id") for f in r.figures or []}
    for figure in (r.book or {}).get("figures", []):
        if isinstance(figure, dict) and figure.get("id") not in listed:
            problems.append(f"{figure.get('id')} (Figure {figure.get('number')}): in book.json, not in figures.json")
    unextracted = 0
    for entry in r.figures or []:
        file = entry.get("file")
        if file is None:
            unextracted += 1
            if not str(entry.get("reason") or "").strip():
                problems.append(f"figures.json {entry.get('id')}: no file and no reason")
        elif not (r.paths.skill / file).is_file():
            problems.append(f"figures.json {entry.get('id')}: file {file} does not exist")
    return verdict(problems, [f"{len(listed)} figures; {unextracted} unextracted, each with a reason"])


def gate_d5(r: Resource) -> Result:
    cards = r.of_kind(CARD)
    problems = r.missing("plan", "figures") + need_docs(r, cards, "idiom cards")
    known = {f.get("id") for f in r.figures or []}
    for card in cards:
        declared = card.frontmatter.get("figures")
        wanted = set(declared if isinstance(declared, list) else [])
        wanted |= set(r.plan_card_by_path.get(card.path, {}).get("figures") or [])
        shown = {
            r.figure_by_file[u.links[0].path]["id"]
            for u in card.section("Figures") if u.figure_line and u.links and u.links[0].path in r.figure_by_file
        }
        problems += [f"{card.path}: does not show {f}" for f in sorted(wanted - shown)]
        problems += [f"{card.path}: {f} is not in figures.json" for f in sorted(wanted - known)]
    return verdict(problems, [f"{len(cards)} idiom cards show their planned figures"])


def gate_d6(r: Resource) -> Result:
    problems = r.missing("figures")
    for entry in r.figures or []:
        fig_id, file = str(entry.get("id")), entry.get("file")
        if not FIGURE_ID.match(fig_id):
            problems.append(f"figures.json: id {fig_id} is not fig-NN-MM")
        if file and file != f"assets/figures/{fig_id}.png":
            problems.append(f"figures.json {fig_id}: file {file} is not assets/figures/{fig_id}.png")
        if file and (r.paths.skill / file).is_file():
            with (r.paths.skill / file).open("rb") as handle:
                if handle.read(8) != PNG_SIGNATURE:
                    problems.append(f"{file}: not a PNG")
    images = 0
    for doc in r.docs.values():
        for unit, link in doc.links:
            if link.image:
                images += 1
                reason = r.dead_reason(link) if link.path else "external image"
                if reason:
                    problems.append(f"{doc.path}:{unit.line}: image {link.target} ({reason})")
    return verdict(problems, [f"{images} image links resolve; file names follow fig-NN-MM"])
