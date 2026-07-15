# AGENTS.md: evidence-based rules and templates

## Why minimal (the evidence, briefly)

- ETH Zurich + LogicStar.ai (arXiv:2602.11988): repository context files did **not** generally improve task success and added >20% inference cost on average; LLM-generated files slightly reduced success; developer-written files helped only marginally (~4%), mainly where no other docs existed. Mechanism: context files push agents into broader exploration. Their conclusion: context files should describe only minimal requirements.
- Factorial adherence study (arXiv:2605.10039, 1,650 Claude Code sessions): file size, instruction position, and single-vs-multi-file architecture had **no detectable effect** on compliance within tested ranges; the one robust effect was **within-session decay** (~5.6% lower odds per additional function generated).
- Practitioner-scale observation: AGENTS.md is auto-discovered ~100% of the time; references out of it are followed >90% when relevant; directory READMEs are read ~80% when working in that directory.

Consequence: **do not rely on the file to hold structure — rely on the boundary tools.** The AGENTS.md points at executable checks and documents the change process; it never substitutes for enforcement.

## The six generation rules

1. **Minimal, high-signal, hand-written.** Every line must say something the agent cannot infer from code, manifests, or existing docs. Never restate the README. Never auto-generate filler.
2. **Lead with commands and boundaries, not architecture prose.** Cut "architecture overview" essays; keep any component description boundary-focused ("what, not why").
3. **Imperative and verifiable.** "All functions must have explicit return types" beats "write clean code" — and if you want a style rule obeyed, back it with a linter; an unenforced prose rule is unreliable.
4. **Three-tier boundaries: Always / Ask first / Never.** The "Never" list is consistently the highest-value section.
5. **Nested, not monolithic.** Root = repo map + global conventions + top-level commands. One short file per top-level package. Split any file approaching ~150–200 lines. (The cascade: the closest file to the edited file wins; explicit prompts override everything.)
6. **Point at executable checks** (`just boundaries`, `just check`) rather than restating their flags or rules.

## Tool bridging

Maintain **AGENTS.md as the single source of truth**. Claude Code reads CLAUDE.md (not AGENTS.md natively): bridge with a thin `CLAUDE.md` containing exactly `@AGENTS.md` (portable, Windows-safe) or a symlink (`ln -s AGENTS.md CLAUDE.md`). Never maintain duplicate files — they drift. Codex reads AGENTS.md natively with a 32 KiB per-file cap (silently truncates — another reason to stay small); Cursor reads AGENTS.md plus `.cursor/rules/*.mdc`; Copilot reads AGENTS.md natively.

## Root AGENTS.md template

Adapt names, commands, and rules to the confirmed design — every line here must be true of the actual scaffold:

```markdown
# <Repo name> — Agent Guide

## What this repo is
<1–2 sentences. Stack: e.g. Python 3.13 / FastAPI / uv workspace; React/Vite frontend.>

## Repo map (where code lives)
- `services/*` — deployable services. MAY import `libs/*`. MUST NOT import each other.
- `libs/*`     — shared libraries, layered (contracts < platform). Lower never imports higher.
- `infra/`     — IaC. NEVER imported by app code. Do not edit without approval.
- `tools/`, `docs/` — tooling and docs.

## Commands (always use these)
- Install:    `uv sync --all-packages`
- Test:       `just test`          (single pkg: `uv run --package <pkg> pytest <path>`)
- Lint:       `just lint`
- Types:      `just typecheck`
- Boundaries: `just boundaries`    (tach check-external · lint-imports)
- All checks: `just check`         (run before every commit)

## Conventions
- src layout everywhere; tests colocated in each package's `tests/`.
- New shared code goes in the lowest `libs/` layer that satisfies its dependencies.
- Inter-package deps require BOTH a `dependencies` entry AND `[tool.uv.sources] x = { workspace = true }`.

## Boundaries
- Always: run `just check` before committing; add/adjust the module's `tach.toml` entry when adding a package.
- Ask first: changing `tach.toml` layers, adding a new top-level dir, editing `infra/`.
- Never: import one service from another; add an undeclared third-party import; edit generated code.

## Changing the structure
The layout is intentional but mutable. To add/split a module or change a contract, follow `docs/STRUCTURE.md` (update `tach.toml`/tags, run `tach sync`, update this file).
```

## Per-package AGENTS.md template

Keep to ~5–8 lines:

```markdown
# libs/platform — Agent Guide
Purpose: logging, config, tracing. Layer: platform (may import contracts). MUST NOT import services or apps.
Public interface: only `platformlib.api` is importable by others (enforced by Import Linter protected contract).
Commands: `uv run --package platform-lib pytest libs/platform` · `uv run --package platform-lib pyright libs/platform`
Conventions: pure functions; no service-specific logic; config via pydantic-settings.
Never: import from `services/*`; add I/O beyond logging sinks.
```

## Staleness CI (keep instruction files docs-as-code)

The structure-change process must update the relevant AGENTS.md. Add a lightweight CI staleness check, e.g. a script asserting: every top-level package dir contains an AGENTS.md; every command named in the root AGENTS.md exists in the justfile; and (optionally) `tach.toml` modules match the tree (`tach sync --check`-style verification). Wire it into `just check` or CI so drift fails loudly.
