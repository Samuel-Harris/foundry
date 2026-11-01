"""Extract page text and the book model (provenance/book.json) from the source PDF.

Usage: uv run tools/extract.py --pdf PATH   (or set $VIS_PDF)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1]
BUILD_PAGES = PACKAGE / "build" / "pages"
BOOK_JSON = PACKAGE / "provenance" / "book.json"

TOC_PDF_PAGES = range(6, 15)
FIRST_BODY_PDF = 26
BODY_OFFSET = 25
FRONT_OFFSET = 1
RUNNING_HEADER_MAX_Y = 55.0
FOOTER_MIN_Y = 600.0
MARGIN_LEFT_MAX_X = 172.0
MARGIN_RIGHT_MIN_X = 372.0

LEVELS = ("chapter", "section", "subsection", "subsubsection")
TOC_NUMBERED = re.compile(r"^(\d+(?:\.\d+)*)\s+(.+?)\s+(\d+)$")
TOC_EXAMPLE = re.compile(r"^Example:\s+(.+?)\s+(\d+)$")
TOC_TRAILING_PAGE = re.compile(r"\s(\d+|[ivxlc]+)$")
FIGURE_START = re.compile(r"^Figure\s+(\d+)\.(\d+)\.\s*")
SECTION_REF = re.compile(
    r"Sec(?:-\n?)?tions?\s+(\d+(?:\.\d+)+)((?:\s*(?:,|and|,\s*and)\s+\d+(?:\.\d+)+)*)"
)
NUMBER = re.compile(r"\d+(?:\.\d+)+")


# ---------------------------------------------------------------- pure helpers


def page_map_for(page_count: int) -> list[dict]:
    return [
        {"from_pdf": 1, "to_pdf": FIRST_BODY_PDF - 1, "offset": FRONT_OFFSET, "style": "roman"},
        {"from_pdf": FIRST_BODY_PDF, "to_pdf": page_count, "offset": BODY_OFFSET, "style": "arabic"},
    ]


def printed_to_pdf(page_map: list[dict], printed: int, style: str = "arabic") -> int:
    for seg in page_map:
        if seg["style"] == style:
            pdf = printed + seg["offset"]
            if seg["from_pdf"] <= pdf <= seg["to_pdf"]:
                return pdf
    raise ValueError(f"printed page {printed} ({style}) is outside the page map")


def pdf_to_printed(page_map: list[dict], pdf: int) -> int:
    for seg in page_map:
        if seg["from_pdf"] <= pdf <= seg["to_pdf"]:
            return pdf - seg["offset"]
    raise ValueError(f"PDF page {pdf} is outside the page map")


def slugify(text: str) -> str:
    text = text.replace("ﬁ", "fi").replace("ﬂ", "fl").replace("+", " ")
    text = re.sub(r"[’'`]", "", text)
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def toc_id(number: str) -> str:
    parts = number.split(".")
    return ("ch" if len(parts) == 1 else "s") + ".".join(f"{int(p):02d}" for p in parts)


def parse_toc_row(text: str) -> dict | None:
    """One joined TOC row -> a partial entry, or None for rows that are not chapter content."""
    text = re.sub(r"\s+", " ", text).strip()
    m = TOC_EXAMPLE.match(text)
    if m:
        title, page = m.groups()
        return {"level": "idiom", "number": None, "title": title, "id": f"idiom:{slugify(title)}",
                "printed_page": int(page)}
    m = TOC_NUMBERED.match(text)
    if m:
        number, title, page = m.groups()
        depth = number.count(".")
        if depth >= len(LEVELS):
            raise ValueError(f"TOC row deeper than {LEVELS[-1]}: {text!r}")
        return {"level": LEVELS[depth], "number": number, "title": title, "id": toc_id(number),
                "printed_page": int(page)}
    return None


def join_toc_rows(rows: list[str]) -> list[str]:
    """Merge a wrapped TOC title (a row with no trailing page number) into the next row."""
    out: list[str] = []
    pending = ""
    for row in rows:
        row = (pending + " " + row).strip() if pending else row.strip()
        if TOC_TRAILING_PAGE.search(row):
            out.append(row)
            pending = ""
        else:
            pending = row
    if pending:
        out.append(pending)
    return out


def assign_parents(entries: list[dict]) -> None:
    stack: dict[str, str] = {}
    last_numbered: str | None = None
    for e in entries:
        if e["level"] == "idiom":
            e["parent"] = last_numbered
            continue
        depth = LEVELS.index(e["level"])
        e["parent"] = stack.get(LEVELS[depth - 1]) if depth else None
        stack[e["level"]] = e["id"]
        for deeper in LEVELS[depth + 1:]:
            stack.pop(deeper, None)
        last_numbered = e["id"]


def resolve_section_refs(text: str, known_ids: set[str]) -> list[tuple[int, str, str | None]]:
    """Find "Section x.y" references; return (offset, number, toc id or None if unknown)."""
    refs = []
    for m in SECTION_REF.finditer(text):
        numbers = [(m.start(), m.group(1))]
        numbers += [(m.start(), n) for n in NUMBER.findall(m.group(2) or "")]
        for offset, number in numbers:
            ident = toc_id(number)
            refs.append((offset, number, ident if ident in known_ids else None))
    return refs


@dataclass(frozen=True)
class Line:
    x0: float
    y0: float
    x1: float
    y1: float
    text: str
    font: str
    size: float

    @property
    def bold(self) -> bool:
        return "Bold" in self.font


def merge_row(lines: list[Line]) -> str:
    return " ".join(l.text for l in sorted(lines, key=lambda l: l.x0)).strip()


def group_rows(lines: list[Line], tol: float = 3.0) -> list[list[Line]]:
    rows: list[list[Line]] = []
    for line in sorted(lines, key=lambda l: (round(l.y0, 1), l.x0)):
        if rows and abs(rows[-1][0].y0 - line.y0) <= tol:
            rows[-1].append(line)
        else:
            rows.append([line])
    return rows


def parse_idiom_box(lines: list[Line], divider_x: float, rules: list[float]) -> list[tuple[str, str]]:
    """Box lines below the name row -> ordered (label, value) fields.

    `rules` are the y positions of the horizontal rules that separate rows, top to bottom;
    the last one is the box bottom. Value text keeps the PDF's line breaks.
    """
    fields: list[tuple[str, str]] = []
    for top, bottom in zip(rules, rules[1:]):
        inside = [l for l in lines if top - 1 <= (l.y0 + l.y1) / 2 < bottom]
        label = merge_row([l for l in inside if l.x0 < divider_x])
        value_rows = group_rows([l for l in inside if l.x0 >= divider_x])
        value = "\n".join(merge_row(r) for r in value_rows)
        if label or value:
            fields.append((label, value))
    return fields


def dehyphenate_lines(lines: list[str], vocabulary: set[str]) -> str:
    """Join wrapped lines with spaces. A line-end hyphen is a soft break (dropped) when the
    joined word occurs unbroken elsewhere in the book, otherwise a real hyphen (kept)."""
    out = ""
    for line in lines:
        line = line.strip()
        if not out:
            out = line
            continue
        m = re.search(r"(\w+)-$", out)
        if m and line[:1].isalpha():
            nxt = re.match(r"\w+", line).group()
            joined = (m.group(1) + nxt).lower()
            out = out[:-1] + line if joined in vocabulary else out + line
        else:
            out = out + " " + line
    return out


def vocabulary_of(texts: list[str]) -> set[str]:
    """Lower-cased words that appear unbroken (not split by a line-end hyphen)."""
    words: set[str] = set()
    for text in texts:
        text = re.sub(r"\w+-\n\w+", " ", text)
        words.update(w.lower() for w in re.findall(r"\w+", text))
    return words


def compose_page_text(lines: list[tuple[float, float, float, float, str]], margin_left: bool) -> str:
    """Body column text, then margin notes after a blank line, each in reading order.

    Running heads and page numbers (above RUNNING_HEADER_MAX_Y or below FOOTER_MIN_Y) are
    dropped. `margin_left` is true on even printed pages, whose sidenotes sit left of the
    body. Fragments on one baseline (justified sidenote words) are joined with a space."""
    columns: dict[bool, list[list]] = {False: [], True: []}
    for x0, y0, x1, y1, text in lines:
        if y1 <= RUNNING_HEADER_MAX_Y or y0 >= FOOTER_MIN_Y:
            continue
        in_margin = x1 <= MARGIN_LEFT_MAX_X if margin_left else x0 >= MARGIN_RIGHT_MIN_X
        rows = columns[in_margin]
        if rows and abs(rows[-1][0] - y0) < 2 and x0 >= rows[-1][1]:
            rows[-1][1] = x1
            rows[-1][2] += " " + text.strip()
        else:
            rows.append([y0, x1, text.strip()])
    body = "".join(r[2] + "\n" for r in columns[False])
    margin = "".join(r[2] + "\n" for r in columns[True])
    return body + ("\n" + margin if margin else "")


# ---------------------------------------------------------------- PDF access


def page_text(page) -> str:
    lines = [(l.x0, l.y0, l.x1, l.y1, l.text) for l in page_lines(page)]
    return compose_page_text(lines, margin_left=(page.number + 1) % 2 == 1)


def page_lines(page) -> list[Line]:
    lines = []
    for block in page.get_text("dict")["blocks"]:
        for raw in block.get("lines", []):
            spans = raw["spans"]
            text = "".join(s["text"] for s in spans)
            if not text.strip():
                continue
            x0, y0, x1, y1 = raw["bbox"]
            lines.append(Line(x0, y0, x1, y1, text, spans[0]["font"], round(spans[0]["size"], 1)))
    return lines


def parse_toc(doc) -> list[dict]:
    rows: list[str] = []
    for pdf in TOC_PDF_PAGES:
        lines = [l for l in page_lines(doc[pdf - 1]) if RUNNING_HEADER_MAX_Y < l.y0 < FOOTER_MIN_Y]
        for row in group_rows(lines):
            text = re.sub(r"(\s*\.)+\s*(?=\S+$)", " ", merge_row(row))
            rows.append(re.sub(r"\s+", " ", text))
    entries = []
    for row in join_toc_rows(rows):
        entry = parse_toc_row(row)
        if entry:
            entries.append(entry)
    seen: set[str] = set()
    for e in entries:
        if e["id"] in seen:
            raise ValueError(f"duplicate TOC id {e['id']}")
        seen.add(e["id"])
    assign_parents(entries)
    return entries


def locate_headings(doc, entries: list[dict], page_map: list[dict]) -> dict[str, tuple[int, float]]:
    """Find each entry's heading in the body: (pdf page, y). Chapters start at the top of
    their first page (the overview figure page)."""
    where: dict[str, tuple[int, float]] = {}
    cache: dict[int, list[Line]] = {}
    for e in entries:
        start = printed_to_pdf(page_map, e["printed_page"])
        if e["level"] == "chapter":
            where[e["id"]] = (start, 0.0)
            continue
        found = None
        for pdf in (start, start + 1, start - 1):
            lines = cache.setdefault(pdf, page_lines(doc[pdf - 1]))
            for l in lines:
                if not l.bold:
                    continue
                t = l.text.strip()
                if e["level"] == "idiom":
                    if t.startswith("Example:") and slugify(t[len("Example:"):]) == e["id"][len("idiom:"):]:
                        found = (pdf, l.y0)
                elif t == e["number"] and l.size >= 10:
                    found = (pdf, l.y0)
                if found:
                    break
            if found:
                break
        if not found:
            raise ValueError(f"heading for {e['id']} {e['title']!r} not found near PDF p.{start}")
        where[e["id"]] = found
    return where


def first_body_y(lines: list[Line]) -> float:
    ys = [l.y0 for l in lines if l.y0 > RUNNING_HEADER_MAX_Y]
    return min(ys) if ys else float("inf")


def compute_ranges(doc, entries: list[dict], where: dict[str, tuple[int, float]], last_body_pdf: int) -> None:
    def end_before(pos: tuple[int, float]) -> int:
        page, y = pos
        if y == 0.0 or y <= first_body_y(page_lines(doc[page - 1])) + 1:
            return page - 1
        return page

    for i, e in enumerate(entries):
        e["pdf_start"] = where[e["id"]][0]
        nxt = None
        for later in entries[i + 1:]:
            if e["level"] == "idiom" or (later["level"] != "idiom"
                                          and LEVELS.index(later["level"]) <= LEVELS.index(e["level"])):
                nxt = later
                break
        e["pdf_end"] = max(e["pdf_start"], end_before(where[nxt["id"]])) if nxt else last_body_pdf


def position_index(entries: list[dict], where: dict[str, tuple[int, float]]):
    numbered = sorted((where[e["id"]], e) for e in entries if e["level"] != "idiom")

    def owner(page: int, y: float) -> dict | None:
        current = None
        for pos, e in numbered:
            if pos <= (page, y):
                current = e
            else:
                break
        return current

    return owner


def box_continuation(page) -> list[tuple[str, str]]:
    """Fields of the box that opens the page without its own name row: the remainder of a
    box broken at the foot of the previous page. Its first field has an empty label when
    the break fell inside a field."""
    segs = [d["rect"] for d in page.get_drawings()]
    verticals = sorted((r for r in segs if r.width < 1.5 and r.height > 3), key=lambda r: r.y0)
    if not verticals:
        return []
    divider, top, bottom = verticals[0].x0, verticals[0].y0, verticals[0].y1
    for r in verticals[1:]:
        if abs(r.x0 - divider) < 1 and r.y0 <= bottom + 4:
            bottom = max(bottom, r.y1)
    lines = [l for l in page_lines(page) if top - 4 <= l.y0 < bottom]
    if any(l.text.strip() == "Idiom" for l in lines):
        return []
    rules = sorted({round(r.y0, 1) for r in segs if r.height < 1.5 and r.width > 150 and top + 1 < r.y0 <= bottom + 1})
    if not rules or bottom - rules[-1] > 2:
        rules.append(round(bottom, 1))
    return parse_idiom_box(lines, divider, [round(top, 1)] + rules)


def extract_idiom_boxes(doc, owner, first: int, last: int) -> list[dict]:
    boxes = []
    for pdf in range(first, last + 1):
        page = doc[pdf - 1]
        lines = page_lines(page)
        for label in lines:
            if label.text.strip() != "Idiom" or label.bold:
                continue
            names = [l for l in lines if l.bold and abs(l.y0 - label.y0) < 3 and l.x0 > label.x1]
            if not names:
                continue
            name = names[0]
            segs = [d["rect"] for d in page.get_drawings()]
            verticals = sorted((r for r in segs if r.width < 1.5 and r.height > 3
                                and name.x0 - 14 < r.x0 < name.x0), key=lambda r: r.y0)
            next_label = min((l.y0 for l in lines if l.text.strip() == "Idiom" and l.y0 > label.y0 + 3),
                             default=float("inf"))
            divider = None
            bottom = name.y1
            for r in verticals:
                if r.y0 <= bottom + 4 and r.y1 > label.y0 - 12 and r.y0 < next_label - 10:
                    divider = r.x0 if divider is None else divider
                    bottom = max(bottom, r.y1)
            if divider is None:
                raise ValueError(f"idiom box {name.text!r} on PDF p.{pdf} has no column divider")
            rules = sorted({round(r.y0, 1) for r in segs if r.height < 1.5 and r.width > 150
                            and label.y0 < r.y0 <= bottom + 1})
            if not rules or bottom - rules[-1] > 2:
                rules.append(round(bottom, 1))
            body = [l for l in lines if l is not label and l is not name and l.y0 >= name.y1 - 4
                    and l.y0 < bottom and l.x0 >= label.x0 - 2 and l.x1 <= label.x0 + 470]
            fields = parse_idiom_box(body, divider, rules)
            last_text = max(l.y1 for l in lines if l.y0 < FOOTER_MIN_Y)
            if bottom >= last_text - 2 and pdf < doc.page_count:
                rest = box_continuation(doc[pdf])
                if rest and not rest[0][0]:
                    fields[-1] = (fields[-1][0], fields[-1][1] + "\n" + rest.pop(0)[1])
                fields += rest
            keyed: dict[str, str] = {}
            for key, value in fields:
                k = key
                n = 2
                while k in keyed:
                    k = f"{key} ({n})"
                    n += 1
                keyed[k] = value
            section = owner(pdf, label.y0)
            boxes.append({
                "slug": slugify(name.text), "name": name.text.strip(),
                "chapter": int(section["id"][1:3]) if section else None,
                "section": section["id"] if section else None,
                "pdf_page": pdf, "fields": keyed,
            })
    return boxes


def caption_row(row: list[Line], left: float) -> list[Line]:
    """The fragments of one row that belong to a caption starting at x=`left`: the
    fragment at the left edge plus those that follow it without a column gap. A caption
    set beside another caption stops at the gap."""
    chain: list[Line] = []
    for line in sorted(row, key=lambda l: l.x0):
        if not chain:
            if abs(line.x0 - left) <= 20:
                chain.append(line)
        elif line.x0 - chain[-1].x1 < 15:
            chain.append(line)
        else:
            break
    return chain


CAPTION_FONTS = ("NimbusSanL", "CMMI", "CMR", "CMSY")


def find_captions(lines: list[Line], vocabulary: set[str]) -> list[tuple[int, int, str, tuple[float, float, float, float]]]:
    """Figure captions on one page: (chapter, number, caption text, caption bbox).

    A caption starts with a bold "Figure N.M." and continues through the sans-serif
    rows directly beneath it in the same column; a row may open with inline maths set
    in a Computer Modern face, as in Figure 5.7's "n < 1)"."""
    found = []
    for head in lines:
        m = FIGURE_START.match(head.text)
        if not (m and head.bold and head.font.startswith("NimbusSanL")):
            continue
        column = [l for l in lines if l is not head and l.y0 > head.y0 - 3 and l.font.startswith(CAPTION_FONTS)
                  and l.x0 >= head.x0 - 2 and not FIGURE_START.match(l.text)]
        rows: list[list[Line]] = []
        for row in group_rows([head] + column):
            row = caption_row(row, head.x0)
            if not rows:
                if head not in row:
                    continue
            elif not row or row[0].y0 - max(l.y1 for l in rows[-1]) > 3:
                break
            rows.append(row)
        block = [l for row in rows for l in row]
        text = dehyphenate_lines([merge_row(row) for row in rows], vocabulary)
        caption = FIGURE_START.sub("", text, count=1).strip()
        bbox = (min(l.x0 for l in block), head.y0, max(l.x1 for l in block), max(l.y1 for l in block))
        found.append((int(m.group(1)), int(m.group(2)), caption, bbox))
    return found


def figure_id(chapter: int, n: int, taken: set[str]) -> str:
    """`fig-NN-MM`; a label the book prints twice (Figure 8.6 on PDF pp.211 and 213) gets
    `b`, `c`, ... on its later occurrences so every caption keeps its own file."""
    base = f"fig-{chapter:02d}-{n:02d}"
    ident, suffix = base, "b"
    while ident in taken:
        ident, suffix = base + suffix, chr(ord(suffix) + 1)
    return ident


def extract_figures(doc, first: int, last: int, vocabulary: set[str]) -> list[dict]:
    figures = []
    taken: set[str] = set()
    for pdf in range(first, last + 1):
        for chapter, n, caption, _ in find_captions(page_lines(doc[pdf - 1]), vocabulary):
            ident = figure_id(chapter, n, taken)
            taken.add(ident)
            figures.append({"id": ident, "number": f"{chapter}.{n}", "chapter": chapter,
                            "pdf_page": pdf, "caption": caption})
    return figures


def extract_crossrefs(doc, owner, known: set[str], first: int, last: int) -> list[dict]:
    refs = []
    for pdf in range(first, last + 1):
        for x0, y0, x1, y1, text, *_ in doc[pdf - 1].get_text("blocks"):
            for _, number, target in resolve_section_refs(text, known):
                src = owner(pdf, y0)
                refs.append({"from": src["id"] if src else None, "pdf_page": pdf,
                             "target_number": number, "target": target})
    return refs


def write_atomic(path: Path, data: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(data, encoding="utf-8")
    os.replace(tmp, path)


def dump_json(path: Path, obj) -> None:
    write_atomic(path, json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


def main(argv: list[str] | None = None) -> int:
    import pymupdf

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pdf", default=os.environ.get("VIS_PDF"), required=os.environ.get("VIS_PDF") is None)
    args = ap.parse_args(argv)
    pdf_path = Path(args.pdf)
    doc = pymupdf.open(pdf_path)
    page_map = page_map_for(doc.page_count)

    texts = [page_text(page) for page in doc]
    for i, text in enumerate(texts):
        write_atomic(BUILD_PAGES / f"{i + 1:04d}.txt", text)
    vocabulary = vocabulary_of(texts)

    entries = parse_toc(doc)
    credits_pdf = next(p for lvl, title, p in doc.get_toc() if title.startswith("Figure Credits"))
    last_body = credits_pdf - 1
    where = locate_headings(doc, entries, page_map)
    compute_ranges(doc, entries, where, last_body)
    owner = position_index(entries, where)
    known = {e["id"] for e in entries}
    first_body = min(e["pdf_start"] for e in entries)

    toc = [{k: e[k] for k in ("id", "level", "number", "title", "parent", "printed_page", "pdf_start", "pdf_end")}
           for e in entries]
    figures = extract_figures(doc, first_body, last_body, vocabulary)
    book = {
        "pdf": {"pages": doc.page_count, "sha256": hashlib.sha256(pdf_path.read_bytes()).hexdigest()},
        "page_map": page_map,
        "toc": toc,
        "idiom_boxes": extract_idiom_boxes(doc, owner, first_body, last_body),
        "figures": figures,
        "crossrefs": extract_crossrefs(doc, owner, known, first_body, last_body),
    }
    dump_json(BOOK_JSON, book)
    print(f"pages {doc.page_count}, toc {len(toc)}, boxes {len(book['idiom_boxes'])}, "
          f"figures {len(figures)}, crossrefs {len(book['crossrefs'])}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
