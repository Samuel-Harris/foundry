from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".apm/skills/claude-code-cost-review/scripts"))

from summarise_sessions import fit_rates, load_sessions, parse_window, summarise  # noqa: E402

RATES = {"input": 4.0, "output": 20.0, "read": 0.2, "write_5m": 5.0, "write_1h": 8.0}
INSIDE = "2026-11-18T10:00:00.000Z"
OUTSIDE = "2026-11-01T10:00:00.000Z"
WINDOW = parse_window(since="2026-11-16", until="2026-11-22")


def usage(*, fresh: int, output: int, read: int, write_5m: int, write_1h: int) -> dict[str, object]:
    return {
        "input_tokens": fresh,
        "output_tokens": output,
        "cache_read_input_tokens": read,
        "cache_creation_input_tokens": write_5m + write_1h,
        "cache_creation": {"ephemeral_5m_input_tokens": write_5m, "ephemeral_1h_input_tokens": write_1h},
        "speed": "standard",
    }


def cost_of(tokens: dict[str, int]) -> float:
    return sum(tokens[key] * RATES[key] for key in RATES) / 1e6


def assistant(*, request_id: str, timestamp: str, tokens: dict[str, int], agent_id: str | None = None) -> dict[str, object]:
    record: dict[str, object] = {
        "type": "assistant",
        "requestId": request_id,
        "timestamp": timestamp,
        "sessionId": "s",
        "effort": "medium",
        "message": {
            "model": "claude-opus-5-5",
            "usage": usage(
                fresh=tokens["input"], output=tokens["output"], read=tokens["read"],
                write_5m=tokens["write_5m"], write_1h=tokens["write_1h"],
            ),
        },
    }
    if agent_id:
        record["agentId"] = agent_id
    return record


def cost_state(requests: list[dict[str, int]]) -> dict[str, object]:
    total = {key: sum(r[key] for r in requests) for key in RATES}
    return {
        "type": "cost-state",
        "modelUsage": {
            "claude-opus-5-5": {
                "inputTokens": total["input"],
                "outputTokens": total["output"],
                "cacheReadInputTokens": total["read"],
                "cacheCreationInputTokens": total["write_5m"] + total["write_1h"],
                "cacheCreationEphemeral5mInputTokens": total["write_5m"],
                "cacheCreationEphemeral1hInputTokens": total["write_1h"],
                "costUSD": sum(cost_of(r) for r in requests),
            }
        },
    }


def write_jsonl(path: Path, records: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, separators=(",", ":")) + "\n" for r in records), encoding="utf-8")


def mix(seed: int) -> dict[str, int]:
    return {
        "input": 100 * seed,
        "output": 2_000 + 700 * seed,
        "read": 400_000 + 90_000 * (seed % 4),
        "write_5m": 30_000 + 11_000 * (seed % 3),
        "write_1h": 5_000 * (seed % 5),
    }


class SummariseSessionsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.projects = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        for seed in range(1, 8):
            tokens = mix(seed)
            write_jsonl(
                self.projects / "proj-a" / f"history-{seed}.jsonl",
                [assistant(request_id=f"h{seed}", timestamp=OUTSIDE, tokens=tokens), cost_state([tokens])],
            )

    def run_summary(self) -> dict[str, object]:
        sessions = load_sessions(self.projects)
        return summarise(sessions=sessions, rates=fit_rates(sessions), window=WINDOW, top=5)

    def test_fitted_rates_price_each_request_at_its_true_cost(self) -> None:
        tokens = mix(11)
        write_jsonl(self.projects / "proj-b" / "live.jsonl", [assistant(request_id="r1", timestamp=INSIDE, tokens=tokens)])
        summary = self.run_summary()
        self.assertAlmostEqual(summary["total_cost"], round(cost_of(tokens), 2), places=2)

    def test_a_request_split_across_content_blocks_is_counted_once(self) -> None:
        tokens = mix(9)
        block = assistant(request_id="dup", timestamp=INSIDE, tokens=tokens)
        write_jsonl(self.projects / "proj-b" / "live.jsonl", [block, block, block])
        summary = self.run_summary()
        self.assertEqual(summary["requests"], 1)
        self.assertAlmostEqual(summary["total_cost"], round(cost_of(tokens), 2), places=2)

    def test_requests_outside_the_window_are_excluded(self) -> None:
        summary = self.run_summary()
        self.assertEqual(summary["requests"], 0)
        self.assertEqual(summary["total_cost"], 0)

    def test_subagent_spend_is_bucketed_by_routing(self) -> None:
        main = self.projects / "proj-b" / "live.jsonl"
        write_jsonl(main, [assistant(request_id="m1", timestamp=INSIDE, tokens=mix(2))])
        subagents = main.with_suffix("") / "subagents"
        for agent_id, meta in {
            "a1": {"agentType": "Explore", "model": "claude-opus-5-5", "launchedWithDefaults": True, "description": "scan"},
            "a2": {"agentType": "poteto-agent", "model": "haiku", "description": "watch CI"},
        }.items():
            write_jsonl(subagents / f"agent-{agent_id}.jsonl",
                        [assistant(request_id=f"r-{agent_id}", timestamp=INSIDE, tokens=mix(3), agent_id=agent_id)])
            (subagents / f"agent-{agent_id}.meta.json").write_text(json.dumps(meta), encoding="utf-8")
        buckets = {row["key"] for row in self.run_summary()["by_agent"]}
        self.assertEqual(buckets, {"main chat", "Explore (inherited)", "poteto-agent (pinned haiku)"})

    def test_the_until_day_is_included(self) -> None:
        write_jsonl(self.projects / "proj-b" / "live.jsonl", [
            assistant(request_id="last", timestamp="2026-11-22T23:59:00.000Z", tokens=mix(4)),
            assistant(request_id="after", timestamp="2026-11-23T00:00:00.000Z", tokens=mix(4)),
        ])
        self.assertEqual(self.run_summary()["requests"], 1)


if __name__ == "__main__":
    unittest.main()
