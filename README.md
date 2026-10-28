# Foundry

![CI](https://github.com/Samuel-Harris/foundry/actions/workflows/ci.yml/badge.svg)

![Foundry](assets/foundry-logo.png)

Foundry is a collection of 62 agent skills, 4 subagents and 4 instructions distributed as [APM](https://microsoft.github.io/apm/) packages for Cursor, Claude Code and GitHub Copilot. Install the whole stack in one command, or pick the individual packages you need.

## What this is

This repository was previously a Cursor plugin marketplace. It is now an APM monorepo of 18 independently installable packages. Every primitive has a single target-neutral source, and APM handles the per-target directory and frontmatter translation at install time — there are no per-target variants to keep in sync.

## Prerequisites

Install APM by following the [APM installation guide](https://microsoft.github.io/apm/quickstart/#1-install-apm). Beyond that, this repository only needs:

- **Git.** Required by APM for remote resolution.
- **An explicit target list.** Every command below passes `--target cursor,claude,copilot`. APM's filesystem auto-detection is never relied upon, and no tool directories are created merely to influence it.
- **Maintainers who need the exact pinned CLI version** should install `apm-cli==0.32.0`, the version pinned by this repository's CI:

  ```bash
  python -m pip install "apm-cli==0.32.0"
  ```

- **Pre-commit checks.** Once per clone, point Git at the tracked hooks:

  ```bash
  git config core.hooksPath .githooks
  ```

  The hook lints staged markdown with `markdownlint-cli2` 0.14.0, and runs `apm install --frozen` for a staged package and its dependents, failing if that rewrites `apm.lock.yaml`. CI's only job runs the same script. The lockfile half requires `apm-cli==0.32.0`. See `AGENTS.md`.

## Install

The default stack, via the meta-package:

```bash
apm install Samuel-Harris/foundry/packages/default-stack#v0.1.0 --target cursor,claude,copilot
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

| Package            | Contents                                                                                                                                                                  | Purpose                                                                                     |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| `coding-style`     | instructions: `compatibility-surface-gate`, `software-engineering-rules`                                                                                                  | Core engineering rules and compatibility guardrails for agent-written code.                 |
| `cursor-usage`     | skills: `cursor-cost-review`                                                                                                                                              | Analyse Cursor spend from a usage export and local transcripts, and rank ways to reduce it. |
| `deep-interview`   | skills: `deep-interview`                                                                                                                                                  | Socratic requirement gathering with ambiguity gating before planning.                       |
| `default-stack`    | *no primitives*                                                                                                                                                           | Meta-package that installs the default Foundry stack.                                       |
| `execution`        | skills: `implement-linear-ticket`                                                                                                                                         | Take a Linear ticket to a merge-ready draft pull request.                                   |
| `explore`          | agents: `explore`                                                                                                                                                         | Thorough read-only codebase search with cross-module reasoning.                             |
| `git-diff`         | skills: `git-diff-all-changes-main`, `git-diff-committed-changes-main`, `git-diff-staged-changes-main`                                                                    | Read-only git diff summaries measured against a repository's main branch.                   |
| `handoff`          | skills: `handoff`                                                                                                                                                         | Produce a handoff document that lets another agent or session continue the work.            |
| `infrastructure`   | skills: `aws-architecture-diagram`                                                                                                                                        | AWS architecture diagrams rendered as Mermaid flowcharts.                                   |
| `planning`         | skills: `masterplan`; instructions: `plan-handoff-standard`                                                                                                               | Product vision authoring and the implementation-plan handoff standard.                      |
| `pr`               | skills: `babysit`, `code-tour`, `summarise-pr`                                                                                                                            | Pull request comprehension and merge-readiness babysitting.                                 |
| `pstack`           | skills: `benchmark-checklist`, `blast-radius`, `bro`, `how`, `in-your-own-words`, `interrogate`, `ketchup`, `ketchup-video`, `no-comments`, `principle-attack-the-premise`, `principle-boundary-discipline`, `principle-build-the-lever`, `principle-encode-lessons-in-structure`, `principle-exhaust-the-design-space`, `principle-experience-first`, `principle-explain-the-number`, `principle-fix-root-causes`, `principle-foundational-thinking`, `principle-guard-the-context-window`, `principle-laziness-protocol`, `principle-make-operations-idempotent`, `principle-migrate-callers-then-delete-legacy-apis`, `principle-minimize-reader-load`, `principle-model-the-domain`, `principle-never-block-on-the-human`, `principle-outcome-oriented-execution`, `principle-prove-it-works`, `principle-redesign-from-first-principles`, `principle-separate-before-serializing-shared-state`, `principle-sequence-verifiable-units`, `principle-subtract-before-you-add`, `principle-test-behavior-not-implementation`, `principle-type-system-discipline`, `sharpen`, `tdd`, `teach`, `typescript-best-practices`, `unslop`, `why`; agents: `comment-sicko` | Port of poteto's pstack: a playbook router, review and design skills, and engineering principles. |
| `repo-init`        | skills: `monorepo-init`, `terraform-monorepo-init`                                                                                                                        | Scaffold a new repository or monorepo with evidence-based agent guidance.                   |
| `repo-maintenance` | skills: `agents-md`, `generate-agent-docs`, `optimise-agent-config`; instructions: `keep-agent-mds-up-to-date`                                                            | Keep AGENTS.md files and agent configuration accurate and lean.                             |
| `review`           | skills: `thermo-nuclear-code-quality-review`, `thermo-nuclear-review`, `thermos`; agents: `thermo-nuclear-code-quality-review-subagent`, `thermo-nuclear-review-subagent` | Branch-level correctness, security and maintainability audits.                              |
| `search`           | skills: `search-worktrees`                                                                                                                                                | Search the codebase across git worktrees.                                                   |
| `skill-creation`   | skills: `design-skill`                                                                                                                                                    | Design, draft, validate and iterate on agent skills.                                        |
| `ui`               | skills: `uncodixify`                                                                                                                                                      | Remove machine-generated UI slop and restore visual quality.                                |

Each package declares its sibling dependencies in `apm.yml`, so installing one package pulls in the primitives it references. See `[docs/DEPENDENCY-CONTRACTS.md](docs/DEPENDENCY-CONTRACTS.md)` for the dependency graph.

## Skills

| Skill                                | Package            | Trigger                                                                                                                                                           |
| ------------------------------------ | ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `cursor-cost-review`                 | `cursor-usage`     | Analyse an exported Cursor usage-events CSV together with local agent transcripts to find where Cursor spend goes and which changes would cut it without lo…      |
| `implement-linear-ticket`            | `execution`        | Take a Linear ticket to a merge-ready draft GitHub pull request. Resolve the issue, branch from origin/$BASE, plan, implement, run thermos, open a draft PR,…     |
| `git-diff-all-changes-main`          | `git-diff`         | Show all changes compared to origin/main. Use when the user asks for a full diff of every local change against main.                                              |
| `git-diff-committed-changes-main`    | `git-diff`         | Show staged and committed changes compared to origin/main. Use when the user asks for the diff of committed work against main.                                    |
| `git-diff-staged-changes-main`       | `git-diff`         | Show staged changes compared to origin/main. Use when the user asks for the diff of staged changes against main.                                                  |
| `handoff`                            | `handoff`          | Create a comprehensive AI context handoff document for long-running sessions. Use when the user asks for a handoff, a context handoff, or a session summary t…    |
| `aws-architecture-diagram`           | `infrastructure`   | Generate AWS architecture diagrams as Mermaid flowcharts with nested account/VPC subgraphs, numbered data-flow steps, and same-account placement. Use only wh…    |
| `deep-interview`                     | `deep-interview`   | Socratic deep interview with mathematical ambiguity gating before autonomous execution. Use when the user has a vague idea and wants thorough requirements ga…    |
| `masterplan`                         | `planning`         | Generate a holistic product vision from Linear tickets. Pulls backlog, to-do, and in-progress tickets and synthesises them into a status-agnostic overview. U…    |
| `babysit`                            | `pr`               | Keep a GitHub pull request merge-ready in a persistent loop by inspecting its current head, resolving unambiguous merge conflicts, addressing valid review co…    |
| `code-tour`                          | `pr`               | Walk through every change in a pull request or Git diff as a chat-only, logically ordered code tour with clickable code citations, commit and review context,…    |
| `summarise-pr`                       | `pr`               | Summarise provided PR change context into concise PR-description bullets. Use when the user asks for a PR description summary, major changes, or design decis…    |
| `benchmark-checklist`                | `pstack`           | Vet a perf measurement (limiter, tuning, limits, errors, repeatability, relevance, and whether the work happened) before you report or act on it. Use when yo…      |
| `blast-radius`                       | `pstack`           | Find what a change could break somewhere else before it ships, beyond the diff, and prove the one fact it's safe because of by running real code instead of w…      |
| `bro`                                | `pstack`           | Restate the last message in plain human language, with no jargon.                                                                                                   |
| `how`                                | `pstack`           | Use for "how does X work", code walkthroughs before changing something, and placement / ownership / layering questions ("where should this live", "which pack…      |
| `in-your-own-words`                  | `pstack`           | Restate in your own words what you think the user's goals are and what problem they're trying to solve. Use for /in-your-own-words.                                 |
| `interrogate`                        | `pstack`           | Use for "interrogate", "adversarial review", "multi-model review", "challenge this", "stress test this code", "find blind spots", or "tear this apart". Adver…      |
| `ketchup`                            | `pstack`           | Catch the user up on what changed in this chat since their last message, in plain words and small visuals. List every item waiting on them with what they nee…      |
| `ketchup-video`                      | `pstack`           | Catch the user up like /ketchup, with a short subtitled video of slides for what happened and the waiting calls as text under it. Use for /ketchup-video.           |
| `no-comments`                        | `pstack`           | Spawn Comment Sicko, fix accepted findings, and offer encodings for claimed constraints.                                                                            |
| `principle-attack-the-premise`       | `pstack`           | Apply when two or more fixes that share one premise have failed the same gate. Write the premise down and test it directly before you write another fix that …      |
| `principle-boundary-discipline`      | `pstack`           | Apply when wiring validation, error handling, or framework adapters. Concentrate guards at system boundaries (CLI, config, network, external APIs); trust int…      |
| `principle-build-the-lever`          | `pstack`           | Apply to any non-trivial work, not just bulk work: edits, migrations, analyses, checks. Build the tool that does it or proves it (codemod, script, generator,…      |
| `principle-encode-lessons-in-structure` | `pstack`           | Apply when you catch yourself writing the same instruction a second time, or notice a recurring correction. Encode the rule as a lint, metadata flag, runtime…      |
| `principle-exhaust-the-design-space` | `pstack`           | Apply when facing a novel UI interaction or architectural decision with no precedent in the codebase. Build 2-3 competing prototypes and compare side by side…      |
| `principle-experience-first`         | `pstack`           | Apply when product, UX, or feature-scope tradeoffs come up. Choose user delight over implementation convenience; ship fewer polished features over more rough…      |
| `principle-explain-the-number`       | `pstack`           | Apply before you measure, and before you trust, report, or act on a number you measured: a speedup, a regression, a throughput, a latency, or an eval result.…      |
| `principle-fix-root-causes`          | `pstack`           | Apply when debugging. Trace each symptom back to the first place the system went wrong and fix it there. A guard is a fix only when the state it handles is l…      |
| `principle-foundational-thinking`    | `pstack`           | Apply before writing logic: choosing core types and data structures, sequencing scaffold-vs-feature work, asking what concurrent actors share. Get the data s…      |
| `principle-guard-the-context-window` | `pstack`           | Apply when context is filling up: large outputs, long files, repeated reads, fan-out planning. Route bulk to subagents; keep summaries in the main thread, no…      |
| `principle-laziness-protocol`        | `pstack`           | Apply when refactoring, evaluating diff size, or tempted to add abstractions, layers, or signal threading. Bias towards deletion and the smallest change that…      |
| `principle-make-operations-idempotent` | `pstack`           | Apply when designing commands, lifecycle steps, or processing loops that run amid crashes, restarts, and retries. Converge to the same end state regardless o…      |
| `principle-migrate-callers-then-delete-legacy-apis` | `pstack`           | Apply when introducing a new internal API while old callers still exist. Migrate callers and delete the old API in the same wave instead of preserving compat…      |
| `principle-minimize-reader-load`     | `pstack`           | Apply when reviewing or shaping code that's hard to trace. Count layers between question and answer, and hidden state in the reader's head; collapse one-call…      |
| `principle-model-the-domain`         | `pstack`           | Apply when writing stateful logic, or when code branches a lot or repeats a shape assumption across files.                                                          |
| `principle-never-block-on-the-human` | `pstack`           | Apply when tempted to ask 'should I do X?' on reversible work.                                                                                                      |
| `principle-outcome-oriented-execution` | `pstack`           | Apply during planned rewrites and migrations with explicit phase boundaries. Converge on the target architecture; don't preserve smooth intermediate states w…      |
| `principle-prove-it-works`           | `pstack`           | Apply after completing a task, before declaring done. Verify against the real artefact (run the feature, read the actual value, inspect the diff), not a prox…      |
| `principle-redesign-from-first-principles` | `pstack`           | Apply when integrating a new requirement into an existing design.                                                                                                   |
| `principle-separate-before-serializing-shared-state` | `pstack`           | Apply when concurrent actors might write to the same file, branch, key, or state object. Eliminate the sharing first; serialise structurally only when one sh…      |
| `principle-sequence-verifiable-units` | `pstack`           | Apply to multi-step work (sweeps, migrations, runs of similar edits) and to how you stack commits and PRs. Break work into small units that each end in a ver…      |
| `principle-subtract-before-you-add`  | `pstack`           | Apply when sequencing an addition, refactor, or rewrite. Remove dead code, redundant validators, and stub references first, then build on the simpler base.         |
| `principle-test-behavior-not-implementation` | `pstack`           | Apply when you write, change, or keep a test. Assert what the code's users can observe, so that the test fails when that behaviour breaks and keeps passing w…      |
| `principle-type-system-discipline`   | `pstack`           | Apply when designing types, reviewing a function signature, or writing code in any statically-typed language. Make illegal states unrepresentable, brand sema…      |
| `sharpen`                            | `pstack`           | Make a task deeper, not bigger, then rewrite the prompt. Use for /sharpen.                                                                                          |
| `tdd`                                | `pstack`           | Use only when the user explicitly asks for TDD, a failing test, or a regression test, OR when the bug has an obvious cheap local test target. Skip when the t…      |
| `teach`                              | `pstack`           | Explain a body of work plainly so a person actually understands it. Runs the `how` and `why` skills and weaves what they find into one clear explanation. Use…      |
| `typescript-best-practices`          | `pstack`           | TypeScript best practices. Use when reading or editing any .ts or .tsx file.                                                                                        |
| `unslop`                             | `pstack`           | Cut AI tells from any writing.                                                                                                                                      |
| `why`                                | `pstack`           | Use for 'why does X work this way', 'why we picked Y', design rationale, regressions, postmortems, or data-backed thresholds. Discovers available MCPs and qu…      |
| `monorepo-init`                      | `repo-init`        | Initialise or retrofit a monorepo for structured agentic development through an interactive design interview and a working scaffold with machine-enforced mod…    |
| `terraform-monorepo-init`            | `repo-init`        | Use when a user asks to set up, bootstrap, restructure or extend an application-and-Terraform monorepo, including adding an application, service-owned infrastru… |
| `agents-md`                          | `repo-maintenance` | Initialise a codebase with hierarchical AGENTS.md documentation, and update it as the code changes.                                                               |
| `generate-agent-docs`                | `repo-maintenance` | Initialise comprehensive hierarchical AGENTS.md documentation across the entire codebase. Use when the user asks to generate or refresh AGENTS.md documentati…    |
| `optimise-agent-config`              | `repo-maintenance` | Audit a repository's agent configuration for the active targets (Cursor, Claude Code, GitHub Copilot) or evaluate whether a specific artefact (instruction, s…    |
| `thermo-nuclear-code-quality-review` | `review`           | Run an extremely strict maintainability review for abstraction quality, giant files, and spaghetti-condition growth. Use for a thermo-nuclear code quality re…    |
| `thermo-nuclear-review`              | `review`           | Comprehensive security and correctness audit of a branch's changes. Use for thermo nuclear, thermonuclear, or deep review requests, or branch/PR diff audits…     |
| `thermos`                            | `review`           | Launch both thermo-nuclear review subagents in parallel, then synthesise their findings. Use for thermos, double thermo review, or combined bug/security and…     |
| `search-worktrees`                   | `search`           | Find files, code, or content across all git worktrees of the current repository. Use when a search must cover every worktree, or when a naive find or grep ac…    |
| `design-skill`                       | `skill-creation`   | Design, draft, validate, and iterate on agent skills. Use when the user asks to create, design, improve, or test a skill, especially when the skill's goal, b…    |
| `uncodixify`                         | `ui`               | Guides UI design away from generic AI aesthetic patterns ("Codex UI") toward human-designed, functional interfaces inspired by Linear, Raycast, Stripe, and G…    |

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

All three targets support instructions, agents and skills, so no primitive is degraded or converted. Structural packaging is verified by the local Tier 1 suite; **runtime recognition and workflow behaviour are untested** — no client application is launched. See `[docs/COMPATIBILITY.md](docs/COMPATIBILITY.md)` for the per-package breakdown and the known limits of the pinned CLI.

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

`bash tests/structural/run-tier1.sh` runs the whole suite, including the scratch-consumer installs, the archive consumer and the tamper rejection, with every CLI call bounded by a hard timeout. `apm pack` refuses to bundle a package that declares a local `path:` dependency, so every package with sibling dependencies is pack-blocked from its committed manifest; the suite asserts that guardrail explicitly rather than skipping those packages.

CI's only job runs `.githooks/pre-commit` on the pull-request diff, or on the commits just pushed. The Tier 1 suite above is what to run locally before relying on a package change. See `[tests/acceptance.md](tests/acceptance.md)` for its assertions and `[docs/DEPENDENCY-CONTRACTS.md](docs/DEPENDENCY-CONTRACTS.md)` for the manifest and CLI contracts.

## Attributions

- Repo initialised from [https://github.com/cursor/plugin-template](https://github.com/cursor/plugin-template).
- The `pstack` package is adapted from [pstack](https://github.com/cursor/plugins/tree/main/pstack) by Lauren Tan (MIT), without its `benny` automation pack. See `packages/pstack/README.md`.
- The `generate-agent-docs` skill was created from the `deepinit` skill in [https://github.com/Yeachan-Heo/oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode).
