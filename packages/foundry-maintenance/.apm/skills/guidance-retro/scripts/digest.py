"""Helpers shared by the two collectors: window parsing, truncation and slicing."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path


@dataclass(frozen=True)
class Window:
    start: datetime
    end: datetime

    @classmethod
    def parse(cls, since: str, until: str | None) -> Window:
        start = parse_day(since)
        end = parse_day(until) if until else datetime.now(timezone.utc)
        if end <= start:
            raise SystemExit(f"window: --until ({end:%Y-%m-%d}) must be after --since ({start:%Y-%m-%d})")
        return cls(start, end)

    def contains(self, moment: datetime) -> bool:
        return self.start <= moment < self.end

    def to_dict(self) -> dict[str, str]:
        last_day = self.end - timedelta(microseconds=1)
        return {"start": self.start.strftime("%Y-%m-%d"), "end": last_day.strftime("%Y-%m-%d")}


def parse_day(value: str) -> datetime:
    try:
        return datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError as error:
        raise SystemExit(f"window: expected YYYY-MM-DD, got {value!r}") from error


def truncate(text: str, limit: int) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return f"{text[:limit]}… [{len(text) - limit} more characters]"


def pack_slices(digests: list[tuple[str, int]], slice_chars: int) -> list[list[str]]:
    """Pack (relative path, size) pairs, in order, into slices of about `slice_chars` each."""
    slices: list[list[str]] = []
    current: list[str] = []
    size = 0
    for path, length in digests:
        if current and size + length > slice_chars:
            slices.append(current)
            current, size = [], 0
        current.append(path)
        size += length
    if current:
        slices.append(current)
    return slices


def add_window_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--since", required=True, help="first day of the window, YYYY-MM-DD (UTC)")
    parser.add_argument("--until", help="day after the window ends, YYYY-MM-DD (default: now)")
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--slice-chars", type=int, default=250_000)


def write_summary(out: Path, summary: dict[str, object]) -> None:
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


def print_summary(summary: dict[str, object]) -> None:
    """Print the summary with the slice lists replaced by their count."""
    print(json.dumps({**summary, "slices": len(summary["slices"])}))
