---
name: agents-md
description: Initialise a codebase with hierarchical AGENTS.md documentation, and update it as the code changes.
---

# AGENTS.md Skill

## Core Concept

AGENTS.md files serve as **AI-readable documentation** that helps agents understand:

- The rules and contracts that hold in that area
- The traps a competent editor would fall into there
- Where to read next for a deeper task

## Hierarchical Tagging System

Every AGENTS.md (except root) includes a parent reference tag:

```markdown
<!-- Parent: ../AGENTS.md -->
```

This creates a navigable hierarchy:

```
/AGENTS.md                          ← Root (no parent tag)
├── src/AGENTS.md                   ← <!-- Parent: ../AGENTS.md -->
│   ├── src/components/AGENTS.md    ← <!-- Parent: ../AGENTS.md -->
│   └── src/utils/AGENTS.md         ← <!-- Parent: ../AGENTS.md -->
└── docs/AGENTS.md                  ← <!-- Parent: ../AGENTS.md -->
```

## AGENTS.md Template

```markdown
<!-- Parent: {relative_path_to_parent}/AGENTS.md -->

# {Directory name}

{One or two sentences: what this directory is for and where it sits in the system. Omit when the name says it.}

## Rules

{Invariants and contracts that hold for every file here and that the code cannot show.}

## Traps

{Things a competent editor would get wrong: ordering constraints, files that must change together, generated files, non-obvious consequences.}

## Where to read next

{Only for routing a task to a deeper AGENTS.md, skill or doc. Not a directory listing.}
```

Omit any empty section. Do not list files, subdirectories, dependencies or code patterns the code already shows. Create an `AGENTS.md` only for a directory that has at least one rule or trap; a directory with none gets no file.

## Execution Workflow

### Step 1: Map Directory Structure

**CRITICAL**: DO NOT generate documentation for any directory that is ignored by `.gitignore` or the host's ignore file (e.g. `.cursorignore`), if one exists.

```text
Dispatch a read-only exploration subagent (the host's built-in explore agent where one exists) with the
prompt below. Where the host has no subagents, equivalent direct read-only inspection is fine:
"List all directories recursively. STRICTLY EXCLUDE any directories that are ignored by .gitignore or the host's ignore file. Also exclude common dependency, build, cache, and VCS directories (e.g. node_modules, .git, dist, build, __pycache__, .venv, coverage, .next, .nuxt) and any other project-specific directories that are clearly generated or tooling-only."
```

### Step 2: Create Work Plan

Generate todo items for each directory, organized by depth level:

```
Level 0: / (root)
Level 1: /src, /docs, /tests
Level 2: /src/components, /src/utils, /docs/api
...
```

### Step 3: Generate Level by Level

**IMPORTANT**: Generate parent levels before child levels to ensure parent references are valid.

For each directory:

1. Read all files in the directory
2. Analyze purpose and relationships
3. Draft only lines that pass every check in [Before you write a line](#before-you-write-a-line); skip the directory when none do
4. Write file with proper parent reference

### Step 4: Compare and Update (if exists)

When AGENTS.md already exists:

1. **Read existing content**
2. **Identify sections**:
   - Auto-generated sections (can be updated)
   - Manual sections (`<!-- MANUAL -->` preserved)
3. **Compare**: does any line name a path, symbol or command that no longer exists, or a rule the code no longer enforces?
4. **Merge**:
   - Update auto-generated content
   - Preserve manual annotations

### Step 5: Validate Hierarchy

After generation, run validation checks:

| Check                     | How to Verify                                             | Corrective Action         |
| ------------------------- | --------------------------------------------------------- | ------------------------- |
| Parent references resolve | Read each AGENTS.md, check `<!-- Parent: -->` path exists | Fix path or remove orphan |
| No orphaned AGENTS.md     | Compare AGENTS.md locations to directory structure        | Delete orphaned files     |

Validation script pattern:

```bash
# Find all AGENTS.md files
find . -name "AGENTS.md" -type f

# Check parent references
grep -r "<!-- Parent:" --include="AGENTS.md" .
```

## Before you write a line

Each line must pass all of these. Delete the line if it fails one.

- **Verified.** You read the code, config or test that makes it true in this session. Run `ls` or `rg` on every path, symbol, config key, skill name and command it names, from the directory the reader starts in. A behaviour claim ("every X does Y", "nothing else writes Z", "the test checks W") holds only if you found the code that enforces it; otherwise say it is a convention, or leave it out.
- **Not visible in the code.** It is a trap, contract, invariant, or cross-file consequence that reading the file would not show. Do not restate signatures, docstrings, a pipeline's stages, a directory's files, or a rule a hook or linter already enforces and explains.
- **Concrete.** Name the thing: the replacement when you say what not to use, the field when you say what a value carries.
- **Owned here.** It is not already stated in another `AGENTS.md`, rule or docstring; link to that owner instead. It sits under the heading it is about.
- **Follows the repository's prose rules** for always-loaded files.

## Triggering Update Mode

When running on an existing codebase with AGENTS.md files:

1. Detect existing files first
2. Read and parse existing content
3. Analyze current directory state
4. Generate diff between existing and current
5. Apply updates while preserving manual sections
