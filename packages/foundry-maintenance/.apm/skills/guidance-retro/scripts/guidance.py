#!/usr/bin/env python3
"""Inventory Foundry's guidance and route miner observations to the package that owns it.

Run from the root of a Foundry checkout.

    guidance.py inventory > RUN/inventory.md
        A Markdown table of every skill, agent and instruction: name, kind,
        package, source path and description. Miners tag observations with these
        names.

    guidance.py route RUN
        Validates every line of RUN/obs/t-<n>.jsonl and RUN/obs/r-<n>.jsonl
        (any other file there is a miner's scratch and is ignored) and splits the valid ones into
        RUN/routed/<package>.jsonl by the package that owns the named guidance,
        or RUN/routed/_unowned.jsonl when no guidance is named or the name is
        unknown. Writes RUN/routed/summary.json with the counts, every
        rejected line and every slice in the collectors' summaries that has no
        RUN/obs/t-<n>.jsonl or RUN/obs/r-<n>.jsonl, so a lost miner is rerun.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PRIMITIVE_GLOBS = (
    ("skill", "packages/*/.apm/skills/*/SKILL.md"),
    ("agent", "packages/*/.apm/agents/*.agent.md"),
    ("instruction", "packages/*/.apm/instructions/*.instructions.md"),
)
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
OBSERVATION_KINDS = {"defect", "friction", "gap", "override", "unprompted"}
OBSERVATION_SOURCES = {"transcript", "review"}
UNOWNED = "_unowned"
MINED_DIGESTS = (("t", "transcripts"), ("r", "reviews"))
MINER_OUTPUT = re.compile(r"[tr]-\d+\.jsonl")


@dataclass(frozen=True)
class Primitive:
    name: str
    kind: str
    package: str
    path: str
    description: str


def frontmatter_field(text: str, key: str) -> str | None:
    match = FRONTMATTER.match(text)
    if not match:
        return None
    lines = match.group(1).splitlines()
    for index, line in enumerate(lines):
        if not line.startswith(f"{key}:"):
            continue
        value = line.split(":", 1)[1].strip()
        if value[:1] in (">", "|"):
            block = []
            for continuation in lines[index + 1 :]:
                if continuation and not continuation[0].isspace():
                    break
                block.append(continuation.strip())
            return " ".join(part for part in block if part)
        return value.strip("\"'")
    return None


def primitive_name(kind: str, path: Path) -> str:
    if kind == "skill":
        return path.parent.name
    return path.name.removesuffix(".agent.md").removesuffix(".instructions.md")


def inventory(root: Path) -> list[Primitive]:
    primitives = []
    for kind, pattern in PRIMITIVE_GLOBS:
        for path in sorted(root.glob(pattern)):
            text = path.read_text(encoding="utf-8")
            relative = path.relative_to(root)
            primitives.append(
                Primitive(
                    name=frontmatter_field(text, "name") or primitive_name(kind, path),
                    kind=kind,
                    package=relative.parts[1],
                    path=str(relative),
                    description=frontmatter_field(text, "description") or "",
                )
            )
    return primitives


def render_inventory(primitives: list[Primitive]) -> str:
    rows = ["| Name | Kind | Package | Path | Description |", "| --- | --- | --- | --- | --- |"]
    for item in primitives:
        description = item.description.replace("|", "/")
        if len(description) > 200:
            description = description[:200] + "…"
        rows.append(f"| `{item.name}` | {item.kind} | `{item.package}` | `{item.path}` | {description} |")
    return "\n".join(rows) + "\n"


def observation_error(raw: Any) -> str | None:
    if not isinstance(raw, dict):
        return "not a JSON object"
    for key in ("pattern", "quote"):
        if not isinstance(raw.get(key), str) or not raw[key].strip():
            return f"{key}: expected a non-empty string"
    ref = raw.get("ref")
    if not (isinstance(ref, int) and not isinstance(ref, bool)) and not (isinstance(ref, str) and ref.strip()):
        return "ref: expected a session id or a PR ref"
    if raw.get("kind") not in OBSERVATION_KINDS:
        return f"kind: expected one of {sorted(OBSERVATION_KINDS)}"
    if raw.get("source") not in OBSERVATION_SOURCES:
        return f"source: expected one of {sorted(OBSERVATION_SOURCES)}"
    if raw.get("guidance") is not None and not isinstance(raw["guidance"], str):
        return "guidance: expected a string or null"
    return None


def missing_slices(run: Path) -> list[str]:
    missing = []
    for prefix, collector in MINED_DIGESTS:
        slices = json.loads((run / collector / "summary.json").read_text(encoding="utf-8"))["slices"]
        missing += [f"{prefix}-{index}" for index in range(len(slices)) if not (run / "obs" / f"{prefix}-{index}.jsonl").is_file()]
    return missing


def route(root: Path, run: Path) -> dict[str, Any]:
    owners = {item.name: item.package for item in inventory(root)}
    routed: dict[str, list[str]] = {}
    rejected: list[dict[str, str]] = []
    unknown_guidance: set[str] = set()
    for path in sorted(path for path in (run / "obs").glob("*.jsonl") if MINER_OUTPUT.fullmatch(path.name)):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            where = f"{path.name}:{number}"
            try:
                raw = json.loads(line)
            except json.JSONDecodeError as error:
                rejected.append({"line": where, "reason": f"invalid JSON: {error.msg}"})
                continue
            error = observation_error(raw)
            if error:
                rejected.append({"line": where, "reason": error})
                continue
            guidance = raw.get("guidance")
            if guidance and guidance not in owners:
                unknown_guidance.add(guidance)
            package = owners.get(guidance or "", UNOWNED)
            routed.setdefault(package, []).append(json.dumps(raw))

    out = run / "routed"
    out.mkdir(exist_ok=True)
    for stale in out.glob("*.jsonl"):
        stale.unlink()
    for package, lines in routed.items():
        (out / f"{package}.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
    summary = {
        "observations": {package: len(lines) for package, lines in sorted(routed.items())},
        "unknown_guidance": sorted(unknown_guidance),
        "rejected": rejected,
        "missing_slices": missing_slices(run),
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def require_foundry(root: Path) -> None:
    manifest = root / "apm.yml"
    if not manifest.is_file() or not re.search(r"^name: foundry$", manifest.read_text(encoding="utf-8"), re.MULTILINE):
        raise SystemExit(f"{root}: not the root of a Foundry checkout (apm.yml with `name: foundry`)")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("inventory")
    route_parser = commands.add_parser("route")
    route_parser.add_argument("run", type=Path)
    args = parser.parse_args(argv)
    root = Path.cwd()
    require_foundry(root)
    if args.command == "inventory":
        sys.stdout.write(render_inventory(inventory(root)))
    else:
        summary = route(root, args.run)
        print(json.dumps({**summary, "rejected": len(summary["rejected"])}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
