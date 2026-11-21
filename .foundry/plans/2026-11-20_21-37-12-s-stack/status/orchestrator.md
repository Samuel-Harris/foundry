# Orchestrator tracker

| Field | Value |
| --- | --- |
| Session | `s-stack-orchestrator` |
| Branch | `s-stack-package` (pull request 76, review only) |
| Default branch | `main` |
| tmux window | `@47` |
| Status board | https://claude.ai/artifact/Y3dKHCV8KrRCDf3zSfo3Jn (source in the orchestrator scratchpad, `board/status-board.html`) |
| Architecture page | https://claude.ai/artifact/LCPjGJNor9jKgXB4rzFev4 (source in the orchestrator scratchpad, `architecture/s-stack-architecture.html`) |
| Architecture page describes | `dcdda28` (version 3) |
| Last tick | 2026-11-21 15:52 |
| Default branch merged at | `f7772cc` (into `7e04846`) |

## Live sessions

| Session | Pane | Worktree | Started |
| --- | --- | --- | --- |
| `s-stack-phase-launcher` | `%172` | `../s-stack-phase-launcher` | 2026-11-21 |
| `s-stack-phase-board` | `%173` | `../s-stack-phase-board` | 2026-11-21 |
| `s-stack-phase-orchestrator-handbook` | `%174` | `../s-stack-phase-orchestrator-handbook` | 2026-11-21 |
| `s-stack-phase-phase-handbooks` | `%175` | `../s-stack-phase-phase-handbooks` | 2026-11-21 |
| `s-stack-phase-pr-handbook` | `%176` | `../s-stack-phase-pr-handbook` | 2026-11-21 |
| `s-stack-phase-spec-planner-handbooks` | `%177` | `../s-stack-phase-spec-planner-handbooks` | 2026-11-21 |

## Open decision requests

None.

## Pull requests under watch

| Number | Phase | Branch | Base | Depends on |
| --- | --- | --- | --- | --- |
| 81 | `foundation` | `s-stack-foundation-package` | `main` | none |
| 82 | `foundation` | `s-stack-verify-skill` | `s-stack-foundation-package` | 81 |

## Merged phases

| Phase | Merged at | Phase code head | Post-merge check |
| --- | --- | --- | --- |
| `foundation` | `7c4f36d` | `50e26ee` | VERIFIED on `1ca289c` (no code change since `7c4f36d`) |

## Closed sessions

| Session | Worktree | Closed | Last commit |
| --- | --- | --- | --- |
| `s-stack-planner` | `../s-stack-planner` | 2026-11-21 | `e99d77d`, merged |
| `s-stack-phase-foundation` | `../s-stack-phase-foundation` | 2026-11-21 | `5df64c0`, merged at `7c4f36d`; worktree kept for fix rounds |

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

For `default-stack`: `docs/COMPATIBILITY.md` line 126 still says "The nine dependency-bearing packages use the sibling path: form".
