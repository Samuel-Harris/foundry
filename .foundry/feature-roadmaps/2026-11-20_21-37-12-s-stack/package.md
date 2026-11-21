# Package

This file says how s-stack ships in Foundry and which limits apply there. The repository's `AGENTS.md` owns Foundry's packaging rules. This file lists only what is specific to s-stack. Every fact about Foundry here was read on `origin/main`.

## What the package contains

The package is `packages/s-stack`. It ships one skill, `sam-mode`, with these parts:

- `SKILL.md`, a short router. It says when to use s-stack and when one session is enough. It states the rules that every session follows and maps each role to its handbook. It also handles `/sam-mode start <feature>`, which runs the launcher for the spec writer.
- One handbook for each role: spec writer, orchestrator, planner, phase session, verifier, reviewer and PR creator.
- One reference file that defines the status file's header and the messages. The handbooks point to it.
- The launcher script.
- The status board template.

`sam-mode` has the same shape as `poteto-mode`, which pairs a short `SKILL.md` with one file for each playbook.

## How sam-mode uses other skills

- **`poteto-mode`.** `sam-mode` adds to it and replaces none of it. `poteto-mode` sets `disable-model-invocation: true`, so a model cannot invoke it through the Skill tool. `sam-mode` therefore tells the session to read `poteto-mode`'s `SKILL.md` from the neighbouring skill directory.
- **How a session loads `sam-mode`.** The launcher types `/sam-mode <role>` as the first words of the session's first prompt. A relayed instruction to "use the skill" does not work. The November run's phase sessions declined one.
- **Skills that the handbooks name.** They are `deep-interview`, `quick-review`, `interrogate`, `summarise-pr`, the four verification skills in p-stack, and the Orchestrate playbook in `poteto-mode`. A handbook names another package's skill in words. It does not use a relative link, because `tests/structural/validate_primitives.py` resolves every relative link inside the source tree.
- **`automate-me`.** `sam-mode` is a mode skill in that skill's sense, so `automate-me` is the way to revise it from later transcripts. The research for this roadmap was its mining step. `automate-me` warns against codifying a pattern seen in one conversation, and all the evidence here comes from one feature run.

## Dependencies

s-stack declares every package whose skills or instructions its handbooks name.

| Package | What s-stack uses from it |
| --- | --- |
| `p-stack` | `poteto-mode`, `interrogate` and the four verification skills |
| `deep-interview` | The spec writer's interview |
| `review` | `quick-review` |
| `pr` | `summarise-pr` |
| `planning` | The plan handoff standard, which applies to `.foundry/plans/**/*.md` |
| `coding-style` | The pull request scope and size rules |

`default-stack` gains s-stack as a dependency. It already depends on `p-stack`.

Three rules in `AGENTS.md` constrain the manifests. The planner proves the final manifests with `bash tests/structural/run-tier1.sh` before it fixes them in the plan.

- **A package reached twice must not parent another.** `apm audit --ci` fails when a local package is reachable both directly and transitively and also has a dependency of its own. `planning` depends on `deep-interview` and `review`, and `default-stack` lists `planning` directly. If s-stack depends on `planning`, `default-stack` must reach `planning` through s-stack only. `p-stack` has no dependencies, so `default-stack` can reach it both ways.
- **The root manifest lists top-level packages only.** s-stack joins the root `apm.yml`. `p-stack` leaves it, because s-stack now reaches `p-stack`. The same holds for `planning` if s-stack depends on it. `tests/structural/check_root_manifest.py` enforces the rule.
- **Every changed package gets a version bump.** `python3 scripts/versioning.py bump` raises the version of s-stack's dependents.

Five more points follow from adding the package:

- `AGENTS.md` and `docs/COMPATIBILITY.md` state that the repository has nineteen packages. Both change to twenty.
- Git must not ignore `.foundry/` in a repository that uses s-stack. Foundry's `.gitignore` has no entry for it, and that stays so.
- The package declares the targets `cursor`, `claude` and `copilot`, like every other package. The Tier 1 suite installs each package for all three. The skill's description says that it needs Claude Code.
- The launcher gets tests of the guarantees in [coordination.md](coordination.md#the-launcher). They run in CI in their own job, as the tests in `packages/foundry-maintenance/tests` do.
- Prose is in British English and passes the repository's Markdown lint.

## Rules that keep maintenance low

1. **s-stack changes no file under `packages/p-stack`.** p-stack is a port that `scripts/pstack_upstream.py` merges from upstream. A local edit becomes a conflict at every sync.
2. **A handbook points to the skill or playbook that owns a rule.** It states only what s-stack adds. When p-stack improves a rule, s-stack inherits the improvement.
3. **Each fact has one home.** The status file's header and the messages are in the reference file. The pull request rules are in the PR creator's handbook. The tick checklist is in the orchestrator's handbook.
4. **Each outside tool is named in one place.** The launcher holds the workmux, tmux and `claude` commands. The PR creator's handbook holds the `gh stack` commands. The orchestrator's handbook holds the tick, the push notification and the two pages.
5. **The always-loaded text has a budget.** `SKILL.md` stays at or under 150 lines, and each handbook at or under 200.
6. **No code beyond the launcher and the template.** A proposal for a third piece of code states which reminder or failure it removes.

Rule 4 matters because these tools change quickly. workmux is at version 0.1.283. Cross-session messaging needs Claude Code 2.1.224 or later. `gh stack` and the page database are recent features.

## When the package is done

- The Tier 1 suite, the primitive validator and the launcher's tests pass.
- s-stack has run one real feature with at least three phases, one of which depends on another, and that run meets the six checks in [README.md](README.md#what-must-be-true-when-it-works).
- The handbooks are revised from that run's transcripts.

## Experiments for the planner

The spec writer could not settle these by reading. Each needs a short experiment before the plan depends on it.

| Question | Why it matters |
| --- | --- |
| Do the manifests in [Dependencies](#dependencies) pass the Tier 1 suite? | The audit rule above can force a different dependency shape. |
| Can a subagent start subagents on this host? | It decides whether the verifier and the PR creator run their skills themselves. See [roles.md](roles.md#what-is-still-unproven). |
| Do the status board's database writes and the architecture page's updates run without a permission prompt? | A prompt every 20 minutes would break the first requirement. |
| Can Claude's built-in Data page type show the Needs you list and the pull request dependencies? | If it can, it replaces the template and removes that code. |
| How does the PR creator prove that the pull requests equal the phase diff? | The check is the main safeguard of decision D3. |
