---
name: explain-pr
description: Walk through the current PR's changelist with the user. Explains what changed and why using parallel subagents for large diffs. Use when asking to explain, walk through, or summarise a PR or branch changes.
disable-model-invocation: true
---

# Explain PR

Walk the user through the changelist on the current branch. The goal is **comprehension**, not review — help the user understand what changed, why, and how the pieces fit together.

## Instructions

### Step 1: Determine the diff

Check if the user already ran a diff command in this conversation.

**If NO diff was run**, ask TWO questions using the AskQuestion tool:

**A) Base branch:**
- `origin/dev` — Normal development (default)
- `origin/main` — Hotfix going directly to production

**B) What changes to include:**

| Scenario | What to review | Git command |
|----------|---------------|-------------|
| **PR / branch changes** | All commits on this branch vs base | `<merge-base>...HEAD` |
| **Staged** | Staged changes only | `--staged` |
| **Unstaged** | Unstaged changes only | *(no args)* |
| **All local changes** | Everything not pushed vs base | `<merge-base>..HEAD` |

**If a diff WAS already run**, reuse those refs.

### Step 2: Compute the diff and gather stats

```bash
# For branch-based comparisons (PR, all local):
git fetch origin <base-branch>
MERGE_BASE=$(git merge-base origin/<base-branch> HEAD)
git diff --stat "$MERGE_BASE" HEAD
git diff --name-only "$MERGE_BASE" HEAD

# For staged:
git diff --staged --stat
git diff --staged --name-only

# For unstaged:
git diff --stat
git diff --name-only
```

### Step 3: Decide walkthrough strategy

Count changed files and total lines changed from the `--stat` output.

| Changelist size | Threshold | Strategy |
|-----------------|-----------|----------|
| **Small** | ≤ 8 files **and** ≤ 400 lines | Walk through the diff directly — no subagents needed |
| **Large** | > 8 files **or** > 400 lines | Spawn parallel `cursor-explore-low` subagents per domain (step 4) |

For a **small** changelist, skip to step 5 and explain the changes inline.

### Step 4: Spawn exploration subagents (large changelists only)

Group changed files by domain, then launch one `cursor-explore-low` subagent per domain that has changes. Each subagent runs in **readonly** mode. Use `-low` because diff summarisation is lightweight — no cross-module reasoning needed.

| Domain | File patterns | Subagent type |
|--------|---------------|---------------|
| Backend | `backend/**/*.py` (excluding alembic) | `cursor-explore-low` |
| Frontend | `frontend/**/*.{ts,tsx,js,jsx,css}` | `cursor-explore-low` |
| Database / Migrations | `backend/alembic/**/*`, `database/**/*` | `cursor-explore-low` |
| Infrastructure | `terraform/**/*`, `.github/**/*`, `amplify.yml`, `docker-compose*.yml`, `**/Dockerfile*` | `cursor-explore-low` |
| Other | Everything not captured above | `cursor-explore-low` |

**Subagent prompt template** — adapt per domain:

> You are exploring a git diff to explain changes to the user.
>
> Run: `git diff <diff-refs> -- <file-patterns>`
>
> For each logical group of changes, produce:
> 1. **What changed** — concise description of the modification
> 2. **Why** — infer the motivation from context (commit messages, surrounding code, naming)
> 3. **How it connects** — note dependencies on or from other changed files
>
> Changed files in your domain:
> ```
> <file list>
> ```
>
> Return a structured summary grouped by logical change, not by file.

Launch all domain subagents in parallel (max 4 concurrent).

### Step 5: Present the walkthrough

Compile results into a structured explanation. Use this format:

```
## PR Walkthrough

### Overview
[1–3 sentence summary of the overall change and its purpose]

### Changes

#### <Logical Group 1 title>
**Files:** `path/a.py`, `path/b.py`

<What changed, why, and how it connects to the rest>

#### <Logical Group 2 title>
...

### Dependency chain (if applicable)
[Show how changes flow: e.g., model → schema → CRUD → endpoint → frontend hook → component]
```

**Grouping rules:**
- Group by **logical change**, not by file or domain. A schema + endpoint + frontend hook that all serve the same feature belong together.
- For small changelists, a single group is fine.
- Use code references (`` `startLine:endLine:filepath` ``) to point the user at key sections.

### Step 6: Offer follow-ups

After presenting the walkthrough, ask the user:

> Anything you'd like me to dive deeper into? I can:
> - Explain a specific file or function in more detail
> - Show the before/after for a particular change
> - Trace the data flow through the stack

## Notes

- This is a **comprehension** tool, not a review tool. Avoid value judgements or suggestions unless the user asks.
- Subagents run in readonly mode.
- Prefer `cursor-explore-low` subagents for this task since the goal is summarisation, not deep analysis.
- When inferring "why", lean on commit messages (`git log --oneline <merge-base>..HEAD`) and surrounding code context.
