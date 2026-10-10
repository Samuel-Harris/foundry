# cursor-usage

Analyse Cursor spend from a usage export and local transcripts, and rank ways to reduce it.

## What it installs

| Primitive | Name | Purpose |
| --- | --- | --- |
| Skill | `cursor-cost-review` | Analyse an exported Cursor usage-events CSV together with local agent transcripts to find where Cursor spend goes and which changes would cut it without lowering engineering quality. |

The skill reads Cursor's local transcripts under `~/.cursor/projects/`, so its transcript analysis only works on a machine that runs Cursor. Its scripts need Python 3.10 or later and no third-party packages.

## Install

```bash
apm install Samuel-Harris/foundry/packages/cursor-usage#v0.1.0 --target cursor,claude,copilot
```

## Targets

Deployed to `cursor`, `claude` and `copilot`.
