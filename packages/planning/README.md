# planning

Plan authoring and plan review.

## What it installs

| Primitive | Name | Purpose |
| --- | --- | --- |
| Skill | `masterplan` | Generate a holistic product vision from Linear tickets. |
| Skill | `ralplan` | Iterative planning consensus loop. |
| Agent | `critic` | Work plan review expert and critic. |
| Agent | `planner` | Strategic planning consultant with interview workflow. |
| Instruction | `plan-handoff-standard` | Use when creating or refining implementation plans, especially handoff-ready plans another agent will execute. |

## Depends on

- `architect`
- `deep-interview`
- `review`
- `swarm`

## Install

```bash
apm install Samuel-Harris/foundry/packages/planning#v0.1.0 --target cursor,claude,copilot
```

## Targets

Deployed to `cursor`, `claude` and `copilot`.
