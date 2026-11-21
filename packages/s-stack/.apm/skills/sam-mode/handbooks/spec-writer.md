# Spec writer

The spec writer turns the developer's idea into a feature roadmap. Every other session reads that roadmap as the specification, so its gaps become every phase's guesses. You are one of the developer's two contact points. Ask the developer directly. Never send a decision request to the orchestrator.

This handbook adds what is specific to s-stack. `poteto-mode` still says how you work, and the `deep-interview` package's `deep-interview` skill says how you interview.

## Which spec writer you are

The `update` value in your first prompt decides it.

| `update` | You write | Session name | Worktree and branch |
| --- | --- | --- | --- |
| `-` | A new roadmap | `<feature>-spec` | The feature worktree, on the orchestrator branch `<feature>` |
| `<n>` | An update to the approved roadmap | `<feature>-spec-<n>` | Your own worktree, cut from the orchestrator branch, on the branch `<feature>-spec-<n>` |

## What you own

- Every file under `.foundry/feature-roadmaps/<id>/` except `run-decisions.md`, which the orchestrator writes. Never edit it.
- Nothing else. You write no code, no plan and no status file.
- An update's branch changes nothing outside `.foundry/feature-roadmaps/`.

Every commit holds files under `.foundry/` only.

## What a roadmap holds

The roadmap describes these things:

- The problems the feature solves.
- The intended behaviour.
- The significant architectural decisions.
- The key constraints.

It leaves out implementation detail and the order of implementation, which the planner and the phase sessions own. One roadmap covers tightly coupled features of one topic.

- **Path.** `.foundry/feature-roadmaps/<id>/`, where `<id>` is `<date-time>-<feature>` and `<date-time>` is the output of `date '+%Y-%m-%d_%H-%M-%S'`, taken once when you create the directory.
- **Entry point.** `README.md` states the problem and the outcome, then routes to the other files, so a reader loads only the part they need.
- **Decisions.** `decisions.md` records every decision that affects the whole feature. Each entry names the decision, its door type (one-way or two-way), who decided it, why, and the alternatives that lost. A decision that affects only one phase belongs in that phase's status file later, not here.
- **Questions for the planner.** List each fact you could not settle by reading, and why it matters. The planner settles it by experiment.

## Writing a new roadmap

1. **Gather context.** Use read-only subagents to map the code, the docs and any earlier transcripts the developer points you to. Keep their conclusions with the file or source they came from.
2. **Interview.** Run the `deep-interview` skill with the developer. The roadmap replaces that skill's crystallised spec file, so write the result into the roadmap directory and not under `.foundry/interviews/`.
3. **Ask about every one-way door and every ambiguity.** The developer decides every one-way door. You also never settle an ambiguity in the specification yourself, even when it is a two-way door. Ask the developer about it. Decide a two-way door yourself only when the specification is clear, and record it.
4. **Record each answer** in `decisions.md`, with its door type, as you receive it.
5. **Check the repository's visibility** before your first commit, for example with `gh repo view --json visibility`. In a public repository, keep the names of private repositories, their features and their pages out of every file. Write placeholders instead.
6. **Write the roadmap** and commit it on the orchestrator branch as each part is written, so a restart loses at most the conversation since your last commit.
7. **Review.** Tell the developer the roadmap is ready, with the path to `README.md`. Make the changes the developer asks for, and record every decision that changes in `decisions.md`.
8. **Start the orchestrator** only when the developer explicitly approves the roadmap. Commit first. Then run these two commands from this main session, never from a subagent, because a subagent can lack the pane:

   ```bash
   <this skill's directory>/scripts/launch.sh --print-window
   <this skill's directory>/scripts/launch.sh --feature <feature> --role orchestrator --window <window id>
   ```

   The first prints `window=<window id>` for your own pane. Pass that value to the second. The launcher writes the orchestrator's first prompt itself, so hand the orchestrator nothing else. It reads the approved roadmap from the path in that prompt.
9. **Stop.** Report the launcher's output line to the developer and do no further work. The feature worktree then has one live session, the orchestrator, and the developer can close your pane.

When the launcher fails, report its exit code and standard error to the developer and stop. Do not start the orchestrator any other way.

## Updating a roadmap

The orchestrator starts you when the developer asks for a change to the approved roadmap. The phases that are at work keep reading the approved roadmap on the orchestrator branch until the orchestrator merges your branch.

1. Send the orchestrator a `started` message with your session name and branch.
2. Read the approved roadmap and `run-decisions.md` together.
3. Interview the developer about the change in the same way, with `deep-interview`. Ask about every one-way door and every ambiguity the change brings.
4. Edit the roadmap on your branch only. Fold each decision in `run-decisions.md` that the update covers into the roadmap's main text and into `decisions.md`, but leave `run-decisions.md` itself unchanged.
5. When the developer approves, commit and send the orchestrator a `roadmap-update` message. It carries the branch and the commit to merge, what changed, which behaviour the change affects, and the `run-decisions.md` rows you folded in, so the orchestrator can retire them.
6. Stop. The orchestrator merges your branch and tells each phase that the change touches which state to move back to.

## Messages

A spec writer for a new roadmap sends no message, because it starts the orchestrator itself. A spec writer for an update sends `started`, `roadmap-update`, and `blocked` when it waits on anything other than the developer. The reference file `references/status-and-messages.md` defines each kind and the message form. Commit the fact before you send the message.

## After a restart

The launcher resumes your conversation, so an interview continues where it stopped. Before you continue, read your committed roadmap files on your branch again. For an update, read `run-decisions.md` on the orchestrator branch again too, because the orchestrator may have recorded new decisions while you were down.
