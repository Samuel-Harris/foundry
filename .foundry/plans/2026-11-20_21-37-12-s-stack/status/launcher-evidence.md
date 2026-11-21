# Phase launcher evidence

## Verify, code head `c1ec2d3d85a9f5f9535101e63ac9956ebaa32371`, VERIFIED

A fresh verifier ran on 21 November 2026. The behavioural checks and their results are in `tests/s-stack/verify-s-stack/checks/launcher.md` at that head.

- The verification skill passed in full. That covers primitives (94 valid), the root manifest (`12 listed, 19 reached`), Markdown lint, line budgets and package isolation. The launcher suite ran 35 tests, all OK. Tier 1 printed `all Tier 1 structural checks passed across 20 packages`. The foundation cold reads passed. Handbook routes were pending, as expected.
- Nine mutations of `launch.sh` each failed at least one named test.
- Live check, with the real `claude` and the real `workmux` on a private tmux server in a scratch repository. The phase pane showed `Unknown command: /sam-mode` with the arguments `phase feature=probe phase=live ...`, because `sam-mode` is not deployed there. So the first prompt's first words were `/sam-mode phase`. A second launch printed `alive probe-phase-live pane=%1`, and the panes were unchanged. On `/exit`, Claude printed the conversation id that the launcher had stored.
- Minor gaps the verifier recorded. The real `sam-mode` did not load in the scratch repository. A real `--resume` relaunch was not run, so resume is proven by the unit suite and the `/exit` id. Roadmap `coordination.md` and C4 still say restarts use `claude --continue`, and neither lists `--print-window`, `--close`, `--remove` or exit 5. That text is owned outside this phase.

This verdict is superseded by the merge of `s-stack-package` at `4739703`, which brings new files and so a new code head.

## Verify, code head `2726205c5a71584501fb366f588125c64af9cfbd`, VERIFIED

A second fresh verifier ran at the merged head on 21 November 2026, in full. The results are recorded under "Rerun at `2ecc9f0`" in `tests/s-stack/verify-s-stack/checks/launcher.md`.

- The verification skill passed in full, including Tier 1 across 20 packages and the cold reads of the newly merged `planner.md` and `spec-writer.md`. The suite ran 35 tests, all OK.
- Four mutations each failed named tests.
- Every launcher call written in `SKILL.md` and `spec-writer.md` was run against the launcher with stubs, and each was accepted.
- Live check with the real `claude` and `workmux`. The first prompt began `/sam-mode phase`, and the second launch printed `alive`. After `/exit`, a relaunch ran `claude --name probe-phase-live --resume <the stored id>` and showed the earlier conversation.
- Minor findings, recorded and not fixed, under the orchestrator's minor-findings rule:
  - A pane left at its shell after `claude` exits is not reused. A relaunch splits a new pane, and `--close` does not clear a dead pane.
  - `SKILL.md`'s `start` form covers only the first spec writer. A restart needs `--window`, as C4 says.
  - The real `sam-mode` did not load in the scratch repository.

## Review, code head `2726205c5a71584501fb366f588125c64af9cfbd`, SIGNIFICANT

The review ran p-stack's `interrogate` skill with two adversaries, on Opus and on Fable. The Gemini seat was dropped, because this host has no Gemini model. The phase session reran every finding below on macOS, and each reproduced. Repros are in the adversaries' worktrees under `.claude/worktrees/` in the main checkout.

1. Outside a UTF-8 locale, tmux replaces the tab separators in `list-panes -F` output with `_`, so no live session is ever detected. Under `LC_ALL=C` a second launch starts a second copy, `--close` reports `absent`, and `--remove` deletes the worktree under two live sessions. Found by Fable.
2. Derived names collide across features. The planner of `a-phase` and phase `planner` of `a` are both `a-phase-planner`. The planner of `trip` reuses, and `--remove` deletes, feature `trip-planner`'s worktree. Found by both. Settled as `launcher-d8`.
3. Two concurrent launches of one name, with the worktree present, start two copies. Found by both.
4. A launch into a zoomed window unzooms it and shrinks the zoomed pane. Found by both.
5. `--print-window` with a stale `TMUX_PANE` prints `window=` and exits 0. Found by Fable.
6. With no tmux server running, `--close` and `--remove` exit 1 instead of `absent` and a normal removal. Found by Fable.
7. `--remove` removes a worktree whose detached HEAD holds commits that are on no branch, and a worktree in which another `claude` is still working. Found by Fable.

## Verify, code head `15bb919f5f9e85fca556362ac5bdb2897900b955`, VERIFIED

A third fresh verifier ran after the review fix round and the merge of phase-handbooks. Its results are under "Rerun at 8839699" in `tests/s-stack/verify-s-stack/checks/launcher.md`.

- The full skill passed, with Tier 1 across 20 packages and nine cold reads. 47 tests pass, and they pass again under `LC_ALL=C`.
- Each of the seven review defects was reproduced against the fixed launcher with stubs and is fixed.
- Six mutations each failed named tests. All three launcher calls in `SKILL.md` and the handbooks were accepted.
- Live check with the real `claude`. The first launch took 0.75 s, then `alive`, then `/exit` and a relaunch with `--resume <stored id>` showing the earlier conversation.
- Minor findings, recorded:
  - `verifier.md` says `## Evidence` holds no results, which contradicts C6.
  - With no tmux server, tmux's own `no server running` line reaches standard error.
  - Cold readers found small ambiguities in `SKILL.md` and `phase-session.md`.

This verdict is superseded. The developer's pane placement rule (`launcher-d9`) is a scope change, so the phase moves back to Implement.

## Verify, code head `13104cc935a923cc9511d71570ac51683a012246`, VERIFIED

A fourth fresh verifier ran after the placement rule, pane reuse, their quick-review fixes and the merge of `s-stack-package` at `c18fb91`. It committed nothing. Its report, summarised:

- The full verification skill passed. Primitives were valid (94), the root manifest printed `12 listed, 19 reached`, lint and budgets passed, and isolation passed. The suite ran 83 tests, all OK, and again under `LC_ALL=C` with `LANG` and `LC_CTYPE` removed. Tier 1 printed `all Tier 1 structural checks passed across 20 packages`. All nine cold reads passed.
- Twelve mutations each failed named tests. They covered select-layout, liveness, the session lock, `--resume`, the orchestrator's column, the sidebar, the window lock, unzooming, re-zoom on failure, reuse, the resumed-nameless rule and the dirty-worktree guard.
- Placement was reproduced with the stubs on a 240x60 private server, with and without a sidebar. Each pane went where the rule says. The sidebar and an untagged developer pane in the orchestrator's column never changed. A zoomed orchestrator stayed zoomed and kept its width. Three concurrent phase launches all started with the orchestrator's width unchanged. A restart reused the same pane and resumed the stored id. A planner with no orchestrator exited 1, and an orchestrator with no spec writer split the topmost pane of the first column.
- All three launcher calls in `SKILL.md` and `spec-writer.md` were accepted.
- Live check with the real `claude` and `workmux`. The first launch took 1.09 s and placed the pane right of the orchestrator. The first prompt began `/sam-mode phase`. A second launch printed `alive` in 0.25 s. `/exit` and a relaunch put `claude --resume <stored id>` in the same pane, with the earlier conversation shown.
- Minor gaps recorded:
  - While the orchestrator shares its column (spec writer alive, or a pane below it), the right-hand area is only as tall as the orchestrator's pane, so space runs out early and launches exit 4.
  - A launch that exits 4 has already created its worktree.
  - The scratch repository has no `sam-mode`.
  - `checks/launcher.md` has no one-off layout reproduction, though the unit tests cover each case.
  - `tests/s-stack/verify-s-stack/SKILL.md` check 8 still says `## Evidence` holds results.

## Review, code head `13104cc935a923cc9511d71570ac51683a012246`, SIGNIFICANT

p-stack's `interrogate` skill ran with two adversaries, on Opus and on Fable. The Gemini seat was dropped, because this host has none. The phase session reran each finding below, and each reproduced. Repros are in the adversaries' worktrees under `.claude/worktrees/` in the main checkout.

1. A restart in the session's own pane kills a command the developer runs there. The pane counted as idle when no `claude` ran in it. Found by both.
2. A plain `claude` in the feature worktree beside the named orchestrator makes every planner, phase and update spec writer launch exit 1. With no orchestrator ever launched, the same plain `claude` is reported as the orchestrator, `alive`. Found by both.
3. Under `LC_ALL=C`, tmux prints a non-ASCII character in `#{pane_current_path}` as `_`, so a worktree under such a path never matches. The first launch fails after `workmux add`, and a resurrected orchestrator is duplicated. Found by both.
4. The first spec writer is respawned into the workmux sidebar when the sidebar is the new window's first pane. Modelled with a stub workmux. Found by both.
5. Two launches that each add a worktree fail when `workmux add` takes over 10 seconds, because the worktree lock waits 10 seconds. Found by Fable.
6. A `claude` that exits at once is reported as `started` with exit 0, after a wait of about 15 seconds. Found by Fable.
7. `--close` in a zoomed window unzooms it. Found by Fable.
8. Run outside a git repository, the launcher creates its lock directory in the working directory. Found by Fable.

Recorded, not fixed:

- A `claude` running outside tmux is invisible to liveness and to `--remove`. The launcher manages tmux sessions only. Found by both.

Dismissed:

- `scripts/versioning.py check` fails on the phase branch. Under C7 a phase branch never bumps, and the PR creator's regenerate commit raises the version on the pull request branch.

## Verify, code head `310d2dff457fe1e8e4163280000f93242feab154`, NOT VERIFIED

A fresh verifier ran the full skill, Tier 1, the cold reads, the live check and 18 mutations. Two checks failed.

1. Dropping the window placement lock left all 98 tests passing. The concurrency test asserted only that each new pane lay right of the orchestrator and that the orchestrator stayed at least as wide. Without the lock, three launches each made their own full-span column, and two of those columns were 1 cell wide.
2. With no tmux socket directory at all, `--close` and `--remove` exited 1. tmux then prints `error connecting to ... (No such file or directory)`, not `no server running`.

Everything else passed. That covered all other review defects, full-height placement with and without a sidebar, the named-orchestrator precedence, a busy pane surviving a relaunch, a non-ASCII path under `LC_ALL=C`, stale and live locks, and a real `claude` launched in 0.52 s, then alive, then resumed in its own pane.

Minor findings:

- A concurrent launch can print a `holder: No such file or directory` line on standard error.
- `checks/launcher.md` lacks newer mutations, a layout and stale-lock reproduction, and the note that the trust dialog's cursor starts on "No, exit".

## Verify, code head `42d3ced56004988cc8e3db84280237636fc19491`, VERIFIED

A fresh verifier ran with nothing committed. Its report, summarised:

- The full verification skill passed. Primitives were valid (94), the root manifest printed `12 listed, 19 reached`, and lint, budgets and isolation passed. 100 tests passed, and again under `LC_ALL=C`. Tier 1 passed across 20 packages, and all nine cold reads passed.
- All 16 mutations listed in `checks/launcher.md` and 3 extra ones each failed named tests, with an unmutated control passing beside them.
- The layout reproduction ran on 240x60 private servers, with and without a sidebar. The sidebar stayed 20 wide. The first phase column was full height, and the orchestrator's column stayed at least as wide (120 against 119, 109 against 109). Later phases tiled inside that column, and the developer pane was never split. With a developer's unnamed `claude` below the named orchestrator, phases were placed by the named one and `alive` named the right pane.
- A SIGKILLed holder's lock was taken over in 0.61 s.
- Both findings at 310d2df are fixed. The window-lock mutant failed 5 runs of 5. With tmux never run, `--close` printed `absent` and `--remove` removed the worktree, kept the branch and refused a second time with exit 5.
- All three launcher calls in the handbooks were accepted.
- Live check with the real `claude` 2.1.330 and `workmux` 0.1.283. The first launch took 0.41 s, and its first prompt began `/sam-mode phase`. The second launch printed `alive` with no pane change. `/exit` and a relaunch took 0.19 s, used the same pane, ran `--resume` with the stored id, and showed the earlier conversation.
- Minor gaps recorded and not fixed, under the minor-findings rule:
  - Before tmux has ever run, tmux's own `error connecting to` line still reaches standard error.
  - `checks/launcher.md` does not say how to hold a launch inside its lock (`tmux set-environment -g STUB_CLAUDE_DELAY`).
  - It does not say how to make a macOS sidebar stub (codesign the copied `sleep`).
  - It still asks for the developer's server to have exactly its earlier sessions, not just none of the verifier's.

## Verifier results moved from the check file

The run decision that verifiers do not commit results into `checks/<phase>.md` moved these records here unchanged, apart from their heading level.

### Mutations at `b7b211d`

Each mutation was applied to `launch.sh`, the unit suite was run, and the file was restored with `git checkout`. The unmutated suite ran 35 tests, all passing.

| Mutation | Failing tests |
| --- | --- |
| `tmux select-layout -t "$window" tiled` after the split | `test_largest_session_pane_is_split`, `test_panes_other_than_the_split_one_keep_their_size` |
| Liveness never matches (`live_pane=""`) | `test_second_launch_reports_alive_and_changes_nothing`, `test_a_resumed_claude_in_the_feature_worktree_is_the_orchestrator_not_the_spec_writer`, `test_a_claude_named_for_the_session_is_alive_outside_its_worktree`, `test_live_session_is_refused`, `test_resumed_nameless_session_is_refused` |
| No nameless-in-worktree rule (`resumed=0` always) | `test_a_resumed_claude_in_the_feature_worktree_is_the_orchestrator_not_the_spec_writer`, `test_resumed_nameless_session_is_refused` |
| No dirty-worktree guard in `--remove` | `test_dirty_worktree_is_refused` |
| No `--resume`, so every start is `--session-id` | `test_restart_resumes_its_own_conversation_unless_fresh`, `test_two_sessions_in_the_feature_worktree_keep_their_own_conversations` |
| No merged-branch guard in `--remove` | `test_unmerged_branch_is_refused` |
| A split failure exits `1` instead of `4` | `test_full_window_exits_4_with_the_tmux_error` |
| `--close` also matches a nameless `claude` | `test_a_resumed_nameless_claude_is_not_closed` |
| Phase worktree added without `--headless` | `test_phase_session_gets_a_pane_in_the_window_and_its_prompt` and three others |

### Live session at `b7b211d`

Claude Code 2.1.330, workmux 0.1.283 and tmux 3.8 on macOS, 21 November 2026. A scratch repository outside this one: a bare `origin` with `main`, a clone with `refs/remotes/origin/HEAD` set to `origin/main`, and a local branch `probe` holding `.foundry/feature-roadmaps/2026-11-21_00-00-00-probe/README.md`. A private server from `env -u TMUX -u TMUX_PANE TMUX_TMPDIR=$(mktemp -d) tmux -f /dev/null new-session -d -x 200 -y 50`, whose `#{socket_path}` was under that `TMUX_TMPDIR`. The real `workmux` and `claude` were on `PATH`.

First launch, from the scratch clone:

```text
$ env -u TMUX -u TMUX_PANE launch.sh --feature probe --role phase --phase live --window @0
✓ Successfully provisioned headless worktree for 'probe-phase-live'
started probe-phase-live pane=%1 worktree=<scratch>/repo__worktrees/probe-phase-live
```

The pane showed Claude Code's folder-trust dialog for the new worktree. It was accepted in the private pane. The pane then showed, with the scratch path shortened:

```text
 ▐▛███▛█   Claude Code v2.1.330
 ▝▝   ▝▝   /…/repo__worktrees/probe-phase-live
⏺ Unknown command: /sam-mode
⏺ Args from unknown skill: phase feature=probe phase=live update=-
  roadmap=.foundry/feature-roadmaps/2026-11-21_00-00-00-probe
  plan=.foundry/plans/2026-11-21_00-00-00-probe/README.md orchestrator=probe-orchestrator
──────────────────────────────────── probe-phase-live ─
❯
```

The first prompt's first words are `/sam-mode phase`: Claude Code read `/sam-mode` as the command and `phase feature=probe ...` as its arguments. `sam-mode` is not deployed in a scratch repository, so Claude Code reports it as unknown, and the session is not shown loading the skill. The session name `probe-phase-live` is on the input box.

Second launch, same command:

```text
alive probe-phase-live pane=%1
```

Exit `0`. Panes `%0 100x50` and `%1 99x50`, and window `@0`, were the same before and after.

On `/exit`, Claude Code printed `claude --resume 7d3af64e-1a98-4978-9637-1f3c2d183b5b`, the id the launcher had written to `s-stack-sessions/probe-phase-live` in the worktree's git directory. The private server was then killed and the worktree removed with `workmux remove probe-phase-live --keep-branch --force` in the scratch clone.

### Rerun at `2ecc9f0`, after the merge of `s-stack-package`

The merge brought `handbooks/planner.md` and `handbooks/spec-writer.md`. The unit suite ran 35 tests, all passing.

| Mutation | Failing tests |
| --- | --- |
| `tmux select-layout -t "$window" tiled` after the split | `test_largest_session_pane_is_split`, `test_panes_other_than_the_split_one_keep_their_size` |
| Liveness never matches (`live_pane=""`) | `test_second_launch_reports_alive_and_changes_nothing`, `test_a_resumed_claude_in_the_feature_worktree_is_the_orchestrator_not_the_spec_writer`, `test_a_claude_named_for_the_session_is_alive_outside_its_worktree`, `test_live_session_is_refused`, `test_resumed_nameless_session_is_refused` |
| No `--resume`, so every start is `--session-id` | `test_restart_resumes_its_own_conversation_unless_fresh`, `test_two_sessions_in_the_feature_worktree_keep_their_own_conversations` |
| No dirty-worktree guard in `--remove` | `test_dirty_worktree_is_refused` |

Every launcher command in the handbooks ran against the stubs on a private server and was accepted. `SKILL.md`'s `launch.sh --feature hb --role spec`, run from the repository root, printed `started hb-spec`. `spec-writer.md`'s `launch.sh --print-window`, run from the feature worktree with `TMUX_PANE` set to the spec writer's pane, printed `window=@1`. Its `launch.sh --feature hb --role orchestrator --window @1` printed `started hb-orchestrator` while the spec writer was still alive in the same worktree. A second run printed `alive hb-orchestrator`.

The live check ran again with the same tools and scratch layout as above. The first launch printed `started probe-phase-live pane=%1`. After the trust dialog was accepted, the pane showed `Unknown command: /sam-mode` and `Args from unknown skill: phase feature=probe phase=live update=- ...`, as above. The second launch printed `alive probe-phase-live pane=%1`, and panes and windows were unchanged. The pane's `claude` ran `claude --name probe-phase-live --session-id 11809bd4-aa1b-450b-9f2e-aeef4c27bdc6`, the id in `s-stack-sessions/probe-phase-live`.

Restart. `/exit` in the pane printed `claude --resume 11809bd4-aa1b-450b-9f2e-aeef4c27bdc6` and left the pane at a shell. The same launch command then printed `started probe-phase-live pane=%2`, and the new pane ran `claude --name probe-phase-live --resume 11809bd4-aa1b-450b-9f2e-aeef4c27bdc6`. That pane showed the earlier `Unknown command: /sam-mode` exchange above the new one, with `probe-phase-live` on the input box. The marker file was unchanged. The worktree was removed with `workmux remove probe-phase-live --keep-branch --force`, and the private server was killed.

### Rerun at `8839699`, after the review fix round and the merge of `s-stack-package`

The merge brought `handbooks/phase-session.md`, `handbooks/verifier.md` and `handbooks/reviewer.md`. The unit suite ran 47 tests, all passing, both as written in `## Rerun` and with `LC_ALL=C` and no `LANG` or `LC_CTYPE`.

Each defect the review at `2726205` found was reproduced against the launcher with the stubs in `packages/s-stack/tests/stubs` on a private server, and none recurred:

| Defect | Reproduction | Result |
| --- | --- | --- |
| C locale hid live sessions | Launcher run with `LC_ALL=C` and no `LANG` or `LC_CTYPE`: start a phase session, launch it again, `--remove`, `--close` twice. Also a nameless `claude --continue` in the worktree, then `--remove` and a start | `alive`, panes unchanged; `--remove` exit `5` naming the live pane; `closed`, then `absent`; nameless case `refused` and `alive` |
| Names collide across features | `--feature` `a-phase`, `a-phase-x`, `trip-planner`, `x-orchestrator`, `x-spec`, `x-spec-3` | Each exit `2` with usage; `ok-feature` accepted |
| Concurrent launches start two copies | Two simultaneous launches of an existing phase worktree, with the stub `claude` delayed 2 s, three rounds | One `started` and one `alive` each round, one `claude` process |
| A zoomed window is unzoomed | Window zoomed on `%0` beside a 30-column pane, then a phase launch | Still zoomed, `%0` still 200x50, the 30-column pane unchanged; an unzoomed window stayed unzoomed |
| Stale `TMUX_PANE` | `--print-window` with `TMUX_PANE=%999` | `launch.sh: no window for pane %999`, exit `1` |
| No tmux server | `--close` and `--remove` after `kill-server` | `absent`, exit `0`; `removed`, exit `0`, branch kept |
| `--remove` loses work | Detached HEAD with a commit on no branch; a `claude --name someone-else` in the worktree; one in a subdirectory of it | Each exit `5` with a `refused` reason; the clean case then removed the worktree and kept the branch |

| Mutation | Failing tests |
| --- | --- |
| `tmux select-layout -t "$window" tiled` after the split | `test_a_zoomed_window_stays_zoomed`, `test_largest_session_pane_is_split`, `test_panes_other_than_the_split_one_keep_their_size` |
| Liveness never matches (`live_pane=""`) | `test_a_claude_named_for_the_session_is_alive_outside_its_worktree`, `test_a_live_session_is_alive`, `test_a_resumed_claude_in_the_feature_worktree_is_the_orchestrator_not_the_spec_writer`, `test_concurrent_launches_of_an_existing_worktree_start_one_copy`, `test_second_launch_reports_alive_and_changes_nothing` |
| No session lock | `test_concurrent_launches_of_an_existing_worktree_start_one_copy`, in five of five runs; it passed five of five unmutated |
| No `--resume`, so every start is `--session-id` | `test_restart_resumes_its_own_conversation_unless_fresh`, `test_two_sessions_in_the_feature_worktree_keep_their_own_conversations` |
| No `-Z` for a zoomed window | `test_a_zoomed_window_stays_zoomed` |
| No detached-HEAD guard in `--remove` | `test_commits_on_a_detached_head_are_refused` |

Every launcher command in `SKILL.md` and the handbooks ran against the stubs and was accepted. `SKILL.md`'s `launch.sh --feature hb --role spec` printed `started hb-spec`. `spec-writer.md`'s `launch.sh --print-window`, from the feature worktree with `TMUX_PANE` set to the spec writer's pane, printed `window=@1`, and its `launch.sh --feature hb --role orchestrator --window @1` printed `started hb-orchestrator`, then `alive hb-orchestrator`. The three new handbooks call no launcher command.

The live check ran again with Claude Code 2.1.330, workmux 0.1.283 and tmux 3.8, in the scratch layout above. The first launch printed `started probe-phase-live pane=%1` and took 0.75 s, including the headless `workmux add` and the wait until `ps` showed the new `claude`. After the trust dialog was accepted, the pane showed `Unknown command: /sam-mode` and `Args from unknown skill: phase feature=probe phase=live update=- ...`. The second launch printed `alive probe-phase-live pane=%1`, with panes `%0 100x50` and `%1 99x50` unchanged. `/exit` printed `claude --resume 1bdcc2c1-1ae8-4bca-9d84-7276e597311b`, the id in `s-stack-sessions/probe-phase-live`. The relaunch took 0.49 s, printed `started probe-phase-live pane=%2`, ran `claude --name probe-phase-live --resume 1bdcc2c1-1ae8-4bca-9d84-7276e597311b`, and showed the earlier `Unknown command: /sam-mode` exchange above the new one. The worktree was removed with `workmux remove probe-phase-live --keep-branch --force`, and the private server was killed.
