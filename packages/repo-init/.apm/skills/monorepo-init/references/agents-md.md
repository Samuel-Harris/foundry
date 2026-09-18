# AGENTS.md rules and templates

## Why minimal

- ETH Zurich and LogicStar.ai (arXiv:2602.11988) found repository context files did not generally improve task success and added over 20% inference cost on average; LLM-generated files slightly reduced success, while developer-written files helped only marginally (~4%), mainly where no other documentation existed. Mechanism: context files push agents into broader exploration. Their conclusion: context files should describe only minimal requirements.
- A factorial adherence study (arXiv:2605.10039, 1,650 Claude Code sessions) found no detectable compliance effect from file size, instruction position, or single-versus-multiple instruction files within tested ranges. The robust effect was within-session compliance decay (~5.6% lower odds per additional function generated).
- Practitioner-scale observation: agents reliably discover AGENTS.md (~100% of the time) and follow relevant references from it (>90% when relevant); directory READMEs are read ~80% of the time when working in that directory.

Do not rely on AGENTS.md to hold structure. It points to executable checks and the change process; boundary tools enforce the structure, and the file never substitutes for enforcement.

## Generation rules

1. Keep every file minimal, high-signal, and hand-written. Every line must say something the agent cannot infer from code, manifests, or existing docs. Do not restate the README or facts obvious from code and manifests. Never auto-generate filler.
2. Lead with commands and boundaries, not architecture essays. Cut "architecture overview" prose; keep any component description boundary-focused ("what, not why").
3. Use imperative, verifiable instructions ("all functions must have explicit return types" beats "write clean code"). Back style rules with a linter; an unenforced prose rule is unreliable.
4. Separate boundaries into Always, Ask first, and Never. The Never list is consistently the highest-value section.
5. Keep the root file to the repository map, global conventions, and commands. Add one short file per top-level package. Split files near 150–200 lines. The closest file to the edited file wins; explicit prompts override everything.
6. Point to `just boundaries` and `just check` rather than duplicating their flags and rules.

Use AGENTS.md as the single shared source of truth. Add host-specific rule files (for example `.cursor/rules/*.mdc` for Cursor) only for guidance that cannot be expressed portably; never duplicate AGENTS.md content there.

## Tool bridging

Maintain AGENTS.md as the single source of truth. Never maintain duplicate instruction files — they drift.

- **Claude Code** reads `CLAUDE.md`, not AGENTS.md natively: bridge with a thin `CLAUDE.md` containing exactly `@AGENTS.md` (portable and Windows-safe) or a symlink (`ln -s AGENTS.md CLAUDE.md`).
- **Cursor** reads AGENTS.md natively, plus any project-specific rules under `.cursor/rules/`.
- **GitHub Copilot** reads AGENTS.md natively.
- **Codex** reads AGENTS.md natively with a 32 KiB per-file cap (it silently truncates — another reason to stay small).

## Root template

Adapt every name, command, and rule to the confirmed scaffold:

```markdown
# <Repo name> — Agent Guide

## What this repo is

<One or two sentences naming the stack and deployables, e.g. Python 3.13 / FastAPI / uv workspace; React/Vite frontend.>

## Repo map (where code lives)

- `services/*` — deployable services. MAY import `libs/*`. MUST NOT import each other.
- `libs/*` — shared libraries, layered contracts < platform. Lower never imports higher.
- `infra/` — infrastructure code (IaC). NEVER imported by application code. Ask before editing.
- `tools/`, `docs/` — repository tooling and documentation.

## Commands

- Install: `uv sync --all-packages`
- Test: `just test` (single package: `uv run --package <pkg> pytest <path>`)
- Lint: `just lint`
- Types: `just typecheck`
- Boundaries: `just boundaries` (tach check-external · lint-imports)
- All checks: `just check` (run before every commit)

## Conventions

- Use src layout everywhere and colocate tests in each package's `tests/`.
- Put new shared code in the lowest library layer that satisfies its dependencies.
- Inter-package dependencies require both a `dependencies` entry and a matching workspace source (`[tool.uv.sources] x = { workspace = true }`).

## Boundaries

- Always: run `just check` before committing; register every new package with the boundary tools (add or adjust its `tach.toml` entry).
- Ask first: change boundary layers, add a top-level directory, or edit `infra/`.
- Never: import one service from another; add an undeclared dependency; edit generated code.

## Changing the structure

The layout is intentional but mutable. To add, split, or change a module or contract, follow `docs/STRUCTURE.md` (update `tach.toml`/tags, run `tach sync`, update this file).
```

## Per-package template

Keep package files to roughly 5–8 lines:

```markdown
# libs/platform — Agent Guide

Purpose: logging, configuration, and tracing.
Layer: platform; may import contracts; must not import services or apps.
Public interface: only `platformlib.api` is importable by other packages (enforced by an Import Linter protected contract).
Commands: `uv run --package platform-lib pytest libs/platform` · `uv run --package platform-lib pyright libs/platform`
Conventions: pure functions; no service-specific logic; configuration via pydantic-settings.
Never: import from `services/*`; add I/O beyond logging sinks.
```

## Staleness checks (keep instruction files docs-as-code)

Every structure change updates the affected AGENTS.md files in the same change. Add a lightweight CI staleness check, for example a script asserting:

- every top-level package contains AGENTS.md;
- every command named in the root AGENTS.md exists in the task runner (`justfile`);
- boundary configuration matches the package tree where the installed tool supports a check mode (`tach sync --check`-style verification).

Wire the staleness check into `just check` or CI so drift fails visibly.
