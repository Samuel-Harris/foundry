# Decision framework — interview axes to structural choices

Run the interview one axis at a time. Infer answers from context where possible and ask only what cannot be inferred. Map each answer to its structural consequence immediately so the design converges visibly.

## The ten axes and their mapping

| Axis                                          | Answer → structural consequence                                                                                                                                                                                                                                                                                      |
| --------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1. Languages and runtimes?**                | Python-only → uv workspace + Tach + Import Linter. TypeScript-only → pnpm + Turborepo + Nx or dependency-cruiser. Both → both stacks side by side using Archetype A, with boundary tools per language. Three or more languages at large scale → recommend, but never scaffold, Pants or Bazel; see thresholds below. |
| **2. Number and type of deployables?**        | One app + shared code → Archetype A. Several apps sharing libs → Archetype B. Many independent services → Archetype E with `services/`, independence contracts, and per-service migrations. Data/ML pipelines → Archetype C. CLI tools + libs → Archetype D.                                                         |
| **3. How much shared code, and how coupled?** | Lots of shared, layered code → `libs/` with a Tach or Import Linter layer stack such as core < clients < feature. Little shared code → keep `libs/` minimal and favour app isolation.                                                                                                                                |
| **4. Agent parallelism and blast radius?**    | High parallelism → strong module isolation, per-module AGENTS.md, explicit file ownership between concurrent tasks, minimal central registries, and append-only or alphabetised unavoidable registries. Low parallelism → simpler single-layer boundaries.                                                           |
| **5. Versioning strategy?**                   | Single-version policy → uv workspace + Turborepo just-in-time internal packages and one lockfile per ecosystem. Independent versioning → compiled or publishable packages, per-package versions, and changesets.                                                                                                     |
| **6. Publish targets?**                       | Internal-only → JIT or compiled internal packages, `workspace = true` sources, and no registry config. PyPI/npm publishing → src layout + publishable packages + mandatory `tach check-external`.                                                                                                                    |
| **7. Testing strategy?**                      | Fast unit-heavy → colocated tests, per-package pytest/vitest, and affected-scoped CI. Heavy integration → dedicated test packages, testcontainers, and a separate CI stage.                                                                                                                                          |
| **8. CI budget and speed sensitivity?**       | Tight → Turborepo/Nx remote cache + affected builds; run Tach and lint in pre-commit. Generous → full matrix per PR.                                                                                                                                                                                                 |
| **9. Expected growth?**                       | Large or polyglot growth → define tags and layers now, keep boundaries strict, and document the build-system migration path in STRUCTURE.md. Stays small → lighter boundaries and fewer layers.                                                                                                                      |
| **10. Team and agent ownership?**             | Multiple owners → CODEOWNERS per top-level directory + Tach domains (`tach.domain.toml`) for local ownership. Single owner → root-level config with catch-all CODEOWNERS.                                                                                                                                            |

## Thresholds that change the plan

- Prefer Nx over plain dependency-cruiser once the TypeScript side exceeds roughly ten projects or needs affected execution or remote caching.
- Add remote caching when CI for single-package changes regularly exceeds a few minutes.
- Recommend Bazel, Pants, or Buck2 only with at least three languages, at least 100 targets or services, and a dedicated build engineer. Never scaffold these.
- Split a monolithic AGENTS.md into nested files near 150–200 lines.
- Extract a module into its own service only when scaling, ownership, or compliance requires it. Default to a modular monolith.

## Design Decision Record template

Fill in and present this record at the end of the interview. Every line must trace to an axis answer. The user must explicitly confirm it before scaffold files are written.

```markdown
# Repo Design Decision Record — <repo name>

- **Languages/runtimes:** <e.g. Python 3.13 with uv; TypeScript with pnpm>
- **Deployables:** <e.g. two services, payments and orders, plus shared libs>
- **Archetype:** <A/B/C/D/E, with adaptations>
- **Directory layout:** <one-line map>
- **Dependency rules:** <e.g. services mutually independent; services → libs only; contracts is the lowest layer>
- **Boundary tooling:** <e.g. Tach check-external + Import Linter layers and protected contracts>
- **Versioning/publish:** <e.g. lockstep, internal-only, single uv.lock>
- **Migrations:** <e.g. per-service alembic/ and version_table>
- **Testing:** <e.g. colocated per-package pytest>
- **Task runner:** <justfile or Makefile>
- **CI:** <provider; boundary check as required gate; affected-scoping yes/no>
- **Ownership:** <CODEOWNERS catch-all and per-directory owners>
- **Agent instructions:** <AGENTS.md root + per top-level package; optional project-specific .cursor/rules files>
- **Explicitly out of scope:** <e.g. Bazel, npm publishing, Kubernetes manifests>
```

Ask: "Shall I scaffold this? Anything to change?" Treat silence or ambiguity as non-confirmation.
