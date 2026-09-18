# Dependency and manifest contracts

This document records the manifest shape each package uses, how sibling packages resolve, and the exact behaviour of the pinned APM CLI that CI depends on.

## Tested CLI

`apm-cli==0.30.0`, installed from PyPI. Never run `apm self-update`; the version is pinned deliberately so that lockfile resolution and deployment behaviour are reproducible.

## Package manifest contract

Every package declares the following keys in `apm.yml`:

```yaml
name: foundry-planning
version: "0.1.0"
description: "Socratic requirement gathering, plan authoring and plan review."
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
    - path: ../foundry-architect
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
    - path: ../foundry-planning
```

This is the documented same-repo sibling mechanism. Do not write `git: <parent repo>` as a substitute.

**Verified, not assumed, and only partly viable.** Installing `packages/foundry-pr` resolved `../foundry-swarm (local)` and, transitively, `../foundry-architect`, then deployed both packages' agents and skills alongside `foundry-pr`'s own three skills. The `path:` form is therefore correct for development and for consumers that resolve the package from the parent repository.

It is **not** viable for `apm pack`. The CLI refuses to bundle a local path dependency in every format:

```text
$ apm pack --dry-run --verbose           # in packages/foundry-swarm
Error: Cannot pack — apm.yml contains local path dependency: ../foundry-architect
Local dependencies are for development only. Replace them with remote references (e.g., 'owner/repo') before packing.
```

The remote `{git, path, ref}` form was tested against it and fails for the opposite reason. With `ref: "^0.1.0"` and no release tag pushed, a real install stops:

```text
$ apm install --target cursor            # with {git: Samuel-Harris/foundry, path: packages/foundry-planning, ref: "^0.1.0"}
[x] 1 package failed:
  +- foundry-foundry-planning -- No matching tag for Samuel-Harris/foundry: No tags on
     Samuel-Harris/foundry satisfy '^0.1.0'. The remote has no tag refs.
```

So no single manifest form satisfies both `apm install` (which needs `path:`) and `apm pack` (which needs a resolvable remote ref) before `v0.1.0` exists. This repository keeps `path:`, because publication is out of scope and install, `--frozen` and `audit --ci` must stay green for every package that can have them green. Bundle production for the seven dependency-bearing packages is deferred to a release job that runs after the tag is pushed, at which point the remote form becomes usable. CI asserts the guardrail for those packages rather than skipping them.

Consumers never use the sibling form. A consumer declares a remote dependency:

```yaml
dependencies:
  apm:
    - git: Samuel-Harris/foundry
      path: packages/foundry-planning
      ref: "v0.1.0"
```

or uses the shorthand install command:

```bash
apm install Samuel-Harris/foundry/packages/foundry-planning#v0.1.0 --target cursor,claude,copilot
```

A remote install requires the `v0.1.0` tag to exist and the consumer to have repository access.

## The meta-package

`packages/foundry-default-stack/apm.yml` lists eight sibling packages as `- path: ../<name>` entries and therefore omits `dependencies: {}`, which is non-empty. Installing `packages/foundry-default-stack` is the one-command route to the default stack.

Those eight direct dependencies pull in two more transitively, so a single meta-package install resolves ten packages:

```text
foundry-default-stack
├── foundry-coding-style
├── foundry-execution      -> foundry-pr, foundry-review
├── foundry-git-diff
├── foundry-planning       -> foundry-swarm, foundry-review, foundry-architect
├── foundry-pr             -> foundry-swarm
├── foundry-repo-maintenance -> foundry-swarm
├── foundry-review
└── foundry-skill-creation -> foundry-planning, foundry-repo-maintenance

transitively added: foundry-swarm, foundry-architect
```

`foundry-architect`, `foundry-handoff`, `foundry-infrastructure`, `foundry-repo-init`, `foundry-search` and `foundry-ui` are intentionally not part of the default stack; install them individually.

There is deliberately **no `apm.yml` at the repository root**. Root-level compile and pack discovery walks the whole tree, so a root manifest would absorb the nested packages' `.apm/` trees into one package and destroy the per-package boundaries.

## Lockfiles

- Commit `apm.lock.yaml` per package once generated.
- Never hand-author or hand-edit hashes or pins. Regenerate with `apm lock` or `apm install`.
- `apm install --frozen` reproduces the lockfile exactly and is the CI-safe form.
- `apm audit --ci` is the release gate.
- **A transitive sibling dependency records an absolute path, which is inert.** Direct local dependencies are pinned as `local_path: ../<name>`, which is portable, but a local dependency reached transitively (for example `foundry-architect` via `foundry-swarm`) additionally records `anchored_local_path: /absolute/path/to/packages/<name>`. Because the committed lockfiles were generated on the authoring machine, they carry that machine's path. Verified: copying the tree to a different absolute root leaves `apm install --frozen` and `apm audit --ci` green, and a plain `apm install` rewrites `anchored_local_path` to the new location. So the recorded path does not pin the lockfile to a machine, and CI does not need to regenerate it.

## Generated-file policy

Per-target deploy output (`.cursor/`, `.claude/`, `.agents/`, `.github/agents/`, `.github/instructions/`) is build output and is never committed; `.gitignore` excludes it. Lockfiles and `apm.yml` are source and are committed. `.github/workflows/` stays tracked, so `.github/` is never ignored wholesale.

## External prerequisites (not declared as dependencies)

The Linear MCP server is required at runtime by `masterplan` and `implement-linear-ticket`. It is **not** declared under `dependencies.mcp`:

- no resolvable Linear APM package has been verified to exist, and claiming a resolved dependency that cannot be resolved would be false;
- APM does not sandbox MCP servers, so declaring one would imply a safety guarantee that does not hold.

The server is documented as a runtime prerequisite instead, and `implement-linear-ticket` stops with an actionable error when it is absent.

## Cross-package references

Every primitive that names a primitive shipped by another package is covered by a declared dependency edge. The graph is acyclic and no reference is left dangling.

| Reference               | Declared in                                                             | Ships in                   | Covering edge                     |
| ----------------------- | ----------------------------------------------------------------------- | -------------------------- | --------------------------------- |
| `architect`             | `foundry-planning` — the `ralplan` skill                                | `foundry-architect`        | planning → architect              |
| `architect`             | `foundry-swarm` — the `swarm` skill                                     | `foundry-architect`        | swarm → architect                 |
| `explore`               | `foundry-planning` — the `deep-interview` skill and the `planner` agent | `foundry-swarm`            | planning → swarm                  |
| `explore`               | `foundry-repo-maintenance` — the `agents-md` skill                      | `foundry-swarm`            | repo-maintenance → swarm          |
| `explore`               | `foundry-pr` — the `code-tour` skill                                    | `foundry-swarm`            | pr → swarm                        |
| `thermos`               | `foundry-execution` — the `implement-linear-ticket` skill               | `foundry-review`           | execution → review                |
| `thermos`               | `foundry-planning` — the `plan-handoff-standard` instruction            | `foundry-review`           | planning → review                 |
| `babysit`               | `foundry-execution` — the `implement-linear-ticket` skill               | `foundry-pr`               | execution → pr                    |
| `deep-interview`        | `foundry-skill-creation` — the `design-skill` skill                     | `foundry-planning`         | skill-creation → planning         |
| `optimise-agent-config` | `foundry-skill-creation` — the `design-skill` skill                     | `foundry-repo-maintenance` | skill-creation → repo-maintenance |

`foundry-planning`'s `ralplan` treats its handoff to `swarm` as optional, and `plan-handoff-standard` treats its `thermos` step as required; both are satisfied by the edges above, so a single-package install of `foundry-planning` carries the capability its own text names.

### Why `foundry-architect` exists

Both `foundry-planning` and `foundry-swarm` need the `architect` agent, and each references it directly. Keeping `architect` inside either package would force one of them to depend on the other for a read-only analysis agent, coupling the planning and execution layers. `architect` is therefore extracted into `foundry-architect`, a 1-agent package that both depend on, and `foundry-swarm` no longer names any primitive owned by `foundry-planning` (its `swarm` skill takes "a validated plan" as input rather than naming the producing skill).

That orientation is what keeps the graph acyclic:

```text
foundry-skill-creation -> foundry-planning -> foundry-swarm -> foundry-architect
                              |                    ^
                              v                    |
                        foundry-review     foundry-repo-maintenance
```

APM cannot express a dependency cycle, so any future reference that points backwards along `skill-creation → planning → swarm → architect` must be reworded or extracted, not declared.

No test asserts that these references resolve inside a single-package install: `tests/structural/validate_primitives.py` checks that relative links resolve on disk **within this repository**, not across package boundaries. The edges above were derived by scanning every primitive for references to primitives owned by another package.

## APM 0.30.0 CLI behaviour that CI depends on

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
Error: Cannot pack — apm.yml contains local path dependency: ../foundry-planning
Local dependencies are for development only. Replace them with remote references (e.g., 'owner/repo') before packing.
```

This is the reason every package with a sibling `path:` dependency cannot be packed before `v0.1.0` is tagged: `foundry-default-stack`, `foundry-execution`, `foundry-planning`, `foundry-pr`, `foundry-repo-maintenance`, `foundry-skill-creation` and `foundry-swarm`. The sibling section above records the full comparison and the tested remote fallback.

### `apm audit --ci` cannot replay a lockfile with a duplicated local `resolved_by` parent

This is an APM 0.30.0 lockfile-writer defect. It makes `packages/foundry-default-stack` the one package here whose own lockfile fails its own audit.

**Trigger.** A local package is reachable by **two** paths from the same manifest (once directly, once transitively) **and** is itself the `resolved_by` parent of another local package. `apm install` then writes two entries with the same `repo_url`, and the drift replay cannot decide which one parents the grandchild. In `foundry-default-stack`, `foundry-planning` is both a direct dependency and a transitive one (via `foundry-skill-creation`), and it parents `foundry-architect` and `foundry-swarm`:

```text
$ apm audit --ci          # in packages/foundry-default-stack
config-consistency  | 2 MCP config inconsistenc(ies) -- run 'apm install' to reconcile
drift               | drift replay failed: corrupt local dependency graph in the lockfile
                    | (ambiguous resolved_by parent '_local/foundry-planning' of
                    | '_local/foundry-architect': 2 local dependencies share that repo_url
                    | (['../foundry-planning', '../foundry-planning'])). Fix the
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

**Scope.** Only the package's own lockfile is affected. All ten packages still resolve and deploy — consumer-side installs of `foundry-default-stack` pass `apm audit --ci` on `cursor`, `claude` and `copilot`, and `apm install --frozen` succeeds in place. Both are asserted by `tests/structural/run-tier1.sh` and CI.

**Handling.** The manifest keeps its eight declared requirements rather than being trimmed to the non-duplicating subset (`foundry-coding-style`, `foundry-execution`, `foundry-git-diff`, `foundry-skill-creation`). That subset does audit cleanly and still resolves all ten packages, but it states the default stack's contents only indirectly, so its contract would silently change whenever a sibling's dependencies change. Instead the defect is asserted: the suite and CI fail if `foundry-default-stack`'s audit *passes* or if it fails with a different message, so a fix in a later APM release is noticed rather than silently tolerated.

### Plugin-format archives do not translate instruction frontmatter

`apm pack --archive` emits a Claude plugin bundle. Installing it deploys the expected file inventory, but per-target instruction translation is not applied: `.cursor/rules/*.mdc` keeps `applyTo` instead of gaining `globs`, and `.claude/rules/*.md` keeps `applyTo` instead of gaining `paths`. Archive-based CI asserts inventory, sibling-file presence and tamper rejection; scoping translation is asserted from the source installs. `apm pack --format apm` is not a substitute: it reports `No deployed files found -- empty bundle created` and writes only the embedded lockfile.

### Skills are never structurally validated by APM

`apm pack` bundles a `SKILL.md` with no `description`, invalid YAML, or a `name` that disagrees with its directory, and `apm install` deploys it. APM 0.30.0 has no skill frontmatter gate. `tests/structural/validate_primitives.py` fills that gap in CI.

### `apm install` does not validate primitives it deploys

`apm install --dry-run` at a package root resolves that package's *dependencies*; it does not validate the package's own primitives. Primitive-level verification therefore lives in the scratch-consumer and archive-consumer CI jobs, which assert the deployed inventory.

### Delivery is not a safety statement

`apm audit --ci` reports content integrity and drift. It is not a security certification, and APM does not sandbox MCP servers.
