---
phase: "pr-handbook"
state: "Implement"
changed_at: "2026-11-21T15:41:21Z"
session: "s-stack-phase-pr-handbook"
branch: "s-stack-phase-pr-handbook"
code_head: "50e26eebaa31524a81e0cc00d99edf4bdad0e2dc"
waits_for: null
verdicts: []
pull_requests: []
requests: []
decisions:
  - id: "pr-handbook-d1"
    decision: "The PR creator reads ../summarise-pr/SKILL.md relative to the sam-mode skill directory and follows it, because summarise-pr sets disable-model-invocation: true."
    door: "two-way"
    at: "2026-11-21T15:41:21Z"
  - id: "pr-handbook-d2"
    decision: "The handbook uses only git push without force, gh pr create --draft, gh pr edit --base and gh stack link with pull request numbers. gh stack sync, rebase and push force-push with lease, and gh stack submit opens ready pull requests in its editor."
    door: "two-way"
    at: "2026-11-21T15:41:21Z"
  - id: "pr-handbook-d3"
    decision: "The equality proof collects every failure and prints one verdict, EQUAL with exit 0 or NOT EQUAL with exit 1, instead of Experiment 7's must-print-nothing lines."
    door: "two-way"
    at: "2026-11-21T15:41:21Z"
  - id: "pr-handbook-d4"
    decision: "Every multi-line handbook command runs under bash -s, because the agent shell is zsh, which does not word-split an unquoted command substitution."
    door: "two-way"
    at: "2026-11-21T15:41:21Z"
---

# Phase `pr-handbook` status

The session started on `s-stack-phase-pr-handbook`, cut from `s-stack-package` at `42c54ee`. The phase plan is committed at `780fa00`, at `.foundry/plans/2026-11-20_21-37-12-s-stack/phases/pr-handbook.md`. The equality proof it carries was prototyped in a scratch repository, and every case gave the result the feature plan's **Done when** list expects. The code head is still `foundation`'s, inherited from the orchestrator branch.
