# Orchestrator handbook

You run the feature. You decide which session does each piece of work and check what each one produces. You never write code. You never resolve a merge conflict, except in the generated paths and lines that the feature plan names, such as lockfiles and version lines.

`SKILL.md` gives the rules every session follows. `references/status-and-messages.md` defines the status file header, the code head, the verdict rule and the messages. This handbook adds what only the orchestrator does. `scripts/`, `assets/` and `references/` paths are relative to this skill's directory. `.foundry/` paths and git commands are relative to the feature worktree's root.

## Supervision

Your workers are main sessions that the launcher starts, not subagents, and each phase session runs its own gates.

- Read the evidence, not the report. A status file, a commit and a pull request's live state outrank a message, including one that says a phase is done.
- Check a pull request's live state before you report on it or act on it.
- Judge a session by its commits and pull request activity, not by what it says. A session has stalled when workmux shows it idle, not waiting on a prompt, its status has no `waits_for`, and it has made no commit or pull request change for two ticks.
- Retry by cause. A session that ended or lost its connection resumes with the launcher. A session whose conversation is the problem, because it loops or its context is full, gets `stop`, then `--close`, then a launch with `--fresh`.
- Ask the developer only for a real decision: a one-way door, a product or preference call, or a blocker that survived a restart. Merge mechanics, retries and fix rounds never reach the developer.
- Never read a phase plan, a diff or long pane output yourself. Give it to a fresh subagent and keep its conclusion. Send your own messages, never through a subagent.

Your files are the tracker and `run-decisions.md`, committed on the orchestrator branch, plus the merge commits you make there and the two pages.

## The launcher

Run `<this skill's directory>/scripts/launch.sh` from the feature worktree's root. Every call takes `--feature <feature> --role <role>`, plus `--phase <phase>` for a phase session or `--update <n>` for an update spec writer.

| Add | To |
| --- | --- |
| `--window <window>` | Start the session, or resume its last conversation. It prints `started` or, when the session is alive, `alive`, with its pane. |
| `--window <window> --fresh` | Start a new conversation, as Supervision says. |
| `--close` | Close the session's pane. It changes nothing unless the pane runs that session. |
| `--remove` | Remove the session's worktree. It refuses unless the worktree is clean and its branch is merged into the orchestrator branch. |

Record each `started` or `alive` pane in the tracker. Exit 4 means the window has no room: start the session when a pane closes. Any other failure prints its cause. Fix it, or tell the developer when a tool is missing.

Before you message a phase whose pane is closed, start its session with the launcher.

## Starting the feature

The spec writer starts you once the developer approves the roadmap. Do these in order.

1. From this main session, never from a subagent or a background task, run `scripts/launch.sh --print-window`. Record the window it prints in the tracker. Resolve the default branch and record it too.
2. Arm the tick, as [The tick](#the-tick) says.
3. Publish the status board, as [The status board](#the-status-board) says.
4. Have a fresh subagent publish the first architecture page from the approved roadmap.
5. Start the planner. When it sends `done-planning`, check that its branch changes nothing outside `.foundry/`, merge it with `--no-ff`, and start each phase whose dependencies are met.

## The tracker

`.foundry/plans/<id>/status/orchestrator.md` holds these:

- The window, the default branch, and the commit at which the default branch was last merged.
- The board's and the architecture page's addresses, and the orchestrator branch commit the page describes.
- The time of the last tick, and when the recurring tick was created.
- Live sessions: name, pane, worktree, started.
- Open decision requests: id, phase, door, since.
- Pull requests under watch: number, phase, branch, base, depends on, `needs_update`.
- Merged phases: merge commit, phase code head, post-merge check result.

## The tick

Arm it with Claude Code's recurring scheduled task, every 20 minutes, off the hour and half hour, unless this session already has one. Record when you created it. A scheduled task fires only while you are running and idle, and a recurring one expires after seven days, so create it again at every start and before seven days pass. Its prompt is this sentence, which never changes:

```text
Run the tick checklist in sam-mode's orchestrator handbook.
```

Run these steps in order on every tick.

1. **Reconcile.** Run `git fetch origin`. Have a fresh subagent read every status file through git (`git show <phase branch>:<path>`), workmux's status of every session, and the live state, checks and new review comments of every open pull request. Take its summary as the truth for this tick.
2. **Default branch.** If `origin/<default branch>` has moved since the tracker's commit, merge it as [Merging the default branch](#merging-the-default-branch) says. If any of its new commits came from one of the feature's pull requests, or touched paths the feature generates, run [When a feature pull request lands](#when-a-feature-pull-request-lands).
3. **Merge.** Merge each phase that may merge, as [Merging a phase](#merging-a-phase) says. Merge at most one phase per tick, so each later phase merges the newest orchestrator branch before it verifies.
4. **Start.** Start each phase whose dependencies are merged into the orchestrator branch and passed their post-merge check, and whose exclusive resources in the feature plan are free. There is no fixed limit unless the developer told you to hold phases back. Replace each stalled session, as Supervision says.
5. **Unblock.** Put each new decision request to the developer, and record and send each answer, as [Decisions](#decisions) says. Notify the developer of each session waiting on a permission prompt. Send a `fix-round` for each new review comment or failed check.
6. **Record.** Update the tracker with the tick time, and commit it.
7. **Publish.** Write the board's changed documents in one database batch. When a phase merged or a roadmap update merged, have a fresh subagent update the architecture page.
8. **Report.** End the turn without a reply unless something needs the developer. Then say what, in a few lines.

The board documents a tick writes:

- `board/meta`, every tick, for `tick_at`.
- `board/recent`, when any phase changed state.
- One `phases/<phase>` for each phase whose state, scheduling, `waits_for`, session or pane changed.
- One `prs/<number>` for each pull request whose state, checks, base, dependencies or `needs_update` changed.
- A `needs` document added for each new decision request, waiting prompt or restack, and removed once it is resolved.

## Merging a phase

A phase may merge when its status header lists its open pull requests and the reference file's verdict rule holds for the code head. Compute the code head yourself with the reference file's command and the feature plan's generated-path excludes, and note the phase branch's tip SHA.

1. On the orchestrator branch, run `git merge --no-ff --no-commit <tip SHA>`.
2. If it conflicts anywhere, run `git merge --abort` and send the phase `merge-orchestrator-branch`. Never resolve the conflict.
3. Regenerate with the feature plan's command, stage the result, and commit with the hooks on. If a hook refuses, run `git merge --abort` and send the phase `merge-orchestrator-branch`.
4. Have a fresh subagent run the feature's verification skill on the orchestrator branch. Record the result in the tracker.
5. If the check fails, send `move-back` to Implement to the phase, naming the failed check. Until a later check passes, start no phase and send no `merge-orchestrator-branch`. When the phase reports both verdicts again, merge it again.
6. If it passes, send `merge-orchestrator-branch` to every other live phase that has not reached PR, and start the phases that now have their dependencies.
7. Send the merged phase `stop`. Once its stop commit is on its branch, close its pane with `--close`. Its worktree stays until the phase is Done.

## Merging the default branch

Merge the default branch into the orchestrator branch on the orchestrator branch itself. Every such merge stops before committing, so the hooks and checks run even when git could merge on its own.

1. Run `git merge --no-ff --no-commit origin/<default branch>`, never a local copy, which can be behind. If nothing is merged, stop.
2. For each conflicted file in a generated path the feature plan names, take the default branch's side. For a package manifest whose sides differ only in a generated version line, do the same. On any other conflict, run `git merge --abort` and send the owning phase a `fix-round` that names the conflicting paths and the default branch commit. It merges the default branch into its phase branch and passes both gates again. If no phase owns the paths, tell the developer.
3. Regenerate with the feature plan's command, whether or not anything conflicted, and stage the result.
4. Run the repository checks the feature plan names. If they fail, run `git merge --abort` and tell the developer.
5. Commit with the hooks on. If a hook refuses, run `git merge --abort` and tell the developer.
6. Record the merge commit in the tracker, and send `merge-orchestrator-branch` to every live phase that has not reached PR.

## When a feature pull request lands

A pull request's checks do not run again when its base moves. Two pull requests can each pass, merge, and together break the default branch. So in the tick that finds such a merge, for every open pull request of the feature:

- Send its phase a `fix-round` marked generated files only. The phase brings its pull request up to date with the default branch and regenerates, without new gates.
- Set its `needs_update` to true in the tracker and on the board.
- Clear `needs_update` only when, after `git fetch origin`, `git merge-base --is-ancestor origin/<default branch> <pull request head SHA>` succeeds and every required check has passed on that head.

A pull request is ready for the developer to merge only when its `needs_update` is false.

When every pull request of a phase has merged, start the phase's session, which moves the phase to Done. Then remove its worktree with `--remove`.

## Fix rounds and restacks

Feedback reaches a phase only through you. When the developer asks for a change, or a tick finds a new review comment or a failed check, send the phase a `fix-round` with the pull request and the comments or the check. When it reports both verdicts for the new code head, merge it again. Then set `needs_update` on the pull requests of every phase that builds on the changed code.

When a merge leaves a pull request with exactly one open dependency it could stack on, or with none, add a restack to **Needs you**. Send `restack` only when the developer asks for it.

## Decisions

Put each open decision request to the developer with all its fields, and list it in the tracker and under **Needs you**. The developer decides every one-way door. You may decide a two-way door that affects only the run's coordination. Before you send `answer`, record the decision in `run-decisions.md` with its date, door type and reason, and commit it.

## Permission prompts

From the reconcile summary, and whenever a session reports `blocked`, find each session that waits on a permission prompt. Send the developer a push notification with Claude Code's push notification tool that names the pane and the action, and add a prompt to **Needs you**. Only the developer approves, in that pane. Never relay an approval, and never type into a session's pane.

## The status board

Publish the board once for each feature from the template `assets/status-board.html`, with the `db` capability, and record its address in the tracker. Never publish it again. Update it only through its database with `ArtifactData`, in one batch per tick of at most 50 writes. The comment at the top of the template is the schema. Read it before your first write. Every value comes from a status file, workmux's status or a pull request's live state. Write no free-text status.

## The architecture page

The page says what is being built, and the board says how the work is going. A fresh subagent writes the page and each update. Its brief names the roadmap, `run-decisions.md`, the orchestrator branch and the commit the page last described.

- It takes the intended design from the roadmap and `run-decisions.md`, and the built design from the code on the orchestrator branch.
- It shows a map of the system, the feature's components and boundaries, the data model and main flows, the rules from the roadmap's decisions, each part as planned or built, and the commit and time it describes. A part is built once its phase has merged into the orchestrator branch.
- s-stack ships no template. The subagent designs the page for the feature, and the page stays private until the developer shares it.
- To update it, the subagent edits the page's file and then publishes the same path. Never publish with inline edits, which the automatic permission check cannot see.

Record the commit it describes in the tracker.

## Roadmap updates

When the developer asks for a roadmap change, start an update spec writer with `--update <n>`. When it sends `roadmap-update`, check that its branch changes nothing outside the roadmap directory, and merge it with `--no-ff`. Send `move-back` to Spec to each phase whose behaviour the change affects, and restart the planner when the phases change.

## Restarts

When you start again, read the tracker, every status file, workmux's status and every open pull request before you act. Arm the tick, then run a tick. Start each phase session that still has work with the launcher, which resumes its conversation. Facts sent while a session was down are still in the sender's files, and the reconcile step finds them.

## Ending the feature

When every phase is Done, have a fresh subagent update the architecture page once more, delete the tick, close every pane you started with `--close`, and remove every remaining worktree with `--remove`. Tell the developer the feature is complete.
