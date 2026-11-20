from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".apm/skills/guidance-retro/scripts"))

from build_report import build_report, render  # noqa: E402
from guidance import inventory, render_inventory, require_foundry, route  # noqa: E402

SKILL_PATH = "packages/review/.apm/skills/thermos/SKILL.md"


def make_foundry(root: Path) -> None:
    (root / "apm.yml").write_text("name: foundry\nversion: \"0.1.0\"\n")
    skill = root / SKILL_PATH
    skill.parent.mkdir(parents=True)
    skill.write_text('---\nname: thermos\ndescription: "Run both reviews | merge findings."\n---\n# Thermos\n')
    agent = root / "packages/explore/.apm/agents/explore.agent.md"
    agent.parent.mkdir(parents=True)
    agent.write_text("---\ndescription: >-\n  Search the\n  codebase.\nmodel: inherit\n---\n")
    instruction = root / "packages/coding-style/.apm/instructions/python-rules.instructions.md"
    instruction.parent.mkdir(parents=True)
    instruction.write_text("---\ndescription: Python style.\napplyTo: \"**/*.py\"\n---\n")


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data))


def evidence(source: str, ref: str | int) -> dict[str, Any]:
    return {"source": source, "ref": ref, "url": None, "quote": "q"}


def candidate(action: str = "update", basis: str = "evidence", path: str = SKILL_PATH, items: list[dict] | None = None, title: str = "T") -> dict[str, Any]:
    return {
        "title": title,
        "action": action,
        "basis": basis,
        "path": path,
        "section": None,
        "change": "new wording",
        "rationale": "why",
        "evidence": items or [],
    }


class GuidanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp())
        make_foundry(self.root)

    def test_inventory_lists_every_primitive_kind_with_its_package(self) -> None:
        table = render_inventory(inventory(self.root))

        self.assertIn(f"| `thermos` | skill | `review` | `{SKILL_PATH}` | Run both reviews / merge findings. |", table)
        self.assertIn("| `explore` | agent | `explore` | `packages/explore/.apm/agents/explore.agent.md` | Search the codebase. |", table)
        self.assertIn("| `python-rules` | instruction | `coding-style` |", table)

    def test_route_splits_by_owning_package_and_reports_bad_lines(self) -> None:
        run = self.root / "run"
        lines = [
            {"kind": "defect", "pattern": "p", "guidance": "thermos", "source": "review", "ref": 12, "url": None, "quote": "q"},
            {"kind": "gap", "pattern": "p", "guidance": None, "source": "transcript", "ref": "s1", "url": None, "quote": "q"},
            {"kind": "friction", "pattern": "p", "guidance": "no-such-skill", "source": "transcript", "ref": "s2", "url": None, "quote": "q"},
            {"kind": "vibes", "pattern": "p", "guidance": None, "source": "transcript", "ref": "s3", "url": None, "quote": "q"},
        ]
        write_json(run / "transcripts/summary.json", {"slices": [["a"], ["b"], ["c"]]})
        write_json(run / "reviews/summary.json", {"slices": [["d"]]})
        (run / "obs").mkdir(parents=True)
        (run / "obs" / "_scratch.jsonl").write_text("not json\n")
        (run / "obs" / "t-1.jsonl").write_text("\n".join(json.dumps(line) for line in lines) + "\nnot json\n")

        summary = route(self.root, run)

        self.assertEqual(summary["observations"], {"_unowned": 2, "review": 1})
        self.assertEqual(summary["unknown_guidance"], ["no-such-skill"])
        self.assertEqual([item["line"] for item in summary["rejected"]], ["t-1.jsonl:4", "t-1.jsonl:5"])
        self.assertEqual(len((run / "routed" / "_unowned.jsonl").read_text().splitlines()), 2)
        self.assertEqual(summary["missing_slices"], ["t-0", "t-2", "r-0"])

    def test_require_foundry_rejects_another_repository(self) -> None:
        other = Path(tempfile.mkdtemp())
        (other / "apm.yml").write_text("name: planning\n")
        with self.assertRaises(SystemExit):
            require_foundry(other)
        require_foundry(self.root)


class BuildReportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp())
        make_foundry(self.root)
        self.run = self.root / "run"
        write_json(self.run / "transcripts/summary.json", {
            "window": {"start": "2026-11-01", "end": "2026-11-08"}, "sessions": 9,
            "by_host": {"claude-code": 9}, "sessions_per_model": {"claude-opus-5-5": 9}, "unreadable_lines": 0, "slices": [],
        })
        write_json(self.run / "reviews/summary.json", {
            "repos": ["o/r"], "window": {"start": "2026-11-01", "end": "2026-11-08"}, "pull_requests_scanned": 5,
            "pull_requests_with_comments": 4, "comments": 20, "truncated_pull_requests": ["o/r#7"], "slices": [],
        })
        write_json(self.run / "routed/summary.json", {"observations": {}, "unknown_guidance": [], "rejected": [], "missing_slices": []})
        for session in ("s1", "s9", "0123456789abcdef"):
            (self.run / f"transcripts/sessions/claude-code-{session}.md").parent.mkdir(parents=True, exist_ok=True)
            (self.run / f"transcripts/sessions/claude-code-{session}.md").write_text("digest")
        for number in (1, 2, 3, 4, 5):
            (self.run / f"reviews/prs/o/r/{number}.md").parent.mkdir(parents=True, exist_ok=True)
            (self.run / f"reviews/prs/o/r/{number}.md").write_text("digest")

    def report(self, *candidates: dict[str, Any]) -> dict[str, Any]:
        write_json(self.run / "candidates/review.json", list(candidates))
        return build_report(self.run, self.root)

    @staticmethod
    def titles(groups: list[dict[str, Any]]) -> list[str]:
        return [item["title"] for group in groups for file in group["files"] for item in file["items"]]

    def test_evidence_bar_places_each_candidate(self) -> None:
        three = [evidence("transcript", "s1"), evidence("review", 4), evidence("review", "5")]
        repeated = [evidence("review", 4), evidence("review", "4"), evidence("transcript", "s1")]
        report = self.report(
            candidate(title="update with three sources", items=three),
            candidate(title="update with one PR counted twice", items=repeated),
            candidate(action="add", path="packages/review/.apm/skills/new-skill/SKILL.md", title="add", items=three),
            candidate(action="delete", title="stale reference", items=[evidence("static", SKILL_PATH)]),
            candidate(title="description contradicts the command", items=[evidence("static", SKILL_PATH)]),
            candidate(action="add", path="packages/review/.apm/skills/other/SKILL.md", title="static add", items=[evidence("static", SKILL_PATH)]),
            {key: value for key, value in candidate(action="delete", basis="judgement", title="models do this by default").items() if key != "evidence"},
            candidate(action="delete", basis="silence", title="never seen"),
            candidate(action="delete", title="delete with one session", items=[evidence("transcript", "s9")]),
        )

        self.assertEqual(
            sorted(self.titles(report["recommendations"])),
            ["add", "description contradicts the command", "models do this by default", "stale reference", "update with three sources"],
        )
        self.assertEqual(self.titles(report["obsolete"]), ["never seen"])
        self.assertEqual(sorted(self.titles(report["watching"])), ["delete with one session", "static add", "update with one PR counted twice"])
        self.assertEqual(report["counts"], {"add": 1, "update": 2, "delete": 2})
        self.assertEqual(report["coverage"], ["Comments on o/r#7 were cut at GitHub's per-page limit."])

    def test_refs_count_once_per_digest_and_unread_refs_are_dropped(self) -> None:
        report = self.report(
            candidate(title="one PR written four ways", items=[evidence("review", 4), evidence("review", "#4"), evidence("review", "PR 4"), evidence("review", "o/r#4")]),
            candidate(title="prefix and full id of one session plus a PR", items=[evidence("transcript", "01234567"), evidence("transcript", "0123456789abcdef"), evidence("review", 5)]),
            candidate(title="cites sessions nobody read", items=[evidence("transcript", "s1"), evidence("transcript", "ghost-1"), evidence("review", 99)]),
        )

        self.assertEqual(sorted(self.titles(report["watching"])), ["cites sessions nobody read", "one PR written four ways", "prefix and full id of one session plus a PR"])
        self.assertIn("2 evidence items cited a session or PR no collector read, and were dropped.", report["coverage"])

    def test_a_bare_number_resolves_only_when_one_repository_has_that_pr(self) -> None:
        write_json(self.run / "reviews/summary.json", {
            "repos": ["o/r", "o/s"], "window": {"start": "2026-11-01", "end": "2026-11-08"}, "pull_requests_scanned": 6,
            "pull_requests_with_comments": 6, "comments": 20, "truncated_pull_requests": [], "slices": [],
        })
        for ref in ("o/s/4", "o/s/9"):
            (self.run / f"reviews/prs/{ref}.md").parent.mkdir(parents=True, exist_ok=True)
            (self.run / f"reviews/prs/{ref}.md").write_text("digest")

        report = self.report(candidate(title="three PRs across two repositories", items=[
            evidence("review", "o/r#4"), evidence("review", "o/s#4"), evidence("review", 9), evidence("review", 4), evidence("review", "x/y#1"),
        ]))

        item = report["recommendations"][0]["files"][0]["items"][0]
        self.assertEqual([cited["ref"] for cited in item["evidence"]], ["o/r#4", "o/s#4", "o/s#9"])
        self.assertIn("2 evidence items cited a session or PR no collector read, and were dropped.", report["coverage"])
        self.assertEqual(render(report, "html").count("<title>r and s guidance retro</title>"), 1)

    def test_names_slices_no_miner_covered(self) -> None:
        write_json(self.run / "routed/summary.json", {"observations": {}, "unknown_guidance": [], "rejected": [], "missing_slices": ["t-3", "r-0"]})

        self.assertIn("No miner output for slices t-3, r-0, so their digests are not in this report.", self.report()["coverage"])

    def test_rejects_paths_outside_foundry_or_missing_for_update(self) -> None:
        for bad in (
            candidate(path="packages/review/.apm/skills/missing/SKILL.md"),
            candidate(action="add", path="packages/nonexistent/.apm/skills/x/SKILL.md"),
            candidate(action="add", path="README.md"),
            candidate(action="add", path="packages/review/../../AGENTS.md"),
            candidate(basis="judgement"),
        ):
            with self.subTest(candidate=bad), self.assertRaises(SystemExit):
                self.report(bad)

    def test_renders_both_formats_with_the_payload_and_title(self) -> None:
        quote = {"source": "review", "ref": 1, "url": "javascript:alert(1)", "quote": "<!--<script></script><script>alert(1)</script>"}
        report = self.report(candidate(items=[quote, evidence("review", 2), evidence("review", 3)]))
        cited = report["recommendations"][0]["files"][0]["items"][0]["evidence"][0]

        html = render(report, "html")
        canvas = render(report, "canvas")

        self.assertIn("<title>r guidance retro</title>", html)
        self.assertIsNone(cited["url"])
        self.assertNotIn("<!--<script", html)
        self.assertNotIn("</script><script>alert", html)
        self.assertNotIn("__REPORT_JSON__", html)
        self.assertIn('const TITLE = "r guidance retro";', canvas)
        self.assertIn('"repos": [\n    "o/r"\n  ]', canvas)


if __name__ == "__main__":
    unittest.main()
