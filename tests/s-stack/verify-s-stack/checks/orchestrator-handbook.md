# Phase `orchestrator-handbook` checks

Phase `orchestrator-handbook` ships `handbooks/orchestrator.md`, the orchestrator's handbook. It is prose, so the behavioural checks are cold reads. A cold read starts a fresh subagent, gives it only the files and the scenario the check names, tells it to read nothing else, and asks the questions. Its answer passes when it agrees in substance with every point of the expected answer. Wording may differ, but a missing or contradicting point fails the check. Wait for every cold-read subagent to finish before reporting.

Every scenario uses placeholder data: the feature `acme-widgets`, the default branch `trunk`, made-up SHAs and `example.invalid` addresses. The files, relative to the repository root:

- The handbook, `packages/s-stack/.apm/skills/sam-mode/handbooks/orchestrator.md`
- The reference, `packages/s-stack/.apm/skills/sam-mode/references/status-and-messages.md`

## Rerun

### Cold read A. One tick

Files: the handbook and the reference. Pass the scenario below inline.

Prompt: "Read only these two files and nothing else, not even files they link to. Answer from them and the scenario alone. You are the orchestrator of feature `acme-widgets`, and the tick has just fired. Assume the post-merge check of any merge you make this tick passes. List, step by step, every action this tick takes: (1) whether the default branch needs anything, (2) which phase you merge and how, and which you do not merge and why, (3) which phase you start, with the launcher call, and which you do not start and why, (4) what you unblock, (5) what you record, (6) which board documents you write and whether the architecture page changes, (7) what you say to the developer."

Scenario:

The feature plan's phases, with the generated paths and commands it names:

| Phase | Depends on | Exclusive resource |
| --- | --- | --- |
| `alpha` | None | None |
| `beta` | `alpha` | None |
| `gamma` | `alpha` | None |
| `delta` | `alpha` | None |
| `epsilon` | `alpha` | Port 8080 |
| `eta` | `alpha` | Port 8080 |
| `zeta` | `gamma` | None |

Generated paths: `**/lock.json`. Regenerate command: `make lock`. Repository checks: `make check`. The feature plan has no open planner requests.

The tracker, `.foundry/plans/2026-01-05_09-00-00-acme-widgets/status/orchestrator.md`:

- Window `@9`. Default branch `trunk`, last merged at `1111111111111111111111111111111111111111`.
- Status board `https://example.invalid/board`. Architecture page `https://example.invalid/arch`, describing orchestrator branch commit `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`.
- Last tick 2026-01-06T10:07:00Z. Recurring tick created 2026-01-05T09:30:00Z.
- Live sessions: `acme-widgets-phase-beta` pane `%11`, `acme-widgets-phase-gamma` pane `%12`, `acme-widgets-phase-epsilon` pane `%13`. `alpha`'s pane is closed.
- Open decision requests: none.
- Pull requests under watch: 10 (`alpha`, base `trunk`, depends on none), 11 (`gamma`, base `trunk`, depends on 10), 12 (`beta`, base `acme-widgets-alpha`, depends on 10). `needs_update` is false for all three.
- Merged phases: `alpha`, merge commit `a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1`, post-merge check VERIFIED.

The reconcile subagent's summary for this tick:

- After `git fetch origin`, `origin/trunk` is still `1111111111111111111111111111111111111111`.
- Workmux shows `beta`, `gamma` and `epsilon` working. None waits on a permission prompt. No other session is live.
- Pull requests 10, 11 and 12 are drafts, every required check passed, and none has a new review comment.
- For each phase, the code head you compute with the reference's command and the `**/lock.json` exclude equals the `code_head` in its header.
- The board, as written at the last tick, shows `gamma` in Verify and every other phase in the state its header or the tracker gives. `delta`, `eta` and `zeta` are in Plan with no session.

The status file headers:

```yaml
---
phase: "beta"
state: "PR"
changed_at: "2026-01-06T09:50:00Z"
session: "acme-widgets-phase-beta"
branch: "acme-widgets-phase-beta"
code_head: "b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2"
waits_for: null
verdicts:
  - gate: "verify"
    result: "NOT VERIFIED"
    code_head: "b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1"
    at: "2026-01-06T08:10:00Z"
    evidence: ".foundry/plans/2026-01-05_09-00-00-acme-widgets/status/beta-evidence.md"
  - gate: "verify"
    result: "VERIFIED"
    code_head: "b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2"
    at: "2026-01-06T09:05:00Z"
    evidence: ".foundry/plans/2026-01-05_09-00-00-acme-widgets/status/beta-evidence.md"
  - gate: "review"
    result: "CLEAR"
    code_head: "b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2"
    at: "2026-01-06T09:30:00Z"
    evidence: ".foundry/plans/2026-01-05_09-00-00-acme-widgets/status/beta-evidence.md"
pull_requests:
  - number: 12
    branch: "acme-widgets-beta"
    base: "acme-widgets-alpha"
    depends_on: [10]
    stacked: true
requests: []
decisions: []
---
```

```yaml
---
phase: "gamma"
state: "Review"
changed_at: "2026-01-06T10:15:00Z"
session: "acme-widgets-phase-gamma"
branch: "acme-widgets-phase-gamma"
code_head: "c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3"
waits_for: null
verdicts:
  - gate: "verify"
    result: "VERIFIED"
    code_head: "c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2"
    at: "2026-01-06T07:40:00Z"
    evidence: ".foundry/plans/2026-01-05_09-00-00-acme-widgets/status/gamma-evidence.md"
  - gate: "review"
    result: "CLEAR"
    code_head: "c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2"
    at: "2026-01-06T08:00:00Z"
    evidence: ".foundry/plans/2026-01-05_09-00-00-acme-widgets/status/gamma-evidence.md"
  - gate: "verify"
    result: "VERIFIED"
    code_head: "c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3"
    at: "2026-01-06T10:14:00Z"
    evidence: ".foundry/plans/2026-01-05_09-00-00-acme-widgets/status/gamma-evidence.md"
pull_requests:
  - number: 11
    branch: "acme-widgets-gamma"
    base: "trunk"
    depends_on: [10]
    stacked: false
requests: []
decisions: []
---
```

```yaml
---
phase: "epsilon"
state: "Implement"
changed_at: "2026-01-06T06:00:00Z"
session: "acme-widgets-phase-epsilon"
branch: "acme-widgets-phase-epsilon"
code_head: "e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1"
waits_for: null
verdicts: []
pull_requests: []
requests:
  - id: "epsilon-r1"
    question: "Should the widget export drop the legacy CSV column that customers still download?"
    options: ["A. Drop it now.", "B. Keep it for one more release."]
    recommendation: "B"
    door: "one-way"
    waiting_work: "The export step of the phase plan."
    since: "2026-01-06T10:12:00Z"
decisions: []
---
```

Expected answer:

1. **Default branch.** `origin/trunk` has not moved since the tracker's commit, so nothing is merged from it and no "feature pull request landed" duty runs.
2. **Merge `beta`.** Its header lists pull request 12, its newest `verify` verdict is `VERIFIED` and its newest `review` verdict is `CLEAR`, and both name `b2b2…`, the current code head. The older `NOT VERIFIED` verdict is superseded. The merge: read `beta`'s tip SHA first, compute the code head from that SHA, run `git merge --no-ff --no-commit <tip SHA>` on the orchestrator branch, merging that SHA and not the branch name, abort and send `merge-orchestrator-branch` to `beta` on any conflict, otherwise regenerate with `make lock`, stage, and commit with the hooks on. A fresh subagent then runs the feature's verification skill on the orchestrator branch, and the result goes in the tracker. Because it passes, `merge-orchestrator-branch` goes to every other live phase that has not reached PR, which is `gamma`, `epsilon` and `delta`, started earlier in this tick from the orchestrator branch before `beta` merged. `beta` gets `stop`, and once its stop commit is on its branch its pane closes with the launcher's `--close`. Its worktree stays.
3. **Do not merge `gamma`.** Its newest `review` verdict names `c2c2…`, an older code head than its current `c3c3…`, even though its newest `verify` verdict covers `c3c3…` and it lists a pull request. The orchestrator sends it nothing for this; the phase session runs its own Review. `epsilon` has no verdicts and no pull requests, so it is not a candidate.
4. **Start `delta`.** Its only dependency `alpha` is merged and passed its post-merge check, it needs no exclusive resource, and it has no session. The call is `scripts/launch.sh --feature acme-widgets --role phase --phase delta --window @9` from the feature worktree's root, and the printed pane goes in the tracker. The tick's Start step comes before its Merge step, so `delta` starts before `beta` is merged. Do not start `eta`: port 8080 is held by the live `epsilon`. Do not start `zeta`: `gamma` is not merged.
5. **Unblock.** Put `epsilon-r1`, a one-way door, to the developer with all its fields, and list it in the tracker and under **Needs you**. The orchestrator does not decide it. There is no permission prompt, no new review comment or failed check, and no stalled session.
6. **Record.** Update the tracker with the tick time, the open request, `delta`'s live session and pane, and `beta`'s merge commit, code head and post-merge check result, then commit it.
7. **Publish.** One database batch of at most 50 writes holding `board/meta` (for `tick_at`), `board/recent` (because `gamma` moved from Verify to Review), `phases/gamma`, `phases/delta` (its scheduling, session and pane changed), and one new `needs` document for `epsilon-r1`. `phases/beta` is written once its pane closes or its scheduling changes. No `prs/<number>` document changes, because no pull request's state, checks, base, dependencies or `needs_update` changed. Because a phase merged, a fresh subagent updates the architecture page.
8. **Report.** A short reply to the developer, because `epsilon-r1` needs a decision. Nothing else needs them.

### Cold read B. A sibling pull request lands on the default branch

Files: the handbook only. Pass the scenario below inline.

Prompt: "Read only this file and nothing else, not even files it links to. Answer from it and the scenario alone. You are the orchestrator of feature `acme-widgets`, and the tick has just fired. (1) What do you do about the default branch? (2) Which open pull requests get a `fix-round` marked generated files only? (3) Which get `needs_update` set to true? (4) For each open pull request, say exactly when it is ready for the developer to merge again. (5) What else does this tick do because pull request 20 merged?"

Scenario:

The feature plan names generated paths `**/lock.json`, the regenerate command `make lock` and the repository checks `make check`. The tracker records window `@9`, default branch `trunk`, last merged at `t1t1…`. After `git fetch origin`, `origin/trunk` is at `t2t2…`. The one new commit is the developer's squash merge of pull request 20, the only pull request of phase `alpha`, which changed `src/widgets/core.py` and `lock.json`. Merging `origin/trunk` into the orchestrator branch would apply without conflict.

The feature's three other pull requests are open, every one a draft:

| Pull request | Phase | Depends on | Head | `git merge-base --is-ancestor origin/trunk <head>` | Required checks on that head |
| --- | --- | --- | --- | --- | --- |
| 21 | `beta` | 20, stacked on it | `h21…` | Fails | All passed, but they ran before pull request 20 merged |
| 22 | `gamma` | None | `h22…` | Succeeds, because its PR creator already merged `trunk` in | All passed |
| 23 | `delta` | None | `h23…` | Succeeds | `lint` failed on a hand-written file, `src/widgets/render.py` |

Expected answer:

1. **Default branch.** Merge `origin/trunk` into the orchestrator branch on the orchestrator branch itself with `git merge --no-ff --no-commit origin/trunk`, which stops before committing even though git could merge on its own. Regenerate with `make lock` although nothing conflicted, stage, run `make check`, and commit with the hooks on. If the checks fail or a hook refuses, `git merge --abort` and tell the developer. Record `t2t2…`, the `trunk` commit merged, in the tracker as the commit at which the default branch was last merged, and send `merge-orchestrator-branch` to every live phase that has not reached PR. Because the new commit came from a feature pull request, the "feature pull request lands" duty runs.
2. **Generated-only fix rounds.** Every open pull request of the feature gets one: 21, 22 and 23. Each phase brings its pull request up to date with `trunk` and regenerates, with no new gates. Whether the default-branch step's resend for pull requests whose `needs_update` is still true also sends a second round in this same tick is not scored.
3. **`needs_update`.** True for 21, 22 and 23, in the tracker and on the board.
4. **Readiness.** A pull request is ready only when its `needs_update` is false, which is cleared only when, after `git fetch origin`, `git merge-base --is-ancestor origin/trunk <head SHA>` succeeds and every required check has passed on that head.
   - 21 is not ready. Its passing checks ran on a head without `t2t2…`. It is ready once its phase has brought it up to date, the ancestor test succeeds on the new head, and every required check has passed on that new head.
   - 22 meets both conditions on `h22…` already, so `needs_update` can be cleared as soon as the orchestrator runs the test, and it is ready. If its generated-only round pushes a new head, the checks must pass again on that head.
   - 23 is not ready. It contains the tip, but a required check failed. The `lint` failure on a hand-written file also needs an ordinary `fix-round` with the failed check, in which the phase fixes it on the phase branch, passes Verify and Review again for the new code head, and is merged again. It is ready once a head that contains `origin/trunk`'s current tip has every required check passed.
   - If `trunk` moves again before then, the condition is tested against the new tip.
5. **Pull request 20.** Pull request 21's only dependency has merged, so it has none left: add a restack to **Needs you**, and send `restack` only if the developer asks. Every pull request of `alpha` has merged, so the order is: start `alpha`'s session with the launcher (`--window @9`) so that it moves the phase to Done; send it `stop`; once its stop commit is on its branch, merge `alpha`'s branch into the orchestrator branch once more with the phase-merge steps (`git merge --no-ff --no-commit <tip SHA>`, abort and send `merge-orchestrator-branch` on a conflict, otherwise regenerate with `make lock`, stage and commit with the hooks on), so its last status commits reach the orchestrator branch; then close its pane with `--close`; then remove its worktree with `--remove`. An answer that leaves out `stop` or `--close`, or runs `--remove` before that merge or while the session is still live, fails this point. The developer, not s-stack, merges pull requests into `trunk`.

### Cold read C. Conflicts when merging

Files: the handbook only. Pass the scenario below inline.

Prompt: "Read only this file and nothing else, not even files it links to. Answer from it and the scenario alone. You are the orchestrator of feature `acme-widgets` (window `@9`, default branch `trunk`). The feature plan names generated paths `**/lock.json` and package manifests' `version:` lines, the regenerate command `make lock` and the repository checks `make check`. Say exactly what you do in each case, and who resolves each conflict. (1) In one tick, `git merge --no-ff --no-commit origin/trunk` on the orchestrator branch conflicts in `packages/widgets/lock.json` and in `packages/widgets/manifest.yml`, whose two sides differ only in the `version:` line. (2) In a later tick, the same merge conflicts in `packages/widgets/lock.json` and in `src/widgets/render.py`. Phase `gamma` owns `src/widgets/`. It is in PR and its pane is closed. (3) In another tick, `beta` may merge, and `git merge --no-ff --no-commit <beta tip SHA>` on the orchestrator branch conflicts only in `packages/widgets/lock.json`."

Expected answer:

1. Take `trunk`'s side for `lock.json` and for `manifest.yml`, because the manifest's sides differ only in the generated version line. Regenerate with `make lock` and stage it, run `make check`, and commit with the hooks on. If the checks fail or a hook refuses, `git merge --abort` and tell the developer. Record the `trunk` commit merged in the tracker and send `merge-orchestrator-branch` to every live phase that has not reached PR. The orchestrator resolves this one itself.
2. `render.py` is hand-written, so run `git merge --abort`, leaving the lockfile conflict unresolved too. `gamma`'s pane is closed, so first start its session with `scripts/launch.sh --feature acme-widgets --role phase --phase gamma --window @9`. Then send `gamma` a `fix-round` that names the conflicting paths and the `trunk` commit. `gamma` merges `trunk` into its phase branch and passes both gates again. The orchestrator never resolves the hand-written conflict.
3. Any conflict in a phase merge, even one confined to a generated file, means `git merge --abort` and a `merge-orchestrator-branch` message to `beta`. The orchestrator never resolves a phase merge conflict.

### Cold read D. Stalls, prompts and a failed post-merge check

Files: the handbook only. Pass the scenario below inline.

Prompt: "Read only this file and nothing else, not even files it links to. Answer from it and the scenario alone. You are the orchestrator of feature `acme-widgets` (window `@9`). For each of the sessions or events below, say whether it needs action and exactly what you do. (1) `acme-widgets-phase-delta`, in Implement: workmux shows it idle and not waiting on a prompt, its header's `waits_for` is null, and it has made no commit and no pull request change for the last three ticks. (2) `acme-widgets-phase-epsilon`, pane `%14`: workmux shows it waiting on a permission prompt to run `make deploy-preview`. (3) `acme-widgets-phase-zeta`: idle, its `waits_for` is `The answer to zeta-r1`, and it has made no commit for three ticks. (4) This tick you merged `beta`, and the fresh subagent's run of the verification skill on the orchestrator branch failed its Tier 1 check. (5) The next tick, `beta` is back in Implement and has reported no new verdicts, and no check has run since. Phase `eta` depends only on `alpha`, which merged and passed its post-merge check long ago, and it needs no exclusive resource. Does `eta` start? (6) `acme-widgets-phase-theta`, in PR: its pull requests are open, it holds both verdicts for its current code head, and it waits for you to merge it. Workmux shows it idle and not waiting on a prompt, its `waits_for` is null, and it has made no commit and no pull request change for three ticks. (7) `acme-widgets-planner`: it sent `done-planning` three ticks ago, you merged its branch, and its pane is still open. Workmux shows it idle, and it has made no commit since."

Expected answer:

1. `delta` has stalled: idle, not on a prompt, no `waits_for`, and no commit or pull request change for two ticks or more. Replace it without asking the developer. A stalled session's conversation is the problem, so it gets `stop`, then `scripts/launch.sh --feature acme-widgets --role phase --phase delta --close`, then a launch with `--window @9 --fresh`. A plain resume without `--fresh` fails this point.
2. `epsilon` has not stalled. Send the developer a push notification with Claude Code's push notification tool, naming pane `%14` and the action `make deploy-preview`, and add a prompt to **Needs you**. Only the developer approves, in that pane. Never relay an approval or type into the pane.
3. `zeta` has not stalled, because its `waits_for` is set. Do not replace it. Make sure `zeta-r1` has been put to the developer and is listed in the tracker and under **Needs you**.
4. Record the result in the tracker. The orchestrator branch is now frozen until a later post-merge check passes. Send `beta` a `move-back` to Implement that names the failed check. Do not send `beta` `stop` and do not close its pane, because those follow a passing check only. Send `merge-orchestrator-branch` to no other phase. Merge `beta` again only when both its newest verdicts name a code head newer than the one that failed.
5. No. While frozen, the tick skips its default-branch step and the starts in its Start step, so the orchestrator starts no phase at all, not only the phases that depend on `beta`, and `eta` waits.
6. `theta` has not stalled. A phase in PR waiting to be merged has no work, so it is not replaced. It merges when the Merge step reaches it.
7. The planner has not stalled, because a planner that has reported has no work. It is not replaced with `--fresh`. Its pane should have closed after `done-planning`, so close it now with `scripts/launch.sh --feature acme-widgets --role planner --close`.

### Cold read E. Planner branches and default-branch commits

Files: the handbook only. Pass the scenario below inline.

Prompt: "Read only this file and nothing else, not even files it links to. Answer from it and the scenario alone. You are the orchestrator of feature `acme-widgets` (window `@9`, default branch `trunk`). The feature plan names generated paths `**/lock.json`, the regenerate command `make lock` and the repository checks `make check`. The feature's lockfile records the package `packages/shared-lib`. Pull requests 31 (`beta`) and 32 (`gamma`) are open drafts, and live phase `delta` is in Implement. Say exactly what you do in each case, and what the tracker records. (1) The planner sends `done-planning`. Its branch changes `.foundry/plans/2026-01-05_09-00-00-acme-widgets/README.md` and `src/widgets/core.py`. (2) In one tick, `origin/trunk` has moved from `t1t1…` to `t2t2…`. The one new commit is a colleague's, from no pull request of this feature, and it changes only `packages/shared-lib/api.py`. Merging it would not conflict. (3) In a later tick, `origin/trunk` has moved from `t2t2…` to `t3t3…`. The one new commit is a colleague's, from no pull request of this feature, and it changes only `docs/style.md`, which no package contains. Merging it would not conflict. By then pull request 31's head contains `t2t2…` and every required check passed on it, so its `needs_update` was cleared. Pull request 32's `needs_update` is still true, because its phase has not yet brought it up to date."

Expected answer:

1. Do not merge the planner's branch, because it changes a file outside `.foundry/plans/`. Any reasonable next step for the refused branch, such as telling the planner or the developer, passes.
2. Merge `origin/trunk` with `git merge --no-ff --no-commit origin/trunk` on the orchestrator branch, regenerate with `make lock`, stage, run `make check`, and commit with the hooks on, aborting and telling the developer if the checks fail or a hook refuses. Record `t2t2…` in the tracker as the default branch commit last merged, and send `merge-orchestrator-branch` to `delta`. The commit changed a package that the feature's generated files depend on, so the "feature pull request lands" duty runs although no feature pull request merged: a `fix-round` marked generated files only to the phases of 31 and 32, and `needs_update` true for both in the tracker and on the board, cleared only when the ancestor test against `origin/trunk` succeeds on each head and every required check has passed there.
3. Merge `origin/trunk` with the same stop-before-commit procedure, record `t3t3…` in the tracker, and send `merge-orchestrator-branch` to `delta`. The commit came from no feature pull request and changed no package the generated files depend on, so the "feature pull request lands" duty does not run, no `needs_update` is newly set and 31 gets nothing. The tick's default-branch step itself says that on any move of the default branch, each open pull request whose `needs_update` is still true gets another `fix-round` marked generated files only. 32's is still true, so 32's phase gets one in this tick, from that step and not from the "lands" duty. 32 stays not ready until the ancestor test against the new tip `t3t3…` succeeds on its head and every required check has passed there. An answer that sends 32 nothing, or that sends it a round only by running the "lands" duty for this docs-only move, fails this point.

### Cold read F. A frozen orchestrator branch across ticks

Files: the handbook only. Pass the scenario below inline.

Prompt: "Read only this file and nothing else, not even files it links to. Answer from it and the scenario alone. You are the orchestrator of feature `acme-widgets` (window `@9`, default branch `trunk`). The feature plan names generated paths `**/lock.json`, the regenerate command `make lock` and the repository checks `make check`. Last tick you merged `beta` at code head `b2b2…`, and the post-merge check failed its Tier 1 check. You sent `beta` a `move-back` to Implement. No check has passed since. Answer for each tick, step by step: whether you merge the default branch, whether you start any phase, which phase you merge, and what else the tick does. (1) This tick: `origin/trunk` has moved from `t1t1…` to `t2t2…` by a colleague's commit that touches only `docs/style.md`. Phase `eta` depends only on `alpha`, which merged and passed its check long ago, needs no exclusive resource, and has no session. Phase `gamma` lists its open pull request, and its newest `verify` (`VERIFIED`) and `review` (`CLEAR`) verdicts both name its current code head. `beta`'s header lists its pull request, its code head is still `b2b2…`, and its newest `verify` (`VERIFIED`) and `review` (`CLEAR`) verdicts both name `b2b2…`, from before the failed check. `acme-widgets-phase-epsilon`, pane `%14`, waits on a permission prompt to run `make deploy-preview`. `acme-widgets-phase-delta`, in Implement, has work: workmux shows it idle and not waiting on a prompt, its `waits_for` is null, and it has made no commit and no pull request change for three ticks. (2) The next tick: nothing on `trunk` or `gamma` has changed. `beta`'s code head is now `b3b3…`, a newer commit, and its newest `verify` (`VERIFIED`) and `review` (`CLEAR`) verdicts both name `b3b3…`. Assume this merge applies cleanly and its post-merge check passes."

Expected answer:

1. **First tick.** The orchestrator branch is frozen, so the tick skips its default-branch step: `origin/trunk` is not merged, and nothing is recorded as merged from it. It skips the starts in its Start step, so `eta` does not start. It still replaces stalled sessions: `delta` has stalled, so it gets `stop`, then `scripts/launch.sh --feature acme-widgets --role phase --phase delta --close`, then a launch with `--window @9 --fresh`. An answer that leaves `delta` alone because the branch is frozen fails this point. In the Merge step it may merge only `beta`, the frozen phase, and only when both its newest verdicts name a code head newer than `b2b2…`, the one that failed. They name `b2b2…`, so `beta` does not merge, although the plain verdict rule would allow it. `gamma` does not merge, because no phase but the frozen one merges while frozen. The other steps still run: Reconcile first; Unblock sends the developer a push notification naming pane `%14` and `make deploy-preview` and adds a prompt to **Needs you**; Record updates and commits the tracker; Publish writes the changed board documents in one batch, including `board/meta` and the new `needs` document. Whether Report also mentions the prompt is not scored. Sending `merge-orchestrator-branch` to any phase fails this point.
2. **Next tick.** Still frozen at the start, so the default-branch step and the starts are skipped again. `beta` now merges, because both newest verdicts name `b3b3…`, newer than `b2b2…`. Read `beta`'s tip SHA first, compute its code head from that SHA, then `git merge --no-ff --no-commit <tip SHA>`, regenerate with `make lock`, stage and commit with the hooks on, and have a fresh subagent run the verification skill. The check passes, so the freeze ends. Send `merge-orchestrator-branch` to every other live phase that has not reached PR, start the phases that now have their dependencies, send `beta` `stop` and close its pane with `--close` once its stop commit lands. `gamma` does not merge in this tick, because at most one phase merges per tick. `origin/trunk` is merged in a later tick's default-branch step; starting `eta` in this tick after the pass, or in the next tick's Start step, both pass. Because a phase merged, a fresh subagent updates the architecture page.

### Cold read G. Board seeding and `depends_on`

Files: the handbook only. Pass the scenario below inline.

Prompt: "Read only this file and nothing else, not even files it links to. Answer from it and the scenario alone. You are the orchestrator of feature `acme-widgets` (window `@9`). You have published the status board and the first architecture page, and started the planner. (1) First, say which `phases` documents you wrote on the board when you published it. Then the planner sends `done-planning`. Its branch changes only `.foundry/plans/2026-01-05_09-00-00-acme-widgets/README.md`. The feature plan lists three phases: `alpha` depends on nothing, `beta` depends on `alpha` merged, and `gamma` depends on `alpha` merged and `beta` done. No phase needs an exclusive resource. Say what you do and exactly which board documents you write. (2) Later, `alpha` is live in Implement and `beta` and `gamma` have not started. A restarted planner sends a second `done-planning`, whose branch again changes only the feature plan. The message names `beta`'s entry as changed: `beta` now also depends on a new phase `delta`, which depends on nothing. Say what you do, which board documents you write, and which phases get `move-back`. (3) Later still, `alpha`, `delta` and `beta` have all merged into the orchestrator branch and passed their post-merge checks. `beta`'s one pull request is an open draft on `trunk`, not yet merged. Does `gamma` start in this tick? If not, when does it start?"

Expected answer:

1. When the board was published, no `phases` document was written, because no feature plan existed yet. The `phases` documents are written when the planner's first `done-planning` merges. Then: check that the branch changes nothing outside `.foundry/plans/`, merge it with `--no-ff`, and close the planner's pane with `scripts/launch.sh --feature acme-widgets --role planner --close`. Write a `phases` document for every phase in the feature plan, `alpha`, `beta` and `gamma`, each with `depends_on` taken from that phase's entry (`alpha` none, `beta` `alpha`, `gamma` `alpha` and `beta`), following the schema in the template's comment, in one database batch. Start `alpha` only, with `scripts/launch.sh --feature acme-widgets --role phase --phase alpha --window @9`, and record its pane. `beta` and `gamma` wait for their dependencies.
2. Check and merge the branch as before, and close the planner's pane. Write `depends_on` again for `beta`, and a `phases` document for the new `delta`. Send `move-back` to Plan only to a started phase whose plan entry the message names as changed: `beta` has not started and `alpha`'s entry did not change, so no phase gets `move-back`. Start `delta`, whose dependencies are met. `beta` still waits.
3. No. `gamma`'s plan entry needs `beta` Done, and merged into the orchestrator branch is not enough. `gamma` starts in the Start step of the first tick after `beta` is Done, that is, after `beta`'s pull request has merged into `trunk` and its session has moved the phase to Done. An answer that starts `gamma` now fails this point.

### Cold read H. The merged SHA and a refused abort

Files: the handbook only. Pass the scenario below inline.

Prompt: "Read only this file and nothing else, not even files it links to. Answer from it and the scenario alone. You are the orchestrator of feature `acme-widgets`. The feature plan names generated paths `**/lock.json` and the regenerate command `make lock`. (1) Phase `beta`, on branch `acme-widgets-phase-beta`, lists its open pull request. Its newest `verify` (`VERIFIED`) and `review` (`CLEAR`) verdicts both name `b2b2…`. You read the branch tip as `b2b2…`. While you are checking, `beta`'s session pushes commit `b3b3…`, which changes `src/widgets/core.py`, onto the branch. Give the exact commands you run to decide and to merge, and say what is merged. (2) You merge `beta`, regenerate with `make lock`, and stage `packages/widgets/lock.json`. On commit, the pre-commit hook refuses and rewrites `packages/widgets/lock.json`. `git merge --abort` then fails with `error: Entry 'packages/widgets/lock.json' not uptodate. Cannot merge.` What do you do?"

Expected answer:

1. The tip SHA is read first and everything follows from it. Compute the code head from that SHA, for example `git log -1 --format=%H b2b2… -- . ':(exclude).foundry' ':(exclude)**/lock.json'`, which gives `b2b2…`. Both newest verdicts name it, so `beta` may merge, and the merge is `git merge --no-ff --no-commit b2b2…` on the orchestrator branch, by SHA and never by branch name. `b3b3…` is not merged, because no verdict covers it. An answer that computes the code head or merges from the branch name fails this point.
2. Run `git checkout -- packages/widgets/lock.json`, the file the refusal names, then `git merge --abort` again. Then send `beta` `merge-orchestrator-branch`. The orchestrator does not resolve or commit the lockfile itself.

### Abort recovery in a scratch repository

The handbook says that when `git merge --abort` refuses because a hook rewrote a file, `git checkout -- <path>` and a second abort recover. This script builds a throwaway repository under `mktemp -d`, with placeholder names and a hermetic git configuration, makes a pre-commit hook refuse a merge commit after rewriting a staged lockfile, and checks that the first abort refuses, naming the file, and that the handbook's recovery restores the pre-merge state. It touches nothing outside its temporary directory.

```bash
bash <<'SCRIPT'
set -u
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
fail() { echo "FAIL: $*"; exit 1; }
cd "$tmp" && git init -q -b trunk repo && cd repo
git config user.name placeholder && git config user.email placeholder@example.invalid
mkdir -p packages/widgets src/widgets hooks
echo '{"v": 1}' > packages/widgets/lock.json
echo 'core = 1' > src/widgets/core.py
git add packages src && git commit -q -m base
git checkout -q -b acme-widgets-phase-beta
echo 'core = 2' > src/widgets/core.py
git commit -q -am "beta change"
tip="$(git rev-parse HEAD)"
git checkout -q -b acme-widgets trunk
before="$(git rev-parse HEAD)"
printf '#!/bin/sh\necho "{\\"v\\": 3}" > packages/widgets/lock.json\necho "lockfile stale, rewritten" >&2\nexit 1\n' > hooks/pre-commit
chmod +x hooks/pre-commit
git merge -q --no-ff --no-commit "$tip" || fail "the merge should stop cleanly before committing"
echo '{"v": 2}' > packages/widgets/lock.json && git add packages/widgets/lock.json
git -c core.hooksPath=hooks commit -q --no-edit 2>/dev/null && fail "the hook should refuse the commit"
git merge --abort 2>abort.err && fail "the first abort should refuse after the hook rewrote a staged file"
grep -q "lock.json" abort.err || fail "the refused abort should name lock.json: $(cat abort.err)"
git rev-parse -q --verify MERGE_HEAD >/dev/null || fail "MERGE_HEAD should remain after the refused abort"
rm -f abort.err
git checkout -- packages/widgets/lock.json
git merge --abort || fail "the abort should succeed after git checkout of the named file"
git rev-parse -q --verify MERGE_HEAD >/dev/null && fail "MERGE_HEAD should be gone"
[ "$(git rev-parse HEAD)" = "$before" ] || fail "HEAD moved"
[ -z "$(git status --porcelain --untracked-files=no)" ] || fail "tracked files changed: $(git status --porcelain)"
git merge -q --no-ff --no-commit "$tip" || fail "a later merge should start"
git merge --abort
echo "blocked abort recovered: refused, then checkout and abort left HEAD at $before with a clean tree"
SCRIPT
```

Expected: exit `0` and a last line starting `blocked abort recovered:`. Git prints `Automatic merge went well; stopped before committing as requested` twice on the way. With only a plain `git merge --abort`, as the handbook said before `fc9c6cd`, the script fails at its first-abort assertion.

## Evidence

### Command lines and private names, handbook blob `6487eb4c74903bc5b8f14145c7da7d4a592601f4`

A `grep` of the handbook for `workmux`, `tmux` and `claude` found no command line. The only mentions are "workmux shows it idle" and "workmux's status" as sources of fact, and "Claude Code's" scheduled task and push notification tool. Every launcher call is by flag: `--feature`, `--role`, `--phase`, `--update`, `--window`, `--fresh`, `--close`, `--remove` and `--print-window`. A case-insensitive `grep` of the handbook, `packages/s-stack/apm.lock.yaml`, this file and the phase's commit messages for the private repository's name, its feature's name and both prototype page ids (taken from the developer's private notes and not reproduced here) found no hit. The handbook has 160 lines.
