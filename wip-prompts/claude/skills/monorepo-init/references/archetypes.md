# Directory archetypes

Five starting layouts. Adapt to the confirmed design — rename `apps/`↔`services/`, drop unused dirs, add domain dirs — but preserve the invariants: every deployable under one top-level dir, every shared lib under another, one-way dependency direction, `infra/`/`notebooks/`/`data/` quarantined. `# →` annotations state what lives there and the dependency rule; carry these rules into the boundary configs and AGENTS.md.

Universal principles (apply to every archetype):
- **Predictability over cleverness.** An agent that has seen one module can predict the shape of every other.
- **Colocation.** Tests live next to the code they test (per-package `tests/` mirroring `src/`); config that governs a package lives in that package.
- **Dependency direction is a one-way street:** apps may import libs; apps never import each other; libs form layers and a lower layer never imports a higher one; shared/core libs import nothing internal.
- **Central registry hotspots** (route tables, DI containers, workspace member lists) are merge-conflict magnets under agent parallelism: minimise them; where unavoidable make them append-only and alphabetised.

## Archetype A — Full-stack app (backend API + web frontend)

```
repo/
├── AGENTS.md                  # → root: repo map, global conventions, top-level commands
├── CLAUDE.md                  # → bridge: contains "@AGENTS.md"
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

Rules: `apps → libs/packages` only; `libs` form a layer stack (`core` < `clients` < feature); apps mutually independent; `infra`/`docs`/`tools` leaf/utility. Python enforcement: Import Linter layers contract (`api | ...` siblings over `clients`, `core`) + `tach check-external`; TS enforcement: Nx tags or dependency-cruiser.

## Archetype B — Multiple apps sharing internal libraries

```
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

Rule: `scope:admin` depends only on `scope:admin` + `scope:shared`; `scope:store` only on `scope:store` + `scope:shared` — so admin and store can never couple. This is Nx's two-dimensional tag pattern (`scope:*` + `type:*`); in Python it's one Import Linter layers contract with the apps as `|`-independent siblings above the `libs` layers, plus `tach check-external` for declaredness.

## Archetype C — Data / ML pipeline repo

```
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

Key boundary: `notebooks/` and `data/` are quarantined. Enforce with an Import Linter `forbidden` contract: `source_modules = pipelines, libs`; `forbidden_modules = notebooks`.

## Archetype D — CLI tools + libraries

```
repo/
├── apps/
│   ├── cli-foo/   # → thin entrypoint; argument parsing only; imports libs
│   └── cli-bar/
├── libs/
│   ├── core/      # → all real logic; unit-tested independently of any CLI
│   └── plugins/   # → optional; may import core
```

Rule: CLIs are thin and independent; all logic in libs so it's testable without the CLI harness. `tach check-external` ensures each CLI declares exactly the libs it imports.

## Archetype E — Services-oriented (multiple deployable services)

```
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

Rule: services are mutually independent (Import Linter layers contract with `payments | orders | notifications` as the top layer); they communicate only through `libs/contracts` (shared schemas), never by importing each other's `src`. This is the modular-monolith → extractable-microservice pattern: because boundaries are enforced, later extraction is largely mechanical (move code, swap in-process calls for RPC, give the service its own DB using the schema it already owns).
