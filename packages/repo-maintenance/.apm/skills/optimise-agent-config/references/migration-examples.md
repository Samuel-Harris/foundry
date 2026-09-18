# Migration Examples

Detailed examples for migrating host artefacts to skills and for writing recommendations. Migrations target the APM primitives so the result deploys to every active target: **Cursor**, **Claude Code** and **GitHub Copilot**.

- skills: `.apm/skills/<name>/SKILL.md` → `.cursor/skills/`, `.claude/skills/`, `.agents/skills/`
- agents: `.apm/agents/<name>.agent.md` → `.cursor/agents/`, `.claude/agents/`, `.github/agents/`
- instructions: `.apm/instructions/<name>.instructions.md` → `.cursor/rules/`, `.claude/rules/`, `.github/instructions/`

## Migrating Apply-Intelligently Instructions to Skills (Optional)

Instructions that load on agent judgement (a `description` with no file-pattern scope) can optionally be migrated to skills. This is beneficial when:

- The instruction contains multi-step procedural instructions
- The instruction would benefit from `references/` subdirectory organisation
- The instruction is >200 lines and could use progressive disclosure

The apply-intelligently form differs per host:

| Host            | File                                       | Apply-intelligently signal                                |
| --------------- | ------------------------------------------ | --------------------------------------------------------- |
| Cursor          | `.cursor/rules/*.mdc`                      | `description` present, no `globs`, no `alwaysApply: true` |
| Claude Code     | `.claude/rules/*.md`                       | `description` present, no `paths`                         |
| GitHub Copilot  | `.github/instructions/*.instructions.md`   | `applyTo: "**"` (the broadest scope the host supports)    |

**Note:** Cursor includes a built-in `/migrate-to-skills` command that can do the Cursor migration automatically. Claude Code and GitHub Copilot have no built-in equivalent, so migrate those manually using the same before/after shape.

Manual migration, one source form per host:

**Before — Cursor** (`.cursor/rules/my-rule.mdc`):

```yaml
---
description: What this rule does
globs:
alwaysApply: false
---
# Title
Body content...
```

**Before — Claude Code** (`.claude/rules/my-rule.md`):

```yaml
---
description: What this rule does
---
# Title
Body content...
```

**Before — GitHub Copilot** (`.github/instructions/my-rule.instructions.md`):

```yaml
---
description: What this rule does
applyTo: "**"
---
# Title
Body content...
```

**After — for every host** (`.apm/skills/my-rule/SKILL.md`):

```yaml
---
name: my-rule
description: What this rule does
---
# Title
Body content...
```

Then delete the original instruction (`.cursor/rules/my-rule.mdc`, `.claude/rules/my-rule.md` or `.github/instructions/my-rule.instructions.md`). The skill format provides the same agent discovery via `description`, but with better organisation (reference docs in subdirectories) and clearer intent.

---

## Migrating Commands to Skills (Optional)

Commands still work, but skills with `disable-model-invocation: true` are the newer alternative. Cursor's built-in `/migrate-to-skills` command can do the Cursor migration automatically; Claude Code and GitHub Copilot have no equivalent, so migrate those manually.

Manual migration, one source form per host:

**Before — Cursor** (`.cursor/commands/commit.md`):

```markdown
# Commit current work

Instructions here...
```

**Before — Claude Code** (`.claude/commands/commit.md`):

```markdown
# Commit current work

Instructions here...
```

**Before — GitHub Copilot** (`.github/prompts/commit.prompt.md`):

```markdown
---
description: Commit current work with standardised message format
---
# Commit current work

Instructions here...
```

Copilot prompt frontmatter keys other than `description` (for example `mode` and `tools`) have no skill equivalent and are dropped during migration; the skill frontmatter contract governs instead.

**After — for every host** (`.apm/skills/commit/SKILL.md`):

```yaml
---
name: commit
description: Commit current work with standardised message format
disable-model-invocation: true
---
# Commit current work
Instructions here...
```

Then delete the original command file (`.cursor/commands/commit.md`, `.claude/commands/commit.md` or `.github/prompts/commit.prompt.md`). The `disable-model-invocation: true` flag prevents the model from automatically invoking the skill — it is only triggered when the user explicitly types `/commit` (Cursor, Claude Code) or runs the prompt (GitHub Copilot).

---

## Example Recommendations

### [P0] Fix missing skill frontmatter

> `.apm/skills/devtools-cli/SKILL.md` is missing its frontmatter block. Without `name` and `description`, the agent cannot discover this skill on any host.
>
> **Add frontmatter** to the beginning of the file:
>
> ```yaml
> ---
> name: devtools-cli
> description: CLI command reference for development tasks. Use when the user asks to start services, run tests, manage worktrees, or reset the database.
> ---
> # Devtools CLI
> [existing content...]
> ```
>
> **Why:** Skills without `description` in frontmatter are invisible to skill discovery. The agent will never proactively use this skill, defeating its purpose. Confirm the fix with `scripts/validate-artefacts.sh`.

### [P0] Move area-specific content out of root AGENTS.md

> The root `AGENTS.md` contains 45 lines of Alembic migration conventions (lines 87–131). This loads on every request but is only relevant when working with migration files.
>
> **Create** `backend/alembic/AGENTS.md`:
>
> ```markdown
> # Alembic migrations
>
> [extracted migration content]
> ```
>
> **Remove** lines 87–131 from the root `AGENTS.md` and replace them with a one-line pointer: `| backend/alembic/ | Database migrations (see backend/alembic/AGENTS.md) |`
>
> **Why:** Reduces always-on context by ~45 lines and places the guidance in a portable document, which Cursor, Claude Code and GitHub Copilot all read. Only use a host-specific instruction if precise file-pattern scoping is genuinely required (for example only `backend/alembic/versions/*.py`), in which case the scope field is `globs` on Cursor (`.cursor/rules/`), `paths` on Claude Code (`.claude/rules/`) and `applyTo` on GitHub Copilot (`.github/instructions/`).

### [P0] Delete broad glob-scoped instruction (content duplicates AGENTS.md)

> `.cursor/rules/python-conventions.mdc` has glob `src/**/*.py`, where most of the files in `src/` are Python files. The equivalent Claude Code instruction (`.claude/rules/python-conventions.md`) and GitHub Copilot instruction (`.github/instructions/python-conventions.instructions.md`) scope the same directory. The content is:
>
> - Max line length: 88 characters
> - Use type hints on all public functions
> - Prefer `pathlib.Path` over `os.path`
>
> All of this already appears in `src/AGENTS.md` (in the "Code Style" section).
>
> **Delete** `.cursor/rules/python-conventions.mdc`, `.claude/rules/python-conventions.md` and `.github/instructions/python-conventions.instructions.md`.
>
> **Why:** A glob like `src/**/*.py` matches the same files that `src/AGENTS.md` naturally scopes to — duplicating the content creates maintenance burden with no benefit. Prefer AGENTS.md because it is portable across AI coding agents (Cursor, Claude Code, GitHub Copilot and others), whereas host-specific instructions are not.

### [P0] Migrate broad glob-scoped instruction to AGENTS.md

> `.cursor/rules/react-patterns.mdc` has glob `packages/ui/**/*.tsx,packages/ui/**/*.ts`, where most of the files in `packages/ui/` are TypeScript files. The equivalent Claude Code instruction (`.claude/rules/react-patterns.md`) and GitHub Copilot instruction (`.github/instructions/react-patterns.instructions.md`) cover the same scope. The content is NOT present in `packages/ui/AGENTS.md`.
>
> **Add to** `packages/ui/AGENTS.md` (in the "For AI Agents" section):
>
> ```markdown
> ### Component Conventions
>
> - Export components as named exports, not default
> - Props interfaces must be exported and named `{ComponentName}Props`
> - Use `forwardRef` for all interactive components
> ```
>
> **Delete** `.cursor/rules/react-patterns.mdc`, `.claude/rules/react-patterns.md` and `.github/instructions/react-patterns.instructions.md`.
>
> **Why:** The glob matches the same scope as `packages/ui/AGENTS.md`. Moving the content there makes it portable across all three targets and eliminates the host-specific instruction files.

### [P2] Consider migrating an apply-intelligently instruction to a skill

> `.cursor/rules/code-review.mdc` uses "Apply Intelligently" (has `description`, no `globs`). The Claude Code equivalent (`.claude/rules/code-review.md`) and GitHub Copilot equivalent (`.github/instructions/code-review.instructions.md`) carry 150+ lines of procedural checklists that would benefit from skill organisation.
>
> **Option A (Cursor only):** Use Cursor's built-in migration: type `/migrate-to-skills` in Agent chat.
>
> **Option B:** Manual migration — **Create** `.apm/skills/code-review/SKILL.md`:
>
> ```yaml
> ---
> name: code-review
> description: Code review checklist and best practices. Use when reviewing PRs or performing code review.
> ---
> [original instruction body content, preserved exactly]
> ```
>
> **Delete** `.cursor/rules/code-review.mdc`, `.claude/rules/code-review.md` and `.github/instructions/code-review.instructions.md`.
>
> **Why:** Skills provide better organisation for procedural content via `references/` subdirectories and progressive disclosure, and deploy to all three hosts. Apply-intelligently instructions still work but lack this structure.

### [P2] Consider migrating a host command to a skill

> `.cursor/commands/deploy.md` is a slash command that could be converted to a skill. `.claude/commands/deploy.md` and `.github/prompts/deploy.prompt.md` are the Claude Code and GitHub Copilot equivalents.
>
> **Option A (Cursor only):** Use Cursor's built-in migration: type `/migrate-to-skills` in Agent chat.
>
> **Option B:** Manual migration — **Create** `.apm/skills/deploy/SKILL.md`:
>
> ```yaml
> ---
> name: deploy
> description: Deploy the application to staging or production environments
> disable-model-invocation: true
> ---
> [original command content, preserved exactly]
> ```
>
> **Delete** `.cursor/commands/deploy.md`, `.claude/commands/deploy.md` and `.github/prompts/deploy.prompt.md`.
>
> **Why:** Skills with `disable-model-invocation: true` provide the same user-invoked behaviour (`/deploy`) with better organisation via `references/` subdirectories, and deploy to all three hosts. Commands still work but lack this structure.

### [P1] Add indexing exclusions for non-code content

> The `data/legal-documents/` directory contains 2,847 markdown files (MPEP chapters, case law) totalling 45MB. These pollute the semantic index and dominate search results.
>
> **Add to** `.cursorindexingignore`:
>
> ```
> # Legal reference documents (not source code)
> data/legal-documents/
> ```
>
> **Why:** Removes non-code content from Cursor's semantic index, improving search relevance without making the files inaccessible (they can still be manually added via `@file`). Cursor is the only target with a committed index-exclusion file; Claude Code and GitHub Copilot filter through host and editor settings, so for those targets confirm the directory is covered by `.gitignore` or their content-exclusion settings.

### [P2] Add an environment activation hook

> The project uses a conda environment (`.conda/` directory exists) but has no hook to activate it before shell commands. This causes environment mismatch errors.
>
> **Cursor — create** `.cursor/hooks.json`:
>
> ```json
> {
>   "version": 1,
>   "hooks": {
>     "sessionStart": [
>       {
>         "command": ".cursor/hooks/session-init.sh"
>       }
>     ]
>   }
> }
> ```
>
> **Cursor — create** `.cursor/hooks/session-init.sh`:
>
> ```bash
> #!/bin/bash
> # Read JSON input from stdin
> cat > /dev/null
> # Output env vars for the session
> echo '{"env": {"CONDA_DEFAULT_ENV": "myenv"}}'
> ```
>
> **Claude Code — add** the equivalent hook to `.claude/settings.json`:
>
> ```json
> {
>   "hooks": {
>     "SessionStart": [
>       {
>         "hooks": [
>           {
>             "type": "command",
>             "command": ".claude/hooks/session-init.sh"
>           }
>         ]
>       }
>     ]
>   }
> }
> ```
>
> **Why:** Ensures shell commands run in the correct environment, preventing "module not found" errors. GitHub Copilot has no committed hook configuration, so on that target the activation must be handled in the project's own scripts or setup instructions.
