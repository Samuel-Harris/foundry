---
phase: "board"
state: "PR"
changed_at: "2026-11-22T01:06:43Z"
session: "s-stack-phase-board"
branch: "s-stack-phase-board"
code_head: "284ad88a3929192851895e2650198266bcddca75"
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
  - gate: "verify"
    result: "VERIFIED"
    code_head: "b2deb4dc95214b6039608c7c3b7f949aae752bce"
    at: "2026-11-21T17:42:45Z"
    evidence: ".foundry/plans/2026-11-20_21-37-12-s-stack/status/board-evidence.md"
  - gate: "review"
    result: "SIGNIFICANT"
    code_head: "b2deb4dc95214b6039608c7c3b7f949aae752bce"
    at: "2026-11-21T18:10:36Z"
    evidence: ".foundry/plans/2026-11-20_21-37-12-s-stack/status/board-evidence.md"
  - gate: "verify"
    result: "VERIFIED"
    code_head: "a5b3a9c8a79a19b3d65691765019a0e6adb28279"
    at: "2026-11-21T20:31:13Z"
    evidence: ".foundry/plans/2026-11-20_21-37-12-s-stack/status/board-evidence.md"
  - gate: "review"
    result: "SIGNIFICANT"
    code_head: "a5b3a9c8a79a19b3d65691765019a0e6adb28279"
    at: "2026-11-21T20:58:48Z"
    evidence: ".foundry/plans/2026-11-20_21-37-12-s-stack/status/board-evidence.md"
  - gate: "verify"
    result: "VERIFIED"
    code_head: "afd3f270ba9c2ddc689b0afe12927591941ccc7f"
    at: "2026-11-21T21:28:58Z"
    evidence: ".foundry/plans/2026-11-20_21-37-12-s-stack/status/board-evidence.md"
  - gate: "review"
    result: "CLEAR"
    code_head: "afd3f270ba9c2ddc689b0afe12927591941ccc7f"
    at: "2026-11-21T21:41:33Z"
    evidence: ".foundry/plans/2026-11-20_21-37-12-s-stack/status/board-evidence.md"
  - gate: "verify"
    result: "VERIFIED"
    code_head: "284ad88a3929192851895e2650198266bcddca75"
    at: "2026-11-22T01:01:30Z"
    evidence: ".foundry/plans/2026-11-20_21-37-12-s-stack/status/board-evidence.md"
  - gate: "review"
    result: "CLEAR"
    code_head: "284ad88a3929192851895e2650198266bcddca75"
    at: "2026-11-22T01:06:43Z"
    evidence: ".foundry/plans/2026-11-20_21-37-12-s-stack/status/board-evidence.md"
pull_requests:
  - number: 86
    branch: "s-stack-board"
    base: "main"
    depends_on: []
    stacked: false
  - number: 92
    branch: "s-stack-board-follow-up"
    base: "main"
    depends_on: []
    stacked: false
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
  - id: "board-d6"
    decision: "Answer to board-r1 from the orchestrator, option A. Under its convergence rule, a gap in checks/board.md is significant only when the broken template that passes is a defect a plausible edit would introduce and that would mislead the developer on the live board: wrong staleness, a hidden or wrong dependency or state, lost or misattributed data, or a page that hangs or will not render. A gap shown only by changed constants, styling or a promise nobody acts on is minor, recorded in the evidence file, and does not hold the phase in Review."
    door: "two-way"
    at: "2026-11-21T18:11:44Z"
  - id: "board-d7"
    decision: "Instruction from the orchestrator, replacing board-d6 from the fifth Review gate on: only a real defect in the template is significant. Every check gap, however misleading its mutant, goes under Check hardening backlog in the evidence file, and the phase goes to PR. The twelve gaps of the fourth review are still closed in the current round."
    door: "two-way"
    at: "2026-11-21T20:59:46Z"
  - id: "board-d8"
    decision: "Follow-up round from the orchestrator after foundation's follow-ups (#88, #89) merged: remove the retired restack need kind from the board template and its schema comment, and make the schema comment's needs_update rule match orchestrator.md, which also requires the heads of a pull request's open dependencies. Then Verify and Review once under the minor-findings rule, and open a new draft pull request."
    door: "two-way"
    at: "2026-11-22T00:37:11Z"
---

# Phase `board` status

The phase plan is committed at `8f55e96`. The template landed at `fef789b`. `quick-review` (bug and code-quality passes) found overflow from untrusted values, a false "Up to date" chip, closed pull requests counted as dependencies, staleness judged from cached data and scattered load state. Fixed in `68f7ab7` and `f3d0e32`. Dismissed with reasons: the no-database `hidden` finding (the publish skeleton ships `[hidden]{display:none!important}`), a single owner for review order (C5 requires both `review_rank` and the dependency rule), the duplicated dark token block (the page contract requires it), a guard for a `window.claude` without `use`, and focus loss on the 30-second re-render. `s-stack-package` was merged at `f0d9c7e` with no conflict and no change outside `.foundry/`. The verifier committed `checks/board.md` at `45f0689`, the new code head, and returned VERIFIED for it. The evidence file records one gap: nobody has watched the live viewer render the test page. The Review gate started for `45f0689`. The developer then asked, through the orchestrator, for a dependency map of the phases on the board (`board-d4`), so the phase moved back to Implement. The VERIFIED verdict at `45f0689` will not cover the new code head.

The Implement round for `board-d4` and `board-d5`: the dependency map (`921552b`), the scheduling labels with the adversarial review's fixes (`3137664`), a second `quick-review` round's fixes (`ba53040`), and a `depends_on` that is not a list shown as unknown (`2f575c8`). Dismissed from the second `quick-review` with reasons: fixed map margins and a split of the layout function (no behaviour change), overlapping lane runs (cosmetic, the Depends on column lists every edge), focus-key collisions (malformed data only), and the overlap between the Scheduling and Session columns (the developer asked for the labels; raised in the pull request). `s-stack-package` was merged at `9e4a8d5` under C7 with a lockfile-only conflict, bringing `spec-planner-handbooks`. The Verify gate is starting for `9e4a8d5`.

The verifier rewrote `checks/board.md` at `a678a49`, the new code head, and returned VERIFIED for it. Its 53 mutated templates all fail the new Rerun check. The Review gate is starting over `45f0689..a678a49`.

The second Review gate returned SIGNIFICANT at `a678a49`: the dependency map draws different graphs alike, and the Rerun check still passes broken templates. The phase is back in Implement for that.

The fix `66118de` gives each skipping edge its own lane, keeps map labels whole up to 40 characters, wraps unknown dependency chips, and keeps a live stale verdict through a cached snapshot. `s-stack-package` was merged at `eff112d` under C7 with a lockfile-only conflict, bringing `phase-handbooks` and `main`'s merge of #81. The Verify gate is starting for `eff112d`.

A first verifier for `eff112d` was stopped before it committed, when the orchestrator relayed the rule that check files hold no results. A fresh verifier rewrote `checks/board.md` at `b2deb4d`, the new code head, under that rule and returned VERIFIED. The Review gate is starting over `a678a49..b2deb4d`.

The third Review gate returned SIGNIFICANT at `b2deb4d`. Every finding is a gap in `checks/board.md`; both adversaries found the template correct. No template change is planned. The phase moves through Implement to Verify, where a fresh verifier closes the gaps systematically.

The code head is unchanged at `b2deb4d`. The Verify gate is starting.

The fourth verifier committed `checks/board.md` at `e21d7e8` and finished two mutation rounds. It was stopped at 20:10 under the orchestrator's 15-minute limit, while it was editing the file again: with fallback fonts it had found a broken word or clipped chip at 1000 px. Its uncommitted edit is saved outside the repository. `s-stack-package` was merged at `cc362c4` under C7, with a lockfile-only conflict. The merge brings `phase-session.md` changes and s-stack 0.1.2, so `cc362c4` is the code head. A fresh verifier is starting there, scoped to one representative mutant per assertion.

The scoped verifier committed `a5b3a9c`, the new code head, and returned VERIFIED. The fallback-font failure was the check, not the template. The Review gate is starting over `b2deb4d..a5b3a9c`.

The fourth Review gate returned SIGNIFICANT at `a5b3a9c`. Both adversaries again found the template correct. Twelve broken templates pass the check, and under `board-d6` each would mislead the developer on the live board or open an injection. No template change is planned. The phase moves through Implement to Verify, where a verifier makes each named mutant fail.

The code head is unchanged at `a5b3a9c`. The Verify gate is starting.

The verifier closed the twelve gaps at `afd3f27`, the new code head, and returned VERIFIED. The fifth Review gate is starting over `a5b3a9c..afd3f27`, under `board-d7`.

The fifth Review gate returned CLEAR at `afd3f27` under `board-d7`: neither adversary found a template defect. Both verdicts cover `afd3f27`. The PR creator is starting. Every foundation pull request is merged into `main`, so the board pull request has no open dependency.

Draft pull request #86 (`s-stack-board` into `main`, head `7f233e4`) is open, with no open dependency. It replays the 14 own commits without lockfile hunks or `.foundry/`, and ends with `chore(s-stack): regenerate generated files`, which raises s-stack from 0.1.2 to 0.1.3 and regenerates its lockfile. The equality proof, in the form of Experiment 7, printed EQUAL against the phase branch, with an empty regenerate check and no `.foundry/` on the branch. The phase session confirmed that both hand-written files on the branch are byte-identical to `afd3f27`. The pull request carries 1,792 hand-written lines plus 22 generated lockfile lines. Its CI run https://github.com/Samuel-Harris/foundry/actions/runs/44953157241 passed: Pre-commit checks and Package versions pass, and the path-filtered jobs skipped.

Pull request #86 merged into `main` as `51f334e`. The code head `afd3f27` is merged into `s-stack-package` (`a606589`), and the orchestrator's post-merge check returned VERIFIED on `3ce7d34`. Every pull request of the phase is merged, so the phase is Done.

The orchestrator opened a two-item follow-up round (`board-d8`), so the phase moved from Done back to Implement. The worktree was recreated on the phase branch at `c7dcf1a`.

Follow-up round: `s-stack-package` was merged under C7 at `a60b107`, cleanly, bringing s-stack 0.1.5. `73251d3` removes the restack need kind and aligns the `needs_update` rule with `orchestrator.md`, as it stands on `s-stack-phase-orchestrator-handbook`, because that file is not yet on `s-stack-package`. `quick-review` (bug and quality) found no significant defect in the code. Both reviewers flagged that "open" collides with the schema's `open` state, which would leave drafts out. `5fc142f` names draft and open pull requests, says the flag is set and cleared, and says required checks come from the repository. The Verify gate is starting for `5fc142f`.

`s-stack-package` was merged again at `f674585`, touching no board path. The verifier updated `checks/board.md` for the removed kind at `284ad88`, the new code head, and returned VERIFIED. The Review gate is starting over `afd3f27..284ad88`.

The follow-up Review gate returned CLEAR at `284ad88`: neither adversary found a defect. Both verdicts cover `284ad88`. The PR creator is starting a new draft pull request against `main`.

Draft pull request #92 (`s-stack-board-follow-up` into `main`, head `f9aa70c`) is open, with no open dependency. It carries `73251d3`, `5fc142f` and `284ad88` without lockfile hunks, then a regenerate commit that raises s-stack from 0.1.7 to 0.1.8. At that moment no open pull request changed `packages/s-stack/apm.yml`. The PR creator's proof printed EQUAL against the local `s-stack-package`. The phase session confirmed that both hand-written files are byte-identical to `284ad88`, and that the branch holds no `.foundry/`. The pull request carries 37 hand-written lines. Tier 1 and the hook passed locally, and CI run https://github.com/Samuel-Harris/foundry/actions/runs/44972350601 passed.
