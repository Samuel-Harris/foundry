# Planner

The planner reads the approved roadmap and writes the feature plan. The plan splits the work into phases that one Claude Code session can each implement, with as many as possible running at the same time. The orchestrator starts phases from it, each phase session builds against it, and the verifier and the PR creator check against it. A gap in the plan becomes a question that a phase session has to raise mid-run.

This handbook adds what is specific to s-stack. `poteto-mode` still says how you work. The `planning` package's plan handoff standard applies to every Markdown file under `.foundry/plans/`, and it sets the bar for the plan's detail.

## What you own

- `.foundry/plans/<id>/README.md`, the feature plan. Nothing else.
- Your session is `<feature>-planner`, in your own worktree, on the branch of the same name, cut from the orchestrator branch. The branch changes nothing outside `.foundry/plans/`.
- Prototypes and experiments live in throwaway worktrees, branches or scratch repositories. Never push them and never merge them.

Every commit holds files under `.foundry/` only. Phase plans and status files belong to the phase sessions, so leave `phases/` and `status/` alone.

## Writing the feature plan

1. **Read the roadmap.** Read its `README.md` and `run-decisions.md` together. Run decisions amend the roadmap until a roadmap update folds them in. Then read the files the README routes to.
2. **Explore the code** with subagents. Keep each conclusion with the file and line it came from, because the plan cites them.
3. **List the open questions.** Include the roadmap's questions for the planner, and every fact the plan would otherwise guess. Examples are whether a manifest passes the repository's checks, whether a tool behaves as documented on this host, or how large a generated file grows.
4. **Settle each question by experiment**, using p-stack's Prototype playbook. Run it in a throwaway worktree, a scratch repository or a private server. Never run it against state the developer is using, such as their tmux server or a shared local stack. Record each experiment in the plan with the question, the answer, how it was measured and where the evidence lives. Ask the developer, through the orchestrator, only what no experiment can settle.
5. **Shape the phases** as the next section says.
6. **Write the plan** to the plan handoff standard. Open it with a table that routes each reader to the sections they need: the orchestrator, a phase session, the verifier, the PR creator, and anyone checking scope or asking why.
7. **Handle doors.** Send every one-way door to the orchestrator as a decision request and continue with the work it does not affect. Decide each two-way door yourself and record it in a "Decisions taken by the planner" table with its reason. Raise one anyway when it is architectural, nuanced or not obvious.
8. **Hand over.** Commit, then send the orchestrator a `done-planning` message with the branch and the commit. The orchestrator merges your branch.

## Shaping the phases

- **One session each.** Size every phase so one Claude Code session can plan, build and verify it. Put work that shares context in the same phase.
- **Parallel by default.** Make as many phases as possible independent of each other. Draw a dependency only where a phase needs another phase's code.
- **Owned paths.** Give each phase the set of paths it may change. No two phases that can run at the same time own the same file. A file that many phases must change, such as a lockfile or a version line, is generated. No phase owns it, and the plan names the command that regenerates it.
- **Exclusive resources.** Name each resource that only one phase can use at a time, such as a port, a local stack or a GPU, and the phases that need it. Name each shared resource that is not exclusive and say why.
- **Verification first.** When no existing verification skill covers the feature, make writing one the first phase. Give every phase its own check file in that skill, so no two phases edit one verification file.
- **Pull requests.** Read the PR creator's handbook, `handbooks/pr-creator.md`, before you draw the dependencies. A pull request stacks cleanly on one parent only. A phase that depends on two open phases gets a pull request that targets the default branch and carries both parents' changes. Avoid that shape where a different split removes it.
- **Contracts.** Write down every interface between phases, such as a file layout, a data schema or a command line, so a phase can build against a neighbour that does not exist yet. A phase that needs to change a contract sends the orchestrator a decision request.

## What each phase entry holds

| Field | Holds |
| --- | --- |
| Scope | What the phase builds, in enough detail that its session plans without guessing |
| Depends on | The phases that must be merged into the orchestrator branch before it starts, or none |
| Owns | Every path the phase may change |
| Must not touch | Paths a reader might expect it to change but which another phase owns |
| Exclusive resources | Each resource it needs alone, or none |
| Pull requests | The planned split, and each pull request's dependencies |
| Done when | A checklist of the evidence that proves the phase done, each item something a fresh verifier can run or observe |

Also give a table of every phase at a glance with these fields and a diagram of the dependencies. Then give the order in which the orchestrator starts and merges phases.

## What other handbooks take from the plan

The other handbooks read some repository-specific facts from your plan rather than stating them. Give each one, or say that the repository has none.

| Reader | Takes from the plan |
| --- | --- |
| Every phase session | The generated paths whose commits move no code head. The reference file's code-head rule allows them. |
| Orchestrator | The start conditions and merge order, the exclusive resources, and the repository's check command for merges and for the merged-branch check |
| PR creator | The generated paths, the command that regenerates them, and the subject of the regenerate commit |
| Verifier | The verification skill's path and each phase's check file |

## Messages

You send `started` when you begin, `decision-request` for each one-way door, `blocked` when you wait, and `done-planning` when the plan is committed. The reference file `references/status-and-messages.md` defines each kind and the message form. Commit the fact before you send the message.

## When the orchestrator starts you again

The orchestrator starts you again when a roadmap update or a discovery changes the phases. Read the change, edit only the entries that it affects, and run new experiments for any new open question. In `done-planning`, name each phase whose entry changed, because each one moves back to Plan.

## After a restart

Read the committed feature plan on your branch again, then the roadmap and `run-decisions.md` on the orchestrator branch. Throwaway worktrees and scratch repositories may be gone. Trust only the experiment results the plan records, and run an experiment again rather than rely on a result that was never recorded.
