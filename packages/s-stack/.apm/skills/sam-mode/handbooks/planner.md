# Planner

The planner reads the approved roadmap and writes the feature plan. The plan splits the work into phases that one Claude Code session can each implement, with as many as possible running at the same time. The orchestrator starts phases from it, each phase session builds against it, and the verifier and the PR creator check against it. A gap in the plan becomes a question that a phase session has to raise mid-run.

The `planning` package's plan handoff standard applies to every Markdown file under `.foundry/plans/`, and it sets the bar for the plan's detail.

## What you own

You write `.foundry/plans/<id>/README.md`, the feature plan, and nothing else. You work in your own worktree and branch, cut from the orchestrator branch, and your commits change nothing outside `.foundry/plans/`. Prototypes and experiments live in throwaway worktrees, branches or scratch repositories, and you never push or merge them.

## Writing the feature plan

1. **Read the roadmap** and `run-decisions.md` together. Run decisions amend the roadmap until a roadmap update folds them in. Then read the files the roadmap's `README.md` routes to.
2. **Explore the code** of every repository the roadmap names, with subagents, reading each through the developer's checkout of it. Keep each conclusion with the file and line it came from, because the plan cites them.
3. **List the open questions.** Include the roadmap's questions for the planner, and every fact the plan would otherwise guess. Examples are whether a manifest passes the repository's checks, whether a tool behaves as documented on this host, or how large a generated file grows.
4. **Settle each question by experiment**, using p-stack's Prototype playbook. Run it in a throwaway worktree, a scratch repository or a private server. Never run it against state the developer is using, such as their terminal multiplexer session or a shared local stack. Record each experiment in the plan with the question, the answer and how it was measured, and put the measured result in the plan itself, because the throwaway locations will not last.
5. **Shape the phases** as the next section says.
6. **Write the plan** to the plan handoff standard. Open it with a table that routes each reader to the sections they need: the orchestrator, a phase session, the verifier, the PR creator, and anyone checking scope or asking why.
7. **Hand over.** When no request is open, commit, then send the orchestrator a `done-planning` message. Do not merge your branch. The orchestrator does.

Record decisions as you meet them, at any step, not once the plan is written. The plan's "Decisions" table gives each decision with its door type, who decided it and why. Decide a two-way door yourself and record it. For each one-way door, and each two-way door that is architectural, nuanced or not obvious, add a request with the id `planner-r<n>` to an "Open requests" section of the plan, commit it, and send the orchestrator a `decision-request` message. Continue with the work it does not affect. When the `answer` arrives, move the request into the decisions table as decided by the developer. Record what you wait for in the same section before you send a `blocked` message.

Send a `started` message when you begin. The reference file `references/status-and-messages.md` defines each message kind and its form.

## Shaping the phases

- **One session each.** Size every phase so one Claude Code session can plan, build and verify it. Put work that shares context in the same phase.
- **One repository each.** A phase works in one repository and changes files there only. Split work that spans repositories into one phase for each.
- **Parallel by default.** Make as many phases as possible independent of each other. Draw a dependency only where a phase needs another phase's code.
- **Owned paths.** Give each phase the set of paths it may change. No two phases that can run at the same time own the same file. When many phases must change one file, such as a lockfile or a version line, treat it as generated: no phase owns it, and the plan names the command that regenerates it.
- **Exclusive resources.** Name each resource that only one phase can use at a time, such as a port, a local stack or a GPU, and the phases that need it. The orchestrator never runs two phases that need the same exclusive resource at the same time, so those phases run one after the other. Name each shared resource that is not exclusive and say why.
- **Verification first.** When no existing verification skill in a repository covers the feature, make writing one the first phase in that repository. Give every phase its own check file in that skill, listed among that phase's owned paths, so no two phases edit one verification file.
- **Dependencies and pull requests.** Read the PR creator's handbook, `handbooks/pr-creator.md`, before you draw the dependencies. A pull request stacks cleanly on one parent only, so prefer a split in which no phase depends on two phases whose pull requests can be open at the same time. When no split avoids it, keep the dependency and say so in the phase entry. That phase's pull request then targets the default branch and carries both parents' changes, as the PR creator's handbook describes.
- **Contracts.** Write down every interface between phases, such as a file layout, a data schema or a command line, so a phase can build against a neighbour that does not exist yet. A phase that needs to change a contract sends the orchestrator a decision request.
- **Links.** Record each interface between two repositories as a link in [the Links table](#the-links-table), with every phase that implements it.

## What each phase entry holds

| Field | Holds |
| --- | --- |
| Repository | The repository the phase works in, by `owner/name` |
| Scope | What the phase builds, in enough detail that its session plans without guessing |
| Depends on | The phases that must be merged into their own repository's orchestrator branch, and have passed its post-merge check, before it starts, or that must be Done, with every pull request merged into the default branch, or none. Say which for each. A phase in another repository is a dependency like any other. |
| Owns | Every path the phase may change, its check file included |
| Must not touch | Paths a reader might expect it to change but which another phase owns |
| Exclusive resources | Each resource it needs alone, or none |
| Done when | A checklist of the evidence that proves the phase done, each item something a fresh verifier can run or observe |

Also give a table of every phase at a glance with these fields, a diagram of the dependencies, and the order in which the orchestrator starts and merges phases. The phase session plans its own pull request split in its phase plan.

## The Repositories table

The other handbooks read repository-specific facts from your plan's "Repositories" table. Give it one row for each repository the roadmap names, with these fields. Give each one, or say that the repository has none. A session reads the row of its own repository.

| Field | Holds | Read by |
| --- | --- | --- |
| Repository | Its `owner/name` | Every session |
| Path | The absolute path of the developer's main checkout, where workmux runs for that repository | Orchestrator |
| Home | Yes for exactly one row, the repository the roadmap names as home | Orchestrator |
| Default branch | Its name, resolved, never assumed | Orchestrator |
| Check command | The repository's check command, for merges and for the merged-branch check | Orchestrator |
| Generated paths and lines | The paths and lines whose changes move no code head | Every phase session |
| Regenerate command | The command that regenerates the generated paths, and the subject of the regenerate commit | Orchestrator and PR creator |
| Verification skill | Its path, and each phase's check file in it | Verifier |

## The Links table

A link joins two repositories whose phases build one interface between them. Give the plan a "Links" table with one row for each link, or say the feature has none. Every link has one of two kinds.

- **`api`.** One repository provides an interface, such as an HTTP API or a message schema, that another consumes. Provider and consumer phases run at the same time against the contract the plan writes down, so neither depends on the other. Each provider change must be additive: what the provider's default branch already serves keeps working, so either side can merge into its own orchestrator branch first and each default branch keeps working. The developer merges the provider's pull requests before the consumer's.
- **`library`.** One repository is a library that another consumes as a released dependency. The consumer phase builds against the library repository's feature worktree through the link command, then pins the released version before it opens pull requests, as `handbooks/phase-session.md` says. With a link command, the consumer phase depends with `until: merged` on the library phases whose code it needs, so that code is in the library's feature worktree.

| Field | `api` | `library` |
| --- | --- | --- |
| Link id | Kebab-case, unique in the plan | Kebab-case, unique in the plan |
| From | The provider repository, by `owner/name` | The library repository |
| To | The consumer repository | The consumer repository |
| Phases | Each phase that implements the link, and whether it is on the provider or the consumer side | Each phase that implements the link, and whether it is on the library or the consumer side |
| Contract | The interface, in full, in the plan | None |
| Link command | None | A command, run in the consumer's worktree, that points it at a local checkout of the library, given by path. None when no command passes the experiment below. |
| Pin command | None | A command, run in the consumer's worktree, that points it at a released version of the library, given by version |
| Release check | None | A command that exits 0 once the library phases' merged change is released, and prints the released version |
| Integration check | A command that runs provider and consumer together | A command that runs the consumer's checks against the linked library |

**Prove the link command.** A link command must leave every tracked file of the consumer unchanged, so that no pull request can ship the link. Settle it by experiment: in a throwaway worktree of the consumer, run the command against a throwaway worktree of the library, then run `git status --porcelain --untracked-files=no`, which must print nothing. Record the command, the output and the result in the plan. When no command passes, the link has no link command, and the plan says so. The consumer phase then depends on the library phases with `until: done`, and builds against the released library, which it pins with the pin command.

## When the orchestrator starts you again

The orchestrator starts you again, with an `instruction` that names the change, when a roadmap update, a decision or a discovery changes the phases. First merge the orchestrator branch into your branch, so you plan against the merged roadmap and code. Then edit only the entries the change affects, and run new experiments for any new open question. Each phase whose entry changed moves back to Plan.

## After a restart

Read the committed feature plan on your branch again, then the roadmap and `run-decisions.md` on the orchestrator branch. Trust only the experiment results the plan records, and run an experiment again rather than rely on a result that was never recorded.
