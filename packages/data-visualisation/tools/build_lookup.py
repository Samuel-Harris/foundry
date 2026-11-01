"""Build references/lookup.md from plan.json, coverage.json, book.json, SKILL.md and tools/lookup_concepts.md.

Run from anywhere: uv run tools/build_lookup.py. The chapter Children lines are copied from
SKILL.md so the router stays their single owner; concepts.md holds the hand-written concept rows.
"""
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
skill = root / ".apm/skills/data-visualisation"
coverage = json.loads((root / "provenance/coverage.json").read_text())["entries"]
plan = json.loads((root / "provenance/plan.json").read_text())
book = json.loads((root / "provenance/book.json").read_text())
LIGATURES = {"ﬀ": "ff", "ﬁ": "fi", "ﬂ": "fl", "ﬃ": "ffi", "ﬄ": "ffl"}
first_child = {f["path"]: f["children"][0] for f in plan["files"] if f["kind"] == "section-node"}


def clean(text: str) -> str:
    for lig, plain in LIGATURES.items():
        text = text.replace(lig, plain)
    return text.replace("’", "'")


def rel(path: str) -> str:
    return path.removeprefix("references/")


def cite(span) -> str:
    a, b = span
    return f"[p.{a}]" if a == b else f"[pp.{a}-{b}]"


def title_of(path: str) -> str:
    match = re.search(r'^title: "?(.*?)"?$', (skill / path).read_text(), re.M)
    return clean(match.group(1))


router_children = [
    line.replace("](references/", "](")
    for line in (skill / "SKILL.md").read_text().splitlines()
    if re.match(r"- \[\d+ ", line)
]
chapters = [e for e in coverage if e["level"] == "chapter"]
sections = [e for e in coverage if e["level"] == "section"]
toc_names = {t["id"]: clean(t["title"]) for t in book["toc"] if t["level"] == "idiom"}
numbers = {e["entry"]: e["number"] for e in coverage}

out = []
out.append("""---
id: lookup
kind: index-node
title: "Idiom and Concept Lookup"
pdf_pages: [26, 392]
printed_pages: [1, 367]
toc: []
fidelity: summary
---

# Idiom and Concept Lookup

A name-to-file index for the book, built from its table of contents: every idiom card, every chapter and section, and the book's key concepts, each with the PDF pages it draws on [pp.6-15]. Use it when you know what something is called; use the router's routing table or a job node when you know only the data and the question. Section numbers follow the book [pp.6-15].

## Children
""")
out += router_children
out.append("""
## Disambiguation

- **Analysis Case Studies vs Arrange Tables.** Chapter 15 analyses six whole systems built from the idioms that chapters 7 to 14 define one at a time; look up an idiom in chapters 7 to 14 and a system in chapter 15 [pp.365-367].
- **Rules of Thumb vs Marks and Channels.** Both justify encoding choices; chapter 5 gives perceptual rankings for channels, chapter 6 gives slogans about whole designs such as 3D, animation and overviews [p.120] [pp.141-142].
- **Manipulate View vs Facet into Multiple Views vs Reduce Items and Attributes vs Embed: Focus+Context.** Four of the book's five answers to complexity: change one view over time, split into views or layers, show less, or keep focus and context in one view [p.269] [p.290].

## Related

- [3.6 How: A Preview](ch03-why-task-abstraction/s03-06-how-preview.md): the map of how choices that most entries below belong to [pp.82-83]
- [J1 Choose a Chart or Idiom](jobs/j1-choose-idiom.md): the route to an idiom when its name is not yet known [p.68]

## Idiom cards

Every card, alphabetically, with the book section that holds it; a card's TOC name is given where it differs [pp.6-15].

| Idiom card | Section | Pages |
| --- | --- | --- |""")
for card in sorted(plan["idiom_cards"], key=lambda c: title_of(c["path"]).lower()):
    name = title_of(card["path"])
    aliases = sorted({
        toc_names[t] for t in card.get("toc", [])
        if t in toc_names and toc_names[t].lower().rstrip("s") != name.lower().rstrip("s")
    })
    alias = f" (TOC: {', '.join(aliases)})" if aliases else ""
    out.append(f"| [{name}]({rel(card['path'])}){alias} | {numbers.get(card['section'], '?')} | {cite(card['pdf_pages'])} |")
out.append("""
## Concepts

Key terms, each pointing to the file that defines or argues it [pp.6-15].

| Concept | File | Pages |
| --- | --- | --- |""")
out.append((root / "tools/lookup_concepts.md").read_text().rstrip())
out.append("""
## Sections by chapter

A section with its own node opens with an introduction that sits at the top of its first subsection leaf, linked after the node [pp.6-15].""")
for ch in chapters:
    out.append(f"\n### {ch['number']} {clean(ch['title'])}\n")
    for s in sections:
        if s["number"].split(".")[0] != ch["number"]:
            continue
        line = f"- [{s['number']} {clean(s['title'])}]({rel(s['path'])})"
        if s["path"] in first_child:
            line += f", opening in [{s['number']}.1]({rel(first_child[s['path']])})"
        out.append(f"{line} {cite(s['pdf_pages'])}")
(skill / "references/lookup.md").write_text("\n".join(out) + "\n")
