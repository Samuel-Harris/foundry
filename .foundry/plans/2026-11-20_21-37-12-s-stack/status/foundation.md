---
phase: "foundation"
state: "Implement"
changed_at: "2026-11-21T13:56:21Z"
session: "s-stack-phase-foundation"
branch: "s-stack-phase-foundation"
code_head: "f7772cca88da57b5984cbff6ca125ae783c440ec"
waits_for: null
verdicts: []
pull_requests: []
requests:
  - id: "foundation-r1"
    question: "Should the shipped references/status-and-messages.md copy C2 word for word, including this run's lockfile exclusion from the code head, or state the general rule with placeholders?"
    options: ["A. General rule: code head excludes only .foundry/, a feature plan may name generated paths that also move no code head, and paths use <id> and <feature>. This run keeps using C2 from the feature plan.", "B. Copy C2 word for word, with this run's paths and the lockfile exclusion."]
    recommendation: "A"
    door: "two-way"
    waiting_work: "The code-head paragraph of references/status-and-messages.md. Everything else proceeds."
    since: "2026-11-21T13:56:21Z"
decisions: []
---

# Phase `foundation` status

The phase plan is at `.foundry/plans/2026-11-20_21-37-12-s-stack/phases/foundation.md`. Implementation of pull request 1 is under way.

## Notes

- `docs/DEPENDENCY-CONTRACTS.md` line 74 says "nine dependency-bearing packages" but lists eight, and some of them declare no dependency. This is pre-existing. The phase adds `s-stack` to that list and corrects nothing else there.
