# AFK mode

AFK mode keeps a feature moving while the developer is away from the keyboard. The orchestrator answers two-way doors itself and records each answer for the developer's review, one-way doors wait, usage stays under the plan limits, and the machine stays awake. Only the orchestrator reads this file: when the developer starts AFK mode, and at every start or tick while the tracker shows it on or holds a "Parks" or "Usage pause" row. `scripts/` and `assets/` paths are relative to this skill's directory. Everything else in `handbooks/orchestrator.md` still applies, apart from what this file changes.

Nothing changes in what s-stack may do with pull requests. Every pull request is a draft, and s-stack never marks one ready and never merges one into the default branch.

## Starting

The developer starts it in your pane, for example "AFK until 08:00". Optional settings follow, each with a default:

| Setting | Default | Meaning |
| --- | --- | --- |
| `until` | none | When the developer expects to return. Shown in the report and on the board. It does not end the mode. |
| `start` | now | Before this time you only reconcile, record and publish, and the phases wait, as [Parks](#parks) says. |
| `sessions` | 2 | The most phase sessions working at once. A phase works when it has work, as Supervision says, and is not parked. |
| `rounds` | 3 | The most failed verdicts of one gate for a phase, as [Parks](#parks) says. |
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
5. Usage: the five-hour and seven-day figures at the start and now, waits for resets, any limit reached, and a usage pause that still holds, with what ends it.

Then remove the marker, run `scripts/afk-watchdog.sh stop-keep-awake`, set `board/meta.afk` to `null`, delete the tracker's "AFK mode" row, record a `run-decisions.md` row for the end, commit, and go back to normal mode. The parks that last until the end of AFK mode end now, as [Parks](#parks) says.

The developer answers "accept all", or names the changes. Then:

- Send each phase that holds AFK decisions one `instruction`. It names each of them, gives the developer's change for each one they changed, and asks the phase to set their `afk` to `false`, make the changes as a fix round, and send `prs-open` once its pull requests carry the result, without the "pending the developer's review" lines. That `prs-open` answers it, or, from a phase not in PR, a `state` reply.
- Remove "pending review" from each decision's `run-decisions.md` row yourself, commit, and delete its board item. Every item goes once the developer has said whether they agree, whichever way they answer.

## Decisions

Work that needs no decision from the developer comes first. In tick step 3, start and unpark phases with no open one-way request before the others, up to `sessions`.

- A phase session still decides an ordinary two-way door itself.
- Answer a raised two-way request yourself. Take the session's recommendation unless you have a reason not to, and record that reason. The planner's requests follow the same rules.
- Before you send `answer`, add a `run-decisions.md` row with the next free ID `AFK-<n>`, `Decided by: AFK` and the mark "AFK, pending review", naming the request id, and commit it. Write an `afk-decision` board item with the same ID as `ref`, the decision and its reason in full as `detail`, and the pull requests that will carry it as `prs`. The `answer` says it is an AFK decision and gives its ID, and the phase records it with that ID and `afk: true`.
- Never answer a one-way request. List it under Decisions on the board with all its fields. The phase carries on with the work the decision does not affect. When nothing else is left, park it, as [Parks](#parks) says.

## Usage

In AFK mode, call the usage tool in tick step 1 and in Starting step 3. It is `mcp__s-stack-usage__usage`, which the launcher loads into your session from `assets/usage-mod/`, and it returns a list of `{kind, percentUsed, resetsAt}`, with `kind` `five_hour` or `seven_day`. Plan limits belong to the account, so these are the windows every session spends from. An empty list or a missing tool means the figures are unknown, not zero.

| Signal | The usage pause it starts ends |
| --- | --- |
| `five_hour` at 95% or more, or a per-model limit message in any pane | At the window's `resetsAt` |
| `seven_day` at 95% or more, or a weekly limit or monthly spend limit message in any pane | At the developer's word |
| No figures, and an 85% usage warning in any pane | As for the 95% signal of the window it names |

The 5% headroom pays for the park messages and the next ticks. A session that a plan limit stopped waits for its own reset. Never replace a session for being rate-limited.

## Parks

A park stops a phase session from starting work until its reason ends. Record each park in the tracker's "Parks" row with its reason and the time you sent it, and remove it from the row when you send `unpark`. The row outlives AFK mode, and goes once it is empty. A phase waiting on a permission prompt gets no `park`. One already parked keeps its park.

| Reason | Send `park` when | It ends |
| --- | --- | --- |
| `start` | AFK mode starts with a later `start`: every working phase. A phase already parked keeps its park, and when its reason ends before the `start` time, its reason becomes `start`, with no `unpark`. When an `answer` you send ends it, send that phase `park` with the reason `start` first, so the answer does not end its wait | At the `start` time, or when that AFK mode ends |
| one-way door `<request id>` | The phase has nothing left that the request does not affect, as [Decisions](#decisions) says | At the answer to that request |
| round cap | A phase's `NOT VERIFIED` and `INCONCLUSIVE` verdicts of one gate since AFK mode began, by their `at` times, reach `rounds`, or its `SIGNIFICANT` verdicts do | When the AFK mode it was sent in ends |
| session cap | More phases work than `sessions`: the most recently started | At a free slot, oldest park first, or when the AFK mode it was sent in ends |
| usage pause | A usage pause starts | When the usage pause ends |

Send `unpark` once a park's reason has ended, no usage pause holds and no later `start` of the AFK mode that is on waits, in tick step 3, or in the turn AFK mode ends. In AFK mode, unpark up to `sessions`, in the order [Decisions](#decisions) sets. A phase left without a slot stays parked, and its reason becomes "session cap".

### The usage pause

One rule covers every usage pause.

- **Start.** A usage pause starts only while AFK mode is on, at its Starting step 3, or in the developer's message that ends it. It starts at a signal in [Usage](#usage), at a limit the developer tells you was reached, or when you choose to wait for a reset. In the message that ends AFK mode, start it before you unpark anything. Record a "Usage pause" row in the tracker with its cause and what ends it: for a signal or a reported limit, what the Usage row for its window says; for a reset you chose to wait for, that reset.
- **Parks.** Send `park` with the reason "usage pause", and what ends the pause, to every phase session, working or idle, that has no park. A phase whose prompt is answered while the pause holds gets its `park` then. A phase parked for another reason keeps that park and gets no second one.
- **Holds.** While the pause holds, whatever mode is on, start no phase session, send no `unpark`, and relaunch none that is idle at a gate boundary.
- **End.** A pause that ends at a time ends at the first tick after it. Any pause ends at the developer's word, a message in your pane that tells you to go on. A message that starts AFK mode ends it at that start's step 3 when step 3 finds no signal; otherwise the pause holds, and its row takes what the new signal's window says. The developer's return alone, and the end of AFK mode, do not end a pause. When it ends, delete the "Usage pause" row and unpark as [Parks](#parks) says, so a phase it parked waits for a later `start`.

## Interrupted sessions and permission prompts

- The reconcile subagent also reports each pane that stopped on an API error, such as "Your computer went to sleep mid-response". Send each one an `instruction` to continue from its recorded state, at that tick. Replace it, as Supervision says, only if it is still quiet at the next tick.
- A session that waits on a permission prompt gets no push notification, unless `notify` is on. Write a `prompt` board item and list it in the return report. The phase takes no slot under `sessions` and gets no `park`, as [Parks](#parks) says. Never approve anything for the developer.

## Restarts

The watchdog's launchd job runs every 20 minutes. For each marker it runs the launcher for the orchestrator, which prints `alive` and changes nothing while you run, and otherwise resumes your conversation, so you restart as `handbooks/orchestrator.md` says. When the tracker shows AFK mode on at any start, a fresh relaunch included, run `scripts/afk-watchdog.sh keep-awake` again, because the keep-awake process ends with the `claude` process it waited on. A reboot or a dead tmux server is not covered: the developer runs `workmux resurrect`.
