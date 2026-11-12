# coding-style

Core engineering rules, compatibility guardrails and Python style for agent-written code.

## What it installs

| Primitive   | Name                         | Purpose                                                                                                                                 |
| ----------- | ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| Instruction | `compatibility-surface-gate` | Gate backward-compatibility and dual code paths.                                                                                        |
| Instruction | `python-rules`               | Python style rules, applied to `**/*.py` — keyword-only parameters, `NewType` and `NamedTuple` for domain values, top-of-file imports and no unused export surfaces. |
| Instruction | `software-engineering-rules` | Core engineering rules for agent-written code — read before writing, think before coding, keep changes surgical, verify with tests, and keep agent context progressively disclosed. |

## Install

```bash
apm install Samuel-Harris/foundry/packages/coding-style#v0.1.0 --target cursor,claude,copilot
```

## Targets

Deployed to `cursor`, `claude` and `copilot`.
