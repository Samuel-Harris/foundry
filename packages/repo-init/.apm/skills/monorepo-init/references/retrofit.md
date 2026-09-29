# Retrofit mode for existing repositories

Greenfield is the primary flow; use this flow when the target already contains code. The order inverts the greenfield flow: enforcement is ratcheted in around the existing coupling, and AGENTS.md comes last. Do not require wholesale cleanup before enforcement begins — the point is to turn on structure without blocking work.

Run a shortened design interview first. Axes 1–4 and 10 usually cover languages, deployables, coupling, parallelism, and ownership. Confirm a retrofit decision record containing the target archetype, ratchet plan, and migration order.

## 1. Map current coupling

Make the mess visible before changing anything. Use version-appropriate Tach inspection (`uv run tach mod` / `tach show`), dependency-cruiser graphs, or `nx graph`. Identify the worst cycles and cross-domain imports; prioritise one or two boundaries whose violation causes the most harm (for example a security-sensitive module, or the two apps that keep coupling). Present that map to the user — it drives the migration order in the decision record.

## 2. Add ownership

Add CODEOWNERS with a catch-all and per-top-level-directory rules before migration starts so changes and migration PRs route to the correct reviewers. This costs nothing and pays immediately.

## 3. Baseline and ratchet existing violations

Turn enforcement on for new violations:

- **Tach:** mark grandfathered imports with `# tach-ignore` (line-level grandfathering); isolate one sensitive module first and expand outward. A `deprecated = true` dependency edge allows existing usages while flagging new ones; use it for temporary migration edges when supported.
- **Import Linter:** list current violations in `ignore_imports` (and `allow_indirect_imports` only where the intended contract requires it) so the contract passes today and fails on anything new.
- **Ratchet:** snapshot current violation counts into a low-conflict baseline format (per-file or per-rule) and configure CI so counts may only decrease.
- **Prior art:** imbue-ai/ratchets, and Notion's ESLint ratchet (which moved the baseline from JSON to TSV specifically to avoid merge conflicts when many people fix violations in parallel — relevant under agent parallelism too).
- **Agent-friendliness:** ratchet checks are deterministic, with clear exit codes and machine-readable output.

Wire the ratcheted checks into pre-commit and CI as a required gate immediately — a baseline that is not enforced is a wish.

## 4. Migrate modules incrementally

Stand up the target structure (`libs/`, layers, workspace config), then move one module at a time behind stable interfaces (a strangler-fig migration) while the old code remains operational. Enforce each new boundary when the module lands and remove its baseline entries. This is the monolith → modular-monolith path; extract a separate service only when scaling, ownership, or compliance requires it.

Bring each migrated module fully to convention:

- src layout;
- its own manifest with declared dependencies;
- colocated tests;
- boundary configuration or tags;
- CODEOWNERS entry;
- passing `tach check-external` where applicable.

## 5. Add minimal AGENTS.md files

Per the evidence, do not front-load a large architecture document onto a messy repo. Add the root AGENTS.md only after canonical commands and boundaries exist, keeping it to commands, the Never list, and a pointer to the ratchet. Add package files as modules enter the target structure or when observed agent errors justify more guidance.

## Verification

Prove all three conditions:

- checks pass with the baseline in place (existing violations grandfathered);
- a new illegal import not present in the baseline fails pre-commit/CI with a legible error — demonstrate this;
- increasing the baseline violation count fails the ratchet.
