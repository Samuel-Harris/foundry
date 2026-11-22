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
