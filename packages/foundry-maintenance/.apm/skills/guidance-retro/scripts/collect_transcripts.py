#!/usr/bin/env python3
"""Digest local Claude Code and Cursor agent transcripts for guidance-retro miners.

Reads every top-level session modified inside the window, keeps what a miner needs
(human messages, assistant prose, which tools ran, which skills were loaded, which
models answered) and drops tool output. Writes one Markdown digest per session to
OUT/sessions/ and OUT/summary.json, whose `slices` list groups the digests into
batches of about --slice-chars characters, one per miner subagent.

Usage:
    collect_transcripts.py --since 2026-10-21 --out RUN/transcripts
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator, Literal

from digest import Window, add_window_args, pack_slices, print_summary, truncate, write_summary

Host = Literal["claude-code", "cursor"]

USER_LIMIT = 3000
ASSISTANT_LIMIT = 1200
SKILL_PATH = re.compile(r"skills/([a-z0-9][a-z0-9-]*)/SKILL\.md")
COMMAND_NAME = re.compile(r"<command-name>/?([^<\s]+)</command-name>")
CURSOR_QUERY = re.compile(r"<user_query>(.*?)</user_query>", re.DOTALL)
CURSOR_ATTACHED_SKILL = re.compile(r"^Skill Name: (\S+)", re.MULTILINE)
# Claude Code writes these as `user` records, but nobody typed them. Older records carry no `origin`.
MACHINE_TEXT = ("<task-notification>", "<local-command-stdout>", "<local-command-caveat>", "<bash-stdout>")


@dataclass
class Session:
    host: Host
    id: str
    project: str
    path: Path
    modified: datetime
    turns: list[tuple[str, str]] = field(default_factory=list)
    skills: set[str] = field(default_factory=set)
    models: Counter[str] = field(default_factory=Counter)
    subagents: int = 0
    unreadable_lines: int = 0

    def say(self, role: str, text: str, limit: int) -> None:
        if text.strip():
            self.turns.append((role, truncate(text, limit)))

    def tool(self, name: str, tool_input: object) -> None:
        self.skills.update(SKILL_PATH.findall(json.dumps(tool_input)))
        if self.turns and self.turns[-1][0] == "tools":
            self.turns[-1] = ("tools", f"{self.turns[-1][1]}, {name}")
        else:
            self.turns.append(("tools", name))

    @property
    def human_turns(self) -> int:
        return sum(1 for role, _ in self.turns if role == "user")

    def render(self) -> str:
        lines = [
            f"# {self.host} session {self.id}",
            "",
            f"- project: {self.project}",
            f"- modified: {self.modified:%Y-%m-%d %H:%M} UTC",
            f"- skills loaded: {', '.join(sorted(self.skills)) or 'none seen'}",
            f"- models: {', '.join(sorted(self.models)) or 'not recorded'}",
            f"- subagent transcripts: {self.subagents}",
            "",
        ]
        for role, text in self.turns:
            lines.append(f"[tools: {text}]" if role == "tools" else f"**{role}:** {text}")
            lines.append("")
        return "\n".join(lines)


def read_lines(session: Session) -> Iterator[dict[str, Any]]:
    with session.path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                session.unreadable_lines += 1
                continue
            if isinstance(record, dict):
                yield record


def text_blocks(content: object) -> list[str]:
    if isinstance(content, str):
        return [content]
    if not isinstance(content, list):
        return []
    return [block.get("text", "") for block in content if isinstance(block, dict) and block.get("type") == "text"]


def tool_blocks(content: object) -> list[dict[str, Any]]:
    if not isinstance(content, list):
        return []
    return [block for block in content if isinstance(block, dict) and block.get("type") == "tool_use"]


def typed_by_person(record: dict[str, Any]) -> bool:
    origin = (record.get("origin") or {}).get("kind")
    return not record.get("isCompactSummary") and origin in (None, "human")


def parse_claude(session: Session) -> None:
    for record in read_lines(session):
        message = record.get("message")
        if not isinstance(message, dict) or record.get("isMeta"):
            continue
        content = message.get("content")
        if record.get("type") == "user":
            if not typed_by_person(record):
                continue
            for text in text_blocks(content):
                session.skills.update(COMMAND_NAME.findall(text))
                if not text.lstrip().startswith(MACHINE_TEXT):
                    session.say("user", text, USER_LIMIT)
        elif record.get("type") == "assistant":
            model = message.get("model")
            if model and not model.startswith("<"):
                session.models[model] += 1
            for text in text_blocks(content):
                session.say("assistant", text, ASSISTANT_LIMIT)
            for block in tool_blocks(content):
                tool_input = block.get("input") or {}
                if block.get("name") == "Skill" and isinstance(tool_input, dict) and tool_input.get("skill"):
                    session.skills.add(str(tool_input["skill"]))
                session.tool(str(block.get("name")), tool_input)


def parse_cursor(session: Session) -> None:
    for record in read_lines(session):
        message = record.get("message")
        if not isinstance(message, dict):
            continue
        content = message.get("content")
        if record.get("role") == "user":
            for text in text_blocks(content):
                session.skills.update(CURSOR_ATTACHED_SKILL.findall(text))
                query = CURSOR_QUERY.search(text)
                session.say("user", query.group(1) if query else text, USER_LIMIT)
        elif record.get("role") == "assistant":
            for text in text_blocks(content):
                session.say("assistant", text, ASSISTANT_LIMIT)
            for block in tool_blocks(content):
                session.tool(str(block.get("name")), block.get("input") or {})


def modified_at(path: Path) -> datetime:
    return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)


def discover(claude_root: Path, cursor_root: Path, window: Window) -> list[Session]:
    sessions: list[Session] = []
    for path in sorted(claude_root.glob("*/*.jsonl")):
        modified = modified_at(path)
        if window.contains(modified):
            session = Session("claude-code", path.stem, path.parent.name, path, modified)
            session.subagents = len(list((path.with_suffix("") / "subagents").glob("*.jsonl")))
            sessions.append(session)
    for path in sorted(cursor_root.glob("*/agent-transcripts/*/*.jsonl")):
        modified = modified_at(path)
        if path.stem == path.parent.name and window.contains(modified):
            session = Session("cursor", path.stem, path.parents[2].name, path, modified)
            session.subagents = len(list((path.parent / "subagents").glob("*.jsonl")))
            sessions.append(session)
    return sessions


def collect(claude_root: Path, cursor_root: Path, window: Window, out: Path, slice_chars: int) -> dict[str, Any]:
    sessions_dir = out / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)
    digests: list[tuple[str, int]] = []
    by_host: Counter[str] = Counter()
    models: Counter[str] = Counter()
    unreadable = 0
    for session in discover(claude_root, cursor_root, window):
        (parse_claude if session.host == "claude-code" else parse_cursor)(session)
        unreadable += session.unreadable_lines
        if session.human_turns == 0:
            continue
        text = truncate(session.render(), slice_chars)
        relative = f"sessions/{session.host}-{session.id}.md"
        (out / relative).write_text(text + "\n", encoding="utf-8")
        digests.append((relative, len(text)))
        by_host[session.host] += 1
        models.update({model: 1 for model in session.models})
    summary = {
        "window": window.to_dict(),
        "sessions": len(digests),
        "by_host": dict(by_host),
        "sessions_per_model": dict(models.most_common()),
        "unreadable_lines": unreadable,
        "slices": pack_slices(digests, slice_chars),
    }
    write_summary(out, summary)
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_window_args(parser)
    parser.add_argument("--claude-root", type=Path, default=Path.home() / ".claude" / "projects")
    parser.add_argument("--cursor-root", type=Path, default=Path.home() / ".cursor" / "projects")
    args = parser.parse_args(argv)
    summary = collect(args.claude_root, args.cursor_root, Window.parse(args.since, args.until), args.out, args.slice_chars)
    print_summary(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
