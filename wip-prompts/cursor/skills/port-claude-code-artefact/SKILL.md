---
name: port-claude-code-artefact
description: Convert a Claude Code (oh-my-claudecode) agent or skill into a Cursor-native artefact. Use when porting agents, skills, or workflows from Claude Code to Cursor.
---

# Port Claude Code Artefact to Cursor

Convert an oh-my-claudecode agent (`.md`) or skill (`SKILL.md`) into a Cursor-native equivalent.

## Instructions

### Step 1: Identify the artefact type

Read the source file. Determine whether it is:

- **Agent** — has frontmatter with `name:`, `model:`, `tools:` → output goes to `.cursor/agents/personal/<name>.md`
- **Skill** — has `SKILL.md` name or `disable-model-invocation: true` → output goes to `.cursor/skills/personal/<name>/SKILL.md`

### Step 2: Read the reference format

Read an existing Cursor agent for format reference:

```
.cursor/agents/review-backend.md
```

Valid Cursor agent frontmatter fields: `name`, `description`, `model`, `readonly`, `is_background`. Nothing else.

### Step 3: Check for redundancy

Before creating the artefact, list existing agents and skills:

```bash
ls .cursor/agents/ .cursor/agents/personal/
ls .cursor/skills/ .cursor/skills/personal/
```

If an existing agent already covers the same purpose with project-specific knowledge (e.g., existing `review-backend` vs a generic `code-reviewer`), **skip the artefact** and report why.

### Step 4: Translate the artefact

Apply ALL of the following rules.

#### Frontmatter Translation

| Claude Code field | Cursor equivalent                                             |
| ----------------- | ------------------------------------------------------------- |
| `name:`           | Keep as-is                                                    |
| `description:`    | Expand — see "Description enrichment" below                   |
| `model: haiku`    | `model: fast`                                                 |
| `model: sonnet`   | Remove (inherits from parent)                                 |
| `model: opus`     | Remove (inherits from parent)                                 |
| `tools:`          | Remove entirely (Cursor agents inherit all tools from parent) |
| `argument-hint:`  | Remove entirely (not a valid Cursor field)                    |
| Read-only agents  | Add `readonly: true`                                          |

#### Description Enrichment

The `description:` field is the ONLY thing an agent sees when deciding whether to read a skill. Summarise the "When to use" and "When NOT to use" signals into the description, then **remove those sections from the body**. Once an agent has read the skill, it already intends to use it — repeating trigger/exclusion criteria inside the body wastes tokens.

#### Template Variable Removal

Remove `{{ARGUMENTS}}` and similar template placeholders. Cursor skills receive context from the conversation, not from positional arguments.

#### Tool Name Replacements

| Claude Code       | Cursor                       |
| ----------------- | ---------------------------- |
| `Edit` tool       | `StrReplace` tool            |
| `Bash` tool       | `Shell` tool                 |
| `lsp_diagnostics` | `ReadLints`                  |
| `ast_grep_search` | `Grep` (with regex patterns) |
| `AskUserQuestion` | `AskQuestion`                |

#### Path Replacements

| Claude Code path | Cursor equivalent                                      |
| ---------------- | ------------------------------------------------------ |
| `.omc/state/`    | Not applicable — use `TodoWrite` for progress tracking |
| `.omc/specs/`    | `.cursor/plans/`                                       |
| `.omc/plans/`    | `.cursor/plans/`                                       |
| `.omc/notepads/` | Not applicable — remove entirely                       |

#### Skill/Workflow Reference Replacements

When a skill references other Claude Code skills or execution modes, map them to existing Cursor equivalents:

| Claude Code reference                 | Cursor equivalent                      |
| ------------------------------------- | -------------------------------------- |
| `Skill("oh-my-claudecode:autopilot")` | Read and invoke `cursor-swarm` skill   |
| `Skill("oh-my-claudecode:omc-plan")`  | Read and invoke `cursor-ralplan` skill |
| `Skill("oh-my-claudecode:ralph")`     | Read and invoke `cursor-swarm` skill   |
| `Skill("oh-my-claudecode:team")`      | Read and invoke `cursor-swarm` skill   |
| `Skill("oh-my-claudecode:explore")`   | Task with `subagent_type: "explore"`   |

If a skill offers multiple execution bridge options that all map to the same Cursor skill, consolidate them into fewer options.

#### Concept Removal — delete entirely

- `state_write` / `state_read` — use `TodoWrite` for progress tracking instead
- `wrapWithPreamble()` / Worker Preamble Protocol — replace with inline: "Execute directly. NEVER delegate via Task tool."
- `oh-my-claudecode:agent-name` references — use just `agent-name`
- `run_in_background: true` — not applicable in Cursor
- `<Inherits_From>` blocks — Cursor has no agent inheritance
- `TaskOutput`, `background_output`, `omc_task`, `python_repl` — Claude Code-specific concepts
- Branding names (Sisyphus-Junior, Oracle, etc.) — use plain descriptive roles
- TypeScript API references (`import { ... } from './swarm'`) — not applicable
- `.claude/settings.json` configuration blocks — not applicable in Cursor

#### Inheritance Flattening

Claude Code agents use `<Inherits_From>` for tier variants. Cursor has no inheritance — every agent file must be **self-contained**. Merge the essential base instructions into each variant so it works standalone.

#### Build Command Replacement

Replace generic build commands with project-specific ones:

| Generic            | Project-specific                                                  |
| ------------------ | ----------------------------------------------------------------- |
| `npx tsc --noEmit` | `pyright -p .` (backend)                                          |
| `npx eslint .`     | `pnpm lint` (frontend)                                            |
| `npm run build`    | `./.devtools/cli test frontend` or `./.devtools/cli test backend` |

#### Coordination Pattern Replacement (Skills)

| Claude Code pattern           | Cursor equivalent                                  |
| ----------------------------- | -------------------------------------------------- |
| SQLite database for state     | `TodoWrite` for progress tracking                  |
| Heartbeat protocol            | Not needed — agents run to completion              |
| Lease-based ownership         | Not needed — batch dispatch, no contention         |
| `run_in_background: true`     | Not applicable                                     |
| Max 5 concurrent agents       | Max 4 (Cursor's Task tool limit)                   |
| User specifies `N:agent-type` | Orchestrator determines count and type per subtask |
| Single agent type for all     | Different agent types can mix in one dispatch      |
| `/oh-my-claudecode:cancel`    | Not supported — agents run to completion           |

### Step 5: Apply conciseness targets

Cursor docs warn: "A 2,000-word prompt doesn't make a subagent smarter. It makes it slower and harder to maintain."

| Variant           | Target line count                           |
| ----------------- | ------------------------------------------- |
| Base agent        | 50–80 lines                                 |
| Low-tier variant  | 30–50 lines                                 |
| High-tier variant | 60–80 lines                                 |
| Skill             | No strict limit, but remove all boilerplate |

Cut verbose examples, redundant explanations, and TypeScript code samples that don't apply. Preserve the constraints that matter: no delegation, verification before done, minimal diffs, structured output.

### Step 6: Write and verify

1. Write the translated file to the target path
2. Re-read it and check:
   - [ ] No Claude Code-specific concepts remain
   - [ ] No `tools:` in frontmatter
   - [ ] `model:` is either `fast`, omitted, or a valid Cursor model ID
   - [ ] `readonly: true` is set for agents that should not modify files
   - [ ] All tool names use Cursor equivalents
   - [ ] File is self-contained (no inheritance references)
   - [ ] Build commands are project-specific
   - [ ] Within conciseness targets
   - [ ] `description:` includes summarised when-to-use/when-not-to-use signals
   - [ ] No "When to use" / "When NOT to use" sections remain in the body
3. Report what was created and any artefacts that were skipped due to redundancy
