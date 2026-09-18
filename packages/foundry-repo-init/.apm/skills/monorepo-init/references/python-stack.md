# Python stack: uv workspaces + Tach + Import Linter

## uv workspaces

- Keep the root `pyproject.toml` virtual, with the workspace members and shared dev tooling at the root:

  ```toml
  [tool.uv]
  package = false

  [tool.uv.workspace]
  members = ["apps/*", "libs/*"]        # or services/*; add exclude = [...] if needed

  [dependency-groups]                    # PEP 735 — shared dev tooling at the root
  dev = ["pytest>=8", "ruff>=0.8", "pyright>=1.1", "tach>=0.2", "import-linter>=2", "pre-commit>=4"]
  ```

- Give each app and library its own `pyproject.toml`. Inter-member dependencies require both entries — omitting the source raises `"...is included as a workspace member, but is missing an entry in tool.uv.sources"`:

  ```toml
  [project]
  dependencies = ["contracts"]

  [tool.uv.sources]
  contracts = { workspace = true }
  ```

- Root `tool.uv.sources` apply to all members unless a member overrides (per-dependency, total).
- Keep one `uv.lock` for the workspace — no version skew. Use `uv sync --all-packages` for everything and `uv sync --package <name>` for one member; member dependencies are always editable. The workspace `requires-python` is the intersection of all members'.
- Root dependency groups install by default at the root; per-member dev groups do not install automatically across members.
- Same-named test files across members collide in pytest collection. Set `addopts = "--import-mode=importlib"` in the root pytest config and give each member a unique import package name.
- Use a workspace when members share a coherent dependency set and are developed together; use path or Git sources instead when a member requires a conflicting dependency version or its own virtual environment.
- Default every member to src layout, using `hatchling` (or uv's default); `uv init --lib` scaffolds it. A minimal member:

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

## Tach (`tach.toml`) — declared dependencies and intra-package modules

Tach is fast (Rust), has no runtime impact, and is incrementally adoptable.

In a uv workspace where members have their own `pyproject.toml`, Tach treats members as distinct packages. Cross-package imports are governed by `tach check-external`, not by `[[modules]]`, `depends_on`, or `layers` in `tach.toml`; cross-package module rules are silently inert. Do not scaffold inert cross-package module entries — config that looks like enforcement but never fires is worse than none.

Use `tach check-external` to verify that every workspace and third-party import is declared in the importing member's manifest. It is bidirectional: an undeclared import fails (`[FAIL] services/orders/src/orders/checkout.py:1: Dependency 'payments' is not declared in package 'orders'.`) and an unused declared dependency also fails — so the scaffold must only declare dependencies each member actually imports. This is the key monorepo win: the shared virtual environment has all dependencies, so an undeclared import passes tests locally but breaks for anyone installing just that package. Config needed: just `source_roots` covering every member's `src` (plus `exclude` if needed):

```toml
# Cross-package policy is in Import Linter. Tach checks declared dependencies.
source_roots = [
    "services/payments/src",
    "services/orders/src",
    "libs/contracts/src",
    "libs/platform/src",
]
```

A uniform `source_roots = ["**/src"]` is acceptable when every member uses src layout. Add a comment in the emitted `tach.toml` explaining the division of labour so future agents do not add inert cross-package modules.

Use `[[modules]]`, `layers`, `[[interfaces]]`, and `tach check` only for module structure inside one package (dotted paths such as `payments.web` → `payments.domain` layers) or for a single-package modular monolith with no member manifests:

```toml
layers = ["ui", "services", "core"]

[[modules]]
path = "app.web"
layer = "ui"
```

Relevant options include:

- `forbid_circular_dependencies = true`;
- `[[interfaces]]` with `expose` (`expose = ["api.*"] from = [...]`);
- `utility = true` for modules shared by all;
- `exact = true` to reject unused module dependencies;
- `tach sync` to write discovered dependencies;
- `deprecated = true` for migration edges;
- `# tach-ignore` for a single grandfathered import in a retrofit;
- `tach.domain.toml` for local ownership.

Cross-package policy belongs in Import Linter because `check-external` verifies declaredness, not whether an edge is permitted. Both gates are required: an agent that adds the forbidden package to `pyproject.toml` sails through `check-external` and must be stopped by the Import Linter contract. The fence test in Phase 3 must try both attacks.

Verify semantics against the installed version with `tach --version`; the config schema and package semantics have changed across versions. If a boundary rule has never been seen failing, treat it as unproven: deliberately violate each configured rule once and watch it fail.

## Import Linter (`.importlinter`) — cross-package policy and intra-package architecture

Import Linter runs by importing packages, so install the workspace before running `uv run lint-imports`. In a uv workspace it encodes which member may import which.

Use a layers contract for one-way package direction and independent siblings:

```ini
[importlinter]
root_packages =
    payments
    orders
    contracts
    platformlib
include_external_packages = True

[importlinter:contract:package-layers]
name = Package layers: services independent above platform and contracts
type = layers
layers =
    payments | orders
    platformlib
    contracts
```

Higher layers may import lower layers. `a | b` means independent siblings; `a : b` means siblings may import each other. One layers contract can therefore express both service independence and library direction. Violation output names the contract and shows the exact import chain with line numbers, so it is agent-legible. `containers` can repeat an internal layer pattern across sibling services; optional layers are marked `(medium)`; `exhaustive = true` (with `exhaustive_ignores`) can reject undeclared modules in a container.

Use a protected contract for public-interface enforcement:

```ini
[importlinter:contract:contracts-public-interface]
name = contracts internals importable only within contracts (use contracts.api)
type = protected
protected_modules = contracts._schemas
allowed_importers = contracts
```

Do not use a forbidden contract for public-interface enforcement because it follows indirect chains, so `payments → contracts.api → contracts._schemas` counts as a violation even though payments only touched the public interface.

Other useful contracts:

- `forbidden` for source modules that must not reach forbidden modules, including indirectly — with `include_external_packages = True` this covers third-party packages, for example forbidding `requests` or `boto3` in a pure schemas layer, or quarantining `notebooks/` from pipelines;
- `independence` for modules that must never import one another in any direction (an alternative to `|` siblings when the modules are not in a layer stack);
- `acyclic siblings` to forbid cycles among siblings.

Keep contract names descriptive because they are the first line of the violation output an agent sees.

## src layout

Default every workspace member to `member/src/pkgname/`. `src/` is not on `sys.path`, so tests import the installed editable package, exposing packaging mistakes (missing files, wrong package name) before release; it also makes Tach source roots uniform (`source_roots = ["**/src"]`) and makes each member a real, isolated installable unit.

Use a flat layout only for a single, never-published app. Avoid import names that shadow the standard library or popular packages (`platform`, `types`, `email`, ...); for example, use `platformlib` for `libs/platform`. Give every member a unique import name to avoid pytest collection collisions.

## Alembic placement

Each deployable owns its own `alembic/` directory, its own configuration (`alembic.ini` or a `--name` section), and its own `version_table`, even when services share a physical database, so histories never collide. Put migrations inside the owning service (`services/payments/alembic/`), never in a shared top-level directory — migration ownership must track schema ownership. Add discoverable `just makemigrations <service>` and `just migrate <service>` wrappers.

Create Alembic files only for services that require a database: create the `alembic/` directory with `alembic.ini`, `env.py`, and an empty `versions/` only if the service declared a database. Do not add unrequested ORM plumbing. Use Alembic's `multidb` template only when you genuinely want one coordinated history.

## pytest, Ruff, and type checking

- Configure Ruff once at the root: one `[tool.ruff]` gives uniform style and lets you lint everything without installing member dependencies. Add per-member `extend` overrides only for real differences.
- Pin pyright or mypy in the root development group. Both need help mapping member `src` roots in a monorepo, so use per-package runs (`uv run --package payments pyright`) or a root config listing `executionEnvironments`/`mypy_path` per member.
- Run pytest per package when `conftest.py` or basename collisions are possible (`uv run --package payments pytest services/payments`), or set `--import-mode=importlib` with unique package names and run from the root.
- Wire all fan-out into the root `justfile` (`just test`).
