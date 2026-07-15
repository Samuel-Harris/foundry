---
name: monorepo-init
description: Initialise a monorepo for structured agentic development — an interactive design interview followed by a full working scaffold with machine-enforced module boundaries (uv workspaces + Tach + Import Linter for Python; pnpm + Turborepo + Nx/dependency-cruiser for TypeScript), nested AGENTS.md files, pre-commit, CI boundary gates, and CODEOWNERS. Use this skill whenever the user wants to start a new repository or monorepo, scaffold a project structure, set up a codebase for AI-agent development, add module-boundary enforcement or AGENTS.md files to a repo, or complains that agent-generated code is becoming a structural mess. Trigger even if they just say "set up a new project", "create a repo for X", or "restructure my repo" — this skill also has a retrofit mode for existing repositories.
---

# monorepo-init

Initialise a monorepo so that AI agents (and humans who haven't internalised the codebase) can navigate, extend, and verify it by convention alone.

## Governing principle

**Structure a machine can verify beats structure that is merely documented.** Empirical evidence (ETH Zurich/LogicStar.ai, arXiv:2602.11988; McMillan, arXiv:2605.10039) shows instruction files alone deliver marginal effects and compliance decays within a session. What reliably holds structure is tooling that fails a commit when a boundary is crossed and emits an error an agent can read and self-correct from. Therefore: every structural rule this skill establishes must be backed by a config a CLI can check (Tach, Import Linter, Nx `depConstraints`, dependency-cruiser). Any rule that cannot be enforced by tooling is advisory only — never rely on prose to hold structure.

Three pillars, in priority order:
1. A pre-defined but **mutable** directory archetype with strict dependency-direction rules.
2. **Machine-enforced module boundaries** wired into pre-commit and CI.
3. Nested, **minimal** AGENTS.md files that point at the executable checks.

## Workflow overview

```
Phase 1: Design interview  →  Design Decision Record  →  ⛔ USER CONFIRMATION GATE
Phase 2: Scaffold (full working repo per the record)
Phase 3: Verify (install + checks pass + illegal import provably fails)
Phase 4: Handover
```

**Never write a single scaffold file before the user has explicitly confirmed the Design Decision Record.** If the user says "just pick sensible defaults", still produce the record from your defaults and get a one-line confirmation — the record is what makes the structure intentional rather than accidental.

If the target repository already exists and contains code, this is a **retrofit**, not a greenfield init — read `references/retrofit.md` and follow that flow instead (it inverts the order: map coupling first, AGENTS.md last).

## Phase 1 — Design interview

Read `references/decision-framework.md`. It contains the ten decision axes, the answer→structure mapping table, and the Design Decision Record template.

How to run the interview:
- Ask about **one axis at a time** (or two tightly-related ones). Don't dump a questionnaire; each answer narrows the next question. E.g. if the answer to "languages?" is "Python only", never ask about npm publish targets.
- **Infer before you ask.** If the user's request, an existing repo, or prior conversation already answers an axis, state the inference in the record instead of asking. Aim for 3–6 questions in a typical session, not ten.
- Map every answer to a concrete structural consequence as you go (archetype, boundary-contract style, tooling) using the mapping table. Tell the user the consequence — "several deployables sharing libs → `services/` layout with independence contracts" — so the interview converges visibly.
- There is **no one-size-fits-all**: different answers must produce materially different scaffolds. Do not emit a fixed template regardless of answers.

End of phase: present the completed **Design Decision Record** (template in the reference) and ask for explicit confirmation. Offer to amend any line. Only after "confirmed" (or equivalent) do you proceed.

## Phase 2 — Scaffold

Read the references relevant to the confirmed design **before writing files**:

| Design involves | Read |
|---|---|
| Choosing/adapting the directory layout | `references/archetypes.md` (always) |
| Python members | `references/python-stack.md` |
| TypeScript/JS members | `references/typescript-stack.md` |
| AGENTS.md files (always) | `references/agents-md.md` |
| Cross-cutting files: justfile, pre-commit, CI, CODEOWNERS, STRUCTURE.md, sample module | `references/scaffold-components.md` (always) |

Then produce the **complete** scaffold. The mandatory checklist (every item — a scaffold missing any of these is incomplete):

1. **Workspace configuration** — root `pyproject.toml` with `[tool.uv.workspace]` and/or `package.json` + `pnpm-workspace.yaml` + `turbo.json`; a single lockfile per ecosystem.
2. **Full directory tree** for the chosen archetype, with real (installable, testable) packages — each member has its own manifest, `src/`, and `tests/`.
3. **AGENTS.md throughout** — root + one per top-level package, plus a Claude Code bridge (`CLAUDE.md` containing `@AGENTS.md`, or a symlink).
4. **Boundary-enforcement configs** — `tach.toml` (with `check-external` wired), `.importlinter`, and/or Nx `depConstraints` / `.dependency-cruiser.js`, as appropriate to the stack.
5. **Task entry points** — root `justfile` (or `Makefile` if the user prefers / `just` is unavailable) with `test`, `lint`, `typecheck`, `boundaries`, `check`.
6. **Pre-commit config** running the fast subset of checks.
7. **CI pipeline** with the boundary check as a required gate.
8. **CODEOWNERS** with per-directory rules and a catch-all fallback.
9. **At least one fully-worked sample module** demonstrating every convention: src layout, colocated tests, a declared public interface, correct workspace sources/tags, a passing boundary check, and its own AGENTS.md. Give it a small amount of real domain-flavoured logic (2–3 functions + tests) so agents have a concrete pattern to copy — but do not write application business logic beyond this.
10. **`docs/STRUCTURE.md`** — the structure-change process. The structure is pre-defined but MUTABLE; this file is what makes mutation safe.

Polyglot build systems (Bazel/Pants/Buck2) are **recommend-only, never scaffolded**: mention them only if the design hits 3+ languages AND 100+ targets/services AND a dedicated build engineer — below that, the lightweight stack wins.

Tooling moves fast (uv, Tach, Turborepo schemas have all changed recently). Pin tool versions in the scaffold, and if a config option errors at verify time, check the installed version's docs rather than assuming the template is right.

## Phase 3 — Verify (non-negotiable)

A scaffold is not done until it is **proven working**:

1. **Install succeeds** — `uv sync --all-packages` and/or `pnpm install` completes cleanly from the fresh scaffold.
2. **`just check` passes** — run `just fmt` once after writing files, then the full loop (typecheck → lint → test → boundaries) must exit 0 out of the box.
3. **The fence is electrified** — deliberately violate the boundaries and confirm each violation **fails with a legible, file-and-line error an agent could self-correct from**. Test at least two attacks, because they are caught by different gates:
   - an **undeclared** cross-package import (one service importing another's code without touching manifests) — must fail the declared-deps check (`tach check-external` / depcruise missing-deps);
   - a **declared-but-forbidden** import (also add the dependency to the importer's manifest, as a careless agent would) — must fail the policy contract (Import Linter / Nx `depConstraints`).
   Show the user the error output, then remove the violations and confirm checks pass again.

If any step fails, fix the scaffold and re-verify — do not hand over a repo where the checks have never been seen green, or where the boundary check has never been seen red. **A boundary rule that has never been seen red is unproven**: boundary tools' semantics vary by version and repo shape (e.g. Tach's cross-package `[[modules]]` rules are silently inert once workspace members have their own manifests), and config that looks like enforcement but never fires is worse than none.

## Phase 4 — Handover

Give the user a short summary: the confirmed design (one line), the directory map, the canonical commands (`just check` etc.), the proof from Phase 3 (checks green; illegal import demonstrably caught), and where the change process lives (`docs/STRUCTURE.md`). Remind them that the root AGENTS.md is the agent entry point and should be kept minimal and current — it points at the checks; the checks hold the structure.

## Reference files

- `references/decision-framework.md` — the ten interview axes, answer→structure mapping, Design Decision Record template. **Read at the start of Phase 1.**
- `references/archetypes.md` — five annotated directory archetypes (full-stack, multi-app, data/ML, CLI+libs, services) with dependency rules. **Read at the start of Phase 2.**
- `references/python-stack.md` — uv workspaces, Tach (modules/layers/interfaces/check-external/deprecation), Import Linter contracts, src layout, Alembic placement, pytest/ruff/typechecker setup.
- `references/typescript-stack.md` — pnpm workspaces, Turborepo tasks, Nx module boundaries (tags + depConstraints), dependency-cruiser, tsconfig project references, internal-package strategies.
- `references/agents-md.md` — evidence-based AGENTS.md rules, root and per-package templates, Claude Code bridging, staleness checks.
- `references/scaffold-components.md` — liftable templates for justfile, pre-commit, CI, CODEOWNERS, `docs/STRUCTURE.md`, and the sample-module pattern. **Read before writing cross-cutting files.**
- `references/retrofit.md` — the secondary flow for existing repos: coupling map → CODEOWNERS → baseline & ratchet → strangler-fig → minimal AGENTS.md last.
