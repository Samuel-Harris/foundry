# default-stack

Meta-package that installs the default Foundry stack.

This package ships no primitives of its own; it exists so a consumer can install the default Foundry stack with one dependency.

## Depends on

- `coding-style`
- `execution`
- `git-diff`
- `p-stack`
- `pr`
- `repo-maintenance`
- `review`
- `s-stack`
- `skill-creation`

## Install

```bash
apm install Samuel-Harris/foundry/packages/default-stack#v0.1.0 --target cursor,claude,copilot
```

## Targets

Deployed to `cursor`, `claude` and `copilot`.
