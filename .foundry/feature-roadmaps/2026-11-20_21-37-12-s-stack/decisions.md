# Decisions

Each decision states its door type, who decided it, the reason and the alternatives that lost. A one-way door is hard to reverse once committed to. A two-way door is not. Codes such as R4 or X3 point to entries in [evidence.md](evidence.md).

The developer decided in two sittings on 20 November 2026. "In the interview" means an answer to one of the seven interview rounds. "On review" means the developer's replies to the first two versions of this roadmap. "The spec writer" means a call made while writing. "The first-draft rubric" is the developer's `s-stack-first-draft-rubric.md`. It sits at the root of the worktree in which this roadmap was written and is kept out of git, because it links to private repositories.

## D1. Four kinds of main session, three kinds of subagent

- **Door.** Two-way.
- **Decided by.** The developer, in interview rounds 1, 3 and 5.
- **Decision.** The spec writer, the orchestrator, the planner and each phase session are main sessions. The verifier, the reviewers and the PR creator are fresh subagents of the phase session.
- **Why.** The November run needed three kinds of session: one that wrote the roadmap, one orchestrator, and one for each phase (R1, R7). Every further main session costs a pane, a first prompt and a handoff. A checker stays independent of the author in two ways. It is a fresh subagent that never saw the implementation conversation, and the orchestrator applies the merge rule in D9.
- **Rejected.** The first-draft rubric's seven main sessions, which give each phase three to four times the panes and handoffs. One verifier session for the whole feature, which the November run effectively had in its phase 00 session. That session spent the night bringing one shared script back in step after each merge (R8).

## D2. Independent sessions with cross-session messaging

- **Door.** One-way. The launcher, the messages and every handbook assume it.
- **Decided by.** The spec writer, because the developer asked for a recommendation. The developer read it on review and did not dispute it.
- **Decision.** Every session is an independent Claude Code session in its own pane. Sessions talk through cross-session messaging. s-stack does not use agent teams.
- **Why.** Agent teams fail two requirements. Each phase needs its own worktree, and the agent teams page says "Two teammates editing the same file leads to overwrites" and never mentions a worktree for a teammate. The run must survive restarts, and the page says "`/resume` and `/rewind` do not restore in-process teammates". The page also says "No nested teams", "One team per session", and that the feature is "experimental and disabled by default" (C1). Cross-session messaging carried the November run, with about 470 messages from the orchestrator alone (R3). The one fault it showed, a changed address after a restart, has a fix that an experiment confirmed (X3).
- **What agent teams do better.** "Teammate permission prompts appear in the lead session" (C1). s-stack covers that need with notifications (D10).
- **Rejected.** Agent teams. Subagents inside one session, as p-stack's Orchestrate playbook runs them, because the developer cannot type into a subagent and wants long-lived sessions to visit. `workmux send` as the message channel, because it types into a pane that the developer may be typing in. s-stack uses workmux to observe sessions, not to message them.

## D3. Phase branches from the orchestrator branch, pull requests split out after the gates

- **Door.** One-way. The launcher, the PR creator and the orchestrator's merge rules all build on it.
- **Decided by.** The developer, who proposed it in the interview: "branch phase worktrees off of the orchestrator branch, did the PR splitting (targetting the repo's default branch), then merged each branch into the orchestrator's branch before branching off the orchestrator branch to kick off phases that had depended on the phase we just finished". On review the developer saw the risk below and kept the model with its safeguards.
- **Decision.** [workflow.md](workflow.md#branches) states it.
- **Why.** The developer reviews each phase as soon as agents have verified and reviewed it. A phase that depends on others gets their code from the orchestrator branch without waiting for a human review. The November run built the whole feature on such a branch (R6).
- **The risk.** The PR creator builds a second copy of every change, on branches cut from the default branch. Agents verified the phase branch, not the copy. The two can differ, a fix round touches both, and a pull request branch first runs without the rest of the feature after the gates have passed. The instructions for `gh stack` in one of the developer's private repositories advise the opposite order. They say to plan the stack before any file is written, and not to split a finished change afterwards (T4).
- **The safeguards.** The phase plan names the split first and the implementer commits along it. The PR creator proves that the pull requests equal the phase diff. Each pull request passes the repository's checks on its own. Each pull request has one writer.
- **The alternative that removes the copy.** A phase builds directly as its pull request stack. Its first branch is cut from the default branch or from a parent's pull request branch, and its branches are the pull request branches. The orchestrator branch becomes a merged preview that nothing is cut from. This alternative needs no equality check. A phase with two unmerged parents then needs a base that merges both. Revisit it if the equality check or the fix rounds cause trouble in the first run.
- **Rejected.** One pull request at the end, because review waits for every phase. Pull requests that target the orchestrator branch with one large pull request at the end, because nothing reaches the default branch until then. Merging a phase straight after Review and before its pull requests exist, which would start dependent phases sooner. The developer's order stays, because a split that needs a code change would otherwise reach those phases as a fix round.

## D4. Dependencies are recorded for each pull request

- **Door.** Two-way.
- **Decided by.** The developer, in interview round 2: "The PRs should be created, but the PR creator should identify exactly which parent phase PRs the child phase's PRs are each dependent on, using gh stacks when there is a single dependency and explaining in the PR description when there are multiple dependencies." The spec writer added the limit below.
- **Decision.** [workflow.md](workflow.md#pull-requests) gives the rule for each case. The orchestrator shows a restack opportunity on the status board and acts when the developer asks.
- **The limit.** A `gh stack` is strictly linear. A pull request has one parent and at most one child (T4). A pull request therefore joins a stack only when the pull request it depends on has no other pull request stacked on it.
- **Consequence.** When two phases depend on the same parent, the second one's pull requests show the parent's changes in their diffs until the parent merges.
- **Rejected.** Holding a phase's pull requests until a parent merges. Restacking without being asked, because a restack changes a diff that the developer may be reading.

## D5. The plan has two levels

- **Door.** Two-way.
- **Decided by.** The developer, in interview round 5.
- **Decision.** The planner writes the feature plan. Each phase session writes its own phase plan when the phase starts.
- **Why.** A later phase is planned against code that exists. The orchestrator reads only the feature plan, which keeps its context small.
- **Rejected.** One planner that writes every phase's detail up front, because the detail for later phases goes stale. Planning in the spec writer's session, whose context is already full from the interview.

## D6. Files are the record, messages are wake-ups, and every file has one writer

- **Door.** One-way. Every handbook relies on it.
- **Decided by.** The spec writer, from the developer's requirement that the run survives restarts and from interview round 6, which chose one status file for each phase.
- **Decision.** A session commits a fact to its own file and then sends a message. The orchestrator reads status files through git.
- **Why.** Reports sent to the orchestrator's old address were lost in November (R4). Files with many writers caused merge conflicts, and the orchestrator allocated decision numbers by hand (R8). A phase session's edits to another worktree were blocked by the permission mode (R9), so a session writes only inside its own worktree and the orchestrator reads through git.
- **Rejected.** A shared decisions list or status table. State that the orchestrator writes on a phase's behalf. State that exists only in messages.

## D7. The launcher gives every session a fixed name

- **Door.** Two-way.
- **Decided by.** The spec writer.
- **Decision.** [coordination.md](coordination.md#session-names) lists the names. The launcher passes each one to `claude --name`.
- **Why.** Claude Code names an unnamed session itself, and the name changes when the session restarts (R4). A session started twice with `--name sstack-name-probe` was listed under that exact name both times (X3).

## D8. s-stack ships prose, one launcher and one status board template

- **Door.** Two-way.
- **Decided by.** The developer chose prose and one launcher in interview round 6, and accepted the template on review.
- **Why a launcher.** The November orchestrator's first `workmux add` started no agent (R2). workmux places a session in a new window or a new tmux session and has no mode for a pane in the current window (T1). An experiment showed that a headless worktree and a split pane meet the developer's preference and that workmux still tracks the session (X1).
- **Why a template.** The November orchestrator rebuilt its status page by hand, and the page's two copies of each phase's state came to disagree (B1). A template fixes the layout once.
- **Left out on purpose.** A command-line tool that enforces state changes, which the developer declined. A command that gathers the status board's data. A subagent gathers it on each tick. That command is the first code to add if ticks prove costly or unreliable.
- **Rejected.** Prose only, which leaves the launch and naming faults to recur.

## D9. The orchestrator merges on verdicts and then checks the merged branch

- **Door.** Two-way.
- **Decided by.** The spec writer.
- **Decision.** The orchestrator merges a phase only when its status file holds a verifier verdict and a reviewer verdict for the code head. After the merges in a tick, a fresh subagent runs the feature's verification skill on the orchestrator branch.
- **Why.** The first-draft rubric says that the states exist so that no step is missed, and in November the review step was mostly missed (R7). The phase session runs its own gates, so the merge rule is the check that does not depend on the author. The November orchestrator merged through a fresh checking subagent, which "caught a variable name that would have crashed [a] command" (R10).
- **Why the code head.** Recording a verdict is itself a commit. A verdict therefore names the latest commit that changes a file outside `.foundry/`, and a commit that only records status cancels nothing.
- **Cost.** One verification run for each tick that merged something.
- **Rejected.** Trusting the phase session's report. Fast-forward merges only, because each merge would then cancel the verdicts of every other phase that is ready.

## D10. Notify the developer of a waiting prompt and approve nothing in advance

- **Door.** Two-way.
- **Decided by.** The developer, in interview round 7.
- **Why.** A message "can't answer a pending permission prompt on your behalf" (C2). In November, sessions waited on prompts in windows that the developer was not watching (R9).
- **Rejected.** A list of approved actions for each feature. Showing waiting sessions on the status board without a notification.

## D11. A 20-minute tick with a prompt that never changes

- **Door.** Two-way.
- **Decided by.** The developer set the interval and the purpose in the first-draft rubric. The spec writer fixed the prompt.
- **Why.** The developer reminded the November orchestrator four times and designed its loop prompt (R5). Each new step meant deleting the scheduled task and creating it again (R5). A fixed prompt that points to a checklist in the handbook removes that work.

## D12. The status board is published once and updated through its database

- **Door.** Two-way.
- **Decided by.** The spec writer. The first-draft rubric asked for a better design than the prototype.
- **Decision.** [coordination.md](coordination.md#the-status-board) lists the sections and the rules.
- **Why.** The prototype has no section for what needs the developer, names one pull request, stores each phase's state twice, and shows one hand-typed time (B1). The November orchestrator published its status pages 42 times (R5). The developer's account can give a page a database that survives a new publish (B2).
- **Not chosen.** Claude's built-in Data page type. Nobody has tested whether it can show the Needs you list and the pull request dependencies. If it can, it replaces the template.

## D13. Git tracks `.foundry/` on the orchestrator branch, and no pull request branch contains it

- **Door.** Two-way.
- **Decided by.** The spec writer proposed it in the first version. On review the developer first asked for git to ignore `.foundry/`. The spec writer set out what that changes, and the developer replied: "We don't need to ignore the .foundry directory."
- **Decision.** [workflow.md](workflow.md#shared-artefacts) states it.
- **Why.** The first-draft rubric has the orchestrator merge a spec writer's branch, which needs the roadmap in git. Tracked files have history, and in a private repository the pushed orchestrator branch is their backup. Every worktree cut from the orchestrator branch contains them, with no further setup. The reviewers must never see the plan, and a pull request is not the place for planning files, so the PR creator leaves `.foundry/` out.
- **Consequences.** The roadmap and the plans never reach the default branch. Each change of state is a small commit on the phase branch, which is why a verdict names the code head (D9). A repository that uses s-stack must not ignore `.foundry/`. Foundry and the developer's two private repositories do not (F10). A pushed orchestrator branch shows the roadmap and the plans to everyone who can read the repository. Foundry is public (F11), so its orchestrator branch is pushed only when the developer says so.
- **Rejected.** An ignored `.foundry/` that every session shares. Experiments showed what it needs. One copy has to live in the main checkout, because removing a worktree deletes its ignored files without a warning (X9). Every worktree then needs a link to that copy, and every session needs `--add-dir` for it, because a write through the link otherwise stops at a permission prompt for each file (X5, X6). The files would have no history and no remote copy.

## D14. Every session starts with `/sam-mode <role>`, and `sam-mode` reads `poteto-mode`

- **Door.** Two-way.
- **Decided by.** The developer, in the first-draft rubric and again on review: s-stack is built on top of p-stack and does not replace it. The spec writer chose the mechanism.
- **Why.** The November phase sessions declined a relayed instruction to use `poteto-mode`. It "came from one of my helper subagents", and the skill "isn't in their sessions' skill lists" (R11). `poteto-mode` sets `disable-model-invocation: true` (F4). A skill named in the first prompt's first words loads, and a relayed instruction does not (R11).

## D15. The package is `s-stack`, the skill is `sam-mode`, and `default-stack` depends on the package

- **Door.** One-way for the names. Consumers pin tags of the form `s-stack--v<version>`.
- **Decided by.** The developer, in the brief and the first-draft rubric, and confirmed on review.
- **Context.** On `origin/main` the existing package is named `p-stack`, and `default-stack` already depends on it (F2). [package.md](package.md#dependencies) lists the manifest limits.

## D16. Verification runs before review

- **Door.** Two-way.
- **Decided by.** The spec writer. The first-draft rubric left it open.
- **Why.** The rubric's state order puts Verify first. A failed verification costs less than a review by three model families that would then run again.
- **Related answer.** The implementer does not ask a verifier to check work in progress. It runs the verification skill itself while it builds. The gate is the fresh verifier.

## D17. No fixed limit on live phase sessions

- **Door.** Two-way.
- **Decided by.** The developer asked on review why the first version set a limit of five. The spec writer had no measurement to defend it and removed it.
- **Decision.** The orchestrator starts every phase that is ready. [coordination.md](coordination.md#parallel-work) lists what bounds parallel work.
- **Why no limit.** The first version gave two reasons, and neither holds up. Panes that share one window get small, but the developer can zoom a pane, and the status board is the main view. The November run did run out of memory, but that happened during heavy compute work, and the transcripts do not tie it to the number of sessions (R12).
- **What would bring a limit back.** Memory pressure that is measured and traced to the sessions themselves, or panes too small to use.

## D18. Review feedback reaches a phase through the orchestrator

- **Door.** Two-way.
- **Decided by.** The spec writer proposed it, and the developer accepted it on review.
- **Decision.** The developer tells the orchestrator, or comments on the pull request. The tick finds new review comments and failed checks and starts a fix round.
- **Why.** The developer's contact points stay at two, and a comment written where the code is needs no second telling.
- **Rejected.** Fix rounds that start only when the developer tells the orchestrator.

## D19. The orchestrator keeps an architecture page current

- **Door.** Two-way.
- **Decided by.** The developer, on review: "I actually want an architecture explainer page. I found that really useful." The first version of this roadmap left the page out. The spec writer chose the rules.
- **Decision.** [coordination.md](coordination.md#the-architecture-page) lists what the page shows and when it changes.
- **Why these rules.** In November the developer asked four times for this page to be updated (R5), so its updates are steps of the tick. That page and the status page used different words for progress and were updated at different times (B3), so this page uses two words and links to the status board for the rest. A subagent writes it, because the orchestrator's context filled up in November (R13).
- **Rejected.** A template, because each feature's architecture differs. An update on every tick, because the page changes only when a phase merges or the roadmap changes.

## Answers to the first draft's open questions

| Question | Answer |
| --- | --- |
| How are the roadmap and the plan passed around? | As committed files under `.foundry/` on the orchestrator branch. Every worktree cut from that branch has them, and a session's first prompt carries their paths (D6, D13). |
| Does each main session get its own worktree? | Each session that changes code at the same time as another gets its own. The first spec writer and the orchestrator share the feature worktree, one after the other. |
| Do the implementer, verifier, reviewer and PR creator share a worktree? | Yes. They are one phase session and its subagents (D1). |
| Do they work in parallel or in sequence? | In sequence inside a phase. Phases run in parallel. |
| Do the verifier and the reviewer run in parallel? | No. Verification runs first (D16). |
| Can the implementer ask for verification while it builds? | It runs the verification skill itself. The gate is a fresh verifier (D16). |
