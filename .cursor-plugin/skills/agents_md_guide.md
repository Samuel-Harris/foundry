---
name: agents_md_guide
description: Guide for understanding, creating, and updating hierarchical AGENTS.md documentation files.
---

# AGENTS.md Documentation Skill

This skill provides guidance on what AGENTS.md files should contain, how to structure them, and how to update them. Use this skill when you need to understand or modify AGENTS.md files.

**Note**: To initialize AGENTS.md documentation across an entire repository, use the `generate_agent_docs` command instead.

## Core Concept

AGENTS.md files serve as **AI-readable documentation** that helps agents understand:

- What each directory contains
- How components relate to each other
- Special instructions for working in that area
- Dependencies and relationships

## Hierarchical Tagging System

Every AGENTS.md (except root) includes a parent reference tag:

```markdown
<!-- Parent: ../AGENTS.md -->
```

This creates a navigable hierarchy:

```text
/AGENTS.md                          ← Root (no parent tag)
├── src/AGENTS.md                   ← <!-- Parent: ../AGENTS.md -->
│   ├── src/components/AGENTS.md    ← <!-- Parent: ../AGENTS.md -->
│   └── src/utils/AGENTS.md         ← <!-- Parent: ../AGENTS.md -->
└── docs/AGENTS.md                  ← <!-- Parent: ../AGENTS.md -->
```

## AGENTS.md Template

```markdown
<!-- Parent: {relative_path_to_parent}/AGENTS.md -->
<!-- Generated: {timestamp} | Updated: {timestamp} -->

# {Directory Name}

## Purpose

{One-paragraph description of what this directory contains and its role}

## Key Files

{List each significant file with a one-line description}

| File      | Description                  |
| --------- | ---------------------------- |
| `file.ts` | Brief description of purpose |

## Subdirectories

{List each subdirectory with brief purpose}

| Directory | Purpose                                   |
| --------- | ----------------------------------------- |
| `subdir/` | What it contains (see `subdir/AGENTS.md`) |

## For AI Agents

### Working In This Directory

{Special instructions for AI agents modifying files here}

### Testing Requirements

{How to test changes in this directory}

### Common Patterns

{Code patterns or conventions used here}

## Dependencies

### Internal

{References to other parts of the codebase this depends on}

### External

{Key external packages/libraries used}

<!-- MANUAL: Any manually added notes below this line are preserved on regeneration -->
```

## Updating Existing AGENTS.md Files

When updating an existing AGENTS.md file:

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

## Empty Directory Handling

When encountering empty or near-empty directories:

| Condition                                 | Action                                                  |
| ----------------------------------------- | ------------------------------------------------------- |
| No files, no subdirectories               | **Skip** - do not create AGENTS.md                      |
| No files, has subdirectories              | Create minimal AGENTS.md with subdirectory listing only |
| Has only generated files (_.min.js,_.map) | Skip or minimal AGENTS.md                               |
| Has only config files                     | Create AGENTS.md describing configuration purpose       |

Example minimal AGENTS.md for directory-only containers:

```markdown
<!-- Parent: ../AGENTS.md -->

# {Directory Name}

## Purpose

Container directory for organizing related modules.

## Subdirectories

| Directory | Purpose                              |
| --------- | ------------------------------------ |
| `subdir/` | Description (see `subdir/AGENTS.md`) |
```

## Quality Standards

### Must Include

- [ ] Accurate file descriptions
- [ ] Correct parent references
- [ ] Subdirectory links
- [ ] AI agent instructions

### Must Avoid

- [ ] Generic boilerplate
- [ ] Incorrect file names
- [ ] Broken parent references
- [ ] Missing important files

## Example Output

### Root AGENTS.md

```markdown
<!-- Generated: 2024-01-15 | Updated: 2024-01-15 -->

# my-project

## Purpose

A web application for managing user tasks with real-time collaboration features.

## Key Files

| File            | Description                      |
| --------------- | -------------------------------- |
| `package.json`  | Project dependencies and scripts |
| `tsconfig.json` | TypeScript configuration         |
| `.env.example`  | Environment variable template    |

## Subdirectories

| Directory | Purpose                                       |
| --------- | --------------------------------------------- |
| `src/`    | Application source code (see `src/AGENTS.md`) |
| `docs/`   | Documentation (see `docs/AGENTS.md`)          |
| `tests/`  | Test suites (see `tests/AGENTS.md`)           |

## For AI Agents

### Working In This Directory

- Always install dependencies after modifying the project manifest
- Use TypeScript strict mode
- Follow ESLint rules

### Testing Requirements

- Run tests before committing
- Ensure >80% coverage

### Common Patterns

- Use barrel exports (index.ts)
- Prefer functional components

## Dependencies

### External

- React 18.x - UI framework
- TypeScript 5.x - Type safety
- Vite - Build tool

<!-- MANUAL: Custom project notes can be added below -->
```

### Nested AGENTS.md

```markdown
<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2024-01-15 | Updated: 2024-01-15 -->

# components

## Purpose

Reusable React components organized by feature and complexity.

## Key Files

| File         | Description                      |
| ------------ | -------------------------------- |
| `index.ts`   | Barrel export for all components |
| `Button.tsx` | Primary button component         |
| `Modal.tsx`  | Modal dialog component           |

## Subdirectories

| Directory | Purpose                                         |
| --------- | ----------------------------------------------- |
| `forms/`  | Form-related components (see `forms/AGENTS.md`) |
| `layout/` | Layout components (see `layout/AGENTS.md`)      |

## For AI Agents

### Working In This Directory

- Each component has its own file
- Use CSS modules for styling
- Export via index.ts

### Testing Requirements

- Unit tests in `__tests__/` subdirectory
- Use React Testing Library

### Common Patterns

- Props interfaces defined above component
- Use forwardRef for DOM-exposing components

## Dependencies

### Internal

- `src/hooks/` - Custom hooks used by components
- `src/utils/` - Utility functions

### External

- `clsx` - Conditional class names
- `lucide-react` - Icons

<!-- MANUAL: -->
```

## Validation

When working with AGENTS.md files, validate:

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
