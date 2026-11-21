---
phase: "phase-handbooks"
state: "Implement"
changed_at: "2026-11-21T17:27:50Z"
session: "s-stack-phase-phase-handbooks"
branch: "s-stack-phase-phase-handbooks"
code_head: "c666afdc929b1e05e49decda745d79b469f0333f"
waits_for: null
verdicts:
  - gate: "verify"
    result: "NOT VERIFIED"
    code_head: "a1c1d834802eae04624ad74e52e6acc198a49bf6"
    at: "2026-11-21T15:54:08Z"
    evidence: ".foundry/plans/2026-11-20_21-37-12-s-stack/status/phase-handbooks-evidence.md"
  - gate: "verify"
    result: "VERIFIED"
    code_head: "305a26e4a846d378d2dac65faa47909405a36865"
    at: "2026-11-21T15:59:49Z"
    evidence: ".foundry/plans/2026-11-20_21-37-12-s-stack/status/phase-handbooks-evidence.md"
  - gate: "review"
    result: "SIGNIFICANT"
    code_head: "305a26e4a846d378d2dac65faa47909405a36865"
    at: "2026-11-21T16:07:41Z"
    evidence: ".foundry/plans/2026-11-20_21-37-12-s-stack/status/phase-handbooks-evidence.md"
  - gate: "verify"
    result: "VERIFIED"
    code_head: "6758c7df2ea497bdc5536dd704c5a49656dbb4f3"
    at: "2026-11-21T16:18:44Z"
    evidence: ".foundry/plans/2026-11-20_21-37-12-s-stack/status/phase-handbooks-evidence.md"
  - gate: "review"
    result: "SIGNIFICANT"
    code_head: "6758c7df2ea497bdc5536dd704c5a49656dbb4f3"
    at: "2026-11-21T16:23:40Z"
    evidence: ".foundry/plans/2026-11-20_21-37-12-s-stack/status/phase-handbooks-evidence.md"
  - gate: "verify"
    result: "VERIFIED"
    code_head: "d32a56ae3096f5df29e5608aa6b6c146183c7dd6"
    at: "2026-11-21T16:31:38Z"
    evidence: ".foundry/plans/2026-11-20_21-37-12-s-stack/status/phase-handbooks-evidence.md"
  - gate: "review"
    result: "SIGNIFICANT"
    code_head: "d32a56ae3096f5df29e5608aa6b6c146183c7dd6"
    at: "2026-11-21T16:37:03Z"
    evidence: ".foundry/plans/2026-11-20_21-37-12-s-stack/status/phase-handbooks-evidence.md"
  - gate: "verify"
    result: "VERIFIED"
    code_head: "691ea624c93b5dbf1e8f33cd9b9dc1021d38308c"
    at: "2026-11-21T16:43:43Z"
    evidence: ".foundry/plans/2026-11-20_21-37-12-s-stack/status/phase-handbooks-evidence.md"
  - gate: "review"
    result: "SIGNIFICANT"
    code_head: "691ea624c93b5dbf1e8f33cd9b9dc1021d38308c"
    at: "2026-11-21T16:48:26Z"
    evidence: ".foundry/plans/2026-11-20_21-37-12-s-stack/status/phase-handbooks-evidence.md"
  - gate: "verify"
    result: "VERIFIED"
    code_head: "c666afdc929b1e05e49decda745d79b469f0333f"
    at: "2026-11-21T16:54:17Z"
    evidence: ".foundry/plans/2026-11-20_21-37-12-s-stack/status/phase-handbooks-evidence.md"
  - gate: "review"
    result: "CLEAR"
    code_head: "c666afdc929b1e05e49decda745d79b469f0333f"
    at: "2026-11-21T16:58:22Z"
    evidence: ".foundry/plans/2026-11-20_21-37-12-s-stack/status/phase-handbooks-evidence.md"
pull_requests:
  - number: 85
    branch: "s-stack-phase-handbooks"
    base: "s-stack-verify-skill"
    depends_on: [82]
    stacked: true
requests: []
decisions:
  - id: "phase-handbooks-d1"
    decision: "verifier.md makes checks/<phase>.md beside the verification skill's SKILL.md, with ## Rerun and ## Evidence sections, the general s-stack rule."
    door: "two-way"
    at: "2026-11-21T15:37:46Z"
  - id: "phase-handbooks-d2"
    decision: "One pull request carries the three handbooks and the phase's check file."
    door: "two-way"
    at: "2026-11-21T15:37:46Z"
  - id: "phase-handbooks-d3"
    decision: "The reviewers' intent is stated from commit messages and the code alone, never from the roadmap or a plan."
    door: "two-way"
    at: "2026-11-21T15:37:46Z"
---

# Phase `phase-handbooks` status

The phase plan is at `.foundry/plans/2026-11-20_21-37-12-s-stack/phases/phase-handbooks.md`. Handbooks committed at 89293d5, 0a15039 and 5f4b1c6. The quick-review pass (bug and code quality) found duplication of SKILL.md and the reference file, a re-review that never re-ran earlier significant findings, a re-review scope that pulled in other phases' code after a merge, and a restart check against the wrong field. Fix 1e49d2e addresses them and the orchestrator's instruction about the fix-round, move-back and stop cases. s-stack-package merged at 25ec3ab, which brought only .foundry/ files, so the code head stays 1e49d2e. The first Verify gate returned NOT VERIFIED at a1c1d83, the verifier's check-file commit: phase-session.md never says to follow a direct instruction from the developer. Back to Implement to fix it.
Fix 305a26e says the session follows a direct instruction and builds what an open request cannot change, and gives the verifier a verdict for a skill without the check-file step. s-stack-package merged again (only .foundry/ came in). The second Verify gate returned VERIFIED at 305a26e. The first Review gate returned SIGNIFICANT at 305a26e, with four findings in verifier.md, reviewer.md and phase-session.md. Back to Implement.
Fix 6b60476 addresses the four significant review findings. s-stack-package merged at d88dfe0 (only .foundry/). The third Verify gate returned VERIFIED at 6758c7d, the verifier's evidence commit. The second Review gate returned SIGNIFICANT at 6758c7d, with three findings. Back to Implement, with the orchestrator's merge-orchestrator-branch request for spec-planner-handbooks taken in the same round.
Fix 73b5410 addresses the three findings of the second review. s-stack-package merged at cddb4b0 with the C7 procedure; it brought spec-planner-handbooks (planner.md, spec-writer.md, their check file) and a lockfile-only conflict, resolved by regenerating. The merge moved the code head to cddb4b0. The fourth Verify gate returned VERIFIED at d32a56a. The third Review gate returned SIGNIFICANT at d32a56a: a stale expected answer in the check file and a Verdicts sentence in phase-session.md. Back to Implement.
Fix e592b60 addresses the third review's handbook findings. The stale expected answer in the check file goes to the next verifier. s-stack-package merged again (only .foundry/).
The fifth verifier was stopped before it committed, on the orchestrator's instruction to remove the evidence-only exception. Commit 691ea62 removes it: the check file holds only checks, and results go in this phase's evidence file. Verification restarts at the new code head. The sixth Verify gate returned VERIFIED at 691ea62. The fourth Review gate returned SIGNIFICANT at 691ea62: whether a phase's own one-off checks rerun at a new code head, and a cold-read prompt that does not ask what its expected answer requires.
Fix c666afd: the phase's own verifier runs its one-off checks at every code head it verifies, and cold read 2 asks what its expected answer requires. s-stack-package merged at 161c7c7 (only .foundry/). The seventh Verify gate returned VERIFIED at c666afd. The fifth Review gate returned CLEAR at c666afd. Both verdicts cover c666afd. Draft pull request 85 is open, stacked on #82 in GitHub stack 83, and the equality proof shows it holds exactly the verified phase diff.
Fix round from the orchestrator: phase-session.md still told the PR creator to merge the default branch into pull request branches (replaced by run decision pr-handbook-r1's rebuild) and kept a restack row (replaced by automatic stacking). Back to Implement.
