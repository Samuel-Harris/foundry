---
phase: "foundation"
state: "Review"
changed_at: "2026-11-21T14:57:22Z"
session: "s-stack-phase-foundation"
branch: "s-stack-phase-foundation"
code_head: "b27c4f18e17a1e0492274a936810619ab28a708c"
waits_for: null
verdicts:
  - gate: "verify"
    result: "NOT VERIFIED"
    code_head: "13f835b7a61f0f3287cdd307b712338ae8751cde"
    at: "2026-11-21T14:26:36Z"
    evidence: ".foundry/plans/2026-11-20_21-37-12-s-stack/status/foundation-evidence.md"
  - gate: "verify"
    result: "VERIFIED"
    code_head: "0f4bf86be72cef85833be3096e3cbf9fc85b59ff"
    at: "2026-11-21T14:35:16Z"
    evidence: ".foundry/plans/2026-11-20_21-37-12-s-stack/status/foundation-evidence.md"
  - gate: "review"
    result: "SIGNIFICANT"
    code_head: "0f4bf86be72cef85833be3096e3cbf9fc85b59ff"
    at: "2026-11-21T14:48:05Z"
    evidence: ".foundry/plans/2026-11-20_21-37-12-s-stack/status/foundation-evidence.md"
  - gate: "verify"
    result: "VERIFIED"
    code_head: "b27c4f18e17a1e0492274a936810619ab28a708c"
    at: "2026-11-21T14:57:22Z"
    evidence: ".foundry/plans/2026-11-20_21-37-12-s-stack/status/foundation-evidence.md"
pull_requests: []
requests: []
decisions:
  - id: "foundation-d1"
    decision: "Answer to foundation-r1, option A, from the orchestrator. The shipped references/status-and-messages.md states the general code-head rule (only .foundry/ excluded, a feature plan may name generated paths that also move no code head) and uses <id>, <feature> and <phase> placeholders. Every other part of C2 is copied unchanged."
    door: "two-way"
    at: "2026-11-21T14:05:00Z"
  - id: "foundation-d2"
    decision: "Answer to foundation-r2 from the orchestrator, outcome option A. json.dumps with ensure_ascii=False round-trips emoji, accented letters, colons, backslashes and U+0001 through PyYAML, but PyYAML rejects DEL (U+007F) and reads NEL (U+0085) as a space. So the reference keeps characters outside the Basic Multilingual Plane out of header strings, and the C2 check allows that sentence."
    door: "two-way"
    at: "2026-11-21T14:51:35Z"
---

# Phase `foundation` status

The phase plan is at `.foundry/plans/2026-11-20_21-37-12-s-stack/phases/foundation.md`. The first Verify gate returned NOT VERIFIED: the shipped reference added an append-only evidence rule that C2 and foundation-d1 do not allow. The fix, 0eba66d, removes it. The second Verify gate returned VERIFIED at 0f4bf86, the verifier's commit that adds a C2 conformance check. The first Review gate returned SIGNIFICANT at 0f4bf86. The fix round (ce16529, c68877a, b27c4f1) repaired the verification files and added the foundation-d2 sentence. s-stack-package was merged at 5b346fa. The third Verify gate returned VERIFIED at b27c4f1. The Review gate covers the commits since 0f4bf86.

## Notes

- `docs/COMPATIBILITY.md` line 126 says "The nine dependency-bearing packages use the sibling `path:` form". Six do. This predates the phase and is outside its change. The phase corrected the same wrong list in `docs/DEPENDENCY-CONTRACTS.md` line 74, which it edits.
