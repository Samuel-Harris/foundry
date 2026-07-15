# Decision framework — interview axes → structural choices

Run the interview one axis at a time. Infer answers from context where you can; ask only what you cannot infer. Map each answer to its structural consequence immediately and say the consequence out loud so the design converges visibly.

## The ten axes and their mapping

| Axis | Answer → structural consequence |
|---|---|
| **1. Languages & runtimes?** | Python-only → uv workspace + Tach + Import Linter. TS-only → pnpm + Turborepo + (Nx or dependency-cruiser). Both → both stacks side by side (Archetype A), boundary tools per language. 3+ langs at large scale → recommend (never scaffold) Pants/Bazel; see thresholds below. |
| **2. Number & type of deployables?** | 1 app + shared code → Archetype A. Several apps sharing libs → Archetype B. Many independent services → Archetype E (`services/`, independence contracts, per-service migrations). Data/ML pipelines → Archetype C. CLI tools + libs → Archetype D. |
| **3. How much shared code, how coupled?** | Lots of shared, layered → `libs/` with a Tach / Import Linter layer stack (core < clients < feature). Little shared → keep `libs/` minimal; favour app isolation. |
| **4. Agent parallelism / blast radius?** | High parallelism (multiple agents concurrently) → strong module isolation (independence contracts), per-module AGENTS.md, recommend git-worktree workflow, minimise central registry files (route tables, DI containers, workspace member lists) and make unavoidable ones append-only/alphabetised. Low → simpler single-layer boundaries. |
| **5. Versioning strategy?** | Single-version policy (lockstep, one lockfile) → uv workspace + Turborepo just-in-time internal packages. Independent versioning → compiled/publishable packages, per-package versions, changesets. |
| **6. Publish targets?** | Internal-only → JIT/compiled internal packages, `workspace = true` sources, no registry config. Published to PyPI/npm → src layout + publishable packages + `tach check-external` mandatory (guarantees declared deps match real imports). |
| **7. Testing strategy?** | Fast unit-heavy → colocated tests, per-package pytest/vitest, `affected`-scoped CI. Heavy integration → dedicated test packages, testcontainers, separate CI stage. |
| **8. CI budget / speed sensitivity?** | Tight → Turborepo/Nx remote cache + `affected` builds; shift Tach/lint left into pre-commit. Generous → full matrix per PR. |
| **9. Expected growth?** | Will grow big/polyglot → design tags/layers now, keep boundaries strict, note the build-system migration path in STRUCTURE.md. Stays small → lighter boundaries, fewer layers. |
| **10. Team/agent ownership?** | Multiple owners → CODEOWNERS per top-level dir + Tach domains (`tach.domain.toml`) for local ownership. Single owner → root-level config with catch-all CODEOWNERS is fine. |

## Thresholds that change the plan (recommend-only)

- **Nx over plain dependency-cruiser** once the TS side exceeds ~10 projects or needs `affected`/remote cache.
- **Remote caching** (Turborepo/Nx) when single-package-PR CI regularly exceeds a few minutes.
- **Bazel/Pants/Buck2** only at 3+ languages AND 100+ targets/services AND a dedicated build engineer. Below that, the lightweight stack wins. Never scaffold these; recommend and link.
- **Split a monolithic AGENTS.md** into nested files once it approaches ~150–200 lines.
- **Extract a module into its own service** only when scaling, ownership, or compliance demands it — enforced boundaries make later extraction largely mechanical, so default to a modular monolith.

## Design Decision Record template

Present this filled-in record at the end of the interview. Every line traces to an axis answer. The user must explicitly confirm before any file is written.

```markdown
# Repo Design Decision Record — <repo name>

- **Languages/runtimes:** <e.g. Python 3.13 (uv); TypeScript (pnpm)>
- **Deployables:** <e.g. 2 services (payments, orders) + shared libs>
- **Archetype:** <A/B/C/D/E, with any adaptations>
- **Directory layout:** <one-line map, e.g. services/* + libs/{contracts,platform} + infra/ + docs/>
- **Dependency rules:** <e.g. services mutually independent; services → libs only; contracts is lowest layer>
- **Boundary tooling:** <e.g. Tach (layers + interfaces + check-external) + Import Linter (intra-service layers)>
- **Versioning/publish:** <e.g. lockstep, internal-only, single uv.lock>
- **Migrations:** <e.g. per-service alembic/, per-service version_table>
- **Testing:** <e.g. colocated per-package pytest; run via `uv run --package X pytest`>
- **Task runner:** <justfile | Makefile>
- **CI:** <e.g. GitHub Actions; boundary check as required gate; affected-scoping: yes/no>
- **Ownership:** <e.g. CODEOWNERS: * @org/maintainers + per-dir rules>
- **Agent instructions:** AGENTS.md root + per top-level package; CLAUDE.md bridge via @AGENTS.md
- **Explicitly out of scope:** <e.g. Bazel, npm publishing, k8s manifests>
```

Confirmation phrasing: ask "Shall I scaffold this? Anything to change?" and wait. Treat silence or ambiguity as non-confirmation.
