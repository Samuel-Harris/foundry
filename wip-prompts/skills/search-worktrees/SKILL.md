# Search Across Worktrees

Find files, code, or content across all git worktrees for the current repository.

## Why this skill exists

Each worktree contains multi-GB dependency trees that make naive `find` or `grep` across the worktree root time out. A single worktree's `.pixi/` alone holds ~57,000 files (2.6 GB); `node_modules` adds another ~1.2 GB. Multiply by 7 worktrees and an unscoped search must traverse hundreds of thousands of irrelevant files.

## Step 1 — Discover worktree paths

From any worktree, `git worktree list` returns all paths:

```bash
git worktree list --porcelain | grep '^worktree ' | sed 's/^worktree //'
```

Store these in a variable for subsequent steps:

```bash
worktrees=$(git worktree list --porcelain | grep '^worktree ' | sed 's/^worktree //')
```

## Step 2 — Choose the right search strategy

### Finding files by name

Use `find` but **scope to `.cursor/`** or another specific subdirectory. Never search the worktree root without pruning.

```bash
for wt in $worktrees; do
  find "$wt/.cursor" -type f -name '*swarm*' 2>/dev/null
done
```

For project source files, target the relevant top-level directories:

```bash
for wt in $worktrees; do
  find "$wt/backend" "$wt/frontend/apps" "$wt/frontend/packages" \
    -type f -name '*.py' -path '*/personal/*' 2>/dev/null
done
```

### Searching file contents with ripgrep

`rg` respects `.gitignore` by default, which handles most of the bloat. Use it from each worktree root:

```bash
for wt in $worktrees; do
  echo "=== $wt ==="
  rg -l 'pattern' "$wt" 2>/dev/null
done
```

If `.gitignore` isn't enough (e.g. searching `.cursor/` which is partially gitignored), add explicit globs:

```bash
for wt in $worktrees; do
  rg -l 'pattern' "$wt/.cursor" --glob '*.md' 2>/dev/null
done
```

### Searching git history

Git history is shared across all worktrees (single `.git` object store), so run this once from any worktree:

```bash
# Commits that touched files matching a path pattern
git log --all --oneline --diff-filter=A --name-only -- '.cursor/agents/personal/*'

# Commits whose message mentions a keyword
git log --all --oneline --grep='swarm'
```

## Directories to always exclude

These are the heavyweight directories that exist per-worktree (from `.gitignore`). When using `find`, prune them explicitly:

| Directory | What it is | Typical size per worktree |
|---|---|---|
| `.pixi/` | Pixi package manager env | ~2.6 GB, ~57k files |
| `node_modules/` | Node.js dependencies (multiple locations) | ~1.2 GB |
| `.conda/` | Conda environment | Large |
| `.venv/`, `backend/.venv/` | Python virtualenv | Large |
| `.turbo/` | Turborepo cache | Variable |
| `.ruff_cache/` | Ruff linter cache | Small but many files |
| `__pycache__/` | Python bytecode (scattered everywhere) | Many directories |
| `.terraform/` | Terraform provider binaries | Large |
| `.mypy_cache/` | mypy type checker cache | Many files |
| `dist/`, `build/` | Build outputs | Variable |
| `.omc/` | oh-my-claudecode state | Small |
| `frontend/packages/api/src/gen/` | Generated API types | Many files |

### `find` with pruning

```bash
for wt in $worktrees; do
  find "$wt" \
    -path '*/.pixi' -prune -o \
    -path '*/node_modules' -prune -o \
    -path '*/.conda' -prune -o \
    -path '*/.venv' -prune -o \
    -path '*/.turbo' -prune -o \
    -path '*/.ruff_cache' -prune -o \
    -path '*/__pycache__' -prune -o \
    -path '*/.terraform' -prune -o \
    -path '*/.mypy_cache' -prune -o \
    -path '*/.omc' -prune -o \
    -path '*/dist' -prune -o \
    -type f -name '*.md' -path '*/personal/*' -print 2>/dev/null
done
```

## Common search scenarios

### Find personal Cursor artefacts (skills, agents, commands)

These live under `.cursor/` and are tiny — search there directly:

```bash
for wt in $worktrees; do
  echo "=== $(basename "$wt") ==="
  find "$wt/.cursor" -path '*/personal/*' -type f 2>/dev/null
done
```

### Find a file you created recently but forgot where

Combine `find` with `-newer` or `-mtime`:

```bash
for wt in $worktrees; do
  find "$wt/.cursor" -type f -mtime -3 2>/dev/null
done
```

### Find uncommitted changes across worktrees

```bash
for wt in $worktrees; do
  echo "=== $(basename "$wt") ($(git -C "$wt" branch --show-current)) ==="
  git -C "$wt" status --short 2>/dev/null
done
```

### Search agent transcripts

Transcripts live in the Cursor projects directory, not in the worktree. Each worktree has its own project folder:

```bash
projects_dir="$HOME/.cursor/projects"
for wt in $worktrees; do
  # Cursor project folder names use dashes instead of path separators
  proj_name=$(echo "$wt" | sed 's|^/||; s|/|-|g')
  transcripts="$projects_dir/$proj_name/agent-transcripts"
  if [ -d "$transcripts" ]; then
    echo "=== $(basename "$wt") ==="
    rg -l 'pattern' "$transcripts" 2>/dev/null
  fi
done
```

## Key principles

1. **Never `find` from the worktree root without pruning.** The dependency directories will cause timeouts.
2. **Prefer `rg` over `find | grep`.** Ripgrep respects `.gitignore` automatically, skipping most bloat.
3. **Scope to the smallest subtree that could contain the result.** Searching `.cursor/` for Cursor artefacts is instant; searching the full worktree is not.
4. **Git history is shared.** You only need to search it once from any worktree — all branches and commits are visible everywhere.
5. **Transcripts are outside the repo.** They live in `~/.cursor/projects/`, keyed by the worktree's filesystem path.
