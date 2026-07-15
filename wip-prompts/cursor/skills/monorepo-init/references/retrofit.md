# Retrofit mode for existing repositories

Use this flow when the target already contains code. Ratchet enforcement around current coupling and add AGENTS.md last. Do not require wholesale cleanup before enforcement begins.

Run a shortened design interview first. Axes 1–4 and 10 usually cover languages, deployables, coupling, parallelism, and ownership. Confirm a retrofit decision record containing the target archetype, ratchet plan, and migration order.

## 1. Map current coupling

Use version-appropriate Tach inspection, dependency-cruiser graphs, or `nx graph` before changing structure. Identify cycles and cross-domain imports. Prioritise one or two boundaries whose violation causes the most harm, then present that map to the user as the basis for migration order.

## 2. Add ownership

Add CODEOWNERS with a catch-all and per-top-level-directory rules before migration so changes route to the correct reviewers.

## 3. Baseline and ratchet existing violations

Turn enforcement on for new violations:

- **Tach:** mark grandfathered imports with `# tach-ignore`; isolate one sensitive module first and expand. Use `deprecated = true` for temporary migration edges when supported.
- **Import Linter:** list current violations in `ignore_imports`, and use `allow_indirect_imports` only where the intended contract requires it.
- **Ratchet:** store current counts in a low-conflict baseline format and configure CI so counts may only decrease.

Wire ratcheted checks into pre-commit and CI as a required gate immediately.

## 4. Migrate modules incrementally

Create the target structure, then move one module at a time behind stable interfaces while old code remains operational. Enforce each new boundary when the module lands and remove its baseline entries.

Bring each migrated module fully to convention:

- src layout;
- its own manifest with declared dependencies;
- colocated tests;
- boundary configuration or tags;
- CODEOWNERS entry;
- passing `tach check-external` where applicable.

Extract a separate service only when scaling, ownership, or compliance requires it. Otherwise preserve a modular monolith.

## 5. Add minimal AGENTS.md files

Add root AGENTS.md only after canonical commands and boundaries exist. Keep it to commands, the Never list, and a pointer to the ratchet. Add package files as modules enter the target structure or when observed agent errors justify more guidance.

## Verification

Prove all three conditions:

- checks pass with the baseline;
- a new illegal import not present in the baseline fails with a legible error;
- increasing the baseline violation count fails the ratchet.
