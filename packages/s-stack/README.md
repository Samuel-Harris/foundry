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

## Targets

Deployed to `cursor`, `claude` and `copilot`, like every Foundry package. Only Claude Code can run the workflow, because it needs cross-session messaging.
