---
phase: "pr-handbook"
state: "Verify"
changed_at: "2026-11-21T16:00:04Z"
session: "s-stack-phase-pr-handbook"
branch: "s-stack-phase-pr-handbook"
code_head: "391d9a86ba533c163608938dda6f2d881e5f8c41"
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

The phase plan is at `.foundry/plans/2026-11-20_21-37-12-s-stack/phases/pr-handbook.md`. Implement is complete. `2fbf1cd` added the handbook. `27785f0` added a merge check to the equality proof and corrected why `gh stack submit` is not used. `quick-review` then found four defects in the merge and binary handling, and `589411b` fixed them, with every scratch case rerun from the handbook's own commands. `391d9a8` reorders one sentence. The handbook is 185 lines. `s-stack-package` was merged at `e69b6ee`, bringing only `.foundry/` changes. The code head is `391d9a8`.

## Notes

- `quick-review` also asked to move the commands into script files. Declined, because the feature plan and roadmap `package.md` maintenance rule 6 put the equality proof in the handbook as commands.
- `SKILL.md` does not list `gh stack` among the tools s-stack needs. That file belongs to `foundation`.
