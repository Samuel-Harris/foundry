# Python stack: uv workspaces + Tach + Import Linter

## uv workspaces

- **Root `pyproject.toml` is virtual**: `[tool.uv] package = false`, plus:
  ```toml
  [tool.uv.workspace]
  members = ["apps/*", "libs/*"]        # or services/*; add exclude = [...] if needed

  [dependency-groups]                    # PEP 735 — shared dev tooling at the root
  dev = ["pytest>=8", "ruff>=0.8", "pyright>=1.1", "tach>=0.2", "import-linter>=2", "pre-commit>=4"]
  ```
- **Members**: each app/lib has its own `pyproject.toml`. Inter-member dependencies require **both** entries — omitting the source raises `"...is included as a workspace member, but is missing an entry in tool.uv.sources"`:
  ```toml
  [project]
  dependencies = ["contracts"]

  [tool.uv.sources]
  contracts = { workspace = true }
  ```
  Root `tool.uv.sources` apply to all members unless a member overrides (per-dependency, total).
- **Single `uv.lock`** for the whole workspace — no version skew. `uv sync --all-packages` installs everything; `uv sync --package <name>` one member; member deps are always editable. The workspace's `requires-python` is the intersection of all members'.
- **Gotchas**: root `[dependency-groups]` dev deps are what `uv sync` installs by default at the root, but per-member dev groups are *not* auto-installed across members. Same-named test files across members collide in pytest collection — give each member a unique import package name and set `--import-mode=importlib` (put `addopts = "--import-mode=importlib"` in root `[tool.pytest.ini_options]`).
- **Use a workspace when** members share a coherent dependency set and are developed together; use path/git sources instead when a member needs a conflicting dependency version or its own venv.
- Each member's build config: use `hatchling` (or uv's default) with src layout; `uv init --lib` scaffolds it. Minimal member `pyproject.toml`:
  ```toml
  [project]
  name = "payments"
  version = "0.1.0"
  requires-python = ">=3.12"
  dependencies = ["contracts", "platform-lib"]

  [tool.uv.sources]
  contracts = { workspace = true }
  platform-lib = { workspace = true }

  [build-system]
  requires = ["hatchling"]
  build-backend = "hatchling.build"

  [tool.hatch.build.targets.wheel]
  packages = ["src/payments"]
  ```

## Tach (`tach.toml`) — declared-dependency enforcement (and intra-package modules)

Fast (Rust), no runtime impact, incrementally adoptable. **Critical, version-verified behaviour (Tach ≥0.35): once workspace members have their own `pyproject.toml`, Tach treats each member as a distinct *package*. Cross-package imports are then governed by `tach check-external` (declared package dependencies), NOT by `[[modules]]`/`depends_on`/`layers` in `tach.toml` — cross-package module rules are silently inert.** Do not scaffold cross-package `[[modules]]` entries in a uv workspace: config that looks like enforcement but never fires is worse than none. Division of labour in a workspace:

- **`tach check-external`** — the cross-package gate. Validates that every import between workspace members, and every third-party import, resolves to a declared dependency in the importing member's own `pyproject.toml`. It is **bidirectional**: an undeclared import fails (`[FAIL] services/orders/src/orders/checkout.py:1: Dependency 'payments' is not declared in package 'orders'.`) and an **unused declared dependency also fails** — so the scaffold must only declare deps each member actually imports. This is the key monorepo win: the shared venv has *all* deps, so an undeclared import passes tests locally but breaks for anyone installing just that package. Config needed: just `source_roots` covering every member's `src` (plus `exclude` if needed):

  ```toml
  # tach.toml — in a uv workspace this is the whole job
  source_roots = [
      "services/payments/src",
      "services/orders/src",
      "libs/contracts/src",
      "libs/platform/src",
  ]
  ```
  A glob (`source_roots = ["**/src"]`) also works if every member uses src layout. Add a comment in the emitted tach.toml explaining the division of labour so future agents don't add inert cross-package modules.

- **`[[modules]]` / `layers` / `[[interfaces]]` / `tach check`** — govern module structure **within** one package (dotted paths, e.g. `payments.web` → `payments.domain` layers), or the whole repo in a *single-package* modular monolith with no member manifests. In that no-member-manifests case the report-style config works as expected:

  ```toml
  layers = ["ui", "services", "core"]
  [[modules]]
  path = "app.web"
  layer = "ui"
  # ... depends_on / [[interfaces]] expose = [...] etc.
  ```
  Useful pieces: `forbid_circular_dependencies = true`; `[[interfaces]] expose = ["api.*"] from = [...]`; `utility = true` for shared-by-all modules; `exact = true` to fail on unused declared module deps; `tach sync` writes discovered deps back into tach.toml; a `deprecated = true` dependency edge allows existing usages while flagging new ones; `# tach-ignore` grandfathers a single import line (retrofit ratchets); `tach.domain.toml` files give teams local ownership of module config.

- **Cross-package *policy*** — which member MAY depend on which, service independence, layer direction, public-interface-only — lives in **Import Linter** (below), because `check-external` only checks *declaredness*: an agent that adds the forbidden package to `pyproject.toml` sails through `check-external`, and must be stopped by the Import Linter contract. Both gates are needed; the fence test in Phase 3 must try both attacks.

Verify behaviour against the installed version (`tach --version`) — the config schema and package semantics have changed across versions. If a boundary rule has never been seen *red*, treat it as unproven: deliberately violate it once and watch it fail.

## Import Linter (`.importlinter`) — cross-package policy + intra-package architecture

In a uv workspace, Import Linter is the tool that encodes **which member MAY import which** (Tach `check-external` only checks declaredness). It runs by importing the packages, so the workspace must be installed: `uv run lint-imports`. Contract types:

- **layers** — ordered high→low; higher may import lower only. Siblings on one line: `a | b` = independent of each other; `a : b` = may import each other. One layers contract can therefore express both service independence and lib direction (verified pattern):

  ```ini
  [importlinter]
  root_packages =
      payments
      orders
      contracts
      platformlib
  include_external_packages = True

  [importlinter:contract:package-layers]
  name = Package layers: services (independent) > platform > contracts
  type = layers
  layers =
      payments | orders
      platformlib
      contracts
  ```
  Violation output names the contract and shows the exact import chain with line numbers — agent-legible. Also supports `containers` (repeat a layer pattern across sibling packages — ideal for enforcing the same web>services>domain structure inside every service), optional layers `(medium)`, and `exhaustive = true` (+ `exhaustive_ignores`) to fail when an undeclared module appears in a container.
- **protected** — modules importable only by an allow-list. **Use this (not `forbidden`) for public-interface enforcement**: `forbidden` follows *indirect* chains, so `payments → contracts.api → contracts._schemas` counts as a violation even though payments only touched the public interface. Verified pattern:

  ```ini
  [importlinter:contract:contracts-public-interface]
  name = contracts internals importable only within contracts (use contracts.api)
  type = protected
  protected_modules = contracts._schemas
  allowed_importers = contracts
  ```
- **forbidden** — `source_modules` must not import `forbidden_modules` (indirectly included); with `include_external_packages = True` this covers third-party packages — e.g. forbid `requests`/`boto3` in a pure schemas layer, or quarantine `notebooks/` from pipelines.
- **independence** — modules that must not import each other in any direction (alternative to `|` siblings when the modules aren't in a layer stack).
- **acyclic siblings** — forbids cycles among siblings.

Keep contract names descriptive — they are the first line of the error an agent sees.

## src vs flat layout

**Default to src layout for every workspace member** (`member/src/pkgname/…`). `src/` isn't on `sys.path`, so tests run against the *installed* editable package, catching packaging bugs (missing files, wrong package name) before release; it also makes `source_roots = ["**/src"]` uniform for Tach and makes each member a real installable unit — exactly the isolation agentic work needs. Flat layout is acceptable only for a single never-published app. (`uv init --lib` scaffolds src layout.) Choose import-package names that don't shadow the stdlib or popular packages (`platform`, `types`, `email`, ...) — e.g. directory `libs/platform` with import package `platformlib`. Also give every member a *unique* import name to avoid pytest collection collisions.

## Alembic (migrations) placement

**Per-service migration ownership**: each deployable owns its own `alembic/` directory, its own `alembic.ini` (or `--name` section), and — critically — its own **`version_table`** so histories never collide even on a shared physical database. Surface `just makemigrations <svc>` / `just migrate <svc>` wrappers in the justfile so agents discover them. Migrations live *inside the owning service* (`services/payments/alembic/`), never in a shared top-level dir — migration ownership must track schema ownership. Only use Alembic's `multidb` template when you truly want one coordinated history. For scaffolds, create the `alembic/` dir with `alembic.ini`, `env.py` and an empty `versions/` only if the service declared a DB; don't add SQLAlchemy plumbing the design didn't ask for.

## pytest / ruff / typechecker across members

- **Ruff**: one root `[tool.ruff]` — uniform style aids agents and lets you lint everything without installing member deps. Per-member `extend` only when genuinely needed.
- **pyright or mypy**: either; pin the version in the root dev group. Both need help mapping member src roots in a monorepo — simplest is per-package runs (`uv run --package payments pyright`) or a root config listing `executionEnvironments`/`mypy_path` per member.
- **pytest**: run per-package to avoid cross-member `conftest.py`/basename collisions (`uv run --package payments pytest services/payments`), or set `--import-mode=importlib` with unique package names and run from the root. Wire the fan-out into `just test`.
