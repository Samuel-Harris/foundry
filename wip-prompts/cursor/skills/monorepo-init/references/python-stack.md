# Python stack: uv workspaces + Tach + Import Linter

## uv workspaces

- Make the root `pyproject.toml` virtual:

  ```toml
  [tool.uv]
  package = false

  [tool.uv.workspace]
  members = ["apps/*", "libs/*"]

  [dependency-groups]
  dev = ["pytest>=8", "ruff>=0.8", "pyright>=1.1", "tach>=0.2", "import-linter>=2", "pre-commit>=4"]
  ```

- Give each app and library its own `pyproject.toml`. Inter-member dependencies require both entries:

  ```toml
  [project]
  dependencies = ["contracts"]

  [tool.uv.sources]
  contracts = { workspace = true }
  ```

- Keep one `uv.lock` for the workspace. Use `uv sync --all-packages` for everything and `uv sync --package <name>` for one member.
- Root dependency groups install by default at the root; per-member dev groups do not install automatically across members.
- Set `addopts = "--import-mode=importlib"` in root pytest config and use unique import package names to avoid cross-member collection collisions.
- Use path or Git sources instead of a workspace when a member requires incompatible dependency versions or an independent environment.
- Default every member to src layout. A minimal member:

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

## Tach — declared dependencies and intra-package modules

In a uv workspace where members have their own `pyproject.toml`, Tach treats members as distinct packages. Cross-package imports are governed by `tach check-external`, not by `[[modules]]`, `depends_on`, or `layers` in `tach.toml`. Do not scaffold inert cross-package module entries.

Use `tach check-external` to verify that every workspace and third-party import is declared in the importing member's manifest. It also rejects unused declared dependencies.

```toml
# Cross-package policy is in Import Linter. Tach checks declared dependencies.
source_roots = [
    "services/payments/src",
    "services/orders/src",
    "libs/contracts/src",
    "libs/platform/src",
]
```

A uniform `source_roots = ["**/src"]` is acceptable when every member uses src layout.

Use `[[modules]]`, `layers`, `[[interfaces]]`, and `tach check` only for module structure inside one package or for a single-package modular monolith:

```toml
layers = ["ui", "services", "core"]

[[modules]]
path = "app.web"
layer = "ui"
```

Relevant options include:

- `forbid_circular_dependencies = true`;
- `[[interfaces]]` with `expose`;
- `utility = true` for modules shared by all;
- `exact = true` to reject unused module dependencies;
- `tach sync` to write discovered dependencies;
- `deprecated = true` for migration edges;
- `# tach-ignore` for a single grandfathered import in a retrofit;
- `tach.domain.toml` for local ownership.

Cross-package policy belongs in Import Linter because `check-external` verifies declaredness, not whether an edge is permitted. Both gates are required.

Verify semantics against the installed version with `tach --version`. Deliberately violate each configured rule and observe it fail.

## Import Linter — cross-package policy

Import Linter runs by importing packages, so install the workspace before running `uv run lint-imports`.

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

Higher layers may import lower layers. `a | b` means independent siblings; `a : b` means siblings may import each other. `containers` can repeat an internal layer pattern across services. `exhaustive = true` can reject undeclared modules in a container.

Use a protected contract for public-interface enforcement:

```ini
[importlinter:contract:contracts-public-interface]
name = contracts internals importable only within contracts
type = protected
protected_modules = contracts._schemas
allowed_importers = contracts
```

Do not use a forbidden contract for public-interface enforcement because it follows indirect chains. Other useful contracts:

- `forbidden` for source modules that must not reach forbidden modules, including indirectly;
- `independence` for modules that must never import one another;
- `acyclic siblings` to forbid cycles among siblings.

Keep contract names descriptive because they lead violation output.

## src layout

Default every workspace member to `member/src/pkgname/`. Tests then import the installed editable package, exposing packaging mistakes. It also makes Tach source roots uniform and preserves installable package isolation.

Use a flat layout only for a single, never-published app. Avoid import names that shadow the standard library or popular packages; for example, use `platformlib` for `libs/platform`.

## Alembic placement

Each deployable owns its own `alembic/`, configuration, and `version_table`, even when services share a physical database. Put migrations inside the owning service. Add discoverable `just makemigrations <service>` and `just migrate <service>` wrappers.

Create Alembic files only for services that require a database. Do not add unrequested ORM plumbing.

## pytest, Ruff, and type checking

- Configure Ruff once at the root. Add per-member overrides only for real differences.
- Pin pyright or mypy in the root development group. Use per-package runs or configure execution environments/source paths for each member.
- Run pytest per package when `conftest.py` or basename collisions are possible, or use importlib mode with unique package names.
- Wire all fan-out into the root `justfile`.
