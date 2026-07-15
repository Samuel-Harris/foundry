# Cross-cutting scaffold components

Adapt every template to the confirmed design. These examples use Python and uv; add or substitute pnpm and Turborepo commands for TypeScript members.

## Task entry points

Use `just` by default. If the user confirms Make or `just` is unavailable, provide equivalent `.PHONY` Makefile targets. Keep `test`, `lint`, `typecheck`, `boundaries`, and `check`.

```just
default: check

install:
    uv sync --all-packages

test:
    uv run pytest services libs

lint:
    uv run ruff check .
    uv run ruff format --check .

typecheck:
    uv run pyright

boundaries:
    uv run tach check-external
    uv run lint-imports
    # Add `uv run tach check` only when intra-package modules are configured.

check: lint typecheck test boundaries

fmt:
    uv run ruff format .
    uv run ruff check --fix .
```

Use per-member pytest commands when root collection causes collisions. For TypeScript, append `pnpm turbo run lint`, `typecheck`, and `test` to the corresponding recipes. Add migration wrappers only for services with databases.

Run `just fmt` once after generating files and before verification.

## Pre-commit

Use local hooks through the pinned workspace environment. Keep pre-commit fast; leave full tests to CI.

```yaml
repos:
  - repo: local
    hooks:
      - id: ruff-check
        name: ruff check
        entry: uv run ruff check --fix
        language: system
        types: [python]
      - id: ruff-format
        name: ruff format
        entry: uv run ruff format
        language: system
        types: [python]
      - id: tach-check-external
        name: tach declared dependencies
        entry: uv run tach check-external
        language: system
        pass_filenames: false
        files: \.py$
      - id: lint-imports
        name: import-linter contracts
        entry: uv run lint-imports
        language: system
        pass_filenames: false
        files: \.py$
```

## CI boundary gate

```yaml
name: ci
on:
  push:
    branches: [main]
  pull_request:

jobs:
  checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - name: Install
        run: uv sync --all-packages --frozen
      - name: Lint
        run: uv run ruff check . && uv run ruff format --check .
      - name: Typecheck
        run: uv run pyright
      - name: Boundaries
        run: |
          uv run tach check-external
          uv run lint-imports
      - name: Tests
        run: uv run pytest services libs
```

Tell the user to configure the checks job, or a dedicated boundaries job, as a required branch-protection check. For TypeScript, install with the frozen pnpm lockfile and run Turborepo tasks, using affected filtering when the confirmed CI budget requires it.

## CODEOWNERS

Place CODEOWNERS at the root or in `.github/`. More-specific later rules override earlier rules. Include a catch-all first and own the ownership configuration itself.

```text
* @org/maintainers
/.github/ @org/maintainers
/services/payments/ @org/payments-team
/services/orders/ @org/orders-team
/libs/ @org/platform-team
/infra/ @org/platform-team
```

For a single owner, use only the catch-all. For multiple owners, recommend required Code Owner review in branch protection.

## docs/STRUCTURE.md

Emit the following playbook with paths and tools adapted to the selected archetype:

```markdown
# Changing this repository's structure

The layout and boundary rules are intentional but mutable. Each playbook ends
with `just check` passing and the root AGENTS.md updated.

## Adding a module or package

1. Create the package with src layout, tests, manifest, workspace sources, and AGENTS.md.
2. Register its source root and package with every boundary tool. Add Nx tags or
   dependency-cruiser rules for TypeScript packages.
3. Declare only dependencies the package actually imports.
4. Update CODEOWNERS and the root repository map. Run `just check`.

## Splitting a module

Introduce the new module beside the old one, move code behind stable interfaces
incrementally, keep boundaries green, and delete the old path after migration.

## Changing a contract or dependency direction — ask first

Add the new allowed edge, migrate imports, and remove the old edge. Use a
documented deprecation or grandfathering mechanism only during migration.
Use codemods for mechanical rewrites, then run `just boundaries`.

## Keeping instructions current

Every structure change updates affected AGENTS.md files in the same change.
CI verifies package instruction files and referenced task-runner commands.
```

## Sample module

Create one complete package that agents can copy. It must include:

- `libs/<name>/src/<unique-package-name>/`;
- 2–3 small domain-flavoured pure functions;
- package-local tests importing the installed package;
- a `<package>.api` public module and private implementation;
- an Import Linter protected contract, or Tach interface in a single-package repository;
- exact manifest dependencies and workspace sources, or TypeScript tags and exports;
- package AGENTS.md;
- a root AGENTS.md reference naming it as the pattern for new packages.

Prove its public-interface boundary fails during Phase 3.

## .gitignore and repository initialisation

Include generated and environment paths relevant to the selected stack: `.venv/`, `__pycache__/`, `dist/`, `node_modules/`, `.pytest_cache/`, `.ruff_cache/`, `.turbo/`, and `data/` for the data/ML archetype.

Run `git init` only when the target is not already a repository. Offer an initial commit after verification; never commit unless the user explicitly requests it.
