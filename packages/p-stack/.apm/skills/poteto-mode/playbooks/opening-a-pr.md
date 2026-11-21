### Opening a PR

Invoked at the end of every other playbook.

Work from a git worktree off trunk, and keep unrelated work out of it. Rebase into small, landable commits. Run `/deslop` from `cursor-team-kit` over the diff before commit (without that plugin, ask for the same cleanup in plain words: remove narrating comments, unsupported guards, dead compatibility paths, and unrelated edits).

Title: `type(scope): subject`, naming a real symbol when one carries the change. Body: a one-minute briefing under 40 lines with these `##` headings in order, dropping empty ones: `## Why`, `## What changed`, `## Scope`, `## Tradeoffs` (only rejected alternatives a reviewer would otherwise ask about), `## Blast Radius`, `## Verification`.

Before you post, check each claim in the body against the diff and test output: every named function, file, count, PR number and scope statement must match what the branch holds. Leave out a number or link you have not looked up, and say what the tests do not cover.

Stack follow-ups by base branch. Open PRs ready, through the run's built-in PR tool with `draft: false` when the host offers one. Without one, use `gh pr create` without `--draft`, or `origin pr create --status open` when Origin's CLI resolves the repository. Opening a PR does not start a babysit.
