# Audit Process

Detailed steps for running the audit, either in parallel with subagents or sequentially. The audit covers every active target: **Cursor**, **Claude Code** and **GitHub Copilot**.

The APM primitives are the portable source of truth. Read them first, then the deployed copies per host:

- skills: `.apm/skills/<name>/SKILL.md` → `.cursor/skills/`, `.claude/skills/`, `.agents/skills/`
- agents: `.apm/agents/<name>.agent.md` → `.cursor/agents/`, `.claude/agents/`, `.github/agents/`
- instructions: `.apm/instructions/<name>.instructions.md` → `.cursor/rules/`, `.claude/rules/`, `.github/instructions/`

## Parallel Audit (Preferred)

If the environment supports subagents, parallelise the audit for speed:

### Subagent 1: Configuration Audit

- Read all config files (`.cursorignore`, `.claudeignore`, `.cursorindexingignore`, `.gitignore`, `.gitattributes`, `.cursorrules`, `.cursor/hooks.json`, `.claude/settings.json`, `.cursor/mcp.json`, `.mcp.json`, `.vscode/mcp.json`, `sandbox.json`)
- List the deployed target directories: `.cursor/` (rules, commands, skills, agents, plugins), `.claude/` (rules, commands, skills, agents), `.github/` (instructions, agents, prompts)
- Identify legacy artefacts: apply-intelligently instructions per host (consider skill migration if procedural), commands (can migrate to skills)
- Assess ignore and index-exclusion file coverage per host

### Subagent 2: Index Pollution Scan

- Run `du`/`find` commands for large directories
- Check for generated code, binary files, LFS paths
- Identify non-code content in the repo

### Subagent 3: Context Weight Analysis

- Measure `AGENTS.md` and `CLAUDE.md` sizes and find all `AGENTS.md` files
- Analyse instruction scoping and activation modes for every host
- Calculate total always-on context weight

### Subagent 4: Documentation Currency Check

- Fetch the current documentation and changelog for each active target:
  - Cursor: <https://docs.cursor.com> and <https://cursor.com/changelog>
  - Claude Code: <https://docs.claude.com/en/docs/claude-code/overview> and <https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md>
  - GitHub Copilot: <https://docs.github.com/en/copilot>
- Compare repo configuration against the latest available features
- Identify missing configurations for new features

### Subagent 5: Content Placement Analysis

- Read **all** `AGENTS.md` files and any `CLAUDE.md`
- Read all instructions under every host directory: `.cursor/rules/`, `.claude/rules/`, `.github/instructions/`
- Read all skills: `SKILL.md` files **and** their subdirectory contents (e.g., `references/*.md`, `scripts/*`)
- Apply the Decision Tree from SKILL.md to each section >10 lines
- Flag content that should be in a different artefact type

For large repos, split into multiple subagents by directory.

Synthesise all subagent findings into the final report.

---

## Sequential Audit (Fallback)

If subagents are not available, run these steps in order:

### Step 1: Read configuration files

Read all of these (skip any that do not exist):

- `.cursorignore` (Cursor blocklist)
- `.claudeignore` (Claude Code blocklist)
- `.cursorindexingignore` (Cursor index exclusion; Claude Code and GitHub Copilot rely on host settings instead)
- `.gitignore`
- `.gitattributes`
- `.cursorrules`
- `.cursor/hooks.json` / `.claude/settings.json` (host hooks)
- `.cursor/mcp.json` / `.mcp.json` / `.vscode/mcp.json` (host MCP configuration)
- `sandbox.json`
- Root `AGENTS.md` and `CLAUDE.md`

### Step 2: List host configuration

```bash
# Cursor
ls .cursor/rules/ 2>/dev/null
ls .cursor/commands/ 2>/dev/null    # Deprecated — flag for migration to skills
ls .cursor/skills/ 2>/dev/null
ls .cursor/agents/ 2>/dev/null
ls .cursor/hooks/ 2>/dev/null
ls .cursor/plugins/ 2>/dev/null

# Claude Code
ls .claude/rules/ 2>/dev/null
ls .claude/commands/ 2>/dev/null
ls .claude/skills/ 2>/dev/null
ls .claude/agents/ 2>/dev/null

# GitHub Copilot
ls .github/instructions/ 2>/dev/null
ls .github/agents/ 2>/dev/null
ls .github/prompts/ 2>/dev/null    # Deprecated — flag for migration to skills

# Shared skill deployment
ls .agents/skills/ 2>/dev/null
```

### Step 3: Map portable document coverage

```bash
find . \( -name "AGENTS.md" -o -name "CLAUDE.md" \) -type f -not -path "*/node_modules/*" -not -path "*/.git/*" | sort
```

### Step 4: Identify index pollution candidates

```bash
# Large directories
du -sh */ 2>/dev/null | sort -rh | head -20

# LFS paths
grep "filter=lfs" .gitattributes 2>/dev/null

# Generated code
grep -r "auto-generated\|DO NOT EDIT" --include="*.ts" --include="*.py" -l . 2>/dev/null | head -20

# Non-code file counts in suspect directories
find . -type f -name "*.md" -not -path "*/node_modules/*" -not -path "*/.git/*" | wc -l
```

### Step 5: Assess context weight

```bash
wc -l AGENTS.md CLAUDE.md 2>/dev/null
wc -l .cursor/rules/* .claude/rules/* .github/instructions/* 2>/dev/null
grep -l "alwaysApply: true" .cursor/rules/* 2>/dev/null
```

### Step 6: Assess skills, commands, and subagents

```bash
# Skills: check structure and descriptions across the shared and host deployments
ls -R .agents/skills/ .cursor/skills/ .claude/skills/ 2>/dev/null
for skill in .agents/skills/*/SKILL.md .cursor/skills/*/SKILL.md .claude/skills/*/SKILL.md; do
  [ -f "$skill" ] || continue
  echo "=== $skill ==="
  head -5 "$skill"
  wc -l "$skill"
done

# Commands per host (can be migrated to skills)
ls .cursor/commands/ 2>/dev/null
ls .claude/commands/ 2>/dev/null
ls .github/prompts/ 2>/dev/null

# Apply-intelligently instructions (consider migrating to skills if procedural)
for file in .cursor/rules/*.mdc; do
  if grep -q "^description:" "$file" && ! grep -q "^globs:" "$file" && ! grep -q "alwaysApply: true" "$file"; then
    echo "Apply-intelligently rule: $file"
  fi
done 2>/dev/null

for file in .claude/rules/*.md .github/instructions/*.instructions.md; do
  if grep -q "^description:" "$file" && ! grep -q "^paths:\|^applyTo:\|^globs:" "$file"; then
    echo "Apply-intelligently instruction: $file"
  fi
done 2>/dev/null

# Subagents: check existence and configuration for every host
for agent in .cursor/agents/*.md .claude/agents/*.md .github/agents/*.md; do
  [ -f "$agent" ] || continue
  echo "=== $agent ==="
  head -10 "$agent"
done
```

### Step 7: Content Placement Analysis

Read **all** `AGENTS.md` files, any `CLAUDE.md`, all instructions, and all skills (including skill subdirectories like `references/`). For each section >10 lines, apply the Decision Tree:

1. **AGENTS.md**: Is it project identity/structure, or should it be an instruction/skill?
2. **Instructions**: Is it guidance ("how to behave") or procedures ("how to do")?
3. **Skills**: Is it procedural, or passive guidance that should be a portable document?

Flag any content that should move between artefact types.

### Step 8: Assess MCP and plugins

```bash
cat .cursor/mcp.json 2>/dev/null
cat .mcp.json 2>/dev/null
cat .vscode/mcp.json 2>/dev/null
cat mcp.json 2>/dev/null
ls .cursor/plugins/ 2>/dev/null
cat sandbox.json 2>/dev/null
```

### Step 9: Check host documentation

Consult the current documentation and changelog for each active target for any new features, settings, or configuration options not covered in this skill:

- Cursor: <https://docs.cursor.com> and <https://cursor.com/changelog>
- Claude Code: <https://docs.claude.com/en/docs/claude-code/overview> and <https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md>
- GitHub Copilot: <https://docs.github.com/en/copilot>

Include relevant new findings in your recommendations.
