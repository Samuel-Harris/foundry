"""The parsed form of one skill markdown file, and the constants every gate shares.

`parse_doc` turns a file into a `Doc`: frontmatter, headings, units (paragraphs,
list items, table rows, code), verbatim blocks, links, anchors and citations.
"""

from __future__ import annotations

import json
import posixpath
import re
from dataclasses import dataclass
from pathlib import Path

import yaml

PASS, FAIL, NOT_CHECKABLE = "PASS", "FAIL", "NOT-CHECKABLE"

HINT = "[NOT FROM BOOK]"
NO_OVERLAP = "No overlapping children."
NO_BOX = "No idiom box in the book."
LOOKUP_PATH = "references/lookup.md"

NODE_KINDS = ("router", "job-node", "index-node", "chapter-node", "section-node")
LEAF_KINDS = ("section-leaf", "subsection-leaf")
CARD = "idiom-card"
ALL_KINDS = NODE_KINDS + LEAF_KINDS + (CARD,)
WIDE_KINDS = ("router", "job-node", "index-node")
SPECIFIC_KINDS = ("section-node", "section-leaf", "subsection-leaf", CARD)

JOB_IDS = ("j1", "j2", "j3", "j4")

CARD_SECTIONS = (
    "Idiom box",
    "What it is",
    "Use when / avoid when",
    "Figures",
    "Alternatives and disambiguation",
    "Related",
    f"Implementation hints {HINT}",
)
NODE_SECTIONS = ("Children", "Disambiguation", "Related")

CITATION = re.compile(r"\[(pp?)\.(\d+)(?:-(\d+))?\]")
LINK = re.compile(r"(!?)\[([^\]]*)\]\(([^)\s]+)\)")
INLINE_CODE = re.compile(r"(`+).+?\1")
ANCHOR = re.compile(r'<a id="([^"]+)"></a>')
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+(.*)$")
VERBATIM_OPEN = re.compile(r"^<!--\s*verbatim\b(.*?)-->$")
VERBATIM_PAGES = re.compile(r"^\s*(?:p\.(\d+)|pp\.(\d+)-(\d+))\s*$")
VERBATIM_CLOSE = "<!-- /verbatim -->"
TABLE_SEPARATOR = re.compile(r"^\|?(\s*:?-{3,}:?\s*\|)+\s*(:?-{3,}:?\s*)?$")
TOC_CHAPTER = re.compile(r"^(?:ch|s)(\d\d)")

LIGATURES = {"\ufb00": "ff", "\ufb01": "fi", "\ufb02": "fl", "\ufb03": "ffi", "\ufb04": "ffl", "\ufb05": "st", "\ufb06": "st"}
QUOTES = {"\u2018": "'", "\u2019": "'", "\u201a": "'", "\u201b": "'", "\u2032": "'",
          "\u201c": '"', "\u201d": '"', "\u201e": '"', "\u201f": '"', "\u2033": '"'}
DASHES = "\u2010\u2011\u2012\u2013\u2014\u2015\u2212"


@dataclass(frozen=True)
class Citation:
    first: int
    last: int


@dataclass(frozen=True)
class Link:
    text: str
    target: str
    image: bool
    path: str | None
    fragment: str | None


@dataclass
class Unit:
    kind: str
    text: str
    line: int
    h2: str
    h3: str
    hint: bool
    citations: list[Citation]
    links: list[Link]

    @property
    def figure_line(self) -> bool:
        return self.kind == "item" and self.h2 == "Figures" and self.text.startswith("![")


@dataclass
class Verbatim:
    pages: tuple[int, int] | None
    text: str
    line: int
    h2: str
    hint: bool
    closed: bool


@dataclass
class Heading:
    level: int
    title: str
    line: int
    hint: bool


@dataclass
class Doc:
    path: str
    frontmatter: dict
    error: str | None
    words: int
    headings: list[Heading]
    units: list[Unit]
    verbatims: list[Verbatim]
    anchors: set[str]

    @property
    def kind(self) -> str | None:
        return self.frontmatter.get("kind")

    @property
    def id(self) -> str | None:
        value = self.frontmatter.get("id")
        return str(value) if value is not None else None

    @property
    def title(self) -> str:
        return str(self.frontmatter.get("title") or "")

    @property
    def toc(self) -> list[str]:
        value = self.frontmatter.get("toc")
        return [str(item) for item in value] if isinstance(value, list) else []

    @property
    def pdf_pages(self) -> tuple[int, int] | None:
        return int_range(self.frontmatter.get("pdf_pages"))

    @property
    def links(self) -> list[tuple[Unit, Link]]:
        return [(unit, link) for unit in self.units for link in unit.links]

    def section(self, title: str) -> list[Unit]:
        return [unit for unit in self.units if unit.h2 == title]

    def has_heading(self, title: str, level: int = 2) -> bool:
        return any(h.level == level and h.title == title for h in self.headings)


@dataclass
class Result:
    status: str
    evidence: list[str]


def int_range(value) -> tuple[int, int] | None:
    if (
        isinstance(value, list)
        and len(value) == 2
        and all(isinstance(v, int) and not isinstance(v, bool) for v in value)
        and value[0] <= value[1]
    ):
        return value[0], value[1]
    return None


def citations_in(text: str) -> list[Citation]:
    found = []
    for match in CITATION.finditer(text):
        first = int(match.group(2))
        last = int(match.group(3)) if match.group(3) else first
        found.append(Citation(first, last))
    return found


def resolve(doc_path: str, target: str) -> tuple[str | None, str | None]:
    if re.match(r"^[a-z][a-z0-9+.-]*:", target):
        return None, None
    path, _, fragment = target.partition("#")
    resolved = posixpath.normpath(posixpath.join(posixpath.dirname(doc_path), path)) if path else doc_path
    return resolved, fragment or None


def links_in(doc_path: str, text: str) -> list[Link]:
    links = []
    for match in LINK.finditer(text):
        path, fragment = resolve(doc_path, match.group(3))
        links.append(Link(match.group(2), match.group(3), match.group(1) == "!", path, fragment))
    return links


def word_list(text: str) -> list[str]:
    return text.split()


class Scanner:
    """Turns a markdown body into headings, units and verbatim blocks in one pass."""

    def __init__(self, path: str, offset: int) -> None:
        self.path = path
        self.offset = offset
        self.headings: list[Heading] = []
        self.units: list[Unit] = []
        self.verbatims: list[Verbatim] = []
        self.anchors: set[str] = set()
        self.h2 = ""
        self.h3 = ""
        self.hint_section = False
        self.buffer: list[str] = []
        self.buffer_kind: str | None = None
        self.buffer_line = 0
        self.fence: list[str] | None = None
        self.fence_line = 0
        self.verbatim: tuple[tuple[int, int] | None, int, list[str]] | None = None

    def emit(self, kind: str, text: str, line: int) -> None:
        marked = text.lstrip("| ").startswith(HINT)
        links = [] if kind == "code" else links_in(self.path, INLINE_CODE.sub(" ", text))
        self.units.append(
            Unit(kind, text, line, self.h2, self.h3, self.hint_section or marked, citations_in(text), links)
        )

    def flush(self) -> None:
        if self.buffer_kind:
            self.emit(self.buffer_kind, " ".join(part.strip() for part in self.buffer), self.buffer_line)
        self.buffer, self.buffer_kind = [], None

    def close_verbatim(self, closed: bool) -> None:
        pages, line, lines = self.verbatim
        text = "\n".join(re.sub(r"^\s*>\s?", "", raw) for raw in lines)
        self.verbatims.append(Verbatim(pages, text, line, self.h2, self.hint_section, closed))
        self.verbatim = None

    def feed(self, number: int, line: str) -> None:
        lineno = number + self.offset
        stripped = line.strip()
        if self.fence is not None:
            if stripped.startswith(("```", "~~~")):
                self.emit("code", "\n".join(self.fence), self.fence_line)
                self.fence = None
            else:
                self.fence.append(line)
            return
        if self.verbatim is not None:
            if stripped == VERBATIM_CLOSE:
                self.close_verbatim(True)
            else:
                self.verbatim[2].append(line)
            return
        self.anchors.update(ANCHOR.findall(line))
        if not stripped:
            self.flush()
            return
        if stripped.startswith(("```", "~~~")):
            self.flush()
            self.fence, self.fence_line = [], lineno
            return
        opening = VERBATIM_OPEN.match(stripped)
        if opening:
            self.flush()
            pages = VERBATIM_PAGES.match(opening.group(1))
            span = None
            if pages:
                first = int(pages.group(1) or pages.group(2))
                span = (first, int(pages.group(3) or first))
            self.verbatim = (span, lineno, [])
            return
        heading = HEADING.match(line)
        if heading:
            self.flush()
            level, title = len(heading.group(1)), heading.group(2)
            if level <= 2:
                self.h2 = title if level == 2 else ""
                self.h3 = ""
                self.hint_section = level == 2 and title.endswith(HINT)
            elif level == 3:
                self.h3 = title
            self.headings.append(Heading(level, title, lineno, self.hint_section))
            return
        if ANCHOR.fullmatch(stripped) or (stripped.startswith("<!--") and stripped.endswith("-->")):
            self.flush()
            return
        if stripped.startswith("|"):
            self.flush()
            if TABLE_SEPARATOR.match(stripped):
                if self.units and self.units[-1].kind == "row" and self.units[-1].line == lineno - 1:
                    self.units[-1].kind = "header-row"
                return
            self.emit("row", stripped, lineno)
            return
        item = LIST_ITEM.match(line)
        if item:
            self.flush()
            self.buffer, self.buffer_kind, self.buffer_line = [item.group(1)], "item", lineno
            return
        if self.buffer_kind is None:
            self.buffer_kind, self.buffer_line = "paragraph", lineno
        self.buffer.append(stripped)

    def finish(self) -> None:
        self.flush()
        if self.fence is not None:
            self.emit("code", "\n".join(self.fence), self.fence_line)
        if self.verbatim is not None:
            self.close_verbatim(False)


def split_frontmatter(text: str) -> tuple[str | None, str, int]:
    lines = text.split("\n")
    if lines and lines[0].strip() == "---":
        for index in range(1, len(lines)):
            if lines[index].strip() == "---":
                return "\n".join(lines[1:index]), "\n".join(lines[index + 1:]), index + 1
    return None, text, 0


def parse_doc(path: str, text: str) -> Doc:
    raw, body, offset = split_frontmatter(text)
    frontmatter: dict = {}
    error = None
    if raw is None:
        error = "no YAML frontmatter block"
    else:
        try:
            loaded = yaml.safe_load(raw)
        except yaml.YAMLError as exc:
            loaded, error = None, f"frontmatter is not valid YAML ({str(exc).splitlines()[0]})"
        if isinstance(loaded, dict):
            frontmatter = loaded
        elif error is None:
            error = "frontmatter is not a mapping"
    scanner = Scanner(path, offset)
    for number, line in enumerate(body.split("\n"), start=1):
        scanner.feed(number, line)
    scanner.finish()
    return Doc(path, frontmatter, error, len(word_list(body)), scanner.headings, scanner.units,
               scanner.verbatims, scanner.anchors)


def load_docs(skill_dir: Path) -> dict[str, Doc]:
    if not skill_dir.is_dir():
        return {}
    return {
        path.relative_to(skill_dir).as_posix(): parse_doc(
            path.relative_to(skill_dir).as_posix(), path.read_text(encoding="utf-8")
        )
        for path in sorted(skill_dir.rglob("*.md"))
    }


def load_json(path: Path) -> tuple[object | None, str | None]:
    if not path.is_file():
        return None, f"{path.name} is missing"
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except json.JSONDecodeError as exc:
        return None, f"{path.name} is not valid JSON ({exc})"


def dump_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def normalise(text: str, source: bool = False) -> str:
    for old, new in {**LIGATURES, **QUOTES}.items():
        text = text.replace(old, new)
    for dash in DASHES:
        text = text.replace(dash, "-")
    text = text.replace("\u00ad", "").replace("\u22c6", "")
    if source:
        text = re.sub(r"-[ \t]*\n\s*", "", text)
    return re.sub(r"\s+", " ", text).strip()


def verbatim_matches(block: str, source: str) -> bool:
    """A hyphen in the block may be absent in the source, where end-of-line
    hyphenation was joined, so each block hyphen is optional in the pattern."""
    needle = normalise(block.replace("*", ""))
    if not needle:
        return False
    pattern = "-?".join(re.escape(part) for part in needle.split("-"))
    return re.search(pattern, normalise(source, source=True)) is not None


def chapter_of(toc_id: str) -> int | None:
    match = TOC_CHAPTER.match(toc_id)
    return int(match.group(1)) if match else None


def fmt_range(span: tuple[int, int] | None) -> str:
    if span is None:
        return "none"
    return f"p.{span[0]}" if span[0] == span[1] else f"pp.{span[0]}-{span[1]}"
