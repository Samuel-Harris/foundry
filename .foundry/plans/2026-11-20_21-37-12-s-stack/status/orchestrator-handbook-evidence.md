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
