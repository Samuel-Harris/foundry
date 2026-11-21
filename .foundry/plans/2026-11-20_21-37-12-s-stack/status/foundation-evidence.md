# Phase `foundation` evidence

Append-only. Each section is headed by what it records and the code head it covers.

## Implement: first end-to-end run of verify-s-stack at `4e0090db48bf9d09b836fb35c111335c6e04f206`

The implementing delegate wrote `tests/s-stack/verify-s-stack/SKILL.md` and ran every command in it verbatim, under zsh from the repository root, with Tier 1 outside the sandbox. The skill was not yet committed, so the code head is the commit before it. The next commit, `ada5590`, only moved the venv step ahead of the snapshot in the skill's prose.

| Check | Result | Key output |
| --- | --- | --- |
| 1. Primitives and root manifest | PASS | `[+] 94 primitives valid (85 skills, 4 agents, 5 instructions)`; `check_root_manifest: 12 listed, 19 reached` |
| 2. Markdown lint | PASS | `Summary: 0 error(s)` over 4 files |
| 3. Line budgets | PASS | `103/150 packages/s-stack/.apm/skills/sam-mode/SKILL.md` |
| 4. Handbook routes | PENDING | All seven handbooks missing, as expected before the middle phases |
| 5. Package isolation | PASS | `no relative link leaves packages/s-stack`; empty `packages/p-stack` diff against `main` |
| 6. Launcher tests | PENDING | `packages/s-stack/tests is missing` |
| 7. Tier 1 | PASS | `[+] all Tier 1 structural checks passed across 20 packages`, exit 0 |
| 8. Phase check files | PASS | `no check files` |

Verdict of the run: VERIFIED, with checks 4 and 6 pending. This is the phase session's own proof that the skill runs. It is not the Verify gate.

## Verify: NOT VERIFIED at `13f835b7a61f0f3287cdd307b712338ae8751cde`

A fresh verifier committed `tests/s-stack/verify-s-stack/checks/foundation.md` at `13f835b` and ran the whole skill, Tier 1 outside the sandbox, and the **Done when** list.

| Check | Result | Key output |
| --- | --- | --- |
| 1. Primitives and root manifest | PASS | `94 primitives valid`; `12 listed, 19 reached` |
| 2. Markdown lint | PASS | `Summary: 0 error(s)` over 5 files |
| 3. Line budgets | PASS | `103/150` |
| 4. Handbook routes | PENDING | Seven handbooks missing |
| 5. Package isolation | PASS | No link leaves the package; empty p-stack diff against `main` |
| 6. Launcher tests | PENDING | `packages/s-stack/tests is missing` |
| 7. Tier 1 | PASS | `all Tier 1 structural checks passed across 20 packages` |
| 8. Phase check files | PASS | Three cold reads in `checks/foundation.md`, all matched |

Every **Done when** item passed, including `apm audit --ci` in a fresh detached worktree with no install (`All 10 check(s) passed`) and the cold read of roles and the phase session's first prompt.

The failure: `references/status-and-messages.md` line 63 adds "The file is append-only. Each verdict adds a section ..." to the Evidence rule. C2 and decision `foundation-d1` allow only placeholders and the general code-head rule, with every other part of C2 copied unchanged. The sentence came from the first quick-review fix round, `4e0090d`.
