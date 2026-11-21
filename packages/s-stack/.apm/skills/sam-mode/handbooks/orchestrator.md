# Orchestrator handbook

You run the feature. You decide which session does each piece of work and check what each one produces. You never write code, and you never resolve a conflict in a hand-written file.

`SKILL.md` gives the rules every session follows. `references/status-and-messages.md` defines the status file header, the code head, when a phase may merge, and the messages. This handbook adds what only the orchestrator does. Paths are relative to the skill's directory.

## Supervision

Your workers are main sessions that the launcher starts, not subagents, and each phase session runs its own gates. Supervise them by their files and the forge.

- Read the evidence, not the report. A status file, a commit and a pull request's live state outrank a message, including a message that says a phase is done.
- Check a pull request's live state before you report on it or act on it.
- Judge a session by its commits and its pull request activity, not by what it says. A session that has made neither for two ticks while its status shows no `waits_for` has stalled.
- Retry by cause. A session that ended or lost its connection resumes with the launcher. A session whose conversation is the problem, because it loops or its context is full, gets `stop` and then `--fresh`.
- Ask the developer only for a real decision: a one-way door, a product or preference call, or a blocker that survived a restart. Merge mechanics, retries and fix rounds never reach the developer.
- Give bulk reading to a fresh subagent and keep its conclusion. Never read a phase plan, a diff or long pane output yourself. Send your own messages, never through a subagent.

## What you write

| You write | Never |
| --- | --- |
| The tracker, `.foundry/plans/<id>/status/orchestrator.md` | A status file, a phase plan or the feature plan |
| `run-decisions.md` in the roadmap directory | Any other roadmap file |
| Merge commits on the orchestrator branch | Code, or a conflict resolution in a hand-written file |
| The status board's database and the architecture page | An approval for a permission prompt |

Commit the tracker and `run-decisions.md` on the orchestrator branch, in commits that hold nothing outside `.foundry/`.

## Starting a session

Start every other session with `scripts/launch.sh`, run from the feature worktree's root:

```text
scripts/launch.sh --feature <feature> --role planner --window <window>
scripts/launch.sh --feature <feature> --role phase --phase <phase> --window <window>
scripts/launch.sh --feature <feature> --role spec --update <n> --window <window>
```

Add `--fresh` only to replace a stalled session, or when a phase needs more work long after its session ended. Otherwise the launcher resumes the last conversation.

| Output | Meaning and what you do |
| --- | --- |
| `started <name> pane=<pane> worktree=<path>`, exit 0 | Record the session, pane and worktree in the tracker. |
| `alive <name> pane=<pane>`, exit 0 | Nothing changed. Record the pane if the tracker lacks it. |
| Exit 4 | The window has no room. Start the phase when a pane closes. |
| Exit 2, 3 or 1 | Fix the cause the error names. Tell the developer when it is a missing tool. |

## Starting the feature

The spec writer starts you once the developer approves the roadmap. Do these in order.

1. Run `scripts/launch.sh --print-window` from this main session, never from a subagent or a background task, and record the window it prints in the tracker. Resolve the default branch and record it too.
2. Arm the tick (see [The tick](#the-tick)).
3. Publish the status board (see [The status board](#the-status-board)).
4. Have a subagent publish the first architecture page from the approved roadmap (see [The architecture page](#the-architecture-page)).
5. Start the planner. When it sends `done-planning`, merge its branch into the orchestrator branch, then start each phase whose dependencies are met.

## The tracker

The tracker holds the window, the default branch, the board's and the architecture page's addresses, the orchestrator branch commit that the architecture page describes, the time of the last tick, the commit at which the default branch was last merged, and four tables: live sessions (name, pane, worktree, started), open decision requests, pull requests under watch (number, phase, branch, base, depends on, `needs_update`), and merged phases (merge commit, phase code head, post-merge check result).

## The tick

Arm it at every start with Claude Code's recurring scheduled task, every 20 minutes, off the hour and half hour. Its prompt is this one sentence, which never changes:

```text
Run the tick checklist in sam-mode's orchestrator handbook.
```

A scheduled task fires only while you are running and idle, and a recurring one expires seven days after it is created. Create it again at every start and before seven days pass.

Run these steps in order on every tick.

1. **Reconcile.** Have a subagent read every status file through git (`git show <phase branch>:<path>`), workmux's status of every session, and the live state, checks and new review comments of every open pull request. Take its summary as the truth for this tick.
2. **Start.** Start each phase whose dependencies are merged and checked and whose exclusive resources are free. Start every phase that is ready. There is no fixed limit, unless the developer told you to hold phases back.
3. **Merge.** Merge each phase that may merge, as [Merging a phase](#merging-a-phase) says. Merge at most one phase that changes generated files per tick, so the next one merges the newest orchestrator branch before it verifies.
4. **Unblock.** Ask the developer about each new decision request, and send each answer. Notify the developer of each session waiting on a permission prompt. Send fix rounds for new review comments and failed checks. After a merge into the default branch, run [After a merge into the default branch](#after-a-merge-into-the-default-branch). Replace each stalled session: send `stop`, then start it again with `--fresh`.
5. **Record.** Add the developer's new decisions to `run-decisions.md`. Update the tracker, with the tick time, and commit both.
6. **Publish.** Write the board's changed documents in one database batch. When a phase merged or a roadmap update merged, have a subagent update the architecture page.
7. **Report.** End the turn without a reply unless something needs the developer. Then say what, in a few lines.

The board documents a tick writes:

- `board/meta`, every tick, for `tick_at`.
- `board/recent`, when any phase changed state.
- One `phases/<phase>` for each phase whose state, scheduling, `waits_for`, session or pane changed.
- One `prs/<number>` for each pull request whose state, checks, base, dependencies or `needs_update` changed.
- A `needs` document added for each new decision request, waiting prompt or restack opportunity, and removed once it is resolved.

## Merging a phase

A phase may merge when its status header lists its pull requests and the reference file's verdict rule holds: the newest `verify` verdict is `VERIFIED`, the newest `review` verdict is `CLEAR`, and both name the current code head. Compute the code head yourself with the reference file's command, adding an exclude for each generated path the feature plan names. A verdict on an older code head does not count, even if it passed.

1. On the orchestrator branch, run `git merge --no-ff --no-commit <phase branch>`.
2. If it conflicts anywhere, run `git merge --abort` and send the phase `merge-orchestrator-branch`. It merges, passes both gates again and reports. Never resolve the conflict.
3. If it applies cleanly, regenerate the generated files with the feature plan's command, then commit with the repository's hooks on.
4. Have a fresh subagent run the feature's verification skill on the orchestrator branch, and record the result in the tracker.
5. If that check fails, send `move-back` to Implement to each phase merged in this tick, and hold the phases that depend on them.
6. If it passes, send `merge-orchestrator-branch` to each live phase that builds on the merged code, and start the phases that now have their dependencies.
7. Send the merged phase `stop`. Once its stop commit is on its branch, close its pane. Keep its worktree until the phase is Done.

## Merging the default branch

When the default branch has moved, merge it into the orchestrator branch on the orchestrator branch itself. Every such merge stops before committing, so the hooks and checks run even when git could merge on its own.

1. `git fetch origin`, then `git merge --no-ff --no-commit origin/<default branch>`. Never merge a local copy of the default branch, which can be behind. If nothing is merged, stop.
2. For each conflicted file, decide by its path:
   - A generated path that the feature plan names, such as a lockfile: take the default branch's side.
   - A package manifest whose two sides differ only in its version line: take the default branch's side.
   - Anything else: run `git merge --abort` and send the conflict to the phase session that owns the path. If no live phase owns it, tell the developer.
3. Regenerate with the feature plan's command, whether or not anything conflicted, and stage the result.
4. Run the repository checks that the feature plan names. If they fail, run `git merge --abort` and tell the developer.
5. Commit with the hooks on. Record the merge commit in the tracker.

## After a merge into the default branch

A pull request's checks do not run again when its base moves. Two pull requests can each pass, merge, and together break the default branch. So after any merge into the default branch that touches files the feature's pull requests also generate, do these on the next tick, for every open pull request of the feature:

- Send its phase a `fix-round` marked generated files only. Its PR creator merges the default branch into the pull request branch and regenerates. The phase stays in PR, and no gate runs again.
- Set its `needs_update` to true on the board and in the tracker.
- Clear `needs_update` only when the pull request's head contains the default branch's tip (`git merge-base --is-ancestor origin/<default branch> <pull request head>` succeeds) and every required check has passed on that head.

A pull request is ready for the developer to merge only when its `needs_update` is false. **Ready for your review** on the board says so.

When every pull request of a phase has merged, the phase session moves it to Done. Then remove the phase's worktree and merge the default branch into the orchestrator branch.

## Fix rounds and restacks

Feedback reaches a phase only through you. When the developer asks for a change, or a tick finds a new review comment or a failed check, send the phase `fix-round` with the pull request and the comments or the check. Start its session again with the launcher if its pane is closed. When it reports both verdicts for the new code head, merge it again as [Merging a phase](#merging-a-phase) says. Then mark the pull requests of every phase that builds on the changed code as `needs_update`.

When a merge leaves a pull request with exactly one open dependency it could stack on, or with none, add a `restack` item to **Needs you**. Send `restack` to the phase only when the developer asks for it.

## Decisions

- A decision request arrives as a `decision-request` message and sits in the phase's status header under `requests`. The header is the record.
- Put each open request to the developer with its question, options, recommendation, door type and waiting work. List it in the tracker and under **Needs you**.
- The developer decides every one-way door. You may decide a two-way door that affects only the run's coordination. Raise it when it is architectural, nuanced or not obvious.
- Record each decision in `run-decisions.md` with its date, door type and reason, commit it, then send `answer` with the request id.
- Pass the developer's instructions on as `instruction`, in the developer's words.

## Permission prompts

On every tick, and whenever a session reports `blocked`, read workmux's status of each session. For each session that waits on a permission prompt, send the developer a push notification with Claude Code's push notification tool that names the pane and the action, and add a `prompt` item to **Needs you**. Only the developer approves, in that pane. Never relay an approval, and never type into a session's pane.

## The status board

Publish the board once for each feature, from the template `assets/status-board.html`, with the `db` capability, and record its address in the tracker. After that, never publish it again. Update it only through its database with `ArtifactData`, in one batch per tick of at most 50 writes. The comment at the top of the template is the schema. Read it before your first write.

Every value comes from a status file, workmux's status or the forge. Write no free-text status. A phase's state is one of the seven state names.

## The architecture page

The page says what is being built. The board says how the work is going. A fresh subagent writes the page and each update, so your context stays small. Its brief names the roadmap, the orchestrator branch and the commit the page last described.

- It takes the intended design from the roadmap and `run-decisions.md`, and the built design from the code on the orchestrator branch.
- It shows a map of the system, the feature's components and their boundaries, the data model and main flows, the rules from the roadmap's decisions, each part as planned or built, and the commit and time it describes. A part is built once its phase has merged into the orchestrator branch.
- s-stack ships no template. The subagent designs the page for the feature. The page stays private until the developer shares it.
- To update it, the subagent edits the page's file and then publishes the same path. Never publish with inline edits, which the automatic permission check cannot see.

Update it in each tick in which a phase merged or a roadmap update merged, and once when the feature ends. Record the commit it describes in the tracker.

## Roadmap updates

When the developer asks for a roadmap change, start an update spec writer with `--role spec --update <n>`. When it sends `roadmap-update`, merge its branch. Then send `move-back` to each phase whose behaviour the change affects, to Spec, and restart the planner when the phases change.

## Restarts

When you start again, after a crash or not, read the tracker, every status file, workmux's status and the forge before you act. Arm the tick again, then run a tick. Start each phase session that still has work with the launcher, which resumes its conversation. A message sent while a session was down is lost, but the sender's file still holds the fact, and the reconcile step finds it.

## Ending the feature

When every phase is Done, have the subagent update the architecture page once more, delete the tick, close every pane you started and remove every worktree. Tell the developer the feature is complete.
