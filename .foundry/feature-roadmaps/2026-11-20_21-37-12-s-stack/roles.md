# Roles

s-stack has four kinds of main session and three kinds of subagent. A main session is its own Claude Code session with its own pane, and the developer can type into it. A subagent runs inside a phase session and returns a report.

| Role | Kind | Started by | Worktree |
| --- | --- | --- | --- |
| Spec writer | Main session | The developer, with `/sam-mode start <feature>`. The orchestrator starts one for a roadmap update when the developer asks. | The feature worktree for a new roadmap. Its own worktree for an update. |
| Orchestrator | Main session | The spec writer, once the developer approves the roadmap | The feature worktree |
| Planner | Main session | The orchestrator | Its own |
| Phase session | Main session, one live session for each phase | The orchestrator | Its own |
| Verifier | Fresh subagent | The phase session | The phase's |
| Reviewer | Fresh subagents | The phase session, through `interrogate` | The phase's |
| PR creator | Fresh subagent | The phase session | The phase's |

## Rules for every main session

- The session starts with `/sam-mode <role>` and follows `poteto-mode` for how it works. The role's handbook adds what is specific to s-stack.
- The session orchestrates its own part. It hands bulk reading and writing to subagents and keeps summaries in its own context.
- The session writes only the files that its role owns. The table in [workflow.md](workflow.md#shared-artefacts) names the owner of each artefact.
- The developer's contact points are the spec writer and the orchestrator. Every other session sends questions for the developer to the orchestrator.
- The developer can still type into any session. A session that receives a direct instruction follows it. It reports the instruction to the orchestrator when the instruction changes the phase's scope or a recorded decision.

## Spec writer

The spec writer turns the developer's idea into a feature roadmap. The whole workflow depends on that document.

**To write a new roadmap**, the spec writer does this:

1. It gathers the relevant context with subagents.
2. It interviews the developer with the `deep-interview` skill until the specification is clear enough to write.
3. It asks the developer about every one-way door.
4. It writes the roadmap. [workflow.md](workflow.md#shared-artefacts) says what a roadmap holds.
5. It waits for the developer's review and makes the changes the developer asks for.
6. On the developer's approval, it starts the orchestrator with the launcher.

**To update an existing roadmap**, the spec writer runs in a worktree cut from the orchestrator branch. It interviews the developer about the change in the same way and edits the roadmap on its own branch, so the sessions that are working keep reading the approved roadmap. Its branch changes nothing outside `.foundry/feature-roadmaps/`. When the developer is satisfied, it commits and tells the orchestrator what changed and which behaviour the change affects. The orchestrator merges the spec writer's branch.

The spec writer writes roadmap files and nothing else. It never writes `run-decisions.md`, which belongs to the orchestrator.

## Orchestrator

The orchestrator runs the feature. It decides which session does each piece of work and checks what each one produces. It never writes code.

It does these things:

- It starts the planner, then each phase session when the phase's dependencies are met. It never runs two phases that need the same exclusive resource.
- It runs a tick every 20 minutes. [coordination.md](coordination.md#the-tick) lists what a tick does.
- It keeps the status board and the architecture page current.
- It keeps the roadmap current. It records the decisions that the developer makes during the run in `run-decisions.md`, and it merges roadmap updates from spec writers.
- It asks the developer for a decision when a session needs one, and it passes the developer's instructions to sessions.
- It merges each phase branch under the rules in [workflow.md](workflow.md#branches).
- It watches the live state of every pull request and sends fix rounds to the owning phase session.
- It closes a phase's pane after the phase is merged, and starts the session again when the phase needs more work.
- It removes worktrees and panes when the feature ends.

It does not do these things:

- It does not edit code or resolve a conflict in code.
- It does not read phase plans, diffs or long pane output itself. It gives that reading to a fresh subagent and keeps the conclusion.
- It does not send instructions through a helper subagent. It sends its own messages.
- It does not relay an approval for a permission prompt. Only the developer approves.

The orchestrator's handbook points to the Orchestrate playbook in `poteto-mode` for supervision rules. It states only the differences. The workers are main sessions that the launcher starts, and each phase session runs its own gates.

## Planner

The planner receives the roadmap and writes the feature plan.

- It explores the code with subagents and settles open questions by prototype where it can.
- It sizes each phase for one Claude Code session and shapes the phases for parallel work.
- It gives each phase a set of owned paths. No two phases that can run at the same time own the same file.
- It names the resources that only one phase can use at a time, such as a port, a local stack or a GPU.
- It writes the contracts between phases, so that a phase can build against a neighbour that does not exist yet.
- It names the evidence that proves each phase done.
- It makes the feature's verification skill the first phase when no existing skill covers the feature.
- It reads the pull request rules in [workflow.md](workflow.md#pull-requests) before it shapes the dependencies, because a pull request stacks cleanly on one parent only.
- It sends every one-way door it finds to the orchestrator.

The planner works in its own worktree. Its branch changes nothing outside `.foundry/plans/`, and its prototypes stay on throwaway branches. The planner reports to the orchestrator when the feature plan is committed, and the orchestrator merges the planner's branch. The orchestrator starts the planner again when a roadmap update or a discovery changes the phases.

## Phase session

The phase session is the implementer. It receives the roadmap and the feature plan, and it owns one phase from Plan to Done.

- It writes the phase plan.
- It implements the plan, with delegates where that helps. It commits along the planned pull request split.
- It runs `quick-review` on each planned pull request layer and fixes the findings before it starts the next layer.
- It can run the verification skill itself at any time while it builds.
- It runs the Verify gate, then the Review gate, then the PR creator.
- It commits its status file at every change of state and tells the orchestrator. Such a commit holds nothing but files under `.foundry/`.
- It handles fix rounds and owns its pull requests until they merge.

Only one main session works on a phase at a time. When that session has ended, the orchestrator can start a new one for more work on the same phase. The new session reads the phase plan and the status file and continues from the recorded state.

Implementers are the only agents that edit product code. A phase session and its delegates edit code inside the phase's owned paths.

## Verifier

The verifier is a fresh subagent that has not seen the implementation conversation. It receives the roadmap, the feature plan, the phase plan and the phase diff.

- It reads `git diff` to see what the implementer built.
- It decides whether the phase needs verification and of which kind. A phase that needs none is rare, and the verifier states the reason when it finds one.
- It creates or updates the verification skill with p-stack's `create-verification-skill`, `create-formal-verification-skill`, `maintain-verification-skill` and `maintain-formal-verification-skill`.
- It adds the phase's checks in a file that only this phase owns, so phases never edit a shared verification file.
- It runs the checks against the running code and returns VERIFIED, NOT VERIFIED or INCONCLUSIVE with its evidence. INCONCLUSIVE is not a pass.

The verifier edits verification skill code and nothing else.

## Reviewer

The phase session runs p-stack's `interrogate` skill on the phase diff. The skill's reviewers are fresh subagents on different model families.

- The reviewers get the diff and the repository. They do not get the roadmap, a plan or the implementer's notes, and their brief tells them not to read `.foundry/`. The code must explain itself.
- A significant finding sends the phase back to Implement.
- With no significant finding open, the phase moves to PR.

The reviewers write nothing.

## PR creator

The PR creator is a fresh subagent. It receives the roadmap, the feature plan and the phase plan. It runs once both gates have passed for the code head.

- It splits the phase diff into pull requests under the rules in [workflow.md](workflow.md#pull-requests).
- It records each pull request's dependencies and chooses its base.
- It writes each description with `summarise-pr`.
- It opens every pull request as a draft.
- It applies restacks and carries fix commits to pull request branches when the phase session asks.

The phase session can run several PR creator subagents, for example one for each pull request. The PR creator moves existing commits. It does not change what the code does.

## What is still unproven

Two points need a short experiment during planning.

- The verifier and the PR creator are subagents. Some of the skills they use start subagents of their own, for example `maintain-verification-skill`. The Claude Code documentation appears to allow a subagent to start subagents, but that sentence was not read verbatim. If nesting fails, the phase session runs those skills itself and their subagents do the checking, as it already does for `interrogate`.
- `interrogate` gives each reviewer its own worktree. That worktree contains `.foundry/`, because the phase branch tracks it. Only the brief keeps the reviewers away from it.
