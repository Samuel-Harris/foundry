---
name: optimise-agent-config
description: Audit a repository's agent configuration for the active targets (Cursor, Claude Code, GitHub Copilot) or evaluate whether a specific artefact (instruction, skill, subagent) is correctly placed. Use when optimising a repo for agentic development, improving indexing, adding or assessing instructions and skills, or deciding where information should live.
---

# Agent Config Optimisation

Audit a repository's agent configuration, indexing setup, instructions, hooks, documentation, and workflows. Produce a prioritised report of recommendations.

**Reference files in this skill:**

- `references/audit-commands.md` — Shell commands for each audit area
- `references/audit-process.md` — Parallel and sequential audit workflows
- `references/migration-examples.md` — Migration formats and example recommendations
- `scripts/validate-artefacts.sh` — Validate frontmatter for skills, agents, and instructions

## Important: Consult the Host Documentation

Each host evolves its own configuration format rapidly. Consult the current documentation for whichever targets the repository uses before recommending changes:

- Cursor: rules, skills, subagents and hooks under `.cursor/`
- Claude Code: rules, skills and subagents under `.claude/`, plus `CLAUDE.md`
- GitHub Copilot: instructions, agents and prompts under `.github/`, plus `AGENTS.md`

Where APM deploys the primitives, the APM documentation for the installed CLI version is the authority.

## Scope

This skill has two phases: **audit** then **implementation**. During the audit phase, do not make changes to the repository — present findings as a prioritised report. Implementation only happens after the user approves specific recommendations (see "After the Report").

For AGENTS.md creation and updates, refer to the **generate-agent-docs** skill.

---

## Verify Before Recommending

**CRITICAL:** Before including any recommendation in the report, verify that it is actually needed by reading the relevant files.

**Common verification failures:**

- Recommending a capability that already exists in a different form (e.g., a skill that orchestrates something you thought was missing)
- Suggesting migrations for artefacts that are already correctly configured
- Flagging files for indexing exclusion when they're already in the host's ignore file
- Proposing new workflows without checking if existing skills or instructions already implement them
- Marking instructions as "well configured" without checking whether their content duplicates existing AGENTS.md guidance

**For each potential recommendation:**

1. Read the relevant configuration files to confirm the gap exists
2. If recommending changes to skills, agents or instructions, read those files first
3. If suggesting new capabilities, check whether they already exist in a different form
4. Cross-reference with existing deployed artefacts under every active target directory to avoid redundant suggestions

**Example:** Before recommending "add MCP server for Linear", check if Linear integration already exists in the host's MCP configuration or an existing skill.

---

## Decision Tree: Where Should This Information Live?

**Multi-agent portability is paramount.** AGENTS.md files are supported by all major AI coding agents (Cursor, Claude Code, GitHub Copilot, and others), while host-specific instruction directories such as `.cursor/rules/` are tied to one host. This means:

- **Default to AGENTS.md** for directory-scoped guidance
- **Broad file-pattern scoping is an anti-pattern** — if an instruction's scope is `dir/**/*.py` or `dir/**/*.ts`, that content belongs in `dir/AGENTS.md`
- **Use host-specific instructions only when precise file-pattern scoping is required** — e.g., `**/*.test.ts`, `**/*.config.js`, `**/migrations/*.py`

If an instruction covers "most files in a directory", it should be in that directory's AGENTS.md instead.

```
Is this information needed on EVERY request, regardless of what files are being worked on?
├─ YES → Root AGENTS.md (keep total under ~100 lines)
│   └─ Won't fit? → Always-applied instruction (host-specific; use sparingly)
├─ NO → Is it specific to a subdirectory, package, or service?
│   ├─ YES → Is it procedural (multi-step "how to do X")?
│   │   ├─ YES → Skill scoped to that area
│   │   └─ NO → Does it need precise file-pattern scoping (e.g., only *.test.py)?
│   │       ├─ YES → Glob-scoped instruction (host-specific; prefer AGENTS.md when possible)
│   │       └─ NO → Subdirectory AGENTS.md (preferred; portable across agents)
│   └─ NO → Does the agent need to decide when it's relevant?
│       ├─ YES → Is it procedural (multi-step "how to do X")?
│       │   ├─ YES → Skill (SKILL.md)
│       │   └─ NO → Apply-intelligently instruction (description, no globs)
│       └─ NO → Is it triggered by an explicit user action?
│           ├─ YES → A user-invoked skill (disable-model-invocation: true)
│           └─ NO → Subagent (if it needs isolated context), otherwise a skill
```

### Artefact Type Reference

| Artefact                         | Nature                   | Loading                        | Best For                                                                    |
| -------------------------------- | ------------------------ | ------------------------------ | --------------------------------------------------------------------------- |
| AGENTS.md                        | Passive, always loaded   | Every request                  | **Preferred.** Identity, constraints, conventions (portable across agents)  |
| Always-applied instruction       | Passive, always loaded   | Every request                  | Universal style when root AGENTS.md is too large (host-specific; sparingly) |
| Glob-scoped instruction          | Passive, auto-attached   | When matching files in context | Precise file-pattern scoping AGENTS.md can't cover (host-specific)          |
| Skill                            | Active, agent-discovered | When task matches description  | Procedural workflows, domain expertise, multi-step "how-to"                 |
| Skill (disable-model-invocation) | Active, user-invoked     | Only when the user invokes it  | Saved prompts, repeatable workflows the user triggers explicitly            |
| Subagent                         | Active, delegated        | When parent agent delegates    | Tasks needing isolated context, parallel execution                          |

In APM terms these are the three primitives: **instructions** (`.apm/instructions/`), **skills** (`.apm/skills/`) and **agents** (`.apm/agents/`).

#### Legacy Artefact Types

| Artefact                        | Status          | Notes                                                                                                            |
| ------------------------------- | --------------- | ---------------------------------------------------------------------------------------------------------------- |
| Apply-intelligently instruction | Still supported | Consider migrating to a skill if it contains multi-step procedures or would benefit from `references/` structure |
| Host command                    | Still supported | Skills with `disable-model-invocation: true` are the newer alternative                                           |

**The acid test:** Default to AGENTS.md for directory-scoped guidance (portable across agents). Use a host-specific instruction only when precise file-pattern scoping is needed. If it tells the agent _how to do something_, it's a skill. If it's a prompt you're tired of retyping, it's a skill with `disable-model-invocation: true`. If it needs a clean context window, it's a subagent.

---

## Audit Checklist

For shell commands to run for each area, see `references/audit-commands.md`.

### 1. Indexing Exclusions

Check the host's ignore files alongside `.gitignore`. The key distinction:

- The host's blocklist file (e.g. `.cursorignore`, `.claudeignore`) — files invisible to the agent entirely
- The host's index-exclusion file (e.g. `.cursorindexingignore`) — files excluded from the semantic index but still readable

**Flag for exclusion:** Large reference docs, scraped data, database snapshots, generated code, binary content, build artefacts, vendored dependencies.

**Exclude deployed agent-config directories from indexing.** Rules, hooks, subagents, and skill reference docs are loaded by the host natively or read by the agent directly — none of them need to be in the semantic index. Add the deployed directories (`.cursor/`, `.claude/`, `.github/agents/`, `.agents/`) to the index-exclusion file.

### 2. Instruction Configuration

For each active target, check the deployed instruction files and their frontmatter.

| Mode                    | Frontmatter                                | Guidance                                                                    |
| ----------------------- | ------------------------------------------ | --------------------------------------------------------------------------- |
| Always applied          | `alwaysApply: true`                        | Use sparingly — loads on every request                                      |
| Apply to specific files | `alwaysApply: false` + `globs: <patterns>` | When precise file-pattern scoping is needed (host-specific)                 |
| Apply intelligently     | `description` only, no globs               | Agent decides based on description; consider a skill for procedural content |
| Apply manually          | No globs, no description                   | Only when explicitly referenced                                             |

**Anti-patterns:**

- God instructions (>500 lines)
- Procedural instructions (should be skills)
- Stale or conflicting instructions
- **Broad file-pattern scoping that covers most files in a directory** — this is a common anti-pattern. If an instruction's scope is `backend/**/*.py` or `frontend/**/*.ts`, that content belongs in `backend/AGENTS.md` or `frontend/AGENTS.md` respectively. Host-specific instructions are not portable; AGENTS.md is.
- Instructions duplicating content already in AGENTS.md — if the same constraints appear in both places, delete the instruction

**Sizing:** Individual instructions <500 lines, all always-applied instructions combined <200 lines.

### 3. AGENTS.md Documentation

**Bloated signs:** >100 lines at root, detailed command references, area-specific conventions, procedural instructions.

**Too thin signs:** No directory map, no tech stack, no build/test commands, no critical constraints.

### 4. Context Weight Optimisation

| Context type                       | Budget         |
| ---------------------------------- | -------------- |
| Root AGENTS.md                     | ~100 lines     |
| All always-applied instructions    | ~200 lines     |
| **Total always-on context**        | **<300 lines** |
| Individual glob-scoped instruction | ~200 lines max |
| Skill SKILL.md body                | ~500 lines max |

**Red flags:** Root AGENTS.md >200 lines, >3 always-applied instructions, a single instruction >500 lines.

### 5. Hooks

Check the host's hooks configuration (for example `.cursor/hooks.json`) for hook definitions. High-value hook patterns:

- Session start — inject branch name, ticket, or environment context
- Pre-execution — validate or transform shell commands
- Before shell execution — block dangerous commands
- After file edit — run formatters or linters after agent edits
- Stop — prompt handoff notes or auto-retry logic

### 6. Generated and Binary Files

Flag: Auto-generated types (OpenAPI/protobuf), compiled output, SQL dumps, LFS-tracked paths, large test fixtures.

### 7. Codebase Indexing Settings

UI-only settings to verify per host (for Cursor: Settings > Features — Codebase Indexing enabled, Include Project Structure enabled, indexing fully complete).

### 8. Skills

**Skills are the preferred format for:**

- Multi-step procedural workflows
- Domain-specific expertise that benefits from `references/` subdirectories
- User-invoked prompts (with `disable-model-invocation: true`)

**Check:** Do the active targets have deployed skills? Do skills use progressive disclosure (lean SKILL.md, heavy docs in `references/`)? Would any apply-intelligently instructions benefit from skill structure?

### 9. Artefact Validation

**IMPORTANT:** Read each artefact file to verify correct structure. Don't just check existence.

Run `scripts/validate-artefacts.sh` from the project root for automated validation of skill, agent and instruction frontmatter.

#### Skill Frontmatter (Required)

```yaml
---
name: skill-name
description: What this skill does and when to use it
---
```

The `name` must equal the directory name, use lowercase letters, digits and single hyphens, and be 64 characters or fewer. The `description` is limited to 1024 characters.

**Optional fields:**

- `disable-model-invocation: true` — For user-invoked-only skills (replacement for commands). Keep the key and put explicit trigger guidance in `description`, so manual-only intent survives on hosts that ignore the key.

**Common errors:**

- Missing frontmatter entirely (no `---` block)
- Missing `name` field, or a `name` that does not match the directory
- Missing `description` field (agent won't discover the skill)
- Empty or placeholder description

#### Agent Frontmatter

`description` is required. Useful optional fields:

```yaml
---
name: agent-name
description: What this agent does and when to use it
model: inherit
tools: [read, edit, search]
color: blue
handoffs: [other-agent]
---
```

Note that `readonly` is a Cursor-shaped extension. When present it is enforced natively only on Cursor; on other hosts the read-only intent must be stated in the agent body.

#### Instruction Frontmatter (Required)

| Field         | Required | Notes                                                        |
| ------------- | -------- | ------------------------------------------------------------ |
| `description` | Yes      | What the instruction does and when it applies                |
| `applyTo`     | Yes      | Glob pattern(s) the instruction applies to, e.g. `**/*.py`   |

`applyTo` maps to `globs` on Cursor, `paths` on Claude Code, and is passed through on Copilot.

**Common errors:**

- `applyTo` present but empty
- Both an always-apply flag and `applyTo` (redundant)
- Omitting `applyTo` when a per-file instruction is intended

### 10. Commands (Legacy)

Host commands still work, but skills with `disable-model-invocation: true` are the newer alternative. See `references/migration-examples.md` for the manual migration format, presented per host.

### 11. Subagents

Check the deployed agent directories (`.cursor/agents/`, `.claude/agents/`, `.github/agents/`) for focused, well-described agents. The `model` field is optional (`inherit` is the default).

High-value patterns: debugger, security auditor, test writer, documentation specialist, code reviewer.

### 12. MCP Server Configuration

Check the host's MCP configuration. Only suggest MCP servers for services the project actually uses (verify in the project manifest, lockfile or compose files).

### 13. Plugins and Packages

Agent configuration is distributed as packages. When the repository publishes or consumes packages, check the package manifests and per-package READMEs for drift between declared and deployed primitives.

### 14. Sandbox Configuration

Check any sandbox configuration for network and filesystem access controls.

### 15. Content Placement Analysis

Apply the **Decision Tree** (above) to evaluate whether content is correctly placed across AGENTS.md files, instructions, and skills.

**Reading requirements:**

- **All** AGENTS.md files in the repository
- All deployed instructions under every active target directory
- All skills: both `SKILL.md` and any files in subdirectories (e.g., `references/`, `scripts/`)

**Use subagents** to parallelise reading across major directories.

**Cross-reference instructions against AGENTS.md for duplication:**

For each glob-scoped instruction, read the AGENTS.md files in the directories covered by its pattern. If the instruction's constraints are already present in those AGENTS.md files, flag the instruction for deletion — the content already lives where it should. Do not mark duplicated instructions as "well configured".

**Migrate broad scopes to AGENTS.md:**

Glob-scoped instructions with patterns like `backend/**/*.py` are an anti-pattern — they cover essentially all code files in a directory, which is exactly what AGENTS.md is for. These should be migrated:

1. **If the content is NOT in AGENTS.md** — move the instruction's content into the appropriate subdirectory AGENTS.md, then delete the instruction
2. **If the content IS already in AGENTS.md** — delete the instruction (it's redundant)

This matters for multi-agent portability: AGENTS.md is supported by Cursor, Claude Code, GitHub Copilot and other agents. Host-specific instructions are not. Preferring AGENTS.md ensures the project's conventions work across all tools.

**For each section >10 lines, ask:**

1. Is this needed on every request? → If no, shouldn't be in root AGENTS.md or an always-applied instruction
2. Is this scoped to a directory? → Subdirectory AGENTS.md (preferred for portability)
3. Does it need precise file-pattern scoping? → Glob-scoped instruction (host-specific)
4. Is this procedural ("how to do X")? → Should be a skill

**Flag content that should move:**

| Current Location           | Content Type                                 | Should Be                                                            |
| -------------------------- | -------------------------------------------- | -------------------------------------------------------------------- |
| Root AGENTS.md             | Procedural instructions                      | Skill                                                                |
| Root AGENTS.md             | Area-specific conventions                    | Subdirectory AGENTS.md                                               |
| Always-applied instruction | Area-specific content                        | Subdirectory AGENTS.md                                               |
| Glob-scoped instruction    | Broad scope (`dir/**/*.py`, `dir/**/*.ts`)   | Subdirectory AGENTS.md (delete the instruction)                      |
| Glob-scoped instruction    | Duplicates content in directory's AGENTS.md  | Delete the instruction (content already exists)                      |
| Instruction                | Multi-step procedures                        | Skill                                                                |
| Skill                      | Passive guidance only                        | Subdirectory AGENTS.md (or an instruction if precise scoping needed) |

**When glob-scoped instructions ARE appropriate:**

Instructions are justified when you need precise file-pattern scoping that AGENTS.md cannot provide, such as:

- `**/*.test.ts` — test file conventions
- `**/*.config.{js,ts}` — configuration file patterns
- `**/migrations/*.py` — migration-specific rules
- `**/*.stories.tsx` — Storybook conventions

If the scope would match "most files in a directory", use AGENTS.md instead.

---

## Audit Process

See `references/audit-process.md` for detailed parallel and sequential audit workflows.

**Quick summary:**

1. Read config files (host ignore files, `.gitignore`, host hooks and MCP configuration, AGENTS.md, CLAUDE.md)
2. List the deployed target directories
3. Identify legacy artefacts that may benefit from migration (apply-intelligently instructions, commands)
4. Check for index pollution (large directories, generated code, binary files)
5. Measure context weight
6. Consult the host documentation for new features
7. **Content placement analysis** — apply the Decision Tree to all AGENTS.md files, instructions, and skills (including skill subdirectories)
8. **Verify each recommendation** — read relevant files to confirm gaps exist before including in the report

---

## Output Format

Present findings as a prioritised report:

```
## Agent Config Optimisation Report

### P0 — Critical (high impact, low effort)
[Recommendations that significantly improve indexing, search quality, or context efficiency]

### P1 — Important (high impact, moderate effort)
[Recommendations that improve developer experience or reduce repetitive work]

### P2 — Recommended (moderate impact)
[Recommendations that would improve the setup but are not urgent]

### P3 — Nice to Have (lower impact or beta features)
[Recommendations for newer or experimental features]

### Already Well Configured
[Areas that are already set up correctly — acknowledge good practices]

### Settings to Verify Manually
[UI-only settings the user should check in the host's settings]
```

For each recommendation, include:

- **What** to change
- **Why** it matters
- **Specific file contents or changes** to make

See `references/migration-examples.md` for example recommendations.

---

## After the Report

Once the prioritised report is complete:

1. **List every actionable recommendation** as a numbered summary (one line each, referencing the priority level, e.g. `[P0] Exclude generated/ from indexing`)

2. **Ask the user** which items they would like implemented:

   > Which of these would you like me to implement? You can specify by number (e.g. "1, 3, 5"), a priority level (e.g. "all P0 and P1"), or say "all".

3. **Wait for the user's response**, then implement only the selected items.
