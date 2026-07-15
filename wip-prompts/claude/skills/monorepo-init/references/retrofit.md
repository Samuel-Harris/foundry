# Retrofit mode — existing repos (secondary flow)

Greenfield is the primary flow; use this when the target repo already contains code. The order **inverts** the greenfield flow: enforcement is ratcheted in around the existing mess, and AGENTS.md comes last. Never demand upfront cleanup — the whole point is to turn on structure without blocking work.

Run a shortened design interview first (axes 1–4 and 10 usually suffice: languages, deployables, coupling, parallelism, ownership) and confirm a decision record scoped to the retrofit — target archetype, ratchet plan, migration order.

## Step 1 — Make the mess visible

Map current coupling before changing anything: `uv run tach mod` / `tach show`, dependency-cruiser graphs, or `nx graph`. Identify the worst cycles and cross-domain imports; prioritise the one or two boundaries whose violation hurts most (e.g. a security-sensitive module, or the two apps that keep coupling). Present the map to the user — it drives the migration order in the decision record.

## Step 2 — CODEOWNERS early

Add CODEOWNERS (catch-all + per-top-level-dir) before migration starts so migration PRs route to the right people. This costs nothing and pays immediately.

## Step 3 — Baseline existing violations, then ratchet

Turn enforcement on for **new** violations only:

- **Tach**: mark existing offending imports with `# tach-ignore` (line-level grandfathering); isolate one sensitive module first and expand outward. A `deprecated = true` dependency edge allows existing usages while flagging new ones.
- **Import Linter**: list current violations in `ignore_imports` (and `allow_indirect_imports` where relevant) so the contract passes today and fails on anything new.
- **The ratchet**: snapshot current violation counts into a baseline file (per-file or per-rule) and configure CI so the count may only **decrease**. Prior art: imbue-ai/ratchets; Notion's ESLint ratchet (they moved the baseline from JSON to TSV specifically to avoid merge conflicts when many people fix violations in parallel — relevant under agent parallelism too). Ratchet checks are agent-friendly: deterministic, clear exit codes, machine-readable output.

Wire the ratcheted checks into pre-commit and CI as a required gate immediately — a baseline that isn't enforced is a wish.

## Step 4 — Strangler-fig module migration

Stand up the target structure (`libs/`, layers, workspace config), then move code module-by-module behind stable interfaces while the old code keeps running. Enforce each new boundary the moment the module lands (remove its entries from the baseline). This is the monolith → modular-monolith path; only extract to separate services where scaling, ownership, or compliance justifies it.

For each migrated module, bring it fully up to convention: src layout, own manifest with declared deps (`tach check-external` clean), colocated tests, tach/tag entry, CODEOWNERS line.

## Step 5 — AGENTS.md last and minimal

Per the evidence, don't front-load a big architecture doc onto a messy repo. Add a short root AGENTS.md (commands + the Never list + a pointer to the ratchet) once the canonical commands actually exist, and grow per-package files only as modules land in the new structure or as agents demonstrably stumble.

## Verification (retrofit edition)

Same bar as greenfield, adapted:
- checks run green **with the baseline in place** (existing violations grandfathered);
- a **new** illegal import (one not in the baseline) fails pre-commit/CI with a legible error — demonstrate this;
- the ratchet provably rejects a baseline-count increase.
