# repo-maintenance

Keep AGENTS.md files and agent configuration accurate and lean.

## What it installs

| Primitive | Name | Purpose |
| --- | --- | --- |
| Skill | `agents-md` | Initialise a codebase with hierarchical AGENTS.md documentation, and update it as the code changes. |
| Skill | `generate-agent-docs` | Initialise hierarchical AGENTS.md files that record each directory's rules and traps. |
| Skill | `optimise-agent-config` | Audit a repository's agent configuration for the active targets (Cursor, Claude Code, GitHub Copilot) or evaluate whether a specific artefact (instruction, skill, subagent) is correctly placed. |
| Instruction | `keep-agent-mds-up-to-date` | When a change renames, removes, moves or changes the behaviour of anything, find and fix every agent doc that still describes the old state. |

## Install

```bash
apm install Samuel-Harris/foundry/packages/repo-maintenance#v0.1.0 --target cursor,claude,copilot
```

## Targets

Deployed to `cursor`, `claude` and `copilot`.
