# Compatibility

This document records what is **structurally verified** about Foundry's APM packages, and what is explicitly **untested**.

## Scope

Foundry is a build-time artefact distribution. APM resolves manifests, copies primitives into a consumer repository and writes a lockfile. That is the whole contract this repository claims to satisfy.

The following are **out of scope** for the current verification and are labelled `untested` everywhere below:

- runtime recognition (whether a client application actually loads a deployed primitive),
- workflow behaviour (whether a skill produces the intended result when triggered),
- agent identity dispatch (whether a host can resolve and dispatch a named subagent).

No runtime row in this document may be read as `supported`.

## Tested versions

| Component | Version | Notes |
| --- | --- | --- |
| APM CLI | `0.30.0` | Pinned. Installed from PyPI into a virtual environment. |
| Cursor | unavailable | Not installed, not launched. All Cursor runtime rows are `untested`. |
| Claude Code | unavailable | Not installed, not launched. All Claude runtime rows are `untested`. |
| GitHub Copilot | unavailable | Not installed, not launched. All Copilot runtime rows are `untested`. |
| OS | macOS 25.6.0 | Local verification. CI runs `ubuntu-latest`. |

## Verification method

Structural verification runs `apm install --target <target>` in each package directory and asserts the resulting lockfile, then `apm audit --ci` against it. CI additionally installs packages into clean scratch consumers, asserts the deployed file inventory, and installs an archive bundle. No client application is launched. See `tests/acceptance.md` for the full assertion list and the recorded evidence.

## Deploy locations

These paths were observed directly from an install, not inferred from documentation. All paths are relative to the **consumer** repository root.

The transformations below are applied by a **source** install (`apm install <path or git ref>`). A plugin-format archive install (`apm install <bundle>.zip`) deploys the same inventory but does not apply the per-target instruction frontmatter translation; see the behaviour notes at the end of this document.

| Target | Primitive | Deployed path | Transformation |
| --- | --- | --- | --- |
| cursor | Skill | `.agents/skills/<name>/` | `references/`, `scripts/` and `assets/` ship alongside `SKILL.md`. Cursor reads the shared `.agents/skills/` root, so no `.cursor/skills/` directory is created. |
| cursor | Agent | `.cursor/agents/<name>.md` | `name`, `model`, `description` and `readonly` pass through verbatim. |
| cursor | Instruction | `.cursor/rules/<name>.mdc` | `applyTo` becomes `globs`. |
| claude | Skill | `.claude/skills/<name>/` | `references/`, `scripts/` and `assets/` ship alongside `SKILL.md`. |
| claude | Agent | `.claude/agents/<name>.md` | `name`, `model`, `description` and `readonly` pass through verbatim. |
| claude | Instruction | `.claude/rules/<name>.md` | `applyTo` becomes `paths`, as a YAML list. The `description` field is not emitted. |
| copilot | Skill | `.agents/skills/<name>/` | `references/`, `scripts/` and `assets/` ship alongside `SKILL.md`. Copilot shares the `.agents/skills/` root with Cursor, so a mixed-target install deploys the skill once. |
| copilot | Agent | `.github/agents/<name>.agent.md` | `name`, `model`, `description` and `readonly` pass through verbatim. |
| copilot | Instruction | `.github/instructions/<name>.instructions.md` | `applyTo` passes through verbatim. |

## Per-package status

Every package installs, and `apm audit --ci` passes, for `cursor`, `claude` and `copilot`. The three runtime columns are `untested` for every package: no client application is launched.

| Package | Primitives deployed | structural | runtime recognition | workflow behaviour |
| --- | --- | --- | --- | --- |
| `architect` | 1 agent | verified | untested | untested |
| `coding-style` | 3 instructions | verified | untested | untested |
| `default-stack` | no primitives; resolves 8 direct and 2 transitive packages | verified | untested | untested |
| `execution` | 1 skill | verified | untested | untested |
| `git-diff` | 3 skills | verified | untested | untested |
| `handoff` | 1 skill | verified | untested | untested |
| `infrastructure` | 1 skill | verified | untested | untested |
| `planning` | 3 skills, 2 agents, 1 instruction | verified | untested | untested |
| `pr` | 3 skills | verified | untested | untested |
| `repo-init` | 1 skill | verified | untested | untested |
| `repo-maintenance` | 3 skills, 1 instruction | verified | untested | untested |
| `review` | 3 skills, 2 agents | verified | untested | untested |
| `search` | 1 skill | verified | untested | untested |
| `skill-creation` | 1 skill | verified | untested | untested |
| `swarm` | 1 skill, 6 agents | verified | untested | untested |
| `ui` | 1 skill | verified | untested | untested |

Structural verification covers all three targets: every package installs, deploys the inventory above, and passes `apm audit --ci` in place — with one documented exception. `default-stack`'s own lockfile cannot be replayed by `apm audit --ci`, because the meta-package reaches `planning` by two paths and an APM 0.30.0 writer defect then records an ambiguous parent chain. Consumers are unaffected: a clean install of `default-stack` resolves the same ten packages and passes `apm audit --ci` on all three targets. See `docs/DEPENDENCY-CONTRACTS.md` for the minimal repro and the reasoning behind keeping the eight-declared-requirement manifest.

`apm install --frozen` succeeds for all sixteen packages in place.

## Archive coverage

`apm pack --archive` succeeds for the nine packages with an empty `dependencies:` mapping:

- `architect`
- `coding-style`
- `git-diff`
- `handoff`
- `infrastructure`
- `repo-init`
- `review`
- `search`
- `ui`

It fails for the seven packages whose manifests declare a sibling `path:` dependency, in every bundle format:

- `default-stack`
- `execution`
- `planning`
- `pr`
- `repo-maintenance`
- `skill-creation`
- `swarm`

Their bundle build is a release-time step that requires the `v0.1.0` tag. Archive install, inventory, skill-only inventory and tamper rejection are verified against the packable bundles, and every bundle is asserted to be free of retired primitives.

## Accepted limitations

### Read-only agents are enforced natively only on Cursor

`readonly: true` is not an APM field. APM passes it through unchanged on all three targets, but only Cursor enforces it natively. On Claude Code and GitHub Copilot the read-only guarantee rests entirely on the prohibition written into the agent body. This is a deliberate, accepted consequence of keeping `readonly` rather than dropping it.

### Instruction scoping uses three different mechanisms

A single `applyTo` pattern is deployed three ways: `globs` on Cursor, `paths` on Claude Code, and `applyTo` on GitHub Copilot. The *intent* is identical, but a subtle change in one host's glob semantics would affect that host only. CI asserts only that the deployed key and pattern are correct; whether a host fires the rule on matching files and refrains on non-matching files is `untested`.

### `disable-model-invocation` is Cursor-shaped

Skills that must only run on explicit request set `disable-model-invocation: true` and also carry explicit trigger guidance in their `description`, so manual-only intent survives on hosts that ignore the key.

## APM 0.30.0 behaviour notes

These were established by running the pinned CLI, and matter when reading CI results.

- **`apm compile --validate` fails on a skill-only package until an install has run.** It requires at least one agent or instruction in `.apm/`; on a package that ships only skills it exits `1` with `No instruction files found in .apm/ directory`. After an install has materialised the deploy targets it exits `0` and reports `Validated 0 primitives` — still inspecting no skill. Declaring `type: skill` changes neither outcome. CI therefore runs `apm install` before `apm compile --validate`, and `tests/structural/validate_primitives.py` remains the real frontmatter and sibling-file gate.
- **`apm audit --ci` fails on a lockfile that records a local package twice.** When a local package is reachable both directly and transitively *and* is the `resolved_by` parent of another local package, `apm install` writes two entries sharing a `repo_url` and the drift replay reports `ambiguous resolved_by parent ...: 2 local dependencies share that repo_url`. Re-running `apm install` does not help. Only the package's own lockfile is affected; consumer installs of the same manifest audit cleanly. `default-stack` is the one package here that hits it. See `docs/DEPENDENCY-CONTRACTS.md`.
- **`apm pack` refuses any manifest that declares a local path dependency.** It exits `1` with `Cannot pack — apm.yml contains local path dependency: <path>`, in every bundle format. The seven dependency-bearing packages use the sibling `path:` form that `apm install` requires, so their bundles cannot be produced before `v0.1.0` is tagged and pushed. CI asserts this guardrail for those packages instead of skipping them silently. See `docs/DEPENDENCY-CONTRACTS.md` for the full comparison of the `path:` and `{git, path, ref}` forms.
- **A plugin-format archive does not translate instruction frontmatter per target.** `apm pack --archive` emits a Claude plugin bundle. Installing that archive deploys the expected file inventory, but `.cursor/rules/*.mdc` keeps the source `applyTo` key instead of `globs`, and `.claude/rules/*.md` keeps `applyTo` instead of `paths`. Per-target translation is only applied by a source install. Archive-based CI therefore asserts inventory and tamper rejection, not scoping; scoping translation is asserted from the source installs.
- **`apm pack --format apm` produces an empty bundle for these packages.** It reports `No deployed files found -- empty bundle created` and writes only the embedded lockfile, so the default plugin-format archive is the only one that carries content in 0.30.0.
- **Skill frontmatter is never validated.** A `SKILL.md` with no `description` installs and packs without complaint, and `apm pack` will happily bundle it. `tests/structural/validate_primitives.py` is the gate for that contract.
- **State-mutating commands serialise on a per-user lifecycle lock.** APM 0.30.0 takes `~/.apm/.apm-lifecycle.lock` for `apm install`, `apm lock`, `apm update`, `apm compile`, `apm init`, `apm prune`, `apm deps` and `apm audit --strip`, and for every other state-mutating command (`apm uninstall`, `apm config`, `apm approve`, `apm marketplace`, `apm plugin`, `apm lifecycle`), with a 120-second bounded wait (`LIFECYCLE_LOCK_TIMEOUT`). Commands that mutate state skip the lock under `--dry-run`. A concurrent or orphaned APM operation makes the next command print `Another APM operation is running; waiting up to 120s.` and block; after 120 seconds it fails with `LifecycleBusyError`. This, not network resolution, is what makes an unbounded `apm` call appear to hang, so every invocation in CI and in `tests/structural/run-tier1.sh` is time-bounded. `apm pack` does not take the lock and returns in about a second when it hits the local-path guardrail.
- **The lifecycle lock path is not configurable.** It is derived from `Path.home()`, so `APM_HOME` does not move it. Redirecting `HOME` does, which is how the structural suite runs installs on a machine whose real `$HOME` is not writable.
- **Frontmatter must be valid YAML.** An unquoted `:` followed by a space inside a `description` makes the key unparseable; APM prints `mapping values are not allowed here` and the command fails. The validator checks every primitive parses, and manifests quote any description containing a colon.
- **`apm install` does not sandbox MCP servers.** A clean `apm audit` result is a content-integrity statement, not a safety certificate.
