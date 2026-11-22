# Proposal: AFK mode

Status: agreed with the developer on 2026-11-22. The orchestrator decides how to route it to phases.

The brief called this "overnight mode". The developer named it AFK mode, `afk-mode` in kebab-case.

## What the developer wants

The developer: "I want to add an overnight mode (this name isn't set in stone) to the orchestrator agent in s-stack that is designed to make the agent continue working on things overnight while the human developer is asleep/away from their keyboard for a significant amount of time."

On decisions, the developer said: "In AFK mode, the agent should prioritise work that doesn't require human decisions. If it runs into something that requires a human decision, it should consider whether it is a one-way or two-way door. If it is a two-way door (e.g., the frequency of a cron-job) that can easily be changed with small edits to the relevant PRs, then the orchestrator [...] should make the decision and the orchestrator should record that decision and present it to the human developer when they return so the human developer can decide whether they want to accept or change that decision. If it is a one-way door (e.g., choosing between Nx and Bazel when implementing a CI orchestration framework for a repo), then that work can be paused until the human has returned."

## What this run showed

The evidence is in the tracker (`.foundry/plans/2026-11-20_21-37-12-s-stack/status/orchestrator.md`), `run-decisions.md` and the phase evidence files.

- The tick is a Claude Code scheduled task. It fires only while the orchestrator's session is running and idle, and it dies when Claude exits (`coordination.md` line 112, `orchestrator.md` line 61). Nothing restarts a dead orchestrator.
- The machine slept during the run. One session stopped on "API Error: Your computer went to sleep mid-response". A verifier took 3.9 hours of wall time.
- Sessions waited on decision requests while the developer was away. One answer came hours later.
- Usage was high. Every gate rerun started Opus readers and graders. `orchestrator-handbook` reached 30 Verify verdicts and 14 reviews (`proposals/gate-cost.md` line 31). The developer delayed tonight's next round to 02:00 GMT because of usage (`run-decisions.md` line 78).
- Push notifications reach the developer's phone when a session waits on a permission prompt (`orchestrator.md` line 161).
- Tonight the developer ran without this design. The orchestrator decided every question, one-way doors included, and marked each "decided overnight" (`run-decisions.md` line 79). AFK mode replaces that ad hoc rule: one-way doors now wait.

## What Claude Code exposes about usage

Read from the Claude Code documentation and this build's mod API (2.1.330). Not yet tried in a run.

- A session at a plan limit shows "You've hit your session limit · resets 3:45pm", with weekly and per-model forms, and warns first at 85%. Recent versions wait by themselves: "Continuing automatically at 3:45pm" (code.claude.com docs, `errors.md` and `interactive-mode.md`).
- The status line JSON carries `rate_limits.five_hour` and `rate_limits.seven_day`, each with `used_percentage` and `resets_at`, on Pro, Max and Ultra plans (`statusline.md`).
- A mod can read the same figures. `$.session.usage()` returns `rateLimits`, a list of `{ kind, percentUsed, resetsAt }` with `kind` `five_hour` or `seven_day`. The `session.measure` event fires when a window moves a whole point. `$.tool` registers a tool the model can call.
- Usage credits are not visible to a session. Only the interactive `/usage` screen shows them. The status line's `total_cost_usd` and the OpenTelemetry cost metric are list-price estimates. No Claude Code setting caps credit spend. The monthly spend limit at claude.ai/settings/usage is the only cap, and it shows "You've hit your monthly spend limit" when reached.

## Options considered

**Name, start and end.**

1. "Away mode", ended by the developer's next message. Renamed by the developer.
2. A fixed window that ends at a set time, even if the developer is not back. Rejected: work would wait on a developer who is still away.
3. An explicit "I'm back" only. Rejected: the developer's next message is a clearer signal.

**Who decides a raised two-way door.**

1. The orchestrator. Chosen. It has the cross-phase view and is the one writer of `run-decisions.md`.
2. The phase session, for every two-way door. Rejected: no cross-phase check, and decisions spread over many files.
3. The orchestrator, after a second-opinion subagent on another model family. Rejected: one more subagent for each decision, against a usage budget.

**Recording and reporting.**

1. Rows in `run-decisions.md`, board items and a report in the orchestrator's pane. Chosen.
2. Also a published report page. Rejected: the board already reads on a phone.
3. A separate AFK log, moved into `run-decisions.md` on acceptance. Rejected: a second record of the same decisions.

**Pull requests and merges.**

1. Carry on as normal, and flag AFK decisions in pull request descriptions. Chosen.
2. Open no pull request while AFK. Rejected: it delays review for no safety gain, because every pull request is a draft.
3. Carry on with no flag. Rejected: a reviewer could approve a pull request without knowing it holds an unreviewed decision.

**Usage source.**

1. A mod tool in the orchestrator's session, with the 85% pane warning as the fallback. Chosen.
2. A mod that writes the figures to a file on `session.measure`. Rejected: one more file to keep fresh.
3. A status line wrapper script. Rejected: it changes the developer's user settings.

**Surviving sleep and stops.**

1. `caffeinate`, a launchd watchdog and resuming interrupted sessions. Chosen.
2. No watchdog. Rejected: a dead orchestrator stops all work until the developer returns.
3. A cloud routine as the watchdog. Rejected: it cannot reach the local tmux server or worktrees.

**Permission prompts.**

1. No push notification unless asked for, and the waiting phase parks. Chosen.
2. Push as today. Rejected: it wakes the developer.
3. No push, but the waiting phase keeps its slot. Rejected: one stuck prompt would halve the work done.

## The design

### 1. Starting and ending

- The developer starts AFK mode by telling the orchestrator so, for example "AFK until 08:00". Optional settings follow, each with a default:

  | Setting | Default | Meaning |
  | --- | --- | --- |
  | `until` | none | When the developer expects to return. Shown in the report, it does not end the mode. |
  | `start` | now | Before this time the orchestrator only reconciles, records and publishes. It starts no phase and no gate. |
  | `sessions` | 2 | The most phase sessions working at once. Parked phases do not count. |
  | `rounds` | 3 | The most failed rounds per gate for each phase, see section 4. |
  | `notify` | off | When on, permission prompts still send a push notification. |

- On start, the orchestrator does these things in order:
  1. Reminds the developer to set or lower the monthly spend limit at claude.ai/settings/usage, because nothing else caps usage credits.
  2. Checks that the watchdog is installed, and asks the developer to install it if not (section 7).
  3. Writes the settings to the tracker and the AFK marker (section 7), and `afk` to the board's `board/meta`.
  4. Starts the keep-awake process (section 7), and warns that a closed lid without an external display still sleeps.
  5. Records a `run-decisions.md` row for the instruction, as today.
- AFK mode ends at the developer's next message in the orchestrator's pane. A turn counts as the developer's unless it is the tick's fixed sentence or a cross-session message. A message the developer types into another session does not end it.
- On ending, the orchestrator's first reply is the return report (section 3). It then removes the marker, stops the keep-awake process, sends `unpark` to every phase parked for a reason other than an open one-way door, and returns to normal mode.

### 2. Decisions

- Work that needs no developer decision comes first. In tick step 3, the orchestrator starts phases with no open one-way request before others, up to the `sessions` cap.
- Phase sessions keep deciding ordinary two-way doors themselves, as `SKILL.md` lines 107 to 110 say.
- A raised two-way request goes to the orchestrator as today. In AFK mode the orchestrator answers it itself. It takes the session's recommendation unless it has a reason not to, and records that reason.
- Before sending `answer`, it adds a row to `run-decisions.md` marked "AFK, pending review", with the request id, and commits it. The `answer` message says the decision is an AFK one.
- A one-way request is not answered. The orchestrator lists it under Needs you. The phase continues with the work the decision does not affect, as now. When nothing else is left, the orchestrator sends it `park` with the reason "one-way door `<id>`", which frees its slot.
- The planner's requests follow the same rules.

### 3. Recording and the return report

- Each AFK decision is a `run-decisions.md` row marked "AFK, pending review", and a `needs` item of a new kind, `afk-decision`, on the board.
- The phase records an AFK answer in its status header's `decisions` list with a new key, `afk: true`. Every other decision has `afk: false`.
- The return report is the orchestrator's first reply on return, in this order:
  1. AFK decisions to accept or change, each with its id, the question, the choice and the reason.
  2. Paused one-way doors, with each one's options and recommendation.
  3. Pull requests ready for review, dependencies first.
  4. Phases parked by the round cap, with their last findings, and other failures and stalls.
  5. Usage: the five-hour and seven-day figures at the start and now, waits for resets, and any limit reached.
- The developer answers "accept all", or names the changes. For each change, the orchestrator sends the phase an `instruction`, which runs a fix round. Either way, it removes the row's mark and sets the phase's decision to `afk: false` through an `instruction`, and the board item is deleted.

### 4. Usage limits

- **Spend.** Only the developer's monthly spend limit on claude.ai caps usage credits. The start step reminds them.
- **Sessions.** At most `sessions` phase sessions work at once. A parked phase does not count.
- **Rounds.** The orchestrator counts each phase's failed verdicts since AFK mode began, from the `at` times in its status file: `NOT VERIFIED` and `INCONCLUSIVE` for Verify, `SIGNIFICANT` for Review. When either count reaches `rounds`, it sends the phase `park` with the reason "round cap". The count is per gate.
- **Usage figures.** In tick step 1 the orchestrator calls the usage tool (section 5).
  - At 95% of `five_hour`, or at a per-model limit message in any pane, it sends `park` to every working phase, until the window's `resetsAt`. It sends `unpark` at the first tick after that time.
  - At 95% of `seven_day`, or at a weekly or monthly spend limit message, it parks every phase until the developer returns.
  - If the tool is missing or returns no windows, the 85% warning in any pane takes the place of both 95% triggers. That is stricter, so a park always has headroom.
  - The 5% headroom pays for the park messages and the next ticks, which matters when the developer has no usage credits.
- A session stopped by a plan limit waits for its own reset. The orchestrator never replaces a session for being rate-limited.

### 5. The usage mod

- A small Claude Code mod, loaded only in the orchestrator's session, registers one tool. The tool returns `$.session.usage().rateLimits` as it is.
- Plan limits belong to the account, so the orchestrator's own session sees the windows that every session spends from. Its figures date from its last API response, which is at most one tick old.
- How it ships is open, see [Risks](#risks).

### 6. Pull requests, merges and the default branch

- Nothing changes in what s-stack may do. Every pull request is a draft. s-stack never marks one ready and never merges into the default branch. The orchestrator branch is not pushed to a public remote.
- Phases open and refresh draft pull requests, the orchestrator merges phases into the orchestrator branch, and fix rounds for failed checks run, all as in normal mode.
- A pull request that carries an AFK decision says so. The PR creator adds one line to its description for each such decision in the phase's `decisions`: "Contains AFK decision `<id>`, pending the developer's review." The line goes at the next refresh after the developer accepts or changes it.
- The board lists those pull requests under the AFK decision's `needs` item.

### 7. Sleep and stops

- **Keep awake.** On entering AFK mode, the orchestrator starts `caffeinate -i -s -w <pid>` in the background, where `<pid>` is its own `claude` process. The Mac then does not idle-sleep while the orchestrator lives, on mains power. A closed lid without an external display still sleeps.
- **Watchdog.** A new script, `scripts/afk-watchdog.sh`, installs a per-user launchd job once, run by the developer. Every 20 minutes the job reads each AFK marker. For each, it runs `launch.sh --feature <feature> --role orchestrator --window <window>`. The launcher prints `alive` and changes nothing when the orchestrator runs. Otherwise it resumes the orchestrator's conversation with its first prompt, and the orchestrator follows `orchestrator.md` "Restarts" (lines 182 to 184): it reads the tracker, arms the tick and runs a tick.
- **The marker.** The orchestrator writes a file `s-stack-afk` in the feature worktree's git directory (`git rev-parse --git-dir`), holding the feature and the window. It is never committed and needs no ignore entry. The orchestrator deletes it when AFK mode ends. Without a marker the watchdog does nothing.
- **Interrupted sessions.** In tick step 1 the reconcile subagent also reports panes that stopped on an API error, such as "Your computer went to sleep mid-response". The orchestrator sends each one a `continue` message at that tick. It is replaced, as `orchestrator.md` line 14 says, only if it is still quiet at the next tick.
- A reboot or a dead tmux server is not covered. The watchdog cannot start a window that no longer exists. The developer runs `workmux resurrect`, as `coordination.md` lines 171 to 176 say.

### 8. Permission prompts

- In AFK mode, a session that waits on a permission prompt gets no push notification, unless the developer set `notify`.
- The prompt goes under Needs you and into the return report. The orchestrator counts the phase as parked, so it takes no slot under the `sessions` cap.
- Nothing is ever approved for the developer.

### 9. Two new messages

| Kind | Sender | When | The message carries |
| --- | --- | --- | --- |
| `park` | Orchestrator | A phase must stop starting work: a round cap, a usage threshold, a start time not yet reached, or an open one-way door with nothing else to do | The reason, and the time to wait until, or "the developer's return" |
| `unpark` | Orchestrator | The reason has passed | Nothing more |

On `park`, a phase session finishes or abandons the subagent step in progress, commits unfinished work as on `stop`, sets `waits_for` to the reason, commits its status and waits. It starts no gate, delegate or PR creator. Unlike `stop`, it keeps its session. On `unpark`, it clears `waits_for`, commits and continues from its recorded state.

## Risks

- **Mod delivery.** APM 0.32.0 deploys skills, agents and instructions. Nothing read in this session shows it can ship a Claude Code mod. The planner proves one of two routes: s-stack ships it, or the developer installs it as a separate plugin, with `packages/s-stack/README.md` saying so. Until then the 85% fallback applies.
- **Usage between ticks.** Figures are read once every 20 minutes. Two working sessions may pass 95% and reach 100% before the next tick. The fallback's 85% pane warning gives more room, and a limited session waits by itself.
- **Credits.** The orchestrator cannot see credit spend. If the developer forgets the spend limit, AFK mode can spend credits up to the next weekly park.
- **The watchdog's environment.** A launchd job runs without the developer's shell `PATH` or tmux variables. The planner proves that it reaches the developer's tmux server and finds `claude`, `workmux` and `tmux`.
- **The keep-awake pid.** The orchestrator must find its own `claude` process id from a Bash tool call, and `caffeinate` must outlive that call. The planner proves both.
- **macOS only.** `caffeinate` and launchd are macOS tools. On Linux the keep-awake step and the watchdog are skipped, and the start message says so.
- **A wrong AFK decision.** It reaches draft pull requests before review. The description line and the return report make it visible, and changing it costs one fix round.
- **A parked phase holds its pane.** Parking keeps the session, so panes stay open overnight. The window may run out of room. The launcher already reports that with exit 4.

## Files this touches

Roadmap, by the spec writer in a roadmap update:

- `README.md`: "What s-stack does" (lines 24 to 60) gains one paragraph on AFK mode.
- `roles.md`: Orchestrator (lines 40 to 63) gains AFK mode in its list of duties (lines 44 to 54).
- `workflow.md`: "One-way and two-way doors" (lines 170 to 178) states the AFK rule. "Every pull request is a draft" (line 153) stays, and gains the AFK description line.
- `coordination.md`: the tick (lines 96 to 112) and its two limits (line 112) gain the watchdog and the usage check. "Permission prompts" (lines 157 to 163) gains the AFK exception. "Restarts" (lines 165 to 186) gains the watchdog. "Parallel work" (line 190) gains the AFK session cap. The message tables (lines 45 to 68) gain `park` and `unpark`.
- `decisions.md`: D10 (lines 86 to 92), D11 (lines 93 to 98), D17 (lines 135 to 142) and D20 (lines 159 to 168) each gain an AFK exception. A new decision, D21, records this proposal.
- `run-decisions.md`: the orchestrator retires the "decided overnight" row (line 79) once AFK mode is built. The spec writer does not edit this file.

Handbooks, references and assets, by the phases that own them:

- `handbooks/orchestrator.md`: Supervision line 13 (a parked phase is not stalled) and line 15 (who decides while AFK). Tick step 1 (line 69) adds the usage tool and API-error panes. Step 3 (line 71) adds the cap and the ordering. Step 5 (line 73) adds AFK answers and silent prompts. Step 8 (line 76) adds the return report. "Decisions" (lines 153 to 157), "Permission prompts" (lines 159 to 161) and "Restarts" (lines 182 to 184) each point to the new reference. A new short section, "AFK mode", names when to read it.
- New `references/afk-mode.md`: the whole of this design's orchestrator rules, read only when AFK mode starts or the tracker shows it on. This keeps the always-read handbook small.
- `SKILL.md`: "Doors" (lines 107 to 110) adds one sentence on AFK answers. "Where to read next" (lines 112 to 117) adds the new reference.
- `references/status-and-messages.md`: the `decisions` entries (lines 51 to 55) gain `afk`. The orchestrator's message table (lines 108 to 122) gains `park` and `unpark`. "Decision requests" (lines 132 to 144) notes the AFK answer.
- `handbooks/phase-session.md`: "Changing state" (line 35) names `park` as a reason to wait. "Messages from the orchestrator" (lines 97 to 106) gains rows for `park` and `unpark`, and the `answer` row (line 101) records `afk`.
- `handbooks/pr-creator.md`: "Descriptions" (lines 131 to 140) adds the AFK decision line.
- `assets/status-board.html`: the schema comment adds `afk` to `board/meta` (lines 30 to 32) and the `afk-decision` kind to `needs` (lines 75 to 77). `NEED_KINDS` (line 288) gains it. A banner shows AFK mode and its settings.
- New `scripts/afk-watchdog.sh`: install, remove and run the launchd job. `scripts/launch.sh` needs no change.
- The usage mod: a new plugin, wherever the planner's proof puts it.
- `packages/s-stack/README.md`: "Requirements" (lines 26 to 31) names macOS for the keep-awake step and the watchdog, and the mod.
- `packages/s-stack/tests/`: tests for `afk-watchdog.sh`, in the style of `test_launch.py`.
- `tests/s-stack/verify-s-stack/checks/`: a check file for the phase that builds this.
