# claude-code-usage

Analyse Claude Code spend from local session files, and rank ways to reduce it.

## What it installs

| Primitive | Name | Purpose |
| --- | --- | --- |
| Skill | `claude-code-cost-review` | Analyse local Claude Code session files to find where Claude Code spend goes and which changes would cut it without lowering engineering quality. |

The skill reads Claude Code's session files under `~/.claude/projects/`, so it only works on a machine that runs Claude Code. Its script needs Python 3.10 or later and no third-party packages. Tests run with `python3 -m unittest discover -s packages/claude-code-usage/tests`.

## Install

```bash
apm install Samuel-Harris/foundry/packages/claude-code-usage#^0.1.0 --target cursor,claude,copilot
```

## Targets

Deployed to `cursor`, `claude` and `copilot`. The skill only has data to read on a machine that runs Claude Code.
