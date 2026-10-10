#!/usr/bin/env python3
"""Summarise Cursor agent transcripts: where assistant turns went, by chat, subagent model and skill.

Usage:
    python3 summarise_transcripts.py --since 2026-10-02 [--projects-dir ~/.cursor/projects] [--top 10] [--json OUT.json]
    python3 summarise_transcripts.py --csv USAGE.csv   # window = the CSV's first..last day

Transcripts record tool calls but not tool results, so turn counts are a proxy for cost, not dollars.
Prints aggregates and short opening prompts only. Standard library only.
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime

LENGTH_BUCKETS = ((0, 50), (50, 100), (100, 200), (200, 10**9))
SKILL_NAME = re.compile(r"Skill Name: ([^\n]+)")
SLASH_COMMAND = re.compile(r"<user_query>\s*/([A-Za-z0-9_-]+)(?=\s|<|$)")
TIMESTAMP = re.compile(r"<timestamp>\w+, (\w+ \d+, \d{4})")
QUERY_BODY = re.compile(r"<user_query>\s*(.*?)\s*(?:</user_query>|$)", re.S)
INHERIT_VALUES = {"", "inherit", "(inherit)", "inherit-parent", "auto"}


@dataclass
class TaskCall:
    model: str
    subagent_type: str
    description: str
    prompt_key: str


@dataclass
class Transcript:
    path: str
    assistant_turns: int = 0
    user_messages: int = 0
    tool_calls: int = 0
    first_query: str = ""
    started: str | None = None
    skills: set[str] = field(default_factory=set)
    task_calls: list[TaskCall] = field(default_factory=list)

    @property
    def workspace(self) -> str:
        return self.path.split(os.sep + "agent-transcripts" + os.sep)[0].rsplit(os.sep, 1)[-1]

    @property
    def chat_id(self) -> str:
        return os.path.splitext(os.path.basename(self.path))[0]


def as_dict(value: object) -> dict:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return {}
        return parsed if isinstance(parsed, dict) else {}
    return {}


def prompt_key(text: str) -> str:
    text = re.sub(r"^<timestamp>.*?</timestamp>\s*", "", text, flags=re.S)
    text = re.sub(r"^<user_query>\s*", "", text)
    return re.sub(r"\s+", " ", text)[:120]


def message_text(content: object) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(p.get("text", "") for p in content if isinstance(p, dict) and p.get("type") == "text")
    return ""


def task_call_from(part: dict) -> TaskCall | None:
    name = part.get("name")
    args = as_dict(part.get("input"))
    if name == "CallDynamicTool" and args.get("toolName") == "Task":
        args = as_dict(args.get("arguments"))
    elif name != "Task":
        return None
    model = str(args.get("model") or "")
    return TaskCall(
        model="inherit" if model in INHERIT_VALUES else model,
        subagent_type=str(args.get("subagent_type") or ""),
        description=str(args.get("description") or ""),
        prompt_key=prompt_key(str(args.get("prompt") or "")),
    )


def read_transcript(path: str) -> Transcript:
    transcript = Transcript(path=path)
    with open(path, errors="replace") as handle:
        for line in handle:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            role = record.get("role")
            content = (record.get("message") or {}).get("content")
            if role == "user":
                transcript.user_messages += 1
                text = message_text(content)
                transcript.skills.update(s.strip() for s in SKILL_NAME.findall(text))
                transcript.skills.update(SLASH_COMMAND.findall(text))
                if transcript.started is None and (stamp := TIMESTAMP.search(text)):
                    transcript.started = datetime.strptime(stamp.group(1), "%b %d, %Y").date().isoformat()
                if not transcript.first_query:
                    match = QUERY_BODY.search(text)
                    transcript.first_query = prompt_key(match.group(1) if match else text)
            elif role == "assistant":
                transcript.assistant_turns += 1
                for part in content if isinstance(content, list) else []:
                    if isinstance(part, dict) and part.get("type") == "tool_use":
                        transcript.tool_calls += 1
                        call = task_call_from(part)
                        if call:
                            transcript.task_calls.append(call)
    return transcript


def match_task_call(subagent: Transcript, calls: list[TaskCall]) -> TaskCall | None:
    key = subagent.first_query
    for call in calls:
        if call.prompt_key and (key.startswith(call.prompt_key[:80]) or call.prompt_key.startswith(key[:80])):
            return call
    return None


def window_from_csv(csv_path: str) -> tuple[str, str]:
    with open(csv_path, newline="") as handle:
        days = [row["Date"][:10] for row in csv.DictReader(handle) if row.get("Date")]
    if not days:
        raise SystemExit(f"error: no Date values in {csv_path}")
    return min(days), max(days)


def summarise(projects_dir: str, since: str, until: str | None, top: int) -> dict:
    cutoff = datetime.fromisoformat(since).timestamp()
    parent_paths = [
        p
        for p in glob.glob(os.path.join(projects_dir, "*", "agent-transcripts", "*", "*.jsonl"))
        if os.path.getmtime(p) >= cutoff
    ]

    parents: list[Transcript] = []
    buckets: dict[str, dict[str, int]] = defaultdict(lambda: {"runs": 0, "turns": 0})
    subagent_runs: list[dict] = []
    for path in parent_paths:
        parent = read_transcript(path)
        if until and parent.started and parent.started > until:
            continue
        parents.append(parent)
        buckets["main chats"]["runs"] += 1
        buckets["main chats"]["turns"] += parent.assistant_turns
        for sub_path in glob.glob(os.path.join(os.path.dirname(path), "subagents", "*.jsonl")):
            if os.path.getmtime(sub_path) < cutoff:
                continue
            subagent = read_transcript(sub_path)
            call = match_task_call(subagent, parent.task_calls)
            label = (
                f"subagent model={call.model} type={call.subagent_type or 'default'}"
                if call
                else "subagent (unmatched to a Task call)"
            )
            buckets[label]["runs"] += 1
            buckets[label]["turns"] += subagent.assistant_turns
            subagent_runs.append(
                {
                    "model": call.model if call else "unknown",
                    "subagent_type": call.subagent_type if call else "unknown",
                    "description": call.description if call else subagent.first_query[:80],
                    "turns": subagent.assistant_turns,
                    "workspace": parent.workspace,
                }
            )
    if not parents:
        raise SystemExit(f"error: no transcripts under {projects_dir} in the window {since}..{until or 'now'}")

    total_turns = sum(b["turns"] for b in buckets.values()) or 1
    turn_shares = [
        {"bucket": k, "runs": v["runs"], "turns": v["turns"], "share": round(v["turns"] / total_turns, 4)}
        for k, v in sorted(buckets.items(), key=lambda x: -x[1]["turns"])
    ]

    length_distribution = []
    for low, high in LENGTH_BUCKETS:
        chats = [p for p in parents if low <= p.assistant_turns < high]
        length_distribution.append(
            {
                "turns": f"{low}-{high - 1 if high < 10**9 else '+'}",
                "chats": len(chats),
                "turns_total": sum(p.assistant_turns for p in chats),
            }
        )

    by_skill: dict[str, list[int]] = defaultdict(list)
    for p in parents:
        for skill in p.skills or {"(no skill or command)"}:
            by_skill[skill].append(p.assistant_turns)
    skills = [
        {
            "skill": s,
            "chats": len(t),
            "turns_total": sum(t),
            "avg_turns": round(sum(t) / len(t), 1),
            "chats_over_200_turns": sum(1 for x in t if x >= 200),
        }
        for s, t in sorted(by_skill.items(), key=lambda x: -sum(x[1]))
    ]

    spawned = Counter((c.model, c.subagent_type or "default") for p in parents for c in p.task_calls)

    return {
        "since": since,
        "until": until,
        "projects_dir": projects_dir,
        "main_chats": len(parents),
        "subagent_runs": len(subagent_runs),
        "total_assistant_turns": total_turns,
        "turn_shares": turn_shares,
        "chat_length_distribution": length_distribution,
        "longest_chats": [
            {
                "workspace": p.workspace,
                "chat_id": p.chat_id,
                "assistant_turns": p.assistant_turns,
                "user_messages": p.user_messages,
                "subagents_spawned": len(p.task_calls),
                "skills": sorted(p.skills),
                "opening_prompt": p.first_query[:100],
            }
            for p in sorted(parents, key=lambda p: -p.assistant_turns)[:top]
        ],
        "skills": skills,
        "task_calls_by_model_and_type": [
            {"model": m, "subagent_type": t, "calls": n} for (m, t), n in spawned.most_common()
        ],
        "largest_inherit_subagents": sorted(
            (r for r in subagent_runs if r["model"] == "inherit"), key=lambda r: -r["turns"]
        )[:top],
    }


def print_report(summary: dict) -> None:
    print(
        f"Transcripts active {summary['since']}..{summary['until'] or 'now'}: {summary['main_chats']} main chats, "
        f"{summary['subagent_runs']} subagent runs, {summary['total_assistant_turns']} assistant turns"
    )
    print("(turns are a cost proxy; transcripts omit tool results, and main-chat turns carry larger contexts)")

    print("\nAssistant turns by source")
    for b in summary["turn_shares"]:
        print(f"  {b['bucket']:70s} runs={b['runs']:4d} turns={b['turns']:6d} {b['share']:6.1%}")

    print("\nMain-chat length distribution (assistant turns)")
    for d in summary["chat_length_distribution"]:
        print(f"  {d['turns']:>8s} chats={d['chats']:4d} turns={d['turns_total']:6d}")

    print("\nLongest main chats")
    for c in summary["longest_chats"]:
        skills = ",".join(c["skills"]) or "-"
        print(
            f"  turns={c['assistant_turns']:4d} users={c['user_messages']:3d} subagents={c['subagents_spawned']:3d} "
            f"{c['workspace'][-35:]} {c['chat_id']} [{skills}] {c['opening_prompt'][:60]!r}"
        )

    print("\nMain chats by invoked skill or slash command")
    for s in summary["skills"][:20]:
        print(
            f"  {s['skill'][:40]:40s} chats={s['chats']:4d} turns={s['turns_total']:6d} "
            f"avg={s['avg_turns']:6.1f} >=200 turns={s['chats_over_200_turns']}"
        )

    print("\nTask calls by requested model and subagent type")
    for t in summary["task_calls_by_model_and_type"]:
        print(f"  {t['calls']:4d} model={t['model']} type={t['subagent_type']}")

    if summary["largest_inherit_subagents"]:
        print("\nLargest subagents that inherited the main chat's model")
        for r in summary["largest_inherit_subagents"]:
            print(f"  turns={r['turns']:4d} type={r['subagent_type']} {r['description'][:70]!r}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    window = parser.add_mutually_exclusive_group(required=True)
    window.add_argument("--since", help="YYYY-MM-DD; include transcripts modified on or after this day")
    window.add_argument("--csv", dest="csv_path", help="usage CSV; the window becomes its first..last day")
    parser.add_argument("--until", help="YYYY-MM-DD; exclude chats whose first message is after this day")
    parser.add_argument("--projects-dir", default=os.path.expanduser("~/.cursor/projects"))
    parser.add_argument("--top", type=int, default=10)
    parser.add_argument("--json", dest="json_path", help="also write the full summary as JSON")
    args = parser.parse_args()

    since, until = window_from_csv(args.csv_path) if args.csv_path else (args.since, args.until)
    summary = summarise(args.projects_dir, since, args.until or until, args.top)
    print_report(summary)
    if args.json_path:
        with open(args.json_path, "w") as handle:
            json.dump(summary, handle, indent=2)
        print(f"\nWrote {args.json_path}")


if __name__ == "__main__":
    main()
