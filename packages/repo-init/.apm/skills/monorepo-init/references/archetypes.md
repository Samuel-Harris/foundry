# Directory archetypes

Five starting layouts for the confirmed design. Rename `apps/`↔`services/`, drop unused directories, or add domain directories — but preserve these invariants:

- Every deployable lives under one top-level directory and every shared library under another.
- Dependency direction is a one-way street: apps may import libraries (`libs/`/`packages/`); apps never import each other; libraries form layers and a lower layer never imports a higher one; shared or core libraries import no internal packages.
- `infra/`, `notebooks/`, and `data/` remain quarantined from application imports.
- Colocation: tests live next to the code they test in a per-package `tests/` directory mirroring `src/`, and config that governs a package lives in that package.
- Central registries are minimised; unavoidable registries (route tables, DI containers, workspace member lists) are merge-conflict magnets under agent parallelism, so make them append-only and alphabetised.
- Predictability over cleverness: an agent that has seen one module can predict the shape of every other.

The `# →` annotations in the trees below state what lives there and the dependency rule; carry these rules into the boundary configs and AGENTS.md.

## Archetype A — Full-stack app

```text
repo/
├── AGENTS.md                  # → root: repo map, global conventions, top-level commands
├── CLAUDE.md                  # → thin host bridge containing "@AGENTS.md" (see agents-md.md)
├── justfile                   # → canonical tasks: test/lint/typecheck/boundaries/check
├── pyproject.toml             # → uv workspace root (virtual; package = false)
├── uv.lock                    # → single lockfile for all Python members
├── package.json               # → pnpm workspace root
├── pnpm-workspace.yaml
├── turbo.json
├── tach.toml                  # → Python module boundaries + layers
├── .importlinter              # → intra-package architecture contracts
├── .dependency-cruiser.js     # → TS import rules
├── .pre-commit-config.yaml
├── .github/workflows/ci.yml
├── CODEOWNERS
├── apps/
│   ├── api/                   # → FastAPI app. MAY import libs/*. MUST NOT import web or other apps.
│   │   ├── AGENTS.md
│   │   ├── pyproject.toml     # → member; deps incl. workspace libs via tool.uv.sources
│   │   ├── src/api/           # → src layout
│   │   ├── tests/
│   │   └── alembic/           # → migrations OWNED by this app
│   └── web/                   # → React/Vite app. MAY import packages/*. MUST NOT import api source.
│       ├── AGENTS.md
│       ├── package.json
│       └── src/
├── libs/                      # → Python shared libraries (layered)
│   ├── core/                  # → lowest layer: domain models, pure logic. Imports nothing internal.
│   └── clients/               # → higher layer: may import core. HTTP/db clients.
├── packages/                  # → TS shared packages
│   └── ui/                    # → shared components (tags: type:ui, scope:shared)
├── infra/                     # → Terraform/CDK. NEVER imported by app code. Edit needs approval.
├── docs/
└── tools/                     # → repo scripts, codegen, lint plugins
```

Rules: `apps → libs/packages` only; `libs` form a layer stack such as `core` < `clients` < feature; apps are mutually independent; `infra`, `docs`, and `tools` are leaf or utility directories. Python enforcement: an Import Linter layers contract (`api | ...` siblings over `clients`, `core`) plus `tach check-external`; TypeScript enforcement: Nx tags or dependency-cruiser.

## Archetype B — Multiple apps sharing internal libraries

```text
repo/
├── apps/
│   ├── admin/      # → independent deployable; tag scope:admin
│   ├── storefront/ # → independent deployable; tag scope:store
│   └── worker/     # → queue consumer; tag scope:worker
├── libs/
│   ├── core/       # → scope:shared, lowest layer
│   ├── auth/       # → scope:shared; may import core
│   └── billing/    # → domain lib; may import core, auth
```

Rule: `scope:admin` depends only on `scope:admin` and `scope:shared`; `scope:store` depends only on `scope:store` and `scope:shared` — so admin and store can never couple. Enforce this with Nx's two-dimensional `scope:*` and `type:*` tags. In Python, use one Import Linter layers contract with the apps as independent `|` siblings above the library layers, plus `tach check-external` for declared dependencies.

## Archetype C — Data/ML pipeline repository

```text
repo/
├── pipelines/         # → orchestration DAGs (Airflow/Dagster/Prefect). Import libs/*.
│   └── training/
├── libs/
│   ├── features/      # → feature engineering; pure, testable
│   ├── models/        # → model definitions; may import features
│   └── io/            # → data access (S3, warehouse); lowest layer
├── notebooks/         # → EXPLORATORY only; NEVER imported by pipelines or libs
├── configs/           # → experiment/hyperparameter configs (yaml)
└── data/              # → gitignored; only sample fixtures committed
```

Rule: `notebooks/` and `data/` are quarantined. Enforce notebook isolation with an Import Linter forbidden contract whose `source_modules` are pipelines and libs and whose `forbidden_modules` is notebooks.

## Archetype D — CLI tools and libraries

```text
repo/
├── apps/
│   ├── cli-foo/   # → thin entrypoint; argument parsing only; imports libs
│   └── cli-bar/
├── libs/
│   ├── core/      # → all real logic; unit-tested independently of any CLI
│   └── plugins/   # → optional; may import core
```

Rule: CLIs are thin, independent entry points. Keep real logic in libraries so it can be tested without the CLI harness. Use `tach check-external` to ensure each CLI declares exactly the libraries it imports.

## Archetype E — Multiple deployable services

```text
repo/
├── services/
│   ├── payments/   # → own deployable, own Dockerfile, own alembic/, own DB schema
│   │   ├── AGENTS.md
│   │   ├── pyproject.toml
│   │   ├── src/payments/
│   │   ├── alembic/
│   │   └── tests/
│   ├── orders/
│   └── notifications/
├── libs/
│   ├── contracts/  # → shared API/event schemas (pydantic/proto). Lowest layer.
│   └── platform/   # → logging, config, tracing; may import contracts
├── infra/
└── docs/
```

Rule: services are mutually independent (an Import Linter layers contract with `payments | orders | notifications` as the top layer); they communicate only through `libs/contracts` (shared schemas), never by importing another service's `src`. This preserves a modular-monolith path to later service extraction: because boundaries are enforced, later extraction is largely mechanical (move code, swap in-process calls for RPC, give the service its own DB using the schema it already owns).
