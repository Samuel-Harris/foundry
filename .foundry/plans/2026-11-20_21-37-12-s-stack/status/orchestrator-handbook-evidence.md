# Phase `orchestrator-handbook` evidence

## Verify 1, code head `019c8a14316585c687fe3cc3434ea67428e9afb3`, VERIFIED

A fresh verifier wrote `tests/s-stack/verify-s-stack/checks/orchestrator-handbook.md` (commit `019c8a1`, four cold reads A to D in `## Rerun`) and ran the whole verification skill on the phase branch, using the pinned APM 0.32.0 at the main checkout's `.venv-apm`.

| Check | Result |
| --- | --- |
| 1. Primitives and root manifest | PASS. `94 primitives valid`; `check_root_manifest: 12 listed, 19 reached` |
| 2. Markdown lint | PASS. 7 files, 0 errors |
| 3. Line budgets | PASS. `SKILL.md` 103/150, `handbooks/orchestrator.md` 158/200 |
| 4. Routes | PENDING, allowed. `orchestrator.md` present, six handbooks pending |
| 5. Package isolation | PASS |
| 6. Launcher tests | PENDING. `packages/s-stack/tests` absent until `launcher` merges |
| 7. Tier 1, outside the sandbox | PASS. `all Tier 1 structural checks passed across 20 packages` |
| 8. Phase check files | PASS. `foundation` cold reads 1 to 3 and its C2 script; `orchestrator-handbook` cold reads A to D |

Every **Done when** item was met. The verifier also listed handbook defects outside the **Done when** list. The three that would fail in a real run sent the phase back to Implement:

1. The tracker recorded the orchestrator branch's merge commit, not the default branch SHA that the tick compares with.
2. `--remove` refuses an unmerged branch, and the stop and Done status commits land after the phase's last merge.
3. Merging a phase step 7 (`stop`, `--close`) read as also running after a failed post-merge check.

## Verify 2, code head `e0a51a20465f216f54eb5aca4fef91810d643eab`, VERIFIED

A fresh verifier re-read the handbook at `b4844d8`, updated the check file to match it (commit `e0a51a2`: tick order, the tracker's default-branch commit, the Done merge before `--remove`, no `stop` after a failed check, and a new cold read E), and reran everything.

| Check | Result |
| --- | --- |
| 1. Primitives and root manifest | PASS. `94 primitives valid`; `check_root_manifest: 12 listed, 19 reached` |
| 2. Markdown lint | PASS. 7 files, 0 errors |
| 3. Line budgets | PASS. `SKILL.md` 103/150, `handbooks/orchestrator.md` 158/200 |
| 4. Routes | PENDING, allowed |
| 5. Package isolation | PASS |
| 6. Launcher tests | PENDING. `packages/s-stack/tests` absent |
| 7. Tier 1, outside the sandbox | PASS. `all Tier 1 structural checks passed across 20 packages` |
| 8. Phase check files | PASS. `foundation` cold reads 1 to 3 and C2 script; `orchestrator-handbook` cold reads A to E |

Every **Done when** item was met, and a grep for private names found nothing. Minor notes left for Review: a waiting hand-written default-branch conflict re-sends `fix-round` each tick; no action is given when a planner branch fails its path check; tick step 3 does not repeat the hold from Merging a phase step 5; the architecture page's commit is recorded after the tracker commit; "reached PR" and "scheduling" are not defined.

## Review 1, code head `e0a51a20465f216f54eb5aca4fef91810d643eab`, SIGNIFICANT

p-stack's `interrogate` ran two adversaries in their own worktrees, one on Opus and one on Fable. The configured Gemini seat is not available in Claude Code and was dropped. Each adversary had the diff, the skill's `SKILL.md` and reference, and no `.foundry/`. The phase session reran each scripted repro and checked each cold-read finding against the handbook's text.

| Finding | Adversaries | Proof |
| --- | --- | --- |
| After a hook refuses a commit and rewrites a staged lockfile, `git merge --abort` fails (`Entry 'lock.json' not uptodate`, exit 128) and leaves `MERGE_HEAD`. The next merge fails with `You have not concluded your merge`. | Opus, Fable | Scratch-repository scripts, both rerun |
| The phase merge computes the code head from the branch, then merges a separately read tip SHA. A commit in between is merged unverified. | Opus | Scratch-repository script, rerun |
| After a failed post-merge check, the freeze in Merging a phase step 5 collides with Merging the default branch step 6 and with steps 2 and 3. Tick Merge still runs, and the failing phase's old verdicts still name its current head. | Opus, Fable | Three cold reads |
| A phase in PR waiting for the one-merge-per-tick queue, and a planner that has finished, both meet the stall definition and get replaced. | Fable | Cold read |
| At Done, `--remove` runs while the session just started to record Done is still live. Check file cold read B, expected point 5, encodes the same order. | Fable | Cold read, and a rerun of cold read B |
| "Merge at most one phase per tick, so each later phase merges the newest orchestrator branch" is false for phases already in PR, which never get `merge-orchestrator-branch`. | Fable | Cold read |

Cold reads A and B of the check file were rerun by the Fable adversary and matched.

## Verify 3, code head `60e66c4203ece3b7a049358bdbb05eff9ab95f07`, VERIFIED

A fresh verifier updated the check file for `fc9c6cd` (commit `60e66c4`: cold reads A, B and D updated, new cold reads F, G and H, and a scratch-repository script for the blocked-abort recovery) and reran everything. C6 checks 1, 2, 3, 5, 7 and 8 PASS (`160/200 handbooks/orchestrator.md`; `all Tier 1 structural checks passed across 20 packages`; foundation cold reads 1 to 3; cold reads A to H; `blocked abort recovered`). Checks 4 and 6 are PENDING, which is allowed. Every **Done when** item was met.

Three gaps that it judged would break a real run sent the phase back to Implement:

1. Tick Start knew only dependencies merged into the orchestrator branch, not those the plan requires to be Done.
2. The freeze skipped tick step 3, which also held the stall replacement, so a stalled frozen phase could never be replaced.
3. `needs_update` stayed true for good when the default branch moved again without touching a package.

It also noted that the board section seeded `phases` documents "when you publish", before any feature plan exists.

## Verify 4, code head `ca4e3b67d6a3a79db36ecb8895578bdbba310c2e`, VERIFIED

A fresh verifier updated the check file for `693d8b2` and the merge of `spec-planner-handbooks` (commit `ca4e3b6`). It covers a frozen tick that still replaces a stall, a dependency that must be Done, a repeated generated-only round on a docs-only move, and seeding at the first `done-planning`. It reran everything. C6 checks 1, 2, 3, 5, 7 and 8 PASS (`161/200 orchestrator.md`; Tier 1 across 20 packages; 13 cold reads across three check files; the abort script). Checks 4 and 6 are PENDING, which is allowed. Every **Done when** item was met.

One remaining item misleads a reader. The resend rule for `needs_update` sat inside a section that tick step 2 runs only for package-changing moves. The phase moved back to Implement to fix it, and also to say where a Done phase's status is read and to scope the `done-planning` board write.

## Verify 5, code head `7ccd3ee91dc0e7d8a18cce43d64f663678b8ed8f`, VERIFIED

A fresh verifier updated cold reads E(3) and B(2) for `22a1695` (commit `7ccd3ee`) and reran everything. C6 checks 1, 2, 3, 5, 7 and 8 PASS (`160/200 orchestrator.md`; Tier 1 across 20 packages; 13 cold reads across three check files; the abort script). Checks 4 and 6 are PENDING, which is allowed. Every **Done when** item was met. Nothing remaining breaks a real run.

Notes recorded and not fixed, because each repeats a correct message and leads no reader to a wrong action:

- In the tick that first sets `needs_update`, the any-move resend can read as a second generated-only round.
- While a default-branch merge stays aborted, each tick retries it and resends the same `fix-round` or notice.
- Several timings are not stated: when the `needs_update` clearing test runs, where the Done merge sits relative to the one-merge limit and the freeze, the seeding of a newly added phase, the meaning of a "newer" code head, and the tracker's first default-branch commit.

## Review 2, code head `7ccd3ee91dc0e7d8a18cce43d64f663678b8ed8f`, SIGNIFICANT

`interrogate` over the commits since `e0a51a2`, with two adversaries on Opus and Fable in their own worktrees. The Gemini seat was dropped. The phase session reran each script and checked each cold read against the text.

| Finding | Adversaries | Proof |
| --- | --- | --- |
| The freeze skips all of tick step 2, the only route to "When a feature pull request lands". A pull request that landed during a freeze sets no `needs_update`, so the board shows stale pull requests as ready. This regression came from Review 1's fix round. | Opus, Fable | Two cold reads; text at line 65 |
| When the hook rewrites a tracked file that the merge did not touch, `git merge --abort` succeeds and keeps the rewrite. The next merge then fails (`Your local changes ... would be overwritten`) every tick. | Fable | Scratch-repository script, rerun |
| The check file's cold read H spells the generated-path exclude as `':(exclude)**/lock.json'`, which misses a root `lock.json`. `':(exclude,glob)**/lock.json'` matches it. | Fable | Scratch-repository script, rerun |

## Verify 6, code head `5af461837620e10ebf182320e1aaa4546bb60a0d`, VERIFIED

A fresh verifier updated the check file for `7b296da` (commit `5af4618`). It removed run results to follow the no-evidence-exception run decision, turned the command-line grep into a rerunnable script, used the glob form in cold read H, updated cold reads D and F, added cold read I (a landing during a freeze), and extended the abort script to a hook that rewrites an untouched file. It then reran everything. C6 checks 1, 2, 3, 5 and 7 PASS (`160/200 handbooks/orchestrator.md`; `all Tier 1 structural checks passed across 20 packages`). Checks 4 and 6 are PENDING, which is allowed. Check 8 PASS: 14 cold reads across three check files, the launcher-call script and the abort script. The verifier did not run `foundation`'s status-header script, so the phase session ran it at the same head: `reference matches C2 apart from the allowed differences`, exit 0.

One-off results at `5af4618`:

- The handbook has 160 lines.
- A case-insensitive grep for workmux, tmux and claude finds only prose: "workmux shows it idle", "workmux's status", and Claude Code's scheduled task and push notification tool.
- The only long options are the launcher flags and the git options `--no-ff`, `--no-commit`, `--abort`, `--is-ancestor`, `--porcelain` and `--untracked-files`.
- A grep of the phase's files and commit messages for the private names found 0 hits.

One item misleads a reader. Done handling sat inside step 2's once-per-commit duty, while a freeze forbids other merges. A skipped Done merge was never retried, and `--remove` would then refuse. The phase moved back to Implement.

## Verify 7, stopped without a verdict

A verifier for `d53722e` was stopped when the orchestrator relayed the developer's cross-phase stacking instruction. Its partial check-file commit `b494dbd` was kept for the next verifier to judge.

## Verify 8, code head `5658aa8edf80e0e427f8afa9568117cc59be86ed`, VERIFIED

A fresh verifier judged `b494dbd`, updated the check file for `d53722e` and `efb61c5` (commit `5658aa8`: restack expectations removed, a base `fix-round` for dependants, the expected force-push, cold read J for Finishing a phase), and ran every check. C6 checks 1, 2, 3, 5 and 7 PASS (`168/200 orchestrator.md`; Tier 1 across 20 packages). Checks 4 and 6 are PENDING, which is allowed. Check 8 PASS: `foundation`'s status-header script, the launcher-call script and the abort script, and 15 cold reads across three check files. Every **Done when** item was met.

One-off results at `5658aa8`:

- The handbook has 168 lines.
- A case-insensitive grep finds workmux, tmux and claude only in prose.
- The only long options are the launcher flags and six git options.
- A private-name grep of the phase's files, diff and commit messages found 0 hits.

Defects that sent the phase back to Implement:

- The pane-close step in Finishing a phase fires on any stop commit. That includes the old one on a session restarted to record Done, so it breaks a real run.
- "They hold only status" is asserted, not checked. That misleads a reader.
- The freeze's "start no phase" conflicts with starting a session for Done. That is minor.

## Verify 9, code head `942257045154f4a7e76c16fa4023a5cf3e656bf5`, VERIFIED

A fresh verifier updated the check file for `4289747` and the merge of `phase-handbooks` (commit `9422570`, with a new cold read K) and ran every check. C6 checks 1, 2, 3, 5 and 7 PASS (`170/200 orchestrator.md`; Tier 1 across 20 packages). Checks 4 and 6 are PENDING, which is allowed. Check 8 PASS: three scripts, and 20 cold reads across four check files. Every **Done when** item was met. The handbook has 170 lines, a case-insensitive grep finds workmux, tmux and claude only in prose, and a private-name grep with a positive control found 0 hits.

Two probes outside the check file, each reading `orchestrator.md` with `phase-session.md`, found defects that break a real run:

1. The orchestrator restarted a session for Done and sent `stop`, but never told it that every pull request had merged. `phase-session.md` moves to Done only on that notice, so the phase loops in PR.
2. A session woken by a message to an open pane records no new start time. The start-time rule then counts it as stopped and closes its pane mid-work. One example is a Done phase sent `move-back`.

A re-merge at an already merged code head was not excluded, which misleads a reader. The phase moved back to Implement, and "Finishing a phase" is redesigned on the orchestrator's own record of the `stop` messages it sent, not on commit timing.

## Verify 10, code head `7b4f0a3362f57084a329061311644e9d05559bc4`, NOT VERIFIED

A fresh verifier updated the check file for `13fe92c` (commit `7b4f0a3`). It updated cold reads A, B, F, J and K, and added L (the Done handshake with `phase-session.md`), M (a `move-back` to a Done phase over three ticks), N (no re-merge at a merged code head) and O (the layout lines). It then ran every check. C6 checks 1, 2, 3, 5 and 7 PASS (`169/200 handbooks/orchestrator.md`; Tier 1 across 20 packages). Checks 4 and 6 are PENDING, which is allowed. Check 8 FAILS: every script passes, and 23 of 24 cold reads pass. Cold read M fails on point 3.

The failure: Finishing a phase step 2 sends "every pull request has merged" to any phase not in Done. A phase moved back to Implement after Done gets the notice again, because starting it reset the record of having told it. `phase-session.md` then moves it to Done, and the new code never gets a verdict.

Other findings, each misleading a reader:

- A pane can close in the same tick its `stop` was sent, because the idle reading predates the `stop`.
- The one-merge reason is false when the default branch merged in the same tick.

One minor item: the update spec writer's pane is never closed.

One-off results at `7b4f0a3`:

- The handbook has 169 lines, and the launcher-call script passes.
- All nine launcher flags match `launch.sh`'s usage text on the `launcher` phase branch.
- A private-name grep found 0 hits, with a positive control of 3.

## Verify 11, code head `aa1691c294db133b3d809d901732719cc55b6097`, INCONCLUSIVE

A fresh verifier updated the check file for `63e2e35` (commit `aa1691c`, with a new cold read P) and ran every check. C6 checks 1, 2, 3, 5 and 7 PASS. Checks 4 and 6 are PENDING, which is allowed. In check 8, all three scripts pass and 24 of 25 cold reads pass. Cold read K was still running when the verifier handed back, so the verdict is INCONCLUSIVE. Every **Done when** item that ran was met (169 lines; a private-name grep found 0 hits, with a positive control of 3).

Two defects would break a real run:

- The "every pull request merged" notice did not check that the phase's current code head was merged, so a Done phase with new code but no new pull request could loop.
- A stalled session got `stop` and `--close` in the same tick, the race already fixed for merged phases.

Minor items:

- It was not stated whether status-only merges are exempt from the default-branch-tick rule, or whether an aborted default-branch merge counts.
- The tracker did not record when stopping began, or clear the mark.
- Resizing panes was not ruled out.

## Verify 12, code head `5831c24172b69250013c6355b521cd195a755958`, VERIFIED

A fresh verifier updated the check file for `b5cc777` and `0f37a7b` (commit `5831c24`, with a new cold read Q) and ran every check to completion. C6 checks 1, 2, 3, 5 and 7 PASS (`169/200 handbooks/orchestrator.md`; Tier 1 across 20 packages). Checks 4 and 6 are PENDING, which is allowed. Check 8 PASS: three scripts and 26 cold reads across four check files. Every **Done when** item was met.

One-off results at `5831c24`:

- The handbook has 169 lines.
- A case-insensitive grep finds workmux, tmux and claude only in prose.
- All nine launcher flags appear in `launch.sh`'s usage text on the `launcher` phase branch.
- A private-name grep found 0 hits, with a positive control of 3.

One defect breaks a real run. A phase sent back after Done, whose pull requests have all merged, returns to PR with no open pull request for its new code. Whether it then merges, or waits for good, depended on how "lists its open pull requests" is read. The orchestrator side is fixed by requiring at least one open pull request. Opening one for that code belongs to `phase-session.md` and the PR creator, and was reported to the orchestrator. The phase moved back to Implement.

## Verify 13, code head `03d289910511be372577e92aa690b0088836b4a5`, VERIFIED

A fresh verifier updated cold reads F, M, N and Q for `131526e` (commit `03d2899`) and ran every check to completion. The code head was computed under the run's generated-files rule: `af6d5ff` changed only a `version:` line outside lockfiles. C6 checks 1, 2, 3, 5 and 7 PASS (`169/200 handbooks/orchestrator.md`; `all Tier 1 structural checks passed across 20 packages`). Checks 4 and 6 are PENDING, which is allowed. Check 8 PASS: three scripts and 26 cold reads across four check files.

Every **Done when** item was met:

- The handbook has 169 lines, and no code span or fenced block starts with workmux, tmux or claude.
- All nine launcher flags appear in `launch.sh`'s usage text on the `launcher` phase branch.
- A private-name grep found 0 hits, with a positive control of 6.

Recorded and not fixed: a phase still in PR whose code moved after every pull request merged has no step. It is the same cross-phase gap as Verify 12's. `phase-session.md` neither moves back on its own new code nor opens a pull request for it, and a `move-back` from the orchestrator would only turn the wait into a loop until it does. It was reported to the orchestrator for `phase-handbooks` and `pr-handbook`. Other minor notes:

- A docs-only default-branch move leaves an already cleared `needs_update`, which matches C7.
- No action is given for a failing planner path check.
- The architecture page's commit is recorded after the tracker commit.

## Review 3, code head `03d289910511be372577e92aa690b0088836b4a5`, SIGNIFICANT

`interrogate` over the commits since `7ccd3ee`, with two adversaries on Opus and Fable in their own worktrees. The phase session checked each cold-read finding against the text and reran the git probe.

| Finding | Adversaries | Proof |
| --- | --- | --- |
| A phase whose pull request the developer merges before the orchestrator merges the phase can never merge, because of the open-pull-request rule from `131526e`. It never reaches Done, and its dependants never start. | Opus, Fable | Two cold reads |
| A merged phase's pane, reopened for a generated-only round, is never stopped again before Done. That starves new starts when the window is full. | Opus | Cold read |
| The "every pull request merged" notice can reach a phase whose post-merge check failed. | Fable | Cold read |
| A refused status-only merge sends a Done phase `merge-orchestrator-branch`. That moves its code head with no code of its own (probe D) and strands it. | Fable | Scratch-repository script, rerun; cold read |
| A pull request whose `needs_update` was already true gets two generated-only rounds in a tick where a feature pull request lands. | Fable | Cold read |
| The base `fix-round` and the developer's restack request have no handler that matches across the handbooks. | Opus, Fable | Cold reads |

## Verify 14, code head `ac632959e2a8aef4ba50e9e4c24b5305017fb475`, INCONCLUSIVE

A fresh verifier updated the check file for `bab4569` (commit `ac63295`, with new cold reads R to V) and ran every check. C6 checks 1, 2, 3, 5 and 7 PASS (`170/200 orchestrator.md`; Tier 1 across 20 packages). Checks 4 and 6 are PENDING, which is allowed. In check 8, all three scripts pass and 30 of 31 cold reads pass. Cold read Q had not reported at hand-back, so the verdict is INCONCLUSIVE.

Defects it named:

- The idle-phase `stop` fired on one idle reading, so a session mid-round could be stopped. This breaks a real run, and is inferred.
- A Done phase reopened for a fix round was stopped with no idle check, which misleads a reader.
- A refused status-only merge whose cause is not the phase's own file loops, which misleads a reader.

The phase moved back to Implement. The redesign replaces every single idle reading with one "quiet" test: idle at this tick and the previous tick, with no new commit between them. It folds in the orchestrator's message mapping onto `phase-session.md`'s handlers and its new merge condition for a phase whose fix pull request merged first.

## Verify 15, code head `d66a4cb92e56a7c3f70625a3d6b124f71974fb3e`, VERIFIED

A fresh verifier updated the check file for `c19dfe0` (commit `d66a4cb`, with new cold reads W and X, and quiet-gated timings throughout) and ran every check to completion. C6 checks 1, 2, 3, 5 and 7 PASS (`169/200 orchestrator.md`; `all Tier 1 structural checks passed across 20 packages`). Checks 4 and 6 are PENDING, which is allowed. Check 8 PASS: three scripts and 33 cold reads across four check files.

Every **Done when** item was met:

- The handbook has 169 lines, and no command line appears.
- All nine launcher flags appear in `launch.sh` on the `launcher` phase branch.
- A private-name grep found 0 hits, with a positive control of 15.

Fixed in the next round, as the handbook's own contradiction:

- The merge rule let a phase merged before re-merge on any pull request merged since the last merge. That contradicts Finishing a phase, which needs a new pull request holding the new code, and it lets unreviewed code reach Done.

## For the cross-handbook integration

Recorded under the orchestrator's run decision, for its read-through once every handbook has merged:

- `orchestrator.md` sends a `fix-round` of the kind "A pull request merged". `phase-session.md` on `s-stack-package` handles only "Generated files only". The new kind exists only on the unmerged `phase-handbooks` branch.
- A phase in PR whose code moved after every pull request merged has no step. Both `phase-session.md` and the PR creator are involved, as recorded at Verify 12 and Verify 13.
- `phase-session.md`'s `stop` handler commits the status file even when nothing changed. Whether that makes a commit sets the quiet timing of the pane close.
- Minor gaps in `orchestrator.md` for that read-through:
  - quiet is undefined for a planner or spec writer;
  - a stalled session's `--close` has no quiet test;
  - "its own status files" is undefined, and a status-file conflict with the orchestrator branch has no fix path;
  - a failing default-branch merge is retried every tick.

## Verify 16, code head `7fc56cf30188c760809d2827c628f575d9564707`, VERIFIED

A fresh verifier updated the check file for the re-merge rule and the merged `phase-session.md` (commit `7fc56cf`, with a new cold read Y) and ran every check. C6 checks 1, 2, 3, 5 and 7 PASS (`169/200 orchestrator.md`; Tier 1 across 20 packages). Checks 4 and 6 are PENDING, which is allowed. In check 8, three scripts and 33 of 34 cold reads pass. Cold read Q did not report before hand-back, so a second fresh verifier reran Q alone at the same head, and it passed.

Every **Done when** item was met:

- The handbook has 169 lines, and no command line appears.
- All nine launcher flags appear in `launch.sh` on the `launcher` phase branch.
- A private-name grep found 0 hits, with a positive control of 5.

The later merge of `s-stack-package` (`7409b48`, `main` up to pull request 85) at `e4cca82` changed only s-stack's `version:` line outside lockfiles, so the code head stays `7fc56cf`.

More for the cross-handbook integration:

- The re-merge test uses commit time as a stand-in for "a pull request holds the new code". It depends on `pr-creator.md`.
- It is not stated whether phase merges wait while a default-branch merge keeps failing.
- The repeat "A pull request merged" round for an already set `needs_update` does not say what it names.
- `stop` and the merged notice can be sent in the same tick.

## Review 4, code head `7fc56cf30188c760809d2827c628f575d9564707`, SIGNIFICANT

`interrogate` over the commits since `03d2899`, with two adversaries on Opus and Fable in their own worktrees. The phase session reran all three git probes.

| Finding | Adversaries | Proof |
| --- | --- | --- |
| The re-merge rule's commit-time test admits code that no pull request holds. An old pull request merged after the fix commit, but before the PR creator carried the fix, passes it. | Opus | Scratch-repository script, rerun; cold read |
| Once a phase's code head is a merge commit, the time test can never pass again, although its merged pull request holds all its code. This follows a conflicted re-merge, or a default-branch conflict round. | Fable | Two scratch-repository scripts, rerun; two cold reads |
| A refused status-only merge whose cause the phase cannot fix loops every four ticks, and never reaches the developer. | Opus | Cold read |
| "A pull request merged" rounds go to phases not in PR, while `phase-session.md`'s handler assumes PR. A PR creator could carry unverified commits. | Opus | Cold read |

The fix replaces the time test with the roadmap's own trigger: a phase merges once it has reported its pull requests open (`prs-open`) at its current code head.

## Verify 17, code head `ed173c2ca71aa2787219af0a31b9b79144a76b7b`, NOT VERIFIED

A fresh verifier updated the check file for `3276b54` (commit `ed173c2`, with new cold reads Z and AA) and ran every check. C6 checks 1, 2, 3, 5 and 7 PASS (`169/200 orchestrator.md`; Tier 1 across 20 packages). Checks 4 and 6 are PENDING, which is allowed. Check 8 FAILS: the three scripts pass and 34 cold reads pass, but cold read Z fails and cold read T was unfinished at hand-back.

Defects that break a real run, on merged contracts:

- Limiting rounds to phases in PR also stopped `needs_update` being set for pull requests of other phases, so the deferred round never fires and a stale pull request shows as ready.
- The resend for a `needs_update` already true had no in-PR condition.

Defects that mislead a reader:

- The restart request for `prs-open` did not say "once a pull request holds your code head".
- The fix-round sentence's "merge it again" left out the `prs-open` condition.

Minor: the tracker had no field for a status-only refusal awaiting the developer.

## Verify 18, code head `912605a97e15e20e50353ec451f3cc1b870a1a01`, VERIFIED

A fresh verifier updated cold reads I, J and Z for `9537a1d` (commit `912605a`) and ran every check. C6 checks 1, 2, 3, 5 and 7 PASS (`170/200 handbooks/orchestrator.md`; `all Tier 1 structural checks passed across 20 packages`). Checks 4 and 6 are PENDING, which is allowed. In check 8, three scripts and 35 of 36 cold reads pass. Cold read T did not finish before hand-back, so a second fresh verifier reran T alone at the same head, and it passed.

Every **Done when** item was met:

- The handbook has 170 lines, and no command line appears.
- All nine launcher flags appear in `launch.sh` on the `launcher` phase branch.
- A private-name grep found 0 hits, with a positive control of 3.

Items to fold into the next fix round, each misleading a reader:

- No tick step owns the deferred "A pull request merged" round when the default branch has not moved.
- A merge whose post-merge check failed may read as "a phase merged" for the architecture page.

Minor items:

- The new tracker field never says when it clears.
- A pull request opened after the landing tick has no starting `needs_update`.

## Review 5, code head `912605a97e15e20e50353ec451f3cc1b870a1a01`, SIGNIFICANT

`interrogate` over the commits since `7fc56cf`, with two adversaries on Opus and Fable in their own worktrees. The phase session checked each cold read against the text and reran the git probe.

| Finding | Adversaries | Proof |
| --- | --- | --- |
| `phase-session.md`'s code-changing fix rounds ("Feedback on a pull request", "A conflict with the default branch") never send `prs-open`, so the phase can never merge again under the `prs-open` rule. | Opus | Three cold reads |
| A deferred "A pull request merged" round goes out in the same tick as the re-merge's `stop`. The phase ends its turn without refreshing, and the round is never resent. | Fable | Three cold reads |
| A stacked child pull request flagged after its parent's fix round gets no round, and the clearing test passes on a head that lacks the parent's fix. | Fable | Scratch-repository script, rerun; cold read |

## Verify 19, code head `92b307924868de977ec658b79820b92557ef752e`, VERIFIED

A fresh verifier updated the check file for `caafc7f` (commits `fd7658e` and `92b3079`, with new cold reads AB, AC and AD) and ran every check at the final head. C6 checks 1, 2, 3, 5 and 7 PASS (`170/200 orchestrator.md`; Tier 1 across 20 packages). Checks 4 and 6 are PENDING, which is allowed. Check 8 PASS: three scripts and 39 cold reads across four check files. One cold read, J, gave an answer that contradicted the file, and passed on a fresh rerun.

Every **Done when** item was met:

- The handbook has 170 lines, and no command line appears.
- All nine launcher flags appear in `launch.sh` on the `launcher` phase branch.
- A private-name grep found 0 hits, with a positive control of 3.

Queued for the next fix round:

- A stacked child's flag has a second clearing rule that can never hold once its parent is squash-merged. This breaks a run, in an edge case, and is inferred.
- A flag on a pull request that has since merged never clears, and blocks `stop`. This misleads a reader.
- No tick step owns clearing `needs_update`. This misleads a reader.

Minor items:

- The step 4 requests repeat every quiet tick.
- Merge step 7's `stop` has no quiet condition.
- Cold read V's instruction conflicts with its point 5.

## Review 6, code head `92b307924868de977ec658b79820b92557ef752e`, SIGNIFICANT

`interrogate` over the commits since `912605a`, with two adversaries on Opus and Fable in their own worktrees. The phase session reran both git probes and checked each cold read against the text.

| Finding | Adversaries | Proof |
| --- | --- | --- |
| A stacked child's flag clears only on ancestry of one fixed commit. A parent refreshed by rebase removes that commit, so the child never clears, never gets `stop`, and gets a round on every quiet tick. | Opus | Scratch-repository script, rerun; cold read |
| A grandchild in a stack is never flagged after its grandparent's fix, and shows as ready on a stale head. | Fable | Scratch-repository script, rerun; cold read |
| Step 4 resends an "A pull request merged" round for a flag a fix round set, naming an unrelated commit. A phase in PR with a flagged pull request can also read as stalled. | Fable | Two cold reads |
| A roadmap update merged during a freeze lets the architecture page show a merge that failed its check as built. | Fable | Cold read |

Together with the three queued `needs_update` items, these show the flag's design was wrong: it tracked one fixed commit, and one level of a stack. The fix replaces it with one readiness rule based on current state.

## Verify 20, code head `5976721323ca91e4e3b2cdd071c45fe731215e9d`, NOT VERIFIED

A fresh verifier rewrote the check file for the `needs_update` redesign (commit `5976721`, with new cold reads AE to AH) and ran every check. C6 checks 1, 2, 3, 5 and 7 PASS (`170/200 orchestrator.md`; Tier 1 across 20 packages). Checks 4 and 6 are PENDING, which is allowed. Check 8 FAILS: all scripts pass, and 42 of 43 cold reads pass. Cold read AH fails, and B and AD passed only on assumptions their readers named.

Defects that break a real run, on merged contracts:

- Tick step 4 told only a quiet phase about flagged pull requests, and a closed pane is never quiet. Merged phases' pull requests would never be refreshed.
- A roadmap update that changes a phase's behaviour, but adds or removes no phase, left that phase in Spec for good.

One defect misleads a reader: the refresh instruction was sent for a pull request flagged only by pending or failed checks.

Minor items:

- The test followed only direct `depends_on`.
- The round named "the feature pull request that landed", which is no longer recorded.

For the integration read-through: C5's `needs_update` wording, and the board template's schema comment, should match the up-to-date test.

## Verify 21, code head `038cdc4e65eae7cf6bbe9c447f9d290ece02bce7`, VERIFIED

A fresh verifier updated cold reads B, AD, AF, AH and the round-naming reads for `20c031a` (commit `038cdc4`) and ran every check. C6 checks 1, 2, 3, 5 and 7 PASS (`170/200 orchestrator.md`; `all Tier 1 structural checks passed across 20 packages`). Checks 4 and 6 are PENDING, which is allowed. Check 8 PASS: three scripts and 43 cold reads across four check files, all on their first run.

Every **Done when** item was met:

- The handbook has 170 lines, and no command line appears.
- All nine launcher flags appear in `launch.sh` on the `launcher` phase branch.
- A private-name grep of the phase diff and commit messages found 0 hits, with a positive control of 6.

Queued for the next fix round:

- The architecture page subagent's brief does not name which merges passed their check. This misleads a reader.

For the cross-handbook integration:

- A dependency reached through another is named as the refresh target, which depends on `pr-creator.md`.
- A phase the restarted planner leaves unchanged is never sent `move-back` to Plan.
- A `move-back` to Plan during a freeze.
- Step 7's `stop` has no quiet test.

Outside this phase: the roadmap's `decisions.md` names a private file that is meant to stay untracked. It was reported to the orchestrator.

## Review 7, code head `038cdc4e65eae7cf6bbe9c447f9d290ece02bce7`, SIGNIFICANT

`interrogate` over the commits since `92b3079`, with two adversaries on Opus and Fable in their own worktrees. The phase session checked each finding against the handbook text.

| Finding | Adversaries | Proof |
| --- | --- | --- |
| A dependency force-pushed to drop a commit still passes the ancestry test, so its child turns ready while it carries the dropped commit. | Opus | Scratch-repository script; cold read |
| A dependency closed without merging drops out of the test, but its commits stay in the child. | Opus | Scratch-repository script; cold read |
| A stacked child merged into its parent's branch counts as merged into the default branch, and its phase is told so. | Opus | Scratch-repository script; cold read |
| A phase in PR that ignores a fix round is never followed up, because a phase in PR was made unstallable. | Fable | Cold read |
| A default-branch conflict round and a refresh round go to one phase in one tick, and the second then runs outside PR. | Fable | Cold read |
| The restarted planner is told nothing, and can never count as stalled. | Fable | Cold read |
| A pull request that lacks both the tip and a dependency's head gets two messages in one tick. | Fable | Cold read |

The check file's cold read Z gives a wrong reason for `kaph` in its expected answer, although the scored outcome is right. The verifier owns that file.

## Verify 22, stopped without a verdict

The verifier for `2056fdb` was stopped before it committed anything, when the orchestrator set the common-path significance bar and asked for "Histories handled by asking".

## Verify 23, code head `e0fcca779f7f839dc14510f983f49ae344696b06`, NOT VERIFIED

A fresh verifier updated the check file for `2056fdb` and `e1e7917` (commits `a9e54cc` and `e0fcca7`, with new cold reads AI, AJ, AK and D(8)) and ran every check twice. C6 checks 1, 2, 3, 5 and 7 PASS (`182 handbooks/orchestrator.md`; Tier 1 across 20 packages). Checks 4 and 6 are PENDING, which is allowed. In check 8, three scripts pass and 45 of 46 cold reads pass, three of them on a fresh reader. Cold read I fails on its own wording, not on the handbook.

Defects that break the common path, found by probe cold reads:

- A message counts as answered only by a commit or a state change. A refresh round (answered by a push and `prs-open`) and a `prs-open` request (answered by the message) stay unanswered. Correct phases then stall and loop through `--fresh` replacements.
- A hand-written conflict with the default branch is retried, and its round resent, every tick. The owning phase restarts both gates each time and never returns to PR.

Defects that mislead a reader:

- The rare-histories list literally includes the expected rebase of a stack child.
- Step 7's `stop` is cancelled in the same tick by the merged notice.

Minor: it is unclear whether reconcile and board writes continue for paused phases.

## Verify 24, code head `d5c3d09a02a0fde2e434bd62895c1b3f7c888769`, VERIFIED

A fresh verifier updated the check file for `b33f4a5` (commit `d5c3d09`, with new cold reads AL and AM, and its own Verify 23 flaws fixed) and ran every check. C6 checks 1, 2, 3, 5 and 7 PASS (`182/200 handbooks/orchestrator.md`; `all Tier 1 structural checks passed across 20 packages`). Checks 4 and 6 are PENDING, which is allowed. Check 8 PASS: three scripts and 48 cold reads across four check files. One cold read, AK, was rerun because of an ungrounded side argument.

Every **Done when** item was met:

- The handbook has 182 lines, and no command line appears.
- A private-name grep of the phase files, diff and commit messages found 0 hits.

One item misleads a reader, and the run converges past it. In the tick a phase returns to PR after a hand-written default-branch conflict, the default-branch retry runs before the phase merges, so one redundant conflict round goes out. Minor: the conflict tip is never cleared, and a phase just sent a conflict round can literally meet the stall test in the same tick.

## Merge of `s-stack-package` at `7daf642`, under run decision `launcher-r3`

`s-stack-package` (`a606589`, which brings `board`) was merged at `7daf642`. Outside `.foundry/` the merge touched `packages/s-stack/.apm/skills/sam-mode/assets/status-board.html` and `tests/s-stack/verify-s-stack/checks/board.md`, both owned by `board`, plus the generated `packages/s-stack/apm.lock.yaml`, whose lockfile-only conflict was resolved under C7. None is an owned path of this phase, so the code head and verdicts stay at `d5c3d09`.

## Review 8, code head `d5c3d09a02a0fde2e434bd62895c1b3f7c888769`, SIGNIFICANT

`interrogate` over the commits since `038cdc4`, under the orchestrator's common-path bar, with two adversaries on Opus and Fable in their own worktrees. Each walked a whole feature lifecycle. The phase session checked each finding against the text.

| Finding | Adversaries | Proof |
| --- | --- | --- |
| A stalled phase replaced with `--fresh` loses its unanswered `fix-round`, so the review comment is never addressed and the replacement repeats. | Opus | Cold read |
| After a hand-written default-branch conflict, the retry runs before the phase re-merges, and merge step 7's same-tick `stop` leaves the phase in Implement with a closed pane for good. | Opus, Fable | Git probe; three cold reads |
| On a guarded tick, the default-branch merge runs before the guard and is never aborted, so later merges fail with unmerged files. | Fable | Git probe; cold read |
| A phase sent to Spec by a roadmap update stays there if the restarted planner leaves its entry unchanged. | Fable | Cold read |
| A crash just after the "every pull request merged" notice leaves the phase marked told, with the notice lost, so it stays in PR. Lower confidence. | Fable | Cold read |

Both lifecycle walks otherwise reached Done for every phase, with each merged code head covered by both verdicts and no stale pull request shown as ready.

## Verify 25, code head `5b8a48145a2aa1e0ef5c890d5516da78f7b785a4`, VERIFIED

A fresh verifier updated the check file for `37d9146` (commits `94802ee`, `d504b46` and `5b8a481`, with new cold reads AN, AO, AP and AQ, and two expected answers corrected after runs). It reran everything after each commit. The verdict rests on the third run. C6 checks 1, 2, 3, 5 and 7 PASS (`183/200 orchestrator.md`; `all Tier 1 structural checks passed across 20 packages`). Checks 4 and 6 are PENDING, which is allowed. Check 8 PASS: the board's headless-Chrome check, the three other scripts, and 52 cold reads across four check files. One read, J, was rerun after an answer that contradicted its own scenario.

Every **Done when** item was met:

- The handbook has 183 lines, and no command line appears.
- A private-name grep of the phase diff, commit messages, plan, status, evidence, handbook and check file found 0 hits.

No defect breaks the common path. For the cross-handbook integration:

- Restarts never say to rerun `--print-window` after a tmux crash. This depends on the launcher.
- Restarts do not order the resend against the tick.
- A commit on `stop` could count as answering an unanswered round. This depends on `phase-session.md`.
- The conflict tip is never cleared.
- "scheduling" is defined only in the board template.
- `phase-session.md`'s `stop` commit is unclear, and its Moving back timing to Plan is worded wrongly.

## Review 9, code head `5b8a48145a2aa1e0ef5c890d5516da78f7b785a4`, SIGNIFICANT

`interrogate` over the commits since `d5c3d09`, under the common-path bar, with two adversaries on Opus and Fable in their own worktrees, each walking a whole feature. The phase session checked each finding against the text.

| Finding | Adversaries | Proof |
| --- | --- | --- |
| The commit a stalled session makes on `stop` counts as answering its unanswered review round. The `--fresh` replacement gets nothing, and the phase stays in PR for good. | Opus | Two cold reads |
| The tracker-fact rare history still catches the developer's merge into the default branch and the forge's stack-child rebase. Rated lower. | Opus | Cold read |
| After a failed post-merge check, the idle-phase `stop` in Finishing a phase can still fire, because it has no passing-check clause. Conditional on one reading. | Fable | Cold read |

The Fable walk otherwise reached Done for all three phases, through a roadmap update, a crash with `workmux resurrect`, a failed check and out-of-order merges.

## Verify 26, code head `ac3d7c0e7e46869167b4774f4a3094d37318d745`, VERIFIED

A fresh verifier updated the check file for `07e5d30` (commit `ac3d7c0`, with new cold reads AR, AS and AT) and ran every check. C6 checks 1, 2, 3, 5 and 7 PASS (`183/200 orchestrator.md`; `all Tier 1 structural checks passed across 20 packages`). Checks 4 and 6 are PENDING, which is allowed. Check 8 PASS: the board's 49 headless-Chrome scenarios, the three other scripts, and 55 cold reads across five check files. A grader marked `foundation` cold read 2 FAIL, because the reader also read `poteto-mode` first, as `SKILL.md` line 16 requires. The verifier and the phase session count it as agreeing in substance. The clash between `SKILL.md` lines 16 and 24 is `foundation`'s, and it is on the integration list.

Every **Done when** item was met:

- The handbook has 183 lines, and no command line appears.
- A private-name grep across the phase's files, diff and commit messages found 0 hits.

No defect breaks the common path. For the cross-handbook integration:

- Supervision's stall `--close` timing differs from Finishing's quiet close.
- A round is resent each tick while it is unanswered.
- A phase waiting in Spec has no `waits_for`, so it can be replaced while the planner runs.
- Merge step 7's `stop` has no quiet test.
- "its own status files" is undefined.
- A phase newly added by a later `done-planning` gets no board document.
- `phase-session.md` line 123's timing for `move-back` to Plan is worded wrongly.

## Review 10, code head `ac3d7c0e7e46869167b4774f4a3094d37318d745`, SIGNIFICANT

`interrogate` over the commits since `5b8a481`, under the common-path bar, with two adversaries on Opus and Fable in their own worktrees, each walking a whole feature. The phase session checked each finding against both handbooks.

| Finding | Adversaries | Proof |
| --- | --- | --- |
| A phase answers a review `fix-round` with the state change to Implement. If it then stalls mid-fix, its `--fresh` replacement is sent nothing, the comment is lost, and the pull request is later shown as ready with the comment unaddressed. | Opus | Two cold reads |
| A `move-back` lost in a crash after a failed post-merge check is never resent, because the tracker records only `fix-round` and `instruction`. The orchestrator branch stays frozen for good. | Fable | Two cold reads |

Both walks otherwise reached Done for every phase, with no deadlock or loop and no unverified code merged.

## Verify 27, stopped without a verdict

The verifier for `3743f4c` was stopped before it committed anything, so that the orchestrator's instruction on developer commits could fold into the round.

## Verify 28, code head `7b34b57159794ec529b4f0246d2daedcf1c85c5b`, NOT VERIFIED

A fresh verifier updated the check file for `3743f4c` and `7d40d4e` (commit `7b34b57`, with new cold reads AU to AX) and ran every check. C6 checks 1, 2, 3, 5 and 7 PASS (`185/200 orchestrator.md`; Tier 1 across 20 packages). Checks 4 and 6 are PENDING, which is allowed. Check 8 FAILS: all scripts pass, including the board's 50 Chrome scenarios, and 58 of 59 cold reads pass. Cold read AX case 2 fails.

The defect breaks the common path. A refresh round was answered by a push, and the developer-commit rule relied on "nothing unanswered" to mean the PR creator was not mid-push. So a tick between a PR creator's refresh push and its `prs-open` took the phase's own commits for a developer's. That gap opens after every merge into the default branch.

Defects that mislead a reader:

- A developer-commit round was not named among the rounds that need a `prs-open` at a newer code head.
- `prs-open` carries no heads, so "the head its phase last reported" was undefined.

Minor items:

- GitHub's "Update branch" merge counts as a developer commit.
- The order of restart messages is not stated.
- Check-file gaps: AT point 1 and Z's tick 2.
