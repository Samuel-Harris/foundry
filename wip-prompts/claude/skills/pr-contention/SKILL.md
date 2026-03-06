---
name: pr-contention
description: Analyse open PRs for merge/logic conflicts and recommend strategies to reduce contention
argument-hint: [github-username (default: @me)]
allowed-tools: Bash, Agent, Read, Grep, Glob
---

# PR Contention Analysis

Analyse all active (open, non-draft) PRs for a given author, identify overlap and contention risks, and recommend prioritised strategies to maximise merge parallelism.

Read the reference files before starting:

- `cat .claude/skills/pr-contention/references/analysis-process.md`
- `cat .claude/skills/pr-contention/references/recommendation-framework.md`
- `cat .claude/skills/pr-contention/references/implementation-actions.md`

## Naming convention

Always refer to PRs by both number AND title throughout the analysis — developers don't remember PRs by number alone. Format: `#14476 (Optimise vector db migration)`. After the first mention in a section, a short parenthetical is fine.

## Phase 1: Gather data (always run)

The target author is "$ARGUMENTS". If empty, default to `@me`.

Follow the steps in `references/analysis-process.md` to:

1. Gather the PR inventory (open, non-draft only)
2. Collect changed files per PR — run `gh pr diff <N> --name-only` for all PRs in parallel bash calls (not subagents). Handle large diffs (HTTP 406) via `gh api` fallback. For very large PRs with data/asset files, filter to code-only files and note the data file count separately.
3. Check merge status (`gh pr view <N> --json mergeable`) and staleness (`git rev-list --count`) — run all in a single parallel batch of bash calls.
4. Build the file overlap matrix across all PR pairs.
5. Identify hot files (touched by 3+ PRs).

## Phase 2: Investigate actual conflicts (always run)

Do NOT assume that file overlap means dependency. Investigate the actual diffs.

For each pair of PRs with shared files, launch a subagent to:

1. Run `git diff origin/dev...origin/<branch> -- <file>` for each shared file on both branches
2. Run `git merge-tree $(git merge-base origin/<branchA> origin/<branchB>) origin/<branchA> origin/<branchB>` to check for real merge conflicts
3. Classify each shared file as:
   - **IDENTICAL**: Both PRs produce the same diff (shared prerequisite work)
   - **INDEPENDENT**: Different sections of the file, git auto-merges cleanly
   - **CONFLICTING**: Same lines/blocks modified differently, git cannot auto-merge
   - **DEPENDENT**: One PR's changes require or extend the other's

Parallelise across PR pairs using subagents — one subagent per pair.

The goal is to determine: which PRs can truly merge in parallel, and which have real blocking dependencies?

## Phase 3: Report (always output)

Present findings in this structure:

### PR Inventory

Table with columns: PR #, Title, Branch, Age, Mergeable, Files Changed, Behind dev

### Overlap Map

For each pair of PRs that share files, list the shared file count and the investigation verdict:
- How many files are IDENTICAL / INDEPENDENT / CONFLICTING / DEPENDENT
- Call out the specific CONFLICTING files and briefly explain what each PR does to them
- Highlight files shared by 3+ PRs as "hot files"

### Dependency Graph

Draw an ASCII diagram showing the actual merge dependencies based on the conflict investigation (not assumptions from file overlap). Show which PRs can merge in parallel and which must be sequential.

### Recommendations

Apply the priority framework from `references/recommendation-framework.md`.

For each recommendation:
- **ID**: Sequential (R1, R2, R3...)
- **Priority**: P0 / P1 / P2 / P3
- **Action**: One-line summary
- **Detail**: What to do and why
- **PRs**: Which PRs are affected (by number AND title)
- **Risk if ignored**: What happens if this isn't addressed

Focus recommendations on **maximising parallelism** — what can be done to decouple PRs that currently block each other?

Group recommendations by priority level:

```
### P0 — Critical (high impact, low effort)
R1. ...

### P1 — Important (high impact, moderate effort)
R2. ...

### P2 — Recommended (moderate impact)
R3. ...

### P3 — Nice to Have (lower impact)
R4. ...
```

### After Recommendations Diagram

Draw a second ASCII diagram showing what the merge order would look like IF all recommendations were implemented. Contrast with the current-state diagram to show the improvement.

End the report with:

> **Ready to proceed?** Tell me which recommendations to implement (e.g., "proceed with R1, R3, R5") or "proceed with all P0 and P1".

## Phase 4: Implementation (only after user confirms)

CRITICAL: Do NOT execute any implementation actions until the user explicitly confirms which recommendations to proceed with. The analysis and report are read-only operations.

Once the user confirms, follow the procedures in `references/implementation-actions.md` for each approved recommendation. For destructive or hard-to-reverse actions (force-push, branch deletion, PR closure), confirm with the user before each individual action.
