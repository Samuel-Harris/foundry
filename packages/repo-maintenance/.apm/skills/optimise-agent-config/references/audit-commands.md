# Audit Commands Reference

Bash commands for each audit area. Run these from the repository root to gather information about the repository's agent configuration across the active targets: **Cursor**, **Claude Code** and **GitHub Copilot**.

Where a command is host-specific, the pattern is repeated per host. The portable source of truth is the APM primitives, which deploy to every target:

- skills: `.apm/skills/<name>/SKILL.md` → `.cursor/skills/`, `.claude/skills/` and the shared `.agents/skills/`
- agents: `.apm/agents/<name>.agent.md` → `.cursor/agents/`, `.claude/agents/`, `.github/agents/`
- instructions: `.apm/instructions/<name>.instructions.md` → `.cursor/rules/`, `.claude/rules/`, `.github/instructions/`

## Host Path Reference

| Concern                                         | Cursor                            | Claude Code                                | GitHub Copilot                                      |
| ----------------------------------------------- | --------------------------------- | ------------------------------------------ | --------------------------------------------------- |
| Repository entry document                       | `AGENTS.md`                       | `CLAUDE.md` (bridged to `AGENTS.md`)       | `AGENTS.md` and `.github/copilot-instructions.md`   |
| Instructions                                    | `.cursor/rules/*.mdc`             | `.claude/rules/*.md`                       | `.github/instructions/*.instructions.md`            |
| Agents (subagents)                              | `.cursor/agents/*.md`             | `.claude/agents/*.md`                      | `.github/agents/*.md`                               |
| Skills                                          | `.cursor/skills/*/SKILL.md`       | `.claude/skills/*/SKILL.md`                | `.agents/skills/*/SKILL.md` (shared deployment)     |
| Commands (legacy)                               | `.cursor/commands/*.md`           | `.claude/commands/*.md`                    | `.github/prompts/*.prompt.md`                       |
| Hooks                                           | `.cursor/hooks.json`              | `.claude/settings.json`                    | not supported                                       |
| MCP configuration                               | `.cursor/mcp.json`                | `.mcp.json` and `.claude/settings.json`    | `.vscode/mcp.json`                                  |
| Blocklist (files invisible to the agent)        | `.cursorignore`                   | `.claudeignore`                            | repository and editor settings                      |
| Index exclusion (indexed-out, still readable)   | `.cursorindexingignore`           | none — Claude Code uses host settings      | none — GitHub Copilot uses host settings            |

## 1. Indexing Exclusions

```bash
# Read existing blocklist files — one per host where the host supports one
cat .cursorignore 2>/dev/null         # Cursor
cat .claudeignore 2>/dev/null         # Claude Code
# GitHub Copilot has no committed ignore file; it filters via repository and editor settings

# Read the index-exclusion file (files stay readable, but leave the semantic index).
# Cursor is the only target with such a committed file; Claude Code and GitHub
# Copilot exclude content through host and editor settings instead.
cat .cursorindexingignore 2>/dev/null

# Check .gitattributes for LFS-tracked paths (these are often binary)
grep "filter=lfs" .gitattributes 2>/dev/null

# Find large non-code directories that might pollute the index
du -sh */ 2>/dev/null | sort -rh | head -20

# Count files in suspect directories
find <directory> -type f | wc -l

# Check for generated code directories
find . -name "gen" -o -name "generated" -o -name "__generated__" | head -20
```

## 2. Instruction Configuration

```bash
# List instructions for every host
ls -la .cursor/rules/ 2>/dev/null          # Cursor (*.mdc)
ls -la .claude/rules/ 2>/dev/null          # Claude Code (*.md)
ls -la .github/instructions/ 2>/dev/null   # GitHub Copilot (*.instructions.md)
ls -la .github/copilot-instructions.md 2>/dev/null

# Check for legacy single-file Cursor rules
ls -la .cursorrules 2>/dev/null

# Read each instruction to assess scope and size
wc -l .cursor/rules/* .claude/rules/* .github/instructions/* 2>/dev/null

# Find always-applied instructions (Cursor flags these explicitly)
grep -l "alwaysApply: true" .cursor/rules/* 2>/dev/null

# Find apply-intelligently instructions (description present, no file-pattern scope).
# These are candidates for skill migration when the content is procedural.
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
```

## 3. Repository Documentation (AGENTS.md and CLAUDE.md)

```bash
# Find all portable documents across hosts
find . \( -name "AGENTS.md" -o -name "CLAUDE.md" \) -type f -not -path "*/node_modules/*" | sort

# Check root document size (large = candidate for trimming)
wc -l AGENTS.md CLAUDE.md 2>/dev/null

# Check the Copilot fallback instruction file
wc -l .github/copilot-instructions.md 2>/dev/null

# Check timestamps
grep "Updated:" */AGENTS.md 2>/dev/null
```

## 4. Context Weight

```bash
# Measure the always-on documents
wc -l AGENTS.md CLAUDE.md 2>/dev/null

# Find all always-applied instructions (Cursor flags these explicitly)
grep -l "alwaysApply: true" .cursor/rules/* 2>/dev/null

# Total context weight per host
wc -l AGENTS.md CLAUDE.md .cursor/rules/* .claude/rules/* .github/instructions/* 2>/dev/null
```

## 5. Hooks

```bash
# Read existing hooks
cat .cursor/hooks.json 2>/dev/null        # Cursor
cat .claude/settings.json 2>/dev/null     # Claude Code (hooks live under settings)
# GitHub Copilot has no committed hook configuration

# List hook scripts
ls .cursor/hooks/ 2>/dev/null
ls .claude/hooks/ 2>/dev/null

# Check for virtual environment indicators
ls .conda/ .venv/ venv/ .python-version .nvmrc .node-version 2>/dev/null
```

## 6. Generated and Binary Files

```bash
# Check for LFS paths
grep "filter=lfs" .gitattributes 2>/dev/null

# Look for generated code markers
grep -r "auto-generated\|DO NOT EDIT\|generated by" --include="*.ts" --include="*.py" -l . 2>/dev/null | head -20

# Find large non-code files
find . -type f \( -name "*.sql" -o -name "*.pkl" -o -name "*.dat" -o -name "*.bin" -o -name "*.pdf" -o -name "*.png" -o -name "*.jpg" -o -name "*.webm" -o -name "*.zip" -o -name "*.tar.gz" \) -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null | head -30
```

## 7. Codebase Indexing Settings

Indexing is configured in each host's UI or settings, not in a committed file:

- Cursor: Settings > Features — Codebase Indexing enabled, Include Project Structure enabled, indexing fully complete
- Claude Code: no separate semantic index; confirm the host honours the project's ignore rules
- GitHub Copilot: indexing and content exclusion are configured in repository and editor settings

## 8. Skills

```bash
# List existing skills for every host (APM deploys shared skills to .agents/skills/)
ls -R .agents/skills/ .cursor/skills/ .claude/skills/ 2>/dev/null

# Check skill descriptions and sizes
for skill in .agents/skills/*/SKILL.md .cursor/skills/*/SKILL.md .claude/skills/*/SKILL.md; do
  [ -f "$skill" ] || continue
  echo "=== $skill ==="
  head -5 "$skill"
  wc -l "$skill"
done
```

## 9. Artefact Validation

**IMPORTANT:** Don't just check existence — read each file to verify its frontmatter against the APM primitive contract.

Use the validation script (it lives beside this skill's `SKILL.md`):

```bash
# Run from the project root; pass a path to validate a different repository root
./scripts/validate-artefacts.sh [repository-root]
```

The script validates the APM primitives and their frontmatter contracts:

- **Skills** — `name` and `description` required; `name` must match the directory name, use lowercase letters, digits and single hyphens, and be 64 characters or fewer; `description` may not exceed 1024 characters
- **Agents** — `description` required so the host can auto-delegate
- **Instructions** — `description` and a file-pattern scope required; the scope is `applyTo` in APM (`.apm/instructions/`) and on GitHub Copilot (`.github/instructions/`), `globs` on Cursor (`.cursor/rules/`), and `paths` on Claude Code (`.claude/rules/`)

It scans the APM sources (`.apm/`), the shared skill deployment (`.agents/skills/`) and the deployed host directories (`.cursor/`, `.claude/`, `.github/`), and exits non-zero when any required field is missing.

## 10. Commands (Legacy)

```bash
# List existing commands per host (skills with disable-model-invocation are preferred)
ls .cursor/commands/ 2>/dev/null    # Cursor
ls .claude/commands/ 2>/dev/null    # Claude Code
ls .github/prompts/ 2>/dev/null     # GitHub Copilot prompt files
```

## 11. Subagents

```bash
# List existing subagents for every host
ls .cursor/agents/ 2>/dev/null
ls .claude/agents/ 2>/dev/null
ls .github/agents/ 2>/dev/null

# Check subagent frontmatter and descriptions
for agent in .cursor/agents/*.md .claude/agents/*.md .github/agents/*.md; do
  [ -f "$agent" ] || continue
  echo "=== $agent ==="
  head -10 "$agent"
done
```

## 12. MCP Server Configuration

```bash
# Read existing MCP config per host
cat .cursor/mcp.json 2>/dev/null     # Cursor
cat .mcp.json 2>/dev/null            # Claude Code (project scope)
cat .vscode/mcp.json 2>/dev/null     # GitHub Copilot (VS Code)
cat mcp.json 2>/dev/null

# Identify project services from docker-compose, requirements, etc.
grep -l "postgres\|redis\|mysql\|mongo" docker-compose*.yml 2>/dev/null
grep -i "linear\|jira\|github\|stripe" requirements.txt 2>/dev/null
```

## 13. Plugins and Packages

```bash
# Host plugin directories (where the host supports them)
ls .cursor/plugins/ 2>/dev/null

# APM primitives declared in this package, which deploy to every target
find . -path "*/.apm/skills/*/SKILL.md" -o -path "*/.apm/agents/*" -o -path "*/.apm/instructions/*" 2>/dev/null | sort
```

## 14. Sandbox

```bash
cat sandbox.json 2>/dev/null           # repository-provided sandbox config
cat .cursor/settings.json 2>/dev/null  # Cursor sandbox and permission settings
cat .claude/settings.json 2>/dev/null  # Claude Code permissions and sandbox settings
# GitHub Copilot has no committed sandbox configuration
```

## 15. Content Placement Analysis

```bash
# All portable documents
find . \( -name "AGENTS.md" -o -name "CLAUDE.md" \) -type f -not -path "*/node_modules/*" | sort

# All instructions for every host
ls .cursor/rules/ .claude/rules/ .github/instructions/ 2>/dev/null

# All skills, including their references/ and scripts/ subdirectories
find .apm/skills .agents/skills .cursor/skills .claude/skills -type f -name "SKILL.md" 2>/dev/null | sort
```
