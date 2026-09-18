---
name: monorepo-init
description: Initialise or retrofit a monorepo for structured agentic development through an interactive design interview and a working scaffold with machine-enforced module boundaries, nested AGENTS.md files, pre-commit, CI gates, and CODEOWNERS. Use when starting or restructuring a repository, scaffolding a project, preparing a codebase for AI-agent development, adding module-boundary enforcement or AGENTS.md files, or fixing structural drift in agent-generated code. Supports Python with uv, Tach, and Import Linter; TypeScript with pnpm, Turborepo, and Nx or dependency-cruiser. Do not use for a narrow feature change that does not alter repository structure.
---

# Monorepo Init

Initialise a monorepo so agents and humans can navigate, extend, and verify it by convention alone.

## Governing principle

**Structure a machine can verify beats structure that is merely documented.** Empirical evidence (ETH Zurich/LogicStar.ai, arXiv:2602.11988; McMillan, arXiv:2605.10039) shows instruction files alone deliver marginal effects and compliance decays within a session. Tooling that fails a commit when a boundary is crossed is more reliable. Back every structural rule with a CLI-checkable config where possible; identify unenforceable rules as advisory.

Three pillars, in priority order:

1. A pre-defined but mutable directory archetype with strict dependency-direction rules.
2. Machine-enforced module boundaries wired into pre-commit and CI.
3. Nested, minimal AGENTS.md files that point at executable checks.

## Workflow

```text
Phase 1: Design interview → Design Decision Record → USER CONFIRMATION GATE
Phase 2: Scaffold the complete repository from the confirmed record
Phase 3: Verify installation, passing checks, and failing illegal imports
Phase 4: Handover
```

Never write scaffold files before the user explicitly confirms the Design Decision Record. If the user requests sensible defaults, produce a record from those defaults and ask for one-line confirmation.

If the target repository contains code, use retrofit mode: read [references/retrofit.md](references/retrofit.md) and follow that flow.

## Phase 1 — Design interview

Read [references/decision-framework.md](references/decision-framework.md).

- Ask about one axis at a time, or two tightly related axes.
- Infer answers from the request, repository, and conversation before asking. Aim for 3–6 questions.
- Map each answer to a concrete structural consequence using the reference and tell the user that consequence.
- Produce materially different scaffolds for different answers.

Present the completed Design Decision Record and ask for explicit confirmation. Offer to amend any line. Proceed only after confirmation.

## Phase 2 — Scaffold

Before writing files, read the references relevant to the confirmed design:

| Design involves                       | Read                                                                           |
| ------------------------------------- | ------------------------------------------------------------------------------ |
| Directory layout                      | [references/archetypes.md](references/archetypes.md), always                   |
| Python members                        | [references/python-stack.md](references/python-stack.md)                       |
| TypeScript/JavaScript members         | [references/typescript-stack.md](references/typescript-stack.md)               |
| AGENTS.md files                       | [references/agents-md.md](references/agents-md.md), always                     |
| Cross-cutting files and sample module | [references/scaffold-components.md](references/scaffold-components.md), always |

Produce the complete scaffold:

1. Workspace configuration: root `pyproject.toml` with `[tool.uv.workspace]` and/or `package.json`, `pnpm-workspace.yaml`, and `turbo.json`; one lockfile per ecosystem.
2. Full chosen directory tree with installable, testable packages. Each member has its own manifest, `src/`, and `tests/`.
3. Root AGENTS.md and one per top-level package.
4. Boundary configs: `tach.toml` with `check-external`, `.importlinter`, and/or Nx `depConstraints` or dependency-cruiser.
5. Root `justfile`, or a Makefile when confirmed, with `test`, `lint`, `typecheck`, `boundaries`, and `check`.
6. Pre-commit configuration running the fast checks.
7. CI pipeline with the boundary check as a required gate.
8. CODEOWNERS with per-directory rules and a catch-all.
9. At least one fully worked sample module demonstrating every convention: src layout, colocated tests, public interface, workspace sources or tags, passing boundaries, and its own AGENTS.md. Include 2–3 small domain-flavoured functions and tests, but no unrequested application business logic.
10. `docs/STRUCTURE.md` documenting the safe structure-change process.

Recommend Bazel, Pants, or Buck2 only when the design has at least three languages, at least 100 targets or services, and a dedicated build engineer. Never scaffold those systems through this skill.

Tool schemas change. Pin tool versions in the scaffold. If verification rejects an option, consult documentation for the installed version before changing the design.

## Phase 3 — Verify

A scaffold is complete only after proving:

1. Installation succeeds with `uv sync --all-packages` and/or `pnpm install`.
2. Run `just fmt` once, then confirm `just check` exits 0.
3. Boundary enforcement fails with legible file-and-line errors for both:
   - an undeclared cross-package import, caught by `tach check-external` or dependency-cruiser missing-deps;
   - a declared-but-forbidden import after adding the dependency to the importer's manifest, caught by Import Linter or Nx `depConstraints`.
4. Remove each deliberate violation and confirm all checks pass again.

Fix failures and repeat verification. A boundary rule that has never been observed failing is unproven.

## Phase 4 — Handover

Summarise:

- the confirmed design in one line;
- the directory map;
- canonical commands such as `just check`;
- proof that checks passed and illegal imports were caught;
- the structure-change process in `docs/STRUCTURE.md`.

Identify the root AGENTS.md as the agent entry point. Keep it minimal and current: it points to the checks, while the checks enforce the structure.

## References

- [references/decision-framework.md](references/decision-framework.md) — interview axes, mappings, and decision-record template.
- [references/archetypes.md](references/archetypes.md) — five directory archetypes and dependency rules.
- [references/python-stack.md](references/python-stack.md) — uv, Tach, Import Linter, src layout, Alembic, and Python checks.
- [references/typescript-stack.md](references/typescript-stack.md) — pnpm, Turborepo, Nx, dependency-cruiser, and project references.
- [references/agents-md.md](references/agents-md.md) — evidence-based AGENTS.md rules and templates.
- [references/scaffold-components.md](references/scaffold-components.md) — cross-cutting templates and sample-module pattern.
- [references/retrofit.md](references/retrofit.md) — migration flow for existing repositories.
