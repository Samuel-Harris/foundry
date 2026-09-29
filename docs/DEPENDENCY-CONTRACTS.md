# Dependency and manifest contracts

This document records the manifest shape each package uses, how sibling packages resolve, and the exact behaviour of the pinned APM CLI that CI depends on.

## Tested CLI

`apm-cli==0.32.0`, installed from PyPI. Never run `apm self-update`; the version is pinned deliberately so that lockfile resolution and deployment behaviour are reproducible.

## Package manifest contract

Every package declares the following keys in `apm.yml`:

```yaml
name: planning
version: "0.1.0"
description: "Plan authoring and plan review."
author: sam
license: MIT
repository: https://github.com/Samuel-Harris/foundry
targets:
  - cursor
  - claude
  - copilot
includes: auto
dependencies:
  apm:
    - path: ../architect
    - path: ../deep-interview
    - path: ../review
    - path: ../swarm
scripts:
  check: apm audit --ci
```

Rules that apply to every package:

- Use the plural `targets:` key. Never declare both `target:` and `targets:`.
- Quote `version`. YAML parses a bare two-component version such as `1.10` as the float `1.1`, so quoting keeps the declared string exact.
- Declare `dependencies: {}` explicitly even when empty. `apm pack` uses the presence of the mapping to select bundle output.
- The only permitted target values here are `cursor`, `claude` and `copilot`. They are always passed explicitly; filesystem auto-detection is never relied upon, and no tool-specific directories are created merely to influence detection.
- Quote any `description` that contains a colon. An unquoted `:` followed by a space makes the whole manifest unparseable, and every command fails with `Failed to parse apm.yml: Invalid YAML format ... mapping values are not allowed here`. The description is not silently dropped — nothing works. Use a quoted YAML scalar (`json.dumps` output is always valid).

## Sibling dependencies

Packages in this repository depend on each other through a **sibling relative path**:

```yaml
dependencies:
  apm:
    - path: ../planning
```

This is the documented same-repo sibling mechanism. Do not write `git: <parent repo>` as a substitute.

**Verified, not assumed, and only partly viable.** Installing `packages/pr` resolved `../swarm (local)` and, transitively, `../architect`, then deployed both packages' agents and skills alongside `pr`'s own three skills. The `path:` form is therefore correct for development and for consumers that resolve the package from the parent repository.

It is **not** viable for `apm pack`. The CLI refuses to bundle a local path dependency in every format:

```text
$ apm pack --dry-run --verbose           # in packages/swarm
Error: Cannot pack — apm.yml contains local path dependency: ../architect
Local dependencies are for development only. Replace them with remote references (e.g., 'owner/repo') before packing.
```

The remote `{git, path, ref}` form was tested against it and fails for the opposite reason. With `ref: "^0.1.0"` and no release tag pushed, a real install stops:

```text
$ apm install --target cursor            # with {git: Samuel-Harris/foundry, path: packages/planning, ref: "^0.1.0"}
[x] 1 package failed:
  +- foundry-planning -- No matching tag for Samuel-Harris/foundry: No tags on
     Samuel-Harris/foundry satisfy '^0.1.0'. The remote has no tag refs.
```

The CLI prefixes the failing dependency's identifier with the repository name, so the error names `foundry-planning` while the manifest path is `packages/planning`.

So no single manifest form satisfies both `apm install` (which needs `path:`) and `apm pack` (which needs a resolvable remote ref) before `v0.1.0` exists. This repository keeps `path:`, because publication is out of scope and install, `--frozen` and `audit --ci` must stay green for every package that can have them green. Bundle production for the nine dependency-bearing packages — `default-stack`, `deep-interview`, `execution`, `planning`, `pr`, `repo-init`, `repo-maintenance`, `skill-creation` and `swarm` — is deferred to a release job that runs after the tag is pushed, at which point the remote form becomes usable. CI asserts the guardrail for those packages rather than skipping them.

Consumers never use the sibling form. A consumer declares a remote dependency:

```yaml
dependencies:
  apm:
    - git: Samuel-Harris/foundry
      path: packages/planning
      ref: "v0.1.0"
```

or uses the shorthand install command:

```bash
apm install Samuel-Harris/foundry/packages/planning#v0.1.0 --target cursor,claude,copilot
```

A remote install requires the `v0.1.0` tag to exist and the consumer to have repository access.

## The meta-package

`packages/default-stack/apm.yml` lists eight sibling packages as `- path: ../<name>` entries and therefore omits `dependencies: {}`, which is non-empty. Installing `packages/default-stack` is the one-command route to the default stack.

Those eight direct dependencies pull in four more transitively, so a single meta-package install resolves twelve packages:

```text
default-stack
├── coding-style
├── execution        -> pr, review
├── git-diff
├── planning         -> architect, deep-interview, review, swarm
├── pr               -> explore
├── repo-maintenance -> explore
├── review
└── skill-creation   -> deep-interview, repo-maintenance

transitively added: architect, swarm, deep-interview, explore
```

`architect`, `handoff`, `infrastructure`, `repo-init`, `search` and `ui` are intentionally not part of the default stack; install them individually.

There is deliberately **no `apm.yml` at the repository root**. Root-level compile and pack discovery walks the whole tree, so a root manifest would absorb the nested packages' `.apm/` trees into one package and destroy the per-package boundaries.

## Lockfiles

- Commit `apm.lock.yaml` per package once generated.
- Never hand-author or hand-edit hashes or pins. Regenerate with `apm lock` or `apm install`.
- `apm install --frozen` reproduces the lockfile exactly and is the CI-safe form.
- `apm audit --ci` is the release gate.
- **A transitive sibling dependency records an absolute path, which is inert.** Direct local dependencies are pinned as `local_path: ../<name>`, which is portable, but a local dependency reached transitively (for example `architect` via `swarm`) additionally records `anchored_local_path: /absolute/path/to/packages/<name>`. Because the committed lockfiles were generated on the authoring machine, they carry that machine's path. Verified: copying the tree to a different absolute root leaves `apm install --frozen` and `apm audit --ci` green, and a plain `apm install` rewrites `anchored_local_path` to the new location. So the recorded path does not pin the lockfile to a machine, and CI does not need to regenerate it.

## Generated-file policy

Per-target deploy output (`.cursor/`, `.claude/`, `.agents/`, `.github/agents/`, `.github/instructions/`) is build output and is never committed; `.gitignore` excludes it. Lockfiles and `apm.yml` are source and are committed. `.github/workflows/` stays tracked, so `.github/` is never ignored wholesale.

## External prerequisites (not declared as dependencies)

The Linear MCP server is required at runtime by `masterplan` and `implement-linear-ticket`. It is **not** declared under `dependencies.mcp`:

- no resolvable Linear APM package has been verified to exist, and claiming a resolved dependency that cannot be resolved would be false;
- APM does not sandbox MCP servers, so declaring one would imply a safety guarantee that does not hold.

The server is documented as a runtime prerequisite instead, and `implement-linear-ticket` stops with an actionable error when it is absent.

## Cross-package references

Every primitive that names a primitive shipped by another package is covered by a declared dependency edge. The graph is acyclic and no reference is left dangling.

| Reference               | Declared in                                                     | Ships in           | Covering edge                     |
| ----------------------- | --------------------------------------------------------------- | ------------------ | --------------------------------- |
| `architect`             | `planning` — the `ralplan` skill                                | `architect`        | planning → architect              |
| `architect`             | `swarm` — the `swarm` skill                                     | `architect`        | swarm → architect                 |
| `explore`               | `swarm` — the `swarm` skill                                     | `explore`          | swarm → explore                   |
| `explore`               | `deep-interview` — the `deep-interview` skill                   | `explore`          | deep-interview → explore          |
| `explore`               | `pr` — the `code-tour` skill                                    | `explore`          | pr → explore                      |
| `explore`               | `repo-maintenance` — the `agents-md` skill                      | `explore`          | repo-maintenance → explore        |
| `thermos`               | `execution` — the `implement-linear-ticket` skill               | `review`           | execution → review                |
| `thermos`               | `planning` — the `plan-handoff-standard` instruction            | `review`           | planning → review                 |
| `babysit`               | `execution` — the `implement-linear-ticket` skill               | `pr`               | execution → pr                    |
| `deep-interview`        | `planning` — `masterplan`, `ralplan` and `plan-handoff-standard` | `deep-interview`   | planning → deep-interview         |
| `deep-interview`        | `skill-creation` — the `design-skill` skill                     | `deep-interview`   | skill-creation → deep-interview   |
| `deep-interview`        | `repo-init` — the `terraform-monorepo-init` skill               | `deep-interview`   | repo-init → deep-interview        |
| `optimise-agent-config` | `skill-creation` — the `design-skill` skill                     | `repo-maintenance` | skill-creation → repo-maintenance |

`planning`'s `ralplan` treats its handoff to `swarm` as optional, and `plan-handoff-standard` treats its `thermos` step as required; both are satisfied by the edges above, so a single-package install of `planning` carries the capability its own text names.

### Why `architect`, `explore` and `deep-interview` exist

Both `planning` and `swarm` need the `architect` agent, and each references it directly. Keeping `architect` inside either package would force one of them to depend on the other for a read-only analysis agent, coupling the planning and execution layers. `architect` is therefore extracted into a dedicated `architect` package that both depend on, and `swarm` no longer names any primitive owned by `planning` (its `swarm` skill takes "a validated plan" as input rather than naming the producing skill).

The same reasoning extracts `explore` and `deep-interview`. `swarm`, `deep-interview`, `pr` and `repo-maintenance` all dispatch the `explore` agent. Keeping that agent inside `swarm` forced `pr` and `repo-maintenance` to depend on `swarm`, and therefore to receive the `swarm` skill and the executor and build-fixer agents they never name. `planning`, `skill-creation` and `repo-init` all name the `deep-interview` skill. Keeping that skill inside `planning` forced `skill-creation` to depend on `planning` for nothing else, and stopped `repo-init` from declaring the dependency at all, because `planning` would have dragged in `architect`, `review` and `swarm`. `deep-interview` depends on `explore` because the skill dispatches that agent.

That orientation is what keeps the graph acyclic:

```text
repo-init --> deep-interview --> explore
skill-creation --> deep-interview
skill-creation --> repo-maintenance --> explore
planning --> deep-interview
planning --> swarm --> explore
planning --> swarm --> architect
planning --> architect
planning --> review
execution --> pr --> explore
execution --> review
```

APM cannot express a dependency cycle, so any future reference that points backwards along `planning → swarm → architect` or `deep-interview → explore` must be reworded or extracted, not declared.

No test asserts that these references resolve inside a single-package install: `tests/structural/validate_primitives.py` checks that relative links resolve on disk **within this repository**, not across package boundaries. The edges above were derived by scanning every primitive for references to primitives owned by another package.

## APM 0.32.0 CLI behaviour that CI depends on

### `apm compile --validate` fails on skill-only packages until an install has run

`apm compile --validate` requires at least one agent or instruction in `.apm/`. On a package whose `.apm/` contains only `skills/`, it exits `1`:

```text
$ apm compile --validate        # clean checkout of a skill-only package
[x] No instruction files found in .apm/ directory
[i]  To add instructions, create files like:
[i]    .apm/instructions/coding-standards.instructions.md
[i]    .apm/agents/backend-engineer.agent.md
```

After `apm install` has materialised the deploy targets, the same command exits `0` and reports `Validated 0 primitives` — it still inspects no skill. Declaring `type: skill` in the manifest changes neither outcome.

Two consequences:

- CI must run `apm install` **before** `apm compile --validate`. The reverse order fails every skill-only package.
- `apm compile --validate` is not a meaningful gate for skill-only packages. `tests/structural/validate_primitives.py` is the real frontmatter and sibling-file contract, and `apm audit --ci` covers deployment integrity.

Where it does run, it counts agents (reported as `chatmodes`) and instructions; it does not inspect skills and does not enforce frontmatter fields, so an agent with no `description` still reports success.

### `apm pack` rejects local path dependencies

`apm pack` refuses any manifest that declares a local `path:` dependency, in every bundle format (`plugin`, `apm`, `agent-plugin`):

```text
Error: Cannot pack — apm.yml contains local path dependency: ../planning
Local dependencies are for development only. Replace them with remote references (e.g., 'owner/repo') before packing.
```

This is the reason every package with a sibling `path:` dependency cannot be packed before `v0.1.0` is tagged: `default-stack`, `deep-interview`, `execution`, `planning`, `pr`, `repo-init`, `repo-maintenance`, `skill-creation` and `swarm`. The sibling section above records the full comparison and the tested remote fallback.

### `apm audit --ci` cannot replay a lockfile with a duplicated local `resolved_by` parent

This is an APM lockfile-writer defect, re-checked on the pinned 0.32.0 CLI. A clean `apm install` of `packages/default-stack` still writes the duplicate, and `apm audit --ci` still fails with the same signature. It makes that package the one whose own lockfile fails its own audit.

**Trigger.** A local package is reachable by **two** paths from the same manifest (once directly, once transitively) **and** is itself the `resolved_by` parent of another local package. `apm install` then writes two entries with the same `repo_url`, and the drift replay cannot decide which one parents the grandchild. In `default-stack`, `pr` is both a direct dependency and a transitive one (via `execution`), and it parents `explore`. `repo-maintenance` is also reached both directly and via `skill-creation`, but the lockfile records `explore`'s parent as `pr`, so the failure that surfaces names `pr`:

```text
$ apm audit --ci          # in packages/default-stack
config-consistency  | 1 MCP config inconsistenc(ies) -- run 'apm install' to reconcile
drift               | drift replay failed: corrupt local dependency graph in the lockfile
                    | (ambiguous resolved_by parent '_local/pr' of
                    | '_local/explore': 2 local dependencies share that repo_url
                    | (['../pr', '../pr'])). Fix the
                    | resolved_by chain or re-run 'apm install'.

[x] 2 of 8 check(s) failed
```

Re-running `apm install` rewrites the identical duplicate, so the suggested remedy does not help.

**Minimal repro, with no Foundry code involved.** Four local packages — `leaf`, `base` (depends on `leaf`), `mid` (depends on `base`) and `meta` (depends on `base` and `mid`) — reproduce it exactly:

```text
$ apm install --target claude          # in meta/
$ apm audit --ci
config-consistency details:
  - local:/path/packages/leaf: cannot resolve local package: ambiguous resolved_by
    parent '_local/base' of '_local/leaf': 2 local dependencies share that repo_url
    (['../base', '../base']); re-run 'apm install' to rebuild the lockfile
```

Two levels are not enough: `meta → {base, mid → base}` alone audits clean. The failure needs the duplicated package to have a child of its own.

**Scope.** Only the package's own lockfile is affected. All twelve packages still resolve and deploy — consumer-side installs of `default-stack` pass `apm audit --ci` on `cursor`, `claude` and `copilot`, and `apm install --frozen` succeeds in place. Both are asserted by `tests/structural/run-tier1.sh` and CI.

**Handling.** The manifest keeps its eight declared requirements rather than dropping the direct edges that duplicate a transitive path (`pr`, also reached via `execution`, and `repo-maintenance`, also reached via `skill-creation`). Dropping those direct edges would state the default stack's contents only indirectly, so its contract would silently change whenever a sibling's dependencies change. Instead the defect is asserted: the suite and CI fail if `default-stack`'s audit *passes* or if it fails with a different message, so a fix in a later APM release is noticed rather than silently tolerated.

### Plugin-format archives do not translate instruction frontmatter

`apm pack --archive` emits a Claude plugin bundle. Installing it deploys the expected file inventory, but per-target instruction translation is not applied: `.cursor/rules/*.mdc` keeps `applyTo` instead of gaining `globs`, and `.claude/rules/*.md` keeps `applyTo` instead of gaining `paths`. Archive-based CI asserts inventory, sibling-file presence and tamper rejection; scoping translation is asserted from the source installs. `apm pack --format apm` is not a substitute: it reports `No deployed files found -- empty bundle created` and writes only the embedded lockfile.

### Skills are never structurally validated by APM

`apm pack` bundles a `SKILL.md` with no `description`, invalid YAML, or a `name` that disagrees with its directory, and `apm install` deploys it. APM 0.32.0 has no skill frontmatter gate. `tests/structural/validate_primitives.py` fills that gap in CI.

### `apm install` does not validate primitives it deploys

`apm install --dry-run` at a package root resolves that package's *dependencies*; it does not validate the package's own primitives. Primitive-level verification therefore lives in the scratch-consumer and archive-consumer CI jobs, which assert the deployed inventory.

### Delivery is not a safety statement

`apm audit --ci` reports content integrity and drift. It is not a security certification, and APM does not sandbox MCP servers.
