# Cross-cutting scaffold components

Adapt every template to the confirmed design. These examples use Python and uv; add or substitute pnpm and Turborepo commands for TypeScript members.

## Task entry points

Use `just` by default. If the user confirms Make or `just` is unavailable, provide an equivalent Makefile (`.PHONY` targets, tabs). The five canonical recipes are non-negotiable: `test`, `lint`, `typecheck`, `boundaries`, and `check`.

```just
# Canonical commands — agents and humans use these, never raw tool invocations.

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
    # Add `uv run tach check` only when intra-package [[modules]] are configured.

check: lint typecheck test boundaries

fmt:
    uv run ruff format .
    uv run ruff check --fix .
```

Use per-member pytest commands when root collection causes collisions. For a service with a database, add `makemigrations <service>` and `migrate <service>` wrappers so agents discover them. For TypeScript, append `pnpm turbo run lint`, `typecheck`, and `test` to the corresponding recipes.

After writing all source files, run `just fmt` once so the scaffold is format-clean before verification. Heredoc and generated files rarely match `ruff format` exactly, and `just check` includes `ruff format --check`.

## Pre-commit

Use local hooks through the pinned workspace environment — `uv run` avoids version skew with the lockfile. Keep pre-commit fast; leave full tests to CI.

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
      - name: Install (frozen lockfile)
        run: uv sync --all-packages --frozen
      - name: Lint
        run: uv run ruff check . && uv run ruff format --check .
      - name: Typecheck
        run: uv run pyright
      - name: Boundaries (required gate)
        run: |
          uv run tach check-external
          uv run lint-imports
      - name: Tests
        run: uv run pytest services libs
```

Tell the user to configure the `checks` job, or a dedicated boundaries job, as a required branch-protection status check — static boundary enforcement is advisory at runtime, so the CI gate is what makes it real. For TypeScript, install with the frozen pnpm lockfile and run Turborepo tasks, using affected filtering (`pnpm turbo run lint typecheck test --filter='...[origin/main]'`) when the confirmed CI budget requires it.

## CODEOWNERS

Place CODEOWNERS at the root or in `.github/`. Include a catch-all first and own the ownership configuration itself; more-specific later rules override earlier rules.

```text
* @org/maintainers
/.github/ @org/maintainers
/services/payments/ @org/payments-team
/services/orders/ @org/orders-team
/libs/ @org/platform-team
/infra/ @org/platform-team
```

For a single owner, use only the catch-all (`* @username`). For multiple owners, recommend required Code Owner review in branch protection.

## docs/STRUCTURE.md

Emit the following playbook with paths and tools adapted to the selected archetype:

```markdown
# Changing this repository's structure

The layout and boundary rules are intentional but mutable — a starting
contract, not a cage. Follow these playbooks; each ends with `just check`
passing and the root AGENTS.md updated.

## Adding a module or package

1. Create the package: src layout, `tests/`, `pyproject.toml` (with
   `[tool.uv.sources]` entries for workspace dependencies), and AGENTS.md.
2. Register its source root and package with every boundary tool: add its
   `src` to `tach.toml` `source_roots`, add the package to `.importlinter`
   `root_packages` and to the appropriate line of the layers contract (or
   add Nx tags / dependency-cruiser rules for TypeScript packages).
3. Declare only dependencies the package actually imports (`tach
   check-external` fails on both undeclared imports and unused declared
   dependencies).
4. Update CODEOWNERS and the root repository map. Run `just check`.

## Splitting a module

Introduce the new module beside the old one, move code behind stable
interfaces incrementally (strangler-fig), keep boundaries green as you go,
and delete the old path after migration. Enforced boundaries make
extraction largely mechanical.

## Changing a contract or dependency direction — ask first

Add the new allowed edge, migrate imports, and remove the old edge. Use a
documented deprecation or grandfathering mechanism only during migration:
Tach's `deprecated` flag or Import Linter's `ignore_imports` flag new
violations while grandfathering existing ones. Use codemods (libcst /
jscodeshift) for mechanical rewrites, then run `just boundaries` to prove
completion.

## Keeping instructions current

Every structure change updates affected AGENTS.md files in the same change.
CI checks staleness: every top-level package contains an AGENTS.md, and
every command referenced by AGENTS.md exists in the justfile.
```

## Sample module

Create one complete package that agents can copy, demonstrating every convention:

- `libs/<name>/src/<unique-package-name>/` with a unique import-package name;
- 2–3 small, domain-flavoured pure functions (for example, for a payments repo, money rounding in integer minor units) — enough to be real without being business logic;
- package-local tests importing the installed package;
- a declared public interface: a `<package>.api` public module and private implementation (`_impl.py`/`_schemas.py`), enforced by an Import Linter protected contract, or a Tach interface entry in a single-package repository;
- exact manifest dependencies and workspace sources, or TypeScript tags and `exports`;
- package AGENTS.md;
- a root AGENTS.md reference naming it as the pattern to copy for new packages.

Prove its public-interface boundary fails during Phase 3.

## .gitignore and repository initialisation

Include generated and environment paths relevant to the selected stack: `.venv/`, `__pycache__/`, `dist/`, `node_modules/`, `.pytest_cache/`, `.ruff_cache/`, `.turbo/`, and `data/` for the data/ML archetype.

Run `git init` only when the target is not already a repository. Offer an initial commit after verification; never commit unless the user explicitly requests it.
