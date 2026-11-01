"""The skill tree plus its provenance JSON, with the derived graphs every gate reads."""

from __future__ import annotations

import re
from collections import defaultdict, deque
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

from .model import (FAIL, LOOKUP_PATH, NODE_KINDS, NOT_CHECKABLE, PASS, VERBATIM_CLOSE, Doc, Link, Result, Unit,
                    Verbatim, chapter_of, fmt_range, load_docs, load_json, normalise, verbatim_matches, word_list)


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
