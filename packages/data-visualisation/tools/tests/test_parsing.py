"""Behaviour of the pure parsing functions in tools/extract.py, tools/figures.py and tools/plan.py."""

from __future__ import annotations

import sys
import unittest
from unittest import mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from extract import (  # noqa: E402
    Line,
    compose_page_text,
    dehyphenate_lines,
    extract_idiom_boxes,
    join_toc_rows,
    page_map_for,
    parse_idiom_box,
    parse_toc_row,
    pdf_to_printed,
    printed_to_pdf,
    resolve_section_refs,
)
from check import AUTOLINK, FIGURE_ITEM  # noqa: E402
from figure_lines import figure_line  # noqa: E402
from figures import Box, figure_region, page_blocks, page_graphics, single_raster  # noqa: E402
from plan import build_plan, match_toc_idioms  # noqa: E402


class PageMapTest(unittest.TestCase):
    def setUp(self) -> None:
        self.page_map = page_map_for(422)

    def test_body_pages_are_printed_plus_25(self) -> None:
        self.assertEqual(printed_to_pdf(self.page_map, 1), 26)
        self.assertEqual(printed_to_pdf(self.page_map, 147), 172)
        self.assertEqual(pdf_to_printed(self.page_map, 172), 147)

    def test_front_matter_is_printed_plus_1(self) -> None:
        self.assertEqual(printed_to_pdf(self.page_map, 5, "roman"), 6)
        self.assertEqual(pdf_to_printed(self.page_map, 6), 5)

    def test_page_outside_the_book_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            printed_to_pdf(self.page_map, 500)
        with self.assertRaises(ValueError):
            pdf_to_printed(self.page_map, 423)


class TocRowTest(unittest.TestCase):
    def test_levels_follow_number_depth(self) -> None:
        cases = {
            "7 Arrange Tables 144": ("chapter", "ch07", "Arrange Tables", 144),
            "7.5 Separate, Order, and Align: Categorical Regions 149": (
                "section", "s07.05", "Separate, Order, and Align: Categorical Regions", 149),
            "7.5.1 List Alignment: One Key 149": ("subsection", "s07.05.01", "List Alignment: One Key", 149),
            "2.4.3.1 Spatial Fields 28": ("subsubsection", "s02.04.03.01", "Spatial Fields", 28),
        }
        for row, (level, ident, title, page) in cases.items():
            entry = parse_toc_row(row)
            self.assertEqual((entry["level"], entry["id"], entry["title"], entry["printed_page"]),
                             (level, ident, title, page), row)

    def test_example_rows_are_named_idioms(self) -> None:
        entry = parse_toc_row("Example: Dot and Line Charts 155")
        self.assertEqual((entry["level"], entry["id"], entry["number"]), ("idiom", "idiom:dot-and-line-charts", None))

    def test_unnumbered_rows_are_not_chapter_content(self) -> None:
        self.assertIsNone(parse_toc_row("Figure Credits 369"))
        self.assertIsNone(parse_toc_row("Why a New Book? xv"))

    def test_wrapped_title_joins_the_row_carrying_the_page(self) -> None:
        rows = ["12.3.2 Share Data: All, Subset,", "None 276", "12.4 Partition into Views 284"]
        self.assertEqual(join_toc_rows(rows), ["12.3.2 Share Data: All, Subset, None 276", "12.4 Partition into Views 284"])


def line(x0: float, y0: float, text: str) -> Line:
    return Line(x0, y0, x0 + 6 * len(text), y0 + 11, text, "NimbusSanL-Regu", 9.0)


class IdiomBoxTest(unittest.TestCase):
    def test_fields_keep_line_breaks_and_merge_one_baseline(self) -> None:
        lines = [
            line(49, 101, "What: Data"), line(154, 99, "Table: one quantitative value attribute, one categori-"),
            line(154, 110, "cal key attribute."),
            line(49, 124, "How: Encode"), line(154, 122, "Heatmap:"), line(210, 122.5, "2D matrix alignment."),
            line(49, 171, "Scale"), line(154, 169, "Key attribute: dozens to hundreds of levels."),
        ]
        fields = parse_idiom_box(lines, divider_x=148, rules=[100, 123, 170, 183])
        self.assertEqual(fields, [
            ("What: Data", "Table: one quantitative value attribute, one categori-\ncal key attribute."),
            ("How: Encode", "Heatmap: 2D matrix alignment."),
            ("Scale", "Key attribute: dozens to hundreds of levels."),
        ])


class SplitIdiomBoxTest(unittest.TestCase):
    """A box that runs off the bottom of one page and continues at the top of the next."""

    def setUp(self) -> None:
        import pymupdf

        self.doc = pymupdf.open()
        first = self.doc.new_page(width=540, height=648)
        first.insert_text((181, 520), "Idiom")
        first.insert_text((286, 520), "SolarPlot", fontname="hebo")
        rows = [(530, 555, "What: Data", ["Table: one quantitative attribute."]),
                (555, 590, "What: Derived", ["Derived table: one derived key", "(bin), one value (item"])]
        first.draw_line((280, 510), (280, 530))
        for top, bottom, label, values in rows:
            first.draw_line((175, top), (498, top))
            first.draw_line((280, top), (280, bottom))
            first.insert_text((181, top + 10), label)
            for i, value in enumerate(values):
                first.insert_text((286, top + 10 + 11 * i), value)
        second = self.doc.new_page(width=540, height=648)
        second.insert_text((43, 150), "Figure 13.8. A figure caption above the continued box.")
        rows = [(250, 273, "", ["count per bin)."]), (273, 296, "How: Encode", ["Radial layout, line marks."])]
        for top, bottom, label, values in rows:
            second.draw_line((148, top), (148, bottom))
            if top != 250:
                second.draw_line((43, top), (367, top))
                second.insert_text((49, top + 10), label)
            second.insert_text((154, top + 10), values[0])
        second.insert_text((43, 330), "Body text resumes after the box.")

    def test_fields_continue_onto_the_next_page(self) -> None:
        boxes = extract_idiom_boxes(self.doc, lambda pdf, y: None, 1, 2)
        self.assertEqual(len(boxes), 1)
        self.assertEqual(boxes[0]["fields"], {
            "What: Data": "Table: one quantitative attribute.",
            "What: Derived": "Derived table: one derived key\n(bin), one value (item\ncount per bin).",
            "How: Encode": "Radial layout, line marks.",
        })


class CrossrefTest(unittest.TestCase):
    known = {"s09.03", "s13.04.01", "s01.14", "s03.07", "s12.03", "s12.04"}

    def resolved(self, text: str) -> list[tuple[str, str | None]]:
        return [(number, target) for _, number, target in resolve_section_refs(text, self.known)]

    def test_hyphenated_reference_resolves(self) -> None:
        self.assertEqual(self.resolved("is covered in Sec-\ntion 9.3."), [("9.3", "s09.03")])

    def test_every_number_in_a_list_resolves(self) -> None:
        self.assertEqual(self.resolved("discussed in Sections 12.3 and 12.4."), [("12.3", "s12.03"), ("12.4", "s12.04")])
        self.assertEqual(self.resolved("Section 1.14 and 3.7."), [("1.14", "s01.14"), ("3.7", "s03.07")])

    def test_unknown_section_is_kept_unresolved(self) -> None:
        self.assertEqual(self.resolved("see Section 13.4.1 and Section 20.1"), [("13.4.1", "s13.04.01"), ("20.1", None)])

    def test_chapter_references_are_not_section_references(self) -> None:
        self.assertEqual(self.resolved("Chapter 7 covers this."), [])


class PageTextTest(unittest.TestCase):
    def test_margin_note_follows_the_body_and_heads_are_dropped(self) -> None:
        lines = [
            (43, 38, 58, 49, "148"),
            (175, 100, 497, 111, "Figure 7.8(a) shows a dot chart of cat"),
            (43, 104, 95, 115, "The terms dot"),
            (100, 104, 160, 115, "chart"),
            (175, 111, 497, 122, "weight over time."),
            (260, 613, 270, 624, "149"),
        ]
        self.assertEqual(compose_page_text(lines, margin_left=True),
                         "Figure 7.8(a) shows a dot chart of cat\nweight over time.\n\nThe terms dot chart\n")


class DehyphenateTest(unittest.TestCase):
    def test_soft_hyphen_is_dropped_only_for_words_the_book_writes_whole(self) -> None:
        vocabulary = {"expectancy"}
        self.assertEqual(dehyphenate_lines(["life ex-", "pectancy and"], vocabulary), "life expectancy and")
        self.assertEqual(dehyphenate_lines(["higher-", "frequency structure"], vocabulary), "higher-frequency structure")


class IdiomMatchTest(unittest.TestCase):
    def test_exact_slug_wins_then_word_subset_takes_an_unclaimed_box(self) -> None:
        toc = [
            {"id": "idiom:bar-charts", "pdf_start": 175, "pdf_end": 176},
            {"id": "idiom:stacked-bar-charts", "pdf_start": 176, "pdf_end": 178},
            {"id": "idiom:dot-and-line-charts", "pdf_start": 180, "pdf_end": 182},
            {"id": "idiom:choropleth-maps", "pdf_start": 206, "pdf_end": 206},
            {"id": "idiom:lineup", "pdf_start": 271, "pdf_end": 273},
        ]
        boxes = [
            {"slug": "bar-charts", "pdf_page": 176}, {"slug": "stacked-bar-charts", "pdf_page": 178},
            {"slug": "dot-charts", "pdf_page": 180}, {"slug": "line-charts", "pdf_page": 181},
            {"slug": "choropleth-map", "pdf_page": 206},
        ]
        matched = {t: b["slug"] for t, b in match_toc_idioms(toc, boxes).items()}
        self.assertEqual(matched, {
            "idiom:bar-charts": "bar-charts",
            "idiom:stacked-bar-charts": "stacked-bar-charts",
            "idiom:dot-and-line-charts": "dot-charts",
            "idiom:choropleth-maps": "choropleth-map",
        })


def toc_entry(ident: str, level: str, number: str | None, title: str, parent: str | None, pages: tuple[int, int]) -> dict:
    return {"id": ident, "level": level, "number": number, "title": title, "parent": parent,
            "pdf_start": pages[0], "pdf_end": pages[1]}


def figure(n: int, page: int, caption: str) -> dict:
    return {"id": f"fig-01-{n:02d}", "number": f"1.{n}", "chapter": 1, "pdf_page": page, "caption": caption}


# Chapter 1 opens on p.10 with an overview figure; 1.2 and 1.3 share p.13.
PLAN_BOOK = {
    "toc": [
        toc_entry("ch01", "chapter", "1", "Arrange Things", None, (10, 14)),
        toc_entry("s01.01", "section", "1.1", "The Big Picture", "ch01", (11, 11)),
        toc_entry("s01.02", "section", "1.2", "Connection: Link Marks", "ch01", (11, 13)),
        toc_entry("idiom:sfdp", "idiom", None, "SFDP", "s01.02", (12, 12)),
        toc_entry("s01.03", "section", "1.3", "Containment: Hierarchy Marks", "ch01", (13, 14)),
    ],
    "idiom_boxes": [{"slug": "multilevel-sfdp", "name": "Multilevel SFDP", "chapter": 1, "section": "s01.02",
                     "pdf_page": 12, "fields": {}}],
    "figures": [figure(1, 10, "Design choices."), figure(2, 13, "Treemap with containment, unlike Figure 1.3."),
                figure(3, 12, "A small network."), figure(4, 14, "A nested layout.")],
    "crossrefs": [],
}
PLAN_PAGES = {
    10: "Arrange Things\nFigure 1.1. Design choices.\n",
    11: "1.1 The Big Picture\nSummarised in Figure 1.1.\n1.2 Connection: Link Marks\nLinks connect nodes.\n",
    12: "Example: SFDP\nA multilevel layout.\nFigure 1.3. A small network.\n",
    13: "Connection ends with Figure 1.3, and Fig-\nure 1.4 nests it.\n1.3 Containment: Hierarchy Marks\nFigure 1.2 is a treemap of the tree.\n"
        "Figure 1.2. Treemap with con-\ntainment, unlike Figure 1.3.\n",
    14: "More containment, misprinted as Figure 1.3.\nFigure 1.4. A nested layout.\n",
}


class PlanTest(unittest.TestCase):
    def setUp(self) -> None:
        with mock.patch("plan.A4_CARDS", ()), \
                mock.patch("plan.CARD_FIGURES", {"idiom:multilevel-sfdp": ("fig-01-03",)}), \
                mock.patch("plan.MISNUMBERED_MENTIONS", {(14, "1.3"): "fig-01-04"}):
            self.plan = build_plan(PLAN_BOOK, read_page=PLAN_PAGES.__getitem__)
        self.leaf = {f["id"]: f for f in self.plan["files"]}
        self.card = self.plan["idiom_cards"][0]["path"]

    def homes(self, fig_id: str) -> list[str]:
        return self.plan["figure_homes"][fig_id]

    def test_toc_idiom_on_a_card_with_another_id_maps_to_its_anchor(self) -> None:
        self.assertEqual(self.plan["entries"]["idiom:sfdp"], f"{self.card}#idiom:sfdp")

    def test_figure_is_homed_where_the_text_mentions_it_not_on_a_shared_page(self) -> None:
        self.assertEqual(self.homes("fig-01-02"), [self.leaf["s01.03"]["path"]])

    def test_page_splits_at_the_heading_and_captions_are_not_mentions(self) -> None:
        self.assertEqual(self.homes("fig-01-03"), [self.leaf["s01.02"]["path"], self.card])

    def test_mention_split_by_line_end_hyphen_still_homes_the_figure(self) -> None:
        self.assertIn(self.leaf["s01.02"]["path"], self.homes("fig-01-04"))

    def test_misnumbered_mention_homes_the_figure_the_text_means(self) -> None:
        self.assertEqual(self.homes("fig-01-04"), [self.leaf["s01.02"]["path"], self.leaf["s01.03"]["path"]])

    def test_card_figures_come_from_the_table_and_must_cover_every_card(self) -> None:
        self.assertEqual(self.plan["idiom_cards"][0]["figures"], ["fig-01-03"])
        with mock.patch("plan.A4_CARDS", ()), mock.patch("plan.CARD_FIGURES", {}):
            with self.assertRaises(ValueError):
                build_plan(PLAN_BOOK, read_page=PLAN_PAGES.__getitem__)

    def test_opening_overview_figure_goes_to_the_big_picture_leaf_and_widens_its_pages(self) -> None:
        self.assertEqual(self.homes("fig-01-01"), [self.leaf["s01.01"]["path"]])
        self.assertEqual(self.leaf["s01.01"]["pdf_pages"], [10, 11])


class FigureLineTest(unittest.TestCase):
    fig = {"id": "fig-09-08", "number": "9.8", "pdf_page": 238, "file": "assets/figures/fig-09-08.png",
           "caption": "Treemap layout, in contrast to the node–link diagrams in Figure 9.3."}

    def test_line_passes_the_checker_and_points_at_the_image_from_any_depth(self) -> None:
        for path, image in (("references/idioms/treemaps.md", "../../assets/figures/fig-09-08.png"),
                            ("references/ch07-a/s07-05-b/s07-05-01-c.md", "../../../assets/figures/fig-09-08.png")):
            match = FIGURE_ITEM.match(figure_line(path, self.fig)[2:])
            self.assertIsNotNone(match, path)
            self.assertEqual((match.group("target"), match.group("n1"), match.group("page"), match.group("caption")),
                             (image, "9.8", "238", self.fig["caption"]))

    def test_bare_urls_are_wrapped_for_markdownlint_and_still_match_the_manifest(self) -> None:
        fig = dict(self.fig, caption="From http://www.example.org/tree. Panel (b) after [Smith 02].")
        caption = FIGURE_ITEM.match(figure_line("references/idioms/treemaps.md", fig)[2:]).group("caption")
        self.assertIn("<http://www.example.org/tree>.", caption)
        self.assertEqual(AUTOLINK.sub(r"\1", caption), fig["caption"])


class EmbeddedRasterTest(unittest.TestCase):
    """A figure is saved as its embedded raster only when nothing else is drawn in it."""

    raster = (60, 80, 360, 280)

    def method(self, under=lambda page: None, over=lambda page: None) -> str:
        import pymupdf

        page = pymupdf.open().new_page(width=540, height=648)
        under(page)
        pix = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 60, 40), 0)
        pix.clear_with(200)
        page.insert_image(pymupdf.Rect(*self.raster), pixmap=pix)
        over(page)
        labels = [l for block in page_blocks(page) for l in block]
        caption = Box(43, 300, 400, 311)
        region, inside = figure_region(caption, [caption], page_graphics(page, [], labels), Box(0, 0, 540, 648))
        return "embedded" if single_raster(region, inside) else "crop"

    def test_plain_raster_is_embedded(self) -> None:
        self.assertEqual(self.method(), "embedded")

    def test_backdrop_under_the_raster_keeps_it_embedded(self) -> None:
        self.assertEqual(self.method(under=lambda page: page.draw_rect(self.raster, color=None, fill=(1, 1, 1))),
                         "embedded")

    def test_text_drawn_on_the_raster_falls_back_to_a_crop(self) -> None:
        self.assertEqual(self.method(over=lambda page: page.insert_text((100, 150), "eye socket")), "crop")

    def test_arrow_drawn_on_the_raster_falls_back_to_a_crop(self) -> None:
        self.assertEqual(self.method(over=lambda page: page.draw_line((100, 150), (200, 200))), "crop")


if __name__ == "__main__":
    unittest.main()
