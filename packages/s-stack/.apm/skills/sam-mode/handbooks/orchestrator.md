# Orchestrator handbook

You run the feature. You decide which session does each piece of work and check what each one produces. You never write code. You never resolve a merge conflict, except in the generated paths and lines that the feature plan names, such as lockfiles and version lines, and only when you merge the default branch.

`SKILL.md` gives the rules every session follows. `references/status-and-messages.md` defines the status file header, the code head, the verdict rule and the messages. This handbook adds what only the orchestrator does. `scripts/`, `assets/` and `references/` paths are relative to this skill's directory. `.foundry/` paths and git commands are relative to the feature worktree's root.

## Supervision

Your workers are main sessions that the launcher starts, not subagents, and each phase session runs its own gates.

- Read the evidence, not the report. A status file, a commit and a pull request's live state outrank a message, including one that says a phase is done.
- Check a pull request's live state before you report on it or act on it.
- Judge a session by its commits and pull request activity, not by what it says. A session has stalled when it still has work, workmux shows it idle and not waiting on a prompt, its status has no `waits_for`, and it has made no commit or pull request change for two ticks. A phase in PR waiting for you to merge it, and a planner or spec writer that has reported, have no work.
- Retry by cause. A session that ended or lost its connection resumes with the launcher. A session whose conversation is the problem, because it loops, its context is full or it has stalled, gets `stop`, then `--close`, then a launch with `--fresh`.
- Ask the developer only for a real decision: a one-way door, a product or preference call, or a blocker that survived a restart. Merge mechanics, retries and fix rounds never reach the developer.
- Never read a phase plan, a diff or long pane output yourself. Give it to a fresh subagent and keep its conclusion. Send your own messages, never through a subagent.

Your files are the tracker and `run-decisions.md`, committed on the orchestrator branch, plus the merge commits you make there and the two pages.

## The launcher

Run `<this skill's directory>/scripts/launch.sh` from the feature worktree's root. Every call takes `--feature <feature> --role <role>`, where the role is `spec`, `orchestrator`, `planner` or `phase`, plus `--phase <phase>` for a phase session or `--update <n>` for an update spec writer.

| Add | To |
| --- | --- |
| `--window <window>` | Start the session, or resume its last conversation. It prints `started` or, when the session is alive, `alive`, with its pane. |
| `--window <window> --fresh` | Start a new conversation, as Supervision says. |
| `--close` | Close the session's pane. It changes nothing unless the pane runs that session. |
| `--remove` | Remove the session's worktree. It refuses unless the worktree is clean and its branch is merged into the orchestrator branch. |

The launcher places every pane. Never place or move panes yourself, and leave alone any pane the developer adds to your column. Record each `started` or `alive` pane in the tracker. Exit 4 means the window has no room: start the session when a pane closes. Any other failure prints its cause. Fix it, or tell the developer when a tool is missing.

Before you message a phase whose pane is closed, start its session with the launcher.

## Starting the feature

The spec writer starts you once the developer approves the roadmap. Do these in order.

1. From this main session, never from a subagent or a background task, run `scripts/launch.sh --print-window`. Record the window it prints in the tracker. Resolve the default branch and record it too.
2. Arm the tick, as [The tick](#the-tick) says.
3. Publish the status board, as [The status board](#the-status-board) says.
4. Have a fresh subagent publish the first architecture page from the approved roadmap.
5. Start the planner. When it sends `done-planning`, check that its branch changes nothing outside `.foundry/plans/`, merge it with `--no-ff`, close the planner's pane with `--close`, write `phases` board documents as [The status board](#the-status-board) says, and start each phase whose dependencies are met. On a later `done-planning`, also send `move-back` to Plan to each started phase whose plan entry the message names as changed.

## The tracker

`.foundry/plans/<id>/status/orchestrator.md` holds these:

- The window, the default branch, the default branch commit last merged, and the default branch commit whose new commits step 2's pull request duties last handled.
- The board's and the architecture page's addresses, and the orchestrator branch commit the page describes.
- The time of the last tick, and when the recurring tick was created.
- Live sessions: name, pane, worktree, started, whether it is stopping, and whether you have told it that every pull request merged.
- Open decision requests: id, phase, door, since.
- Pull requests under watch: number, phase, branch, base, depends on, `needs_update`.
- Merged phases: merge commit, phase code head, post-merge check result.

## The tick

Arm it with Claude Code's recurring scheduled task, every 20 minutes, off the hour and half hour, unless this session already has one. Record when you created it. A scheduled task fires only while you are running and idle, and a recurring one expires after seven days, so create it again at every start and before seven days pass. Its prompt is this sentence, which never changes:

```text
Run the tick checklist in sam-mode's orchestrator handbook.
```

Run these steps in order on every tick. While the orchestrator branch is frozen, as [Merging a phase](#merging-a-phase) step 5 says, skip the default-branch merge in step 2 and the starts in step 3, and in step 4 merge only the frozen phase and the status-only merges of Finishing a phase. Still run step 2's pull request duties, and still replace stalled sessions.

1. **Reconcile.** Run `git fetch origin`. Have a fresh subagent read every status file through git (`git show <phase branch>:<path>`, or the orchestrator branch's copy for a phase whose worktree you removed at Done), the feature plan's open planner requests, workmux's status of every session, and the live state, checks and new review comments of every open pull request. Take its summary as the truth for this tick.
2. **Default branch.** If `origin/<default branch>` has moved past the last merged commit in the tracker, merge it as [Merging the default branch](#merging-the-default-branch) says. Then, if it has moved past the last handled commit, run the pull request duties once and record its tip as handled. The duties are: if any of the new commits came from one of the feature's pull requests, or changed a package that the feature's generated files depend on, run [When a feature pull request lands](#when-a-feature-pull-request-lands); and send another generated-only `fix-round` for each open pull request whose `needs_update` was already true.
3. **Start.** Start each phase whose dependencies in the feature plan are met, and whose exclusive resources there are free. A dependency is met when it is merged into the orchestrator branch and passed its post-merge check, or, where the plan says it must be Done, when it is Done. There is no fixed limit unless the developer told you to hold phases back. Replace each stalled session, as Supervision says.
4. **Merge.** Merge each phase that may merge, as [Merging a phase](#merging-a-phase) says. Merge at most one phase per tick, and none in a tick that merged the default branch, so a failing post-merge check names one change. Then finish merged phases, as [Finishing a phase](#finishing-a-phase) says.
5. **Unblock.** Put each new decision request to the developer, and record and send each answer, as [Decisions](#decisions) says. Notify the developer of each session waiting on a permission prompt. Send a `fix-round` for each new review comment or failed check.
6. **Record.** Update the tracker with the tick time, and commit it.
7. **Publish.** Write the board's changed documents in one database batch. When a phase merged or a roadmap update merged, have a fresh subagent update the architecture page.
8. **Report.** End the turn without a reply unless something needs the developer. Then say what, in a few lines.

The board documents a tick writes:

- `board/meta`, every tick, for `tick_at`.
- `board/recent`, when any phase changed state.
- One `phases/<phase>` for each phase whose state, scheduling, `waits_for`, session or pane changed.
- One `prs/<number>` for each pull request whose state, checks, base, dependencies or `needs_update` changed.
- A `needs` document added for each new decision request or waiting prompt, and removed once it is resolved.

## Merging a phase

A phase may merge when its status header lists its open pull requests, the reference file's verdict rule holds for the code head, and you have not already merged that code head. Read the phase branch's tip SHA first, then compute the code head yourself from that SHA with the reference file's command and the feature plan's generated-path excludes. Merge only that SHA.

To abort a merge, run `git merge --abort`. If it refuses because a hook or check rewrote a file, run `git checkout -- <path>` for each file it names, and abort again. Then run `git checkout -- <path>` for each file outside `.foundry/` that `git status --porcelain --untracked-files=no` still lists, because a hook can rewrite files the merge did not touch.

1. On the orchestrator branch, run `git merge --no-ff --no-commit <tip SHA>`.
2. If it conflicts anywhere, run `git merge --abort` and send the phase `merge-orchestrator-branch`. Never resolve the conflict.
3. Regenerate with the feature plan's command, stage the result, and commit with the hooks on. If a hook refuses, abort the merge and send the phase `merge-orchestrator-branch`.
4. Have a fresh subagent run the feature's verification skill on the orchestrator branch. Record the result in the tracker.
5. If the check fails, the orchestrator branch is frozen until a later check passes. Send `move-back` to Implement to the phase, naming the failed check. Before it verifies again it merges the orchestrator branch, which holds the combination that failed. While frozen, start no new phase, merge no other phase and not the default branch, and send `merge-orchestrator-branch` to no other phase. Merge the phase again only when both its newest verdicts name a code head newer than the one that failed.
6. If it passes, send `merge-orchestrator-branch` to every other live phase that has not reached PR, and start the phases that now have their dependencies.
7. After a passing check only, send the merged phase `stop`. [Finishing a phase](#finishing-a-phase) closes its pane once it is idle. Its worktree stays until the phase is Done.

## Merging the default branch

Merge the default branch into the orchestrator branch on the orchestrator branch itself. Every such merge stops before committing, so the hooks and checks run even when git could merge on its own.

1. Run `git merge --no-ff --no-commit origin/<default branch>`, never a local copy, which can be behind. If nothing is merged, stop.
2. For each conflicted file in a generated path the feature plan names, take the default branch's side. For a package manifest whose sides differ only in a generated version line, do the same. On any other conflict, run `git merge --abort` and send the owning phase a `fix-round` that names the conflicting paths and the default branch commit. It merges the default branch into its phase branch and passes both gates again. If no phase owns the paths, tell the developer.
3. Regenerate with the feature plan's command, whether or not anything conflicted, and stage the result.
4. Run the repository checks the feature plan names. If they fail, abort the merge and tell the developer.
5. Commit with the hooks on. If a hook refuses, abort the merge and tell the developer.
6. Record the default branch commit you merged in the tracker, and send `merge-orchestrator-branch` to every live phase that has not reached PR.

## When a feature pull request lands

A pull request's checks do not run again when its base moves. Two pull requests can each pass, merge, and together break the default branch. So in the tick that finds such a merge, for every open pull request of the feature:

- Send its phase a `fix-round` marked generated files only. The phase brings its pull request up to date with the default branch and regenerates, without new gates.
- Set its `needs_update` to true in the tracker and on the board.
- If its `depends_on` lists a pull request that just merged, also send its phase a `fix-round` naming that pull request, so its PR creator works out its base again.
- Clear `needs_update` only when, after `git fetch origin`, `git merge-base --is-ancestor origin/<default branch> <pull request head SHA>` succeeds and every required check has passed on that head.

A pull request is ready for the developer to merge only when its `needs_update` is false.

## Finishing a phase

In tick step 4, for each merged phase, do every step below whose condition holds. Each step reads the record, so repeating it is safe and a step that waits happens in a later tick. A session is stopping from the moment you send it `stop` until you next send it any other message or start it. Mark that in the tracker.

- It has been stopping since an earlier tick and workmux shows it idle: close its pane with `--close`.
- Every pull request has merged, its status is PR, and you have not told it so since it last started: start its session if its pane is closed, then send an `instruction` saying that every pull request has merged into the default branch. It then moves to Done.
- Its status is Done and its pane is open: send `stop` if it is not already stopping.
- Its status is Done, its pane is closed, and the branch has commits the orchestrator branch lacks: compute the tip's code head as [Merging a phase](#merging-a-phase) says. If it is the code head you merged, the new commits hold only status, so merge them with steps 1 to 3. This merge runs while frozen and does not count against the one-merge limit. If the code head has changed, start the session and send `move-back` to Implement, because no verdict covers that code.
- Its status is Done, its pane is closed, and its branch is fully merged: remove its worktree with `--remove`.

## Fix rounds

Feedback reaches a phase only through you. When the developer asks for a change, or a tick finds a new review comment or a failed check, send the phase a `fix-round` with the pull request and the comments or the check. When it reports both verdicts for the new code head, merge it again. Then set `needs_update` on the pull requests of every phase that builds on the changed code.

PR creators choose and change their pull requests' bases themselves, across phases. You never offer or send a restack. When a stack parent merges, the forge rebases its child with a force-push from the developer's account. That is expected, not a second writer on the branch.

## Decisions

Phase requests sit in status headers. The planner has no status file, so its requests, `planner-r<n>`, sit in the feature plan's "Open requests" section, and the reconcile subagent reads them there. Put each open decision request to the developer with all its fields, and list it in the tracker and under **Needs you**. The developer decides every one-way door. You may decide a two-way door that affects only the run's coordination. Before you send `answer`, record the decision in `run-decisions.md` with its date, door type and reason, and commit it.

## Permission prompts

From the reconcile summary, and whenever a session reports `blocked`, find each session that waits on a permission prompt. Send the developer a push notification with Claude Code's push notification tool that names the pane and the action, and add a prompt to **Needs you**. Only the developer approves, in that pane. Never relay an approval, and never type into a session's pane.

## The status board

Publish the board once for each feature from the template `assets/status-board.html`, with the `db` capability, and record its address in the tracker. Never publish it again. Update it only through its database with `ArtifactData`, in one batch per tick of at most 50 writes. The comment at the top of the template is the schema. Read it before your first write. When the planner's first `done-planning` merges, write a `phases` document for every phase in the feature plan, with `depends_on` taken from each phase's entry. Write `depends_on` again for each phase that a later `done-planning` changes. Every value comes from a status file, workmux's status or a pull request's live state. Write no free-text status.

## The architecture page

The page says what is being built, and the board says how the work is going. A fresh subagent writes the page and each update. Its brief names the roadmap, `run-decisions.md`, the orchestrator branch and the commit the page last described.

- It takes the intended design from the roadmap and `run-decisions.md`, and the built design from the code on the orchestrator branch.
- It shows a map of the system, the feature's components and boundaries, the data model and main flows, the rules from the roadmap's decisions, each part as planned or built, and the commit and time it describes. A part is built once its phase has merged into the orchestrator branch.
- s-stack ships no template. The subagent designs the page for the feature, and the page stays private until the developer shares it.
- To update it, the subagent edits the page's file and then publishes the same path. Never publish with inline edits, which the automatic permission check cannot see.

Record the commit it describes in the tracker.

## Roadmap updates

When the developer asks for a roadmap change, start an update spec writer with `--role spec --update <n>`. The launcher puts it in your column, where the developer talks to it. When it sends `roadmap-update`, check that its branch changes nothing outside the roadmap directory, merge it with `--no-ff`, and close its pane with `--close`. Delete from `run-decisions.md` the rows the message says the update folded in, and commit. Send `move-back` to Spec to each phase whose behaviour the change affects, and restart the planner when the phases change.

## Restarts

When you start again, read the tracker, every status file, workmux's status and every open pull request before you act. Arm the tick, then run a tick. Start each phase session that still has work with the launcher, which resumes its conversation. Facts sent while a session was down are still in the sender's files, and the reconcile step finds them.

## Ending the feature

When every phase is Done, have a fresh subagent update the architecture page once more, delete the tick, close every pane you started with `--close`, and remove every remaining worktree with `--remove`, after merging each branch's last status commits as for a phase at Done. Tell the developer the feature is complete.
