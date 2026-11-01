"""Behaviour of tools/check.py, driven through its CLI against a tiny fixture skill."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

CHECK = Path(__file__).resolve().parents[1] / "check.py"

LEAF = "references/ch01-arrange-tables/s01-01-why-arrange.md"
NODE = "references/ch01-arrange-tables/node.md"
CARD = "references/idioms/scatterplots.md"
CAPTION = "A scatterplot of two quantitative attributes."
JUDGED = {"B1", "B4", "B6", "C6"}

PAGES = {
    10: "Chapter 1 Arrange Tables\nTables hold keys and values.\n",
    11: "Arrange tables by ex-\npressing values on aligned axes. A scatterplot shows two “quantitative” attributes.\n",
    12: "Idiom Scatterplots\nWhat: Data Two quantitative value attributes.\nThe subsection on keys.\n",
}


def front(**fields) -> str:
    return "---\n" + "".join(f"{key}: {json.dumps(value)}\n" for key, value in fields.items()) + "---\n"


def node(doc_id: str, kind: str, title: str, children: list[tuple[str, str, str, str]], related: str,
         disambiguation: str = "- No overlapping children.", pages=(10, 12), extra: str = "") -> str:
    items = "".join(
        f"- [{name}]({target}) · ~? words. **Use when** {criterion} [{cite}]\n"
        for name, target, criterion, cite in children
    )
    return front(id=doc_id, kind=kind, title=title, pdf_pages=list(pages), toc=[], fidelity="summary") + (
        f"# {title}\n\nRoutes the reader through the arrangement of tables. [pp.10-12]\n\n"
        f"## Children\n\n{items}\n## Disambiguation\n\n{disambiguation}\n\n## Related\n\n{related}\n{extra}"
    )


CHAPTER_CHILD = ("1 Arrange Tables", "../ch01-arrange-tables/node.md",
                 "your data is a table of keys and values that needs a spatial layout", "pp.10-12")
CARD_CHILD = ("Scatterplots", "../idioms/scatterplots.md",
              "plotting two quantitative attributes to reveal correlation, clusters and outliers", "pp.11-12")
CARD_RELATED = "- [Scatterplots](../idioms/scatterplots.md): the chapter's main idiom for two attributes [p.12]\n"

FILES = {
    "SKILL.md": front(
        name="data-visualisation", description="Routes visualisation questions.", id="router", kind="router",
        title="Data visualisation", pdf_pages=[10, 12], toc=[], fidelity="summary",
    ) + textwrap.dedent("""\
        # Data visualisation

        Entry point for choosing, coding, critiquing and composing visualisations. [pp.10-12]

        ## Children

        - [J1 Choose an idiom](references/jobs/j1-choose-idiom.md) · ~? words. **Use when** someone hands you a dataset plus question and wants a chart type picked [p.10]
        - [J2 Write plotting code](references/jobs/j2-write-code.md) · ~? words. **Use when** the encoding is already decided and matplotlib or D3 source must be produced [p.11]
        - [J3 Critique a visualisation](references/jobs/j3-critique.md) · ~? words. **Use when** an existing figure needs review against perceptual rules and validation levels [p.10]
        - [J4 Design dashboards](references/jobs/j4-dashboards.md) · ~? words. **Use when** several linked views, filtering or navigation must be planned together [p.10]
        - [1 Arrange Tables](references/ch01-arrange-tables/node.md) · ~? words. **Use when** your data is a table of keys and values that needs a spatial layout [pp.10-12]
        - [Lookup](references/lookup.md) · ~? words. **Use when** you already know an idiom or concept name and want its exact page directly [pp.10-12]

        ## Routing table

        | Data type | Compare values | Find correlation |
        | --- | --- | --- |
        | Table | [1.1 Why Arrange?](references/ch01-arrange-tables/s01-01-why-arrange.md) [p.10] | [Scatterplots](references/idioms/scatterplots.md) [p.12] |
        | Multidimensional table | [1.1 Why Arrange?](references/ch01-arrange-tables/s01-01-why-arrange.md) [p.11] | [Scatterplots](references/idioms/scatterplots.md) [p.12] |
        | Key-value table | [1.1 Why Arrange?](references/ch01-arrange-tables/s01-01-why-arrange.md) [p.10] | [Scatterplots](references/idioms/scatterplots.md) [p.11] |

        ## Disambiguation

        - **J1 Choose an idiom vs J2 Write plotting code.** Choosing settles the encoding; writing code assumes it is settled. [p.11]

        ## Related

        - [Scatterplots](references/idioms/scatterplots.md): the most common answer for two quantitative attributes [p.12]
        """),
    "references/jobs/j1-choose-idiom.md": node("j1", "job-node", "J1 Choose an idiom", [CHAPTER_CHILD], CARD_RELATED),
    "references/jobs/j2-write-code.md": node("j2", "job-node", "J2 Write plotting code", [CARD_CHILD], CARD_RELATED),
    "references/jobs/j3-critique.md": node("j3", "job-node", "J3 Critique a visualisation", [CHAPTER_CHILD], CARD_RELATED),
    "references/jobs/j4-dashboards.md": node("j4", "job-node", "J4 Design dashboards", [CHAPTER_CHILD], CARD_RELATED),
    "references/lookup.md": node("lookup", "index-node", "Lookup", [
        ("1 Arrange Tables", "ch01-arrange-tables/node.md", "the question concerns spatial layout of keys and values in tables", "pp.10-12"),
        ("1.1 Why Arrange?", "ch01-arrange-tables/s01-01-why-arrange.md", "deciding how spatial position expresses keys versus values", "pp.10-12"),
        ("Scatterplots", "idioms/scatterplots.md", "plotting two quantitative attributes to reveal correlation, clusters and outliers", "pp.11-12"),
    ], "- [Scatterplots](idioms/scatterplots.md): the chapter's main idiom for two attributes [p.12]\n"),
    NODE: node("ch01", "chapter-node", "1 Arrange Tables", [
        ("1.1 Why Arrange?", "s01-01-why-arrange.md", "deciding how spatial position expresses keys versus values", "pp.10-12"),
        ("Scatterplots", "../idioms/scatterplots.md", "plotting two quantitative attributes to reveal correlation, clusters and outliers", "pp.11-12"),
    ], "- [Scatterplots](../idioms/scatterplots.md): the chapter's main idiom for two attributes [p.12]\n",
        disambiguation="- **Why Arrange vs Scatterplots.** The section covers the layout choice; the card covers one idiom. [p.11]",
    ).replace('toc: []', 'toc: ["ch01"]'),
    LEAF: front(id="s01.01", kind="section-leaf", title="Why Arrange?", pdf_pages=[10, 12], printed_pages=[1, 3],
                toc=["s01.01", "s01.01.01"], fidelity="mixed") + textwrap.dedent(f"""\
        # 1.1 Why Arrange?

        Tables hold keys and values, and arrangement decides where each lands. [p.10]

        <!-- verbatim p.11 -->
        > Arrange tables by expressing values on aligned axes.
        <!-- /verbatim -->

        <a id="s01.01.01"></a>
        ### 1.1.1 Keys

        The subsection treats keys as the index of a table. [p.12]

        ## Figures

        - ![Figure 1.1](../../assets/figures/fig-01-01.png) **Figure 1.1** [p.11]. {CAPTION}

        ## Related

        - [Scatterplots](../idioms/scatterplots.md): the idiom that arranges two value attributes [p.12]
        """),
    CARD: front(id="idiom:scatterplots", kind="idiom-card", title="Scatterplots", pdf_pages=[11, 12],
                printed_pages=[2, 3], toc=["idiom:scatterplots"], fidelity="mixed", boxed=True,
                figures=["fig-01-01"]) + textwrap.dedent(f"""\
        # Scatterplots

        ## Idiom box

        <!-- verbatim p.12 -->
        > What: Data Two quantitative value attributes.
        <!-- /verbatim -->

        ## What it is

        A scatterplot places items by two quantitative attributes. [p.11]

        ## Use when / avoid when

        - Use it to show two “quantitative” attributes together. [p.11]

        ## Figures

        - ![Figure 1.1](../../assets/figures/fig-01-01.png) **Figure 1.1** [p.11]. {CAPTION}

        ## Alternatives and disambiguation

        - Aligned axes arrange values in a table too. [p.11]

        ## Related

        - [1.1 Why Arrange?](../ch01-arrange-tables/s01-01-why-arrange.md): the section that motivates the idiom [p.10]

        ## Implementation hints {"[NOT FROM BOOK]"}

        ### matplotlib

        Call `ax.scatter(x, y)` with one point per item.

        ### D3

        Append one circle per item with linear x and y scales.
        """),
}

BOOK = {
    "pdf": {"pages": 12, "sha256": "0"},
    "page_map": [{"from_pdf": 1, "to_pdf": 9, "offset": 1, "style": "roman"},
                 {"from_pdf": 10, "to_pdf": 12, "offset": 9, "style": "arabic"}],
    "toc": [
        {"id": "ch01", "level": "chapter", "number": "1", "title": "Arrange Tables", "parent": None,
         "printed_page": 1, "pdf_start": 10, "pdf_end": 12},
        {"id": "s01.01", "level": "section", "number": "1.1", "title": "Why Arrange?", "parent": "ch01",
         "printed_page": 1, "pdf_start": 10, "pdf_end": 12},
        {"id": "s01.01.01", "level": "subsection", "number": "1.1.1", "title": "Keys", "parent": "s01.01",
         "printed_page": 3, "pdf_start": 12, "pdf_end": 12},
        {"id": "idiom:scatterplots", "level": "idiom", "number": "", "title": "Scatterplots", "parent": "s01.01",
         "printed_page": 3, "pdf_start": 11, "pdf_end": 12},
    ],
    "idiom_boxes": [{"slug": "scatterplots", "name": "Scatterplots", "chapter": 1, "section": "s01.01",
                     "pdf_page": 12, "fields": {"What: Data": "Two quantitative value attributes."}}],
    "figures": [{"id": "fig-01-01", "number": "1.1", "chapter": 1, "pdf_page": 11, "caption": CAPTION}],
    "crossrefs": [],
}

PLAN = {
    "files": [
        {"path": NODE, "kind": "chapter-node", "id": "ch01", "chapter": 1, "toc": ["ch01"], "pdf_pages": [10, 12],
         "children": [LEAF]},
        {"path": LEAF, "kind": "section-leaf", "id": "s01.01", "chapter": 1, "toc": ["s01.01", "s01.01.01"],
         "pdf_pages": [10, 12], "children": []},
    ],
    "entries": {"ch01": NODE, "s01.01": LEAF, "s01.01.01": f"{LEAF}#s01.01.01", "idiom:scatterplots": CARD},
    "idiom_cards": [{"id": "idiom:scatterplots", "path": CARD, "boxed": True, "chapter": 1, "section": "s01.01",
                     "parent": NODE, "pdf_pages": [11, 12], "figures": ["fig-01-01"]}],
    "figure_homes": {"fig-01-01": [LEAF, CARD]},
}

FIGURES = [{"id": "fig-01-01", "number": "1.1", "pdf_page": 11, "caption": CAPTION,
            "file": "assets/figures/fig-01-01.png", "method": "embedded", "dpi": 150, "reason": None,
            "referenced_by": []}]

LEDGER = textwrap.dedent("""\
    # Fidelity ledger

    | Level | Choice | Reason |
    | --- | --- | --- |
    | Router, job nodes, lookup | Summary, cited, navigation only | Small enough to read at every hop |
    | Chapter and section nodes | Summary, cited, navigation only | Content lives in leaves |
    | Section and subsection leaves | Mixed | Verbatim where wording matters |
    | Idiom cards | Mixed | The box is the book's own schema |
    """)


class CheckTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.skill = self.tmp / "skill"
        self.provenance = self.tmp / "provenance"
        self.pages = self.tmp / "pages"
        for path, text in FILES.items():
            self.write(path, text)
        figure = self.skill / "assets/figures/fig-01-01.png"
        figure.parent.mkdir(parents=True)
        figure.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\0" * 16)
        self.pages.mkdir()
        for page, text in PAGES.items():
            (self.pages / f"{page:04d}.txt").write_text(text)
        self.provenance.mkdir()
        for name, data in (("book.json", BOOK), ("plan.json", PLAN), ("figures.json", FIGURES)):
            (self.provenance / name).write_text(json.dumps(data))
        (self.provenance / "fidelity-ledger.md").write_text(LEDGER)

    def write(self, path: str, text: str) -> None:
        target = self.skill / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)

    def edit(self, path: str, old: str, new: str) -> None:
        text = (self.skill / path).read_text()
        self.assertIn(old, text)
        self.write(path, text.replace(old, new, 1))

    def check(self, *extra: str) -> tuple[int, dict[str, str]]:
        proc = subprocess.run(
            [sys.executable, str(CHECK), "--skill-dir", str(self.skill), "--provenance-dir", str(self.provenance),
             "--pages-dir", str(self.pages), *extra],
            capture_output=True, text=True,
        )
        self.assertNotIn("Traceback", proc.stderr)
        report = (self.provenance / "reports" / "self-check.md").read_text()
        statuses = dict(re.findall(r"^\| ([A-F]\d) \| ([A-Z-]+) \|", report, re.M))
        self.output = proc.stdout + report
        return proc.returncode, statuses

    def assert_fails(self, gate: str, *extra: str) -> None:
        code, statuses = self.check("--write-sizes", *extra)
        self.assertEqual(statuses[gate], "FAIL", self.output)
        self.assertEqual(code, 1)

    def test_fixture_passes_every_mechanical_gate(self) -> None:
        code, statuses = self.check("--write-sizes")
        self.assertEqual(len(statuses), 32)
        for gate, status in statuses.items():
            self.assertEqual(status, "NOT-CHECKABLE" if gate in JUDGED else "PASS", f"{gate}\n{self.output}")
        self.assertEqual(code, 0, self.output)
        self.assertIn("· ~", (self.skill / NODE).read_text())
        self.assertNotIn("~? words", (self.skill / NODE).read_text())
        figures = json.loads((self.provenance / "figures.json").read_text())
        self.assertEqual(figures[0]["referenced_by"], [LEAF, CARD])
        coverage = json.loads((self.provenance / "coverage.json").read_text())
        self.assertIn({"entry": "s01.01.01", "path": f"{LEAF}#s01.01.01"},
                      [{"entry": e["entry"], "path": e["path"]} for e in coverage["entries"]])
        self.assertIn("## Measured counts", (self.provenance / "fidelity-ledger.md").read_text())

    def test_reruns_are_stable(self) -> None:
        self.check("--write-sizes")
        before = {p: p.read_text() for p in self.tmp.rglob("*.md")}
        code, _ = self.check("--write-sizes")
        self.assertEqual(code, 0)
        self.assertEqual(before, {p: p.read_text() for p in self.tmp.rglob("*.md")})

    def test_unwritten_sizes_fail_b2(self) -> None:
        code, statuses = self.check()
        self.assertEqual(statuses["B2"], "FAIL")
        self.assertEqual(code, 1)

    def test_leaf_linked_only_from_lookup_is_an_orphan(self) -> None:
        self.edit(NODE, "- [1.1 Why Arrange?](s01-01-why-arrange.md)", "- [1.1 Why Arrange?](../idioms/scatterplots.md)")
        code, statuses = self.check("--write-sizes")
        self.assertEqual((statuses["A2"], statuses["F3"]), ("FAIL", "FAIL"), self.output)

    def test_missing_card_fails_a3(self) -> None:
        (self.skill / CARD).unlink()
        self.assert_fails("A3")

    def test_missing_anchor_fails_a1(self) -> None:
        self.edit(LEAF, '<a id="s01.01.01"></a>', "")
        self.assert_fails("A1")

    def test_title_restating_use_when_fails_b1(self) -> None:
        self.edit(NODE, "plotting two quantitative attributes to reveal correlation, clusters and outliers",
                  "for scatterplots")
        self.assert_fails("B1")

    def test_unknown_sibling_in_disambiguation_fails_b4(self) -> None:
        self.edit(NODE, "**Why Arrange vs Scatterplots.**", "**Why Arrange vs Heatmaps.**")
        self.assert_fails("B4")

    def test_unseeded_book_cross_reference_fails_b3(self) -> None:
        book = dict(BOOK, crossrefs=[{"from": "s01.01.01", "pdf_page": 12, "target_number": "1", "target": "ch01"}])
        (self.provenance / "book.json").write_text(json.dumps(book))
        self.assert_fails("B3")

    def test_changed_word_in_verbatim_fails_c1(self) -> None:
        self.edit(LEAF, "> Arrange tables by expressing values", "> Arrange tables by expressing keys")
        self.assert_fails("C1")

    def test_verbatim_quote_may_cross_a_page_break_past_margin_notes(self) -> None:
        (self.pages / "0011.txt").write_text(PAGES[11] + "Values sit on axes that\n\nA margin note on eleven.\n")
        (self.pages / "0012.txt").write_text("run across the page.\n" + PAGES[12] + "\nA margin note on twelve.\n")
        self.edit(LEAF, "<!-- verbatim p.11 -->", "<!-- verbatim pp.11-12 -->\n> Values sit on axes that run across "
                  "the page.\n<!-- /verbatim -->\n\n<!-- verbatim p.12 -->\n> A margin note on twelve.\n"
                  "<!-- /verbatim -->\n\n<!-- verbatim p.11 -->")
        code, statuses = self.check("--write-sizes")
        self.assertEqual(statuses["C1"], "PASS", self.output)
        self.edit(LEAF, "> A margin note on twelve.", "> A margin note on eleven. run across the page.")
        self.edit(LEAF, "<!-- verbatim p.12 -->", "<!-- verbatim pp.11-12 -->")
        self.assert_fails("C1")

    def test_uncited_paragraph_fails_c2(self) -> None:
        self.edit(LEAF, "the index of a table. [p.12]", "the index of a table.")
        self.assert_fails("C2")

    def test_citation_outside_file_range_fails_c2(self) -> None:
        self.edit(CARD, "two quantitative attributes. [p.11]", "two quantitative attributes. [p.10]")
        self.assert_fails("C2")

    def test_figure_caption_mismatch_fails_d1(self) -> None:
        self.edit(LEAF, f"[p.11]. {CAPTION}", "[p.11]. A different caption.")
        self.assert_fails("D1")

    def test_duplicate_printed_number_resolves_by_image_path(self) -> None:
        second = {"id": "fig-01-01b", "number": "1.1", "chapter": 1, "pdf_page": 12, "caption": "A second figure 1.1."}
        (self.provenance / "book.json").write_text(json.dumps(dict(BOOK, figures=BOOK["figures"] + [second])))
        (self.provenance / "figures.json").write_text(json.dumps(FIGURES + [dict(
            FIGURES[0], id="fig-01-01b", pdf_page=12, caption=second["caption"],
            file="assets/figures/fig-01-01b.png")]))
        (self.skill / "assets/figures/fig-01-01b.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\0" * 16)
        plan = json.loads(json.dumps(PLAN))
        plan["idiom_cards"][0]["figures"] = ["fig-01-01b"]
        plan["figure_homes"] = {"fig-01-01": [LEAF], "fig-01-01b": [CARD]}
        (self.provenance / "plan.json").write_text(json.dumps(plan))
        self.edit(CARD, "figures: [\"fig-01-01\"]", "figures: [\"fig-01-01b\"]")
        self.edit(CARD, f"fig-01-01.png) **Figure 1.1** [p.11]. {CAPTION}",
                  f"fig-01-01b.png) **Figure 1.1** [p.12]. {second['caption']}")
        code, statuses = self.check("--write-sizes")
        self.assertEqual((statuses["D1"], statuses["D5"]), ("PASS", "PASS"), self.output)
        self.edit(CARD, "fig-01-01b.png) **Figure 1.1** [p.12]", "fig-01-01b.png) **Figure 1.2** [p.12]")
        self.assert_fails("D1")

    def test_missing_figure_without_reason_fails_d4(self) -> None:
        (self.skill / "assets/figures/fig-01-01.png").unlink()
        self.assert_fails("D4")

    def test_citation_inside_hint_fails_e3(self) -> None:
        self.edit(CARD, "one point per item.", "one point per item. [p.11]")
        self.assert_fails("E3")

    def test_hint_marker_inside_verbatim_fails_e4(self) -> None:
        self.edit(LEAF, "> Arrange tables", "> [NOT FROM BOOK] Arrange tables")
        self.assert_fails("E4")

    def test_card_without_d3_hint_fails_e2(self) -> None:
        self.edit(CARD, "### D3", "### Vega")
        self.assert_fails("E2")

    def test_dead_anchor_fails_f2(self) -> None:
        self.edit(LEAF, "](../idioms/scatterplots.md)", "](../idioms/scatterplots.md#nowhere)")
        self.assert_fails("F2")

    def test_link_syntax_inside_code_is_not_a_link(self) -> None:
        self.edit(CARD, "Call `ax.scatter(x, y)` with one point per item.",
                  "Call `ax.scatter(x, y[a](b))` with one point per item.\n\n```python\nz = y[c](d)\n```")
        code, statuses = self.check("--write-sizes")
        self.assertEqual(statuses["F2"], "PASS", self.output)
        self.edit(CARD, "with one point per item.", "with one point per [item](nowhere.md).")
        self.assert_fails("F2")

    def test_empty_package_fails_without_crashing(self) -> None:
        shutil.rmtree(self.skill)
        shutil.rmtree(self.provenance)
        code, statuses = self.check()
        self.assertEqual(code, 1)
        self.assertEqual(len(statuses), 32)
        self.assertGreaterEqual(sum(s == "FAIL" for s in statuses.values()), 25, self.output)


if __name__ == "__main__":
    unittest.main()
