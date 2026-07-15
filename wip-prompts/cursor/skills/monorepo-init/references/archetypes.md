# Directory archetypes

Adapt these starting layouts to the confirmed design. Rename `apps/` to `services/`, drop unused directories, or add domain directories while preserving these invariants:

- Every deployable lives under one top-level directory and every shared library under another.
- Apps may import libraries; apps never import each other.
- Libraries form layers, and lower layers never import higher layers.
- Shared or core libraries import no internal packages.
- `infra/`, `notebooks/`, and `data/` remain quarantined from application imports.
- Tests live next to each package in a `tests/` directory mirroring `src/`.
- Central registries are minimised; unavoidable registries are append-only and alphabetised.

## Archetype A — Full-stack app

```text
repo/
├── AGENTS.md
├── justfile
├── pyproject.toml
├── uv.lock
├── package.json
├── pnpm-workspace.yaml
├── turbo.json
├── tach.toml
├── .importlinter
├── .dependency-cruiser.js
├── .pre-commit-config.yaml
├── .github/workflows/ci.yml
├── CODEOWNERS
├── apps/
│   ├── api/
│   │   ├── AGENTS.md
│   │   ├── pyproject.toml
│   │   ├── src/api/
│   │   ├── tests/
│   │   └── alembic/
│   └── web/
│       ├── AGENTS.md
│       ├── package.json
│       └── src/
├── libs/
│   ├── core/
│   └── clients/
├── packages/
│   └── ui/
├── infra/
├── docs/
└── tools/
```

Rules: `apps → libs/packages` only; `libs` form a layer stack such as core < clients < feature; apps are mutually independent; `infra`, `docs`, and `tools` are leaf or utility directories. Use Import Linter layers plus `tach check-external` for Python and Nx tags or dependency-cruiser for TypeScript.

## Archetype B — Multiple apps sharing internal libraries

```text
repo/
├── apps/
│   ├── admin/
│   ├── storefront/
│   └── worker/
├── libs/
│   ├── core/
│   ├── auth/
│   └── billing/
```

Rule: `scope:admin` depends only on `scope:admin` and `scope:shared`; `scope:store` depends only on `scope:store` and `scope:shared`. Enforce this with Nx's two-dimensional `scope:*` and `type:*` tags. In Python, use an Import Linter layers contract with apps as independent `|` siblings above library layers, plus `tach check-external` for declared dependencies.

## Archetype C — Data/ML pipeline repository

```text
repo/
├── pipelines/
│   └── training/
├── libs/
│   ├── features/
│   ├── models/
│   └── io/
├── notebooks/
├── configs/
└── data/
```

Rule: `notebooks/` and `data/` are quarantined. Enforce notebook isolation with an Import Linter forbidden contract whose source modules are pipelines and libs.

## Archetype D — CLI tools and libraries

```text
repo/
├── apps/
│   ├── cli-foo/
│   └── cli-bar/
├── libs/
│   ├── core/
│   └── plugins/
```

Rule: CLIs are thin, independent entry points. Keep real logic in libraries so it can be tested without the CLI harness. Use `tach check-external` to ensure each CLI declares exactly the libraries it imports.

## Archetype E — Multiple deployable services

```text
repo/
├── services/
│   ├── payments/
│   │   ├── AGENTS.md
│   │   ├── pyproject.toml
│   │   ├── src/payments/
│   │   ├── alembic/
│   │   └── tests/
│   ├── orders/
│   └── notifications/
├── libs/
│   ├── contracts/
│   └── platform/
├── infra/
└── docs/
```

Rule: services are mutually independent and communicate through `libs/contracts`, never by importing another service's source. Encode services as independent `|` siblings in an Import Linter layers contract. This preserves a modular-monolith path to later service extraction.
