# Phase `launcher` checks

Phase `launcher` ships `packages/s-stack/.apm/skills/sam-mode/scripts/launch.sh`, its unit suite, which is the suite in `packages/s-stack/tests/`, with stub `workmux` and `claude` commands in `packages/s-stack/tests/stubs/`, and the CI job `s-stack-launcher-tests`.

Every tmux command in these checks, and every launcher run, goes under `env -u TMUX -u TMUX_PANE` with a private `TMUX_TMPDIR` from `mktemp -d`. When `$TMUX` is set, tmux ignores `TMUX_TMPDIR` and talks to the developer's own server. Before the first launch on a private server, confirm `#{socket_path}` lies under that directory, resolved with `pwd -P`.

## Rerun

### Unit suite

The suite starts a private tmux server per test, with stub `workmux` and `claude`, and asserts on panes, windows, exit codes and standard output. It skips, with a stated reason, when `tmux` is not on `PATH`. Run from the repository root.

```bash
env -u TMUX -u TMUX_PANE python3 -m unittest discover -s packages/s-stack/tests
```

Expected: exit `0` and `OK`. A skip because `tmux` is missing is PENDING, not PASS.

### Unit suite outside a UTF-8 locale

Without a UTF-8 locale, tmux prints a tab in a `-F` format as `_`, which once hid every live session. This runs the whole suite with no UTF-8 locale in the environment.

```bash
env -u TMUX -u TMUX_PANE -u LANG -u LC_CTYPE LC_ALL=C python3 -m unittest discover -s packages/s-stack/tests
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

One-off checks. Each touches something outside a unit test, such as the real `claude` or `workmux`. Run each once per code head. Report the result in the verifier's report, never in this file.

### Mutations

Apply each change to `launch.sh`, run the unit suite, and restore the file with `git checkout --`. Use at least these: add `tmux select-layout tiled` after the split; make liveness never match; drop the session lock; drop `--resume`; put a planner or phase session in the orchestrator's column; split the workmux sidebar; drop the window placement lock; measure a zoomed window without unzooming it; skip the re-zoom when the split fails; never reuse a session's own idle pane; reuse a busy own pane; never take over a stale lock; split without `-f`; skip the width restore after the full-span split; let an unnamed `claude` count beside a named orchestrator; drop `-u` from tmux; delete the argument rule in `pane_is_idle`, so a shell running a script or `-c` command counts as idle; break a stale lock without the breaker; read start times in the local time zone; ignore an unnamed `claude` in the session's own tagged pane; let `--close` close a busy tagged pane.

It passes when every mutation makes at least one named test fail and the unmutated suite passes.

### Layout and locks

Reproduce these with the stubs on a 240x60 private server, and list the panes with `list-panes -F '#{pane_id} #{pane_left},#{pane_top} #{pane_width}x#{pane_height} #{@s-stack-session}'` after each launch.

- **Shared column.** The orchestrator shares its column: the first spec writer is above it and an untagged developer pane is below it. Launch one phase, then three more. Do this with and without a sidebar pane whose current command is `workmux`.
- **Precedence.** A named orchestrator runs with a developer's unnamed `claude` in an untagged pane below it.
- **Stale lock.** Kill a launch with SIGKILL while it holds its session lock, then launch the same session again.

It passes when all of these hold:

- The sidebar's width never changes.
- The first phase's column spans the window's height, and the orchestrator's column is at least as wide as that column.
- Later phases tile inside that column.
- With the developer's unnamed `claude` present, a phase is placed by the named orchestrator and the developer's pane is never split.
- After the SIGKILL, the relaunch starts within a few seconds instead of waiting for the lock.

### Launcher calls in the handbooks

Run every launcher command in `SKILL.md` and `handbooks/*.md` (`grep -n 'launch.sh'`) against the launcher, with the stubs from `packages/s-stack/tests/stubs` on a private server.

It passes when the launcher accepts every form.

### Live session

Use the real `claude`, `workmux` and tmux on a private server, in a scratch repository outside this one. The repository needs a bare `origin` with `main`, a clone whose `refs/remotes/origin/HEAD` is set, and a branch holding `.foundry/feature-roadmaps/2026-11-21_00-00-00-probe/`. Start the orchestrator's pane first, because a phase session is placed to its right. Then launch one phase session, accepting the folder-trust dialog of the scratch folder in the private pane if it appears. Wait until the dialog has drawn, because a key sent earlier chooses "No, exit". Its cursor starts on "No, exit", so press Down and then Enter. Launch the same command again. Exit the session with `/exit` and launch once more. Afterwards, remove the scratch worktree with `workmux remove <name> --keep-branch --force` in the scratch repository and kill the private server.

It passes when all of these hold:

- The first prompt in the phase pane begins `/sam-mode phase`.
- The second launch prints `alive <name> pane=<pane id>` and changes no pane.
- The relaunch after `/exit` runs `claude --name <name> --resume <id>`, where `<id>` is the id stored at `s-stack-sessions/<name>` in the worktree's git directory, and the pane shows the earlier conversation.
- The relaunch after `/exit` prints the same `pane=<pane id>` as the first launch, and the window's pane count is unchanged.
- Nothing the check started is left on the developer's own tmux server: no window, pane or `@s-stack-session` tag from the check. The server may have gained windows the developer opened.
