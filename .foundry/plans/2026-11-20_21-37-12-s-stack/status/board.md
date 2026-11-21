---
phase: "board"
state: "Verify"
changed_at: "2026-11-21T17:12:06Z"
session: "s-stack-phase-board"
branch: "s-stack-phase-board"
code_head: "eff112da063ff5156ee3cc09e7a50adb8453ed95"
waits_for: null
verdicts:
  - gate: "verify"
    result: "VERIFIED"
    code_head: "45f0689499b3a4ea0dbe0001949e8a54ba184509"
    at: "2026-11-21T16:04:25Z"
    evidence: ".foundry/plans/2026-11-20_21-37-12-s-stack/status/board-evidence.md"
  - gate: "review"
    result: "SIGNIFICANT"
    code_head: "45f0689499b3a4ea0dbe0001949e8a54ba184509"
    at: "2026-11-21T16:12:25Z"
    evidence: ".foundry/plans/2026-11-20_21-37-12-s-stack/status/board-evidence.md"
  - gate: "verify"
    result: "VERIFIED"
    code_head: "a678a49d30e83b4d65ce068b8120ac192e61595c"
    at: "2026-11-21T16:53:47Z"
    evidence: ".foundry/plans/2026-11-20_21-37-12-s-stack/status/board-evidence.md"
  - gate: "review"
    result: "SIGNIFICANT"
    code_head: "a678a49d30e83b4d65ce068b8120ac192e61595c"
    at: "2026-11-21T17:05:18Z"
    evidence: ".foundry/plans/2026-11-20_21-37-12-s-stack/status/board-evidence.md"
pull_requests: []
requests: []
decisions:
  - id: "board-d1"
    decision: "The template has no <title>. Its schema comment tells the orchestrator to publish with title \"<feature> status board\", and the script sets document.title from meta.feature."
    door: "two-way"
    at: "2026-11-21T15:39:03Z"
  - id: "board-d2"
    decision: "The page declares only db, with the root rule read view and write admin, and never writes."
    door: "two-way"
    at: "2026-11-21T15:39:03Z"
  - id: "board-d3"
    decision: "Ready for your review lists only draft pull requests, as C5 says."
    door: "two-way"
    at: "2026-11-21T15:39:03Z"
  - id: "board-d4"
    decision: "Instruction from the developer, relayed by the orchestrator: the board gains a dependency map of the phases, drawn from a new depends_on field on each phases document (a list of phase and until entries, until merged or done). The phase moved back from Review to Implement for it."
    door: "two-way"
    at: "2026-11-21T16:06:59Z"
  - id: "board-d5"
    decision: "Instruction from the developer, relayed by the orchestrator: the scheduling value renders as a phrase that names the session, live as session live, closed as session closed, queued as queued to start, blocked as blocked, and session closed is styled neutral, never in the Done colour. C5 data values are unchanged."
    door: "two-way"
    at: "2026-11-21T16:08:04Z"
---

# Phase `board` status

The phase plan is committed at `8f55e96`. The template landed at `fef789b`. `quick-review` (bug and code-quality passes) found overflow from untrusted values, a false "Up to date" chip, closed pull requests counted as dependencies, staleness judged from cached data and scattered load state. Fixed in `68f7ab7` and `f3d0e32`. Dismissed with reasons: the no-database `hidden` finding (the publish skeleton ships `[hidden]{display:none!important}`), a single owner for review order (C5 requires both `review_rank` and the dependency rule), the duplicated dark token block (the page contract requires it), a guard for a `window.claude` without `use`, and focus loss on the 30-second re-render. `s-stack-package` was merged at `f0d9c7e` with no conflict and no change outside `.foundry/`. The verifier committed `checks/board.md` at `45f0689`, the new code head, and returned VERIFIED for it. The evidence file records one gap: nobody has watched the live viewer render the test page. The Review gate started for `45f0689`. The developer then asked, through the orchestrator, for a dependency map of the phases on the board (`board-d4`), so the phase moved back to Implement. The VERIFIED verdict at `45f0689` will not cover the new code head.

The Implement round for `board-d4` and `board-d5`: the dependency map (`921552b`), the scheduling labels with the adversarial review's fixes (`3137664`), a second `quick-review` round's fixes (`ba53040`), and a `depends_on` that is not a list shown as unknown (`2f575c8`). Dismissed from the second `quick-review` with reasons: fixed map margins and a split of the layout function (no behaviour change), overlapping lane runs (cosmetic, the Depends on column lists every edge), focus-key collisions (malformed data only), and the overlap between the Scheduling and Session columns (the developer asked for the labels; raised in the pull request). `s-stack-package` was merged at `9e4a8d5` under C7 with a lockfile-only conflict, bringing `spec-planner-handbooks`. The Verify gate is starting for `9e4a8d5`.

The verifier rewrote `checks/board.md` at `a678a49`, the new code head, and returned VERIFIED for it. Its 53 mutated templates all fail the new Rerun check. The Review gate is starting over `45f0689..a678a49`.

The second Review gate returned SIGNIFICANT at `a678a49`: the dependency map draws different graphs alike, and the Rerun check still passes broken templates. The phase is back in Implement for that.

The fix `66118de` gives each skipping edge its own lane, keeps map labels whole up to 40 characters, wraps unknown dependency chips, and keeps a live stale verdict through a cached snapshot. `s-stack-package` was merged at `eff112d` under C7 with a lockfile-only conflict, bringing `phase-handbooks` and `main`'s merge of #81. The Verify gate is starting for `eff112d`.
