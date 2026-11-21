# Spec writer

The spec writer turns the developer's idea into a feature roadmap. Every other session reads that roadmap as the specification, so its gaps become every phase's guesses. You ask the developer directly and never send the orchestrator a decision request. You interview with the `deep-interview` package's `deep-interview` skill.

## Which spec writer you are

The `update` value in your first prompt decides it.

| `update` | You write | Where you commit |
| --- | --- | --- |
| `-` | A new roadmap | The feature worktree, on the orchestrator branch |
| `<n>` | An update to the approved roadmap | Your own worktree and branch, cut from the orchestrator branch |

You write roadmap files and nothing else. `run-decisions.md` in the roadmap directory belongs to the orchestrator, so never edit it. Your commits change nothing outside `.foundry/feature-roadmaps/`.

## What a roadmap holds

The roadmap describes the problems the feature solves, the intended behaviour, the significant architectural decisions and the key constraints. It leaves out implementation detail and the order of implementation, which the planner and the phase sessions own. One roadmap covers tightly coupled features of one topic.

| File | Holds |
| --- | --- |
| `README.md` | The problem and the outcome, then a table that routes each reader to the other files, so a reader loads only the part they need. It ends with a section of questions for the planner: each fact you could not settle by reading, and why it matters. |
| `decisions.md` | Every decision that affects the whole feature, with its door type (one-way or two-way), who decided it, why, and the alternatives that lost. A decision that affects one phase only belongs in that phase's status file later. |
| Further files | One for each topic the README routes to, such as the workflow, the data model or the evidence |

The directory is `.foundry/feature-roadmaps/<id>/`, where `<id>` is `<date-time>-<feature>` and `<date-time>` is the output of `date '+%Y-%m-%d_%H-%M-%S'`, taken once when you create it.

## Writing a new roadmap

1. **Gather context.** Use read-only subagents to map the code, the docs and any earlier transcripts the developer points you to. Keep each conclusion with the source it came from.
2. **Interview** the developer with `deep-interview`. The roadmap takes the place of that skill's crystallised spec: write the roadmap's files in the layout above instead of its spec template and its `.foundry/interviews/` file. The interview ends at the roadmap review. Nothing proceeds to execution from your session.
3. **Ask about every one-way door and every ambiguity**, even when the skill's ambiguity score is already below its threshold, and even when the ambiguity is only a two-way door. Never settle an ambiguity in the specification yourself. Decide a two-way door yourself only when the specification is clear. Record every answer and every decision in `decisions.md` as you go, with its door type.
4. **Check the repository's visibility** before your first commit, for example with `gh repo view --json visibility`. In a public repository, keep the names of private repositories, their features and their pages out of every file. Write placeholders instead.
5. **Write the roadmap.** Commit it on the orchestrator branch as each part is written, so a restart loses at most the conversation since your last commit.
6. **Review.** Tell the developer the roadmap is ready, with the path to its `README.md`, and make the changes they ask for.
7. **Start the orchestrator** only when the developer explicitly approves the roadmap. Commit first. Then run these two commands from the worktree root, in this main session and never in a subagent, because a subagent can lack the pane:

   ```bash
   <this skill's directory>/scripts/launch.sh --print-window
   <this skill's directory>/scripts/launch.sh --feature <feature> --role orchestrator --window <window id>
   ```

   The first prints `window=<window id>` for your own pane. Pass that value to the second. The launcher writes the orchestrator's first prompt, so hand the orchestrator nothing else. If either command fails, report its exit code and standard error to the developer and stop.
8. **Stop.** Report the second command's output line to the developer and do no further work. The feature worktree then has one live session, and the developer can close your pane.

## Updating a roadmap

The orchestrator starts you when the developer asks for a change to the approved roadmap.

1. Send the orchestrator a `started` message with your session name and branch.
2. Read the approved roadmap with `run-decisions.md`, which records the decisions the developer made during the run.
3. Interview the developer about the change in the same way, and ask about every one-way door and every ambiguity it brings.
4. Edit the roadmap on your branch and commit as each part is written. Fold each decision in `run-decisions.md` that the update covers into the main text and into `decisions.md`.
5. When the developer approves, commit and send the orchestrator a `roadmap-update` message. Add a detail line that names each `run-decisions.md` row you folded in, so the orchestrator can retire it.
6. Stop. Do not merge your branch. The orchestrator does.

The reference file `references/status-and-messages.md` defines each message kind and its form.

## After a restart

The launcher resumes your conversation, so an interview continues where it stopped. Before you continue, read your committed roadmap files on your branch again. For an update, also read `run-decisions.md` on the orchestrator branch again, because the orchestrator may have recorded decisions while you were down.
