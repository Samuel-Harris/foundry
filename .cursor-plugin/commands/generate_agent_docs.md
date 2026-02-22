---
name: generate_agent_docs
description: Initialize comprehensive hierarchical AGENTS.md documentation across the entire codebase.
---

# Generate Agent Documentation

This command initializes comprehensive, hierarchical AGENTS.md documentation across the entire codebase. It explores the repository structure and creates AGENTS.md files in each directory following the hierarchical tagging system.

**Note**: For guidance on what AGENTS.md files should contain and how to update them, see the `agents_md_guide.md` skill.

## Execution Workflow

### Step 1: Map Directory Structure

Use an exploration subagent to list all directories recursively:

```text
Task(description="List directories recursively",
  subagent_type="explore",
  prompt="List all directories recursively. Exclude directories that should not be documented: prefer using .gitignore, .cursorignore, and .cursorindexingignore (if present) to determine exclusions; otherwise exclude common dependency, build, cache, and VCS directories (e.g. node_modules, .git, dist, build, __pycache__, .venv, coverage, .next, .nuxt) and any other project-specific directories that are clearly generated or tooling-only.")
```

### Step 2: Create Work Plan

Generate todo items for each directory, organized by depth level:

```text
Level 0: / (root)
Level 1: /src, /docs, /tests
Level 2: /src/components, /src/utils, /docs/api
...
```

**Important**: Process directories level by level, starting with the root and working down. This ensures parent references are valid when child directories reference their parent AGENTS.md files.

### Step 3: Generate Level by Level

**IMPORTANT**: Generate parent levels before child levels to ensure parent references are valid.

For each directory at the current level:

1. Read all files in the directory
2. Analyze purpose and relationships
3. Generate AGENTS.md content using the template from the `agents_md_guide.md` skill
4. Write file with proper parent reference (except root)

Use the skill's guidance for:

- AGENTS.md template structure
- Hierarchical tagging system
- Content quality standards
- Empty directory handling

### Step 4: Compare and Update (if exists)

When AGENTS.md already exists:

1. **Read existing content**
2. **Identify sections**:
   - Auto-generated sections (can be updated)
   - Manual sections (`<!-- MANUAL -->` preserved)
3. **Compare**:
   - New files added?
   - Files removed?
   - Structure changed?
4. **Merge**:
   - Update auto-generated content
   - Preserve manual annotations
   - Update timestamp

### Step 5: Validate Hierarchy

After generation, run validation checks:

| Check                     | How to Verify                                             | Corrective Action         |
| ------------------------- | --------------------------------------------------------- | ------------------------- |
| Parent references resolve | Read each AGENTS.md, check `<!-- Parent: -->` path exists | Fix path or remove orphan |
| No orphaned AGENTS.md     | Compare AGENTS.md locations to directory structure        | Delete orphaned files     |
| Completeness              | List all directories, check for AGENTS.md                 | Generate missing files    |
| Timestamps current        | Check `<!-- Generated: -->` dates                         | Regenerate outdated files |

Validation script pattern:

```bash
# Find all AGENTS.md files
find . -name "AGENTS.md" -type f

# Check parent references
grep -r "<!-- Parent:" --include="AGENTS.md" .
```

## Smart Delegation

| Task               | Agent           |
| ------------------ | --------------- |
| Directory mapping  | `explore`       |
| File analysis      | `generalPurpose` |
| Content generation | `generalPurpose`        |
| AGENTS.md writes   | `generalPurpose`        |

## Parallelization Rules

1. **Same-level directories**: Process in parallel
2. **Different levels**: Sequential (parent first)
3. **Large directories**: Spawn dedicated agent per directory
4. **Small directories**: Batch multiple into one agent

## Performance Considerations

- **Cache directory listings** - Don't re-scan same directories
- **Batch small directories** - Process multiple at once
- **Skip unchanged** - If directory hasn't changed, skip regeneration
- **Parallel writes** - Multiple agents writing different files simultaneously

## Empty Directory Handling

When encountering empty or near-empty directories:

| Condition                                 | Action                                                  |
| ----------------------------------------- | ------------------------------------------------------- |
| No files, no subdirectories               | **Skip** - do not create AGENTS.md                      |
| No files, has subdirectories              | Create minimal AGENTS.md with subdirectory listing only |
| Has only generated files (_.min.js,_.map) | Skip or minimal AGENTS.md                               |
| Has only config files                     | Create AGENTS.md describing configuration purpose       |

See the `agents_md_guide.md` skill for example minimal AGENTS.md templates.
