---
phase: "pr-handbook"
state: "Implement"
changed_at: "2026-11-21T16:18:40Z"
session: "s-stack-phase-pr-handbook"
branch: "s-stack-phase-pr-handbook"
code_head: "e5f37b81960b7fc447e65ab7cf06bf282db462f4"
waits_for: null
verdicts:
  - gate: "verify"
    result: "NOT VERIFIED"
    code_head: "a42cd47ca1eb9cbcfc5dc51e6b608b4864b31d22"
    at: "2026-11-21T16:09:22Z"
    evidence: ".foundry/plans/2026-11-20_21-37-12-s-stack/status/pr-handbook-evidence.md"
  - gate: "verify"
    result: "NOT VERIFIED"
    code_head: "e5f37b81960b7fc447e65ab7cf06bf282db462f4"
    at: "2026-11-21T16:18:40Z"
    evidence: ".foundry/plans/2026-11-20_21-37-12-s-stack/status/pr-handbook-evidence.md"
pull_requests: []
requests: []
decisions:
  - id: "pr-handbook-d5"
    decision: "From the orchestrator: a CLEAR review moves the phase straight to PR. Minor findings go to the evidence file, and only a finding that would mislead a reader or break a real run is fixed, which means a new code head and both gates again."
    door: "two-way"
    at: "2026-11-21T16:09:22Z"
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

The phase plan is at `.foundry/plans/2026-11-20_21-37-12-s-stack/phases/pr-handbook.md`. Implement is complete. `2fbf1cd` added the handbook. `27785f0` added a merge check to the equality proof and corrected why `gh stack submit` is not used. `quick-review` then found four defects in the merge and binary handling, and `589411b` fixed them, with every scratch case rerun from the handbook's own commands. `391d9a8` reorders one sentence. The handbook is 185 lines. `s-stack-package` was merged at `e69b6ee`, bringing only `.foundry/` changes. The first Verify gate returned NOT VERIFIED at `a42cd47`, the verifier's check-file commit: `git diff-tree --quiet` without `-r` breaks the carry loop and the proof on a commit that changes only a nested lockfile. `f66ec2c` adds `-r` to both checks, and the check file's Rerun block then printed `0 failed`. The second Verify gate returned NOT VERIFIED at `e5f37b8`, the verifier's extended check file: an add/add conflict on a squash-merged parent's new `apm.yml` stages an empty file, and the proof is path-relative when run from a subdirectory. The phase is back in Implement for both.

## Notes

- `quick-review` also asked to move the commands into script files. Declined, because the feature plan and roadmap `package.md` maintenance rule 6 put the equality proof in the handbook as commands.
- `SKILL.md` does not list `gh stack` among the tools s-stack needs. That file belongs to `foundation`.
