#!/usr/bin/env python3
"""Render a guidance-retro run as an HTML page or a Cursor canvas.

Run from the root of the Foundry checkout the candidates name paths in. Reads
RUN/transcripts/summary.json, RUN/reviews/summary.json, RUN/routed/summary.json
and every RUN/candidates/*.json (each a JSON list of candidates), applies the
evidence bar, groups the result by package and file, and writes the page to
stdout.

    build_report.py RUN --format html   > RUN/report.html
    build_report.py RUN --format canvas > RUN/report.canvas.tsx

Evidence bar:
    add                    3 distinct sources (sessions plus PRs), else watching
    update, delete         one static item or 3 distinct sources, else watching
    delete, judgement      recommended, labelled as judgement
    delete, silence        always listed under "possibly obsolete"
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any

from guidance import require_foundry

TEMPLATES = Path(__file__).resolve().parent.parent / "references"
TEMPLATE_FILES = {"html": "report.html", "canvas": "report.canvas.tsx"}
REPORT_TOKEN = "__REPORT_JSON__"
TITLE_TOKEN = "__TITLE__"
MIN_SOURCES = 3
HOST_PREFIX = re.compile(r"^(claude-code|cursor)-")

ACTIONS = ("add", "update", "delete")
BASES = ("evidence", "judgement", "silence")
EVIDENCE_SOURCES = ("transcript", "review", "static")


class Invalid(SystemExit):
    def __init__(self, field: str, problem: str) -> None:
        super().__init__(f"{field}: {problem}")


def text(raw: dict[str, Any], key: str, field: str, optional: bool = False) -> str | None:
    value = raw.get(key)
    if value is None and optional:
        return None
    if not isinstance(value, str) or not value.strip():
        raise Invalid(f"{field}.{key}", "expected a non-empty string")
    return value


def choice(raw: dict[str, Any], key: str, allowed: tuple[str, ...], field: str) -> str:
    value = raw.get(key)
    if value not in allowed:
        raise Invalid(f"{field}.{key}", f"expected one of {', '.join(allowed)}, got {value!r}")
    return value


def reference(raw: dict[str, Any], field: str) -> str:
    """A session id, a PR number (string or integer) or, for static evidence, a file path."""
    value = raw.get("ref")
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    return text(raw, "ref", field)


def https_url(value: str | None) -> str | None:
    """Keep only https links: the page turns them into clickable hrefs."""
    return value if value and value.startswith("https://") else None


@dataclass(frozen=True)
class Evidence:
    source: str
    ref: str
    url: str | None
    quote: str

    @classmethod
    def parse(cls, raw: Any, field: str) -> Evidence:
        if not isinstance(raw, dict):
            raise Invalid(field, "expected an object")
        return cls(
            source=choice(raw, "source", EVIDENCE_SOURCES, field),
            ref=reference(raw, field),
            url=https_url(text(raw, "url", field, optional=True)),
            quote=text(raw, "quote", field),
        )


@dataclass(frozen=True)
class Candidate:
    title: str
    action: str
    basis: str
    path: str
    package: str
    section: str | None
    change: str
    rationale: str
    evidence: tuple[Evidence, ...]

    @classmethod
    def parse(cls, raw: Any, field: str, root: Path) -> Candidate:
        if not isinstance(raw, dict):
            raise Invalid(field, "expected an object")
        action = choice(raw, "action", ACTIONS, field)
        basis = choice(raw, "basis", BASES, field)
        if action != "delete" and basis != "evidence":
            raise Invalid(f"{field}.basis", f"an {action} must rest on evidence, got {basis!r}")
        path = text(raw, "path", field)
        parts = Path(path).parts
        if len(parts) < 3 or parts[0] != "packages" or ".." in parts or not (root / "packages" / parts[1]).is_dir():
            raise Invalid(f"{field}.path", f"{path!r} is not inside an existing packages/<name>/ directory")
        if action != "add" and not (root / path).exists():
            raise Invalid(f"{field}.path", f"{path!r} does not exist, so it cannot be updated or deleted")
        evidence = raw.get("evidence", [])
        if not isinstance(evidence, list):
            raise Invalid(f"{field}.evidence", "expected a list")
        return cls(
            title=text(raw, "title", field),
            action=action,
            basis=basis,
            path=path,
            package=parts[1],
            section=text(raw, "section", field, optional=True),
            change=text(raw, "change", field),
            rationale=text(raw, "rationale", field),
            evidence=tuple(Evidence.parse(item, f"{field}.evidence[{index}]") for index, item in enumerate(evidence)),
        )

    @property
    def distinct_sources(self) -> int:
        return len({(item.source, item.ref) for item in self.evidence if item.source != "static"})

    @property
    def has_static(self) -> bool:
        return any(item.source == "static" for item in self.evidence)


@dataclass(frozen=True)
class Digests:
    """The sessions and PRs the collectors wrote, so evidence can cite only what was read."""

    sessions: frozenset[str]
    prs: frozenset[str]

    @classmethod
    def read(cls, run: Path) -> Digests:
        return cls(
            sessions=frozenset(HOST_PREFIX.sub("", path.stem) for path in (run / "transcripts" / "sessions").glob("*.md")),
            prs=frozenset(path.stem for path in (run / "reviews" / "prs").glob("*.md")),
        )

    def canonical(self, item: Evidence) -> Evidence | None:
        """Return the evidence with its ref in canonical form, or None when it cites nothing that was read."""
        if item.source == "static":
            return item
        if item.source == "review":
            number = re.sub(r"\D", "", item.ref)
            return replace(item, ref=number) if number in self.prs else None
        if item.ref in self.sessions:
            return item
        matches = [session for session in self.sessions if len(item.ref) >= 8 and session.startswith(item.ref)]
        return replace(item, ref=matches[0]) if len(matches) == 1 else None


def placement(candidate: Candidate) -> tuple[str, str | None]:
    """Return the report section a candidate belongs in, and why it fell short of the bar if it did."""
    if candidate.basis == "silence":
        return "obsolete", None
    if candidate.basis == "judgement":
        return "recommendations", None
    if candidate.action != "add" and candidate.has_static:
        return "recommendations", None
    if candidate.distinct_sources >= MIN_SOURCES:
        return "recommendations", None
    return "watching", f"{candidate.distinct_sources} of {MIN_SOURCES} distinct sources"


def group(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    packages: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for entry in entries:
        packages.setdefault(entry["package"], {}).setdefault(entry["path"], []).append(entry)
    groups = []
    for package in sorted(packages):
        files = [
            {"path": path, "items": sorted(items, key=lambda item: (-item["sources"], item["title"]))}
            for path, items in sorted(packages[package].items())
        ]
        groups.append({"package": package, "files": files})
    return groups


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise SystemExit(f"{path}: missing; run the step that writes it first") from error
    except json.JSONDecodeError as error:
        raise SystemExit(f"{path}: invalid JSON: {error}") from error


def foundry_commit(root: Path) -> str:
    result = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=root, capture_output=True, text=True, check=False)
    return result.stdout.strip() or "unknown"


def coverage_notes(transcripts: dict[str, Any], reviews: dict[str, Any], routed: dict[str, Any], unmatched: int) -> list[str]:
    notes = []
    if unmatched:
        notes.append(f"{unmatched} evidence items cited a session or PR no collector read, and were dropped.")
    if reviews["truncated_pull_requests"]:
        numbers = ", ".join(f"#{number}" for number in reviews["truncated_pull_requests"])
        notes.append(f"Comments on {numbers} were cut at GitHub's per-page limit.")
    if transcripts["unreadable_lines"]:
        notes.append(f"{transcripts['unreadable_lines']} transcript lines could not be parsed and were skipped.")
    if routed["rejected"]:
        notes.append(f"{len(routed['rejected'])} miner observations were malformed and dropped.")
    if routed["unknown_guidance"]:
        notes.append(f"Miners named guidance Foundry does not have: {', '.join(routed['unknown_guidance'])}.")
    return notes


def build_report(run: Path, root: Path) -> dict[str, Any]:
    transcripts = read_json(run / "transcripts" / "summary.json")
    reviews = read_json(run / "reviews" / "summary.json")
    routed = read_json(run / "routed" / "summary.json")
    sections: dict[str, list[dict[str, Any]]] = {"recommendations": [], "obsolete": [], "watching": []}
    digests = Digests.read(run)
    unmatched = 0
    for path in sorted((run / "candidates").glob("*.json")):
        raw = read_json(path)
        if not isinstance(raw, list):
            raise Invalid(path.name, "expected a JSON list of candidates")
        for index, item in enumerate(raw):
            candidate = Candidate.parse(item, f"{path.name}[{index}]", root)
            cited = [digests.canonical(evidence) for evidence in candidate.evidence]
            unmatched += cited.count(None)
            candidate = replace(candidate, evidence=tuple(evidence for evidence in cited if evidence))
            section, shortfall = placement(candidate)
            entry = {**asdict(candidate), "sources": candidate.distinct_sources}
            if shortfall:
                entry["shortfall"] = shortfall
            sections[section].append(entry)

    recommended = sections["recommendations"]
    return {
        "repo": reviews["repo"],
        "window": transcripts["window"],
        "foundry_commit": foundry_commit(root),
        "min_sources": MIN_SOURCES,
        "sources": {
            "pull_requests": reviews["pull_requests_with_comments"],
            "review_comments": reviews["comments"],
            "sessions": transcripts["sessions"],
            "sessions_by_host": transcripts["by_host"],
            "sessions_per_model": transcripts["sessions_per_model"],
        },
        "counts": {action: sum(1 for entry in recommended if entry["action"] == action) for action in ACTIONS},
        "coverage": coverage_notes(transcripts, reviews, routed, unmatched),
        "recommendations": group(recommended),
        "obsolete": group(sections["obsolete"]),
        "watching": group(sections["watching"]),
    }


def render(report: dict[str, Any], page_format: str) -> str:
    template_path = TEMPLATES / TEMPLATE_FILES[page_format]
    template = template_path.read_text(encoding="utf-8")
    if template.count(REPORT_TOKEN) != 1:
        raise SystemExit(f"{template_path}: expected {REPORT_TOKEN} exactly once")
    payload = json.dumps(report, indent=2)
    if page_format == "html":
        payload = payload.replace("<", "\\u003c")
    title = f"{report['repo'].split('/')[-1]} guidance retro"
    return template.replace(TITLE_TOKEN, title).replace(REPORT_TOKEN, payload)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("run", type=Path)
    parser.add_argument("--format", choices=sorted(TEMPLATE_FILES), required=True)
    args = parser.parse_args(argv)
    require_foundry(Path.cwd())
    sys.stdout.write(render(build_report(args.run, Path.cwd()), args.format))
    return 0


if __name__ == "__main__":
    sys.exit(main())
