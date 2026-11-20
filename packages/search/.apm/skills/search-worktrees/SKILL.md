---
name: search-worktrees
description: Find files, code, or content across all git worktrees of the current repository. Use when a search must cover every worktree, or when a naive find or grep across a worktree root is too slow because of dependency directories.
---

# Search Across Worktrees

Find files, code, or content across all git worktrees for the current repository.

## Why this skill exists

Each worktree usually contains heavyweight, gitignored dependency directories — package manager stores, virtualenvs, caches, build outputs. Multiply those across several worktrees and an unscoped `find` or `grep` must traverse hundreds of thousands of irrelevant files before it reaches the code you care about. Scope the search deliberately.

## Step 1 — Discover worktree paths

From any worktree, `git worktree list` returns all paths:

```bash
git worktree list --porcelain | sed -n 's/^worktree //p'
```

Loop over them line by line, so the loop works in both bash and zsh and with spaces in paths:

```bash
git worktree list --porcelain | sed -n 's/^worktree //p' | while IFS= read -r wt; do
  # per-worktree command using "$wt"
done
```

## Step 2 — Choose the right search strategy

### Finding files by name

Use `find`, but **scope it to a specific subdirectory**. Never search a worktree root without pruning.

```bash
git worktree list --porcelain | sed -n 's/^worktree //p' | while IFS= read -r wt; do
  find "$wt/<subdir>" -type f -name '<pattern>' 2>/dev/null
done
```

For source files, target the relevant top-level directories rather than the root.

### Searching file contents with ripgrep

`rg` respects `.gitignore` by default, which handles most of the bloat. Use it from each worktree root:

```bash
git worktree list --porcelain | sed -n 's/^worktree //p' | while IFS= read -r wt; do
  echo "=== $wt ==="
  rg -l '<pattern>' "$wt" 2>/dev/null
done
```

If `.gitignore` isn't enough — for example when searching a partially gitignored directory — add explicit globs:

```bash
git worktree list --porcelain | sed -n 's/^worktree //p' | while IFS= read -r wt; do
  rg -l '<pattern>' "$wt/<subdir>" --glob '*.md' 2>/dev/null
done
```

### Searching git history

Git history is shared across all worktrees (single `.git` object store), so run this once from any worktree:

```bash
# Commits that touched files matching a path pattern
git log --all --oneline --name-only -- '<path pattern>'

# Commits that added such a file
git log --all --oneline --diff-filter=A --name-only -- '<path pattern>'

# Commits whose message mentions a keyword
git log --all --oneline --grep='<keyword>'
```

## Directories to always exclude

These are the common heavyweight directories that exist per worktree. When using `find`, prune them explicitly. Read the repository's `.gitignore` and add any project-specific offenders:

| Directory | What it typically is |
| --- | --- |
| `node_modules/` | Node.js dependencies |
| `.venv/`, `venv/`, `.tox/` | Python virtual environments |
| `.conda/` | Conda environments |
| `.turbo/`, `.nx/` | Monorepo build caches |
| `.ruff_cache/`, `.mypy_cache/` | Linter and type-checker caches |
| `__pycache__/` | Python bytecode |
| `.terraform/` | Terraform provider binaries |
| `dist/`, `build/`, `target/` | Build outputs |
| generated-code directories | Machine-generated sources (check `.gitignore`) |

### `find` with pruning

```bash
git worktree list --porcelain | sed -n 's/^worktree //p' | while IFS= read -r wt; do
  find "$wt" \
    -path '*/node_modules' -prune -o \
    -path '*/.venv' -prune -o \
    -path '*/.tox' -prune -o \
    -path '*/.turbo' -prune -o \
    -path '*/.ruff_cache' -prune -o \
    -path '*/__pycache__' -prune -o \
    -path '*/.terraform' -prune -o \
    -path '*/dist' -prune -o \
    -path '*/build' -prune -o \
    -type f -name '*.md' -print 2>/dev/null
done
```

## Common search scenarios

### Find uncommitted changes across worktrees

```bash
git worktree list --porcelain | sed -n 's/^worktree //p' | while IFS= read -r wt; do
  echo "=== $(basename "$wt") ($(git -C "$wt" branch --show-current)) ==="
  git -C "$wt" status --short 2>/dev/null
done
```

### Search generated agent configuration

Agent configuration directories are usually small and are sometimes partially gitignored. Search them directly with an explicit glob rather than relying on `.gitignore`:

```bash
git worktree list --porcelain | sed -n 's/^worktree //p' | while IFS= read -r wt; do
  rg -l '<pattern>' "$wt/.agents" "$wt/.cursor" "$wt/.claude" "$wt/.github" --glob '*.md' 2>/dev/null
done
```

## Key principles

1. **Prefer `rg` over `find | grep`.** Ripgrep respects `.gitignore` automatically, skipping most bloat.
2. **Scope to the smallest subtree that could contain the result.** Searching one configuration directory is instant; searching the full worktree is not.
