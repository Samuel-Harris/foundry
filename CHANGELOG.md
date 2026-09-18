# Changelog

All notable changes to this repository are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0]

### Changed

- **Distribution model.** The repository is no longer a Cursor plugin marketplace. It publishes sixteen independently installable [APM](https://microsoft.github.io/apm/) packages — fifteen content packages and one meta-package — that support `cursor`, `claude` and `copilot`. The `.cursor-plugin/` marketplace manifest and `scripts/validate-template.mjs` are retired.
- **Repository layout.** All workflow prompts now live under `packages/<name>/.apm/` as first-class APM primitives: skills at `.apm/skills/<name>/SKILL.md`, agents at `.apm/agents/<name>.agent.md` and instructions at `.apm/instructions/<name>.instructions.md`.
- **Packages are grouped by capability.** `foundry-coding-style`, `foundry-planning`, `foundry-architect`, `foundry-swarm`, `foundry-execution`, `foundry-review`, `foundry-pr`, `foundry-repo-init`, `foundry-repo-maintenance`, `foundry-skill-creation`, `foundry-search`, `foundry-ui`, `foundry-git-diff`, `foundry-handoff` and `foundry-infrastructure` each own one concern, and `foundry-default-stack` resolves the ten that make up the default stack.
- **Cross-package references are declared, not implied.** Every primitive that names a primitive owned by another package is covered by a sibling dependency edge. `foundry-architect` was extracted so that `foundry-planning` and `foundry-swarm` can share the `architect` agent without either depending on the other, which keeps the graph acyclic (APM cannot express a cycle).
- **Portability.** Every moved primitive had its Cursor-specific coupling removed: tool invocations, agent dispatch, artefact paths and repository-specific assumptions were replaced with target-neutral equivalents. Two Cursor-shaped frontmatter keys are deliberately retained — `readonly: true` on three agents and `disable-model-invocation: true` on the manual-only skills — with their cross-target consequences recorded in `docs/COMPATIBILITY.md`.
- **Artefact paths.** Plans, interviews, masterplans and handoffs now write to `.foundry/` rather than `.cursor/artefacts/`, so they are independent of the host's directory layout.
- **CI.** The pipeline was replaced with a Tier 1 structural suite: per-package install, audit and validation, scratch-consumer and archive-consumer installs for all three targets, archive tamper rejection, markdownlint and a primitive frontmatter validator. The seven packages with local `path:` dependencies have their `apm pack` guardrail asserted rather than skipped, and `foundry-default-stack`'s audit defect is asserted with its exact failure signature.
- **Documentation.** The root `README.md` now describes the package catalogue and dependency graph, and `docs/COMPATIBILITY.md` and `docs/DEPENDENCY-CONTRACTS.md` record the verified structural behaviour and the three APM 0.30.0 defects this repository works around: local-path pack refusal, skill-only `compile --validate` failure, and the duplicated-`resolved_by` audit failure.

### Added

- `foundry-default-stack` meta-package that installs the default stack in one command, resolving ten packages from eight declared dependencies.
- `foundry-architect`, `foundry-coding-style`, `foundry-git-diff`, `foundry-handoff`, `foundry-infrastructure`, `foundry-skill-creation`, `foundry-search`, `foundry-ui` and `foundry-repo-maintenance` packages.
- `masterplan`, `code-tour` and `aws-architecture-diagram` skills.
- `optimise-agent-config`, a target-neutral replacement for `optimise-cursor-repo`.
- `tests/structural/validate_primitives.py`, a structural gate for the frontmatter and sibling-file contracts that APM 0.30.0 does not validate.
- `tests/structural/run-tier1.sh` and `tests/structural/scan_secrets.py`, the local Tier 1 suite and secret scan.
- `AGENTS.md`, which records the empirically verified APM 0.30.0 behaviour a future agent working in this repository needs.
- `apm.yml` and `README.md` for every package.

### Removed

- `.cursor-plugin/`, `scripts/validate-template.mjs` and the `wip-prompts/` tree.
- `pr-contention`, `port-claude-code-artefact`, `explain-pr`, `generate-pr-story` and the Claude variant of `monorepo-init`.
- `cursor-sequential-ralplan` and `optimise-cursor-repo`, replaced by their renamed target-neutral equivalents.

[Unreleased]: https://github.com/Samuel-Harris/foundry/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Samuel-Harris/foundry/releases/tag/v0.1.0
