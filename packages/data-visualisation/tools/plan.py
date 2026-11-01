"""Plan every file of the resource from provenance/book.json.

Usage: uv run tools/plan.py   (run tools/extract.py first; reads build/pages for sizes)

Writes provenance/plan.json and build/packets/chNN.json, and prints the leaves whose
source text is too large to summarise within the leaf budget.
"""

from __future__ import annotations

import json
import re
import sys

from extract import BOOK_JSON, BUILD_PAGES, PACKAGE, dump_json, slugify
from check import LIGATURES

PLAN_JSON = PACKAGE / "provenance" / "plan.json"
FIGURES_JSON = PACKAGE / "provenance" / "figures.json"
PACKETS = PACKAGE / "build" / "packets"

SECTION_NODE_MIN_PAGES = 6
SLUG_WORDS = 4
LEAF_WORD_BUDGET = 2000
AT_RISK_SOURCE_WORDS = 2 * LEAF_WORD_BUDGET
STOPWORDS = {"a", "an", "the", "and", "or", "of", "to", "in", "for", "on", "with", "is", "are", "do", "it", "its",
             "be", "by", "as", "at", "vs", "versus", "isnt"}

FIGURE_MENTION = re.compile(
    r"\bFigures?\s+(\d+\.\d+(?:\([a-z]\))?(?:(?:,\s*(?:and\s+)?|\s*–\s*|\s+(?:and|through|to)\s+)\d+\.\d+(?:\([a-z]\))?)*)")

# A4: unboxed cards for the core idioms of chapters 10 and 11, one per TOC entry that
# names a colormap type, a non-colour channel, or an interaction idiom.
A4_CARDS = (
    ("s10.03.01", "Categorical Colormaps"),
    ("s10.03.02", "Ordered Colormaps"),
    ("s10.03.03", "Bivariate Colormaps"),
    ("s10.03.04", "Colorblind-Safe Colormaps"),
    ("s10.04.01", "Size Channels"),
    ("s10.04.02", "Angle Channel"),
    ("s10.04.03", "Curvature Channel"),
    ("s10.04.04", "Shape Channel"),
    ("s10.04.05", "Motion Channels"),
    ("s10.04.06", "Texture and Stippling"),
    ("s11.03", "Change View over Time"),
    ("s11.04.02", "Highlighting"),
    ("s11.05.01", "Geometric Zooming"),
    ("s11.05.02", "Semantic Zooming"),
    ("s11.05.03", "Constrained Navigation"),
    ("s11.06.01", "Slice"),
    ("s11.06.02", "Cut"),
    ("s11.06.03", "Project"),
)

# Card id -> the figures that depict its idiom, decided by reading each caption against the
# text where the idiom is discussed. A figure that only sits near the idiom, or shows a
# sibling idiom, stays off the card.
CARD_FIGURES: dict[str, tuple[str, ...]] = {
    "idiom:3d-perspective": ("fig-14-04",),
    "idiom:adjacency-matrix-view": ("fig-09-06", "fig-09-07"),
    "idiom:angle-channel": ("fig-10-14",),
    "idiom:animated-transitions": ("fig-11-05",),
    "idiom:bar-charts": ("fig-07-04", "fig-07-09", "fig-07-16", "fig-07-17"),
    "idiom:birds-eye-maps": ("fig-12-03",),
    "idiom:bivariate-colormaps": ("fig-10-06",),
    "idiom:boxplot-charts": ("fig-13-07",),
    "idiom:cartographic-layering": ("fig-12-13",),
    "idiom:categorical-colormaps": ("fig-10-06", "fig-10-07", "fig-10-08", "fig-10-09", "fig-10-10"),
    "idiom:cerebral": ("fig-12-05", "fig-12-17"),
    "idiom:change-view-over-time": ("fig-11-02", "fig-11-03", "fig-11-04", "fig-11-05"),
    "idiom:choropleth-map": ("fig-08-02",),
    "idiom:cluster-calendar-time-series-vis": ("fig-06-07",),
    "idiom:cluster-heatmaps": ("fig-07-11",),
    "idiom:colorblind-safe-colormaps": (),
    "idiom:constrained-navigation": ("fig-15-20",),
    "idiom:context-preserving-visual-links": ("fig-11-06",),
    "idiom:continuous-scatterplots": ("fig-13-06",),
    "idiom:curvature-channel": (),
    "idiom:cut": ("fig-11-08",),
    "idiom:dense-software-overviews": ("fig-07-20",),
    "idiom:dimensionality-reduction-for-document-collections": ("fig-13-12", "fig-13-13"),
    "idiom:doitrees-revisited": ("fig-14-02",),
    "idiom:dosfa": ("fig-13-04",),
    "idiom:dot-charts": ("fig-07-08",),
    "idiom:ellipsoid-tensor-glyphs": ("fig-08-11", "fig-08-12"),
    "idiom:exploratory-data-visualizer-edv": ("fig-12-02",),
    "idiom:filmfinder": ("fig-13-02",),
    "idiom:fisheye-lens": ("fig-14-05", "fig-14-10"),
    "idiom:flexible-isosurfaces": ("fig-08-05", "fig-08-06"),
    "idiom:force-directed-placement": ("fig-09-04",),
    "idiom:geographically-weighted-boxplots": ("fig-13-11",),
    "idiom:geometric-zooming": (),
    "idiom:grouseflocks": ("fig-09-10",),
    "idiom:heatmaps": ("fig-07-11",),
    "idiom:hierarchical-edge-bundles": ("fig-12-16",),
    "idiom:hierarchical-parallel-coordinates": ("fig-13-09",),
    "idiom:highlighting": ("fig-11-06",),
    "idiom:histograms": ("fig-13-05", "fig-13-08"),
    "idiom:hyperbolic-geometry": ("fig-14-06",),
    "idiom:hyperslice": ("fig-11-09",),
    "idiom:improvise": ("fig-12-07",),
    "idiom:layer-oriented-time-series-vis": ("fig-06-08",),
    "idiom:line-charts": ("fig-07-08", "fig-07-09", "fig-07-10"),
    "idiom:lineup": ("fig-11-03", "fig-11-04"),
    "idiom:motion-channels": (),
    "idiom:multidimensional-transfer-functions": ("fig-08-06b",),
    "idiom:multiform-overview-detail-microarrays": ("fig-12-04",),
    "idiom:multilevel-force-directed-placement-sfdp": ("fig-09-05",),
    "idiom:nonlinear-magnification-fields": ("fig-14-09",),
    "idiom:normalized-stacked-bar-charts": ("fig-07-18",),
    "idiom:ordered-colormaps": ("fig-10-06", "fig-10-11", "fig-10-12", "fig-10-13"),
    "idiom:parallel-coordinates": ("fig-07-12", "fig-07-13", "fig-07-14"),
    "idiom:pie-charts": ("fig-07-17", "fig-07-18"),
    "idiom:pivotgraph": ("fig-15-11", "fig-15-12"),
    "idiom:polar-area-charts": ("fig-07-17",),
    "idiom:project": (),
    "idiom:radial-bar-charts": ("fig-07-15", "fig-07-16"),
    "idiom:scatterplot-matrix-splom": ("fig-07-12",),
    "idiom:scatterplots": ("fig-07-02", "fig-07-03"),
    "idiom:semantic-zooming": ("fig-11-07", "fig-15-20"),
    "idiom:shape-channel": ("fig-10-09",),
    "idiom:similarity-clustered-streamlines": ("fig-08-09",),
    "idiom:size-channels": ("fig-10-09",),
    "idiom:slice": ("fig-11-08", "fig-11-09"),
    "idiom:solarplot": ("fig-13-08",),
    "idiom:stacked-bar-charts": ("fig-07-05", "fig-07-18"),
    "idiom:streamgraphs": ("fig-07-06", "fig-07-07"),
    "idiom:stretch-and-squish-navigation": ("fig-14-07", "fig-14-08"),
    "idiom:superimposed-line-charts": ("fig-12-14", "fig-12-15"),
    "idiom:texture-and-stippling": (),
    "idiom:toolglass-and-magic-lenses": ("fig-14-03",),
    "idiom:topographic-terrain-map": ("fig-08-04",),
    "idiom:treemaps": ("fig-09-08", "fig-09-09"),
    "idiom:trellis": ("fig-12-09", "fig-12-10"),
}

# (PDF page, printed number) -> figure id, where the book's text cites a figure by the
# wrong number. The second "Figure 8.6" (p.213) is called "Figure 8.7(a)-(c)" on p.212.
MISNUMBERED_MENTIONS = {(212, "8.7"): "fig-08-06b"}

# TOC-named idiom id -> box slug, for matches the word rule in match_toc_idioms cannot
# find. Empty: every match in this book is an exact slug, a plural or a word subset.
HAND_MATCHES: dict[str, str] = {}


def short_slug(title: str) -> str:
    words = [w for w in slugify(title).split("-") if w and w not in STOPWORDS]
    return "-".join(words[:SLUG_WORDS])


def number_part(ident: str) -> str:
    return ident[1:].replace(".", "-")


def tokens(slug: str) -> set[str]:
    return {w[:-1] if w.endswith("s") and len(w) > 3 else w for w in slug.split("-") if w not in STOPWORDS}


def match_toc_idioms(toc_idioms: list[dict], boxes: list[dict]) -> dict[str, dict]:
    """TOC idiom id -> the box it names. Exact slugs claim their box first; a remaining
    TOC idiom then takes the first unclaimed box inside its pages whose words (plurals
    folded) contain, or are contained in, its own."""
    by_slug = {b["slug"]: b for b in boxes}
    matched: dict[str, dict] = {}
    for t in toc_idioms:
        slug = HAND_MATCHES.get(t["id"], t["id"][len("idiom:"):])
        if slug in by_slug:
            matched[t["id"]] = by_slug[slug]
    claimed = {b["slug"] for b in matched.values()}
    for t in toc_idioms:
        if t["id"] in matched:
            continue
        want = tokens(t["id"][len("idiom:"):])
        for box in sorted(boxes, key=lambda b: b["pdf_page"]):
            have = tokens(box["slug"])
            if (box["slug"] not in claimed and t["pdf_start"] <= box["pdf_page"] <= t["pdf_end"]
                    and (want <= have or have <= want)):
                matched[t["id"]] = box
                claimed.add(box["slug"])
                break
    return matched


def page_words(pages: tuple[int, int]) -> int:
    total = 0
    for p in range(pages[0], pages[1] + 1):
        total += len(page_text(p).split())
    return total


def build_plan(book: dict, read_page=None) -> dict:
    read_page = read_page or page_text
    toc = book["toc"]
    by_id = {e["id"]: e for e in toc}
    kids: dict[str, list[dict]] = {}
    for e in toc:
        kids.setdefault(e["parent"], []).append(e)

    def numbered_kids(ident: str) -> list[dict]:
        return [k for k in kids.get(ident, []) if k["level"] != "idiom"]

    def descendants(ident: str) -> list[str]:
        out = []
        for k in numbered_kids(ident):
            out.append(k["id"])
            out += descendants(k["id"])
        return out

    files: list[dict] = []
    entries: dict[str, str] = {}
    owner_node: dict[str, str] = {}

    def add(path: str, kind: str, top: dict, covered: list[str], pages: tuple[int, int], chapter: int) -> dict:
        f = {"path": path, "kind": kind, "id": top["id"], "chapter": chapter, "toc": covered,
             "pdf_pages": list(pages), "children": []}
        files.append(f)
        for ident in covered:
            entries[ident] = path if ident == top["id"] else f"{path}#{ident}"
        return f

    for ch in (e for e in toc if e["level"] == "chapter"):
        n = int(ch["id"][2:])
        ch_dir = f"references/ch{n:02d}-{short_slug(ch['title'])}"
        node = add(f"{ch_dir}/node.md", "chapter-node", ch, [ch["id"]], (ch["pdf_start"], ch["pdf_end"]), n)
        for sec in numbered_kids(ch["id"]):
            base = f"s{number_part(sec['id'])}-{short_slug(sec['title'])}"
            subs = numbered_kids(sec["id"])
            span = sec["pdf_end"] - sec["pdf_start"] + 1
            if span >= SECTION_NODE_MIN_PAGES and subs:
                sec_dir = f"{ch_dir}/{base}"
                sec_node = add(f"{sec_dir}/node.md", "section-node", sec, [sec["id"]],
                               (sec["pdf_start"], sec["pdf_end"]), n)
                node["children"].append(sec_node["path"])
                owner_node[sec["id"]] = sec_node["path"]
                for i, sub in enumerate(subs):
                    start = sec["pdf_start"] if i == 0 else sub["pdf_start"]
                    leaf = add(f"{sec_dir}/s{number_part(sub['id'])}-{short_slug(sub['title'])}.md",
                               "subsection-leaf", sub, [sub["id"]] + descendants(sub["id"]),
                               (start, sub["pdf_end"]), n)
                    sec_node["children"].append(leaf["path"])
            else:
                leaf = add(f"{ch_dir}/{base}.md", "section-leaf", sec, [sec["id"]] + descendants(sec["id"]),
                           (sec["pdf_start"], sec["pdf_end"]), n)
                node["children"].append(leaf["path"])
                owner_node[sec["id"]] = node["path"]

    def section_of(ident: str) -> str:
        e = by_id[ident]
        while e["level"] not in ("section",):
            e = by_id[e["parent"]]
        return e["id"]

    cards = plan_cards(book, by_id, section_of, owner_node)
    for card in cards:
        for ident in card["toc"]:
            entries[ident] = card["path"] if ident == card["id"] else f"{card['path']}#{ident}"
        parent = next(f for f in files if f["path"] == card["parent"])
        parent["children"].append(card["path"])

    homes = figure_homes(book, files, cards, read_page)
    return {"files": files, "entries": dict(sorted(entries.items())), "idiom_cards": cards, "figure_homes": homes}


def plan_cards(book: dict, by_id: dict, section_of, owner_node: dict[str, str]) -> list[dict]:
    toc_idioms = [e for e in book["toc"] if e["level"] == "idiom"]
    boxes = book["idiom_boxes"]
    covers: dict[str, list[str]] = {b["slug"]: [] for b in boxes}
    matched = match_toc_idioms(toc_idioms, boxes)
    unboxed = [t for t in toc_idioms if t["id"] not in matched]
    for ident, box in matched.items():
        covers[box["slug"]].append(ident)

    def enclosing_idiom(page: int, chapter: int) -> dict | None:
        hits = [t for t in toc_idioms if t["pdf_start"] <= page <= t["pdf_end"] and int(section_of(t["parent"])[1:3]) == chapter]
        return hits[-1] if hits else None

    cards = []
    for b in boxes:
        matched = [by_id[i] for i in covers[b["slug"]]]
        if matched:
            lo = min([t["pdf_start"] for t in matched] + [b["pdf_page"]])
            hi = max([t["pdf_end"] for t in matched] + [b["pdf_page"]])
        elif (around := enclosing_idiom(b["pdf_page"], b["chapter"])) is not None:
            lo, hi = min(around["pdf_start"], b["pdf_page"]), max(around["pdf_end"], b["pdf_page"])
        else:
            sec = by_id[b["section"]]
            lo, hi = sec["pdf_start"], sec["pdf_end"]
        cards.append(card(f"idiom:{b['slug']}", b["name"], True, b["chapter"], b["section"],
                          owner_node[section_of(b["section"])], (lo, hi), covers[b["slug"]]))
    for t in unboxed:
        sec = section_of(t["parent"])
        cards.append(card(t["id"], t["title"], False, int(sec[1:3]), t["parent"], owner_node[sec],
                          (t["pdf_start"], t["pdf_end"]), [t["id"]]))
    for ident, name in A4_CARDS:
        e = by_id[ident]
        sec = section_of(ident)
        cards.append(card(f"idiom:{slugify(name)}", name, False, int(sec[1:3]), ident, owner_node[sec],
                          (e["pdf_start"], e["pdf_end"]), []))
    ids = [c["id"] for c in cards]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        raise ValueError(f"two cards share an id: {dupes}")
    if set(ids) != set(CARD_FIGURES):
        raise ValueError(f"CARD_FIGURES does not match the planned cards: "
                         f"missing {sorted(set(ids) - set(CARD_FIGURES))}, unknown {sorted(set(CARD_FIGURES) - set(ids))}")
    known = {f["id"] for f in book["figures"]}
    for c in cards:
        if unknown := set(CARD_FIGURES[c["id"]]) - known:
            raise ValueError(f"CARD_FIGURES[{c['id']!r}] names figures not in book.json: {sorted(unknown)}")
        c["figures"] = list(CARD_FIGURES[c["id"]])
    return sorted(cards, key=lambda c: c["id"])


def card(ident: str, name: str, boxed: bool, chapter: int, section: str, parent: str,
         pages: tuple[int, int], toc_ids: list[str]) -> dict:
    return {"id": ident, "name": name, "path": f"references/idioms/{ident[len('idiom:'):]}.md", "boxed": boxed,
            "chapter": chapter, "section": section, "parent": parent, "pdf_pages": list(pages),
            "toc": sorted(toc_ids), "figures": []}


def page_text(page: int) -> str:
    return (BUILD_PAGES / f"{page:04d}.txt").read_text(encoding="utf-8")


def fold(text: str) -> str:
    for lig, plain in LIGATURES.items():
        text = text.replace(lig, plain)
    return " ".join(text.split())


def alnum(text: str) -> str:
    return re.sub(r"[^0-9a-z]", "", fold(text).lower())


def strip_captions(lines: list[str], captions: list[dict]) -> list[str]:
    """Drop each caption printed on the page: its "Figure N.M." head line and the lines
    after it while they still spell out the caption (hyphenation and spacing ignored)."""
    drop: set[int] = set()
    for fig in captions:
        head = f"Figure {fig['number']}."
        want = alnum(f"{head} {fig['caption']}")
        for i, line in enumerate(lines):
            if not fold(line).startswith(head) or not want.startswith(alnum(line)):
                continue
            got = ""
            for j in range(i, len(lines)):
                if not want.startswith(got + alnum(lines[j])):
                    break
                got += alnum(lines[j])
                drop.add(j)
            break
    return [line for i, line in enumerate(lines) if i not in drop]


def mentioned_numbers(text: str) -> list[str]:
    return [n for span in FIGURE_MENTION.findall(fold(text)) for n in re.findall(r"\d+\.\d+", span)]


def leaf_mentions(book: dict, leaves: list[dict], read_page) -> dict[str, list[tuple[int, str]]]:
    """Printed figure number -> (page, leaf) for every mention in a leaf's body text,
    captions excluded. A page shared by two leaves is split at the later one's heading."""
    owner = {ident: f["path"] for f in leaves for ident in f["toc"]}
    numbered = [e for e in book["toc"] if e["level"] not in ("chapter", "idiom")]
    for i, e in enumerate(numbered):
        if e["id"] not in owner:
            owner[e["id"]] = next((owner[x["id"]] for x in numbered[i + 1:] if x["id"] in owner), None)
    starts: dict[int, list[dict]] = {}
    for e in numbered:
        starts.setdefault(e["pdf_start"], []).append(e)
    captions: dict[int, list[dict]] = {}
    for fig in book["figures"]:
        captions.setdefault(fig["pdf_page"], []).append(fig)

    found: dict[str, list[tuple[int, str]]] = {}
    for ch in (e for e in book["toc"] if e["level"] == "chapter"):
        current = None
        for page in range(ch["pdf_start"], ch["pdf_end"] + 1):
            lines = strip_captions(read_page(page).splitlines(), captions.get(page, []))
            heads = {}
            for e in starts.get(page, []):
                want = fold(f"{e['number']} {e['title']}")
                at = next((i for i, line in enumerate(lines) if fold(line) and (
                    fold(line).startswith(want) or (want.startswith(fold(line)) and len(fold(line)) > len(e["number"]) + 3))), 0)
                heads[at] = owner[e["id"]]
            chunk: list[str] = []
            for i, line in enumerate(lines + [""]):
                if i in heads or i == len(lines):
                    for n in mentioned_numbers(re.sub(r"-\n", "", "\n".join(chunk))) if current else []:
                        found.setdefault(n, []).append((page, current))
                    chunk, current = [], heads.get(i, current)
                chunk.append(line)
    return found


def figure_homes(book: dict, files: list[dict], cards: list[dict], read_page) -> dict[str, list[str]]:
    """The leaves of the figure's chapter whose body text mentions it by number; a figure
    sharing its printed number takes only the mentions nearer its page than the other's,
    and MISNUMBERED_MENTIONS overrides the number where the text cites the wrong figure.
    A figure on a chapter's opening overview page goes to the chapter's first leaf; one no
    leaf mentions falls back to every leaf whose pages hold it. Plus every card that lists
    it. Only the opening overview figure widens a leaf's range; figure lines are exempt from
    the citation-range check, so other homes leave ranges as the text spans."""
    leaves = [f for f in files if f["kind"].endswith("leaf")]
    by_number: dict[str, list[dict]] = {}
    for fig in book["figures"]:
        by_number.setdefault(fig["number"], []).append(fig)
    mentioned_in: dict[str, list[str]] = {}
    for number, found in leaf_mentions(book, leaves, read_page).items():
        for page, path in found:
            fig_id = MISNUMBERED_MENTIONS.get((page, number))
            if fig_id is None and number in by_number:
                fig_id = min(by_number[number], key=lambda f: (abs(f["pdf_page"] - page), f["pdf_page"]))["id"]
            if fig_id:
                mentioned_in.setdefault(fig_id, []).append(path)
    homes: dict[str, list[str]] = {}
    for fig in book["figures"]:
        mine_ch = [f for f in leaves if f["chapter"] == fig["chapter"]]
        if fig["pdf_page"] < min(f["pdf_pages"][0] for f in mine_ch):
            first = min(mine_ch, key=lambda f: f["pdf_pages"][0])
            first["pdf_pages"] = [fig["pdf_page"], first["pdf_pages"][1]]
            mine = [first["path"]]
        else:
            near = mentioned_in.get(fig["id"], [])
            mine = [f["path"] for f in mine_ch if f["path"] in near] or [
                f["path"] for f in mine_ch if f["pdf_pages"][0] <= fig["pdf_page"] <= f["pdf_pages"][1]]
        homes[fig["id"]] = mine + [c["path"] for c in cards if fig["id"] in c["figures"]]
    return dict(sorted(homes.items()))


def packets(book: dict, plan: dict, figures: list[dict]) -> dict[int, dict]:
    files_by_ch: dict[int, list[dict]] = {}
    for f in plan["files"]:
        files_by_ch.setdefault(f["chapter"], []).append(f)
    by_fig = {f["id"]: f for f in figures}
    toc_chapter = {}
    for e in book["toc"]:
        parent = e
        while parent["parent"]:
            parent = next(x for x in book["toc"] if x["id"] == parent["parent"])
        toc_chapter[e["id"]] = int(parent["id"][2:])
    out = {}
    for ch in (e for e in book["toc"] if e["level"] == "chapter"):
        n = int(ch["id"][2:])
        out[n] = {
            "chapter": n,
            "title": ch["title"],
            "pdf_pages": [ch["pdf_start"], ch["pdf_end"]],
            "files": files_by_ch[n],
            "idiom_cards": [c for c in plan["idiom_cards"] if c["chapter"] == n],
            "idiom_boxes": [b for b in book["idiom_boxes"] if b["chapter"] == n],
            "toc": [e for e in book["toc"] if toc_chapter[e["id"]] == n],
            "pages": [f"build/pages/{p:04d}.txt" for p in range(ch["pdf_start"], ch["pdf_end"] + 1)],
            "figures": [{"id": f["id"], "number": f["number"], "pdf_page": f["pdf_page"], "caption": f["caption"],
                         "file": by_fig.get(f["id"], {}).get("file"), "homes": plan["figure_homes"][f["id"]]}
                        for f in book["figures"] if f["chapter"] == n],
            "crossrefs": [dict(c, target_path=plan["entries"].get(c["target"]))
                          for c in book["crossrefs"] if c["from"] and toc_chapter[c["from"]] == n],
        }
    return out


def main() -> int:
    book = json.loads(BOOK_JSON.read_text(encoding="utf-8"))
    plan = build_plan(book)
    dump_json(PLAN_JSON, plan)
    figures = json.loads(FIGURES_JSON.read_text(encoding="utf-8"))["figures"] if FIGURES_JSON.exists() else []
    for n, packet in packets(book, plan, figures).items():
        dump_json(PACKETS / f"ch{n:02d}.json", packet)

    kinds: dict[str, int] = {}
    for f in plan["files"]:
        kinds[f["kind"]] = kinds.get(f["kind"], 0) + 1
    kinds["idiom-card"] = len(plan["idiom_cards"])
    print(f"planned files: {kinds}", file=sys.stderr)
    leaves = [f for f in plan["files"] if f["kind"].endswith("leaf")]
    risky = [(page_words(tuple(f["pdf_pages"])), f) for f in leaves]
    risky = sorted(((w, f) for w, f in risky if w > AT_RISK_SOURCE_WORDS), key=lambda x: -x[0])
    print(f"leaves whose source exceeds {AT_RISK_SOURCE_WORDS} words: {len(risky)}/{len(leaves)}", file=sys.stderr)
    for words, f in risky:
        print(f"  {words:6d} words  pp.{f['pdf_pages'][0]}-{f['pdf_pages'][1]}  {f['path']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
