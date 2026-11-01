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
import json
import posixpath
import re
import sys
from collections import defaultdict, deque
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Callable

import yaml

PACKAGE = Path(__file__).resolve().parents[1]

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
SIZE_LIMITS = {
    "router": 2500,
    "job-node": 1500,
    "index-node": 1500,
    "chapter-node": 1500,
    "section-node": 1500,
    "section-leaf": 2000,
    "subsection-leaf": 2000,
    CARD: 1500,
}
LOOKUP_LIMIT = 4000
JOB_IDS = ("j1", "j2", "j3", "j4")
JOB_REACH = {"j1": (2, 3), "j3": (4, 6), "j4": (11, 12)}
JOB_CARDS = ("j1", "j2")
UNBOXED_CHAPTERS = (10, 11)
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
FIGURE_KEYS = ("caption", "dpi", "file", "id", "method", "number", "pdf_page", "reason", "referenced_by")
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
LEDGER_HEADER = ["level", "choice", "reason"]
LEDGER_KEYWORDS = {"router": ("router",), "job": ("job-node",), "lookup": ("index-node",),
                   "chapter": ("chapter-node",), "section": ("section-node",)}
COUNTS_START = "<!-- measured-counts:start (written by tools/check.py) -->"
COUNTS_END = "<!-- measured-counts:end -->"
EVIDENCE_CAP = 60
STOPWORDS = frozenset(
    "a an the and or of to in on for with by is are be this that it its as at from when you your "
    "use need needs want wants which what how into than then there these those not no any all one "
    "more most should can do does".split()
)

CITATION = re.compile(r"\[(pp?)\.(\d+)(?:-(\d+))?\]")
PAGE_REFERENCE = re.compile(r"\bpp?\.\s*\d+")
PLOTTING_LIBRARY = re.compile(r"\b(?:matplotlib|pyplot|seaborn|plotly|d3|vega(?:-lite)?|ggplot2?)\b|\bplt\.\w", re.I)
CONCEPTS = "Concepts"
BOX_KEY_SUFFIX = re.compile(r"\s*\(\d+\)$")  # book.json numbers a repeated field label, e.g. "What: Derived (2)"
LINK = re.compile(r"(!?)\[([^\]]*)\]\(([^)\s]+)\)")
INLINE_CODE = re.compile(r"(`+).+?\1")
ANCHOR = re.compile(r'<a id="([^"]+)"></a>')
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+(.*)$")
VERBATIM_OPEN = re.compile(r"^<!--\s*verbatim\b(.*?)-->$")
VERBATIM_PAGES = re.compile(r"^\s*(?:p\.(\d+)|pp\.(\d+)-(\d+))\s*$")
VERBATIM_CLOSE = "<!-- /verbatim -->"
TABLE_SEPARATOR = re.compile(r"^\|?(\s*:?-{3,}:?\s*\|)+\s*(:?-{3,}:?\s*)?$")
CHILD_ITEM = re.compile(
    r"^\[(?P<title>[^\]]+)\]\((?P<target>[^)\s]+)\) · ~(?P<size>[\d,]+|\?) words\. "
    r"\*\*Use when\*\* (?P<criterion>.+)$"
)
RELATED_ITEM = re.compile(r"^\[(?P<title>[^\]]+)\]\((?P<target>[^)\s]+)\): (?P<why>.+)$")
DISAMBIGUATION_ITEM = re.compile(r"^\*\*(?P<lead>.+?)\.\*\* (?P<text>.+)$")
FIGURE_ITEM = re.compile(
    r"^!\[Figure (?P<n1>\d+\.\d+)\]\((?P<target>[^)\s]+)\) \*\*Figure (?P<n2>\d+\.\d+)\*\* "
    r"\[p\.(?P<page>\d+)\]\. (?P<caption>.+)$"
)
SIZE_FIELD = re.compile(r"(\) · ~)([\d,]+|\?)( words\.)")
TOC_CHAPTER = re.compile(r"^(?:ch|s)(\d\d)")
AUTOLINK = re.compile(r"<(https?://[^>\s]+)>")  # figure_lines.py wraps bare URLs for markdownlint MD034
FIGURE_ID = re.compile(r"^fig-(\d\d)-(\d\d)([a-z])?$")

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


def criterion_words(text: str) -> list[str]:
    return re.findall(r"[a-z]+", CITATION.sub(" ", text).lower())


def name_key(name: str) -> str:
    name = re.sub(r"^\d+(\.\d+)*\s+", "", name.strip())
    words = re.findall(r"[a-z0-9]+", name.lower())
    return " ".join(w[:-1] if w.endswith("s") and len(w) > 3 else w for w in words)


def chapter_of(toc_id: str) -> int | None:
    match = TOC_CHAPTER.match(toc_id)
    return int(match.group(1)) if match else None


def fmt_range(span: tuple[int, int] | None) -> str:
    if span is None:
        return "none"
    return f"p.{span[0]}" if span[0] == span[1] else f"pp.{span[0]}-{span[1]}"


@dataclass
class Paths:
    skill: Path
    provenance: Path
    pages: Path

    @property
    def reports(self) -> Path:
        return self.provenance / "reports"


class Resource:
    """The parsed skill tree plus provenance data, with derived graphs cached."""

    def __init__(self, paths: Paths) -> None:
        self.paths = paths
        self.docs = load_docs(paths.skill)
        self.book, self.book_error = load_json(paths.provenance / "book.json")
        if self.book is not None and not isinstance(self.book, dict):
            self.book, self.book_error = None, "book.json is not an object"
        self.plan, self.plan_error = load_json(paths.provenance / "plan.json")
        if self.plan is not None and not isinstance(self.plan, dict):
            self.plan, self.plan_error = None, "plan.json is not an object"
        raw, self.figures_error = load_json(paths.provenance / "figures.json")
        self.figures_wrapped = isinstance(raw, dict)
        entries = raw.get("figures") if isinstance(raw, dict) else raw
        self.figures: list[dict] | None = None
        if raw is not None:
            if isinstance(entries, list) and all(isinstance(e, dict) for e in entries):
                self.figures = entries
            else:
                self.figures_error = "figures.json holds no list of figure objects"
        self.written: set[str] = set()
        self._page_cache: dict[int, str | None] = {}

    def missing(self, *names: str) -> list[str]:
        errors = {"book": self.book_error, "plan": self.plan_error, "figures": self.figures_error}
        return [f"provenance/{errors[name]}" for name in names if errors[name]]

    @cached_property
    def book_pages(self) -> int | None:
        pages = (self.book or {}).get("pdf", {}).get("pages")
        return pages if isinstance(pages, int) else None

    @cached_property
    def toc(self) -> list[dict]:
        return [e for e in (self.book or {}).get("toc", []) if isinstance(e, dict) and "id" in e]

    @cached_property
    def book_chapters(self) -> dict[int, tuple[int, int]]:
        return {
            int(e["id"][2:]): (e.get("pdf_start"), e.get("pdf_end"))
            for e in self.toc
            if e.get("level") == "chapter" and re.fullmatch(r"ch\d\d", str(e["id"]))
        }

    @cached_property
    def plan_files(self) -> list[dict]:
        return [f for f in (self.plan or {}).get("files", []) if isinstance(f, dict) and "path" in f]

    @cached_property
    def plan_cards(self) -> list[dict]:
        return [c for c in (self.plan or {}).get("idiom_cards", []) if isinstance(c, dict) and "path" in c]

    @cached_property
    def plan_card_by_path(self) -> dict[str, dict]:
        return {c["path"]: c for c in self.plan_cards}

    def of_kind(self, *kinds: str) -> list[Doc]:
        return [doc for doc in self.docs.values() if doc.kind in kinds]

    def doc_by_id(self, doc_id: str) -> Doc | None:
        return next((doc for doc in self.docs.values() if doc.id == doc_id), None)

    def chapters(self, doc: Doc) -> set[int]:
        found = {c for c in map(chapter_of, doc.toc) if c is not None}
        card = self.plan_card_by_path.get(doc.path)
        if card and isinstance(card.get("chapter"), int):
            found.add(card["chapter"])
        return found

    def children(self, doc: Doc) -> list[Unit]:
        return [u for u in doc.section("Children") if u.kind == "item" and not u.hint]

    def child_paths(self, doc: Doc) -> list[str]:
        return [link.path for unit in self.children(doc) for link in unit.links[:1] if link.path]

    def exists(self, path: str | None) -> bool:
        return path is not None and (path in self.docs or (self.paths.skill / path).is_file())

    def page_text(self, page: int) -> str | None:
        if page not in self._page_cache:
            file = self.paths.pages / f"{page:04d}.txt"
            self._page_cache[page] = file.read_text(encoding="utf-8") if file.is_file() else None
        return self._page_cache[page]

    @cached_property
    def coverage(self) -> tuple[list[dict], list[str]]:
        covering: dict[str, list[Doc]] = defaultdict(list)
        for doc in self.docs.values():
            for toc_id in doc.toc:
                covering[toc_id].append(doc)
        planned = (self.plan or {}).get("entries", {})
        rows, problems = [], []
        for entry in self.toc:
            entry_id = str(entry["id"])
            targets = []
            for doc in covering.get(entry_id, []):
                if doc.id == entry_id:
                    targets.append(doc.path)
                elif entry_id in doc.anchors:
                    targets.append(f"{doc.path}#{entry_id}")
                else:
                    problems.append(f'{doc.path}: lists {entry_id} in toc but has no <a id="{entry_id}"></a> anchor')
            label = f"{entry_id} ({' '.join(str(p) for p in (entry.get('number'), entry.get('title')) if p)})"
            if not targets:
                problems.append(f"{label}: no file covers it")
            plan_target = planned.get(entry_id) if isinstance(planned, dict) else None
            if plan_target and targets and plan_target not in targets:
                problems.append(f"{label}: plan puts it at {plan_target}, files put it at {', '.join(targets)}")
            primary = plan_target if plan_target in targets else (targets[0] if targets else None)
            rows.append({
                "entry": entry_id,
                "level": entry.get("level"),
                "number": entry.get("number"),
                "title": entry.get("title"),
                "path": primary,
                "other_paths": [t for t in targets if t != primary],
                "pdf_pages": [entry.get("pdf_start"), entry.get("pdf_end")],
            })
        return rows, problems

    @cached_property
    def coverage_target(self) -> dict[str, str]:
        return {row["entry"]: row["path"] for row in self.coverage[0] if row["path"]}

    @cached_property
    def plan_drift(self) -> tuple[list[str], list[str]]:
        planned = {f["path"] for f in self.plan_files} | {c["path"] for c in self.plan_cards}
        integration = {"SKILL.md", LOOKUP_PATH}
        missing = sorted(p for p in planned if p not in self.docs)
        unplanned = sorted(
            p for p in self.docs
            if p not in planned and p not in integration and not p.startswith("references/jobs/")
        ) if self.plan else []
        return missing, unplanned

    def traverse(self, start: str, stop: set[str]) -> set[str]:
        seen, queue = {start}, deque([start])
        while queue:
            current = queue.popleft()
            if current in stop or current not in self.docs:
                continue
            for child in self.child_paths(self.docs[current]):
                if child in self.docs and child not in seen:
                    seen.add(child)
                    queue.append(child)
        return seen

    @cached_property
    def reachable(self) -> set[str]:
        if "SKILL.md" not in self.docs:
            return set()
        return self.traverse("SKILL.md", {LOOKUP_PATH})

    @cached_property
    def orphans(self) -> list[str]:
        return sorted(set(self.docs) - self.reachable)

    @cached_property
    def parents(self) -> dict[str, set[str]]:
        found: dict[str, set[str]] = defaultdict(set)
        for doc in self.of_kind(*NODE_KINDS):
            for child in self.child_paths(doc):
                found[child].add(doc.path)
        return found

    @cached_property
    def link_check(self) -> tuple[int, int, list[str]]:
        checked, external, dead = 0, 0, []
        for doc in self.docs.values():
            for unit, link in doc.links:
                if link.path is None:
                    external += 1
                    continue
                checked += 1
                reason = self.dead_reason(link)
                if reason:
                    dead.append(f"{doc.path}:{unit.line}: {link.target} ({reason})")
        return checked, external, dead

    def dead_reason(self, link: Link) -> str | None:
        if link.path.startswith(".."):
            return "points outside the skill"
        if not self.exists(link.path):
            return "no such file"
        if link.fragment:
            target = self.docs.get(link.path)
            if target is None:
                return "anchor on a non-markdown file"
            if link.fragment not in target.anchors:
                return f"no anchor #{link.fragment}"
        return None

    @cached_property
    def figure_by_file(self) -> dict[str, dict]:
        return {f["file"]: f for f in self.figures or [] if f.get("file")}

    @cached_property
    def figure_refs(self) -> dict[str, list[str]]:
        refs: dict[str, set[str]] = defaultdict(set)
        for doc in self.docs.values():
            for _, link in doc.links:
                if link.image and link.path in self.figure_by_file:
                    refs[self.figure_by_file[link.path]["id"]].add(doc.path)
        return {key: sorted(value) for key, value in refs.items()}

    @cached_property
    def verbatim_results(self) -> list[tuple[str, Verbatim, str | None]]:
        results = []
        for doc in self.docs.values():
            for block in doc.verbatims:
                results.append((doc.path, block, self.verbatim_problem(doc, block)))
        return results

    def verbatim_problem(self, doc: Doc, block: Verbatim) -> str | None:
        if not block.closed:
            return f"no closing {VERBATIM_CLOSE}"
        if block.pages is None:
            return "opening comment has no p.N or pp.N-M"
        if block.pages[0] > block.pages[1]:
            return f"opening comment cites reversed range {fmt_range(block.pages)}"
        span = doc.pdf_pages
        if span is None or block.pages[0] < span[0] or block.pages[1] > span[1]:
            return f"cites {fmt_range(block.pages)}, outside the file's pdf_pages {fmt_range(span)}"
        texts = [self.page_text(p) for p in range(block.pages[0], block.pages[1] + 1)]
        if any(t is None for t in texts):
            return f"page text for {fmt_range(block.pages)} is missing from {self.paths.pages}"
        if not normalise(block.text):
            return "block is empty"
        bodies, notes = zip(*(text.partition("\n\n")[::2] for text in texts))
        if not any(verbatim_matches(block.text, source) for source in ("\n".join(bodies), *notes)):
            return f"not a substring of {fmt_range(block.pages)}: {normalise(block.text)[:80]!r}"
        return None

    def kind_counts(self) -> dict[str, dict[str, int]]:
        counts: dict[str, dict[str, int]] = {}
        for doc in self.docs.values():
            row = counts.setdefault(str(doc.kind), {"files": 0, "verbatim": 0, "summary": 0, "non-book": 0})
            row["files"] += 1
            row["verbatim"] += sum(len(word_list(b.text)) for b in doc.verbatims)
            for unit in doc.units:
                if unit.hint or unit.kind == "code":
                    row["non-book"] += len(word_list(unit.text))
                elif unit.kind in ("paragraph", "item", "row") and not unit.figure_line:
                    row["summary"] += len(word_list(unit.text))
        return counts


def verdict(problems: list[str], passed: list[str], judge: list[str] | None = None) -> Result:
    if problems:
        return Result(FAIL, problems)
    if judge:
        return Result(NOT_CHECKABLE, passed + judge)
    return Result(PASS, passed)


def need_docs(r: Resource, docs: list[Doc], what: str) -> list[str]:
    return [] if docs else [f"no {what} found under {r.paths.skill}"]


def gate_a1(r: Resource) -> Result:
    rows, problems = r.coverage
    problems = r.missing("book", "plan") + list(problems)
    if r.book is not None and not rows:
        problems.append("book.json lists no TOC entries")
    missing, unplanned = r.plan_drift
    problems += [f"{p}: in plan.json but missing on disk" for p in missing]
    problems += [f"{p}: on disk but not in plan.json" for p in unplanned]
    mapped = sum(1 for row in rows if row["path"])
    return verdict(problems, [f"{mapped}/{len(rows)} TOC entries mapped; plan and disk agree"])


def gate_a2(r: Resource) -> Result:
    problems = [] if "SKILL.md" in r.docs else ["SKILL.md is missing: nothing is reachable"]
    problems += [f"{p}: not reachable from SKILL.md through ## Children links" for p in r.orphans]
    for planned in r.plan_files:
        doc = r.docs.get(planned["path"])
        if doc is None or doc.kind not in NODE_KINDS:
            continue
        expected = set(planned.get("children") or [])
        expected |= {c["path"] for c in r.plan_cards if c.get("parent") == planned["path"]}
        for child in sorted(expected - set(r.child_paths(doc))):
            problems.append(f"{doc.path}: ## Children lacks planned child {child}")
    return verdict(problems, [
        f"{len(r.reachable)}/{len(r.docs)} files reachable from SKILL.md (lookup.md not expanded)",
    ])


def gate_a3(r: Resource) -> Result:
    problems = r.missing("book")
    boxes = [b for b in (r.book or {}).get("idiom_boxes", []) if isinstance(b, dict)]
    if r.book is not None and not boxes:
        problems.append("book.json lists no idiom boxes")
    for box in boxes:
        card = r.doc_by_id(f"idiom:{box.get('slug')}")
        if card is None or card.kind != CARD:
            problems.append(f"idiom box {box.get('name')} (p.{box.get('pdf_page')}): no idiom card with id idiom:{box.get('slug')}")
            continue
        if card.frontmatter.get("boxed") is not True:
            problems.append(f"{card.path}: the book boxes this idiom but frontmatter boxed is not true")
        blocks = [v for v in card.verbatims if v.h2 == "Idiom box"]
        if not blocks:
            problems.append(f"{card.path}: ## Idiom box holds no verbatim block")
            continue
        problems += box_problems(card, box, blocks)
    return verdict(problems, [
        f"{len(boxes)} idiom boxes, each with a boxed card quoting every field of its own box and nothing else",
    ])


def squash(text: str) -> str:
    return normalise(text.replace("*", "")).replace("-", "")


def box_problems(card: Doc, box: dict, blocks: list[Verbatim]) -> list[str]:
    """Each book field must appear across the card's box blocks, and each block must quote the box's own
    fields from its page (or the next, where a box breaks across a page)."""
    raw = box.get("fields") if isinstance(box.get("fields"), dict) else {}
    fields = [f"{BOX_KEY_SUFFIX.sub('', str(key))} {value}" for key, value in raw.items()]
    quoted = squash(" ".join(b.text for b in blocks))
    problems = [
        f"{card.path}: ## Idiom box lacks the field {normalise(f, source=True)[:60]!r}"
        for f in fields if squash(normalise(f, source=True)) not in quoted
    ]
    page = box.get("pdf_page")
    for block in blocks:
        if not verbatim_matches(block.text, "\n\n".join(fields)):
            problems.append(f"{card.path}:{block.line}: ## Idiom box block is not from the {box.get('name')} box")
        elif isinstance(page, int) and block.pages and not (page <= block.pages[0] and block.pages[1] <= page + 1):
            problems.append(f"{card.path}:{block.line}: box block cites {fmt_range(block.pages)}, the box is on p.{page}")
    return problems


def card_structure_problems(doc: Doc) -> list[str]:
    return [f"{doc.path}: no ## {title}" for title in CARD_SECTIONS if not doc.has_heading(title)]


def gate_a4(r: Resource) -> Result:
    problems = r.missing("book", "plan")
    evidence = []
    for chapter in UNBOXED_CHAPTERS:
        if chapter not in r.book_chapters:
            evidence.append(f"chapter {chapter} is not in book.json; nothing to check")
            continue
        planned = [c for c in r.plan_cards if c.get("chapter") == chapter]
        if not planned:
            problems.append(f"plan.json lists no idiom cards for chapter {chapter}")
        cards = [r.docs[c["path"]] for c in planned if c["path"] in r.docs]
        problems += [f"{c['path']}: planned chapter {chapter} card is missing" for c in planned if c["path"] not in r.docs]
        if planned and not cards:
            problems.append(f"chapter {chapter}: no idiom card exists on disk")
        for card in cards:
            problems += card_structure_problems(card)
        evidence.append(f"chapter {chapter}: {len(cards)} cards ({', '.join(c.path for c in cards)})")
    return verdict(problems, evidence)


def gate_a5(r: Resource) -> Result:
    problems = r.missing("book")
    router = r.docs.get("SKILL.md")
    lookup = r.docs.get(LOOKUP_PATH)
    if router is None or LOOKUP_PATH not in r.child_paths(router):
        problems.append(f"SKILL.md ## Children does not link {LOOKUP_PATH}")
    if lookup is None:
        problems.append(f"{LOOKUP_PATH} is missing")
        return verdict(problems, [])
    if lookup.kind != "index-node" or lookup.id != "lookup":
        problems.append(f"{LOOKUP_PATH}: frontmatter must say kind index-node, id lookup")
    linked = set()
    for _, link in lookup.links:
        if link.path and not link.image:
            linked.add(link.path)
            linked.add(f"{link.path}#{link.fragment}" if link.fragment else link.path)
    wanted = [row for row in r.coverage[0] if row["level"] in ("chapter", "section")]
    for row in wanted:
        if row["path"] and row["path"] not in linked:
            problems.append(f"{LOOKUP_PATH}: no link to {row['entry']} at {row['path']}")
    cards = sorted({d.path for d in r.of_kind(CARD)} | {c["path"] for c in r.plan_cards})
    problems += [f"{LOOKUP_PATH}: no link to idiom card {p}" for p in cards if p not in linked]
    concepts = [u for u in lookup.section(CONCEPTS) if u.kind == "row" and not u.hint]
    if not concepts:
        problems.append(f"{LOOKUP_PATH}: no ## {CONCEPTS} table with concept rows")
    for unit in concepts:
        links = [l for l in unit.links if not l.image]
        if not links:
            problems.append(f"{LOOKUP_PATH}:{unit.line}: concept row links no file")
        for link in links:
            reason = r.dead_reason(link) if link.path else "external link"
            if reason:
                problems.append(f"{LOOKUP_PATH}:{unit.line}: concept link {link.target} ({reason})")
    return verdict(problems, [
        f"lookup links {len(wanted)} chapters and sections and {len(cards)} idiom cards, "
        f"and {len(concepts)} concept rows to files that exist",
    ])


def gate_b1(r: Resource) -> Result:
    nodes = r.of_kind(*NODE_KINDS)
    problems = need_docs(r, nodes, "nodes")
    checked = 0
    for node in nodes:
        for unit in r.children(node):
            head, marker, criterion = unit.text.partition("**Use when**")
            if not marker:
                problems.append(f"{node.path}:{unit.line}: child has no **Use when** criterion")
                continue
            checked += 1
            title_words = set(criterion_words(" ".join(l.text for l in links_in(node.path, head))))
            target = r.docs.get(unit.links[0].path) if unit.links else None
            if target:
                title_words |= set(criterion_words(target.title))
            fresh = {w for w in criterion_words(criterion) if w not in title_words and w not in STOPWORDS}
            if len(fresh) < 6:
                problems.append(
                    f"{node.path}:{unit.line}: use-when has {len(fresh)} content words beyond the title, needs 6"
                )
    return verdict(problems, [f"{checked} use-when criteria carry at least 6 non-title content words"], [
        "Judge: read every ## Children item and confirm each use-when names a data type, task or "
        f"situation rather than paraphrasing the title. Files: {', '.join(n.path for n in nodes)}",
    ])


def gate_b2(r: Resource) -> Result:
    nodes = r.of_kind(*NODE_KINDS)
    problems = need_docs(r, nodes, "nodes")
    items = 0
    for node in nodes:
        units = r.children(node)
        if not units:
            problems.append(f"{node.path}: ## Children has no items")
        for unit in units:
            items += 1
            match = CHILD_ITEM.match(unit.text)
            if not match:
                problems.append(f"{node.path}:{unit.line}: child item is not '[title](path) · ~N words. **Use when** ...'")
                continue
            path, _ = resolve(node.path, match.group("target"))
            target = r.docs.get(path)
            if target is None:
                problems.append(f"{node.path}:{unit.line}: child {match.group('target')} does not exist")
            elif match.group("size") != f"{target.words:,}":
                problems.append(
                    f"{node.path}:{unit.line}: size ~{match.group('size')} words, {path} has {target.words:,}; "
                    "run tools/check.py --write-sizes"
                )
    for doc in r.docs.values():
        limit = LOOKUP_LIMIT if doc.path == LOOKUP_PATH else SIZE_LIMITS.get(str(doc.kind))
        if limit and doc.words > limit:
            problems.append(f"{doc.path}: {doc.words:,} words, over the {doc.kind} limit of {limit:,}")
    return verdict(problems, [f"{items} child items with exact sizes; every file within its size limit"])


def gate_b3(r: Resource) -> Result:
    nodes = r.of_kind(*NODE_KINDS)
    problems = r.missing("book") + need_docs(r, nodes, "nodes")
    related: dict[str, set[str]] = {}
    for doc in r.docs.values():
        units = [u for u in doc.section("Related") if u.kind == "item" and not u.hint]
        related[doc.path] = set()
        if doc.kind in NODE_KINDS and not units:
            problems.append(f"{doc.path}: ## Related has no items")
        for unit in units:
            match = RELATED_ITEM.match(unit.text)
            if not match:
                problems.append(f"{doc.path}:{unit.line}: related item is not '[title](path): why [p.N]'")
                continue
            path, _ = resolve(doc.path, match.group("target"))
            if path not in r.docs:
                problems.append(f"{doc.path}:{unit.line}: related target {match.group('target')} does not exist")
            if len(criterion_words(match.group("why"))) < 3:
                problems.append(f"{doc.path}:{unit.line}: related item does not say why it is related")
            related[doc.path].add(path)
    seeded = 0
    for ref in (r.book or {}).get("crossrefs", []):
        source = r.coverage_target.get(str(ref.get("from")), "").split("#")[0]
        target = r.coverage_target.get(str(ref.get("target")), "").split("#")[0]
        if not source or not target or source == target:
            continue
        holders = {source} | r.parents.get(source, set())
        if any(target in related.get(h, set()) for h in holders):
            seeded += 1
        else:
            problems.append(
                f"{source}: book cross-reference on p.{ref.get('pdf_page')} to Section {ref.get('target_number')} "
                f"({target}) is not under ## Related here or in a parent node"
            )
    return verdict(problems, [f"every node has related links; {seeded} book cross-references seeded"])


def gate_b4(r: Resource) -> Result:
    nodes = r.of_kind(*NODE_KINDS)
    problems = need_docs(r, nodes, "nodes")
    notes = 0
    for node in nodes:
        units = [u for u in node.section("Disambiguation") if u.kind == "item" and not u.hint]
        if not units:
            problems.append(f"{node.path}: ## Disambiguation has no items")
            continue
        if any(u.text == NO_OVERLAP for u in units):
            if len(units) > 1:
                problems.append(f"{node.path}: '{NO_OVERLAP}' must be the only disambiguation item")
            continue
        names = set()
        for unit in r.children(node):
            match = CHILD_ITEM.match(unit.text)
            if match:
                names.add(name_key(match.group("title")))
                target = r.docs.get(resolve(node.path, match.group("target"))[0] or "")
                if target:
                    names.add(name_key(target.title))
        for unit in units:
            match = DISAMBIGUATION_ITEM.match(unit.text)
            if not match:
                problems.append(f"{node.path}:{unit.line}: disambiguation item is not '**A vs B.** what separates them [p.N]'")
                continue
            notes += 1
            lead = [n for n in re.split(r"\s+vs\.?\s+", match.group("lead"), flags=re.I) if n.strip()]
            if len(lead) < 2:
                problems.append(f"{node.path}:{unit.line}: lead names fewer than two siblings")
            for name in lead:
                if name_key(name) not in names:
                    problems.append(f"{node.path}:{unit.line}: '{name.strip()}' is not a child of this node")
    return verdict(problems, [f"{notes} disambiguation notes name only real siblings"], [
        "Judge: confirm every group of children whose use-when conditions overlap has a note, and that "
        f"each '{NO_OVERLAP}' is true. Files: {', '.join(n.path for n in nodes)}",
    ])


def gate_b5(r: Resource) -> Result:
    router = r.docs.get("SKILL.md")
    if router is None:
        return verdict(["SKILL.md is missing"], [])
    problems = []
    children = set(r.child_paths(router))
    for job in JOB_IDS:
        doc = r.doc_by_id(job)
        if doc is None or doc.kind != "job-node" or doc.path not in children:
            problems.append(f"SKILL.md ## Children has no job node with id {job}")
    headers = [u for u in router.units if u.kind == "header-row" and not u.hint]
    rows = [u for u in router.units if u.kind == "row" and not u.hint]
    if not headers or headers[0].text.strip("|").count("|") < 2:
        problems.append("SKILL.md: no routing table with a data-type column and at least two task columns")
    if len(rows) < 3:
        problems.append(f"SKILL.md: routing table has {len(rows)} data rows, needs at least 3 data types")
    for row in rows:
        targets = [r.docs.get(l.path or "") for l in row.links if not l.image]
        if not any(t is not None and t.kind in SPECIFIC_KINDS for t in targets):
            problems.append(f"SKILL.md:{row.line}: routing row links no section, leaf or idiom card")
    return verdict(problems, [f"router lists {len(JOB_IDS)} job entry points and a {len(rows)}-row routing table"])


def gate_b6(r: Resource) -> Result:
    nodes = r.of_kind(*NODE_KINDS)
    problems = need_docs(r, nodes, "nodes")
    for node in nodes:
        problems += [f"{node.path}: no ## {title}" for title in NODE_SECTIONS if not node.has_heading(title)]
    return verdict(problems, ["every node has Children, Disambiguation and Related sections"], [
        "Judge: for each node, pick a realistic query per child and confirm the node alone settles the "
        f"next hop without opening a child. Files: {', '.join(n.path for n in nodes)}",
    ])


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


def gate_e1(r: Resource) -> Result:
    problems = r.missing("book")
    router = r.docs.get("SKILL.md")
    children = set(r.child_paths(router)) if router else set()
    evidence = []
    for job in JOB_IDS:
        doc = r.doc_by_id(job)
        if doc is None or doc.kind != "job-node":
            problems.append(f"no job node with id {job}")
            continue
        if doc.path not in children:
            problems.append(f"SKILL.md ## Children does not link {doc.path}")
        reached = [r.docs[p] for p in r.traverse(doc.path, {LOOKUP_PATH, "SKILL.md"}) if p != doc.path]
        chapters = set().union(*(r.chapters(d) for d in reached)) if reached else set()
        for chapter in JOB_REACH.get(job, ()):
            if chapter in r.book_chapters and chapter not in chapters:
                problems.append(f"{doc.path}: ## Children never leads to chapter {chapter}")
        if job in JOB_CARDS and not any(d.kind == CARD for d in reached):
            problems.append(f"{doc.path}: ## Children never leads to an idiom card")
        if not reached:
            problems.append(f"{doc.path}: leads nowhere")
        evidence.append(f"{job}: reaches {len(reached)} files in chapters {sorted(chapters)}")
    return verdict(problems, evidence)


def gate_e2(r: Resource) -> Result:
    cards = r.of_kind(CARD)
    problems = need_docs(r, cards, "idiom cards")
    hints = f"Implementation hints {HINT}"
    for card in cards:
        if not card.has_heading(hints):
            problems.append(f"{card.path}: no ## {hints}")
            continue
        for library in ("matplotlib", "D3"):
            body = [u for u in card.units if u.h2 == hints and u.h3 == library]
            if not body:
                problems.append(f"{card.path}: no ### {library} hint with content")
    return verdict(problems, [f"{len(cards)} idiom cards carry matplotlib and D3 hints"])


def gate_e3(r: Resource) -> Result:
    problems = need_docs(r, list(r.docs.values()), "markdown files")
    hint_units = 0
    for doc in r.docs.values():
        for unit in doc.units:
            if unit.hint:
                hint_units += 1
                if PAGE_REFERENCE.search(unit.text):
                    problems.append(f"{doc.path}:{unit.line}: hint carries a page reference")
        for heading in doc.headings:
            if heading.hint and PAGE_REFERENCE.search(heading.title):
                problems.append(f"{doc.path}:{heading.line}: hint heading carries a page reference")
    return verdict(problems, [f"{hint_units} hint units, none with a p.N or pp.N-M page reference"])


def gate_e4(r: Resource) -> Result:
    problems = need_docs(r, list(r.docs.values()), "markdown files")
    for doc in r.docs.values():
        for block in doc.verbatims:
            if HINT in block.text:
                problems.append(f"{doc.path}:{block.line}: {HINT} inside a verbatim block")
            if block.hint:
                problems.append(f"{doc.path}:{block.line}: verbatim block inside a hint section")
        for unit in doc.units:
            if not unit.hint and HINT in unit.text:
                problems.append(f"{doc.path}:{unit.line}: {HINT} mixed into book text instead of opening the item")
    return verdict(problems, ["hints sit in their own sections or items, never in verbatim or summary text"])


def gate_e5(r: Resource) -> Result:
    problems = need_docs(r, list(r.docs.values()), "markdown files")
    for doc in r.docs.values():
        book_units = [u for u in doc.units if not u.hint and u.kind != "code"]
        book_blocks = [b for b in doc.verbatims if not b.hint]
        if doc.kind in NODE_KINDS:
            for title in NODE_SECTIONS:
                if not any(u.h2 == title for u in book_units):
                    problems.append(f"{doc.path}: without hints ## {title} is empty")
                if any(u.h2 == title and u.hint for u in doc.units):
                    problems.append(f"{doc.path}: ## {title} depends on a {HINT} item")
        elif doc.kind == CARD:
            for title in CARD_SECTIONS[:-1]:
                if title == "Figures" and not doc.frontmatter.get("figures"):
                    continue
                if not any(u.h2 == title for u in book_units) and not any(b.h2 == title for b in book_blocks):
                    problems.append(f"{doc.path}: without hints ## {title} is empty")
            if doc.frontmatter.get("boxed") is False and not any(
                u.h2 == "Idiom box" and u.text == NO_BOX for u in book_units
            ):
                problems.append(f"{doc.path}: unboxed card must say '{NO_BOX}'")
        elif doc.kind in LEAF_KINDS:
            if not any(u.citations for u in book_units) and not book_blocks:
                problems.append(f"{doc.path}: no book content once hints are removed")
    return verdict(problems, ["every file keeps its book structure with hints removed"])


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
