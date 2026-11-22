# Phase plan: integration

## Problem

Every handbook of the `sam-mode` skill is merged, but each was written by a different phase against the others' drafts. A session follows several at once: a phase session follows `phase-session.md`, the reference file and `SKILL.md`, and starts subagents under `verifier.md`, `reviewer.md` and `pr-creator.md`, while the orchestrator follows `orchestrator.md`. Where two of them disagree, a run stalls or loops on the common path. Examples: the PR creator needs pushed heads that no status key holds, so every round after the first push stops; the merge rule refuses `WAIVED`, which the developer adopted in gate-cost; a clean merge of the orchestrator branch cancels both verdicts. The developer also adopted gate-cost (run-decisions row 65), whose text is not yet in any handbook.

## Intended behaviour

After this phase, the handbooks agree with each other, with `references/status-and-messages.md`, and with run-decisions rows 65 to 70. Concretely, every item in `.foundry/plans/2026-11-20_21-37-12-s-stack/integration-fixes.md` holds, read at its line numbers on `dfbad07`. The handbook files have not changed since then on this branch, so those line numbers still apply.

## Scope

Owned paths for this round, from the phase's first prompt:

- `packages/s-stack/.apm/skills/sam-mode/SKILL.md`
- `packages/s-stack/.apm/skills/sam-mode/handbooks/**`
- `packages/s-stack/.apm/skills/sam-mode/references/**`
- `packages/s-stack/.apm/skills/sam-mode/assets/status-board.html`, only if a fix needs it. None does: the fix list's board section says no change.
- `tests/s-stack/verify-s-stack/checks/*.md` and `tests/s-stack/verify-s-stack/SKILL.md`, as fixes require.
- Generated: `packages/s-stack/apm.lock.yaml`, regenerated with `apm install --target cursor,claude,copilot` in `packages/s-stack`, then `python3 scripts/relativise_lockfiles.py packages/s-stack/apm.lock.yaml`, in each commit that makes it stale (feature plan C7). The `version:` line is the PR creator's regenerate commit.

Must not touch: `scripts/launch.sh`, `packages/s-stack/tests/`, every roadmap file. A fix that needs one of them becomes a decision request to `s-stack-orchestrator`.

## Decisions

- **Every common-path and minor fix is made.** Cosmetic fixes (F9, F10, F11, P10, P11, S2, O9) are made only where they touch a line another fix changes. The developer set this rule.
  - F9 touches reference line 74 and rule 107. P1 and F8 change neighbouring rows, not those lines. F9 is skipped.
  - F10 (`SKILL.md` line 31): no other fix touches it. Skipped.
  - F11 (`SKILL.md` line 84): no other fix touches it. Skipped.
  - P10 (`phase-session.md` line 101, `stop` row): no other fix touches it. Skipped.
  - P11 (`phase-session.md` line 111): P2 and P4 change the PR section, not line 111. Skipped.
  - S2 (`spec-writer.md` line 37): no other fix touches it. Skipped.
  - O9: line 162 is not touched by another fix; line 83 is not either. Skipped.
- **F1 follows integration-r1** (run-decisions row 70): a clean merge of the orchestrator branch moves no code head. The command in F1 is used as written, with the feature plan's lockfile exclude added by sessions as the reference says.
- **R1 deletes the PR creator's copy of the merge rule** and points at the reference, so the rule has one owner.
- **Line budgets.** `SKILL.md` stays at or under 150 lines, each handbook at or under 200. Measured after each commit with `wc -l`.
- **Checks.** A check whose expected answer encodes the old behaviour is updated in the same commit as the fix that changes the behaviour, and only to state the new behaviour. Each check a fix touches is listed in the evidence file.
- **One pull request**, unless the hand-written diff passes 2,500 lines. The fixes are one change: each handbook only agrees with the others once all have landed.

## Pull requests and commits

One draft pull request against `main`, `s-stack-integration`, titled along the lines of "fix(s-stack): make the sam-mode handbooks agree, and adopt gate-cost". Its commits, in order:

1. `fix(s-stack): code head, waivers and pushed heads in the status reference`. F1, F2, F3, F4, F5, F6, F7, F8, F12, with any check update they need. Lockfile regenerated.
2. `fix(s-stack): phase session, verifier and reviewer follow the reference`. P1 to P9, P12 to P18. Lockfile regenerated.
3. `fix(s-stack): planner dependency kinds`. S1. Lockfile regenerated.
4. `fix(s-stack): orchestrator handbook follows the reference and gate-cost`. O1 to O8, O10. Lockfile regenerated.
5. `fix(s-stack): PR creator reads the merge rule and the local orchestrator branch`. R1, R2, R3. Lockfile regenerated.
6. Check-file updates that no single fix commit owns, if any.

The run-decisions clarification F3 asks for is the orchestrator's file. It is sent to `s-stack-orchestrator` as a request, not written here.

## Execution order

1. Make each commit above by hand in the phase session, reading the current text at each line before editing it.
2. After each, run `wc -l` on the changed handbook, `python3 tests/structural/validate_primitives.py`, and the lockfile regenerate.
3. Run review's `quick-review` on the layer diff before the next layer is started. This is one pull request, so the final review covers the whole diff, and the per-commit runs are skipped.
4. Merge `s-stack-package` with `git merge --no-ff`, then Verify and Review as `phase-session.md` and the gate rules in the first prompt say.

## Verification

- The verifier's first Verify covers the whole phase diff. Cold reads are graded by fresh Opus subagents. Every check that a fix touches, and every check whose files changed, must pass.
- Tier 1 and the pre-commit hook run with `APM=/Users/samharris/projects/foundry/.venv-apm/bin/apm`, that bin directory first on `PATH`, outside the sandbox.
- Review runs `interrogate` with one Opus reviewer first, who cannot waive, because these are agent instructions. A Fable adversary then joins. A finding is significant only if it breaks the common path as the run decisions define it for the handbook it is in: rows 49 (orchestrator), 57 (launcher), 62 (pr-handbook); for the other handbooks, a phase from Plan to Done with ordinary events.
- Minor findings are recorded in the evidence file and not fixed.
