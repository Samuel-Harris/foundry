# coding-style

Core engineering rules and compatibility guardrails for agent-written code.

## What it installs

| Primitive   | Name                         | Purpose                                                                                                                                 |
| ----------- | ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| Instruction | `compatibility-surface-gate` | Gate backward-compatibility and dual code paths.                                                                                        |
| Instruction | `software-engineering-rules` | Core engineering rules for agent-written code — read before writing, think before coding, keep changes surgical, and verify with tests. |

## Install

```bash
apm install Samuel-Harris/foundry/packages/coding-style#v0.1.0 --target cursor,claude,copilot
```

## Targets

Deployed to `cursor`, `claude` and `copilot`.
