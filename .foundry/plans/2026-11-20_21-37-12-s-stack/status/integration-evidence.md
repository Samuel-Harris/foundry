# Integration evidence

## Implement

### Fixes made

Every common-path and minor item in `integration-fixes.md`, with these exceptions and additions.

- Cosmetic items F9, F10, F11, P10, P11, S2 and O9 are skipped, because no other fix touches their lines.
- O6: only the line-14 half, by request `integration-r2`, answered A.
- F7's pointer to `planner.md` links its "When the orchestrator starts you again" section, and that section now says the restart comes as an `instruction`, and names a decision as a trigger.
- `verifier.md`'s "None" bullet and its "run everything again" after a check fix now follow the scoped run. Both contradicted P16 as written.
- `reviewer.md` step 4 tells the first reviewer in its brief that it is first, because the brief's waiver rule keys on that.

### Checks updated with the fixes

From a read-only scan of every Rerun check against the fix list (subagent, Opus):

- `foundation.md` cold read 3 points 1, 3 and 5(b) follow F1, F2, F3 and F7. The C2 contract check maps the new verdict wording and leaves out the rules this round added, which the reference owns. A new Rerun check, "Code head in a scratch repository", runs the reference's code-head loop on a built history. It passed (three `ok:` lines), and it failed with the loop's `&& continue` line removed.
- `phase-handbooks.md` cold read 1 now uses a conflicted merge (a clean one no longer moves the code head) and the scoped Verify. Cold read 2 point 2 follows P16.
- `orchestrator-handbook.md`: the preamble and the scratch-repository read describe the recorded head as the `pushed` head (O1). Cold reads BC and BD now expect a refresh `instruction`, because the `pushed` line exposes the developer's commit, which is the gap O1 closes. Seventeen expected answers say the post-merge subagent runs the checks in the merge's blast radius (O2).
- `board.md` line 954 and `pr-handbook.md` line 1518, both Evidence prose, follow P16.

### quick-review, on `git diff bb07229^ 3199199`

Two Opus subagents: the thermo-nuclear bug review and the code-quality review.

Fixed in `d8a1a63`:

- Both: a `WAIVED` verdict that the merge rule does not count left the phase with no route to PR, and a fresh agent could waive again on the same scope. A waiver at a phase's first Verify or Review never counted. Now the phase session's brief says whether the agent may waive, which it may only when the gate's newest verdict that is not `WAIVED` is `VERIFIED` or `CLEAR`.
- Bug review 3: the end-of-feature full run could be skipped by re-merges after review. "Ending the feature" now runs it unless one passed since the last phase merge.
- Bug review 4: a merge that needed no post-merge check did not count as passing in tick step 3, merge step 7 and Finishing a phase. Step 4 now says it counts as passing.
- Bug review 5: the reviewer's scope takes a failed post-merge check and merge from the brief, as the verifier's does.
- Bug review 6: `orchestrator.md`'s reason for never sending `merge-orchestrator-branch` to a Done phase was stale.
- Bug review 7: while the orchestrator branch is frozen, the post-merge check includes the check that failed.
- Quality review 4: the C2 check copied the code-head rule's wording and could not fail on behaviour. Replaced by the scratch-repository check.

Recorded as minor, not fixed:

- Quality 1: the gate baseline is stated in the reference's Waivers rule, `reviewer.md` step 1, `verifier.md`'s scope and `phase-session.md`'s Verdicts. They agree, and moving the recipe is a refactor beyond the fix list.
- Quality 3: "the local orchestrator branch" is stated in `pr-commands.md`, `pr-creator.md` and the phase session's brief, as R2 and P2 place it.
- Quality 5: P15's exception paragraph is dense, the end-of-feature failure does not say which phase the freeze waits on when the owner merged earlier, and the Done-phase status-fix `instruction` has no row of its own. Each is a rare history.
- Quality 6: small paraphrases of the waiver criterion and of the full-run timing.

## Verify 1: VERIFIED at `faa5b867b5747f43174ad66e5260f3347039c72d`, 2026-11-22T15:29:36Z

Fresh Opus verifier, first Verify, scope the whole phase diff, no waiver allowed. Cold reads were answered by fresh Opus readers and graded by fresh Opus graders. Answers saved in the session scratchpad `coldreads/` directory.

- Commits: `2025699` adds `checks/integration.md`, six cold reads for the fixes no other check file reaches. `0740f25` and `faa5b86` make seven cold reads (foundation 1, integration 2, orchestrator E, N, Y and AH) ask for what their unchanged expected answers score, and give AH the reference. Checked: the three commits touch only `tests/s-stack/verify-s-stack/checks/`, and no expected answer changed.
- Skill checks 1, 2, 3, 4, 5 and 7 PASS. Tier 1: `all Tier 1 structural checks passed across 20 packages`, at `2025699` and `0740f25`. Check 6 outside the radius: `launch.sh` and `packages/s-stack/tests/` unchanged.
- foundation: cold reads 1 and 3, the C2 check and the code-head scratch check PASS. Cold read 2 outside the radius (only unchanged `SKILL.md`).
- phase-handbooks: cold reads 1 to 4 PASS.
- spec-planner-handbooks: cold read 1 PASS. Cold read 2 outside the radius (`spec-writer.md`, `SKILL.md` unchanged).
- pr-handbook: script parse, 145 scratch cases (0 failed), line budget and three cold reads PASS.
- orchestrator-handbook: cold reads A to BD (56) PASS, launcher calls, abort recovery and the head-comparison script PASS.
- integration: cold reads 1 to 6 PASS.
- board, launcher: outside the radius.
- Private names: no match in the phase diff or commit messages.
- Gap accepted by the phase session: cold reads whose check text and input files were byte-identical between `0740f25` and `faa5b86` kept their `0740f25` result rather than run a third time. Only check files changed between those heads.

Reader remarks, not scored, recorded as minor:

- `orchestrator.md` merge step 7 sends `stop` without a quiet test: decided by `integration-r2`.
- Whether a failed full run holds back the architecture-page update.
- `phase-session.md` does not name the message that ends a `blocked` wait.
- `phase-session.md` line 14 does not say whether to build to the roadmap while its request is open.
- `reviewer.md`'s opening says Review follows VERIFIED, not VERIFIED or WAIVED.
- No `phases` board document is written for a phase a later `done-planning` adds.

## Review 1: SIGNIFICANT at `faa5b867b5747f43174ad66e5260f3347039c72d`, 2026-11-22T15:38:56Z

`interrogate` over `git diff s-stack-package...s-stack-phase-integration`, excluding `.foundry/` and lockfiles. The intent came from the commit messages. First reviewer: Opus, briefed as first and not allowed to waive. The Fable adversary started at the same time, because the first reviewer could not waive. Repros are under the session scratchpad's `review-opus/` and `review-fable/` directories.

Significant:

- **Opus 1. The waiver list admits what its condition excludes.** Cold read of the reference and `verifier.md`: a one-line change to a timeout default that no check reads. The reader said the "small, isolated change ... that no check or probe exercises" item covers it, while the condition and the verifier's INCONCLUSIVE rule exclude it. It resolved the conflict by verifying. Classified significant: waiver calls are on every re-gate of the common path, and the reference had compressed away gate-cost rule 3's examples, which settle it.
- **Fable 1. A failed post-merge check can freeze the orchestrator branch for good.** Cold read of the reference, `phase-session.md` and `orchestrator.md`, and `review-fable/probe2.sh`, re-run by the phase session. The run printed `code head, base rule  57cd077…` and `code head, new rule   a598151…`. After a failed check, the moved-back phase merges the orchestrator branch cleanly. If it needs no code change, its code head stays the failed one. Merging a phase step 5 then never allows a re-merge, and nothing else can end the freeze. A failed post-merge check is on the orchestrator's common path (run-decisions row 49), and the new code-head rule makes this the normal outcome.

Recorded as minor, not fixed:

- **Fable 2.** `verify-s-stack/SKILL.md`'s scoped run says the brief names the radius, while `verifier.md` has the verifier work it out. The skill also does not say whether checks 1 to 7 are scoped. The reader acted correctly.
- **Fable 3.** `verifier.md` cites "the reference file" without its path. The reader did not waive, which is correct.
- The Opus reader noted `<pr>=<its current head>` in `phase-session.md`'s answer row could be read as a pull request number. It resolved this from the header's `<branch>=<sha>` form.
- The Fable reader noted no file names the state a phase records between merging `origin/<default>` and re-running the gates after a PR creator `FAIL`. It acted correctly.

## Verify 2: NOT VERIFIED at `ccedb5143a5831c32ad9b08bc26b46ee75f6b0de`, 2026-11-22T15:58:48Z

Fresh Opus verifier. Scope: the phase's work since `faa5b86`, one commit, `d1cecf7`. No waiver: the scope changes handbook text and expected results. Answers and grades are under the session scratchpad's `verify2/` directory.

- Commits: `853fe3a` adds integration cold reads 7 (a frozen phase re-merges at the failed code head) and 8 (which untested changes may be waived). `ccedb51` rewrites point 2 of orchestrator cold reads T and AT, which still expected the old "newer code head" re-merge test that `d1cecf7` replaced. Checked: both commits touch only check files, and the new points keep the same bar.
- Skill checks 1 to 5 and 7 PASS. Tier 1 passed across 20 packages. All five scripted checks PASS.
- 64 cold reads: foundation 1 and 3, integration 1 to 4, 7 and 8, and orchestrator A to BD. Every one passed on its counted run except orchestrator AP.
- **AP FAIL**, point 2. `orchestrator.md` line 165, "Write `depends_on` again for each phase that a later `done-planning` changes", was read as "changes its dependencies". A diagnostic rerun passed. It is not counted.
- Outside the radius: foundation 2, integration 5 and 6, phase-handbooks, pr-handbook, spec-planner-handbooks, board and launcher. None of their files changed since `faa5b86`.

Next: reword line 165 to "each phase whose entry a later `done-planning` changes", then Verify again.

## Verify 3: VERIFIED at `982bdc43a0d05a7638e6a65008062f037c9196e9`, 2026-11-22T16:19:45Z

Fresh Opus verifier. Scope: the phase's work since `faa5b86`, which is `d1cecf7`, `853fe3a`, `ccedb51` and `982bdc4`. No waiver: the gate's newest real verdict was NOT VERIFIED. No commits. Answers and grades are under the session scratchpad's `verify3/` directory.

- Skill checks 1 to 5 and 7 PASS. Tier 1 passed across 20 packages. `.githooks/pre-commit` over `faa5b86...HEAD` exited 0.
- Five scripted checks PASS.
- 64 cold reads PASS, including AP, integration 7 and 8, and T and AT.
- Outside the radius: foundation 2, integration 5 and 6, phase-handbooks, pr-handbook, spec-planner-handbooks, board and launcher. None of their files changed since `faa5b86`.

## Review 2: SIGNIFICANT at `982bdc43a0d05a7638e6a65008062f037c9196e9`, 2026-11-22T16:26:56Z

Scope: `d1cecf7`, `853fe3a`, `ccedb51` and `982bdc4`. First reviewer: Opus, not allowed to waive. The Fable adversary ran beside it. Both re-ran round 1's probes, and both probes now PASS: the changed default is not waived, and the frozen phase re-merges with the failed check run. Repros are under the session scratchpad's `review2-opus/` and `review2-fable/` directories.

Significant:

- **Opus 1, also Fable 1.** `orchestrator.md` step 4's "the check that failed runs on every merge, whatever the merge changes" contradicts Finishing a phase's status-only merge of a Done phase "with steps 1 to 3" while frozen. The Opus cold read of `orchestrator.md` and the reference said the text conflicts. It said a pass on that merge would end the freeze with the failing code unchanged, and that the frozen phase's own re-merge could then be blocked. The three Fable readers took the right action but flagged the same tension. Classified significant: this change introduced it, and it sits on the failed-check path of the orchestrator's common path.

Recorded as minor, not fixed:

- **Fable 2.** Orchestrator cold read AV, points 1 and 2 (lines 786 and 787), still give "names the failed code head" as the reason `beta` does not merge. The scored action (no merge) is right, and AV passed in Verify 3.
- **Fable 3, Opus.** The waivable examples, a type annotation and a log level, can overlap the never-waivable list, a public interface or a default, and no sentence says which list wins. Every reader chose not to waive.
- Untested reader remarks: after a `move-back` for a check, the phase's own gates may be waived on an empty scope, which leaves the post-merge rerun as the backstop. "Sent `prs-open` since" does not say since what. An intermittent check can fail again with no bound. "Moving back" does not say to redo the PR step.

## Verify 4: NOT VERIFIED at `82a30d2a8133ed8413569cc861cd3fea1a35dafc`, 2026-11-22T16:46:10Z

Fresh Opus verifier. Scope: `82a30d2`. No waiver: the scope changes handbook text and expected answers. No commits. Answers and grades are under the session scratchpad's `verify4/` directory.

- Skill checks 1 to 5 and 7 PASS. The pre-commit hook over `982bdc4...HEAD` exited 0.
- Orchestrator scripted checks PASS. Orchestrator cold reads: 55 of 56 PASS, including the changed D, T and AT. Integration cold reads 4 and 7 PASS.
- **Orchestrator cold read J, point 4, FAIL**, reproduced by a fresh reader. In tick (4), `beta` was working at the previous tick. Both readers called it quiet from the current reading alone and sent the deferred round. The text at fault is tick step 4's "wait until it is quiet" in `orchestrator.md`, which predates this phase.
- Cold reads AK and V failed a first grader that lacked the scenario, and passed on a regrade with it. V point 2's "two messages" also catches the restack `instruction` that point 4 requires.

Next: restate the quiet test at tick step 4, and narrow V point 2 to refresh messages.

## Verify 5: NOT VERIFIED at `4393405f870f084cb5c54cb825d878f46a3e2cac`, 2026-11-22T17:01:15Z

Fresh Opus verifier. Scope: `82a30d2` and `4393405`. No waiver. No commits. Answers and grades are under the session scratchpad's `verify5/` directory.

- Skill checks 1 to 5 and 7 PASS. The pre-commit hook over `982bdc4...HEAD` exited 0. Three orchestrator scripted checks PASS.
- 58 cold reads: 57 PASS, including J, V, integration 7, D, F, T, AT and AV.
- **Orchestrator cold read I, point 1, FAIL.** The reader left `prs/40` out of the tick's board batch, although pull request 40 merged that tick. The text is `orchestrator.md` line 83, from `8bf296b`, which this diff did not change.
- Under `integration-d3`, the phase session reran I twice, each with a fresh Opus reader and grader (`verify5/rerun/`). Rerun 2 PASS. Rerun 1 FAIL: it wrote `prs/40` only "if it was under watch". The verifier's own diagnostic rerun passed, but it does not count under the rule. One rerun failed, so the text gets fixed at its source.

Next: line 83 says a pull request that merged or closed this tick has changed state.

## Verify 6: VERIFIED at `90f855ad42b9f67abe0a0150f1da1b05ae81932f`, 2026-11-22T17:21:57Z

Fresh Opus verifier, with the orchestrator's rerun rule in its brief. Scope: `82a30d2`, `4393405` and `90f855a`. No waiver. No commits. The report named branch HEAD `debda08`, a status-only commit. The phase session computed the code head as `90f855a`, and the verdict names that. Answers and grades are under the session scratchpad's `verify6/` directory.

- Skill checks 1 to 5 and 7 PASS. The pre-commit hook over `982bdc4...HEAD` exited 0. Three orchestrator scripted checks PASS.
- Cold reads: orchestrator A to BD and integration 4 and 7, 58 in all. 57 passed on their first run, including D, T, V, AT, I and J.
- Orchestrator BB failed its first run on point 1: the reader called an "Update branch" merge a developer commit. That reading rests on `orchestrator.md` lines 141 and 149, which this scope did not change. Both reruns, each with a fresh reader and grader, passed. Recorded as reader variance under `integration-d3`.

## Review 3: CLEAR at `90f855ad42b9f67abe0a0150f1da1b05ae81932f`, 2026-11-22T17:28:10Z

Scope: `82a30d2`, `4393405` and `90f855a`. First reviewer: Opus, not allowed to waive. The Fable adversary ran beside it. Repros are under the session scratchpad's `review3-opus/` and `review3-fable/` directories.

- Probes from Reviews 1 and 2, run again by both reviewers: the timeout default is not waived, the frozen phase re-merges with the failed check run, and a Done phase's status-only merge during a freeze runs no check and leaves the branch frozen. All PASS.
- Opus: two new cold reads, a second failure on a frozen re-merge and the quiet test with a waiting prompt. Both PASS.
- Fable: verbatim reruns of integration 7 and orchestrator V and J, its own quiet-test scenario, and a last-phase full-run failure owned by another phase. All matched.

Recorded as minor, not fixed:

- Integration cold read 4, line 66, still says "frozen until a later check passes", which is looser than the handbook but does not contradict it.
- "The frozen phase" is inferred, not defined, when a full run fails in paths owned by a phase other than the one just merged. Both readers inferred correctly.
- Step 7's "after a passing check only" does not say whether a failed full run holds back the just-merged phase's `stop`.
- A `WAIVED` verdict given after the failed check satisfies step 5's timing rule, as integration cold read 7 expects.
- No cap on repeated `move-back` cycles for a check that fails intermittently, and which failure time step 5 means after two failures.

## PR

PR creator, fresh Opus. One draft pull request, https://github.com/Samuel-Harris/foundry/pull/96, branch `s-stack-integration`, base `main`, no dependencies.

- The refresh carried the 16 phase commits `bb07229` to `90f855a`. Regenerate commit `3d668db` raised s-stack from 0.1.12 to 0.1.13, after `gh pr list` showed no open pull request changing `packages/s-stack/`.
- Proof: `EQUAL`, `RECORD s-stack-integration=3d668db6cab4a6289361d86951e16e763d6dd506`.
- On the branch, the pre-commit hook over `origin/main...HEAD`, `versioning.py check origin/main` and Tier 1 all exited 0.
- 436 hand-written lines (320 added, 116 deleted) against `origin/main`, including the `version:` line.
- Phase session check: `gh pr view` shows a draft against `main` at `3d668db`. `git diff 90f855a origin/s-stack-integration` outside `.foundry/` changes only the `version:` line. The branch holds no `.foundry/` path.
