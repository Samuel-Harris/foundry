# AGENTS.md rules and templates

## Why minimal

- ETH Zurich and LogicStar.ai (arXiv:2602.11988) found repository context files did not generally improve task success and increased inference cost. Developer-written files helped marginally where other documentation was absent.
- A factorial adherence study (arXiv:2605.10039) found no detectable compliance effect from file size, position, or single-versus-multiple instruction files within tested ranges. The robust effect was within-session compliance decay.
- Agents reliably discover AGENTS.md and follow relevant references from it.

Do not rely on AGENTS.md to hold structure. It points to executable checks and the change process; boundary tools enforce the structure.

## Generation rules

1. Keep every file minimal, high-signal, and hand-written. Do not restate the README or facts obvious from code and manifests.
2. Lead with commands and boundaries, not architecture essays.
3. Use imperative, verifiable instructions. Back style rules with a linter.
4. Separate boundaries into Always, Ask first, and Never. Prioritise the Never list.
5. Keep the root file to the repository map, global conventions, and commands. Add one short file per top-level package. Split files near 150–200 lines.
6. Point to `just boundaries` and `just check` rather than duplicating their flags and rules.

Use AGENTS.md as the shared source of truth. Add `.cursor/rules/*.mdc` only for Cursor-specific guidance that cannot be expressed portably; do not duplicate AGENTS.md content there.

## Root template

Adapt every name, command, and rule to the confirmed scaffold:

```markdown
# <Repo name> — Agent Guide

## What this repo is

<One or two sentences naming the stack and deployables.>

## Repo map

- `services/*` — deployable services. MAY import `libs/*`. MUST NOT import each other.
- `libs/*` — shared libraries, layered contracts < platform. Lower never imports higher.
- `infra/` — infrastructure code. NEVER imported by application code. Ask before editing.
- `tools/`, `docs/` — repository tooling and documentation.

## Commands

- Install: `uv sync --all-packages`
- Test: `just test`
- Lint: `just lint`
- Types: `just typecheck`
- Boundaries: `just boundaries`
- All checks: `just check`

## Conventions

- Use src layout everywhere and colocate tests in each package's `tests/`.
- Put new shared code in the lowest library layer that satisfies its dependencies.
- Inter-package dependencies require a manifest dependency and a matching workspace source.

## Boundaries

- Always: run `just check` before committing; register every new package with boundary tools.
- Ask first: change boundary layers, add a top-level directory, or edit `infra/`.
- Never: import one service from another; add an undeclared dependency; edit generated code.

## Changing the structure

Follow `docs/STRUCTURE.md` when adding, splitting, or changing a module or contract.
```

## Per-package template

Keep package files to roughly 5–8 lines:

```markdown
# libs/platform — Agent Guide

Purpose: logging, configuration, and tracing.
Layer: platform; may import contracts; must not import services or apps.
Public interface: only `platformlib.api` is importable by other packages.
Commands: `uv run --package platform-lib pytest libs/platform` · `uv run --package platform-lib pyright libs/platform`
Conventions: pure functions; no service-specific logic; configuration via pydantic-settings.
Never: import from `services/*`; add I/O beyond logging sinks.
```

## Staleness checks

Add a lightweight check that verifies:

- every top-level package contains AGENTS.md;
- commands named in root AGENTS.md exist in the task runner;
- boundary configuration matches the package tree where the installed tool supports a check mode.

Run the staleness check through `just check` or CI so drift fails visibly.
