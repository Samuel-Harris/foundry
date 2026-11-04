"""Gates E1 to E5: job entry points and the separation of [NOT FROM BOOK] hints from book text."""

from __future__ import annotations

import re

from .model import (CARD, CARD_SECTIONS, HINT, JOB_IDS, LEAF_KINDS, LOOKUP_PATH, NO_BOX, NODE_KINDS, NODE_SECTIONS,
                    Result)
from .resource import Resource, need_docs, verdict

JOB_REACH = {"j1": (2, 3), "j3": (4, 6), "j4": (11, 12)}
JOB_CARDS = ("j1", "j2")

PAGE_REFERENCE = re.compile(r"\bpp?\.\s*\d+")


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
