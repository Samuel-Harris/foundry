# Phase `spec-planner-handbooks` evidence

## Verify, code head `0d7b25d0a0156ac524a6a32e7e221ad4fed9e1ee`

A fresh verifier subagent wrote `tests/s-stack/verify-s-stack/checks/spec-planner-handbooks.md` in commits `7c59af5` and `0d7b25d`. The second commit fixed the check rather than the handbook: the first expected answer assumed a front end that `planner.md` rightly split in two. The verifier then ran `tests/s-stack/verify-s-stack/SKILL.md` end to end at `0d7b25d`.

| Check | Result |
| --- | --- |
| 1. Primitives and root manifest | PASS. `94 primitives valid`, `12 listed, 19 reached` |
| 2. Markdown lint | PASS. 8 files, 0 errors |
| 3. Line budgets | PASS. `SKILL.md` 103/150, `planner.md` 64/200, `spec-writer.md` 61/200 |
| 4. Routes | PENDING. `planner.md` and `spec-writer.md` present, five other handbooks pending |
| 5. Package isolation | PASS |
| 6. Launcher tests | PENDING. `packages/s-stack/tests` missing |
| 7. Tier 1 | PASS. `all Tier 1 structural checks passed across 20 packages`, exit 0, checked by the phase session in the log |
| 8. Check files | PASS. Three foundation cold reads, the C2 comparison and both spec-planner-handbooks cold reads |

Verdict: VERIFIED. The verifier noted two small gaps, which the phase session fixes in a new code head: `planner.md` did not say what happens when a phase must depend on two open phases, and `spec-writer.md` did not say which command's output to report.

## Verify, code head `08874f390fa5e43df00cb90946b113b92f1fb1e0`

A second fresh verifier ran the full skill again at HEAD `8d22ba0` and left the check file unchanged. Checks 1, 2, 3, 5, 7 and 8 passed. Check 4 is pending on the five handbooks other phases own, and check 6 is pending on the launcher's tests. Tier 1 printed `all Tier 1 structural checks passed across 20 packages`, exit 0, which the phase session confirmed in the log. All four Done-when items passed, and both cold reads matched their expected answers point by point. Verdict: VERIFIED. Minor note: in `planner.md` the sentence that gives every phase its own check file sits inside the "no existing verification skill" bullet.

## Review, code head `08874f390fa5e43df00cb90946b113b92f1fb1e0`

p-stack's `interrogate` skill ran with two adversaries, on Opus and on Fable, each in its own detached worktree at `08874f3`. Each got only the diff and the repository and was told not to read `.foundry/`. The configured Gemini seat is not available on this host. Neither adversary found a significant issue. Their cold reads covered roadmap updates, soft approvals, launcher failures, one-way doors, a typed developer instruction and a restart, and in every one the session acted correctly. The phase session reran each minor finding's command and confirmed it. Verdict: CLEAR.

Minor findings fixed in the next code head:

- The planner sent decision requests only after writing the plan.
- The planner's record of a developer's answer lacked the door type and who decided.
- Nothing stopped the planner sending `done-planning` while a request was open.
- An update spec writer skipped the visibility check.
- In the check file, the first cold read cites roadmap `workflow.md`, which never ships, and leaves out **Must not touch**. The next verifier fixes that.

Findings dismissed, with reasons:

- A restarted planner can still find answers. The orchestrator records each decision in `run-decisions.md` (roadmap `coordination.md`, tick step 5), and the planner reads that file after a restart.
- The spec writer asks the developer directly and sends no decision request, as roadmap `roles.md` and `workflow.md` design it. The reference file still lists the spec writer as a sender, and that gap is with the orchestrator as a `foundation` follow-up.
- Session names and branch names belong to the launcher.

## Verify, code head `6f70b3707c6c24f174c333817b3a17f37a5d9f63`

A third fresh verifier made the check-file fix the review asked for at `6f70b37`. Cold read 1's expected fields now come from `planner.md`'s own table and include **Must not touch**. It then ran the full skill. Checks 1, 2, 3, 5, 7 and 8 passed. Checks 4 and 6 are pending, as the skill allows. Tier 1 printed `all Tier 1 structural checks passed across 20 packages`, exit 0, which the phase session confirmed in the log. All Done-when items passed. Verdict: VERIFIED.

Minor notes, recorded and not fixed, under the orchestrator's instruction to fix only what would mislead a reader or break a real run:

- `spec-writer.md` does not define `<this skill's directory>`. `SKILL.md` lines 16 and 24 do.
- `spec-writer.md` does not say who to record as decider for a two-way door the spec writer decides itself.
- `planner.md` does not say where each phase's check file lives. The plan names it.

## Review, code head `6f70b3707c6c24f174c333817b3a17f37a5d9f63`

p-stack's `interrogate` skill ran again with two adversaries, on Opus and on Fable, over the commits since `08874f3`. Each worked in its own detached worktree at `6f70b37`, got only the diff and the repository, and was told not to read `.foundry/`. Neither found anything, significant or minor. Their seven cold reads covered decisions met before the plan existed, a request still open at the end of planning, a restart mid-request, a restarted planner with an old-format plan, an update spec writer in a public repository given private names, and the check file's cold read 1. Every session acted correctly. Fable's mechanical checks found the lockfile hashes in step and `versioning.py check` clean. Verdict: CLEAR.
