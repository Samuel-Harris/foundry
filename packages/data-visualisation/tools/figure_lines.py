"""Print the exact `## Figures` list line for figures, as seen from one file of the skill.

    python tools/figure_lines.py references/idioms/treemaps.md fig-09-08 fig-09-09
    python tools/figure_lines.py --file references/idioms/treemaps.md

Paths are relative to the skill directory. `--file` prints a line for every figure
plan.json homes in that file. Captions come verbatim from provenance/figures.json.
"""

from __future__ import annotations

import re

import argparse
import json
import posixpath
import sys

from extract import PACKAGE

PLAN_JSON = PACKAGE / "provenance" / "plan.json"
FIGURES_JSON = PACKAGE / "provenance" / "figures.json"


BARE_URL = re.compile(r"(?<![<(])(https?://[^\s<>()]*[^\s<>().,;:!?])")  # markdownlint MD034


def figure_line(path: str, figure: dict) -> str:
    image = posixpath.relpath(figure["file"], posixpath.dirname(path) or ".")
    label = f"Figure {figure['number']}"
    caption = BARE_URL.sub(r"<\1>", figure["caption"])
    return f"- ![{label}]({image}) **{label}** [p.{figure['pdf_page']}]. {caption}"


def homed_in(plan: dict, path: str) -> list[str]:
    return [fig for fig, homes in plan["figure_homes"].items() if path in homes]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--file", help="print every figure the plan homes in this file")
    parser.add_argument("args", nargs="*", metavar="PATH FIG-ID", help="a file path, then figure ids")
    args = parser.parse_args(argv)
    if args.file:
        if args.args:
            parser.error("--file takes no figure ids")
        path = args.file
        ids = homed_in(json.loads(PLAN_JSON.read_text(encoding="utf-8")), path)
    elif len(args.args) >= 2:
        path, ids = args.args[0], args.args[1:]
    else:
        parser.error("give a file path and at least one figure id, or --file PATH")

    figures = {f["id"]: f for f in json.loads(FIGURES_JSON.read_text(encoding="utf-8"))["figures"]}
    status = 0
    for fig_id in ids:
        figure = figures.get(fig_id)
        if figure is None:
            print(f"{fig_id}: not in figures.json", file=sys.stderr)
            status = 1
        elif not figure.get("file"):
            print(f"{fig_id}: no image ({figure.get('reason')}); it needs no figure line", file=sys.stderr)
        else:
            print(figure_line(path, figure))
    return status


if __name__ == "__main__":
    sys.exit(main())
