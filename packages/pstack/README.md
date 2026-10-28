# pstack

poteto's agent workflow: a playbook router, review and design skills, and one-rule engineering principles.

## What it installs

| Primitive | Name | Purpose |
| --- | --- | --- |
| Skill | `architect` | Sketch types, signatures and module structure before code, then stay in the loop while implementation fills in. |
| Skill | `arena` | Spawn parallel candidates at the same task, pick a base, and graft the strongest parts of the losers into it. |
| Skill | `automate-me` | Draft or revise a personal `-mode` skill from the user's own working history. |
| Skill | `benchmark-checklist` | Vet a performance measurement before you report or act on it. |
| Skill | `blast-radius` | Find what a change could break beyond the diff, and prove the one fact that makes it safe by running real code. |
| Skill | `bro` | Restate the last message in plain human language, with no jargon. |
| Skill | `correct` | Find the mistakes agents keep repeating in a repository and make each one impossible. |
| Skill | `create-formal-verification-skill` | Generate a project-local skill that formally verifies the code where a bug costs most and tests reach least. |
| Skill | `create-verification-skill` | Generate a project-local verification skill that drives the app the way a user does. |
| Skill | `figure-it-out` | Design an auditable, bespoke playbook when no narrower one fits. |
| Skill | `how` | Explain how code works now: architecture, runtime flow, and where new code should live. |
| Skill | `in-your-own-words` | Restate what the agent thinks the user's goals and problem are. |
| Skill | `interrogate` | Have adversaries on different models try to break a change, keeping only findings a run proves. |
| Skill | `ketchup` | Catch the user up on what changed in this chat since their last message, with every waiting decision listed. |
| Skill | `ketchup-video` | Catch the user up like `ketchup`, as a short subtitled video of slides. |
| Skill | `maintain-formal-verification-skill` | Bring a formal verification back in line with the code after the code changes. |
| Skill | `maintain-verification-skill` | Keep a verification skill and its feature map honest with source readers and one live pass. |
| Skill | `make-bot-ui` | Build a page whose buttons wake a Grok Bot over a webhook. |
| Skill | `no-comments` | Spawn Comment Sicko, fix accepted findings, and offer encodings for claimed constraints. |
| Skill | `poteto-mode` | Route a task to one of the bundled playbooks and run it with deliberate subagents and verified work. |
| Skill | `principle-attack-the-premise` | Test the shared premise of repeated failed fixes before writing another. |
| Skill | `principle-boundary-discipline` | Concentrate guards at system boundaries and keep business logic pure. |
| Skill | `principle-build-the-lever` | Build the tool that does or proves the work instead of working by hand. |
| Skill | `principle-encode-lessons-in-structure` | Encode a repeated instruction as a lint, flag, runtime check or script. |
| Skill | `principle-exhaust-the-design-space` | Build two or three competing prototypes before committing to an unprecedented design. |
| Skill | `principle-experience-first` | Choose user delight over implementation convenience. |
| Skill | `principle-explain-the-number` | Find what limits a measured number before trusting or reporting it. |
| Skill | `principle-fix-root-causes` | Trace each symptom to the first place the system went wrong and fix it there. |
| Skill | `principle-foundational-thinking` | Choose core types and data structures before writing logic. |
| Skill | `principle-guard-the-context-window` | Route bulk reading to subagents and keep summaries in the main thread. |
| Skill | `principle-laziness-protocol` | Bias towards deletion and the smallest change that solves the problem. |
| Skill | `principle-make-operations-idempotent` | Make commands and loops converge to the same end state across crashes and retries. |
| Skill | `principle-migrate-callers-then-delete-legacy-apis` | Migrate callers and delete the old API in the same wave. |
| Skill | `principle-minimize-reader-load` | Collapse layers and hidden state a reader must hold in their head. |
| Skill | `principle-model-the-domain` | Encode the domain in one structure instead of scattered conditionals. |
| Skill | `principle-never-block-on-the-human` | Proceed on reversible work and present the result. |
| Skill | `principle-outcome-oriented-execution` | Converge rewrites on the target architecture without throwaway compatibility states. |
| Skill | `principle-prove-it-works` | Verify against the real artefact, not a proxy or "it compiles". |
| Skill | `principle-redesign-from-first-principles` | Integrate a new requirement as if it had been foundational from day one. |
| Skill | `principle-separate-before-serializing-shared-state` | Eliminate shared writes before adding coordination. |
| Skill | `principle-sequence-verifiable-units` | Break work into small units that each end in a check. |
| Skill | `principle-subtract-before-you-add` | Remove dead weight before building on the simpler base. |
| Skill | `principle-test-behavior-not-implementation` | Assert what the code's users can observe, not its internals. |
| Skill | `principle-type-system-discipline` | Make illegal states unrepresentable and parse external data at boundaries. |
| Skill | `reflect` | Review the active transcript in parallel and route each learning to a concrete skill edit. |
| Skill | `setup-pstack` | Choose a model per role and a reasoning budget, and write the user-level model rule. |
| Skill | `sharpen` | Rewrite a prompt to make the task deeper, not bigger, without doing the task. |
| Skill | `show-me-your-work` | Keep a reviewable decision trail for long-running or unattended work. |
| Skill | `statechart` | Check a TLA+ model of a stateful system and draw it as a Mermaid statechart. |
| Skill | `swarm` | Fan out parallel workers over slices or races and return one report. |
| Skill | `tdd` | Write the failing test first when a cheap local test path exists. |
| Skill | `teach` | Explain a body of work plainly by running `how` and `why` and weaving the results together. |
| Skill | `technical-writing` | Apply a layered technical-writing standard to docs, RFCs, readmes, PR descriptions and commit messages. |
| Skill | `typescript-best-practices` | Apply TypeScript rules when reading or editing `.ts` or `.tsx` files. |
| Skill | `unslop` | Cut AI tells from any writing. |
| Skill | `why` | Explain why code is shaped the way it is from source control and every available evidence source. |
| Agent | `comment-sicko` | Read-only comment reviewer that keeps only comments the code cannot replace. |
| Agent | `poteto-agent` | Delegate subagent for code-writing and helper tasks spawned during a `/poteto-mode` run. |

## Install

```bash
apm install Samuel-Harris/foundry/packages/pstack#v0.1.0 --target cursor,claude,copilot
```

## Targets

Deployed to `cursor`, `claude` and `copilot`.

## Tests

The script test suites live under `tests/`, outside `.apm/`, so they are not deployed. CI runs each one.

- `tests/statechart/` tests the `statechart` skill's `scripts/`. Run them with Node.js 22.18 or later:

  ```bash
  cd packages/pstack/tests/statechart
  npm ci
  npm test
  ```

  The TLC tests skip unless `TLA2TOOLS` names a `tla2tools.jar` (CI uses TLC 1.7.4 and Temurin 25, the versions `scripts/run.ts` pins). On macOS, a `TMPDIR` that is reached through a symlink fails the relative-symlink launcher test; point `TMPDIR` at a resolved path.

- `tests/poteto-mode/` tests the `poteto-mode` skill's `scripts/` (the `watch-pr` CLI and `check-plan.mjs`). The test package is `package.json` at the package root, beside `.apm/`, because Bun resolves the runtime's `commander` import by walking up from `.apm/skills/poteto-mode/scripts/`; installing it here keeps `node_modules/` out of the deployed skill directory. Run them with Bun 1.3.5 or later:

  ```bash
  cd packages/pstack
  bun install --frozen-lockfile
  bun run typecheck:poteto-mode
  bun run test:poteto-mode
  ```

## Upstream

This package ports [pstack](https://github.com/cursor/plugins/tree/main/pstack) by Lauren Tan, released under the MIT licence (see [`LICENSE`](LICENSE)), from upstream commit `c742dd6`. The port is adapted: prose is in British English, and tool, path and feature names are target-neutral so the same source deploys to Cursor, Claude Code and GitHub Copilot. It omits upstream's `benny` automation pack.
