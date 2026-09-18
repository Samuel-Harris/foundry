# swarm

Coordinated parallel subagents working a shared task list.

## What it installs

| Primitive | Name | Purpose |
| --- | --- | --- |
| Skill | `swarm` | Coordinated parallel agents on a shared task list. |
| Agent | `build-fixer-low` | Simple build error fixer for trivial type errors and single-line fixes. |
| Agent | `build-fixer-medium` | Build and type error resolution specialist. |
| Agent | `executor-high` | Complex multi-file task executor for cross-module refactoring. |
| Agent | `executor-low` | Simple single-file task executor. |
| Agent | `executor-medium` | Focused task executor for implementation work. |
| Agent | `explore` | Thorough codebase search with cross-module reasoning. |

## Depends on

- `architect`

## Install

```bash
apm install Samuel-Harris/foundry/packages/swarm#v0.1.0 --target cursor,claude,copilot
```

## Targets

Deployed to `cursor`, `claude` and `copilot`.
