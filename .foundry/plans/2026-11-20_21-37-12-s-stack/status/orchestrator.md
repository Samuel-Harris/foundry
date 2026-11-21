# Orchestrator tracker

| Field | Value |
| --- | --- |
| Session | `s-stack-orchestrator` |
| Branch | `s-stack-package` (pull request 76, review only) |
| Default branch | `main` |
| tmux window | `@47` |
| Status board | https://claude.ai/artifact/Y3dKHCV8KrRCDf3zSfo3Jn (source in the orchestrator scratchpad, `board/status-board.html`) |
| Architecture page | https://claude.ai/artifact/LCPjGJNor9jKgXB4rzFev4 (source in the orchestrator scratchpad, `architecture/s-stack-architecture.html`) |
| Architecture page describes | `2b5a9b6` (version 5) |
| Last tick | 2026-11-21 21:12 |
| Default branch merged at | `6f42b1c` (#85, into `7409b48`) |

## Live sessions

| Session | Pane | Worktree | Started |
| --- | --- | --- | --- |
| `s-stack-phase-launcher` | `%172` | `../s-stack-phase-launcher` | 2026-11-21 |
| `s-stack-phase-board` | `%173` | `../s-stack-phase-board` | 2026-11-21 |
| `s-stack-phase-orchestrator-handbook` | `%174` | `../s-stack-phase-orchestrator-handbook` | 2026-11-21 |
| `s-stack-phase-pr-handbook` | `%176` | `../s-stack-phase-pr-handbook` | 2026-11-21 |

## Open decision requests

None.

## Pull requests under watch

| Number | Phase | Branch | Base | Depends on |
| --- | --- | --- | --- | --- |
| 81 | `foundation` | merged into `main` as `d7e036c` | | |
| 82 | `foundation` | merged into `main` as `e4a18d1` | | |
| 84 | `spec-planner-handbooks` | merged into `main` as `0531411` | | |
| 85 | `phase-handbooks` | merged into `main` as `6f42b1c` | | |

## Merged phases

| Phase | Merged at | Phase code head | Post-merge check |
| --- | --- | --- | --- |
| `foundation` | `7c4f36d` | `50e26ee` | VERIFIED on `1ca289c` (no code change since `7c4f36d`) |
| `spec-planner-handbooks` | `4739703` (tip `22340be`) | `6f70b37` | VERIFIED on `fd342b4` (no code change since `4739703`) |
| `phase-handbooks` | `377dc78` (tip `88ebe79`) | `c666afd` | VERIFIED on `0d1eb74` (no code change since `377dc78`) |
| `phase-handbooks` (re-merge) | `986be95` (tip `32811f9`) | `a1c95f1` | VERIFIED on `ce086bb` |

## Closed sessions

| Session | Worktree | Closed | Last commit |
| --- | --- | --- | --- |
| `s-stack-planner` | `../s-stack-planner` | 2026-11-21 | `e99d77d`, merged |
| `s-stack-phase-foundation` | removed, branch kept | 2026-11-21 | Done at `d7a6cb3`, merged; #81 and #82 merged into `main` |
| `s-stack-phase-spec-planner-handbooks` | removed, branch kept | 2026-11-21 | Done at `b9429a2`, merged; #84 merged into `main` |
| `s-stack-phase-phase-handbooks` | removed, branch kept | 2026-11-21 | Done at `0cb6af5`, merged; #85 merged into `main` |

## Queued fix rounds

One `foundation` fix round, sent once the middle phases reach Verify, so pull requests 81 and 82 change once. Raised by `spec-planner-handbooks` at `f054264`.

1. `references/status-and-messages.md`: planner requests are `planner-r<n>`, kept in an "Open requests" section of the feature plan, because the planner has no status file.
2. `references/status-and-messages.md`: the `done-planning` row lists the phases whose plan entry changed, and the `roadmap-update` row lists the `run-decisions.md` rows it folded in.
3. `SKILL.md` branch table: add rows for the planner's and the update spec writer's branches. Say that `run-decisions.md` amends the roadmap until an update folds it in.
4. One home for the launch steps (`--print-window`, then `--window`, run from a main session) in `SKILL.md`. `spec-writer.md` and `orchestrator.md` then point to it, and their owning phases remove their copies.
5. `references/status-and-messages.md` orchestrator rows, raised by `orchestrator-handbook` at `6c34228`. Two uses of `fix-round`: generated files only, with the phase staying in PR, and a hand-written conflict from the default branch, with the phase going back to Implement. `move-back` to Implement after a failed post-merge check. `stop` before closing a pane, which also covers replacing a stalled session.
6. `SKILL.md`: list `gh stack` among the tools s-stack needs. Raised by `pr-handbook`.
7. `references/status-and-messages.md`: the spec writer is listed as a sender of decision requests, but it asks the developer directly by design. Raised by `spec-planner-handbooks`.
8. `SKILL.md` line 16 says to read `poteto-mode` "before anything else", but the start form says "Do nothing else". Make the two consistent. Raised by `board`.
9. `SKILL.md`: a commit never mixes `.foundry/` with other files, except a merge of the orchestrator branch, which always does. `phase-session.md` already states this exception. Raised by `phase-handbooks`.
10. `references/status-and-messages.md`: the orchestrator table also needs a kind for "every pull request merged". Raised by `phase-handbooks` (extends item 5).
11. `references/status-and-messages.md`: the code-head command follows git history simplification, so after a merge it can resolve to a commit off the phase branch's first-parent line. Add `--first-parent`, and check that a pre-Verify merge that brings in code still moves the code head. Raised by `phase-handbooks`.
12. `references/status-and-messages.md`: write generated-path exclusions with glob magic, `':(exclude,glob)**/<name>'`. The plain `':(exclude)**/<name>'` does not match a file at the repository root. Foundry is safe only because its root `apm.lock.yaml` is gitignored. Raised by `orchestrator-handbook`.
13. `tests/s-stack/verify-s-stack/SKILL.md` check 8: `## Evidence` must not "record one-off checks with their results". Results go in the phase's evidence file under `.foundry/`, as the no evidence-exception run decision says. The feature plan's C6 has the same wording, and that run decision overrides it. Raised by `phase-handbooks`.
14. `references/status-and-messages.md`: drop the `restack` orchestrator message kind. PR creators now restack themselves (run decision, automatic stacking). Raised by `orchestrator-handbook`. Make the `fix-round` row cover a merged dependency, after which the PR creator works out the base again. Raised by `phase-handbooks`.
15. `SKILL.md` line 20: a feature name must also not contain `-phase-` or end with `-phase`, `-planner`, `-orchestrator`, `-spec` or `-spec-<n>` (run decision `launcher-r2`). Raised by `launcher`.
16. `references/status-and-messages.md`: the code-head rule must ignore version-only changes, as the run decision on version lines says. Its message rows must also cover a failed post-merge check, a `state` reply to an early merged notice, and the merged notice itself (move-back, state and instruction rows). Raised by `phase-handbooks`.
17. `references/status-and-messages.md` line 61 reads as the whole merge condition and does not mention `prs-open`. Point it to `orchestrator.md`'s merge rule (run decision on `prs-open` re-merges). Raised by `orchestrator-handbook`.

For `default-stack`: `docs/COMPATIBILITY.md` line 126 still says "The nine dependency-bearing packages use the sibling path: form".

## Merge cautions

- After the pre-commit hook has rewritten a staged lockfile, `git merge --abort` exits 128 and leaves `MERGE_HEAD`. Recover with `git reset --merge`, then check `git status`. Found by `orchestrator-handbook` (review of `e0a51a2`).
- Read a phase's tip and its code head in one step, and merge that tip SHA, not the branch name, so no commit added after the verdicts check can slip in.

## Queued roadmap update

At the end of the run, start a spec writer to fold `run-decisions.md` into the roadmap. At least these items: `coordination.md` "The launcher" and "Restarts" and C4 now resume by stored id with `--print-window`, `--close`, `--remove` and exit 5; `roles.md` drops the Orchestrate playbook pointer; the status board gains the dependency map and session labels; the generated-files rules for code heads, conflicts and the line limit. Raised by `launcher`.

Known launcher limits to record in that update: a pane left at its shell after `claude` exits is not reused, and `--close` does not clear it, so a relaunch adds a pane. A restarted spec writer needs `--window`.

## Window layout

The orchestrator's pane `%165` holds the whole column after the sidebar `%147`. Start planner and phase sessions by hand to the right of that column: split the largest session pane there, with `-v` unless both halves stay at least 80 columns wide. Start a spec writer in `%165`'s column. Never move a pane the developer adds to that column, and never run `select-layout`.

## Deferred follow-ups for live phases

- `phase-handbooks`: widen "a Done phase asked to change code moves back to Implement" to any state past Implement (Verify, Review, PR, Done). It covers a phase in PR whose code changes after its pull requests merged, for example from a direct instruction from the developer. Fold this into its next Implement round, or send it as a follow-up fix round. It fails safe meanwhile. Raised by `orchestrator-handbook` at `03d2899`.
- After every handbook phase is merged, have a fresh subagent do one cross-handbook read-through on `s-stack-package`: orchestrator, phase-session, verifier, reviewer, pr-creator, spec-writer and planner, plus the reference file. Collect the recorded handshake edge cases from each phase's evidence file. Route the fixes to the owning phases, or to the foundation round for the reference file.
  - Include: can `orchestrator.md` send the merged notice to a phase that has just entered PR (PR step 1) before `prs-open` lists its new pull request? Check against the re-merge guard and the notice's conditions. Raised by `phase-handbooks`' reviewers at `a1c95f1`.
- `phase-handbooks` (Done, needs a follow-up round): in `phase-session.md`, fix-round step 4's "Move to PR and report" must say to send `prs-open` once the PR creator has carried the fix. The same applies to line 111's "A conflict with the default branch" round, which also ends without a PR creator or `prs-open`. Under the `prs-open` re-merge rule, a phase that never sends it cannot merge again. `orchestrator.md` at `caafc7f` asks a quiet phase for it meanwhile. Raised by `orchestrator-handbook`'s fifth review.
- `phase-handbooks` (Done, needs a follow-up round): `phase-session.md` line 109, the "A pull request merged" round, runs no gate. Add that if the PR creator reports a STOP, the phase sends the orchestrator a decision request naming the STOP and stays in PR. Raised by `pr-handbook`'s review at `b4da68b`.
  - Include: the board template's schema comment (C5) describes `needs_update` as containing main's tip with passing checks. `orchestrator.md` at `20c031a` also requires the heads of open dependencies. Make the comment match. Raised by `orchestrator-handbook`.
- `spec-planner-handbooks` (Done, needs a follow-up round): in `checks/spec-planner-handbooks.md`, reword cold read 1's expected point 5 to "Port 5432 is named as an exclusive resource of the sharing back-end phase. Naming it for another phase under a stated assumption neither passes nor fails this point." A check passed 5 of 5 runs on `s-stack-package`, but strict graders can fail it, which would wrongly fail a post-merge check. `planner.md` needs no change.
