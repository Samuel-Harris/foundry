# pstack

poteto's agent workflow: a playbook router, review and design skills, and one-rule engineering principles.

## What it installs

| Primitive | Name | Purpose |
| --- | --- | --- |
| Skill | `benchmark-checklist` | Vet a performance measurement before you report or act on it. |
| Skill | `blast-radius` | Find what a change could break beyond the diff, and prove the one fact that makes it safe by running real code. |
| Skill | `bro` | Restate the last message in plain human language, with no jargon. |
| Skill | `how` | Explain how code works now: architecture, runtime flow, and where new code should live. |
| Skill | `in-your-own-words` | Restate what the agent thinks the user's goals and problem are. |
| Skill | `interrogate` | Have adversaries on different models try to break a change, keeping only findings a run proves. |
| Skill | `ketchup` | Catch the user up on what changed in this chat since their last message, with every waiting decision listed. |
| Skill | `ketchup-video` | Catch the user up like `ketchup`, as a short subtitled video of slides. |
| Skill | `no-comments` | Spawn Comment Sicko, fix accepted findings, and offer encodings for claimed constraints. |
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
| Skill | `sharpen` | Rewrite a prompt to make the task deeper, not bigger, without doing the task. |
| Skill | `tdd` | Write the failing test first when a cheap local test path exists. |
| Skill | `teach` | Explain a body of work plainly by running `how` and `why` and weaving the results together. |
| Skill | `typescript-best-practices` | Apply TypeScript rules when reading or editing `.ts` or `.tsx` files. |
| Skill | `unslop` | Cut AI tells from any writing. |
| Skill | `why` | Explain why code is shaped the way it is from source control and every available evidence source. |
| Agent | `comment-sicko` | Read-only comment reviewer that keeps only comments the code cannot replace. |

## Install

```bash
apm install Samuel-Harris/foundry/packages/pstack#v0.1.0 --target cursor,claude,copilot
```

## Targets

Deployed to `cursor`, `claude` and `copilot`.

## Upstream

This package ports [pstack](https://github.com/cursor/plugins/tree/main/pstack) by Lauren Tan, released under the MIT licence (see [`LICENSE`](LICENSE)), from upstream commit `c742dd6`. The port is adapted: prose is in British English, and tool, path and feature names are target-neutral so the same source deploys to Cursor, Claude Code and GitHub Copilot. It omits upstream's `benny` automation pack.
