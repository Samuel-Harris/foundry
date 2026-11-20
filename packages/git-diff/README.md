# git-diff

Read-only git diff summaries measured against a repository's main branch.

## What it installs

| Primitive | Name | Purpose |
| --- | --- | --- |
| Skill | `git-diff-all-changes-main` | Show all changes compared to origin/main. |
| Skill | `git-diff-committed-changes-main` | Show committed changes on this branch since it diverged from origin/main, excluding staged and unstaged edits. |
| Skill | `git-diff-staged-changes-main` | Show staged and committed changes compared to the merge base with origin/main, excluding unstaged edits. |

## Install

```bash
apm install Samuel-Harris/foundry/packages/git-diff#v0.1.0 --target cursor,claude,copilot
```

## Targets

Deployed to `cursor`, `claude` and `copilot`.
