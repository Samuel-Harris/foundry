# Phase `launcher` checks

Phase `launcher` ships `packages/s-stack/.apm/skills/sam-mode/scripts/launch.sh`, its unit suite `packages/s-stack/tests/test_launch.py` with stub `workmux` and `claude` commands in `packages/s-stack/tests/stubs/`, and the CI job `s-stack-launcher-tests`.

Every tmux command in these checks, and every launcher run, goes under `env -u TMUX -u TMUX_PANE` with a private `TMUX_TMPDIR` from `mktemp -d`. When `$TMUX` is set, tmux ignores `TMUX_TMPDIR` and talks to the developer's own server.

## Rerun

### Unit suite

The suite starts a private tmux server per test, with stub `workmux` and `claude`, and asserts on panes, windows, exit codes and standard output. It skips, with a stated reason, when `tmux` is not on `PATH`. Run from the repository root.

```bash
env -u TMUX -u TMUX_PANE python3 -m unittest discover -s packages/s-stack/tests
```

Expected: exit `0` and `OK`. A skip because `tmux` is missing is PENDING, not PASS.

### Executable mode in git

```bash
bash <<'EOF'
set -euo pipefail
status=0
for f in packages/s-stack/.apm/skills/sam-mode/scripts/launch.sh packages/s-stack/tests/stubs/claude packages/s-stack/tests/stubs/workmux; do
  mode=$(git ls-files -s -- "$f" | awk '{print $1}')
  echo "${mode:-untracked} $f"
  [ "$mode" = 100755 ] || status=1
done
exit $status
EOF
```

Expected: three lines, each starting `100755`, and exit `0`.

## Evidence

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
