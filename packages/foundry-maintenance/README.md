# foundry-maintenance

Keep Foundry's own guidance current by mining recent PR reviews and agent transcripts.

## What it installs

| Primitive | Name | Purpose |
| --- | --- | --- |
| Skill | `guidance-retro` | Mine a repository's PR review comments and the user's local Claude Code and Cursor transcripts over a window, fanned out across subagents, and publish a report of which Foundry skills, agents and instructions to add, update or delete. |

The skill runs only from a Foundry checkout, because its recommendations name Foundry source paths. It reads transcripts under `~/.claude/projects/` and `~/.cursor/projects/`, and PR comments through an authenticated `gh`. Its scripts need Python 3.10 or later and no third-party packages. Their tests run with `python3 -m unittest discover -s packages/foundry-maintenance/tests`.

## Install

```bash
apm install Samuel-Harris/foundry/packages/foundry-maintenance#^0.1.0 --target cursor,claude,copilot
```

## Targets

Deployed to `cursor`, `claude` and `copilot`.
