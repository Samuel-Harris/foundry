# repo-maintenance

Keep AGENTS.md files and agent configuration accurate and lean.

## What it installs

| Primitive | Name | Purpose |
| --- | --- | --- |
| Skill | `agents-md` | Initialise a codebase with hierarchical AGENTS.md documentation, and update it as the code changes. |
| Skill | `generate-agent-docs` | Initialise comprehensive hierarchical AGENTS.md documentation across the entire codebase. |
| Skill | `optimise-agent-config` | Audit a repository's agent configuration for the active targets (Cursor, Claude Code, GitHub Copilot) or evaluate whether a specific artefact (instruction, skill, subagent) is correctly placed. |
| Instruction | `keep-agent-mds-up-to-date` | Keep project documentation (AGENTS.md, agent rules, skills, commands and hooks) up to date when code changes make them stale. |

## Depends on

- `swarm`

## Install

```bash
apm install Samuel-Harris/foundry/packages/repo-maintenance#v0.1.0 --target cursor,claude,copilot
```

## Targets

Deployed to `cursor`, `claude` and `copilot`.
