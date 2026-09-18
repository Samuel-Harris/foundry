# foundry-default-stack

Meta-package that installs the default Foundry stack.

This package ships no primitives of its own; it exists so a consumer can install the default Foundry stack with one dependency.

## Depends on

- `foundry-coding-style`
- `foundry-execution`
- `foundry-git-diff`
- `foundry-planning`
- `foundry-pr`
- `foundry-repo-maintenance`
- `foundry-review`
- `foundry-skill-creation`

## Install

```bash
apm install Samuel-Harris/foundry/packages/foundry-default-stack#v0.1.0 --target cursor,claude,copilot
```

## Targets

Deployed to `cursor`, `claude` and `copilot`.
