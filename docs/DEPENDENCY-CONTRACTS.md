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
    - path: ../deep-interview
    - path: ../review
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

**Verified, not assumed, and only partly viable.** Before the `swarm` and `architect` packages were removed, installing `packages/pr` resolved `../swarm (local)` and, transitively, `../architect`, then deployed both packages' agents and skills alongside `pr`'s own three skills. The `path:` form is therefore correct for development and for consumers that resolve the package from the parent repository.

It is **not** viable for `apm pack`. The CLI refuses to bundle a local path dependency in every format:

```text
$ apm pack --dry-run --verbose           # in packages/planning
Error: Cannot pack — apm.yml contains local path dependency: ../deep-interview
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

So no single manifest form satisfies both `apm install` (which needs `path:`) and `apm pack` (which needs a resolvable remote ref) before `v0.1.0` exists. This repository keeps `path:` permanently, not only until the tag exists, because a remote install already resolves it correctly (see below) and the remote form would pin every sibling to a tag, so a change spanning two packages could not be tested on a feature branch. Bundle production for the six packages with sibling `path:` dependencies — `default-stack`, `execution`, `planning`, `repo-init`, `s-stack` and `skill-creation` — is deferred until bundles are needed; a release job would then rewrite a throwaway copy of each manifest to `{git: Samuel-Harris/foundry, path: packages/<name>, ref: <tag>}` and pack that. The local Tier 1 suite asserts the guardrail for those packages rather than skipping them.

**A remote install rewrites sibling paths to the same repository and commit.** When APM fetches a package from a git remote, it expands each `path: ../<name>` dependency into a dependency on `packages/<name>` in the same repository at the same resolved commit (`_expand_remote_parent_local_path` in `apm_cli/deps/apm_resolver.py`); a path that escapes the repository root is rejected. Verified with 0.32.0: `apm install Samuel-Harris/foundry/packages/swarm#main` in an empty directory resolved `swarm`, `architect` and, transitively, `explore` all at `main @c00c862a`, and the consumer's lockfile records only `virtual_path: packages/<name>` with `resolved_ref: main`, with no local or absolute path. A consumer therefore gets mutually consistent packages from one tag or branch.

To test a feature branch end to end, push it and install from it in an empty directory:

```bash
apm install Samuel-Harris/foundry/packages/<name>#<branch> --target cursor,claude,copilot
```

Every sibling then resolves to the branch's commit. Before pushing, `bash tests/structural/run-tier1.sh` exercises the same dependency graph against the working tree.

Consumers never write the sibling form themselves. A consumer declares a remote dependency:

```yaml
dependencies:
  apm:
    - git: Samuel-Harris/foundry
      path: packages/planning
      ref: "^0.1.0"
```

or uses the shorthand install command:

```bash
apm install Samuel-Harris/foundry/packages/planning#^0.1.0 --target cursor,claude,copilot
```

APM resolves the range against the `planning--v<version>` tags that CI creates on `main`. A remote install requires the consumer to have repository access.

## The meta-package

`packages/default-stack/apm.yml` lists nine sibling packages as `- path: ../<name>` entries and therefore omits `dependencies: {}`, which is non-empty. Installing `packages/default-stack` is the one-command route to the default stack.

Those nine direct dependencies pull in two more transitively, so a single meta-package install resolves eleven packages:

```text
default-stack
├── coding-style
├── execution        -> pr, review
├── git-diff
├── p-stack
├── pr
├── repo-maintenance
├── review
├── s-stack          -> coding-style, deep-interview, p-stack, planning, pr, review
└── skill-creation   -> deep-interview, repo-maintenance

transitively added: planning, deep-interview
planning             -> deep-interview, review
```

`cursor-usage`, `data-visualisation`, `foundry-maintenance`, `handoff`, `infrastructure`, `repo-init`, `search` and `ui` are intentionally not part of the default stack; install them individually.

There is deliberately **no `apm.yml` at the repository root**. Root-level compile and pack discovery walks the whole tree, so a root manifest would absorb the nested packages' `.apm/` trees into one package and destroy the per-package boundaries.

## Lockfiles

- Commit `apm.lock.yaml` per package once generated.
- Never hand-author or hand-edit hashes or pins. Regenerate with `apm lock` or `apm install`.
- `apm install --frozen` does **not** reject a stale lockfile when the dependencies are local. It fails only when the lockfile is missing; otherwise it re-resolves `apm.yml`, rewrites the lockfile and exits `0` with `Lockfile presence verified`. Verified with 0.32.0: adding `- path: ../review` to `packages/swarm/apm.yml` passed `--frozen` and `apm audit --ci`, and the rewritten lockfile gained a `_local/review` entry. A rewrite after install is therefore the staleness signal. `.githooks/pre-commit`, which CI runs as its only job, runs `git diff` on `apm.lock.yaml` after installing, ignoring the absolute-path lines described below; that catches both a manifest change and a primitive content change committed without regenerating the lockfile. Locally, `run-tier1.sh` catches the same rewrite with its tracked-file stability check.
- `apm audit --ci` is the release gate.
- **APM writes a transitive sibling dependency's path as an absolute path; the committed lockfile records it relative to the package.** Direct local dependencies are pinned as `local_path: ../<name>`, which is portable, but a local dependency reached transitively (for example `deep-interview` via `s-stack` in `default-stack`) additionally records `anchored_local_path`, and its deployment entries record `owners` and `active_owner` as `local:<path>`. APM writes both as `/absolute/path/to/packages/<name>`.
  - Cause: APM's `_portable_anchor_identity` relativises the path against the project root with `Path.relative_to`, which only succeeds for paths inside it. Each lockfile's project root is `packages/<name>`, every sibling is outside it, so APM falls back to the absolute path. APM 0.35.0 behaves the same way.
  - Normalisation: `scripts/relativise_lockfiles.py` rewrites those absolute paths to `../<name>`, relative to the lockfile's directory, the same form APM itself writes for packages inside the project root. `.githooks/pre-commit` runs it after `apm install --frozen` and before diffing the lockfile, and `run-tier1.sh` runs it before its stability diff, so the committed lockfile is the normalised one. It also makes the content hashes of files that link into a transitive sibling's materialised directory independent of the checkout path, as [the drift section below](#apm-audit---ci-reports-drift-on-default-stacks-relativised-lockfile) explains. For that it reads the deployed files, and it exits `1` without changing the lockfile when one is missing or no longer matches its recorded hash. Run it after any `apm install` in a package with transitive siblings: `python3 scripts/relativise_lockfiles.py packages/<name>/apm.lock.yaml`.
  - Both fields must change together. Verified with 0.32.0: with relative owners but an absolute `anchored_local_path`, `apm audit --ci` fails with `invalid owner(s) local:../explore` (the `explore` package has since been removed); with both relative, `apm audit --ci` passes in every package except `default-stack`, whose relativised lockfile reports drift for another reason (see [`apm audit --ci` reports drift on `default-stack`'s relativised lockfile](#apm-audit---ci-reports-drift-on-default-stacks-relativised-lockfile)). Any later install rewrites both back to absolute paths, which the normaliser undoes.

## Generated-file policy

Per-target deploy output (`.cursor/`, `.claude/`, `.agents/`, `.github/agents/`, `.github/instructions/`) is build output and is never committed; `.gitignore` excludes it. Lockfiles and `apm.yml` are source and are committed. `.github/workflows/` stays tracked, so `.github/` is never ignored wholesale.

## External prerequisites (not declared as dependencies)

The Linear MCP server is required at runtime by `masterplan` and `implement-linear-ticket`. It is **not** declared under `dependencies.mcp`:

- no resolvable Linear APM package has been verified to exist, and claiming a resolved dependency that cannot be resolved would be false;
- APM does not sandbox MCP servers, so declaring one would imply a safety guarantee that does not hold.

The server is documented as a runtime prerequisite instead, and `implement-linear-ticket` stops with an actionable error when it is absent.

## Cross-package references

Every primitive that names a primitive shipped by another package is covered by a declared dependency edge. The graph is acyclic and no reference is left dangling.

| Reference               | Declared in                                                      | Ships in           | Covering edge                     |
| ----------------------- | ---------------------------------------------------------------- | ------------------ | --------------------------------- |
| `quick-review`          | `execution` — the `implement-linear-ticket` skill                | `review`           | execution → review                |
| `quick-review`          | `planning` — the `plan-handoff-standard` instruction             | `review`           | planning → review                 |
| `babysit`               | `execution` — the `implement-linear-ticket` skill                | `pr`               | execution → pr                    |
| `deep-interview`        | `planning` — `masterplan` and `plan-handoff-standard`            | `deep-interview`   | planning → deep-interview         |
| `deep-interview`        | `skill-creation` — the `design-skill` skill                      | `deep-interview`   | skill-creation → deep-interview   |
| `deep-interview`        | `repo-init` — the `terraform-monorepo-init` skill                | `deep-interview`   | repo-init → deep-interview        |
| `optimise-agent-config` | `skill-creation` — the `design-skill` skill                      | `repo-maintenance` | skill-creation → repo-maintenance |
| `poteto-mode`           | `s-stack` — the `sam-mode` skill and its handbooks               | `p-stack`          | s-stack → p-stack                 |
| `interrogate`           | `s-stack` — the `sam-mode` skill and its handbooks               | `p-stack`          | s-stack → p-stack                 |
| `deep-interview`        | `s-stack` — the `sam-mode` skill and its handbooks               | `deep-interview`   | s-stack → deep-interview          |
| `quick-review`          | `s-stack` — the `sam-mode` skill and its handbooks               | `review`           | s-stack → review                  |
| `summarise-pr`          | `s-stack` — the `sam-mode` skill and its handbooks               | `pr`               | s-stack → pr                      |
| `plan-handoff-standard` | `s-stack` — the `sam-mode` skill and its handbooks               | `planning`         | s-stack → planning                |
| `software-engineering-rules` | `s-stack` — the `sam-mode` skill and its handbooks          | `coding-style`     | s-stack → coding-style            |

`plan-handoff-standard` treats its `quick-review` step as required; the `planning → review` edge above satisfies it, so a single-package install of `planning` carries the capability its own text names.

### Why `deep-interview` exists

`planning`, `skill-creation` and `repo-init` all name the `deep-interview` skill. Keeping that skill inside `planning` forced `skill-creation` to depend on `planning` for nothing else, and stopped `repo-init` from declaring the dependency at all, because `planning` would have dragged in `review`. `deep-interview`, `pr` and `repo-maintenance` ask for a read-only exploration subagent in host-neutral terms rather than naming one, so they need no dependency for it.

That orientation is what keeps the graph acyclic:

```text
repo-init --> deep-interview
skill-creation --> deep-interview
skill-creation --> repo-maintenance
planning --> deep-interview
planning --> review
execution --> pr
execution --> review
s-stack --> p-stack
s-stack --> deep-interview
s-stack --> review
s-stack --> pr
s-stack --> planning
s-stack --> coding-style
```

APM cannot express a dependency cycle, so any future reference that points backwards along `planning → deep-interview` or `execution → pr` must be reworded or extracted, not declared.

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

This is the reason every package with a sibling `path:` dependency cannot be packed from its committed manifest: `default-stack`, `execution`, `planning`, `repo-init`, `s-stack` and `skill-creation`. The sibling section above records the full comparison, the tested remote fallback and the release-job rewrite that would produce their bundles.

### `apm audit --ci` cannot replay a lockfile with a duplicated local `resolved_by` parent

This is an APM lockfile-writer defect in the pinned 0.32.0 CLI. No Foundry package triggers it today, but `default-stack` and `s-stack` each sit one edge away from it.

**Trigger.** A local package is reachable by **two** paths from the same manifest (once directly, once transitively) **and** is itself the `resolved_by` parent of another local package. `apm install` then writes two entries with the same `repo_url`, and the drift replay cannot decide which one parents the grandchild. `default-stack` lists `coding-style`, `p-stack`, `pr`, `repo-maintenance` and `review` directly, and `execution`, `s-stack` or `skill-creation` also pull each of them in (see the tree in [The meta-package](#the-meta-package)), so its lockfile records each of them twice. None of the five has a sibling dependency, so the replay has no grandchild to resolve and this defect does not fire. `default-stack`'s audit fails for an unrelated reason until `apm install --frozen` has run, as [the next section](#apm-audit---ci-reports-drift-on-default-stacks-relativised-lockfile) shows. `s-stack` likewise reaches `deep-interview` and `review` both directly and via `planning`, and neither of those has a sibling dependency either. Until the `explore` package was removed, `pr` parented `explore`, and `default-stack`'s own audit failed:

```text
$ apm audit --ci          # in packages/default-stack, while pr depended on explore
drift               | drift replay failed: corrupt local dependency graph in the lockfile
                    | (ambiguous resolved_by parent '_local/pr' of
                    | '_local/explore': 2 local dependencies share that repo_url
                    | (['../pr', '../pr'])). Fix the
                    | resolved_by chain or re-run 'apm install'.
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

**Scope.** Only the meta-package's own lockfile would be affected. Consumer-side installs of the same manifest audit cleanly, and `apm install --frozen` still succeeds in place.

**Handling.** The manifest keeps its nine declared requirements rather than dropping the direct edges that duplicate a transitive path (`coding-style`, `p-stack`, `pr`, `repo-maintenance` and `review`). Dropping those direct edges would state the default stack's contents only indirectly, so its contract would silently change whenever a sibling's dependencies change. The cost is that giving any of those five a sibling dependency would break `default-stack`'s own `apm audit --ci`, which `tests/structural/run-tier1.sh` now expects to pass.

### `apm audit --ci` reports drift on `default-stack`'s relativised lockfile

APM 0.32.0 materialises a local dependency that a sibling declares under `apm_modules/_local/<first 12 hex of sha256(anchored_local_path)>/` (`apm_cli/models/dependency/materialization.py`), and rewrites cross-skill links into that directory, such as `../../../apm_modules/_local/<hash>/p-stack/.apm/skills/bro/SKILL.md` in `.agents/skills/ketchup/SKILL.md`. `default-stack` reaches `p-stack` through `s-stack`, so 32 deployed p-stack skill files carry that hash, and `anchored_local_path` is absolute at install time. Their text, and their `sha256:` hashes in the lockfile, therefore depend on the checkout path. Reaching `p-stack` twice is not the cause: with the direct `- path: ../p-stack` edge removed, the lockfile records `p-stack` once and the same 32 files carry the hash.

`scripts/relativise_lockfiles.py` replaces each of those hashes with the hash the file has when its links name the directory of the relative `anchored_local_path`. The committed lockfile is then the same from every checkout, which `tests/versioning/test_relativise_lockfiles.py` asserts. `apm audit --ci` on it fails two checks until `apm install --frozen` rewrites it. `content-integrity` compares its hashes with the deployed files, which still name the directory of the absolute path. `drift` replays the install from the relative `anchored_local_path`, so the replay's links name a different directory from the deployed files'. Rerun it from the repository root with the pinned CLI, outside the agent sandbox, bounding each `apm` call as `AGENTS.md` requires:

```bash
cd packages/default-stack
apm install --frozen --target cursor,claude,copilot   # deploys, and writes absolute paths
python3 ../../scripts/relativise_lockfiles.py apm.lock.yaml
git diff --exit-code apm.lock.yaml                    # the committed form, so no output
apm audit --ci                                        # [x] 2 of 9 check(s) failed (content-integrity, drift)
apm install --frozen --target cursor,claude,copilot
apm audit --ci                                        # [*] All 10 check(s) passed
python3 ../../scripts/relativise_lockfiles.py apm.lock.yaml
```

At `7747021`, before the `s-stack` edge, the same commands pass all 10 checks on the relativised lockfile, and so does `packages/s-stack`, where `p-stack` is a direct dependency and deploys under `apm_modules/_local/p-stack/` with no hash.

CI stays green because nothing audits the relativised lockfile. CI's only APM check, `.githooks/pre-commit`, runs `apm install --frozen`, relativises and diffs the lockfile, and never runs `apm audit`. `tests/structural/run-tier1.sh` runs `apm install --frozen` before `apm audit --ci` in each package, so the audit sees APM's own lockfile, and relativises again before its stability diff. A consumer's own lockfile records no sibling path and audits cleanly. Run `apm install --frozen` before auditing `packages/default-stack` by hand.

### Plugin-format archives do not translate instruction frontmatter

`apm pack --archive` emits a Claude plugin bundle. Installing it deploys the expected file inventory, but per-target instruction translation is not applied: `.cursor/rules/*.mdc` keeps `applyTo` instead of gaining `globs`, and `.claude/rules/*.md` keeps `applyTo` instead of gaining `paths`. The local Tier 1 suite's archive check asserts inventory, sibling-file presence and tamper rejection; scoping translation is asserted from the source installs. `apm pack --format apm` is not a substitute: it reports `No deployed files found -- empty bundle created` and writes only the embedded lockfile.

### Skills are never structurally validated by APM

`apm pack` bundles a `SKILL.md` with no `description`, invalid YAML, or a `name` that disagrees with its directory, and `apm install` deploys it. APM 0.32.0 has no skill frontmatter gate. `tests/structural/validate_primitives.py` fills that gap in the local Tier 1 suite.

### `apm install` does not validate primitives it deploys

`apm install --dry-run` at a package root resolves that package's *dependencies*; it does not validate the package's own primitives. Primitive-level verification lives in the local Tier 1 suite's scratch-consumer and archive-consumer checks, which assert the deployed inventory.

### Delivery is not a safety statement

`apm audit --ci` reports content integrity and drift. It is not a security certification, and APM does not sandbox MCP servers.
