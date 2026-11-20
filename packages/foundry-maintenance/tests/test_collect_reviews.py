from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".apm/skills/guidance-retro/scripts"))

import collect_reviews  # noqa: E402
from collect_reviews import COUNT_QUERY, collect, gh_graphql, main, split_ranges  # noqa: E402
from digest import Window  # noqa: E402

START = datetime(2026, 11, 1, tzinfo=timezone.utc)
END = datetime(2026, 11, 9, tzinfo=timezone.utc)
WINDOW = Window(START, END)


def node(body: str, created: str = "2026-11-03T10:00:00Z", login: str = "reviewer", bot: bool = False, **extra: Any) -> dict:
    return {
        "author": {"login": login, "__typename": "Bot" if bot else "User"},
        "body": body,
        "createdAt": created,
        "url": f"https://github.com/o/r/pull/1#{len(body)}",
        **extra,
    }


def pr(number: int, comments: list[dict] | None = None, reviews: list[dict] | None = None, threads: list[list[dict]] | None = None, total_comments: int | None = None) -> dict:
    comments = comments or []
    return {
        "number": number,
        "title": f"PR {number}",
        "url": f"https://github.com/o/r/pull/{number}",
        "state": "MERGED",
        "author": {"login": "author"},
        "comments": {"totalCount": total_comments if total_comments is not None else len(comments), "nodes": comments},
        "reviews": {"totalCount": len(reviews or []), "nodes": reviews or []},
        "reviewThreads": {
            "totalCount": len(threads or []),
            "nodes": [{"comments": {"totalCount": len(thread), "nodes": thread}} for thread in threads or []],
        },
    }


class FakeGitHub:
    """Answers count queries from per-day PR counts, and page queries from a fixed PR list."""

    def __init__(self, prs_per_day: dict[int, int], prs: list[dict], page_size: int = 1) -> None:
        self.prs_per_day = prs_per_day
        self.prs = prs
        self.page_size = page_size

    def __call__(self, query: str, variables: dict[str, str]) -> dict[str, Any]:
        span = variables["q"].split("updated:")[1]
        start, end = (datetime.strptime(part, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc) for part in span.split(".."))
        if query == COUNT_QUERY:
            count = sum(n for day, n in self.prs_per_day.items() if start <= datetime(2026, 11, day, 12, tzinfo=timezone.utc) < end)
            return {"search": {"issueCount": count}}
        start_at = int(variables.get("cursor", "0"))
        end_at = start_at + self.page_size
        more = end_at < len(self.prs)
        return {"search": {"pageInfo": {"hasNextPage": more, "endCursor": str(end_at) if more else None}, "nodes": self.prs[start_at:end_at]}}


class SplitRangesTests(unittest.TestCase):
    def test_splits_until_every_range_is_under_the_search_cap(self) -> None:
        middle = datetime(2026, 11, 5, tzinfo=timezone.utc)

        self.assertEqual(split_ranges("o/r", START, END, FakeGitHub({2: 900, 5: 900}, [])), [(START, middle), (middle, END)])

    def test_one_range_when_under_the_cap_and_none_when_empty(self) -> None:
        self.assertEqual(split_ranges("o/r", START, END, FakeGitHub({3: 10}, [])), [(START, END)])
        self.assertEqual(split_ranges("o/r", START, END, FakeGitHub({}, [])), [])


class CollectReviewsTests(unittest.TestCase):
    def test_keeps_window_comments_of_every_kind_and_cleans_html(self) -> None:
        bugbot = "<!-- BUGBOT -->\n<picture><img src=x></picture>\n### Leak\n\nUse `List<int>` here.<sup>footer</sup>"
        prs = [
            pr(
                1,
                comments=[node("Please split this PR"), node("old", created="2026-10-01T00:00:00Z"), node("   ")],
                reviews=[node(bugbot, login="cursor", bot=True, state="COMMENTED")],
                threads=[[node("Missing test", path="a.py", line=3)]],
            ),
            pr(2, comments=[node("too early", created="2026-10-30T00:00:00Z")]),
        ]
        out = Path(tempfile.mkdtemp())

        summary = collect(["o/r"], WINDOW, out, 250_000, FakeGitHub({3: 2}, prs))

        digest = (out / "prs/o/r/1.md").read_text()
        self.assertIn("conversation comment by reviewer (user)", digest)
        self.assertIn("review (commented) by cursor (bot)", digest)
        self.assertIn("inline comment by reviewer (user), 2026-11-03T10:00:00Z on `a.py:3`", digest)
        self.assertIn("Use `List<int>` here.footer", digest)
        self.assertNotIn("BUGBOT", digest)
        self.assertNotIn("<picture>", digest)
        self.assertNotIn("old", digest)
        self.assertIn("- ref: o/r#1", digest)
        self.assertFalse((out / "prs/o/r/2.md").exists())
        self.assertEqual(summary["pull_requests_scanned"], 2)
        self.assertEqual(summary["pull_requests_with_comments"], 1)
        self.assertEqual(summary["comments"], 3)
        self.assertEqual(summary["slices"], [["prs/o/r/1.md"]])

    def test_records_prs_whose_comment_lists_were_cut_short(self) -> None:
        prs = [pr(7, comments=[node("one")], total_comments=150)]

        summary = collect(["o/r"], WINDOW, Path(tempfile.mkdtemp()), 250_000, FakeGitHub({3: 1}, prs))

        self.assertEqual(summary["truncated_pull_requests"], ["o/r#7"])

    def test_keeps_prs_of_several_repositories_apart_when_their_numbers_collide(self) -> None:
        servers = {"o/a": FakeGitHub({3: 1}, [pr(1, comments=[node("from a")])]), "o/b": FakeGitHub({3: 1}, [pr(1, comments=[node("from b")])])}

        def graphql(query: str, variables: dict[str, str]) -> dict[str, Any]:
            return servers[variables["q"].split()[0].removeprefix("repo:")](query, variables)

        out = Path(tempfile.mkdtemp())
        summary = collect(["o/a", "o/b"], WINDOW, out, 250_000, graphql)

        self.assertIn("from a", (out / "prs/o/a/1.md").read_text())
        self.assertIn("from b", (out / "prs/o/b/1.md").read_text())
        self.assertEqual(summary["repos"], ["o/a", "o/b"])
        self.assertEqual(summary["pull_requests_with_comments"], 2)

    def test_rejects_a_repository_that_is_not_owner_slash_name(self) -> None:
        for bad in ("../etc", "o/../x", "just-a-name", "o/r/extra"):
            with self.subTest(repo=bad), self.assertRaises(SystemExit), mock.patch("sys.stderr"):
                main(["--repo", bad, "--since", "2026-11-01", "--out", tempfile.mkdtemp()])


class GhGraphqlTests(unittest.TestCase):
    @staticmethod
    def completed(returncode: int, stdout: str = "", stderr: str = "") -> subprocess.CompletedProcess:
        return subprocess.CompletedProcess([], returncode, stdout, stderr)

    def test_retries_a_server_timeout_then_returns_the_data(self) -> None:
        answers = [self.completed(1, stderr="gh: HTTP 502"), self.completed(0, stdout='{"data": {"ok": true}}')]
        with mock.patch.object(collect_reviews.subprocess, "run", side_effect=answers), mock.patch.object(collect_reviews.time, "sleep") as sleep:
            self.assertEqual(gh_graphql("query", {}), {"ok": True})
        sleep.assert_called_once()

    def test_fails_at_once_on_any_other_error(self) -> None:
        with mock.patch.object(collect_reviews.subprocess, "run", return_value=self.completed(1, stderr="gh: HTTP 401")) as run, mock.patch.object(collect_reviews.time, "sleep"):
            with self.assertRaises(SystemExit):
                gh_graphql("query", {})
        self.assertEqual(run.call_count, 1)


if __name__ == "__main__":
    unittest.main()
