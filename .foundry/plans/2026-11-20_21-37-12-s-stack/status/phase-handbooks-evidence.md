# Phase `phase-handbooks` evidence

## Verify: NOT VERIFIED at `a1c1d834802eae04624ad74e52e6acc198a49bf6`

A fresh verifier committed `tests/s-stack/verify-s-stack/checks/phase-handbooks.md` at `a1c1d83` before running anything, then ran the whole verification skill.

- Passed: primitives (`94 primitives valid`), root manifest (`12 listed, 19 reached`), markdownlint (9 files, 0 errors), line budgets (`phase-session.md` 138, `reviewer.md` 41, `verifier.md` 78), routes (the three handbooks present, four others pending), package isolation, Tier 1 (`all Tier 1 structural checks passed across 20 packages`), all of `foundation.md`'s Rerun checks, and phase-handbooks cold reads 1 to 3.
- Launcher tests pending, as the skill expects before `launcher` merges.
- Failed: phase-handbooks cold read 4, part 2. Given `phase-session.md` and a direct instruction from the developer that changes scope, the reader recorded it and sent `instruction` and a decision request, but never said it follows the instruction. It read the decision-request sentence as "wait for the answer". Roadmap `roles.md` says a session that receives a direct instruction follows it.
- Gaps the readers raised outside the checks: `verifier.md` does not say what to do when the skill lacks the step that reruns check files and the phase does not own the skill.

## Verify: VERIFIED at `305a26e4a846d378d2dac65faa47909405a36865`

A second fresh verifier reran the whole verification skill with the check file from `a1c1d83` unchanged, and made no commit.

- Passed: primitives (`94 primitives valid`), root manifest (`12 listed, 19 reached`), markdownlint (9 files, 0 errors), line budgets (`phase-session.md` 138, `reviewer.md` 41, `verifier.md` 78 of 200), package isolation, Tier 1 (`all Tier 1 structural checks passed across 20 packages`, no tracked-file change), `foundation.md`'s three cold reads and C2 check, and all four phase-handbooks cold reads.
- Cold read 4 part 2 now passes: the reader follows the instruction, records it, commits, sends `instruction` before starting the work, adds a decision request when it conflicts with the feature plan, and builds only what the answer cannot change.
- Pending, not failing: four handbook routes other phases own, and the launcher tests.
- Private-name search over the phase diff and commit messages: no hits.

## Review: SIGNIFICANT at `305a26e4a846d378d2dac65faa47909405a36865`

p-stack's `interrogate`, scope `git diff s-stack-package...HEAD -- . ':(exclude).foundry' ':(exclude)**/apm.lock.yaml'`, intent from commit messages and code. Two reviewers, Opus and Fable, each in a detached worktree at `20dbdbf`. The Gemini seat is unavailable on this host and was dropped. Each finding below was checked by the phase session against the handbook text or by rerunning the reproduction.

Significant:

1. `verifier.md` gives INCONCLUSIVE for results that `tests/s-stack/verify-s-stack/SKILL.md` calls VERIFIED. The skill says "VERIFIED when no check is FAIL ... PENDING never fails the verdict". The handbook's table has no place for PENDING, and "A check you skipped is a check that could not run" reads as covering it. One cold reader returned INCONCLUSIVE, and another returned VERIFIED but was only 60% sure. Both reviewers found it.
   Probe: cold read of `verifier.md` and the skill, with checks 4 and 6 printing PENDING and every other check passing. The expected verdict is VERIFIED.
2. `reviewer.md`'s later-review range `<last reviewed code head>..<code head>` can end on the orchestrator branch. The code head command follows git's history simplification, and after the orchestrator has merged the phase, a merge of the orchestrator branch makes it pick an orchestrator merge commit. The range then walks the orchestrator's first-parent line and shows its conflict resolution as the phase's work. Rerun in the reviewer's scratch repository `scratch-codehead-conflict`: the code head is `e78a928 merge phase b (orchestrator resolved uv.lock)`, NOT on the phase's first-parent line.
   Probe: in that repository, the scope commands must list nothing from the orchestrator's merge of phase b.
3. `phase-session.md`'s `merge-orchestrator-branch` row moves the phase back to Implement whenever it is in Verify or later, even when the merge brought only `.foundry/` files and left the code head and the verdicts unchanged. Re-entering PR then reads as starting a new PR creator for pull requests that are already open.
   Probe: cold read in which a phase in Review gets a merge that brings only `.foundry/` files. Expected: it stays in Review, keeps its VERIFIED verdict, and starts no verifier.
4. `verifier.md`'s "None" bullet says the verdict is then VERIFIED, while "Run the whole verification skill", "You write one file" and the verdict table point elsewhere. A reader cannot tell whether a None phase still reruns the merged phases' checks.
   Probe: cold read of `verifier.md` with a diff that renames private variables only. Expected: run the whole skill, write no check file, and let the table decide the verdict.

Not significant, recorded only:

- An orchestrator `instruction` is reported back to the orchestrator as an `instruction` message. This is redundant and harmless.
- `phase-session.md`'s message cases go beyond `references/status-and-messages.md`'s orchestrator table: `move-back` for a failed orchestrator-branch check, the three `fix-round` kinds, and no kind for "every pull request merged". The orchestrator directed this wording and queued the reference change for a `foundation` fix round. The file is outside this phase.
- `SKILL.md` says a commit never mixes `.foundry/` with other files, while `phase-session.md` states the merge exception. `SKILL.md` belongs to `foundation`.
- Minor gaps: Plan sends only `started`; the INCONCLUSIVE row does not name the state while a decision request waits; a voluntary fix after CLEAR has no stated path.
- `checks/phase-handbooks.md`'s `## Evidence` section holds no results.

## Verify: VERIFIED at `6758c7df2ea497bdc5536dd704c5a49656dbb4f3`

A third fresh verifier recorded the one-off checks in the check file's `## Evidence` section at `6758c7d`, its only commit, then reran the whole verification skill at that head.

- Passed: primitives, root manifest, markdownlint (9 files, 0 errors), line budgets (138, 41 and 78 of 200), package isolation, Tier 1 at `6758c7d` (`all Tier 1 structural checks passed across 20 packages`), `foundation.md`'s three cold reads and C2 check, and all four phase-handbooks cold reads.
- Pending, not failing: four handbook routes other phases own, and the launcher tests.
- Private-name search over the 5 files of the phase diff, the diff text and every phase commit message: 0 hits.
- Wording gaps the cold readers raised, none contradicting an expected answer: when a merge moves the code head during Verify, which state to be in; when a scope change counts as conflicting with the feature plan; whether a restart re-reads the roadmap and feature plan.
