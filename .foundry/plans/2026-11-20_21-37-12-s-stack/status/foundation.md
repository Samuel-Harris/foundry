---
phase: "foundation"
state: "Verify"
changed_at: "2026-11-21T23:37:38Z"
session: "s-stack-phase-foundation"
branch: "s-stack-phase-foundation"
code_head: "98999eef74b7d80f3c83160ef8fa4b439790c2aa"
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
  - gate: "review"
    result: "SIGNIFICANT"
    code_head: "b27c4f18e17a1e0492274a936810619ab28a708c"
    at: "2026-11-21T15:04:05Z"
    evidence: ".foundry/plans/2026-11-20_21-37-12-s-stack/status/foundation-evidence.md"
  - gate: "verify"
    result: "VERIFIED"
    code_head: "50e26eebaa31524a81e0cc00d99edf4bdad0e2dc"
    at: "2026-11-21T15:14:55Z"
    evidence: ".foundry/plans/2026-11-20_21-37-12-s-stack/status/foundation-evidence.md"
  - gate: "review"
    result: "CLEAR"
    code_head: "50e26eebaa31524a81e0cc00d99edf4bdad0e2dc"
    at: "2026-11-21T15:21:04Z"
    evidence: ".foundry/plans/2026-11-20_21-37-12-s-stack/status/foundation-evidence.md"
  - gate: "verify"
    result: "VERIFIED"
    code_head: "829f3b1982124399b5ea54f8b597d62b7c8779a9"
    at: "2026-11-21T23:29:29Z"
    evidence: ".foundry/plans/2026-11-20_21-37-12-s-stack/status/foundation-evidence.md"
  - gate: "review"
    result: "SIGNIFICANT"
    code_head: "829f3b1982124399b5ea54f8b597d62b7c8779a9"
    at: "2026-11-21T23:36:34Z"
    evidence: ".foundry/plans/2026-11-20_21-37-12-s-stack/status/foundation-evidence.md"
pull_requests:
  - number: 81
    branch: "s-stack-foundation-package"
    base: "main"
    depends_on: []
    stacked: false
  - number: 82
    branch: "s-stack-verify-skill"
    base: "s-stack-foundation-package"
    depends_on: [81]
    stacked: true
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
  - id: "foundation-d3"
    decision: "verify-s-stack check 5 parses CommonMark with markdown-it-py, declared and pinned as markdown-it-py==4.0.0 in inline PEP 723 metadata and run with uv run --no-project, as scripts/pstack_upstream.py does. Three regular-expression parsers each mis-read some Markdown, and the orchestrator ruled out borrowing markdown-it-py from apm-cli's rich dependency, which a fresh clone or an apm-cli bump could lose."
    door: "two-way"
    at: "2026-11-21T15:07:33Z"
---

# Phase `foundation` status

The phase plan is at `.foundry/plans/2026-11-20_21-37-12-s-stack/phases/foundation.md`. The first Verify gate returned NOT VERIFIED: the shipped reference added an append-only evidence rule that C2 and foundation-d1 do not allow. The fix, 0eba66d, removes it. The second Verify gate returned VERIFIED at 0f4bf86, the verifier's commit that adds a C2 conformance check. The first Review gate returned SIGNIFICANT at 0f4bf86. The fix round (ce16529, c68877a, b27c4f1) repaired the verification files and added the foundation-d2 sentence. s-stack-package was merged at 5b346fa. The third Verify gate returned VERIFIED at b27c4f1. The second Review gate, over the commits since 0f4bf86, returned SIGNIFICANT at b27c4f1: the link checker's new fence stripping hides real links. Fix round 50e26ee parses Markdown with markdown-it-py (foundation-d3), compares the code-head rule on every branch, and narrows the cleanup. s-stack-package was merged at 7f51eff. The fourth Verify gate returned VERIFIED at 50e26ee. The third Review gate, over b27c4f1..50e26ee, returned CLEAR. Both verdicts cover 50e26ee. Draft pull requests 81 (the package and its wiring) and 82 (the verification skill, stacked on 81 in GitHub stack 83) are open. The equality proof shows that together they hold exactly the verified phase diff. Both merged into main, #81 as d7e036c and #82 as e4a18d1. The phase reached Done, then moved back to Implement for the orchestrator's follow-up round of 17 queued items in SKILL.md, the status reference and the verification skill. s-stack-package was merged at 9feaae9 and again at eb3ad81. The round's commits are 28fb827, 4e35b4a, b02556c and 829f3b1, after one quick-review fix pass. The follow-up Verify gate returned VERIFIED at 829f3b1, and the Review gate returned SIGNIFICANT: the router and reference moved the merge rule's ownership to orchestrator.md while phase-session.md still moves to PR on the reference's merge rule. Fix e92c913 and 98999ee make the reference own the merge rule a phase checks before PR, so phase-session.md reads correctly unchanged. The Verify gate is running again in full.

## Notes

- `docs/COMPATIBILITY.md` line 126 says "The nine dependency-bearing packages use the sibling `path:` form". Six do. This predates the phase and is outside its change. The phase corrected the same wrong list in `docs/DEPENDENCY-CONTRACTS.md` line 74, which it edits.
