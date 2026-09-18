# Tier 1 acceptance suite

Tier 1 proves **structural packaging and deployment**. It answers: does the manifest resolve, does the install succeed, and does the deployed inventory match what the package promises?

It does **not** prove runtime recognition, workflow behaviour or agent identity dispatch. No client application is launched, no skill is trigger-tested and no MCP server is contacted. Those rows are `untested` in [`docs/COMPATIBILITY.md`](../docs/COMPATIBILITY.md).

## How to run it locally

From the repository root, with `apm` on `PATH`:

```bash
apm --version
python3 tests/structural/validate_primitives.py
apm install --target cursor,claude,copilot        # must precede compile --validate
apm audit --ci
apm compile --validate
apm pack --dry-run --verbose
apm pack --archive -o ./dist
```

The commands that take no package argument are run with the package directory as the working directory; `tests/structural/validate_primitives.py` runs once from the repository root and covers all sixteen packages.

`apm install` must run before `apm compile --validate`: on a package whose `.apm/` holds only skills, `compile --validate` exits `1` until an install has materialised the deploy targets. Even then it is a weak check — it counts agents and instructions, validates no skill and enforces no frontmatter. `tests/structural/validate_primitives.py` is the real contract gate and covers all sixteen packages. See [`docs/DEPENDENCY-CONTRACTS.md`](../docs/DEPENDENCY-CONTRACTS.md).

The suite must run outside the agent sandbox: APM writes into a `.cursor/` staging directory regardless of the requested targets, and the sandbox denies those writes with `Operation not permitted`.

## Assertions

Each assertion below must produce recorded evidence.

1. **Primitive contract.** Every skill carries `name` and `description`; every agent carries `description`; every instruction carries `description` and `applyTo`. A skill's `name` equals its directory name. Every `description` is at most 1024 characters. Frontmatter parses as valid YAML. Every relative markdown link inside a primitive resolves on disk.
   — `python3 tests/structural/validate_primitives.py`

2. **Source install into a clean scratch consumer, per target.** For each of `cursor`, `claude` and `copilot`, separately: `apm init` with that explicit target, then `apm install <absolute path to packages/default-stack> --target <target>`, then `apm view default-stack`, then `apm audit --ci` exits `0`.

3. **Archive install into a separate scratch consumer.** Each packable package is packed with `apm pack --archive -o ./dist`, then installed from the archive in a disposable directory with no access to the authoring checkout or its `apm_modules/` cache. The seven packages with sibling `path:` dependencies — `default-stack`, `execution`, `planning`, `pr`, `repo-maintenance`, `skill-creation` and `swarm` — cannot be packed before the `v0.1.0` tag exists; the suite asserts that documented guardrail instead of skipping them silently (see [`docs/DEPENDENCY-CONTRACTS.md`](../docs/DEPENDENCY-CONTRACTS.md)).

4. **Deployed inventory matches.** Every expected skill, agent and instruction file for the ten default-stack packages is present after deployment, and no retired item (`pr-contention`, `port-claude-code-artefact`, `sequential-ralplan`, `explain-pr`, `generate-pr-story`, `optimise-cursor-repo`) is deployed. This is a containment assertion plus a denylist, not a reverse diff: an unexpected extra file in a deploy root would not fail the suite.

5. **Sibling files resolve after deployment.** Every `references/` and `scripts/` path promised by a skill exists after source deployment, and every relative link inside a primitive resolves on disk. The archive consumer asserts the deployed inventory of one bundle and that no sibling file is missing from it.

6. **Instruction scoping translation.** Tier 1 asserts that the deployed scoping key and pattern are correct for each of the five instructions (four distinct patterns: `**/*`, `**/*.py`, `**/AGENTS.md`, `.foundry/plans/**/*.md`): `globs` on `.cursor/rules/*.mdc`, a `paths` list on `.claude/rules/*.md` and `applyTo` verbatim on `.github/instructions/*.instructions.md`. Whether a client fires the rule on matching files and refrains on non-matching files is `untested` — no client is launched. A plugin-format archive install does not apply this translation at all, so scoping is asserted from source installs.

7. **Tampered archive is rejected.** A copy of an archive with one byte changed is rejected. No bypass flag is used.

8. **Missing sibling dependency fails actionably.** Removing a declared sibling dependency produces an actionable failure, not a silent skip.

9. **Frozen install and audit.** `apm install --frozen` succeeds for all sixteen packages and `apm audit --ci` exits `0` for fifteen of them. `default-stack` is the documented exception: its own lockfile cannot be replayed because APM 0.30.0 records an ambiguous `resolved_by` parent for a locally duplicated dependency. The suite asserts that specific failure rather than accepting any failure, and the consumer-side audit of the same manifest is asserted separately in assertion 2. See [`docs/DEPENDENCY-CONTRACTS.md`](../docs/DEPENDENCY-CONTRACTS.md).

10. **Stability.** Re-running install and pack leaves the working tree unchanged: the suite records `git status --porcelain` plus `git diff` before and after, and the two must match.

11. **Secret scan.** Scanned over every tracked and untracked (unignored) working-tree file plus `packages/*/dist/**`, not only tracked files. Files over 2 MB and unreadable files are counted and reported as skipped rather than being counted as clean.

12. **Target resolution recorded.** `apm targets --json --all` output is recorded, and no tool folder was created merely to influence detection.

13. **No runtime claim.** `docs/COMPATIBILITY.md` labels every runtime row `untested`. No runtime row claims `supported`. Evidenced by inspection of the document; no automated check asserts it.

## Out of scope

- Launching Cursor, Claude Code or GitHub Copilot.
- Trigger-testing any skill.
- Verifying agent identity resolution at runtime.
- Contacting any MCP server.
- Hooks, prompts, commands and LSP primitives.
