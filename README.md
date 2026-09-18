# Foundry

[![CI](https://github.com/Samuel-Harris/foundry/actions/workflows/ci.yml/badge.svg)](https://github.com/Samuel-Harris/foundry/actions/workflows/ci.yml)

![Foundry](assets/foundry-logo.png)

Foundry is a collection of 23 agent skills, 11 subagents and 5 instructions distributed as [APM](https://microsoft.github.io/apm/) packages for Cursor, Claude Code and GitHub Copilot. Install the whole stack in one command, or pick the individual packages you need.

## What this is

This repository was previously a Cursor plugin marketplace. It is now an APM monorepo of 16 independently installable packages. Every primitive has a single target-neutral source, and APM handles the per-target directory and frontmatter translation at install time — there are no per-target variants to keep in sync.

## Prerequisites

Install APM by following the [APM installation guide](https://microsoft.github.io/apm/quickstart/#1-install-apm). Beyond that, this repository only needs:

- **Git.** Required by APM for remote resolution.
- **An explicit target list.** Every command below passes `--target cursor,claude,copilot`. APM's filesystem auto-detection is never relied upon, and no tool directories are created merely to influence it.
- **Maintainers who need the exact pinned CLI version** should install `apm-cli==0.30.0`, the version pinned by this repository's CI:

  ```bash
  python -m pip install "apm-cli==0.30.0"
  ```

## Install

The default stack, via the meta-package:

```bash
apm install Samuel-Harris/foundry/packages/foundry-default-stack#v0.1.0 --target cursor,claude,copilot
```

A single package:

```bash
apm install Samuel-Harris/foundry/packages/<package>#v0.1.0 --target cursor,claude,copilot
```

From a local development checkout:

```bash
apm install /absolute/path/to/packages/<package> --target cursor,claude,copilot
```

A remote install requires the `v0.1.0` tag to exist and the consumer repository to have access.

## Packages

| Package                    | Contents                                                                                                                                                                  | Purpose                                                                                   |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| `foundry-architect`        | agents: `architect`                                                                                                                                                       | The architect agent: read-only strategic architecture and debugging advice.               |
| `foundry-coding-style`     | instructions: `compatibility-surface-gate`, `software-engineering-rules`, `zen-of-python`                                                                                 | Core engineering rules, compatibility guardrails and Python style for agent-written code. |
| `foundry-default-stack`    | _no primitives_                                                                                                                                                           | Meta-package that installs the default Foundry stack.                                     |
| `foundry-execution`        | skills: `implement-linear-ticket`                                                                                                                                         | Take a Linear ticket to a merge-ready draft pull request.                                 |
| `foundry-git-diff`         | skills: `git-diff-all-changes-main`, `git-diff-committed-changes-main`, `git-diff-staged-changes-main`                                                                    | Read-only git diff summaries measured against a repository's main branch.                 |
| `foundry-handoff`          | skills: `handoff`                                                                                                                                                         | Produce a handoff document that lets another agent or session continue the work.          |
| `foundry-infrastructure`   | skills: `aws-architecture-diagram`                                                                                                                                        | AWS architecture diagrams rendered as Mermaid flowcharts.                                 |
| `foundry-planning`         | skills: `deep-interview`, `masterplan`, `ralplan`; agents: `critic`, `planner`; instructions: `plan-handoff-standard`                                                     | Socratic requirement gathering, plan authoring and plan review.                           |
| `foundry-pr`               | skills: `babysit`, `code-tour`, `summarise-pr`                                                                                                                            | Pull request comprehension and merge-readiness babysitting.                               |
| `foundry-repo-init`        | skills: `monorepo-init`                                                                                                                                                   | Scaffold a new repository or monorepo with evidence-based agent guidance.                 |
| `foundry-repo-maintenance` | skills: `agents-md`, `generate-agent-docs`, `optimise-agent-config`; instructions: `keep-agent-mds-up-to-date`                                                            | Keep AGENTS.md files and agent configuration accurate and lean.                           |
| `foundry-review`           | skills: `thermo-nuclear-code-quality-review`, `thermo-nuclear-review`, `thermos`; agents: `thermo-nuclear-code-quality-review-subagent`, `thermo-nuclear-review-subagent` | Branch-level correctness, security and maintainability audits.                            |
| `foundry-search`           | skills: `search-worktrees`                                                                                                                                                | Search the codebase across git worktrees.                                                 |
| `foundry-skill-creation`   | skills: `design-skill`                                                                                                                                                    | Design, draft, validate and iterate on agent skills.                                      |
| `foundry-swarm`            | skills: `swarm`; agents: `build-fixer-low`, `build-fixer-medium`, `executor-high`, `executor-low`, `executor-medium`, `explore`                                           | Coordinated parallel subagents working a shared task list.                                |
| `foundry-ui`               | skills: `uncodixify`                                                                                                                                                      | Remove machine-generated UI slop and restore visual quality.                              |

Each package declares its sibling dependencies in `apm.yml`, so installing one package pulls in the primitives it references. See [`docs/DEPENDENCY-CONTRACTS.md`](docs/DEPENDENCY-CONTRACTS.md) for the dependency graph.

## Skills

| Skill                                | Package                    | Trigger                                                                                                                                                        |
| ------------------------------------ | -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `implement-linear-ticket`            | `foundry-execution`        | Take a Linear ticket to a merge-ready draft GitHub pull request. Resolve the issue, branch from origin/$BASE, plan, implement, run thermos, open a draft PR,…  |
| `git-diff-all-changes-main`          | `foundry-git-diff`         | Show all changes compared to origin/main. Use when the user asks for a full diff of every local change against main.                                           |
| `git-diff-committed-changes-main`    | `foundry-git-diff`         | Show staged and committed changes compared to origin/main. Use when the user asks for the diff of committed work against main.                                 |
| `git-diff-staged-changes-main`       | `foundry-git-diff`         | Show staged changes compared to origin/main. Use when the user asks for the diff of staged changes against main.                                               |
| `handoff`                            | `foundry-handoff`          | Create a comprehensive AI context handoff document for long-running sessions. Use when the user asks for a handoff, a context handoff, or a session summary t… |
| `aws-architecture-diagram`           | `foundry-infrastructure`   | Generate AWS architecture diagrams as Mermaid flowcharts with nested account/VPC subgraphs, numbered data-flow steps, and same-account placement. Use only wh… |
| `deep-interview`                     | `foundry-planning`         | Socratic deep interview with mathematical ambiguity gating before autonomous execution. Use when the user has a vague idea and wants thorough requirements ga… |
| `masterplan`                         | `foundry-planning`         | Generate a holistic product vision from Linear tickets. Pulls backlog, to-do, and in-progress tickets and synthesises them into a status-agnostic overview. U… |
| `ralplan`                            | `foundry-planning`         | Iterative planning consensus loop. Orchestrates Planner, Architect, and Critic agents in rounds until the plan is approved or max iterations reached. Use for… |
| `babysit`                            | `foundry-pr`               | Keep a GitHub pull request merge-ready in a persistent loop by inspecting its current head, resolving unambiguous merge conflicts, addressing valid review co… |
| `code-tour`                          | `foundry-pr`               | Walk through every change in a pull request or Git diff as a chat-only, logically ordered code tour with clickable code citations, commit and review context,… |
| `summarise-pr`                       | `foundry-pr`               | Summarise provided PR change context into concise PR-description bullets. Use when the user asks for a PR description summary, major changes, or design decis… |
| `monorepo-init`                      | `foundry-repo-init`        | Initialise or retrofit a monorepo for structured agentic development through an interactive design interview and a working scaffold with machine-enforced mod… |
| `agents-md`                          | `foundry-repo-maintenance` | Initialise a codebase with hierarchical AGENTS.md documentation, and update it as the code changes.                                                            |
| `generate-agent-docs`                | `foundry-repo-maintenance` | Initialise comprehensive hierarchical AGENTS.md documentation across the entire codebase. Use when the user asks to generate or refresh AGENTS.md documentati… |
| `optimise-agent-config`              | `foundry-repo-maintenance` | Audit a repository's agent configuration for the active targets (Cursor, Claude Code, GitHub Copilot) or evaluate whether a specific artefact (instruction, s… |
| `thermo-nuclear-code-quality-review` | `foundry-review`           | Run an extremely strict maintainability review for abstraction quality, giant files, and spaghetti-condition growth. Use for a thermo-nuclear code quality re… |
| `thermo-nuclear-review`              | `foundry-review`           | Comprehensive security and correctness audit of a branch's changes. Use for thermo nuclear, thermonuclear, or deep review requests, or branch/PR diff audits…  |
| `thermos`                            | `foundry-review`           | Launch both thermo-nuclear review subagents in parallel, then synthesise their findings. Use for thermos, double thermo review, or combined bug/security and…  |
| `search-worktrees`                   | `foundry-search`           | Find files, code, or content across all git worktrees of the current repository. Use when a search must cover every worktree, or when a naive find or grep ac… |
| `design-skill`                       | `foundry-skill-creation`   | Design, draft, validate, and iterate on agent skills. Use when the user asks to create, design, improve, or test a skill, especially when the skill's goal, b… |
| `swarm`                              | `foundry-swarm`            | Coordinated parallel agents on a shared task list. Analyses the task, decomposes into subtasks, and dispatches agents in batches of up to 4. Use for large-sc… |
| `uncodixify`                         | `foundry-ui`               | Guides UI design away from generic AI aesthetic patterns ("Codex UI") toward human-designed, functional interfaces inspired by Linear, Raycast, Stripe, and G… |

The `Trigger` column is the `description` field of each `SKILL.md`, truncated to 160 characters. It is quoted, not paraphrased. The `git-diff-*` skills assume a base branch of `main`.

## Runtime prerequisites

`masterplan` and `implement-linear-ticket` require the **Linear MCP server** to be configured on the host. It is **not** installed by APM and is not declared as a dependency of any package, because no resolvable Linear APM package exists to depend on. `implement-linear-ticket` stops with an actionable error when the server is absent.

APM does not sandbox MCP servers. A clean `apm audit` result is a statement about content integrity and drift, not a safety certificate.

## Compatibility

| Target         | Skills deploy to  | Agents deploy to  | Instructions deploy to  |
| -------------- | ----------------- | ----------------- | ----------------------- |
| Cursor         | `.agents/skills/` | `.cursor/agents/` | `.cursor/rules/`        |
| Claude Code    | `.claude/skills/` | `.claude/agents/` | `.claude/rules/`        |
| GitHub Copilot | `.agents/skills/` | `.github/agents/` | `.github/instructions/` |

All three targets support instructions, agents and skills, so no primitive is degraded or converted. Structural packaging is verified in CI for all three targets; **runtime recognition and workflow behaviour are untested** — no client application is launched. See [`docs/COMPATIBILITY.md`](docs/COMPATIBILITY.md) for the per-package breakdown and the known limits of the pinned CLI.

## Development

Local validation, per package:

```bash
apm --version
python3 tests/structural/validate_primitives.py
python3 tests/structural/scan_secrets.py
apm install --target cursor,claude,copilot        # must precede compile --validate
apm audit --ci
apm compile --validate
apm pack --dry-run --verbose
apm pack --archive -o ./dist
```

`apm compile --validate` exits `1` on a package whose `.apm/` contains only skills until an install has materialised the deploy targets, so install first. It also inspects no skill, so `tests/structural/validate_primitives.py` is the real frontmatter and sibling-file gate.

`bash tests/structural/run-tier1.sh` runs the whole suite, including the scratch-consumer installs, the archive consumer and the tamper rejection, with every CLI call bounded by a hard timeout. `apm pack` refuses to bundle a package that declares a local `path:` dependency, so every package with sibling dependencies is pack-blocked until the `v0.1.0` tag exists; the suite asserts that guardrail explicitly rather than skipping those packages.

CI runs the Tier 1 structural suite: per-package install, audit and validation, a scratch-consumer install for each of the three targets, an archive-consumer install with tamper rejection, a secrets scan and markdownlint. See [`tests/acceptance.md`](tests/acceptance.md) for the assertions and [`docs/DEPENDENCY-CONTRACTS.md`](docs/DEPENDENCY-CONTRACTS.md) for the manifest and CLI contracts.

## Attributions

- Repo initialised from <https://github.com/cursor/plugin-template>.
- The `generate-agent-docs` skill was created from the `deepinit` skill in <https://github.com/Yeachan-Heo/oh-my-claudecode>.
