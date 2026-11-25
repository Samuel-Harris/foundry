---
name: sam-mode
description: "Run one large feature as a group of cooperating Claude Code sessions (a spec writer, an orchestrator, a planner and one session for each phase), each in its own git worktree and tmux pane, with verified and reviewed draft pull requests for each phase. Use for /sam-mode start <feature> or /sam-mode <role>. Needs Claude Code with cross-session messaging, tmux, workmux and `gh stack`. Not for small patches or minor bug fixes, which one poteto-mode session handles."
---

# Sam mode

s-stack runs one large feature as a group of Claude Code sessions. A spec writer turns the developer's idea into a feature roadmap, an orchestrator starts a planner and one session for each phase, and each phase opens draft pull requests once agents have verified and reviewed it. s-stack adds roles, shared artefacts and handoffs to p-stack's `poteto-mode` skill and replaces none of it.

## When to use it

Use it for a large feature that splits into several phases, some of which can run at the same time. Do not use it for a small patch or a minor bug fix. One session in `poteto-mode` handles those.

## First, read poteto-mode

Read `../poteto-mode/SKILL.md`, relative to this skill's directory, before anything else. The one exception is `/sam-mode start <feature>`, which runs the launcher and nothing else, without reading `poteto-mode`. `poteto-mode` sets `disable-model-invocation: true`, so the Skill tool cannot load it. Follow it for how to work. The handbook for your role adds only what is specific to s-stack.

## The invocation

Three placeholders recur. `<feature>` is the feature's kebab-case name. It must not contain `-phase-` or end with `-phase`, `-planner`, `-orchestrator`, `-spec` or `-spec-<n>`, because session names join their parts with hyphens, so a name ending in a role suffix or containing `-phase-` cannot be told apart from another session's name. The launcher refuses such a name. `<id>` is the roadmap's directory name `<date-time>-<feature>`, and `<phase>` is a phase id from the feature plan.

There are two forms.

- `/sam-mode start <feature>`. Run `<this skill's directory>/scripts/launch.sh --feature <feature> --role spec` with the repository root as the working directory and report its output. Do nothing else.
- `/sam-mode <role> feature=<feature> phase=<phase> update=<n> roadmap=<path> plan=<path> orchestrator=<feature>-orchestrator`. This is the first prompt the launcher types, and `-` means an empty value. Take the role, read its handbook, then read the roadmap and the plan the prompt names.

`update` is a roadmap update number, set only for a spec writer that edits an existing roadmap. `roadmap` is the feature roadmap's directory and `plan` the feature plan's `README.md`, each `-` until it exists. For a phase session outside the home repository, both are absolute paths into the home feature worktree. Read them there and never write them. `orchestrator` is the orchestrator's session name, the address for every report.

## Starting a session

Start every session after the first spec writer from a main session, never from a subagent, because a subagent can lack the pane. The spec writer starts the orchestrator, and the orchestrator starts the planner, phase sessions and update spec writers. Run these two commands with the repository root as the working directory:

```bash
<this skill's directory>/scripts/launch.sh --print-window
<this skill's directory>/scripts/launch.sh --feature <feature> --role <role> [--phase <phase>] [--update <n>] [--repo <path>] --window <window id>
```

The first prints `window=<window id>` for your own pane. Pass that value to the second. `--repo` names a checkout of the repository a phase session works in, when that is not the home repository, as the orchestrator handbook says. If either command fails, report its exit code and standard error, and do not start the session another way.

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

- Orchestrate your own part. Hand bulk reading and writing to subagents and keep their summaries in your own context.
- Write only the files your role owns. The artefact table below names each owner.
- The developer talks to the spec writer, the orchestrator, and the planner during an architecture review. Every other session sends its questions for the developer to the orchestrator.
- The developer can still type into any session. Follow a direct instruction. Report it to the orchestrator when it changes the phase's scope or a recorded decision.

## Rules for every session, subagents included

### Repositories

- A feature works in one or more repositories. Each is named by its GitHub `owner/name`, as `gh repo view --json nameWithOwner --jq .nameWithOwner` prints it. A single-repository feature is a feature with one repository.
- The home repository is the one where `/sam-mode start` ran. The roadmap names every repository and which is home. The feature plan's "Repositories" table gives each one's facts, and a session reads the row of its own repository.
- Every phase works in exactly one repository, which its plan entry names, and changes files in that repository only.
- The feature worktree is the worktree of a repository's orchestrator branch. The home one holds the spec writer and the orchestrator.
- Two repositories may be linked, by a shared API or as a library and its consumer. The feature plan's "Links" table names each link and its phases, and `handbooks/planner.md` defines its fields. A phase that a link names reads that row.

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
- The roadmap, the feature plan, the tracker and `run-decisions.md` live only on the home repository's orchestrator branch. A phase's phase plan, status file and evidence file live at the same paths on its phase branch, in its own repository, and merge into that repository's orchestrator branch.
- A commit never mixes files under `.foundry/` with other files. The exception is a merge of another branch, which brings both.
- `run-decisions.md` records the decisions taken during the run. Each row amends the roadmap until a roadmap update folds it in.
- Git tracks `.foundry/` on every repository's orchestrator branch and every branch cut from it. A pull request branch never contains it. No repository of the feature may ignore it.

### States

Every phase moves through Spec, Plan, Implement, Verify, Review, PR and Done.

- A phase moves forward one state at a time and skips none. It can move back any number of states.
- Only the phase session changes its phase's state, by committing its status file.
- A verdict names the code head it covers. A new code head needs new verdicts. The reference file defines the code head and the merge rule, which a phase checks before it moves to PR. `handbooks/orchestrator.md` owns the further checks the orchestrator makes before it merges.

### Branches

Every repository of the feature has its own default branch and its own orchestrator branch. Every other branch lives in one repository and is cut from that repository's branches.

| Branch | Name | Cut from |
| --- | --- | --- |
| Default branch | Resolved from the repository | |
| Orchestrator branch | `<feature>` | The repository's default branch: in the home repository when the feature starts, in any other when the launcher starts its first phase |
| Planner branch | `<feature>-planner` | The home orchestrator branch, when the planner starts |
| Update spec writer branch | `<feature>-spec-<n>` | The home orchestrator branch, when the update starts |
| Phase branch | `<feature>-phase-<phase>` | The orchestrator branch of the phase's repository, when the phase starts |
| Pull request branch | The repository's convention | The default branch, or the branch of the pull request it depends on |

Never assume a default branch is `main`. Resolve each one, for example with `gh repo view --json defaultBranchRef --jq .defaultBranchRef.name`.

Every orchestrator branch and every branch cut from one carry `.foundry/`. Push none of them, in any repository, to a public remote unless the developer says so. Pull request branches never contain `.foundry/`, and the PR creator pushes them.

### Pull requests

- Every pull request is a draft. s-stack never marks one ready for review and never merges one into the default branch. The developer does both.
- The PR creator's handbook owns the split, the dependencies and the proof that the pull requests equal the phase diff.

### Doors

- The developer decides every one-way door. A phase session or the planner sends a decision request to the orchestrator and continues with the work the decision does not affect. A subagent reports a one-way door to its phase session, which sends the request. The spec writer asks the developer directly.
- Decide a two-way door yourself and record it in your own file. Raise it when the choice is architectural, nuanced or not obvious.
- In AFK mode, [references/afk-mode.md](references/afk-mode.md) says who answers a raised door.

### tmux

The developer's own tmux server runs every pane of the run, theirs included. Inside a pane, `$TMUX` names that server, and tmux then ignores `TMUX_TMPDIR`, so `TMUX_TMPDIR=<dir> tmux kill-server` kills the developer's server.

- Never run `kill-server`, and never end a session, window or pane that the run did not start. The launcher's `--close` is how a pane the run started is closed.
- To reach any other server, pass `-S <full socket path>`, or unset `TMUX`, and first confirm the target with `tmux -S <path> list-sessions -F '#{socket_path}'`.
- A test that starts tmux runs it with `env -u TMUX` and `-S` into its own temporary directory, and on teardown kills only that server, also when the test fails.

## Where to read next

| To learn | Read |
| --- | --- |
| The status file header, the messages and decision requests | [references/status-and-messages.md](references/status-and-messages.md) |
| Everything specific to one role | That role's handbook, from the table above |
| AFK mode, for the orchestrator | [references/afk-mode.md](references/afk-mode.md) |
