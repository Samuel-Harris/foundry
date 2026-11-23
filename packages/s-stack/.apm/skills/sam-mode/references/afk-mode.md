# AFK mode

AFK mode keeps a feature moving while the developer is away from the keyboard. The orchestrator answers two-way doors itself and records each answer for the developer's review, one-way doors wait, usage stays under the plan limits, and the machine stays awake. Only the orchestrator reads this file: when the developer starts AFK mode, and at every start or tick while the tracker shows it on. `scripts/` and `assets/` paths are relative to this skill's directory. Everything else in `handbooks/orchestrator.md` still applies, apart from what this file changes.

Nothing changes in what s-stack may do with pull requests. Every pull request is a draft, and s-stack never marks one ready and never merges one into the default branch.

## Starting

The developer starts it in your pane, for example "AFK until 08:00". Optional settings follow, each with a default:

| Setting | Default | Meaning |
| --- | --- | --- |
| `until` | none | When the developer expects to return. Shown in the report and on the board. It does not end the mode. |
| `start` | now | Before this time you only reconcile, record and publish. Every working phase is parked until then. |
| `sessions` | 2 | The most phase sessions working at once. A phase works when it has work, as Supervision says, and is not parked. |
| `rounds` | 3 | The most failed verdicts of one gate for a phase, as [Usage](#usage) says. |
| `notify` | off | When on, a permission prompt still sends a push notification. |

Do these in order:

1. Remind the developer to set or lower the monthly spend limit at claude.ai/settings/usage, because nothing else caps usage credits.
2. Run `scripts/afk-watchdog.sh status` from the feature worktree's root. On `absent`, or on `other`, which means the job runs another worktree's copy and stops working when that worktree is removed, ask the developer to install the watchdog by typing `! <this skill's directory>/scripts/afk-watchdog.sh install` in your pane, or to say to go without it, and end your turn. Never install it yourself, because it adds a launchd job to their machine. Go on from step 3 at their next message, which belongs to the start and ends nothing. On `unsupported`, tell the developer that keep-awake and the watchdog are macOS only and are skipped.
3. Call the usage tool, as [Usage](#usage) says, and record the figures.
4. Record the tracker's "AFK mode" row, as `handbooks/orchestrator.md` says. Write the marker from the feature worktree's root: `printf '%s %s\n' <feature> <window> > "$(git rev-parse --absolute-git-dir)/s-stack-afk"`. It is never committed. Write `board/meta.afk` as the board template's schema says.
5. Except on `unsupported`, run `scripts/afk-watchdog.sh keep-awake`. It keeps the Mac from idle sleep while your `claude` process lives, on mains power. Tell the developer that a closed lid without an external display still sleeps.
6. Record a `run-decisions.md` row for the instruction, as for any instruction, and commit.

## Ending

AFK mode ends at the first message the developer types in your pane. Every other turn leaves it on: the tick's fixed sentence, a cross-session message, a notification that a subagent, a background task or a command finished, and the launcher's `/sam-mode orchestrator` prompt that starts a relaunched or resumed session. A message the developer types into another session does not end it.

Your first reply is the return report, in this order:

1. AFK decisions to accept or change, each with its ID, the question, the choice and the reason.
2. Paused one-way doors, each with its options and recommendation.
3. Pull requests ready for review, dependencies first.
4. Phases parked by the round cap, with their last findings, and other failures, stalls and permission prompts.
5. Usage: the five-hour and seven-day figures at the start and now, waits for resets, and any limit reached.

Then remove the marker, run `scripts/afk-watchdog.sh stop-keep-awake`, set `board/meta.afk` to `null`, record a `run-decisions.md` row for the end, and commit. Then, unless a usage pause holds, as the next paragraph says, lift the parks: send `unpark` to every phase the tracker's "AFK mode" row lists as parked, except one parked for an open one-way door, clear the row, and go back to normal mode.

A usage pause outlives the mode. When one is in force, or the developer's message reports a limit, which starts one, park as [Usage](#usage) says, and send no `unpark` in that turn. Mark the row ended and keep its parks. Lift them as above at the first tick after the pause's reset time, or, for a pause that waits for the developer's return, when the developer says to go on.

The developer answers "accept all", or names the changes. Then:

- Send each phase that holds AFK decisions one `instruction`. It names each of them, gives the developer's change for each one they changed, and asks the phase to set their `afk` to `false`, make the changes as a fix round, and send `prs-open` once its pull requests carry the result, without the "pending the developer's review" lines. That `prs-open` answers it, or, from a phase not in PR, a `state` reply.
- Remove "pending review" from each decision's `run-decisions.md` row yourself, commit, and delete its board item. Every item goes once the developer has said whether they agree, whichever way they answer.

## Decisions

Work that needs no decision from the developer comes first. In tick step 3, start and unpark phases with no open one-way request before the others, up to `sessions`.

- A phase session still decides an ordinary two-way door itself.
- Answer a raised two-way request yourself. Take the session's recommendation unless you have a reason not to, and record that reason. The planner's requests follow the same rules.
- Before you send `answer`, add a `run-decisions.md` row with the next free ID `AFK-<n>`, `Decided by: AFK` and the mark "AFK, pending review", naming the request id, and commit it. Write an `afk-decision` board item with the same ID as `ref`, the decision and its reason in full as `detail`, and the pull requests that will carry it as `prs`. The `answer` says it is an AFK decision and gives its ID, and the phase records it with that ID and `afk: true`.
- Never answer a one-way request. List it under Decisions on the board with all its fields. The phase carries on with the work the decision does not affect. When nothing else is left, send it `park` with the reason "one-way door `<request id>`".

## Usage

In tick step 1, call the usage tool, `mcp__s-stack-usage__usage`, which the launcher loads into your session from `assets/usage-mod/`. It returns a list of `{kind, percentUsed, resetsAt}`, with `kind` `five_hour` or `seven_day`. Plan limits belong to the account, so these are the windows every session spends from. An empty list or a missing tool means the figures are unknown, not zero.

| Signal | Do |
| --- | --- |
| `five_hour` at 95% or more, or a per-model limit message in any pane | Pause until the window's `resetsAt`, and `unpark` the phases the pause parked at the first tick after it |
| `seven_day` at 95% or more, or a weekly limit or monthly spend limit message in any pane | Pause until the developer returns |
| No figures, and an 85% usage warning in any pane | Treat it as the 95% signal of the window it names |
| A phase's `NOT VERIFIED` and `INCONCLUSIVE` verdicts since AFK mode began, by their `at` times, reach `rounds`, or its `SIGNIFICANT` verdicts do | Send it `park` with the reason "round cap", until the developer returns |
| More phases working than `sessions` | Park the most recently started, with the reason "session cap", and unpark them, oldest first, as slots free |

Each pause in this table is a usage pause, and so is a limit the developer tells you was reached. A limit message in your own pane is one too: park first, then stop until it resets. A usage pause parks every phase session, working or idle, with the reason and the time it waits until, with two exceptions. A phase already parked keeps its park and its reason. A phase waiting on a permission prompt is not parked, as [the prompts rule](#interrupted-sessions-and-permission-prompts) says, until its prompt is answered while the pause lasts, when you park it too. While the pause lasts, start no phase session, unpark none, and relaunch none that is idle at a gate boundary.

The 5% headroom pays for the park messages and the next ticks. A session that a plan limit stopped waits for its own reset. Never replace a session for being rate-limited.

Record each park in the tracker with its reason and the time it waits until.

## Interrupted sessions and permission prompts

- The reconcile subagent also reports each pane that stopped on an API error, such as "Your computer went to sleep mid-response". Send each one an `instruction` to continue from its recorded state, at that tick. Replace it, as Supervision says, only if it is still quiet at the next tick.
- A session that waits on a permission prompt gets no push notification, unless `notify` is on. Write a `prompt` board item and list it in the return report. The phase takes no slot under `sessions`, but it is not parked, even during a usage pause: record no park for it, and send it no `unpark`. Never approve anything for the developer.

## Restarts

The watchdog's launchd job runs every 20 minutes. For each marker it runs the launcher for the orchestrator, which prints `alive` and changes nothing while you run, and otherwise resumes your conversation, so you restart as `handbooks/orchestrator.md` says. When the tracker shows AFK mode on at any start, a fresh relaunch included, run `scripts/afk-watchdog.sh keep-awake` again, because the keep-awake process ends with the `claude` process it waited on. A reboot or a dead tmux server is not covered: the developer runs `workmux resurrect`.
