# Coordination

This file defines how sessions start, how they are addressed, what they tell each other, and how the orchestrator keeps the developer informed. [workflow.md](workflow.md) defines the states and the branches that this file refers to.

## Session names

The launcher gives every session a fixed name. The name is the session's address for messages. For a session with its own worktree, the name is also the branch and the workmux handle, so `workmux status`, `workmux send` and `workmux capture` reach it by the same name.

| Session | Session name | Worktree and branch |
| --- | --- | --- |
| Spec writer, new roadmap | `<feature>-spec` | The feature worktree, on the orchestrator branch `<feature>` |
| Orchestrator | `<feature>-orchestrator` | The feature worktree, on the orchestrator branch |
| Planner | `<feature>-planner` | Its own, named as the session |
| Spec writer, roadmap update | `<feature>-spec-<n>` | Its own, named as the session |
| Phase session | `<feature>-phase-<phase>` | Its own, named as the session |

The developer starts a feature by typing `/sam-mode start <feature>` in any Claude Code session in the repository. That session runs the launcher for the spec writer and does nothing else. The first spec writer ends once the orchestrator has started, so the feature worktree has one live session at a time.

## The launcher

The launcher is one script. It is the only part of s-stack that knows the workmux, tmux and `claude` command lines. The orchestrator starts every other session through it, and `/sam-mode start` runs it for the first spec writer.

It takes the feature, the role, the phase for a phase session, and the tmux window to use. It then does this:

1. It creates the role's worktree when the worktree does not exist, with `workmux add --headless`, so the project's workmux file operations and hooks run. It cuts the feature worktree from the default branch and every other worktree from the orchestrator branch.
2. It splits a new pane in the given window and tiles the window again.
3. It starts `claude --name <session name>` in that pane with the role's first prompt.

The first prompt is fixed text built from the launcher's inputs. It is `/sam-mode <role>`, followed by the feature, the phase, the roadmap path, the plan path and the orchestrator's session name. The orchestrator writes no brief. Everything specific to a phase is in the feature plan.

The launcher guarantees these things:

- It never opens a new tmux window.
- It starts at most one live session for a name. When one is alive, it reports the pane and changes nothing.
- When the worktree exists and no session is alive, it starts a new session there under the same name.
- It takes the window as an input. The orchestrator records its own window when it starts, because a command run from a subagent or a background task can lack `$TMUX_PANE`.
- It reports tmux's error when the window has no room for another pane.
- It fails with a clear message when tmux, workmux or the `claude` command is missing.

## Messages

Sessions talk through Claude Code cross-session messaging, addressed by session name. A message wakes its receiver. It is never the record. A sender commits the fact to its own file first and then sends the message, so a lost message costs time and loses no information.

A phase session, the planner or a spec writer sends these to the orchestrator:

| When | The message carries |
| --- | --- |
| The session starts | Its session name and branch |
| A phase changes state | The new state and the code head |
| The session needs a decision | The decision request, as [workflow.md](workflow.md#one-way-and-two-way-doors) defines it |
| The session is blocked | What it waits for |
| A phase's pull requests are open | Their numbers and each one's dependencies |
| The developer gave it an instruction that changes scope | The instruction |
| The planner has finished | The branch and commit to merge |
| A spec writer has an approved update | The branch and commit to merge, what changed, and the behaviour that the change affects |

The orchestrator sends these:

| When | The message carries |
| --- | --- |
| The developer has decided | The answer and the request that it answers |
| The developer gave an instruction | The instruction, in the developer's words |
| The orchestrator branch changed under a live phase | A request to merge it |
| A fix round starts | The pull request and its comments, or the failed check |
| The developer asked for a restack | The pull request and its new base |
| A roadmap or plan change touches a phase | The state to move back to and what changed |
| A phase's pane is about to close | A request to commit and stop |

Four rules apply:

- Each handbook names the orchestrator's session as the source of task direction. A session acts on the orchestrator's messages within its own permissions.
- A message never grants a permission.
- Two phase sessions can message each other to settle an interface between their phases. They tell the orchestrator only when the outcome changes the plan or the roadmap.
- Every session of a feature runs in the same permission mode. Claude Code holds a message for approval when the receiver runs in a bypass mode and the sender does not.

## Status files

A status file holds these facts about one phase:

- The phase, its state and the time of the last change.
- The phase branch and its code head.
- Each verdict, with the gate, the result, the code head it covers and where the evidence is.
- Each pull request, with its number, branch, base and the open pull requests it depends on.
- The decisions made for this phase, each with its door type.
- What the phase waits for, when it waits.

The facts that the status board needs sit in a fixed header that a program can parse. Notes go below the header.

The phase session commits the file on its phase branch. The orchestrator reads it through git, for example with `git show <phase branch>:<path>`. Worktrees of one repository share their commits. The orchestrator therefore reads no file outside its own worktree, and no session writes outside its own.

## The tracker

The tracker is the orchestrator's own file, committed on the orchestrator branch. It holds the tmux window, the addresses of the status board and the architecture page, the commit that the architecture page describes, the live sessions and their panes, the open decision requests, the pull requests under watch and the time of the last tick. A restarted orchestrator reads the tracker and the status files and continues.

## The tick

The orchestrator arms a recurring 20-minute tick when it starts. The tick's prompt is one fixed sentence that tells the orchestrator to run the tick checklist in its handbook. The checklist lives in the handbook, so a change to a step never means that the tick is created again.

A tick does this:

1. **Reconcile.** It reads every status file through git, `workmux status`, and the live state of every open pull request. It trusts these over any message or report.
2. **Start.** It starts each phase whose dependencies are merged and checked and whose exclusive resources are free.
3. **Merge.** It merges each phase that reports its pull requests open and holds both verdicts for its code head. It then has a fresh subagent check the merged branch.
4. **Unblock.** It asks the developer about open decision requests and forwards answers. It notifies the developer of each session that waits on a permission prompt. It sends fix rounds for new review comments and failed checks. It replaces a session that has stalled.
5. **Record.** It records new decisions in `run-decisions.md` and updates the tracker.
6. **Publish.** It writes the changed rows and the tick time to the status board. When a phase merged or the roadmap changed, it has a subagent update the architecture page.
7. **Report.** It ends without a reply unless something needs the developer. Then it says what, in a few lines.

The orchestrator gives the bulk reading in a tick to a subagent and keeps the conclusions.

Two limits in Claude Code shape the tick. A scheduled task fires only while the session is running and idle. A recurring task expires seven days after it is created. The orchestrator therefore arms the tick at every start and creates it again before seven days pass, and the status board shows the time of the last tick.

## The status board

The status board answers four questions, in this order. What needs the developer now? What can the developer review? Where is each phase? Is the orchestrator alive?

| Section | Shows |
| --- | --- |
| Needs you | Open decision requests with their door type and waiting time. Sessions that wait on a permission prompt, with the pane. Restack opportunities. |
| Ready for your review | Draft pull requests in the order to review them, dependencies first, with links. |
| Pull requests | Every pull request, its state, its checks and the pull requests it depends on. |
| Phases | Every phase, its state, whether it is queued or blocked, whether its session is live, and the time of its last change. |
| Recent changes | The latest state changes, newest first. The list has a fixed length. |
| Heartbeat | The time of the last tick. The page marks itself stale when that time is more than 40 minutes old. |

These rules apply:

- The orchestrator publishes the board once for each feature, from the template that s-stack ships. After that it updates the board's database and does not publish the page again.
- Every value comes from a status file, `workmux status` or the forge. The board holds no free-text status that someone must keep in step by hand.
- A phase's state is one of the seven state names and nothing else.
- The board reads on a phone.
- The board links to the architecture page. It leaves out demo scripts, compute notes and any explanation of the architecture.

## The architecture page

The architecture page explains what the feature is and how its parts fit together. It serves the developer and anyone the developer shares it with. The status board says how the work is going. The architecture page says what is being built.

It shows these things:

- A map of the system and where the feature sits in it.
- The feature's components and the boundaries between them.
- The data model and the main flows.
- The rules that constrain the design, taken from the roadmap's decisions.
- For each part, whether it is planned or built. A part is built when the phase that owns it has merged into the orchestrator branch.
- The orchestrator branch commit that the page describes, and the time.

These rules apply:

- A subagent of the orchestrator writes the page and each update, so the orchestrator's context stays small.
- The page takes the intended design from the roadmap and the built design from the code on the orchestrator branch. An update covers what merged since the commit that the page last described.
- The page uses two words for progress, planned and built. For anything finer it links to the status board.
- The orchestrator publishes the first version when it starts, from the approved roadmap. It updates the page in every tick in which a phase merged or a roadmap update was merged, and once more when the feature ends.
- s-stack ships no template for this page. Each feature's architecture differs, so the subagent designs the page for the feature.
- The page is private until the developer shares it.

## Permission prompts

Phase sessions run in the developer's normal permission mode. Nothing is approved in advance.

On each tick, and whenever a session reports that it is blocked, the orchestrator checks `workmux status`. For each session that waits on a prompt, the orchestrator sends the developer a push notification that names the pane and the action, and lists the session under Needs you. The developer approves in that pane.

`workmux send` refuses a session that waits on a dialog, so the orchestrator cannot answer a prompt by accident.

## Restarts

| Session | A restart loses | The new session rebuilds from |
| --- | --- | --- |
| Orchestrator | Its conversation and the tick | The tracker, the status files, `workmux status` and the forge. It arms the tick again. |
| Phase session | Its conversation | The phase plan, the status file and the phase branch |
| Planner or spec writer | Its conversation | Its committed files |

The launcher starts the new session under the same name, so every other session keeps the same address. A message sent while a session was down is lost. The sender's committed file still holds the fact, and the next tick finds it.

## Parallel work

- **No fixed limit on live phase sessions.** The orchestrator starts every phase that is ready. The dependencies between phases and the exclusive resources bound how many run at once. The developer can tell the orchestrator to hold phases back at any time.
- **Exclusive resources.** The feature plan names each resource that only one phase can use at a time. The orchestrator does not run two phases that need the same one together.
- **Closed panes.** The orchestrator closes a phase's pane once the phase is merged into the orchestrator branch. The worktree stays until the phase is Done. A fix round starts a new session in it.
- **A full window.** When tmux has no room for another pane, the launcher says so. The orchestrator starts the phase when a pane closes.
