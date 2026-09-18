# Working in this repository

Operational notes for agents editing Foundry. This repository publishes sixteen
[APM](https://microsoft.github.io/apm/) packages — fifteen content packages plus
a meta-package. Almost everything surprising about it comes from the pinned CLI,
so this file records **empirically verified APM 0.30.0 behaviour**, not a
restatement of the design. For what each package contains, see `README.md`; for
the dependency graph and the CLI defects it works around, see
`docs/DEPENDENCY-CONTRACTS.md`.

## Caveat: this describes apm-cli 0.30.0

The repository pins **apm-cli 0.30.0**. APM is **pre-1.0** (0.30.0 < 1.0.0), so
CLI flags, manifest keys, supported targets, deploy paths and bundle formats are
all subject to change without notice.

Do not cite a commit for the pin. `apm --version` prints a trailing short SHA,
but the published wheel ships with `__BUILD_SHA__ = None` and falls back to
`git rev-parse --short HEAD` resolved from the site-packages directory, so the
SHA it prints is the **consuming repository's** HEAD, not the CLI's. It changes
on every commit here and identifies nothing about the installed CLI.

Every statement below was observed with 0.30.0 on macOS. **Re-verify against the
installed version before relying on it.** The pinned version is repeated in the
`README.md` prerequisites and in `.github/workflows/ci.yml` (`apm-version`); the
three must stay in step. If you bump one, bump all three and re-run
`bash tests/structural/run-tier1.sh`.

## Which CLI runs

- Repository scripts default to the local virtual-environment copy when it
  exists and fall back to a `PATH`-resolved `apm`. `.venv-apm/` is gitignored,
  so a fresh clone has only the `PATH` copy.
- A bare `apm` resolves through `PATH`. On the authoring machine that is
  Homebrew's `/opt/homebrew/bin/apm`.
- Both are 0.30.0 here. **Prefer the venv copy** so a Homebrew upgrade cannot
  silently change behaviour. Confirm with `apm --version` before trusting a
  result.
- `.venv-apm/` and `apm_modules/` are gitignored. Never commit them.

## Bound every `apm` call

Wrap `apm` in a hard timeout, always:

```bash
timeout 300 apm pack --dry-run --verbose          # Linux / CI
perl -e 'alarm shift; exec @ARGV' 300 apm pack --dry-run --verbose   # macOS, no GNU timeout
```

`apm` 0.30.0 serialises every state mutation behind one OS-user lock,
`~/.apm/.apm-lifecycle.lock`, with a 120-second bounded wait
(`LIFECYCLE_LOCK_TIMEOUT = 120.0`). `apm install`, `apm lock`, `apm update`,
`apm compile`, `apm init`, `apm prune`, `apm deps` and `apm audit --strip` take it, as does every other
state-mutating command (`apm uninstall`, `apm config`, `apm approve`,
`apm marketplace`, `apm plugin`, `apm lifecycle`). Commands that mutate state
skip the lock under `--dry-run`. A concurrent or orphaned APM process makes the
next command print
`Another APM operation is running; waiting up to 120s.` and block for up to two
minutes before raising `LifecycleBusyError`. That, not network resolution, is
what makes an unbounded `apm` call look like a hang. `apm pack` does **not**
take the lock and fails fast, but bound it anyway.

`tests/structural/run-tier1.sh` implements a `bounded` helper that prefers
`timeout`, then `gtimeout`, then `perl -e 'alarm shift; exec @ARGV'`. Reuse it
rather than calling `apm` directly.

## Manifest schema

Each package has `packages/<name>/apm.yml`:

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
    - path: ../foundry-review
    - path: ../foundry-swarm
scripts:
  check: apm audit --ci
```

Rules that bite:

- Use the plural `targets:` key. Never declare both `target:` and `targets:`.
- **Quote `version`.** YAML parses `0.1.0` as the string `0.1.0`, but a
  two-component version such as `1.10` parses as the float `1.1` and loses
  information. Quote it so the declared version is always the literal string.
- **Quote any `description` containing a colon.** An unquoted `:` followed by a
  space makes the whole manifest unparseable and every command fails with
  `mapping values are not allowed here`. The generator writes descriptions with
  `json.dumps`, which is always valid YAML.
- **Declare `dependencies: {}` explicitly, even when empty.** `apm pack` uses
  the presence of the `dependencies` mapping to decide whether to emit a bundle
  at all. Omitting it produces no bundle.
- Keep `scripts.check` as `apm audit --ci`, not `apm compile --validate`:
  `compile --validate` is a weak check that fails outright on a clean skill-only
  package (see below).
- The only targets used here are `cursor`, `claude` and `copilot`. They are
  always passed explicitly with `--target`; filesystem auto-detection is never
  relied upon.

## Dependencies: sibling paths, and why packing fails

Packages depend on each other through a **sibling relative path**:

```yaml
dependencies:
  apm:
    - path: ../foundry-planning
```

- This form **works for `apm install`**, `apm install --frozen` and
  `apm audit --ci`. The lockfile records it as `repo_url: _local/foundry-planning`,
  `source: local`, `local_path: ../foundry-planning`.
- This form **fails for `apm pack`**, in every format:

  ```text
  Error: Cannot pack — apm.yml contains local path dependency: ../foundry-planning
  Local dependencies are for development only. Replace them with remote references (e.g., 'owner/repo') before packing.
  ```

  The seven packages that declare one — `foundry-default-stack`,
  `foundry-execution`, `foundry-planning`, `foundry-pr`,
  `foundry-repo-maintenance`, `foundry-skill-creation` and `foundry-swarm` — are
  therefore **pack-blocked** until `v0.1.0` is tagged. CI asserts that guardrail
  instead of skipping those packages silently.
- The remote fallback `{git: Samuel-Harris/foundry, path: packages/<name>, ref: "^0.1.0"}`
  is **not viable pre-release**: without a pushed tag, a real install stops with
  `No tags on Samuel-Harris/foundry satisfy '^0.1.0'`. Keep the `path:` form;
  produce bundles for the seven dependency-bearing packages from a release job
  after the tag exists.
- Consumers never use the sibling form. They install the remote shorthand,
  `apm install Samuel-Harris/foundry/packages/<name>#v0.1.0`.
- **A transitive sibling dependency additionally records an absolute path, which
  is harmless.** Direct dependencies get a portable `local_path: ../<name>`, but
  a local dependency reached through another local package (for example
  `foundry-architect` via `foundry-swarm`) also gets
  `anchored_local_path: /absolute/path/to/packages/<name>`. The committed
  lockfiles carry the authoring machine's path. Verified: `install --frozen` and
  `audit --ci` still pass at a different absolute root, and `apm install`
  rewrites the field to the local path. Do not hand-edit it.
- **Only the direct-dependency form dedupes.** When a package is reachable both
  directly and transitively it appears twice in the lockfile. That is harmless
  unless the duplicated package is itself the parent of a third, which breaks
  `apm audit --ci` — see below.

## Primitive naming contracts

| Primitive | Source path | Required frontmatter |
| --- | --- | --- |
| Skill | `.apm/skills/<name>/SKILL.md` | `name`, `description` |
| Agent | `.apm/agents/<name>.agent.md` | `description` (plus optional `name`, `model`, `tools`, `color`, `handoffs`) |
| Instruction | `.apm/instructions/<name>.instructions.md` | `description`, `applyTo` |

- **Skill `name` must equal its directory name**, use lowercase letters, digits
  and single hyphens, and be at most 64 characters. `description` is at most
  1024 characters.
- Agents are `*.agent.md`, not `*.md`. Instructions are `*.instructions.md`, not
  `*.mdc`. Those suffixes are the source contract; the deployed suffix differs
  per target (see below).
- **APM 0.30.0 does not validate any of this.** `apm compile --validate` passes
  an agent with no `description`, and `apm pack` bundles a `SKILL.md` with
  invalid YAML. `tests/structural/validate_primitives.py` is the real gate: it
  checks required fields, the name/directory rule, valid YAML, the description
  length limit and that every relative link resolves on disk. Run it after any
  primitive edit.

## Instruction scoping translation

`applyTo` is translated per target by a **source** install:

| Target | Deployed path | Key emitted |
| --- | --- | --- |
| cursor | `.cursor/rules/<name>.mdc` | `globs: "<pattern>"` (keeps `description`) |
| claude | `.claude/rules/<name>.md` | `paths:` as a YAML list (drops `description`) |
| copilot | `.github/instructions/<name>.instructions.md` | `applyTo: "<pattern>"` verbatim (keeps `description`) |

A **plugin-format archive** install does not apply this translation: all three
targets then keep the source `applyTo` key, so Cursor gets no `globs` and Claude
gets no `paths`. Assert scoping from source installs only.

## Deploy locations

Observed from scratch consumers and the lockfiles. Paths are relative to the
**consumer** root.

| Primitive | cursor | claude | copilot |
| --- | --- | --- | --- |
| Skill | `.agents/skills/<name>/` | `.claude/skills/<name>/` | `.agents/skills/<name>/` |
| Agent | `.cursor/agents/<name>.md` | `.claude/agents/<name>.md` | `.github/agents/<name>.agent.md` |
| Instruction | `.cursor/rules/<name>.mdc` | `.claude/rules/<name>.md` | `.github/instructions/<name>.instructions.md` |

Cursor and Copilot share the `.agents/skills/` root, so a mixed-target install
deploys each skill once. `references/`, `scripts/` and `assets/` ship alongside
`SKILL.md`.

`apm targets --json --all` reports `cursor` as `active` here because the
repository root keeps a `.cursor/settings.json`; `claude` and `copilot` show as
`inactive`. This is detection only — targets are always passed explicitly, and no
tool folder is created to influence detection.

## `apm.lock.yaml`

Generated, committed, and never hand-edited. Regenerate with `apm install`.

- `lockfile_version`, `apm_version: 0.30.0`, `dependencies: [...]`.
- `deployments:` — one entry per deployed path with `target`, `value`,
  `content_hash` (sha256) and ownership. Directories carry `content_hash: null`.
- Shared skill deployments under `.agents/skills/` are recorded with
  `target: legacy`, not `target: cursor` or `target: copilot`.
- `local_deployed_files` and `local_deployed_file_hashes` list the deployed tree
  and its hashes; `apm audit --ci` and bundle integrity checks compare against
  them.
- `apm install --frozen` refuses to run when the lockfile is missing or out of
  sync with `apm.yml`. Use it in CI; use plain `apm install` after editing a
  manifest.
- Transitive local dependencies carry an `anchored_local_path`. It is rewritten
  by the next `apm install` and does not pin the lockfile to a machine, so a
  lockfile committed from any checkout root is valid. Never hand-edit it.

## Validate, audit and pack

- `apm compile --validate` needs at least one agent or instruction in `.apm/`. On
  a package that ships only skills it exits `1` with `No instruction files found
  in .apm/ directory` — until an install has materialised the deploy targets,
  after which it exits `0` and prints `Validated 0 primitives`. Declaring
  `type: skill` changes neither outcome. **Always install before validating.**
  It counts agents (reported as `chatmodes`) and instructions, inspects no skill,
  and enforces no frontmatter. Do not treat it as a contract gate.
- `apm audit --ci` is the real gate for a lockfile and its deployed tree. It runs
  nine or ten baseline checks plus drift detection and replays the install into a
  scratch tree; it also skips gitignored deploy paths automatically, which is what
  makes it usable here.
- **`apm audit --ci` cannot replay a lockfile that records a local package
  twice.** If a local package is reachable directly *and* transitively *and* it
  parents another local package, the drift replay fails with `ambiguous
  resolved_by parent ...: 2 local dependencies share that repo_url`. Re-running
  `apm install` rewrites the same duplicate. `foundry-default-stack` is the only
  package here affected; its eight-dependency manifest is kept deliberately and
  the failure is asserted rather than being worked around by trimming the
  manifest. Consumer installs of the same manifest audit cleanly. The repro is in
  `docs/DEPENDENCY-CONTRACTS.md`.
- `apm pack --archive -o ./dist` emits a **Claude plugin bundle** (default
  format) as a `.zip`; installing it round-trips the file inventory but not
  per-target instruction translation. `apm pack --format apm` is not a
  substitute: it reports `No deployed files found -- empty bundle created` and
  writes only the embedded lockfile.
- Packing writes `.claude-plugin/plugin.json` and `.github/plugin/plugin.json`
  into the package directory. Those are build output and are gitignored.
- Never add `--force`, `--trust-transitive-mcp`, `--allow-insecure`, `--no-policy`
  or any other policy-bypass flag to make a check pass.

## CI and the audit-only pattern

`.github/workflows/ci.yml` uses `microsoft/apm-action@v1` with
`setup-only: true`. This matters: `apm install` overwrites managed files before
an audit runs, which would erase tampered bytes before `content-integrity` and
drift detection could see them. `setup-only` provides the CLI only. The action's
`apm-version` input defaults to `0.14.0`, so always pass `apm-version: "0.30.0"`.

Jobs: `contract` (primitive validator plus secret scan), `validate-packages`
(matrix over all sixteen), `scratch-consumer` (matrix over the three targets),
`archive-consumer` (pack, install, inventory, tamper rejection) and
`lint-markdown`. The `validate-packages` matrix carries a `pack_blocked` flag for
the seven local-path packages and an `audit_known_broken` flag for
`foundry-default-stack`; both assert the pinned CLI's documented failure rather
than skipping the package.

## Generated-file policy

- Commit `apm.yml`, `README.md` and `apm.lock.yaml` per package.
- Commit each package's `.gitignore`, even though it is generated and the root
  `.gitignore` already ignores `apm_modules/`. `apm install` appends
  `# APM dependencies` and `apm_modules/` to the `.gitignore` in its working
  directory whenever that exact line is absent there, so a package without one
  grows an untracked file on the next install and dirties the tree. Sixteen
  byte-identical 33-byte files are the expected end state.
- Never commit deploy output. `.gitignore` excludes `apm_modules/`, `dist/`,
  `build/`, `.claude/`, `.agents/`, `.cursor/rules/`, `.cursor/agents/`,
  `.github/agents/`, `.github/instructions/`, `.github/plugin/` and
  `.claude-plugin/`.
- `.github/workflows/` must stay tracked, so `.github/` is never ignored
  wholesale.
- `.cursor/settings.json`, `.vscode/`, `assets/`, `LICENSE`,
  `.markdownlint.json` and the repo-owned `.markdownlint-cli2.jsonc` ignore list
  are preserved, not generated.

## Local Tier 1 suite

`bash tests/structural/run-tier1.sh` runs the primitive validator, the secret
scan, the per-package matrix (`install --dry-run`, `install --frozen`,
`audit --ci`, `compile --validate`, `pack --dry-run`, in that order),
scratch-consumer installs per target with a full file inventory, instruction
scoping translation, archive packing and install, tamper rejection, the
missing-sibling failure and a tracked-file stability check. Set `APM=` to point
at a different CLI, `APM_TIMEOUT=` to change the per-call bound, and
`APM_TARGETS=` to narrow the target list.

**Run it outside the agent sandbox.** APM creates a `.cursor/` directory inside
its resolution staging areas regardless of which `--target` values were passed,
and the Cursor sandbox denies every write beneath a `.cursor` path with
`[Errno 1] Operation not permitted`. Inside the sandbox, `install --frozen` and
`audit --ci` therefore fail for any package with dependencies, and the
scratch-consumer installs fail, none of which reflects a repository defect. The
sandbox also blocks the CLI's lifecycle lock at `$HOME/.apm/`, so point `HOME` at
a writable directory when the real one is read-only.

## British English

Write prose and documentation in British English.
