#!/usr/bin/env python3
"""Digest the review comments left on a GitHub repository's pull requests in a window.

Searches every PR updated in the window through `gh api graphql`, splitting the
window until each search stays under GitHub's 1,000-result cap, and keeps the
conversation comments, review bodies and inline review comments created inside
it. Writes one Markdown digest per PR with comments to OUT/prs/ and
OUT/summary.json, whose `slices` list batches the digests for miner subagents.

Usage:
    collect_reviews.py --repo owner/name --since 2026-10-21 --out RUN/reviews
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

from digest import Window, add_window_args, pack_slices, print_summary, truncate, write_summary

GraphQL = Callable[[str, dict[str, str]], dict[str, Any]]

SEARCH_CAP = 1000
PAGE_SIZE = 25
COMMENT_LIMIT = 2500
RETRIES = 3
SERVER_TIMEOUT = re.compile(r"HTTP 50[24]")
HTML_NOISE = re.compile(
    r"<!--.*?-->|<picture>.*?</picture>|</?(?:a|b|br|code|details|div|em|h\d|i|img|kbd|p|pre|source|span|strong|sub|summary|sup|table|tbody|td|th|thead|tr)\b[^>]*>",
    re.DOTALL | re.IGNORECASE,
)
BLANK_RUN = re.compile(r"\n{3,}")

COUNT_QUERY = """
query($q: String!) { search(query: $q, type: ISSUE, first: 1) { issueCount } }
"""

PAGE_QUERY = """
query($q: String!, $cursor: String) {
  search(query: $q, type: ISSUE, first: %d, after: $cursor) {
    pageInfo { hasNextPage endCursor }
    nodes {
      ... on PullRequest {
        number title url state
        author { login }
        comments(last: 100) {
          totalCount
          nodes { author { login __typename } body createdAt url }
        }
        reviews(last: 50) {
          totalCount
          nodes { author { login __typename } body createdAt url state }
        }
        reviewThreads(last: 100) {
          totalCount
          nodes {
            comments(last: 50) {
              totalCount
              nodes { author { login __typename } body createdAt url path line }
            }
          }
        }
      }
    }
  }
}
""" % PAGE_SIZE


@dataclass(frozen=True)
class Comment:
    kind: str
    author: str
    is_bot: bool
    created: str
    url: str
    body: str
    location: str | None

    def render(self) -> str:
        where = f" on `{self.location}`" if self.location else ""
        role = "bot" if self.is_bot else "user"
        return f"### {self.kind} by {self.author} ({role}), {self.created}{where}\n\n{self.url}\n\n{truncate(self.body, COMMENT_LIMIT)}\n"


def clean_body(body: str) -> str:
    return BLANK_RUN.sub("\n\n", HTML_NOISE.sub("", body)).strip()


def gh_graphql(query: str, variables: dict[str, str]) -> dict[str, Any]:
    command = ["gh", "api", "graphql", "-f", f"query={query}"]
    for key, value in variables.items():
        command += ["-f", f"{key}={value}"]
    for attempt in range(RETRIES + 1):
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        if result.returncode == 0:
            return json.loads(result.stdout)["data"]
        # GitHub answers 502 or 504 when a nested query runs past its server-side time limit.
        if attempt == RETRIES or not SERVER_TIMEOUT.search(result.stderr):
            break
        time.sleep(5 * 2**attempt)
    raise SystemExit(f"gh api graphql failed: {result.stderr.strip()}")


def search_query(repo: str, start: datetime, end: datetime) -> str:
    stamp = "%Y-%m-%dT%H:%M:%SZ"
    return f"repo:{repo} is:pr updated:{start.strftime(stamp)}..{end.strftime(stamp)}"


def split_ranges(repo: str, start: datetime, end: datetime, graphql: GraphQL) -> list[tuple[datetime, datetime]]:
    """Halve [start, end) until each part's search returns at most SEARCH_CAP PRs."""
    count = graphql(COUNT_QUERY, {"q": search_query(repo, start, end)})["search"]["issueCount"]
    if count <= SEARCH_CAP or end - start <= timedelta(minutes=1):
        return [(start, end)] if count else []
    middle = start + (end - start) / 2
    return split_ranges(repo, start, middle, graphql) + split_ranges(repo, middle, end, graphql)


def author_of(node: dict[str, Any]) -> tuple[str, bool]:
    author = node.get("author") or {}
    return author.get("login") or "ghost", author.get("__typename") == "Bot"


def comments_in(pr: dict[str, Any], window: Window) -> tuple[list[Comment], bool]:
    """Return the PR's non-empty comments created in the window, and whether any list was cut short."""
    found: list[tuple[str, dict[str, Any], str | None]] = []
    found += [("conversation comment", node, None) for node in pr["comments"]["nodes"]]
    found += [(f"review ({node['state'].lower()})", node, None) for node in pr["reviews"]["nodes"]]
    truncated = pr["comments"]["totalCount"] > len(pr["comments"]["nodes"])
    truncated |= pr["reviews"]["totalCount"] > len(pr["reviews"]["nodes"])
    truncated |= pr["reviewThreads"]["totalCount"] > len(pr["reviewThreads"]["nodes"])
    for thread in pr["reviewThreads"]["nodes"]:
        thread_comments = thread["comments"]
        truncated |= thread_comments["totalCount"] > len(thread_comments["nodes"])
        for node in thread_comments["nodes"]:
            location = f"{node['path']}:{node['line']}" if node.get("line") else node.get("path")
            found.append(("inline comment", node, location))

    comments = []
    for kind, node, location in found:
        created = datetime.fromisoformat(node["createdAt"].replace("Z", "+00:00"))
        body = clean_body(node["body"])
        if not body or not window.contains(created):
            continue
        author, is_bot = author_of(node)
        comments.append(Comment(kind, author, is_bot, node["createdAt"], node["url"], body, location))
    comments.sort(key=lambda comment: comment.created)
    return comments, truncated


def render_pr(pr: dict[str, Any], comments: list[Comment]) -> str:
    author, _ = author_of(pr)
    header = f"# PR #{pr['number']}: {pr['title']}\n\n- url: {pr['url']}\n- author: {author}\n- state: {pr['state'].lower()}\n"
    return "\n".join([header, *(comment.render() for comment in comments)])


def fetch_prs(repo: str, window: Window, graphql: GraphQL) -> list[dict[str, Any]]:
    prs: dict[int, dict[str, Any]] = {}
    # `updated` is a PR's latest activity, so a PR reviewed in the window and touched after it is found only by searching to now.
    for start, end in split_ranges(repo, window.start, max(window.end, datetime.now(timezone.utc)), graphql):
        variables = {"q": search_query(repo, start, end)}
        while True:
            search = graphql(PAGE_QUERY, variables)["search"]
            for node in search["nodes"]:
                if node:
                    prs[node["number"]] = node
            if not search["pageInfo"]["hasNextPage"]:
                break
            variables = {**variables, "cursor": search["pageInfo"]["endCursor"]}
    return [prs[number] for number in sorted(prs)]


def collect(repo: str, window: Window, out: Path, slice_chars: int, graphql: GraphQL) -> dict[str, Any]:
    prs_dir = out / "prs"
    prs_dir.mkdir(parents=True, exist_ok=True)
    prs = fetch_prs(repo, window, graphql)
    digests: list[tuple[str, int]] = []
    comment_count = 0
    truncated: list[int] = []
    for pr in prs:
        comments, cut_short = comments_in(pr, window)
        if cut_short:
            truncated.append(pr["number"])
        if not comments:
            continue
        text = truncate(render_pr(pr, comments), slice_chars)
        relative = f"prs/{pr['number']}.md"
        (out / relative).write_text(text + "\n", encoding="utf-8")
        digests.append((relative, len(text)))
        comment_count += len(comments)
    summary = {
        "repo": repo,
        "window": window.to_dict(),
        "pull_requests_scanned": len(prs),
        "pull_requests_with_comments": len(digests),
        "comments": comment_count,
        "truncated_pull_requests": truncated,
        "slices": pack_slices(digests, slice_chars),
    }
    write_summary(out, summary)
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", required=True, help="owner/name")
    add_window_args(parser)
    args = parser.parse_args(argv)
    summary = collect(args.repo, Window.parse(args.since, args.until), args.out, args.slice_chars, gh_graphql)
    print_summary(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
