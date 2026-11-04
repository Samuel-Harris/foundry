"""Extract every figure in provenance/book.json to assets/figures/ and write provenance/figures.json.

Usage: uv run tools/figures.py --pdf PATH   (or set $VIS_PDF); run tools/extract.py first.

A figure sits above its caption, between the caption and the nearest text-flow line
above it. The crop is the union of the images, vector drawings and figure-label text in
that band. When one embedded raster covers the whole band and nothing else is drawn in it,
that raster is used instead.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path

from extract import BOOK_JSON, PACKAGE, RUNNING_HEADER_MAX_Y, Line, dump_json, find_captions, page_lines

FIGURES_DIR = PACKAGE / ".apm" / "skills" / "data-visualisation" / "assets" / "figures"
FIGURES_JSON = PACKAGE / "provenance" / "figures.json"

DPI = 150
MAX_EMBEDDED_DPI = 150
PAD = 3.0
PROSE_FONTS = ("URWBookmanL-Ligh", "NimbusSanL-Regu", "NimbusSanL-Bold", "MSAM10")
EMBEDDED_COVERAGE = 0.9
GROW_GAP = 30.0


@dataclass(frozen=True)
class Box:
    x0: float
    y0: float
    x1: float
    y1: float

    def union(self, other: Box) -> Box:
        return Box(min(self.x0, other.x0), min(self.y0, other.y0), max(self.x1, other.x1), max(self.y1, other.y1))

    @property
    def area(self) -> float:
        return max(0.0, self.x1 - self.x0) * max(0.0, self.y1 - self.y0)

    def x_overlaps(self, other: Box) -> bool:
        return self.x0 < other.x1 and other.x0 < self.x1


@dataclass(frozen=True)
class Graphic:
    box: Box
    kind: str  # "image" | "drawing" | "label"
    xref: int = 0


def is_prose_block(lines: list[Line]) -> bool:
    """Running text, sidenotes, headings and idiom boxes: the flow a figure sits between.
    Panel labels, typeset figure text and axis labels are not prose."""
    if not lines:
        return False
    first = lines[0]
    if first.y1 <= RUNNING_HEADER_MAX_Y + 2 or first.text.strip() == "This page intentionally left blank":
        return True
    if first.font.startswith("NimbusSanL") and (first.size >= 12 or first.text.startswith("Example:")):
        return True
    body = [l for l in lines if l.font.startswith(PROSE_FONTS) and l.size >= 9]
    if any(l.font.startswith("URWBookmanL-Ligh") and len(l.text.split()) >= 4 for l in body):
        return True
    return len(body) >= 2 and sum(len(l.text) for l in body) > 60 or any(len(l.text) > 45 for l in body)


def page_blocks(page) -> list[list[Line]]:
    blocks = []
    for block in page.get_text("dict")["blocks"]:
        lines = []
        for raw in block.get("lines", []):
            spans = raw["spans"]
            text = "".join(s["text"] for s in spans)
            if text.strip():
                lines.append(Line(*raw["bbox"], text, spans[0]["font"], round(spans[0]["size"], 1)))
        if lines:
            blocks.append(lines)
    return blocks


def bounds(lines: list[Line]) -> Box:
    return Box(min(l.x0 for l in lines), min(l.y0 for l in lines), max(l.x1 for l in lines), max(l.y1 for l in lines))


def near(a: Box, b: Box, gap: float) -> bool:
    return a.x0 < b.x1 + gap and b.x0 < a.x1 + gap and a.y0 < b.y1 + gap and b.y0 < a.y1 + gap


def figure_region(caption: Box, flow: list[Box], graphics: list[Graphic], page: Box) -> tuple[Box | None, list[Graphic]]:
    """The band above `caption` up to the nearest flow text, and the graphics inside it."""
    ceiling = max([b.y1 for b in flow if b.y1 <= caption.y0 + 1 and b.x_overlaps(caption)],
                  default=RUNNING_HEADER_MAX_Y)
    band = [g for g in graphics if g.box.y0 >= ceiling - 2 and g.box.y1 <= caption.y0 + 2]
    inside = [g for g in band if g.box.x_overlaps(caption)]
    if not inside:
        return None, []
    region = inside[0].box
    for g in inside[1:]:
        region = region.union(g.box)
    grown = True
    while grown:
        grown = False
        for g in band:
            if g not in inside and near(g.box, region, GROW_GAP):
                inside.append(g)
                region = region.union(g.box)
                grown = True
    region = Box(max(page.x0, region.x0 - PAD), max(ceiling, region.y0 - PAD),
                 min(page.x1, region.x1 + PAD), min(caption.y0 - 0.5, region.y1 + PAD))
    return region, inside


def page_graphics(page, prose: list[Box], labels: list[Line]) -> list[Graphic]:
    def over_text(b: Box) -> bool:
        return any(b.x_overlaps(f) and b.y0 < f.y1 and f.y0 < b.y1 for f in prose)

    out = []
    for info in page.get_image_info(xrefs=True):
        b = Box(*info["bbox"])
        if b.area < 4 or (b.y1 - b.y0 < 15 and over_text(b)):
            continue
        out.append(Graphic(b, "image", info["xref"]))
    for d in page.get_drawings():
        r = d["rect"]
        b = Box(r.x0, r.y0, r.x1, r.y1)
        if b.y1 <= RUNNING_HEADER_MAX_Y + 2 or over_text(b):
            continue
        out.append(Graphic(b, "drawing"))
    out += [Graphic(Box(l.x0, l.y0, l.x1, l.y1), "label") for l in labels]
    return out


def png_bytes(image) -> bytes:
    from PIL import Image

    image = image.convert("RGB")
    quantised = image.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    buf = io.BytesIO()
    quantised.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def render_crop(page, region: Box) -> bytes:
    import pymupdf
    from PIL import Image

    pix = page.get_pixmap(dpi=DPI, clip=pymupdf.Rect(region.x0, region.y0, region.x1, region.y1), alpha=False)
    return png_bytes(Image.frombytes("RGB", (pix.width, pix.height), pix.samples))


def embedded_image(doc, graphic: Graphic) -> tuple[bytes, int]:
    import pymupdf
    from PIL import Image

    pix = pymupdf.Pixmap(doc, graphic.xref)
    if pix.n - pix.alpha != 3:
        pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
    if pix.alpha:
        pix = pymupdf.Pixmap(pix, 0)
    image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    width_in = (graphic.box.x1 - graphic.box.x0) / 72
    max_px = round(width_in * MAX_EMBEDDED_DPI)
    if image.width > max_px:
        image = image.resize((max_px, round(image.height * max_px / image.width)), Image.Resampling.LANCZOS)
    return png_bytes(image), round(image.width / width_in)


def single_raster(region: Box, inside: list[Graphic]) -> Graphic | None:
    images = [g for g in inside if g.kind == "image"]
    if len(images) != 1 or images[0].xref == 0:
        return None
    image = images[0]
    # Labels and arrows drawn on top of the raster are not in its file. A box the raster's
    # own size is its backdrop or frame, as under Figure 6.3, and adds nothing.
    others = [g for g in inside if g is not image and not (
        abs(g.box.x0 - image.box.x0) <= 1 and abs(g.box.x1 - image.box.x1) <= 1
        and abs(g.box.y0 - image.box.y0) <= 1 and abs(g.box.y1 - image.box.y1) <= 1)]
    if others or image.box.area < EMBEDDED_COVERAGE * region.area:
        return None
    return image


def write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_bytes() == data:
        return
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_bytes(data)
    os.replace(tmp, path)


def extract_one(doc, fig: dict) -> dict:
    page = doc[fig["pdf_page"] - 1]
    lines = page_lines(page)
    chapter, n = (int(p) for p in fig["number"].split("."))
    captions = find_captions(lines, set())
    mine = [c for c in captions if (c[0], c[1]) == (chapter, n)]
    entry = {"id": fig["id"], "number": fig["number"], "pdf_page": fig["pdf_page"], "caption": fig["caption"],
             "file": None, "method": None, "dpi": None, "reason": None, "referenced_by": []}
    if len(mine) != 1:
        entry["reason"] = f"expected one caption for Figure {fig['number']} on the page, found {len(mine)}"
        return entry
    caption = Box(*mine[0][3])
    caption_boxes = [Box(*c[3]) for c in captions]
    prose, labels = [], []
    for block in page_blocks(page):
        b = bounds(block)
        in_caption = any(b.x0 >= c.x0 - 2 and b.x1 <= c.x1 + 2 and b.y0 >= c.y0 - 2 and b.y1 <= c.y1 + 2
                         for c in caption_boxes)
        if in_caption or is_prose_block(block):
            prose += [Box(l.x0, l.y0, l.x1, l.y1) for l in block]
        else:
            labels += block
    page_box = Box(page.rect.x0, page.rect.y0, page.rect.x1, page.rect.y1)
    region, inside = figure_region(caption, prose + caption_boxes, page_graphics(page, prose, labels), page_box)
    if region is None:
        entry["reason"] = "no image, drawing or figure label found between the caption and the text above it"
        return entry
    raster = single_raster(region, inside)
    if raster:
        data, entry["dpi"] = embedded_image(doc, raster)
        entry["method"] = "embedded"
    else:
        data = render_crop(page, region)
        entry["method"] = "crop"
        entry["dpi"] = DPI
    rel = f"assets/figures/{fig['id']}.png"
    write_bytes(FIGURES_DIR / f"{fig['id']}.png", data)
    entry["file"] = rel
    return entry


def main(argv: list[str] | None = None) -> int:
    import pymupdf

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pdf", default=os.environ.get("VIS_PDF"), required=os.environ.get("VIS_PDF") is None)
    args = ap.parse_args(argv)
    doc = pymupdf.open(args.pdf)
    book = json.loads(BOOK_JSON.read_text(encoding="utf-8"))
    entries = [extract_one(doc, fig) for fig in book["figures"]]

    previous = {}
    if FIGURES_JSON.exists():
        previous = {e["id"]: e.get("referenced_by", [])
                    for e in json.loads(FIGURES_JSON.read_text(encoding="utf-8")).get("figures", [])}
    for e in entries:
        e["referenced_by"] = previous.get(e["id"], [])
    wanted = {f"{e['id']}.png" for e in entries if e["file"]}
    for stale in FIGURES_DIR.glob("*.png"):
        if stale.name not in wanted:
            stale.unlink()
    dump_json(FIGURES_JSON, {"figures": entries})

    total = sum(p.stat().st_size for p in FIGURES_DIR.glob("*.png"))
    methods: dict[str, int] = {}
    for e in entries:
        methods[e["method"] or "failed"] = methods.get(e["method"] or "failed", 0) + 1
    print(f"figures {len(entries)} {methods}, {total / 1e6:.2f} MB", file=sys.stderr)
    for e in entries:
        if e["reason"]:
            print(f"  {e['id']}: {e['reason']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
