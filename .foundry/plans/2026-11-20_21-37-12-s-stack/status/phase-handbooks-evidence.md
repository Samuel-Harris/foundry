# Phase `phase-handbooks` evidence

## Verify: NOT VERIFIED at `a1c1d834802eae04624ad74e52e6acc198a49bf6`

A fresh verifier committed `tests/s-stack/verify-s-stack/checks/phase-handbooks.md` at `a1c1d83` before running anything, then ran the whole verification skill.

- Passed: primitives (`94 primitives valid`), root manifest (`12 listed, 19 reached`), markdownlint (9 files, 0 errors), line budgets (`phase-session.md` 138, `reviewer.md` 41, `verifier.md` 78), routes (the three handbooks present, four others pending), package isolation, Tier 1 (`all Tier 1 structural checks passed across 20 packages`), all of `foundation.md`'s Rerun checks, and phase-handbooks cold reads 1 to 3.
- Launcher tests pending, as the skill expects before `launcher` merges.
- Failed: phase-handbooks cold read 4, part 2. Given `phase-session.md` and a direct instruction from the developer that changes scope, the reader recorded it and sent `instruction` and a decision request, but never said it follows the instruction. It read the decision-request sentence as "wait for the answer". Roadmap `roles.md` says a session that receives a direct instruction follows it.
- Gaps the readers raised outside the checks: `verifier.md` does not say what to do when the skill lacks the step that reruns check files and the phase does not own the skill.
