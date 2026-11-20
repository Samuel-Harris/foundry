from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".apm/skills/guidance-retro/scripts"))

from collect_transcripts import collect  # noqa: E402
from digest import Window, pack_slices  # noqa: E402

WINDOW = Window(datetime(2026, 11, 1, tzinfo=timezone.utc), datetime(2026, 11, 8, tzinfo=timezone.utc))
INSIDE = datetime(2026, 11, 3, tzinfo=timezone.utc).timestamp()
BEFORE = datetime(2026, 10, 20, tzinfo=timezone.utc).timestamp()


def write_jsonl(path: Path, records: list[object], mtime: float = INSIDE, raw_tail: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(record) + "\n" for record in records) + raw_tail, encoding="utf-8")
    os.utime(path, (mtime, mtime))


def claude_records(prompt: str) -> list[object]:
    return [
        {"type": "mode", "mode": "normal"},
        {"type": "user", "message": {"role": "user", "content": prompt}},
        {
            "type": "assistant",
            "message": {
                "model": "claude-opus-5-5",
                "content": [
                    {"type": "text", "text": "Running the tests now."},
                    {"type": "tool_use", "name": "Skill", "input": {"skill": "thermos"}},
                    {"type": "tool_use", "name": "Read", "input": {"file_path": "/x/.claude/skills/unslop/SKILL.md"}},
                ],
            },
        },
        {"type": "user", "message": {"role": "user", "content": [{"type": "tool_result", "content": "SECRET TOOL OUTPUT"}]}},
        {"type": "user", "isMeta": True, "message": {"role": "user", "content": "meta noise"}},
        {"type": "user", "origin": {"kind": "task-notification"}, "message": {"role": "user", "content": "<task-notification>subagent report</task-notification>"}},
        {"type": "user", "message": {"role": "user", "content": "<task-notification>older subagent report</task-notification>"}},
        {"type": "user", "isCompactSummary": True, "message": {"role": "user", "content": "compaction summary"}},
        {"type": "assistant", "message": {"model": "<synthetic>", "content": [{"type": "text", "text": "No response requested."}]}},
        {"type": "user", "message": {"role": "user", "content": "<command-name>/poteto-mode</command-name> no, you never ran them"}},
    ]


class CollectTranscriptsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.claude = self.tmp / "claude"
        self.cursor = self.tmp / "cursor"
        self.out = self.tmp / "out"

    def run_collect(self) -> dict:
        return collect(self.claude, self.cursor, WINDOW, self.out, 250_000, ())

    def test_claude_digest_keeps_human_and_assistant_text_and_drops_tool_output(self) -> None:
        session = self.claude / "proj-a" / "s1.jsonl"
        write_jsonl(session, claude_records("fix the bug"), raw_tail='{"truncated')
        write_jsonl(session.with_suffix("") / "subagents" / "agent-1.jsonl", [])

        summary = self.run_collect()

        digest = (self.out / "sessions" / "claude-code-s1.md").read_text()
        self.assertIn("**user:** fix the bug", digest)
        self.assertIn("no, you never ran them", digest)
        self.assertIn("**assistant:** Running the tests now.", digest)
        self.assertIn("[tools: Skill, Read]", digest)
        self.assertIn("skills loaded: poteto-mode, thermos, unslop", digest)
        self.assertIn("models: claude-opus-5-5", digest)
        self.assertIn("subagent transcripts: 1", digest)
        self.assertNotIn("SECRET TOOL OUTPUT", digest)
        self.assertNotIn("meta noise", digest)
        self.assertNotIn("subagent report", digest)
        self.assertNotIn("compaction summary", digest)
        self.assertEqual(summary["unreadable_lines"], 1)
        self.assertEqual(summary["sessions_per_model"], {"claude-opus-5-5": 1})

    def test_cursor_digest_extracts_the_query_and_attached_skills(self) -> None:
        text = "<manually_attached_skills>\nSkill Name: poteto-mode\nlong inlined skill</manually_attached_skills>\n<user_query>\nship it\n</user_query>"
        write_jsonl(
            self.cursor / "proj-b" / "agent-transcripts" / "c1" / "c1.jsonl",
            [
                {"role": "user", "message": {"content": [{"type": "text", "text": text}]}},
                {"role": "assistant", "message": {"content": [{"type": "tool_use", "name": "Shell", "input": {"command": "ls"}}]}},
                {"type": "turn_ended"},
            ],
        )

        summary = self.run_collect()

        digest = (self.out / "sessions" / "cursor-c1.md").read_text()
        self.assertIn("**user:** ship it", digest)
        self.assertNotIn("long inlined skill", digest)
        self.assertIn("skills loaded: poteto-mode", digest)
        self.assertEqual(summary["by_host"], {"cursor": 1})

    def test_sessions_outside_the_window_or_without_human_turns_are_skipped(self) -> None:
        write_jsonl(self.claude / "p" / "old.jsonl", claude_records("old work"), mtime=BEFORE)
        write_jsonl(self.claude / "p" / "silent.jsonl", [{"type": "assistant", "message": {"content": [{"type": "text", "text": "hi"}]}}])
        write_jsonl(self.cursor / "p" / "agent-transcripts" / "c2" / "subagents" / "x.jsonl", [{"role": "user", "message": {"content": [{"type": "text", "text": "sub"}]}}])

        summary = self.run_collect()

        self.assertEqual(summary["sessions"], 0)
        self.assertEqual(summary["slices"], [])


    def test_project_filter_keeps_the_checkout_and_its_worktrees_in_both_hosts_naming(self) -> None:
        for folder in (
            "-Users-me-code-app",
            "-Users-me-code-app--worktrees-fix-bug",
            "-Users-me-code-app-worktrees-Worker1",
            "-Users-me-code-app--claude-worktrees-agent-1",
            "-Users-me-code-application",
            "-Users-me-code-other",
        ):
            write_jsonl(self.claude / folder / f"{folder}.jsonl", claude_records("work"))
        write_jsonl(self.cursor / "Users-me-code-app-worktrees-sam-eng-1" / "agent-transcripts" / "c1" / "c1.jsonl", [
            {"role": "user", "message": {"content": [{"type": "text", "text": "<user_query>go</user_query>"}]}},
        ])

        summary = collect(self.claude, self.cursor, WINDOW, self.out, 250_000, (Path("/Users/me/code/app"),))

        self.assertEqual(summary["projects"], [
            "-Users-me-code-app",
            "-Users-me-code-app--claude-worktrees-agent-1",
            "-Users-me-code-app--worktrees-fix-bug",
            "-Users-me-code-app-worktrees-Worker1",
            "Users-me-code-app-worktrees-sam-eng-1",
        ])
        self.assertEqual(summary["by_host"], {"claude-code": 4, "cursor": 1})


class PackSlicesTests(unittest.TestCase):
    def test_packs_in_order_and_gives_an_oversized_item_its_own_slice(self) -> None:
        self.assertEqual(
            pack_slices([("a", 4), ("b", 4), ("c", 30), ("d", 1)], 10),
            [["a", "b"], ["c"], ["d"]],
        )


if __name__ == "__main__":
    unittest.main()
