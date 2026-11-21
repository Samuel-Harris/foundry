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

## Review: SIGNIFICANT at `6758c7df2ea497bdc5536dd704c5a49656dbb4f3`

A later review covered `6b60476` and `6758c7d`. The merges `fd6fdf7` and `d88dfe0` in the range are clean, with empty remerge-diffs. Two reviewers, Opus and Fable, each in a detached worktree at `06b7634`. All four probes from the first review pass, in both reviewers' runs.

Significant:

1. `verifier.md` gives no order that both fills `## Evidence` and names the current code head. "Commit the check file ... before you run anything" conflicts with an Evidence section that holds results. A cold read in each review could not find an order that ends, and `6758c7d` is such a post-run commit.
2. A fast-forward merge of the orchestrator branch puts the orchestrator's merges back into the later-review scope. Rerun in the reviewer's clone `.repro/ff`: after `git merge demo`, the range lists `e78a928` and `b170eba`, and the uv.lock resolution appears. With `--no-ff`, it lists only the phase's own merge, and its remerge-diff is empty.
3. `phase-session.md`'s "opens no new ones" contradicts a phase plan that adds a pull request after a scope change. A cold read would push new-scope commits into an unrelated open pull request.

Not significant, but fixed with finding 1 because it is one sentence: the None case is missing from the check-file and run sections. Recorded only: whether `prs-open` is resent on re-entering PR, the order of starting the PR creator and moving to PR, the state for a scope change received in PR, and "once nothing is half done" being undefined.

## Verify: VERIFIED at `d32a56ae3096f5df29e5608aa6b6c146183c7dd6`

A fourth fresh verifier ran the whole verification skill at `a721dc6`, code head `cddb4b0`, then committed this run's one-off results to the check file's `## Evidence` alone at `d32a56a`, with no new run, as `verifier.md` now says.

- Passed: primitives, root manifest, markdownlint (12 files, 0 errors), line budgets (phase-session 138, reviewer 41, verifier 78 of 200), package isolation, Tier 1 (`all Tier 1 structural checks passed across 20 packages`), `foundation.md`'s three cold reads and C2 check, all four phase-handbooks cold reads, and both spec-planner-handbooks cold reads.
- Pending, not failing: the `orchestrator.md` and `pr-creator.md` routes, and the launcher tests.
- Private-name search over the phase diff, its text and 24 commit messages: 0 hits.
- Minor, recorded: point 2 of phase-handbooks cold read 2's expected answer still says any later change to the check file needs a full rerun, while `verifier.md` now exempts an Evidence-only commit. The reader followed the handbook, and the verifier judged it a pass.

## Review: SIGNIFICANT at `d32a56ae3096f5df29e5608aa6b6c146183c7dd6`

A later review covered `73b5410`, `d32a56a` and the resolution of merge `cddb4b0`, which was lockfile-only. Two reviewers, Opus and Fable, each in a detached worktree at `d8c512d`. All seven probes from the earlier reviews pass, in both reviewers' runs.

Significant:

1. `checks/phase-handbooks.md` cold read 2's expected answer 2 still says "A later change to the file means a new commit and a full rerun". Since `73b5410`, `verifier.md` exempts an Evidence-only commit. Two fresh runs of the check, exactly as written, contradict that point, so check 8 of the verification skill fails at this head. The fourth verifier had noted it and judged it a pass.
2. `phase-session.md`'s Verdicts paragraph says any commit that moves the code head needs a full verification run. Read literally, that contradicts the Evidence-only exception, and each rerun would add another Evidence commit. Both reviewers' cold readers raised it.

Not significant, fixed alongside because each needs one clause: "Nothing runs `## Evidence`" is untrue where a lint check reads the file (reproduced with markdownlint, which the pre-commit hook would catch), and the new routing sentence for pull requests no longer covers commits the phase plan does not assign, such as the verifier's. Recorded only: whether a second pass reruns one-off checks and replaces old Evidence, and naming the head when the verifier makes no commit.

## Verify: VERIFIED at `691ea624c93b5dbf1e8f33cd9b9dc1021d38308c`

A sixth fresh verifier ran the whole verification skill on 2026-11-21 between 16:40 and 16:43 UTC, at HEAD `96fb87b`. It made no commit, because no check misstated a requirement. This was the first run under the rule that run results never go in the check file.

- Passed: primitives (`94 primitives valid`), root manifest (`12 listed, 19 reached`), markdownlint (12 files, 0 errors), line budgets (phase-session 138, reviewer 41, verifier 78 of 200), no relative link leaving the package, no p-stack change, Tier 1 16:40:53 to 16:42:26 (`all Tier 1 structural checks passed across 20 packages`), `foundation.md`'s three cold reads and C2 check, all four phase-handbooks cold reads (cold read 2 under its new expected answer), and both spec-planner-handbooks cold reads.
- Pending, not failing: the `orchestrator.md` and `pr-creator.md` routes, and the launcher tests.
- One-off private-name search at 16:42:15 over the five files of the phase diff, the diff text and 33 commit messages: 0 matches.
- Outside this phase: `tests/s-stack/verify-s-stack/SKILL.md` check 8 and feature plan C6 still say `## Evidence` records results, against the newer run decision.

## Review: SIGNIFICANT at `691ea624c93b5dbf1e8f33cd9b9dc1021d38308c`

A later review covered `e592b60` and `691ea62`, with clean merges `5a33f9e` and `ed38da7`. Two reviewers, Opus and Fable, each in a detached worktree at `c82b67e`. Nine probes, seven from earlier findings and two for the removed exception, all pass. The exception is the one Fable's strict run of cold read 2 tripped, below.

Significant:

1. `verifier.md`'s `## Evidence` row says one-off checks are ones "nobody runs again", and "Run the checks" step 1 names only `## Rerun`. Yet every new code head needs a full run. Two cold readers given the same scenario took opposite actions: one reran the one-off check, and the other returned VERIFIED without it. Both reviewers found it.
2. `checks/phase-handbooks.md` cold read 2 expects, in point 2, the general rule that any later change outside `.foundry/` means a full rerun. Its prompt never asks about that, so a correct handbook can fail a strict judge.

Recorded only: a single verifier commit that checks the work of two pull requests has no stated home. `pr-creator.md`, which owns the split and does not exist yet, should settle it.

## Verify: VERIFIED at `c666afdc929b1e05e49decda745d79b469f0333f`

A seventh fresh verifier ran the whole verification skill, then this phase's own `## Evidence` check, on 2026-11-21 between 16:50 and 16:53 UTC, at HEAD `580ddbb`. It made no commit.

- Passed: primitives, root manifest, markdownlint (12 files, 0 errors), line budgets (phase-session 138, reviewer 41, verifier 78 of 200), package isolation, Tier 1 16:50:31 to 16:52:54 (`all Tier 1 structural checks passed across 20 packages`), `foundation.md`'s three cold reads and C2 check, all four phase-handbooks cold reads (cold read 2 with its new prompt), and both spec-planner-handbooks cold reads.
- Pending, not failing: the `orchestrator.md` and `pr-creator.md` routes, and the launcher tests.
- Private-name search at 16:51:45 over the phase diff's files, its text and 38 commit messages: 0 matches.
- Cold readers' remarks, none failing a check: the move back to Implement after a merge sits only in the message table; "Read first" and "After a restart" overlap; how to tell a scope change from a conflict with the feature plan.

## Review: CLEAR at `c666afdc929b1e05e49decda745d79b469f0333f`

A later review covered `c666afd`, with clean merges `ed38da7` and `161c7c7`. Two reviewers, Opus and Fable, each in a detached worktree at `69ccdf2`. All ten probes from the earlier significant findings pass, in both reviewers' runs. Each reviewer added its own cold reads against the new Evidence wording: a code head made by a merge, a later phase's verifier, and another phase's one-off check. None broke the change. Markdownlint reported 0 errors, and `versioning.py check origin/main` reported no package without a bump.

Not significant, recorded only:

- "after every merge" in the Evidence row could, read alone, suggest that a head made by a merge is exempt. The row's next sentences settle it, and every reader acted correctly.
- No sentence says outright that another phase's Evidence checks fall outside the verdict. Readers inferred it from "your own check file".
- Step 1's "your own check file" assumes the phase has one. A None phase's reader filled the gap correctly.
- Older gaps in `phase-session.md`: the state for a developer instruction received in PR, a verifier commit that checks the work of all pull requests, and no Verify row for a stale VERIFIED.
- Older wording in `verifier.md`: "needs no verification" against "needs no checks of its own".

## PR: draft pull request 85 for code head `c666afdc929b1e05e49decda745d79b469f0333f`

https://github.com/Samuel-Harris/foundry/pull/85 is a draft on branch `s-stack-phase-handbooks`, head `2c43b3d`, with base `s-stack-verify-skill`. It depends on #82 and joined GitHub stack #83, which holds #81 (merged), #82 and #85. A fresh PR creator replayed the 13 non-merge phase commits without lockfile hunks or `.foundry/`, then added `chore(s-stack): regenerate generated files`, which raises s-stack from 0.1.0 to 0.1.1 and regenerates its lockfile.

- The Experiment 7 equality proof printed `EQUAL`.
- The phase session checked independently. `git diff origin/s-stack-verify-skill origin/s-stack-phase-handbooks`, without lockfiles and `apm.yml`, equals `git diff s-stack-package...s-stack-phase-phase-handbooks -- . ':(exclude).foundry'` under the same exclusions. The branch holds 0 files under `.foundry/`, and `apm.yml` changes only its `version:` line.
- `FOUNDRY_DIFF_RANGE=origin/s-stack-verify-skill...HEAD bash .githooks/pre-commit` exited 0, with the lockfile unchanged. `versioning.py check origin/main` reported no package without a bump.
- Hand-written lines: 372 added and 1 removed against #82's branch, and 682 added and 1 removed against `main`.
- `gh stack link 81 82 85` also tried to retarget #82 to #81's old branch, and GitHub refused with HTTP 422. #82's base is still `main`.
- `s-stack-phase-spec-planner-handbooks` checked first and agreed that #84 targets `main`, because #85 is #82's only child.

## Verify: VERIFIED at `515c907896a51762c83dfeb2756981e03bd4b257`

This was the fix round for `pr-handbook-r1` and automatic stacking. A fresh verifier ran the whole verification skill and this phase's `## Evidence` check on 2026-11-21 between 17:29 and 17:34 UTC, at HEAD `f194006`. It made no commit.

- Passed: primitives, root manifest, markdownlint (12 files, 0 errors), line budgets (phase-session 137, verifier 78, reviewer 41 of 200), package isolation, Tier 1 17:29:45 to 17:34:11 (`all Tier 1 structural checks passed across 20 packages`), `foundation.md`'s three cold reads and C2 check, all four phase-handbooks cold reads, and both spec-planner-handbooks cold reads.
- Pending, not failing: the `orchestrator.md` and `pr-creator.md` routes, and the launcher tests.
- Private-name search at 17:31:23: 0 matches.
- One-off cold read: a fix round for a merged dependency. The phase session starts a PR creator that works out the base again and refreshes the branches as `pr-creator.md` says, stays in PR, runs no gate again, and has no `restack` handling. The verifier checked this against `pr-creator.md` on `s-stack-phase-pr-handbook`.
- Outside this phase: `references/status-and-messages.md` still lists `restack` as an orchestrator message, and its `fix-round` row does not cover a merged dependency.

## Review: CLEAR at `515c907896a51762c83dfeb2756981e03bd4b257`

A later review covered `515c907`, with clean merges `161c7c7`, `0bf2777` and `bd8149e`. Two reviewers, Opus and Fable, each in a detached worktree at `28ba138`, ran five cold reads between them, plus the validator and markdownlint. Neither found anything significant. The last verdict was CLEAR, so no probes were given.

Not significant, recorded only:

- The merged-elsewhere round says nothing about updating `pull_requests` or reporting afterwards. This is borderline, and it is fixed in the next round because a stale base would mislead the status board.
- "A pull request yours depend on" and the heading "merged elsewhere" read awkwardly when the merged pull request is the phase's own. It is fixed in the same edit.
- The conflict round never says in words to start a PR creator or to move to PR. Readers inferred both from the fix-round row and the PR section.
- "The phase stays in PR" assumes the phase is in PR when the round arrives.
- A conflict found during a refresh, and how a merge commit's resolution reaches a pull request branch, belong to `pr-creator.md`.
- `versioning.py check origin/main` fails at the phase head, as it does on every phase branch. The pull request's regenerate commit raises the version.

The orchestrator's instruction, received during this review, sends the phase back to Implement in the same round. `phase-session.md` moved a phase to Done on "every pull request has merged" in any state, and moved back only after a failed post-merge check.
