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

## Verify: VERIFIED at `0f4bf86be72cef85833be3096e3cbf9fc85b59ff`

A second fresh verifier reviewed `checks/foundation.md` and added the Rerun check "Status header matches C2", committed alone as `0f4bf86`. The check diffs the reference's header section against the feature plan's C2, allowing only the placeholders and the general code-head rule. It exits 0 on the current reference. The phase session reran it against `13f835b`, where it printed the append-only sentences, the defect that failed the first gate.

| Check | Result | Key output |
| --- | --- | --- |
| 1. Primitives and root manifest | PASS | `94 primitives valid`; `12 listed, 19 reached` |
| 2. Markdown lint | PASS | `Summary: 0 error(s)` over 5 files |
| 3. Line budgets | PASS | `103/150` |
| 4. Handbook routes | PENDING | Seven handbooks missing |
| 5. Package isolation | PASS | No link leaves the package; `default branch: main`; empty p-stack diff |
| 6. Launcher tests | PENDING | `packages/s-stack/tests is missing` |
| 7. Tier 1 | PASS | `all Tier 1 structural checks passed across 20 packages`, exit 0 |
| 8. Phase check files | PASS | Three cold reads matched; the C2 check exited 0 |

**Done when.** Every item passed. `apm audit --ci` in a fresh detached worktree at `0f4bf86` with no install printed `All 10 check(s) passed`. The counts grep's only hit is `AGENTS.md:4` "nineteen content packages", which is correct. `SKILL.md` is 103 lines. Cold read 1 named all seven handbook paths and wrote `/sam-mode phase feature=<feature> phase=<phase> update=- roadmap=<path> plan=<path> orchestrator=<feature>-orchestrator`. A private-names grep over every changed file and commit message found nothing.

The full report is in the phase session's scratchpad as `verify-gate-2.md`.

## Review: SIGNIFICANT at `0f4bf86be72cef85833be3096e3cbf9fc85b59ff`

p-stack's `interrogate` ran two adversaries, on Opus and Fable, each in its own detached worktree, with the diff and the repository only. The configured Gemini seat is unavailable on this host and was dropped. The phase session reran the first two findings below and saw both reproduce.

| Finding | Found by | Severity | Proof |
| --- | --- | --- | --- |
| The "Status header matches C2" Rerun check in `checks/foundation.md` crashes where `.foundry/` is absent, which includes every pull request branch and `main`, so verify-s-stack reports NOT VERIFIED there | Both | Significant | `git archive HEAD -- . ':(exclude).foundry'`, then the check: `FileNotFoundError: ... .foundry/plans/2026-11-20_21-37-12-s-stack/README.md` |
| The skill's cleanup leaves an empty `.cursor/` and `.github/` in every package, and `apm targets` then reports `cursor` active | Opus | Significant | `find packages -mindepth 2 -maxdepth 2 -type d -empty \| wc -l` printed `40` |
| The C2 check accepts a reworded code-head rule ("cancels every verdict") because it tests that line only for three substrings | Fable | Significant | Mutated reference, check exit `0` |
| Check 5's link checker misses angle-bracket links, links with titles, indented reference definitions and HTML links | Both | Low | Probe tree, 2 of 5 leaking links reported |
| C2's `json.dumps` quoting does not round-trip characters outside the Basic Multilingual Plane through PyYAML | Both | Low, contract | Sent to the orchestrator as `foundation-r2` |

Both adversaries ran Tier 1 (`all Tier 1 structural checks passed across 20 packages`), root install and audit, the pre-commit hook in check-all mode, `versioning.py check`, and scratch-consumer installs for each target, all clean.
