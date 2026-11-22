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

## Verify: VERIFIED at `21557166e37a58d905fa420d8b4605584e490bdc`

A fresh verifier ran the whole verification skill and this phase's `## Evidence` check on 2026-11-21 between 17:40 and 17:44 UTC, at HEAD `5703280`. It made no commit.

- Passed: primitives, root manifest, markdownlint (12 files, 0 errors), line budgets (phase-session 137, verifier 78, reviewer 41 of 200), package isolation, Tier 1 17:40:40 to 17:43:26 (`all Tier 1 structural checks passed across 20 packages`), `foundation.md`'s three cold reads and C2 check, all four phase-handbooks cold reads, and both spec-planner-handbooks cold reads.
- Pending, not failing: the `orchestrator.md` and `pr-creator.md` routes, and the launcher tests.
- Private-name search at 17:42:04: 0 matches.
- One-off cold read, a merge notice while in Implement: the phase does not move to Done, sends `state` with Implement, and passes both gates for its new code. Every required point passed.
- One-off cold read, #90 merged with #91 stacked on it: the phase starts a PR creator that works out the bases again and refreshes the branches, records each base and `depends_on`, sends `prs-open`, stays in PR and runs no gate. Every required point passed.
- Gaps the readers noted, outside this check: where fix commits go once every pull request has merged, and whether a merged pull request stays listed in `pull_requests`.

## Review: SIGNIFICANT at `21557166e37a58d905fa420d8b4605584e490bdc`

A later review covered `2155716`, with clean merge `4bf6139`. Two reviewers, Opus and Fable, each in a detached worktree at `c43a4a8`, ran nine cold reads between them. Both reviewers found the same three things.

Significant:

1. The new Verdicts sentence, "Whenever the phase is past Implement and no verdict covers its current code head, move back to Implement", also fires in Verify. No verdict exists on entry to Verify, after the verifier's commit, or on a restart in Verify. Read literally, the phase can never stay in Verify, and the sentence contradicts Verify step 2 and "After a restart". Four cold readers on two models could not choose between the readings.
2. The Moving back bullet for Implement gives a failed post-merge check as a case of "no verdict covers the current code head". In that case the phase branch has not moved and both verdicts still cover it.
3. A phase that ignores the every-pull-request-merged notice outside PR has no stated way to reach Done after it returns to PR. The commit created that path.

Not significant, recorded only: the round for a merged pull request does not say what happens to the merged pull request's own `pull_requests` entry; "stays in PR" assumes the phase is in PR (an older gap); which pull request takes commits made after every pull request has merged belongs to `pr-creator.md`; and the `instruction` row routes the notice to PR step 4 in wording a reader followed correctly.

## Verify: VERIFIED at `30f0709ecdfb8865913ac95e1c7f50fcb2e8a9be`

A fresh verifier ran the whole verification skill and this phase's `## Evidence` check on 2026-11-21 between 17:50 and 17:59 UTC, at HEAD `d41b2e5`. It made no commit.

- Passed: primitives, root manifest, markdownlint (12 files, 0 errors), line budgets (phase-session 137, verifier 78, reviewer 41 of 200), package isolation, Tier 1 17:50:14 to 17:58:38 (`all Tier 1 structural checks passed across 20 packages`), `foundation.md`'s three cold reads and C2 check, all four phase-handbooks cold reads, and both spec-planner-handbooks cold reads.
- Pending, not failing: the `orchestrator.md` and `pr-creator.md` routes, and the launcher tests.
- Private-name search at 17:52:35: 0 matches.
- Five one-off cold reads of the cases the last review broke, all passing:
  - first entry to Verify starts the verifier;
  - a restart in Verify reruns the gate;
  - the orchestrator's `move-back` from PR after a failed check moves back with no contradiction;
  - the merged notice in Implement is ignored, `state` is sent, and the notice comes again in PR, which leads to Done;
  - a stale verify verdict in Review moves back to Implement.
- Outside this phase, all in `references/status-and-messages.md`: its `move-back` and `state` "When" columns and its `instruction` row do not cover a failed check, a reply to an early notice, or the merged notice.

## Review: SIGNIFICANT at `30f0709ecdfb8865913ac95e1c7f50fcb2e8a9be`

A later review covered `30f0709`, with clean merges `4bf6139` and `e826e6a`, the second bringing only a generated `version:` line. Two reviewers, Opus and Fable, each in a detached worktree at `11ba2fc`, ran nine cold reads between them. Probes 1 and 2 pass in both reviews. Probe 3 still dead-ends.

Significant:

1. The narrowed rule, "In Review, PR or Done, if the newest verdicts do not name the current code head, move back to Implement", fires on entry to Review. A phase never holds a review verdict for its current head until the Review gate reports, so the rule contradicts Review step 2 and "After a restart". It is the Verify defect again, one state later.
2. "Your current code head is merged" does not say merged into which branch. Under one reading, a fix made after every pull request has merged reaches no pull request, and the phase never reaches Done. Line 85 routes commits only to open pull requests or to new ones the phase plan assigns.

Not significant, fixed alongside: the narrowing left Verify no exit for a VERIFIED verdict that names an older head. Recorded only, all older text: the order of moving to PR and starting the PR creator in a fix round, the end of a `blocked` wait, no PR creator step in the conflict round, and restarts in the middle of a state change.

The orchestrator's deferred instruction also goes into this round: a Done phase asked to change code moves back to Implement, and its PR creator opens a new pull request for commits no open pull request carries.

## Verify: VERIFIED at `52afb2aaf8bf4136369f33bbe38aba122e8b1220`

A fresh verifier ran the whole verification skill and this phase's `## Evidence` check on 2026-11-21 between 18:08 and 18:12 UTC, at HEAD `2facd26`. It confirmed the code head under the run decision on `version:` lines, and made no commit.

- Passed: primitives, root manifest, markdownlint (12 files, 0 errors), line budgets (phase-session 137, verifier 78, reviewer 41 of 200), package isolation, Tier 1 18:08:51 to 18:11:27 (`all Tier 1 structural checks passed across 20 packages`), `foundation.md`'s three cold reads and C2 check, all four phase-handbooks cold reads, and both spec-planner-handbooks cold reads.
- Pending, not failing: the `orchestrator.md` and `pr-creator.md` routes, and the launcher tests.
- Private-name search at 18:10: 0 matches.
- Five one-off cold reads, all passing every required point:
  - entry to Review after a SIGNIFICANT verdict runs the gate;
  - entry to Verify and a restart in Verify run the verifier;
  - a `move-back` from PR after a failed check moves the phase to Implement;
  - the merged notice in Implement is ignored, comes again once the code head is merged into the orchestrator branch, and leads to Done, with the fix in a new pull request;
  - a developer's change request in Done moves the phase back to Implement, and the fix goes in a new pull request.
- Remarks outside the required points: in a fix round, the order of moving to PR and starting the PR creator (older text); the NOT VERIFIED, INCONCLUSIVE and SIGNIFICANT table rows do not repeat "for the current code head"; and the reference file's message rows lag.

## Review: SIGNIFICANT at `52afb2aaf8bf4136369f33bbe38aba122e8b1220`

A later review covered `bbd35bd` and `52afb2a`, with clean merges `e826e6a`, `c56f0bb` and `2facd26`. Two reviewers, Opus and Fable, each in a detached worktree at `c452bff`, ran seven cold reads between them. Both earlier probes pass: entry to Review after a SIGNIFICANT verdict runs the gate, and a fix made after every pull request merged reaches a new pull request.

Significant, and found by both reviewers independently: PR step 4's resend condition ("once your status file shows PR and your current code head is merged into the orchestrator branch") omits the orchestrator's first condition, that every pull request has merged into the default branch, new ones included. Read cold, the phase reaches Done while its new fix pull request is still open, or before it exists.

Not significant, recorded only: the SIGNIFICANT, NOT VERIFIED and INCONCLUSIVE table rows carry no code-head qualifier (readers resolved them from "A verdict covers only the code head it names"); a restart in PR after a merge moved the code head is covered only by the restart and merge-orchestrator-branch sentences (the reader acted correctly); whether merged pull requests stay in `pull_requests`; and the `state` sent on an ignored notice (the reference file's known lag).

## Verify: NOT VERIFIED at `771ac5da563603602759cd6a1b18acd7a6123760`

A fresh verifier ran the whole verification skill on 2026-11-21 between 18:18 and 18:21 UTC, at HEAD `dd80f74`, and made no commit. Everything passed except the one-off cold read of the merged notice, which shows an early Done:

- PR step 1 commits state PR before step 3 records the new pull request.
- In that window, every recorded pull request has merged, and the reader assumed the orchestrator might already have merged the code head.
- If the notice arrived then, the phase would move to Done with its fix in no pull request.

The orchestrator's handbook closes the window: it merges a phase only while the phase lists an open pull request (`orchestrator.md` at `131526e`, as the orchestrator stated). But `phase-session.md` does not say so. Passed: primitives, root manifest, markdownlint (12 files, 0 errors), line budgets, package isolation, Tier 1 18:18:37 to 18:21:04, every Rerun cold read of all three check files, the C2 check, and the private-name search (0 hits). Pending, not failing: two routes and the launcher tests.

## Verify: NOT VERIFIED at `8e258caf80c51a48ee2b2c42e7f75ed9a09e17a9`

A fresh verifier ran the whole verification skill on 2026-11-21 between 18:24 and 18:28 UTC, at HEAD `f34346d`, and made no commit. Everything passed except the one-off rerun of the merged-notice cold read. Two independent reads, on different models, found the same dead end:

1. The developer merges the new fix pull request into the default branch before the orchestrator merges the phase branch again.
2. Under the added sentence, the orchestrator merges a re-merged phase only while it lists an open pull request, so it never merges this one.
3. The code head never reaches the orchestrator branch, the notice never comes, and the phase waits in PR indefinitely.

Passed: primitives, root manifest, markdownlint (12 files, 0 errors), line budgets, package isolation, Tier 1 18:24:14 to 18:26:43, all four phase-handbooks cold reads, and the private-name search (0 hits). Pending, not failing: two routes and the launcher tests.

## Verify: VERIFIED at `a1c95f1df8eab39ede778ec82f49b025034881da`

A fresh verifier ran the whole verification skill and this phase's `## Evidence` check on 2026-11-21 between 18:30 and 18:35 UTC, at HEAD `d0c496e`. It made no commit.

- Passed: primitives, root manifest, markdownlint (12 files, 0 errors), line budgets (phase-session 137, verifier 78, reviewer 41 of 200), package isolation, Tier 1 18:30:35 to 18:34:50 (`all Tier 1 structural checks passed across 20 packages`), `foundation.md`'s three cold reads and C2 check, all four phase-handbooks cold reads, and both spec-planner-handbooks cold reads.
- Pending, not failing: the `orchestrator.md` and `pr-creator.md` routes, and the launcher tests.
- Private-name search at 18:32:11: 0 matches.
- One-off cold read of the merged notice in Implement, passing every required point: the phase ignores the notice and sends `state`; after both gates its fix goes into a new pull request; it moves to Done only on the notice in PR; the text leaves the notice's timing to `handbooks/orchestrator.md`; and no contradiction.
- Minor remark: Fix rounds step 3 ("the pull request branch that owns each one") could be read as pointing at a merged pull request's branch, but PR step 2 settles it.

## Review: CLEAR at `a1c95f1df8eab39ede778ec82f49b025034881da`

A later review covered the net change of `771ac5d`, `52bc3da`, `8e258ca` and `a1c95f1`: the last sentence of PR step 4 now leaves the merged notice's timing to `handbooks/orchestrator.md`. The merges `2facd26`, `fede1c5` and `589cc38` are clean. Two reviewers, Opus and Fable, each in a detached worktree at `731c14d`, ran three cold reads between them. The early-Done probe passes in both reviews, and neither found anything significant.

Not significant, recorded only:

- PR step 4's only condition for Done is "in PR", and the phase enters PR before the PR creator opens a new pull request. A notice arriving in that window would move the phase to Done early. That is the notice's timing, which `orchestrator.md` owns, and it was sent to the orchestrator.
- Fix rounds step 3 ("the pull request branch that owns each one") reads, alone, as sending a fix to a merged branch. PR step 2 settles it, and both readers chose a new pull request. Older text.
- Fix rounds starts the PR creator before moving to PR; the PR section does the reverse. Older text.
- The `state` sent on an ignored notice, and the notice having no message kind of its own, are the reference file's known lag.

## PR: pull request 85 rebuilt for code head `a1c95f1df8eab39ede778ec82f49b025034881da`

https://github.com/Samuel-Harris/foundry/pull/85 is still a draft. GitHub retargeted it to `main` when #82 merged, and it now has head `f54b7b8` and `depends_on: []`. It joins no stack. A fresh PR creator rebuilt it under `pr-handbook-r1`, as a plain fast-forward from `2c43b3d`:

- `11aa20a` merges `origin/main` with a tree that replays the pull request's 13 own commits and the 9 fix-round commits (`515c907` to `a1c95f1`) onto `origin/main`.
- `f54b7b8` is the regenerate commit, which raises s-stack from 0.1.1 to 0.1.2.

The proof printed `EQUAL`, and the hook and `versioning.py check origin/main` passed. GitHub reports it MERGEABLE.

The phase session checked independently. The four files #85 adds over `origin/main` (the three handbooks and `checks/phase-handbooks.md`) are each identical to the phase tip, `apm.yml` changes only its `version:` line, the branch holds no file under `.foundry/`, and `2c43b3d` is an ancestor of the new head. Hand-written lines against `main`: 371 added and 1 removed. The description's Dependencies section now says none.

## Done

#85 merged into main as `6f42b1c` at 18:47:47 UTC on 2026-11-21. GitHub confirms the merge. The orchestrator reports code head `a1c95f1` merged into `s-stack-package` at `986be95`, with its post-merge check VERIFIED on `ce086bb`. The phase is Done.

## Verify: NOT VERIFIED at `5d30a593661581bad342e74e6d9ced3f1289ee3c`

Follow-up round of 2026-11-22. A fresh verifier ran the whole verification skill between 00:21 and 00:26 UTC, at HEAD `1816fc3`, and made no commit.

Passed:

- primitives (`94 primitives valid`) and the root manifest (`12 listed, 19 reached`);
- markdownlint (13 files, 0 errors);
- line budgets (phase-session 136, verifier 78, reviewer 41 of 200);
- package isolation;
- Tier 1 (`all Tier 1 structural checks passed across 20 packages`);
- the rendered-board check (50 `ok`);
- `foundation.md`'s three cold reads and C2 check, all four phase-handbooks cold reads, and both spec-planner-handbooks cold reads;
- the private-name search (0 matches).

Pending, not failing: the `orchestrator.md` and `pr-creator.md` routes, and the launcher tests.

The one-off cold reads of changes a, d, e and f passed. Three failed on consistency:

- b: the `fix-round` row says every fix round re-derives bases with a PR creator, while a conflict round whose commit the branch already holds changes nothing.
- c: the "pull request merged" round sends `prs-open` unconditionally, then says what to do after a `STOP`. Because `prs-open` triggers the orchestrator's re-merge, sending it after a `STOP` could admit code that no pull request holds.
- g: the reference file's `fix-round` row omits commits the developer made, which `phase-session.md`'s feedback round now carries. The file belongs to `foundation`.

## Verify: NOT VERIFIED at `2de88c241dff05eee336f0494c7e7a57bc1c54fd`

A fresh verifier ran the whole verification skill between 00:28 and 00:32 UTC on 2026-11-22, at HEAD `58939af`, and made no commit.

Passed: primitives, root manifest, markdownlint (13 files, 0 errors), line budgets, package isolation, Tier 1 (`all Tier 1 structural checks passed across 20 packages`), the board check (50 `ok`), every Rerun cold read of the four check files, the C2 check, and the private-name search (0 matches).

Of the one-off cold reads, the delegate and move-back case passed. Three cases failed on consistency, although every reader took the right actions:

- The PR creator's `DEVELOPER-COMMITS` report was routed to a feedback round in PR step 2, but PR step 3 ("unless a `STOP`") and the "pull request merged" round sent `prs-open` straight away.
- The feedback round's step 3 said `prs-open` answers the round, with no exception for a `STOP`.
- "In Verify, Review, PR or Done, an instruction or a message that asks for a change to the code moves the phase back to Implement first" covered a conflict round, which says for itself when to move back.

## Verify: VERIFIED at `148f7450311affebc0961feb6b509d45f3481bf0`

A fresh verifier ran the whole verification skill and this phase's `## Evidence` check on 2026-11-22 between 00:35 and 00:39 UTC, at HEAD `507ddc1`. It made no commit.

- Passed: primitives (`94 primitives valid`), root manifest (`12 listed, 19 reached`), markdownlint (13 files, 0 errors), line budgets (phase-session 139, verifier 78, reviewer 41 of 200), package isolation, Tier 1 00:35:18 to 00:37:56 (`all Tier 1 structural checks passed across 20 packages`), the board check (50 `ok`), `foundation.md`'s three cold reads and C2 check, all four phase-handbooks cold reads, and both spec-planner-handbooks cold reads.
- Pending, not failing: the `orchestrator.md` and `pr-creator.md` routes, and the launcher tests.
- Private-name search at 00:36:47: 0 matches.
- Four one-off cold reads, all passing with no contradiction:
  - a conflict round whose commit the branch already holds changes nothing and resends `prs-open`;
  - a `STOP` in a "pull request merged" round, and one after the gates in a feedback round, means no `prs-open`, a decision request, and staying in state;
  - `DEVELOPER-COMMITS` runs the feedback round with `git cherry-pick -x` and both gates before `prs-open`;
  - a delegate's work lands by cherry-pick, and an instruction in Review moves the phase back to Implement first.
- Gaps the readers noted, none contradicting a required point:
  - what answers a fix round while a `STOP` decision request is open;
  - an `answer` that needs a code change in PR;
  - whether the feedback round merges the orchestrator branch before Verify;
  - a no-op conflict round leaves any conflict on a pull request branch to `pr-creator.md`;
  - the reference file's `fix-round` row lags, which belongs to `foundation`.

## Review: CLEAR at `148f7450311affebc0961feb6b509d45f3481bf0`

The review covered the phase diff, `git diff s-stack-package...HEAD`, which changes only `phase-session.md` through `5d30a59`, `2de88c2` and `148f745`. Two reviewers, Opus and Fable, each in a detached worktree at `4875436`, ran ten cold reads and two git probe repositories between them. The last review was CLEAR, so no probes were given. Neither found anything significant under the minor-findings rule. Every git probe of the code head, the cherry-pick rule and the merge rule behaved as the handbook says.

Not significant, recorded only:

- The feedback round does not say that a developer commit, once taken with `git cherry-pick -x`, is already on its pull request branch. A cold reader expected an empty cherry-pick, or a repeated `DEVELOPER-COMMITS`. This is not fixed, because the run decision on `pr-handbook`'s overlay refinements has the PR creator identify commits by their `cherry-pick -x` trailer, and `pr-creator.md` says the phase holding the change makes its proof EQUAL.
- "Each commit the developer made" includes no rule for a GitHub "Update branch" merge, which `git cherry-pick` rejects without `-m`. `pr-creator.md` and the orchestrator's rule both exclude such merges, and readers skipped or asked.
- A developer commit that also edits another phase's file has no rule. Not a common path.
- A no-op conflict round that arrives while the phase is in Implement would send `prs-open` without verdicts for the code head. Two rounds must overlap, and the orchestrator's merge rule would refuse.
- An `answer` asking for a code change has no stated move back (readers used the Verdicts rule); after a `STOP` is answered, nothing says how the PR creator learns the decision; and fix rounds do not restate the orchestrator-branch merge or `quick-review`.

## PR: draft pull request 91 for code head `148f7450311affebc0961feb6b509d45f3481bf0`

https://github.com/Samuel-Harris/foundry/pull/91 is a draft on branch `s-stack-phase-handbooks-follow-up` at `f7ae100`, with base `main`, `depends_on: []` and no stack.

- #90 merged into `main` while the PR creator worked, so it rebuilt the branch from the new `origin/main`.
- It carried `5d30a59`, `2de88c2` and `148f745` with `cherry-pick -x` trailers and no lockfile hunks.
- The regenerate commit raises s-stack from 0.1.6 to 0.1.7. No other open pull request carries an s-stack version.
- `pr.sh prove`, from the bash block in `pr-commands.md` on `s-stack-phase-pr-handbook`, printed `EQUAL` once #85's spec named its merged dependencies.
- The hook and `versioning.py check origin/main` passed. GitHub reports the pull request MERGEABLE.

The phase session checked independently. Against `main`, #91 changes only `phase-session.md` (identical to the phase tip), the lockfile and the `version:` line. The branch holds no file under `.foundry/` and contains `origin/main`. It adds 26 hand-written lines.

## Done, after the follow-up round

#91 merged into main as `d6187b5` at 01:04:52 UTC on 2026-11-22. GitHub confirms the merge, and `148f745` is an ancestor of `s-stack-package`. The orchestrator reports the merge at `4585528`, with its post-merge check VERIFIED on `7e0b76d`. The phase is Done.
