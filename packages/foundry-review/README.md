# foundry-review

Branch-level correctness, security and maintainability audits.

## What it installs

| Primitive | Name | Purpose |
| --- | --- | --- |
| Skill | `thermo-nuclear-code-quality-review` | Run an extremely strict maintainability review for abstraction quality, giant files, and spaghetti-condition growth. |
| Skill | `thermo-nuclear-review` | Comprehensive security and correctness audit of a branch's changes. |
| Skill | `thermos` | Launch both thermo-nuclear review subagents in parallel, then synthesise their findings. |
| Agent | `thermo-nuclear-code-quality-review-subagent` | Thermo-nuclear code quality audit (maintainability, structure, 1k-line rule, spaghetti, code-judo). |
| Agent | `thermo-nuclear-review-subagent` | Thermo-nuclear branch audit (bugs, breaking changes, security, devex, feature-flag leaks) scoped to the diff. |

## Install

```bash
apm install Samuel-Harris/foundry/packages/foundry-review#v0.1.0 --target cursor,claude,copilot
```

## Targets

Deployed to `cursor`, `claude` and `copilot`.
