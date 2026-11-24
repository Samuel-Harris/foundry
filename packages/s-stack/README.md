# s-stack

Run one large feature as cooperating Claude Code sessions, each in its own worktree and tmux pane.

## What it installs

| Primitive | Name | Purpose |
| --- | --- | --- |
| Skill | `sam-mode` | Run one large feature as cooperating Claude Code sessions, each in its own worktree and tmux pane. |

## Depends on

- `p-stack`
- `deep-interview`
- `review`
- `pr`
- `planning`
- `coding-style`

## Install

```bash
apm install Samuel-Harris/foundry/packages/s-stack#^0.1.0 --target cursor,claude,copilot
```

## Requirements

- Claude Code 2.1.224 or later, with cross-session messaging.
- tmux.
- workmux.
- For AFK mode, macOS for keeping the machine awake and for the watchdog that restarts the orchestrator, which the developer installs once with `scripts/afk-watchdog.sh install`. On other systems AFK mode runs without both. The launcher loads the skill's usage mod into the orchestrator's session, so it can read the plan's usage limits. That needs a Claude Code build with mod support, proven on 2.1.330.

## Targets

Deployed to `cursor`, `claude` and `copilot`, like every Foundry package. Only Claude Code can run the workflow, because it needs cross-session messaging.
