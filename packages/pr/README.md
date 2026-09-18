# pr

Pull request comprehension and merge-readiness babysitting.

## What it installs

| Primitive | Name | Purpose |
| --- | --- | --- |
| Skill | `babysit` | >- |
| Skill | `code-tour` | Walk through every change in a pull request or Git diff as a chat-only, logically ordered code tour with clickable code citations, commit and review context, meaningful tests beside behaviour, and a complete appendix for non-behavioural churn. |
| Skill | `summarise-pr` | Summarise provided PR change context into concise PR-description bullets. |

## Depends on

- `swarm`

## Install

```bash
apm install Samuel-Harris/foundry/packages/pr#v0.1.0 --target cursor,claude,copilot
```

## Targets

Deployed to `cursor`, `claude` and `copilot`.
