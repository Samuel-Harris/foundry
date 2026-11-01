"""Gates A1 to A5 (coverage of the book) and B1 to B6 (navigation through the tree)."""

from __future__ import annotations

import re

from .model import (CARD, CARD_SECTIONS, CITATION, JOB_IDS, LOOKUP_PATH, NO_OVERLAP, NODE_KINDS, NODE_SECTIONS,
                    SPECIFIC_KINDS, Doc, Result, Verbatim, fmt_range, links_in, normalise, resolve, verbatim_matches)
from .resource import Resource, need_docs, verdict

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

UNBOXED_CHAPTERS = (10, 11)

STOPWORDS = frozenset(
    "a an the and or of to in on for with by is are be this that it its as at from when you your "
    "use need needs want wants which what how into than then there these those not no any all one "
    "more most should can do does".split()
)

CONCEPTS = "Concepts"
BOX_KEY_SUFFIX = re.compile(r"\s*\(\d+\)$")  # book.json numbers a repeated field label, e.g. "What: Derived (2)"

CHILD_ITEM = re.compile(
    r"^\[(?P<title>[^\]]+)\]\((?P<target>[^)\s]+)\) · ~(?P<size>[\d,]+|\?) words\. "
    r"\*\*Use when\*\* (?P<criterion>.+)$"
)
RELATED_ITEM = re.compile(r"^\[(?P<title>[^\]]+)\]\((?P<target>[^)\s]+)\): (?P<why>.+)$")
DISAMBIGUATION_ITEM = re.compile(r"^\*\*(?P<lead>.+?)\.\*\* (?P<text>.+)$")


def criterion_words(text: str) -> list[str]:
    return re.findall(r"[a-z]+", CITATION.sub(" ", text).lower())


def name_key(name: str) -> str:
    name = re.sub(r"^\d+(\.\d+)*\s+", "", name.strip())
    words = re.findall(r"[a-z0-9]+", name.lower())
    return " ".join(w[:-1] if w.endswith("s") and len(w) > 3 else w for w in words)


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
