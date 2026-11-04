"""Run the code in idiom cards' implementation hints and report pass or fail per card.

    uv run tools/run_hints.py                                 # every idiom card
    uv run tools/run_hints.py references/idioms/treemaps.md   # paths relative to the skill

Each python block under `### matplotlib` runs in a fresh interpreter with
MPLBACKEND=Agg, inside a temporary directory, so nothing is written into the skill.
Each JavaScript block under `### D3` is syntax-checked as an ES module with
`node --check` when node is on PATH.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from extract import PACKAGE

SKILL = PACKAGE / ".apm" / "skills" / "data-visualisation"
HINTS_HEADING = re.compile(r"^## Implementation hints \[NOT FROM BOOK\]\s*$")
FENCE = re.compile(r"^```\s*([\w+-]*)\s*$")
LANGUAGES = {"matplotlib": ("python", "py"), "D3": ("js", "javascript")}
TIMEOUT = 60
TAIL_LINES = 6


def hint_blocks(text: str) -> dict[str, list[str]]:
    """`### matplotlib` python blocks and `### D3` JavaScript blocks inside the hints section."""
    blocks: dict[str, list[str]] = {name: [] for name in LANGUAGES}
    in_hints, library, fence, body = False, None, None, []
    for line in text.splitlines():
        if fence is not None:
            if line.strip() == "```":
                if library and fence in LANGUAGES[library]:
                    blocks[library].append("\n".join(body) + "\n")
                fence, body = None, []
            else:
                body.append(line)
        elif m := FENCE.match(line):
            fence = m.group(1).lower()
        elif line.startswith("## "):
            in_hints, library = bool(HINTS_HEADING.match(line)), None
        elif in_hints and line.startswith("### "):
            library = line[4:].strip() if line[4:].strip() in LANGUAGES else None
    return blocks


def tail(text: str) -> str:
    return "\n".join("    " + line for line in text.strip().splitlines()[-TAIL_LINES:])


def run(cmd: list[str], cwd: str, env: dict | None = None) -> str | None:
    """None on success, else the error tail."""
    try:
        done = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        return f"    timed out after {TIMEOUT}s"
    return None if done.returncode == 0 else tail(done.stderr or done.stdout) or f"    exit {done.returncode}"


def check_card(path: Path, node: str | None) -> list[tuple[str, str, str | None]]:
    """(library, PASS | FAIL | SKIP, detail) for each library of one card."""
    blocks = hint_blocks(path.read_text(encoding="utf-8"))
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        env = dict(os.environ, MPLBACKEND="Agg")
        if not blocks["matplotlib"]:
            results.append(("matplotlib", "FAIL", "    no python block under ### matplotlib"))
        for i, code in enumerate(blocks["matplotlib"]):
            script = Path(tmp) / f"hint{i}.py"
            script.write_text(code, encoding="utf-8")
            error = run([sys.executable, "-I", script.name], tmp, env)
            results.append(("matplotlib", "FAIL" if error else "PASS", error))
        if not blocks["D3"]:
            results.append(("D3", "SKIP", "    no JavaScript block"))
        elif node is None:
            results.append(("D3", "SKIP", "    node not on PATH"))
        for i, code in enumerate(blocks["D3"] if node else []):
            module = Path(tmp) / f"hint{i}.mjs"
            module.write_text(code, encoding="utf-8")
            error = run([node, "--check", module.name], tmp)
            results.append(("D3", "FAIL" if error else "PASS", error))
    return results


def resolve(arg: str) -> Path:
    return SKILL / arg if (SKILL / arg).is_file() else Path(arg).resolve()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("paths", nargs="*", help="idiom cards, relative to the skill directory")
    args = parser.parse_args(argv)
    cards = [resolve(p) for p in args.paths] or sorted((SKILL / "references" / "idioms").glob("*.md"))
    node = shutil.which("node")

    failed = 0
    for card in cards:
        label = card.relative_to(SKILL) if card.resolve().is_relative_to(SKILL.resolve()) else card
        for library, status, detail in check_card(card, node):
            print(f"{status} {label} {library}")
            if detail and status != "PASS":
                print(detail)
            failed += status == "FAIL"
    print(f"\n{len(cards)} cards, {failed} failing hint blocks")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
