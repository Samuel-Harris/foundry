# s-stack

Run one large feature as cooperating Claude Code sessions, each in its own worktree and tmux pane.

## What it installs

| Primitive | Name | Purpose |
| --- | --- | --- |
| Skill | `sam-mode` | Run one large feature as a group of cooperating Claude Code sessions (a spec writer, an orchestrator, a planner and one session for each phase), each in its own git worktree and tmux pane, with verified and reviewed draft pull requests for each phase. Use for `/sam-mode start <feature>` or `/sam-mode <role>`. Needs Claude Code with cross-session messaging, tmux and workmux. Not for small patches or minor bug fixes, which one poteto-mode session handles. |

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
