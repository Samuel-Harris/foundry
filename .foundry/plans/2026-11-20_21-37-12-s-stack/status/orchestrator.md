# Orchestrator tracker

| Field | Value |
| --- | --- |
| Session | `s-stack-orchestrator` |
| Branch | `s-stack-package` (pull request 76, review only) |
| Default branch | `main` |
| tmux window | `@47` |
| Status board | https://claude.ai/artifact/Y3dKHCV8KrRCDf3zSfo3Jn (source in the orchestrator scratchpad, `board/status-board.html`) |
| Architecture page | https://claude.ai/artifact/LCPjGJNor9jKgXB4rzFev4 (source in the orchestrator scratchpad, `architecture/s-stack-architecture.html`) |
| Architecture page describes | `9adc56f` (version 9) |
| Last tick | 2026-11-22 18:51 |
| Default branch merged at | `7747021` (#96, into `9be10ef`) |

## Live sessions

| Session | Pane | Worktree | Started |
| --- | --- | --- | --- |
| `s-stack-phase-default-stack` | `%202` | `../s-stack-phase-default-stack` | 2026-11-22, last phase |

## Open decision requests

None.

## Pull requests under watch

| Number | Phase | Branch | Base | Depends on |
| --- | --- | --- | --- | --- |
| 81 | `foundation` | merged into `main` as `d7e036c` | | |
| 82 | `foundation` | merged into `main` as `e4a18d1` | | |
| 84 | `spec-planner-handbooks` | merged into `main` as `0531411` | | |
| 85 | `phase-handbooks` | merged into `main` as `6f42b1c` | | |
| 86 | `board` | merged into `main` as `51f334e` | | |
| 87 | `spec-planner-handbooks` | merged into `main` as `b440889` | | |
| 88 | `foundation` | merged into `main` as `054a9e7` | | |
| 89 | `foundation` | merged into `main` as `5c4d320` | | |
| 90 | `spec-planner-handbooks` | merged into `main` as `bce824b` | | |
| 91 | `phase-handbooks` | merged into `main` as `d6187b5` | | |
| 92 | `board` | merged into `main` as `92a91f7` | | |
| 93 | `orchestrator-handbook` | merged into `main` as `ee49f7b` | | |
| 94 | `launcher` | merged into `main` as `0fdbb53` | | |
| 95 | `pr-handbook` | merged into `main` as `25a6b61` | | |
| 96 | `integration` | merged into `main` as `7747021` | | |

## Merged phases

| Phase | Merged at | Phase code head | Post-merge check |
| --- | --- | --- | --- |
| `foundation` | `7c4f36d` | `50e26ee` | VERIFIED on `1ca289c` (no code change since `7c4f36d`) |
| `spec-planner-handbooks` | `4739703` (tip `22340be`) | `6f70b37` | VERIFIED on `fd342b4` (no code change since `4739703`) |
| `phase-handbooks` | `377dc78` (tip `88ebe79`) | `c666afd` | VERIFIED on `0d1eb74` (no code change since `377dc78`) |
| `phase-handbooks` (re-merge) | `986be95` (tip `32811f9`) | `a1c95f1` | VERIFIED on `ce086bb` |
| `board` | `a606589` (tip `22e6ab0`) | `afd3f27` | VERIFIED on `3ce7d34` |
| `spec-planner-handbooks` (follow-up) | `b89a458` (tip `40c3e56`) | `47f792f` | VERIFIED on `8f735d6` |
| `foundation` (follow-up) | `3364856` (tip `8616cb8`) | `74bba4e` | VERIFIED on `3364856` |
| `spec-planner-handbooks` (second follow-up) | `5c411ce` (tip `d5c4ff2`) | `775a30a` | VERIFIED on `a89e044` (no code change since `5c411ce`) |
| `phase-handbooks` (follow-up) | `4585528` (tip `7e09ef7`) | `148f745` | VERIFIED on `7e0b76d` (no code change since `4585528`) |
| `board` (follow-up) | `3940c5b` (tip `de27bbb`) | `284ad88` | VERIFIED on `fe43e00` (no code change since `3940c5b`) |
| `orchestrator-handbook` | `7cd7034` (tip `2fbf619`) | `ff83115` | NOT VERIFIED on `6703d16` (scoped): cold reads AP (twice), AE, AN, I, Z; branch frozen, phase moved back |
| `orchestrator-handbook` (post-merge fix) | `9eb7fac` (tip `455c545`) | `a3f4749` | VERIFIED on `9eb7fac` (scoped) |
| `pr-handbook` | `ab06c83` (tip `c9e0f72`) | `27d6f55` | VERIFIED on `899ec3a` (scoped, no code change since `ab06c83`) |
| `launcher` | `a51f246` (tip `117abdb`) | `890d46d` | VERIFIED on `3a21396` (scoped, no code change since `a51f246`) |
| `integration` | `9f6c1c0` (tip `d8e5fe7`) | `90f855a` | VERIFIED on `e407673` (74 cold reads, 8 scripts; no code change since `9f6c1c0`) |

## Closed sessions

| Session | Worktree | Closed | Last commit |
| --- | --- | --- | --- |
| `s-stack-planner` | `../s-stack-planner` | 2026-11-21 | `e99d77d`, merged |
| `s-stack-phase-foundation` | removed, branch kept | 2026-11-22 | Done at `5423ae5`, merged; #88 and #89 merged into `main` |
| `s-stack-phase-spec-planner-handbooks` | removed, branch kept | 2026-11-22 | Done at `079c16d`, merged; #84, #87 and #90 merged into `main` |
| `s-stack-phase-phase-handbooks` | removed, branch kept | 2026-11-22 | Done again at `8a63c84`, merged; #85 and #91 merged into `main` |
| `s-stack-phase-board` | removed, branch kept | 2026-11-22 | Done again at `53276c3`, merged; #86 and #92 merged into `main` |
| `s-stack-phase-orchestrator-handbook` | removed, branch kept | 2026-11-22 | Done at `d110165`, merged; #93 merged into `main` |
| `s-stack-phase-pr-handbook` | removed, branch kept | 2026-11-22 | Done at `9b141bd`, merged; #95 merged into `main` |
| `s-stack-phase-launcher` | removed, branch kept | 2026-11-22 | Done at `72d5dda`, merged; #94 merged into `main` |
| `s-stack-phase-integration` | removed, branch kept | 2026-11-22 | Done at `c90e7b0`, merged; #96 merged into `main` |
| `s-stack-spec` | removed, branch kept | 2026-11-22 | gate-cost proposal at `d41db5b`, merged at `883083b` |

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





- 2026-11-22 11:34: a `launcher` verifier set `TMUX_TMPDIR` to a directory it had not created, so tmux fell back to the developer's real server and created session `$4` (name `4`, one window, a shell in a scratch repository). The kill was refused by the permission check. The developer was asked to run `tmux kill-session -t '$4'`. Launcher briefs now create `TMUX_TMPDIR` first and confirm tmux cannot connect there before creating any server.


- After the pre-commit hook has rewritten a staged lockfile, `git merge --abort` exits 128 and leaves `MERGE_HEAD`. Recover with `git reset --merge`, then check `git status`. Found by `orchestrator-handbook` (review of `e0a51a2`).
- Read a phase's tip and its code head in one step, and merge that tip SHA, not the branch name, so no commit added after the verdicts check can slip in.

## Queued roadmap update

At the end of the run, start a spec writer to fold `run-decisions.md` into the roadmap. At least these items: `coordination.md` "The launcher" and "Restarts" and C4 now resume by stored id with `--print-window`, `--close`, `--remove` and exit 5; `roles.md` drops the Orchestrate playbook pointer; the status board gains the dependency map and session labels; the generated-files rules for code heads, conflicts and the line limit. Raised by `launcher`.

Known launcher limits to record in that update: a pane left at its shell after `claude` exits is not reused, and `--close` does not clear it, so a relaunch adds a pane. A restarted spec writer needs `--window`.

## Window layout

The orchestrator's pane `%165` holds the whole column after the sidebar `%147`. Start planner and phase sessions by hand to the right of that column: split the largest session pane there, with `-v` unless both halves stay at least 80 columns wide. Start a spec writer in `%165`'s column. Never move a pane the developer adds to that column, and never run `select-layout`.

## Deferred follow-ups for live phases

- Gate-cost text and the read-through fixes went to `s-stack-phase-integration` on 2026-11-22. The roadmap section of `integration-fixes.md` goes to a fresh spec writer at the end of the run.
- After every handbook phase is merged, have a fresh subagent do one cross-handbook read-through on `s-stack-package`: orchestrator, phase-session, verifier, reviewer, pr-creator, spec-writer and planner, plus the reference file. Collect the recorded handshake edge cases from each phase's evidence file. Route the fixes to the owning phases, or to the foundation round for the reference file.
  - Include: can `orchestrator.md` send the merged notice to a phase that has just entered PR (PR step 1) before `prs-open` lists its new pull request? Check against the re-merge guard and the notice's conditions. Raised by `phase-handbooks`' reviewers at `a1c95f1`.
  - Include: `references/status-and-messages.md` has no developer-commit row and splits the generated and dependency `fix-round` uses into two rows, unlike `orchestrator.md` at `0008162`. A suggestion applied while a round is unanswered is left to the PR creator's `DEVELOPER-COMMITS` report. Raised by `orchestrator-handbook`.
  - Include: in `references/status-and-messages.md`, "a fact already committed to the sender's own file" fits `started` and the folded run-decisions rows awkwardly. Raised by `spec-planner-handbooks` at `775a30a`.
  - Include: `references/status-and-messages.md`'s `fix-round` row carries only "the pull request and its comments, or the failed check". It must also carry the developer's commits, as the developer-commit rule and `phase-session.md`'s feedback round now do. Raised by `phase-handbooks` at `5d30a59`.
  - Include: `SKILL.md`'s "repository root" leaves a worktree session to work out which root it means (readers chose the worktree root, which is right). Raised by `spec-planner-handbooks` at `775a30a`. Its other item, `phase-session.md` line 26, is in `phase-handbooks`' current round.
  - Include: `board` took its `needs_update` wording from `orchestrator.md` on the `orchestrator-handbook` branch at `1e0a39e`, because that handbook is not yet on `s-stack-package`. Check the two still match once it merges.
  - Include: `pr.sh`'s proof run against `origin/s-stack-package` gives false merge FAILs, because only the developer pushes that branch and it lags the local one. The handbooks should name the local orchestrator branch. Raised by `board`'s PR creator.
  - Include: the board template's `needs_update` rule says "draft or open pull request", while `orchestrator.md` lines 113 to 116 say "open pull request". Make them use the same words. Raised by `orchestrator-handbook` at `9c1e21f`.
  - Include: `orchestrator.md`'s developer-commit check (line 148) relies on the PR creator ending each carried commit with `(cherry picked from commit <sha>)`. Only `pr-handbook`'s `references/pr-commands.md` states it. Raised by `orchestrator-handbook` at `73ba6d4`.
  - Include: `phase-session.md` and `references/status-and-messages.md` must say the phase records each pull request branch's pushed head and passes it to the PR creator (`PUSHED=`), which `pr-creator.md` assumes after pr-handbook-r5. Raised by `pr-handbook` at `49b3fab`. Since `1223f1e` (pr-handbook-d21), `prove` prints a `RECORD <branch>=<sha>,...` line after EQUAL, and the phase must store and pass that line verbatim, not one SHA per branch.
  - Include: `prs-open` (C3), or the status header's `pull_requests` entries (C2), should carry each pushed head. `orchestrator.md` line 148 records the head on arrival, so a developer commit landing between the push and `prs-open` is never compared. This pairs with the `PUSHED=` item above. Raised by `orchestrator-handbook` at `ff83115`.
  - Include: `phase-session.md` needs a row for the orchestrator's refresh instruction (start a PR creator; on `DEVELOPER-COMMITS` start a feedback round, otherwise send `prs-open`). Raised by `orchestrator-handbook` at `ff83115`.
  - Include: the run decision on parallel package versions. `pr-creator.md` and `orchestrator.md` may need to state it.

## Post-merge check briefs

Tell the post-merge verifier to grade every cold read with Opus subagents, not Sonnet. `spec-planner-handbooks` found Sonnet graders flaky on a correct answer to its point 3.
