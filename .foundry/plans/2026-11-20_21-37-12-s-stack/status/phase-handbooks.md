---
phase: "phase-handbooks"
state: "Implement"
changed_at: "2026-11-21T15:54:08Z"
session: "s-stack-phase-phase-handbooks"
branch: "s-stack-phase-phase-handbooks"
code_head: "a1c1d834802eae04624ad74e52e6acc198a49bf6"
waits_for: null
verdicts:
  - gate: "verify"
    result: "NOT VERIFIED"
    code_head: "a1c1d834802eae04624ad74e52e6acc198a49bf6"
    at: "2026-11-21T15:54:08Z"
    evidence: ".foundry/plans/2026-11-20_21-37-12-s-stack/status/phase-handbooks-evidence.md"
pull_requests: []
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
