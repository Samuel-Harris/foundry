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

## Verify: VERIFIED at `b27c4f18e17a1e0492274a936810619ab28a708c`

A third fresh verifier changed no verification file, so the verdict covers `b27c4f1`. All eight checks ran as written: 1, 2, 3, 5, 7 and 8 PASS, 4 and 6 PENDING as planned. Tier 1 printed `all Tier 1 structural checks passed across 20 packages`, exit 0. Check 8 ran four Rerun checks: three cold reads, all matched, and "Status header matches C2", which printed `reference matches C2 apart from the allowed differences`.

The review fixes behave. In a `git archive HEAD -- . ':(exclude).foundry'` export, the C2 check printed `PENDING: .foundry/ is absent...`, exit 0. After the skill's Cleanup, `find packages -mindepth 2 -maxdepth 2 -type d -empty` printed nothing and `git status --short` was clean.

Every **Done when** item passed. `apm audit --ci` in a fresh detached worktree at `b27c4f1` with no install printed `All 10 check(s) passed`. A private-names grep over every changed file and commit message found nothing. The full report is in the phase session's scratchpad as `verify-gate-3.md`.

## Review: SIGNIFICANT at `b27c4f18e17a1e0492274a936810619ab28a708c`

The second `interrogate` run, Opus and Fable, covered `git diff 0f4bf86 b27c4f1` outside `.foundry/`. The phase session reran the first finding and saw it reproduce.

| Finding | Found by | Severity | Proof |
| --- | --- | --- | --- |
| Regression: check 5 strips fences with a regular expression before code spans, so two inline `` `~~~` `` spans hide every link between them. The checker at `0f4bf86` caught the same file. | Fable | Significant | Probe file, check 5 printed `no relative link leaves packages/s-stack`, exit 0 |
| A longer fence holding a shorter one, or a code span holding three backticks, also hides or invents links. Unquoted or uppercase HTML attributes and a reference definition in a blockquote are missed. | Both | Low, same cause | CommonMark (markdown-it-py) output compared with the checker's |
| On a tree without `.foundry/`, the C2 check returns PENDING before its code-head comparison, which needs nothing from `.foundry/`, so a reworded rule passes there. Run from a subdirectory, it also claims `.foundry/` is absent. | Fable | Significant | Mutated export, `PENDING ...`, exit 0 |
| The empty-folder cleanup pattern also matches nested `.github` folders and names starting with `.github`, which can make its own post-check fail | Opus | Low | Scratch tree; nothing with content was deleted |

Clean under both: the reference's new emoji sentence is true for PyYAML 6.0.4, the C2 check on the worktree, install and audit in `packages/s-stack`, `FOUNDRY_CHECK_ALL=1` pre-commit, and `versioning.py check`.

## Verify: VERIFIED at `50e26eebaa31524a81e0cc00d99edf4bdad0e2dc`

A fourth fresh verifier changed no verification file, so the verdict covers `50e26ee`. Checks 1, 2, 3, 5, 7 and 8 PASS, and 4 and 6 are PENDING as planned. Tier 1 printed `all Tier 1 structural checks passed across 20 packages`, exit 0. All three cold reads matched, and the C2 check matched from the root and from a subdirectory.

The fixes in `50e26ee` behave. On a probe tree, check 5 reported exactly six leaks: a link between two inline `~~~` spans, an unquoted HTML href, an image, a single-quoted `src`, an unused reference definition and a `%2E%2E` escape. It ignored fenced links, a code-span link, an in-package link, an anchor and an `https:` link. In a `.foundry`-less export the C2 check printed PENDING, exit 0. With the code-head rule reworded there, it exited 1.

Every **Done when** item passed, including `apm audit --ci` in a fresh detached worktree with no install (`All 10 check(s) passed`). The full report is in the phase session's scratchpad as `verify-gate-4.md`.

## Review: CLEAR at `50e26eebaa31524a81e0cc00d99edf4bdad0e2dc`

The third `interrogate` run, Opus and Fable, covered `git diff b27c4f1 50e26ee` outside `.foundry/`. Both found only edge cases in check 5's link checker on adversarial input, plus one environment note. None is significant.

- **Raw HTML forms.** Character references, a leading space or tab, backslashes, attributes in comments, `data-href` and text in HTML blocks. The repository's markdownlint config leaves MD033 (no inline HTML) on, so check 2 already fails any HTML in `sam-mode`, which the round-1 Fable adversary confirmed.
- **Duplicate reference definition.** CommonMark never renders the second definition, so nothing leaks.
- **Contrived Markdown.** A query string that walks the path back into the package, a symlink inside the skill, a percent-encoded slash, and other file extensions. No handbook author produces these by accident.
- **Offline cold cache.** With a cold uv cache and no network, check 5 exits 1 with uv's resolution error. Checks 2 and 7 need the network in the same way.

Both adversaries confirmed that the C2 check gives the intended result in every combination of plan present or absent and code-head rule matching or not, and that the cleanup loop deletes only empty folders under each package's own `.cursor/` and `.github/`.

## PR: draft pull requests 81 and 82 for code head `50e26eebaa31524a81e0cc00d99edf4bdad0e2dc`

A fresh PR creator replayed the phase's commits onto two branches cut from `origin/main` at `f7772cc`, without lockfile hunks or `.foundry/`, following C7.

| Pull request | Branch and head | Base | Depends on | Hand-written lines |
| --- | --- | --- | --- | --- |
| [81](https://github.com/Samuel-Harris/foundry/pull/81) | `s-stack-foundation-package` at `fe20069` | `main` | None | 352, plus 5,270 generated lockfile lines |
| [82](https://github.com/Samuel-Harris/foundry/pull/82) | `s-stack-verify-skill` at `78162e9` | `s-stack-foundation-package`, GitHub stack 83 | 81 | 310 against its parent |

Pull request 81 ends with `chore(s-stack): regenerate generated files`. `versioning.py bump` printed `nothing to bump`, because s-stack is new on `main`. The regenerated lockfile is byte-identical to the phase branch's.

On each branch, `FOUNDRY_DIFF_RANGE=origin/main...HEAD bash .githooks/pre-commit`, `versioning.py check origin/main` and Tier 1 (`all Tier 1 structural checks passed across 20 packages`) all exited 0.

The equality proof in the form of Experiment 7 printed nothing on every "must print nothing" line, and its tree diff against `s-stack-phase-foundation` exited 0. The phase session checked independently: `git diff --stat origin/s-stack-verify-skill s-stack-phase-foundation -- . ':(exclude).foundry'` printed nothing, neither remote branch holds a file under `.foundry/`, and both pull requests are drafts.

The PR creator pushed only these two branches, with plain pushes. The automatic permission check refused `gh stack submit --auto`, so it opened the drafts with `gh pr create --draft` and linked them with `gh stack link 81 82`.

## One-off check results moved from `checks/foundation.md`

These results stood in the check file's `## Evidence` section until the run decision that check files hold no results.

### C2 conformance of the reference at `512edd797f497f955ca5a0175faead7c18a8c2d8`

Compared the reference's header section with feature plan C2 by `diff` of the text from "The header is" to the tracker sentence. Differences: the `<id>`, `<feature>` and `<phase>` placeholders and the general code-head rule, both as the orchestrator decided (`foundation-r1`, option A), plus two additions that C2 does not contain: "Run it from the worktree root." in the code-head rule, and three sentences in the **Evidence** rule making the evidence file append-only with one section per verdict. Option A says every other part of C2 is copied unchanged, so the append-only rule is a contract change made without a decision request. Result: FAIL, reported to the phase session.

### Private names at `512edd797f497f955ca5a0175faead7c18a8c2d8`

A case-insensitive `grep` over every file in `git diff --name-only s-stack-package...HEAD -- . ':(exclude).foundry'` and over the phase's commit messages, for the private repository's name, its feature's name and both prototype page ids (taken from the developer's private notes and not reproduced here), found no hit.

## Follow-up round, Verify: VERIFIED at `829f3b1982124399b5ea54f8b597d62b7c8779a9`

A fresh verifier ran the whole skill with the main checkout's pinned venv in place of `.venv-apm`, which this worktree lacks. Checks 0, 1, 2, 3, 5, 7 and 8 PASS. Check 4 is PENDING for `orchestrator.md` and `pr-creator.md`, and check 6 is PENDING because `packages/s-stack/tests` is missing. Tier 1 printed `all Tier 1 structural checks passed across 20 packages`, exit 0. Check 8 ran every phase's Rerun section: the board's headless Chrome check (`board renders as specified`), the C2 check, and nine cold reads, all passing. Mutated references made the C2 check exit 1.

Every **Done when** item passed. `apm audit --ci` in `packages/s-stack` passed 10 of 10 checks without a reinstall. All 17 queued items are addressed at the code head, items 10 and the merged-notice part of 16 through the phase session's decision to keep that notice an `instruction`. In a scratch repository the code-head loop gave the expected result for status-only, version-only, `.foundry/`-only merge, version-only merge and code-bringing merge cases, and the controls showed both the glob and `-I` clauses are needed.

Minor findings, recorded and not fixed (run decision on minor findings):

- `packages/s-stack/README.md` lists the requirements without `gh stack`, and the body of `SKILL.md` names it only in the frontmatter.
- `checks/foundation.md` has no rerunnable check for "Starting a session", the feature-name rule or the code-head loop's behaviour.
- `tests/s-stack/verify-s-stack/SKILL.md` names `handbooks/verifier.md` without saying it is relative to `sam-mode`.

The full report is in the phase session's scratchpad as `verify-round2.md`.

## Follow-up round, Review: SIGNIFICANT at `829f3b1982124399b5ea54f8b597d62b7c8779a9`

Two reviewers, Opus and Fable, reviewed `28fb827`, `4e35b4a`, `b02556c` and `829f3b1` under `handbooks/reviewer.md`. The merges in the range resolved no conflicts.

| Finding | Found by | Classification | Proof |
| --- | --- | --- | --- |
| `SKILL.md` and the reference say `handbooks/orchestrator.md` owns the merge rule, while `handbooks/phase-session.md` lines 5 and 84 say the reference owns it and move to PR "once the reference file's merge rule holds". A phase session with VERIFIED and CLEAR verdicts for its code head could not decide to move to PR. | Both | Significant | Cold reads given only those files; each reader quoted the contradiction and would not move on the verdicts alone |
| `/sam-mode start` with a feature name the limits forbid has no stated action, and a reader cannot tell who enforces the limits | Fable | Not significant | Cold read of `SKILL.md`; the launcher is not on this branch, so no wrong outcome was shown |

Both reviewers also ran, with clean results: the three cold reads in `checks/foundation.md`, the C2 check (pass, PENDING without the plan, and exit 1 on each mutation tried), the code-head loop on scratch histories including renames, symlinks, binaries and mode-only changes, `apm install` and `apm audit --ci` in `packages/s-stack`, `versioning.py check`, and the pre-commit hook over `50e26ee...HEAD`.
