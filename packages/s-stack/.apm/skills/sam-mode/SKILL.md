---
name: sam-mode
description: "Run one large feature as a group of cooperating Claude Code sessions (a spec writer, an orchestrator, a planner and one session for each phase), each in its own git worktree and tmux pane, with verified and reviewed draft pull requests for each phase. Use for /sam-mode start <feature> or /sam-mode <role>. Needs Claude Code with cross-session messaging, tmux and workmux. Not for small patches or minor bug fixes, which one poteto-mode session handles."
---

# Sam mode

s-stack runs one large feature as a group of Claude Code sessions. A spec writer turns the developer's idea into a feature roadmap, an orchestrator starts a planner and one session for each phase, and each phase opens draft pull requests once agents have verified and reviewed it. s-stack adds roles, shared artefacts and handoffs to p-stack's `poteto-mode` skill and replaces none of it.

## When to use it

Use it for a large feature that splits into several phases, some of which can run at the same time. Do not use it for a small patch or a minor bug fix. One session in `poteto-mode` handles those.

## First, read poteto-mode

Read `../poteto-mode/SKILL.md`, relative to this skill's directory, before anything else. `poteto-mode` sets `disable-model-invocation: true`, so the Skill tool cannot load it. Follow it for how to work. The handbook for your role adds only what is specific to s-stack.

## The invocation

There are two forms.

- `/sam-mode start <feature>`. With the repository root as the working directory, run `scripts/launch.sh --feature <feature> --role spec` from this skill's directory and report its output. Do nothing else.
- `/sam-mode <role> feature=<feature> phase=<phase> update=<n> roadmap=<path> plan=<path> orchestrator=<feature>-orchestrator`. This is the first prompt the launcher types, and `-` means an empty value. Take the role, read its handbook, then read the roadmap and the plan the prompt names.

`<feature>` is the feature's kebab-case name. `<phase>` is a phase id from the feature plan. `update` is a roadmap update number, set only for a spec writer that edits an existing roadmap. `orchestrator` is the orchestrator's session name, the address for every report.

## Roles and handbooks

Main sessions take the role from their first prompt. Subagent roles have no launcher role. The phase session points each subagent at its handbook. Paths are relative to this skill's directory.

| First-prompt role | Handbook |
| --- | --- |
| `spec` | `handbooks/spec-writer.md` |
| `orchestrator` | `handbooks/orchestrator.md` |
| `planner` | `handbooks/planner.md` |
| `phase` | `handbooks/phase-session.md` |
| None, verifier subagent | `handbooks/verifier.md` |
| None, reviewer subagents | `handbooks/reviewer.md` |
| None, PR creator subagent | `handbooks/pr-creator.md` |

## Rules for every main session

- Work the way `poteto-mode` says. Your handbook adds only what s-stack needs.
- Orchestrate your own part. Hand bulk reading and writing to subagents and keep their summaries in your own context.
- Write only the files your role owns. The artefact table below names each owner.
- The developer talks to the spec writer and the orchestrator. Every other session sends its questions for the developer to the orchestrator.
- The developer can still type into any session. Follow a direct instruction. Report it to the orchestrator when it changes the phase's scope or a recorded decision.

## Shared rules

Three placeholders recur. `<feature>` is the feature's name, `<id>` is the roadmap's directory name `<date-time>-<feature>`, and `<phase>` is a phase id.

### Artefacts

| Artefact | Path | Writer |
| --- | --- | --- |
| Feature roadmap | `.foundry/feature-roadmaps/<id>/` | Spec writer. The orchestrator writes only `run-decisions.md` in it. |
| Feature plan | `.foundry/plans/<id>/README.md` | Planner |
| Phase plan | `.foundry/plans/<id>/phases/<phase>.md` | That phase's session |
| Status file | `.foundry/plans/<id>/status/<phase>.md` | That phase's session |
| Tracker | `.foundry/plans/<id>/status/orchestrator.md` | Orchestrator |
| Status board and architecture page | Published pages, addresses in the tracker | Orchestrator |

- Every file under `.foundry/` has one writer.
- A commit never mixes files under `.foundry/` with other files.
- Git tracks `.foundry/` on the orchestrator branch and every branch cut from it. A pull request branch never contains it. A repository that uses s-stack must not ignore it.

### States

Every phase moves through Spec, Plan, Implement, Verify, Review, PR and Done.

- A phase moves forward one state at a time and skips none. It can move back any number of states.
- Only the phase session changes its phase's state, by committing its status file.
- A verdict names the code head it covers. A new code head needs new verdicts. The reference file defines the code head.
- The orchestrator merges a phase only when the newest verify verdict is VERIFIED and the newest review verdict is CLEAR, both for the current code head.

### Branches

| Branch | Name | Cut from |
| --- | --- | --- |
| Default branch | Resolved from the repository | |
| Orchestrator branch | `<feature>` | The default branch, when the feature starts |
| Phase branch | `<feature>-phase-<phase>` | The orchestrator branch, when the phase starts |
| Pull request branch | The repository's convention | The default branch, or the branch of the pull request it depends on |

Never assume the default branch is `main`. Resolve it, for example with `gh repo view --json defaultBranchRef --jq .defaultBranchRef.name`.

### Pull requests

- Every pull request is a draft. s-stack never marks one ready for review and never merges one into the default branch. The developer does both.
- The PR creator's handbook owns the split, the dependencies and the proof that the pull requests equal the phase diff.

### Doors

- The developer decides every one-way door. Send a decision request to the orchestrator and continue with the work the decision does not affect.
- Decide a two-way door yourself and record it in your own file. Raise it when the choice is architectural, nuanced or not obvious.

## Where to read next

| To learn | Read |
| --- | --- |
| The status file header, the messages and decision requests | [references/status-and-messages.md](references/status-and-messages.md) |
| Everything specific to one role | That role's handbook, from the table above |
