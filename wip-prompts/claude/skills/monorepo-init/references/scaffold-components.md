# Cross-cutting scaffold components (liftable templates)

Adapt every template to the confirmed design. Templates below assume the Python/uv stack; add or substitute pnpm/turbo lines when a TS side exists.

## justfile (task entry points)

`just` is the default; if the user prefers `make` or `just` isn't installable, emit an equivalent Makefile (`.PHONY` targets, tabs). The five canonical recipes are non-negotiable: `test`, `lint`, `typecheck`, `boundaries`, `check`.

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
    # add `uv run tach check` only if intra-package [[modules]] are configured

check: lint typecheck test boundaries

fmt:
    uv run ruff format .
    uv run ruff check --fix .
```

Notes: if per-package pytest fan-out is needed (conftest collisions), replace `test` with per-member `uv run --package X pytest <dir>` lines. With a TS side, append `pnpm turbo run lint typecheck test` to the respective recipes. If a service has a DB, add `makemigrations svc:` / `migrate svc:` wrappers here so agents discover them.

After writing all source files, run `just fmt` once so the scaffold is format-clean **before** Phase 3 verification — heredoc/generated files rarely match ruff-format exactly, and `just check` includes `ruff format --check`.

## .pre-commit-config.yaml (fast subset only)

Local hooks via `uv run` avoid version skew with the lockfile. Keep pre-commit fast — full tests belong in CI, not here.

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
        name: tach declared-deps
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

## CI (.github/workflows/ci.yml) — boundary check is a required gate

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

Tell the user to mark the `checks` job (or a dedicated boundaries job) as a **required status check** in branch protection — static Python boundary enforcement is advisory at runtime, so the CI gate is what makes it real. With a TS side add a job (or steps) running `pnpm install --frozen-lockfile` and `pnpm turbo run lint typecheck test --filter='...[origin/main]'` for affected-scoping when CI budget is tight.

## CODEOWNERS

Place at repo root or `.github/`. Later, more-specific rules override earlier ones; always include the catch-all first and own the ownership file itself:

```
* @org/maintainers
/.github/ @org/maintainers
/services/payments/ @org/payments-team
/services/orders/   @org/orders-team
/libs/              @org/platform-team
/infra/             @org/platform-team
```

Single-owner repos: just the catch-all (`* @username`). Recommend enabling "Require review from Code Owners" branch protection when there are multiple owners.

## docs/STRUCTURE.md (the mutation playbook)

The structure is a starting contract, not a cage. Emit this file with the archetype-specific paths filled in:

```markdown
# Changing this repo's structure

The layout and boundary rules are intentional but mutable. Follow these
playbooks; each ends with `just check` green and the root AGENTS.md updated.

## Adding a module/package
1. Create the package: src layout, `tests/`, `pyproject.toml` (with
   `[tool.uv.sources]` entries for workspace deps), AGENTS.md.
2. Register it with the boundary tools: add its `src` to `tach.toml`
   `source_roots`, add the package to `.importlinter` `root_packages` and to
   the appropriate line of the layers contract (or add Nx tags /
   dependency-cruiser rules on the TS side).
3. Declare only the dependencies it actually imports (`tach check-external`
   fails on both undeclared imports AND unused declared deps).
4. Update CODEOWNERS and the root AGENTS.md repo map. Run `just check`.

## Splitting a module
Introduce the new module alongside the old, move code incrementally
(strangler-fig), keep boundaries green as you go, then delete the old path.
Enforced boundaries make extraction largely mechanical.

## Changing a contract / dependency direction  (ASK FIRST)
Add the new allowed edge, migrate imports, then remove the old edge.
During migration use deprecation paths: Tach's `deprecated` flag or
Import Linter's `ignore_imports` flag new violations while grandfathering
existing ones. For mechanical import rewrites use codemods (libcst /
jscodeshift), then re-run `just boundaries` to prove completion.

## Keep instructions in sync
Any structure change must update the affected AGENTS.md files in the same
PR. CI checks staleness (every top-level package has an AGENTS.md; commands
referenced by AGENTS.md exist in the justfile).
```

## The sample module (item 9 of the checklist)

One fully-worked package that demonstrates **every** convention so an agent has a concrete pattern to copy:

- src layout (`libs/<name>/src/<pkg>/`), unique import-package name;
- 2–3 small, domain-flavoured pure functions (e.g. for a payments repo: money rounding in integer minor units) — enough to be real, not business logic;
- colocated `tests/` with passing pytest tests importing the installed package;
- a declared public interface: a `<pkg>.api` module plus internals in a private module (`_impl.py`/`_schemas.py`), enforced by an Import Linter `protected` contract (workspace) or a tach `[[interfaces]]` entry (single-package repo) — and proven to bite in Phase 3;
- correct `dependencies` + `[tool.uv.sources]` (or tags/`exports` on the TS side);
- its own AGENTS.md (per-package template);
- referenced from the root AGENTS.md as "the pattern to copy for new packages".

## .gitignore and git init

Emit a standard `.gitignore` (`.venv/`, `__pycache__/`, `dist/`, `node_modules/`, `.pytest_cache/`, `.ruff_cache/`, `.turbo/`, plus `data/` for Archetype C). Run `git init` if the directory isn't a repo, and offer to create the initial commit once Phase 3 verification is green — never commit before verification.
