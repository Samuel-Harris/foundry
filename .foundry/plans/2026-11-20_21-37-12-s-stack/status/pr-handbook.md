---
phase: "pr-handbook"
state: "Implement"
changed_at: "2026-11-21T16:48:29Z"
session: "s-stack-phase-pr-handbook"
branch: "s-stack-phase-pr-handbook"
code_head: "412a91d852ac3d59e38fa95a6aa366d5e59a3e91"
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
  - gate: "verify"
    result: "NOT VERIFIED"
    code_head: "d7efc941b0d361189e023ccb4846dfca78c5c186"
    at: "2026-11-21T16:31:44Z"
    evidence: ".foundry/plans/2026-11-20_21-37-12-s-stack/status/pr-handbook-evidence.md"
  - gate: "verify"
    result: "VERIFIED"
    code_head: "412a91d852ac3d59e38fa95a6aa366d5e59a3e91"
    at: "2026-11-21T16:38:32Z"
    evidence: ".foundry/plans/2026-11-20_21-37-12-s-stack/status/pr-handbook-evidence.md"
  - gate: "review"
    result: "SIGNIFICANT"
    code_head: "412a91d852ac3d59e38fa95a6aa366d5e59a3e91"
    at: "2026-11-21T16:48:29Z"
    evidence: ".foundry/plans/2026-11-20_21-37-12-s-stack/status/pr-handbook-evidence.md"
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
  - id: "pr-handbook-d5"
    decision: "From the orchestrator: a CLEAR review moves the phase straight to PR. Minor findings go to the evidence file, and only a finding that would mislead a reader or break a real run is fixed, which means a new code head and both gates again."
    door: "two-way"
    at: "2026-11-21T16:09:22Z"
  - id: "pr-handbook-d6"
    decision: "Answer to pr-handbook-r1 from the orchestrator, option A. A pull request branch is refreshed by replaying its own commits with git apply --3way onto its base (the parent's branch when stacked, else origin/<default> with open dependencies merged), recorded as one merge commit with git commit-tree -p HEAD -p <base>, then the regenerate commit. The per-pull-request tree check replaces the merge-tree -X ours check, the squash-step heuristics are deleted with no fallback, each of the six Review findings becomes a check-file case, and the guarantees stay: no force-push, the default tip is an ancestor of the head, at most one merge and one regenerate commit per round, and an up-to-date round changes nothing."
    door: "two-way"
    at: "2026-11-21T16:49:18Z"
---

# Phase `pr-handbook` status

The phase plan is at `.foundry/plans/2026-11-20_21-37-12-s-stack/phases/pr-handbook.md`. Implement is complete. `2fbf1cd` added the handbook. `27785f0` added a merge check to the equality proof and corrected why `gh stack submit` is not used. `quick-review` then found four defects in the merge and binary handling, and `589411b` fixed them, with every scratch case rerun from the handbook's own commands. `391d9a8` reorders one sentence. The handbook is 185 lines. `s-stack-package` was merged at `e69b6ee`, bringing only `.foundry/` changes. The first Verify gate returned NOT VERIFIED at `a42cd47`, the verifier's check-file commit: `git diff-tree --quiet` without `-r` breaks the carry loop and the proof on a commit that changes only a nested lockfile. `f66ec2c` adds `-r` to both checks, and the check file's Rerun block then printed `0 failed`. The second Verify gate returned NOT VERIFIED at `e5f37b8`, the verifier's extended check file: an add/add conflict on a squash-merged parent's new `apm.yml` stages an empty file, and the proof is path-relative when run from a subdirectory. `3b89160` fixes both: the merge procedure uses the empty blob as a missing base and aborts when a resolution fails, and the parameter block moves to the repository root. The check file's 15 Rerun cases then printed `0 failed`, and the proof run from a subdirectory failed a dropped root-level file. The code head is `3b89160`, and Verify started again, but the third verifier was stopped before any verdict, because the orchestrator asked for idempotent generated-only fix rounds, which means a new code head. `d17dd6b` makes those rounds idempotent. A round on a branch that already contains the default branch's tip changes nothing, and a round after a further move adds one merge and at most one new regenerate commit. A scratch run of three rounds confirmed both, with the proof `EQUAL` each time. `s-stack-package` was merged at `40334e4` after `spec-planner-handbooks` merged. The only conflict was the lockfile, which was regenerated. The fourth Verify gate returned NOT VERIFIED at `d7efc94`: a later generated-only round reapplies the squash step and drops a newer default-branch change, and an interrupted round cannot resume. `25e6ef4` fixes both. The squash step runs only while the branch's merge base with the merged branch is in the parent's history, and an up-to-date round skips only its merge. The check file's 22 Rerun cases then printed `0 failed`, and a round interrupted after its merge finished on the next one. The fifth Verify gate returned VERIFIED at `412a91d`, the verifier's check-file commit on top of `25e6ef4`. It raised one finding that misleads a reader and three minor ones, carried to a fix round after Review so that both gates run once more over one combined fix. The first Review gate returned SIGNIFICANT at `412a91d`. Six of its findings break a real run, and all come from merging the default branch and repairing conflicts by heuristic. Request `pr-handbook-r1` asks to replace that with a rebuild. The phase is back in Implement, and the orchestrator answered option A (`pr-handbook-d6`).

## Notes

- `quick-review` also asked to move the commands into script files. Declined, because the feature plan and roadmap `package.md` maintenance rule 6 put the equality proof in the handbook as commands.
- `SKILL.md` does not list `gh stack` among the tools s-stack needs. That file belongs to `foundation`.
