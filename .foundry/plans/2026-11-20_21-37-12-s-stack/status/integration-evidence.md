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
