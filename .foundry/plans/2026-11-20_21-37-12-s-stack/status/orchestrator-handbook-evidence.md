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
