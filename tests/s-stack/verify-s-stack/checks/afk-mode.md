# Phase `afk-mode` checks

Phase `afk-mode` ships AFK mode: `references/afk-mode.md` and its pointers in `handbooks/orchestrator.md`, `handbooks/phase-session.md`, `handbooks/pr-creator.md`, `references/status-and-messages.md` and `SKILL.md`; `scripts/afk-watchdog.sh`; the usage mod in `assets/usage-mod/`, which `scripts/launch.sh` loads into the orchestrator only; the board's Decisions and Permission prompts sections and its AFK notice; and the tmux rule in `SKILL.md`. Prose that agents act on is checked with cold reads, and the scripts and the mod with runs.

A cold read starts a fresh subagent, gives it only the files the check names and the scenario the check quotes, tells it to read nothing else, and asks the questions. Its answer passes when it agrees in substance with every point of the expected answer. Wording may differ, but a missing or contradicting point fails the check. The verifier batches the cold reads that name the same files into one reader and grades every answer itself, as `handbooks/verifier.md` says. Every scenario uses placeholder data: the feature `acme-widgets`, window `@9`, and made-up times, which are UTC.

The board's rendering of the new sections and the AFK notice is checked by `board.md`'s Rerun check, and the launcher's `--plugin-dir` flag by the launcher's unit suite (`test_only_the_orchestrator_loads_the_usage_mod`). Neither is repeated here.

Files, under `packages/s-stack/.apm/skills/sam-mode/`:

- `handbooks/orchestrator.md`, `references/afk-mode.md` and `references/status-and-messages.md`, the orchestrator set
- `handbooks/phase-session.md`
- `handbooks/pr-creator.md`
- the schema comment, the HTML comment at the top of `assets/status-board.html`
- `SKILL.md`

## Rerun

### Watchdog and keep-awake unit tests

The suite runs `afk-watchdog.sh` against private tmux servers, a stub `launchctl` and a stub `caffeinate`, and never loads a launchd job or starts a real `caffeinate`. One test runs the installed plist's `ProgramArguments` under `env -i` with only its `EnvironmentVariables` and asserts the orchestrator starts, then reports `alive`. Run from the repository root.

```bash
env -u TMUX -u TMUX_PANE python3 -m unittest discover -s packages/s-stack/tests -p 'test_afk_watchdog.py' -v
```

Expected on macOS: exit `0`, `Ran 14 tests` and `OK`, with no test skipped. Off macOS the launchd and keep-awake classes skip with their stated reason, which is PENDING, not PASS.

### The watchdog off macOS

Every subcommand but `status` and `run` must refuse with exit `6` off macOS, and `status` must print `unsupported`, without calling `launchctl` or `caffeinate`. A stub `uname` that prints `Linux` stands in for another system, and stubs of `launchctl` and `caffeinate` record any call.

```bash
bash <<'EOF'
set -u
w="$PWD/packages/s-stack/.apm/skills/sam-mode/scripts/afk-watchdog.sh"
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
printf '#!/bin/sh\necho Linux\n' > "$tmp/uname"
for c in launchctl caffeinate; do printf '#!/bin/sh\necho "%s $*" >> "%s/calls"\n' "$c" "$tmp" > "$tmp/$c"; done
chmod +x "$tmp"/uname "$tmp"/launchctl "$tmp"/caffeinate
status=0
for sub in install remove keep-awake stop-keep-awake; do
  err=$(PATH="$tmp:$PATH" HOME="$tmp" "$w" "$sub" 2>&1 >/dev/null); code=$?
  echo "$sub exit=$code $err"
  [ "$code" = 6 ] && [ -n "$err" ] || status=1
done
out=$(PATH="$tmp:$PATH" HOME="$tmp" "$w" status); code=$?
echo "status exit=$code $out"
[ "$code" = 0 ] && [ "$out" = unsupported ] || status=1
[ ! -e "$tmp/calls" ] || { echo "called: $(cat "$tmp/calls")"; status=1; }
[ ! -e "$tmp/Library" ] || { echo "wrote $tmp/Library"; status=1; }
exit $status
EOF
```

Expected: four lines `<subcommand> exit=6 afk-watchdog.sh: <subcommand> needs macOS`, then `status exit=0 unsupported`, and exit `0`.

### Executable modes

The orchestrator runs `scripts/afk-watchdog.sh` directly, and the unit tests run the stubs through `PATH`, so each must be executable in git.

```bash
bash <<'EOF'
status=0
for f in packages/s-stack/.apm/skills/sam-mode/scripts/afk-watchdog.sh packages/s-stack/tests/stubs/caffeinate packages/s-stack/tests/stubs/launchctl; do
  mode=$(git ls-files -s -- "$f" | awk '{print $1}')
  echo "${mode:-untracked} $f"
  [ "$mode" = 100755 ] || status=1
done
exit $status
EOF
```

Expected: three lines, each starting `100755`, and exit `0`.

### The usage mod's own test, and two mutants

`claude plugin test` runs the mod's `register.test.ts` locally, with no model call. The test must pass on the shipped mod and fail on a copy whose tool drops the figures and on a copy whose test calls another tool name, which shows that it reaches the mod's own handler. The tool name the reference tells the orchestrator to call must be the name the test calls. It needs Claude Code with mod support on `PATH`, and without `claude` it prints a PENDING line.

```bash
bash <<'EOF'
set -u
command -v claude >/dev/null || { echo "PENDING: claude not found, so the usage mod cannot be tested here"; exit 0; }
mod="$PWD/packages/s-stack/.apm/skills/sam-mode/assets/usage-mod"
ref="$PWD/packages/s-stack/.apm/skills/sam-mode/references/afk-mode.md"
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
status=0
t() { perl -e 'alarm shift; exec @ARGV' 120 claude plugin test "$1" > "$tmp/out" 2>&1; grep -Eq '^ *1 pass$' "$tmp/out" && grep -Eq '^ *0 fail$' "$tmp/out"; }
if t "$mod"; then echo "shipped mod: pass"; else echo "shipped mod: FAIL"; cat "$tmp/out"; status=1; fi
mutate() { # name, file, perl substitution
  rm -rf "$tmp/m"; cp -R "$mod" "$tmp/m"
  perl -0pi -e "$3" "$tmp/m/$2"
  if cmp -s "$mod/$2" "$tmp/m/$2"; then echo "$1: the substitution changed nothing"; status=1; return; fi
  if t "$tmp/m"; then echo "$1: survived"; status=1; else echo "$1: killed"; fi
}
mutate "empty figures" hooks/register.ts 's/\(await \$\.session\.usage\(\)\)\.rateLimits/[]/'
mutate "other tool name" hooks/register.test.ts "s/'mcp__s-stack-usage__usage'/'mcp__s-stack-usage__other'/"
called=$(grep -o "mcp__[a-z0-9_-]*__[a-z0-9_]*" "$mod/hooks/register.test.ts" | sort -u)
named=$(grep -o "mcp__[a-z0-9_-]*__[a-z0-9_]*" "$ref" | sort -u)
echo "test calls: $called; reference names: $named"
[ -n "$called" ] && [ "$called" = "$named" ] || status=1
exit $status
EOF
```

Expected: `shipped mod: pass`, `empty figures: killed`, `other tool name: killed`, `test calls: mcp__s-stack-usage__usage; reference names: mcp__s-stack-usage__usage`, and exit `0`.

### Cold read 1. Starting AFK mode without the watchdog

Files: the orchestrator set.

Prompt: "Read only these three files and nothing else, not even files they link to. Answer from them and the scenario alone. You are the orchestrator of feature `acme-widgets`, in window `@9`. The feature worktree's root is `/work/acme-widgets`. The tracker does not show AFK mode on. The developer types in your pane: 'AFK until 08:00, sessions 1'. On this machine, `scripts/afk-watchdog.sh status` would print `absent com.s-stack.afk-watchdog.1a2b3c4d`. (1) What do you do, in order, up to the end of that turn? (2) The developer replies 'go without it'. Is AFK mode on, and what do you do now, in order? Give the exact command that writes the AFK marker. (3) Which value does each AFK setting take?"

Expected answer:

1. Remind the developer to set or lower the monthly spend limit at claude.ai/settings/usage, because nothing else caps usage credits. Run `scripts/afk-watchdog.sh status` from the feature worktree's root. On `absent`, ask the developer to install the watchdog by typing `! <this skill's directory>/scripts/afk-watchdog.sh install` in the pane, or to say to go without it, and end the turn. Never install it yourself, because it adds a launchd job to their machine. An answer that installs it, or that writes the marker or the tracker row in this turn, fails this point.
2. The reply belongs to the start, so AFK mode does not end. Go on from step 3: call the usage tool and record the figures; record the tracker's "AFK mode" row with its settings, its start time and the usage at the start; from the feature worktree's root write the marker with `printf '%s %s\n' acme-widgets @9 > "$(git rev-parse --absolute-git-dir)/s-stack-afk"`, which is never committed; write `board/meta.afk`; run `scripts/afk-watchdog.sh keep-awake` and tell the developer that a closed lid without an external display still sleeps; record a `run-decisions.md` row for the instruction and commit.
3. `until` 08:00, which is shown but does not end the mode; `sessions` 1; `rounds` 3; `notify` off; `start` now.

### Cold read 2. Requests while AFK

Files: the orchestrator set.

Prompt: "Read only these three files and nothing else, not even files they link to. Answer from them and the scenario alone. You are the orchestrator of feature `acme-widgets`. The tracker shows AFK mode on since 22:00 with the default settings. The highest AFK ID in `run-decisions.md` is `AFK-7`. This tick's reconcile summary shows four open requests. `alpha`, working in Implement, raised `alpha-r2`: two-way, 'How often should the cache refresh job run?', options 'A. Every hour.' and 'B. Every 15 minutes.', recommendation B; its work goes into pull request 31. `beta`, in Implement, raised `beta-r1`: one-way, 'Nx or Bazel for CI orchestration?', and still has work the decision does not affect. `gamma`, in Implement, raised `gamma-r1`, one-way, and has nothing left that the decision does not affect. The planner raised `planner-r3`, two-way, recommendation A, and you see no reason against A. (1) What do you do with each request, step by step, and with which IDs? (2) What does `alpha` record when your message arrives? (3) Do you reply to the developer at the end of this tick?"

Expected answer:

1. `alpha-r2`: answer it yourself, taking the recommendation, B. Before sending `answer`, add a `run-decisions.md` row with the next free ID, `AFK-8`, `Decided by: AFK` and the mark "AFK, pending review", naming `alpha-r2`, and commit it. Write an `afk-decision` board item with `ref` `AFK-8`, the decision and its reason in full as `detail`, and `prs` holding 31. The `answer` says it is an AFK decision and gives `AFK-8`.
2. `planner-r3`: the planner's requests follow the same rules, so answer A in the same way, with its own ID, `AFK-9` if `alpha-r2` took `AFK-8`. Which request takes which of the two IDs is not scored.
3. `beta-r1`: never answer a one-way request. List it under Decisions on the board with all its fields. `beta` carries on with the work the decision does not affect, and is not parked.
4. `gamma-r1`: not answered, and listed under Decisions with all its fields. Nothing else is left, so send `gamma` `park` with the reason "one-way door `gamma-r1`".
5. `alpha` removes `alpha-r2` from `requests` and records the decision in `decisions` with the ID `AFK-8` and `afk: true`.
6. No. In AFK mode the orchestrator never replies to a tick.

### Cold read 3. Usage signals and the round cap

Files: the orchestrator set.

Prompt: "Read only these three files and nothing else, not even files they link to. Answer from them and the scenario alone. You are the orchestrator of feature `acme-widgets`. AFK mode has been on since 00:30, with `sessions` 2 and `rounds` 3. (1) At the 03:10 tick the usage tool returns `[{kind: five_hour, percentUsed: 96, resetsAt: 04:10}, {kind: seven_day, percentUsed: 40, resetsAt: <Friday>}]`, `alpha` and `beta` are working, and `gamma`'s session is idle at a gate boundary: it is quiet, its status moved to Verify after its start time in the tracker, and nothing you sent it is unanswered. What do you do now, and at the ticks of 03:50 and 04:30? (2) At a tick with usage at 30%, phase `delta`'s verdicts are verify `NOT VERIFIED` at 00:10, verify `NOT VERIFIED` at 01:00, verify `INCONCLUSIVE` at 02:00 and verify `NOT VERIFIED` at 03:00. Phase `epsilon`'s are review `SIGNIFICANT` at 01:30, review `SIGNIFICANT` at 02:30 and verify `NOT VERIFIED` at 02:45. What do you do about each? (3) On another night the usage tool returns an empty list, and one pane shows the warning that 85% of the weekly limit is used. What do you do? (4) A session stopped on a plan limit message. Do you replace it?"

Expected answer:

1. `five_hour` is at 95% or more, so this is a usage pause until 04:10, the window's `resetsAt`. Send `park` to every phase session, working or idle, so to `alpha`, `beta` and `gamma`, each with the reason and 04:10, record a "Usage pause" row ending at 04:10, and record each park in the tracker's "Parks" row with its reason and the time it was sent. While the pause lasts, start no phase session, and do not relaunch `gamma` at its gate boundary. At 03:50 nothing changes: the pause still holds. At 04:30, the first tick after 04:10, the pause ends: delete its row and, in tick step 3, unpark up to `sessions` 2. The third phase stays parked, its reason now "session cap", until a slot frees. Which two go first is not scored. An answer that leaves `gamma` unparked at 03:10, relaunches it before 04:30, or unparks all three at 04:30, fails this point.
2. `delta`: its failed Verify verdicts since AFK mode began are three (01:00, 02:00 and 03:00; the 00:10 one is before 00:30), which reaches `rounds`, so send it `park` with the reason "round cap", until the end of AFK mode. `epsilon`: the count is per gate, two for Review and one for Verify, so it is not parked. An answer that counts the 00:10 verdict, or adds `epsilon`'s two gates together, fails this point.
3. An empty list means the figures are unknown, not zero, so the 85% warning stands in for the 95% signal of the window it names, the weekly one: a usage pause that ends only at the developer's word, so park every phase until the developer tells you to go on.
4. No. A session that a plan limit stopped waits for its own reset, and is never replaced for being rate-limited.

### Cold read 4. The start time, the session cap and the order of work

Files: the orchestrator set.

Prompt: "Read only these three files and nothing else, not even files they link to. Answer from them and the scenario alone. You are the orchestrator of feature `acme-widgets`. The developer started AFK mode at 23:00 with `start` 02:00 and `sessions` 2. (1) At the 23:20 tick, `alpha` is working, with an open one-way request `alpha-r1` and other work it can do, and `beta` and `gamma` have their dependencies met but no session. What does this tick do with each? (2) At the 02:07 tick nothing else has changed. Which phases work after this tick, and which wait? (3) At 04:00, after a usage park ended, three phases are working: `alpha`, started at 21:00, then `beta` and then `gamma`, both started at 02:07. What do you do, and what happens as slots free up?"

Expected answer:

1. Before the start time the orchestrator only reconciles, records and publishes. Every working phase is parked until 02:00, so `alpha` gets `park` until 02:00, and neither `beta` nor `gamma` is started.
2. Phases with no open one-way request are started and unparked before the others, up to `sessions`: `beta` and `gamma` start, and `alpha` waits, parked, because it has an open one-way request and both slots are taken. An answer that also lets `alpha` work, which makes three working phases, fails this point.
3. More phases work than `sessions`, so park the most recently started, `gamma`, with the reason "session cap", and unpark parked phases oldest first as slots free.

### Cold read 5. Prompts, stopped panes and restarts while AFK

Files: the orchestrator set.

Prompt: "Read only these three files and nothing else, not even files they link to. Answer from them and the scenario alone. You are the orchestrator of feature `acme-widgets`, and the tracker shows AFK mode on, with `notify` off. (1) At a tick, `zeta`'s session waits on a permission prompt in pane `%14` for `make deploy-preview`. What do you do, and does `zeta` count towards `sessions`? (2) The same tick, `eta`'s pane shows 'API Error: Your computer went to sleep mid-response'. What do you do now, and at the next tick? (3) Your own claude process exited at 03:05. At 03:20 your conversation resumes and its first turn is the launcher's `/sam-mode orchestrator feature=acme-widgets ...` prompt. What started it, is AFK mode still on, and what do you do in this start beyond a normal restart? (4) Would the same apply at the end of your sixth tick, when you relaunch yourself fresh?"

Expected answer:

1. Send no push notification, because `notify` is off. Write a `prompt` board item, which the board shows under Permission prompts, and list it in the return report. `zeta` takes no slot under `sessions`, but it is not parked: no park is recorded for it, and it gets no `unpark`. Never approve anything for the developer, and never type into the pane.
2. Send `eta` an `instruction` to continue from its recorded state, at this tick. Replace it, as Supervision says, only if it is still quiet at the next tick.
3. The watchdog's launchd job, which runs every 20 minutes and runs the launcher for the orchestrator of each AFK marker, resumed the conversation. The launcher's prompt is not the developer's message, so AFK mode stays on. Restart as the handbook's Restarts says, and, because the tracker shows AFK mode on, run `scripts/afk-watchdog.sh keep-awake` again, because the keep-awake process ended with the `claude` process it waited on.
4. Yes. A fresh relaunch is a start too, so the new session also runs `keep-awake` again and stays in AFK mode.

### Cold read 6. The return and the developer's answers

Files: the orchestrator set.

Prompt: "Read only these three files and nothing else, not even files they link to. Answer from them and the scenario alone. You are the orchestrator of feature `acme-widgets`. AFK mode began at 22:00. Overnight you decided `AFK-8` (`alpha-r2`, every 15 minutes) and `AFK-9` (`beta-r2`, keep the old API). `gamma` is parked for the one-way door `gamma-r1`, `delta` for the round cap, and `epsilon` for the session cap. Draft pull requests 30 and 31 are ready for review, and 31 depends on 30. `alpha` is in PR with draft 30, whose description carries the line "Contains AFK decision `AFK-8`, pending the developer's review." `zeta` has waited on a permission prompt since 05:00. At 06:00 the developer typed 'stop' into `beta`'s pane. At 07:20 the tick fired, at 07:25 Claude Code notified you that a background subagent you started at that tick had finished, and at 07:30 `alpha` sent you a `state` message. At 07:40 the developer types in your pane: 'morning, I'm back'. (1) When did AFK mode end? (2) What is your first reply, in order? (3) What do you do after it? (4) The developer answers: 'AFK-8 is fine. For AFK-9, use the new API.' What do you do for each, what answers each message you send, and what happens to pull request 30's line?"

Expected answer:

1. At 07:40, the developer's message in the orchestrator's pane. The tick's fixed sentence, the subagent's completion notification, `alpha`'s cross-session message and the message typed into `beta`'s pane do not end it.
2. The return report, in this order: AFK decisions `AFK-8` and `AFK-9`, each with its ID, the question, the choice and the reason; the paused one-way door `gamma-r1`, with its options and recommendation; the pull requests ready for review, dependencies first, 30 then 31; `delta` parked by the round cap with its last findings, and other failures, stalls and permission prompts; usage, the five-hour and seven-day figures at the start and now, waits for resets, and any limit reached.
3. Remove the marker, run `scripts/afk-watchdog.sh stop-keep-awake`, set `board/meta.afk` to `null`, record a `run-decisions.md` row for the end, and commit. Delete the tracker's "AFK mode" row and go back to normal mode. The round cap and the session cap end with AFK mode and no usage pause holds, so send `unpark` to `delta` and `epsilon` and remove them from the "Parks" row. `gamma` stays parked until `gamma-r1` is answered, and `zeta` waits on a prompt and was never parked.
4. Send `alpha` and `beta` one `instruction` each. `alpha`'s names `AFK-8`; `beta`'s names `AFK-9` with the change, use the new API, made as a fix round. Each asks the phase to set its decision's `afk` to `false` and send `prs-open` once its pull requests carry the result, without the "pending the developer's review" lines, so pull request 30 loses its line. Each is answered by that `prs-open`, or by a `state` reply from a phase not in PR. Remove "pending review" from both decisions' `run-decisions.md` rows yourself, commit, and delete both board items, the changed one included.

### Cold read 7. A parked phase session

Files: `handbooks/phase-session.md` and `references/status-and-messages.md`.

Prompt: "Read only these two files and nothing else, not even files they link to. Answer from them and the scenario alone. You are the phase session for phase `alpha` of feature `acme-widgets`, in Implement. A delegate is halfway through a code step, with uncommitted edits in the phase worktree. (1) The orchestrator sends `park`, with the reason 'five-hour usage limit' and the time 04:10. What do you do, and what do you not do? (2) At 03:30 your session is relaunched with a new conversation. What do you do? (3) At 04:15 the orchestrator sends `unpark`. What do you do? (4) Earlier, an `answer` arrived for your request `alpha-r2`, saying it is AFK decision `AFK-8`, option B. What do you record, with which ID and keys? What would differ for an ordinary answer from the developer? (5) Later, in PR with draft 30 open, the orchestrator sends an `instruction`: the developer reviewed `AFK-8` and accepts it, so set its `afk` to `false` and send `prs-open` once the pull request carries that. What do you do, does a gate run, and what do you send?"

Expected answer:

1. Finish or abandon the subagent step in progress, commit the unfinished code to the planned pull request it belongs to, as on `stop`, set `waits_for` to the reason, commit the status file and wait. Start no gate, delegate or PR creator. Unlike `stop`, keep the session.
2. `waits_for` is set, so keep waiting for what it names, the `park`, and start nothing it holds back.
3. Clear `waits_for`, commit, and continue from the recorded state.
4. Remove `alpha-r2` from `requests`, record the outcome in `decisions` with the ID `AFK-8`, `afk: true` and the door, clear `waits_for` if the answer ends the wait, commit, and continue the work that waited. An ordinary answer is recorded with an `alpha-d<n>` ID and `afk: false`.
5. Set `AFK-8`'s `afk` to `false` and commit. It asks for a PR creator round, not new work: run PR steps 2 and 3, then send `prs-open`. No gate runs again, and the phase stays in PR.

### Cold read 8. The AFK decision line in a pull request description

Files: `handbooks/pr-creator.md` only.

Prompt: "Read only the file `packages/s-stack/.apm/skills/sam-mode/handbooks/pr-creator.md` and nothing else, not even files it links to or names. Answer from it and the scenario alone. You are the PR creator for phase `widgets`, refreshing its pull request 12. The phase's status `decisions` hold `AFK-3` with `afk: true`, `widgets-d2` with `afk: false`, and `AFK-1` with `afk: false`, which the developer has already reviewed. (1) Which lines about AFK decisions does the description carry, word for word? (2) The developer then reviews `AFK-3`, and the phase sets its `afk` to `false`. What happens to the description at the next refresh?"

Expected answer:

1. One line, for `AFK-3` only: "Contains AFK decision `AFK-3`, pending the developer's review." No line for `widgets-d2` or `AFK-1`.
2. The next refresh removes the `AFK-3` line, so the description carries no AFK decision line.

### Cold read 9. AFK documents on the board

Files: the schema comment only.

Prompt: "Read only the HTML comment at the top of `packages/s-stack/.apm/skills/sam-mode/assets/status-board.html`, which ends at its first `-->`, and nothing else, not the rest of that file and no other file. Answer from it and the scenario alone. You are the orchestrator of feature `acme-widgets`. AFK mode began at 2026-11-23T22:00:00Z. The developer expects to be back at 2026-11-24T08:00:00Z, work starts at once, at most 2 phase sessions run, 3 failed rounds per gate are allowed, and push notifications are off. At 2026-11-24T01:00:00Z you decided `AFK-8`: `alpha-r2`, a two-way door, whose answer is option B, every 15 minutes, because it was the phase's recommendation; pull request 31 carries it. `beta-r1`, a one-way door asking 'Nx or Bazel?', options 'A. Nx.' and 'B. Bazel.', recommendation A, has waited since 2026-11-23T23:00:00Z. `zeta`'s session has waited on a permission prompt in pane `%14` since 2026-11-24T00:30:00Z. (1) Write `board/meta`'s `afk` field and the three `needs` documents, every field. (2) Under which heading does the page show each `needs` document? (3) On return, the developer says they disagree with `AFK-8`. What happens to its document? (4) What happens to `afk` once AFK mode ends?"

Expected answer:

1. `afk` is `{since: "2026-11-23T22:00:00Z", until: "2026-11-24T08:00:00Z", start: null or "2026-11-23T22:00:00Z", sessions: 2, rounds: 3, notify: false}`. `AFK-8`: `kind` `afk-decision`, `phase` `alpha`, a one-line `summary`, `ref` `AFK-8`, `detail` the choice and its reason in full, `prs` `[31]`, `door` `two-way` or `null`, `pane` `null`, `since` 2026-11-24T01:00:00Z. `beta-r1`: `kind` `decision`, `phase` `beta`, `ref` `beta-r1`, `detail` the question's options and the recommendation, `prs` `[]`, `door` `one-way`, `pane` `null`, `since` 2026-11-23T23:00:00Z. The prompt: `kind` `prompt`, `phase` `zeta`, `pane` `%14`, `door` `null`, `prs` `[]`, `since` 2026-11-24T00:30:00Z, and a `ref` and `detail` that are `null` or a short id and text. Every time is a UTC string. An answer that gives the AFK decision the kind `decision`, or leaves out `ref`, `detail` or `prs`, fails this point.
2. `AFK-8` and `beta-r1` under Decisions, the prompt under Permission prompts.
3. It is deleted: an `afk-decision` is resolved once the developer has said whether they agree, whichever way they answer.
4. It is set to `null`, while the developer is present.

### Cold read 10. The tmux rule

Files: `SKILL.md` only.

Prompt: "Read only the file `packages/s-stack/.apm/skills/sam-mode/SKILL.md` and nothing else, not even files it links to. Answer from it and the scenario alone. You are a phase session, running in a tmux pane of the run. A unit test left a tmux server behind whose socket is `/tmp/tmp.abc/tmux-501/default`. (1) A delegate proposes to run `TMUX_TMPDIR=/tmp/tmp.abc tmux kill-server` in your pane to clean up. What would that do, and may you run it? (2) How do you list the sessions on the test's server? (3) You write a new test that starts tmux. How must it run tmux, and what must its teardown do?"

Expected answer:

1. Inside a pane `$TMUX` names the developer's own server, and tmux then ignores `TMUX_TMPDIR`, so the command kills the developer's server, which runs every pane of the run, theirs included. Never run it: never run `kill-server`, and never end a session, window or pane the run did not start.
2. Pass the full socket path with `-S /tmp/tmp.abc/tmux-501/default`, or unset `TMUX`, and first confirm the target with `tmux -S <path> list-sessions -F '#{socket_path}'`.
3. Run tmux with `env -u TMUX` and `-S` into its own temporary directory, and on teardown kill only that server, also when the test fails.

### Cold read 11. A usage pause with every kind of phase

Files: the orchestrator set.

Prompt: "Read only these three files and nothing else, not even files they link to. Answer from them and the scenario alone. You are the orchestrator of feature `acme-widgets`. AFK mode has been on since 00:30, with `sessions` 2 and `rounds` 3, and the tick fires at 10, 30 and 50 minutes past the hour. At the 03:10 tick the usage tool returns `[{kind: five_hour, percentUsed: 96, resetsAt: 04:05}, {kind: seven_day, percentUsed: 40, resetsAt: <Friday>}]`. `alpha` is working, `beta` is idle at a gate boundary, `gamma` is parked for the one-way door `gamma-r1`, `delta` is parked by the round cap, `epsilon` is parked by the session cap, and `kappa`'s dependencies are met but it has not started. `zeta` has waited on a permission prompt since 02:30. (1) What do you send each phase at 03:10, and what do you record? (2) At the 03:30 tick, the reconcile summary shows that the developer approved `zeta`'s prompt in its pane and `zeta` is working again. What do you do? (3) At 03:40 the developer types 'back early' in your pane. Which mode are you in afterwards, what do you do about the parks, and what does the tracker hold? (4) At 03:50 you relaunch yourself fresh after your sixth tick. What does the fresh session do at its 03:50 tick about `kappa`, `beta` and the parks, and what at 04:10? (5) On another night AFK mode is on, `delta` is parked by the round cap and `epsilon` by the session cap, and `alpha` is working. At 02:00 the developer types in your pane: 'Claude just told me we hit the weekly limit, it resets Thursday 09:00.' What do you do that turn, which phases end the turn parked, and when are they unparked?"

Expected answer:

1. This is a usage pause until 04:05: record a "Usage pause" row with its cause and 04:05. Send `park` with the reason and 04:05 to `alpha` and `beta`, and record each park in the tracker with its reason and that time. `gamma`, `delta` and `epsilon` keep their parks and reasons, and get no new `park`. `zeta` is not parked, because it waits on a permission prompt: it gets no `park`, takes no slot, and has a `prompt` board item. Start no phase session, `kappa` included, and do not relaunch `beta`. An answer that parks `zeta`, or re-parks `gamma`, `delta` or `epsilon` with 04:05, fails this point.
2. Its prompt was answered while the pause lasts, so send `zeta` `park` with the reason and 04:05, and record it. Unpark no one.
3. AFK mode ends at that message: give the return report, remove the marker, run `stop-keep-awake`, set `board/meta.afk` to `null`, record the end in `run-decisions.md`, commit, and go back to normal mode. The usage pause outlives the mode, so send no `unpark`. Delete the "AFK mode" row; the "Usage pause" row, ending at 04:05, and the "Parks" row, with every parked phase and its reason, stay. An answer that sends any `unpark` at 03:40, or stays in AFK mode, fails this point.
4. The tracker holds a "Usage pause" row, so the fresh session reads `references/afk-mode.md` and follows its Parks rules while working in normal mode. At 03:50 it starts no phase session, so not `kappa`, unparks none, and does not relaunch `beta`. At 04:10, the first tick after 04:05, it sends `unpark` to `alpha`, `beta`, `zeta`, `delta` and `epsilon`, but not `gamma`, which waits on an open one-way door, deletes the "Usage pause" row, and removes those five from the "Parks" row. The round cap and the session cap ended with AFK mode at 03:40. It does not run `keep-awake` or answer two-way requests itself, because AFK mode is off. An answer that starts `kappa` or unparks anyone at 03:50 fails this point.
5. AFK mode ends at that message, and the reported limit is a usage pause that waits for the developer. Give the return report and do the end's other steps, park `alpha` with the reason, keep `delta`'s and `epsilon`'s parks, send no `unpark`, and delete the "AFK mode" row. The "Usage pause" row ends at the developer's word, because a weekly limit's row says so, and stays with the "Parks" row. All three end the turn parked. They are unparked when the developer tells the orchestrator to go on, not at the reset on Thursday. An answer that unparks `delta` or `epsilon` in that turn fails this point.

### Cold read 12. A weekly pause at the return, and a later AFK start

Files: the orchestrator set.

Prompt: "Read only these three files and nothing else, not even files they link to. Answer from them and the scenario alone. You are the orchestrator of feature `acme-widgets`. AFK mode has been on since Monday 22:00, with `sessions` 2 and `rounds` 3, and the tick fires at 10, 30 and 50 minutes past the hour. At the Tuesday 02:10 tick the usage tool returns `[{kind: five_hour, percentUsed: 30, resetsAt: 06:00}, {kind: seven_day, percentUsed: 96, resetsAt: <Thursday 09:00>}]`. `alpha` and `beta` are working, and `delta` is parked by the round cap. (1) What do you send and record at 02:10? (2) At 07:50 `seven_day` still reads 96%. At 08:00 the developer types 'morning, I'm back' in your pane. Does anyone get `unpark`, and what does the tracker hold afterwards? (3) The developer says nothing more about usage. On Thursday at 21:00 `kappa`'s dependencies are met and it has no session, and the developer types 'AFK until 08:00' in your pane. The watchdog prints `installed`, and the usage tool returns `five_hour` 0% and `seven_day` 3%. What happens to the pause and to each phase, by the end of the 21:10 tick? (4) What would differ in (3) if `seven_day` read 97%? (5) What would differ in (3) if the developer typed 'AFK until 08:00, start 23:00' instead? Does any phase work before 23:00, and what happens at the 23:10 tick?"

Expected answer:

1. `seven_day` at 95% or more starts a usage pause that ends only at the developer's word. Record a "Usage pause" row with its cause and that end. Send `park` with the reason "usage pause" and that end to `alpha` and `beta`, and record both in the "Parks" row. `delta` keeps its round-cap park and gets no second one.
2. AFK mode ends at that message: the return report, whose usage item names the pause and that it waits for the developer's word, then the end's steps, with the "AFK mode" row deleted. The round cap ends with AFK mode, but the pause still holds, because the developer's return alone does not end it, so no phase gets `unpark`. The tracker holds the "Usage pause" row and the "Parks" row with `alpha`, `beta` and `delta`. An answer that unparks anyone at 08:00, or reads "the developer returns" as the pause's end, fails this point.
3. A message that starts AFK mode is the developer's word, so the pause ends at that start's step 3, which finds no signal and starts none. Delete the "Usage pause" row. Every park's reason has now ended, so at the 21:10 tick, in tick step 3, up to `sessions` 2: two of `alpha`, `beta`, `delta` and `kappa` work, and the others stay parked with the reason "session cap". `delta`'s round cap ended with Monday's AFK mode, so it may be one of the two. An answer that leaves every phase parked all night fails this point.
4. Step 3 starts a new usage pause at once, ending at the developer's word, so the phases stay parked, `kappa` does not start, and a new "Usage pause" row is recorded.
5. The pause still ends at step 3, and its row is deleted, but no phase works before 23:00. `alpha`, `beta` and `delta` get no `unpark`: their parks' reasons ended before the `start` time, so each reason becomes `start`, and `kappa` does not start. At the 23:10 tick, the first after 23:00, up to `sessions` 2 of `alpha`, `beta`, `delta` and `kappa` work, and the others stay parked with the reason "session cap". An answer that unparks or starts any phase before 23:00 fails this point.

## Evidence

The phase's verifier runs these when they are in its blast radius and puts every result in its report, never in this file. Neither installs or loads a launchd job, and neither leaves a `caffeinate` running.

### The usage tool in a real session

This shows that a real `claude` session loaded with the mod gets the tool under the name the reference gives, and that it returns the plan's usage windows. From an empty `mktemp -d` directory, run `claude -p "Call the mcp__s-stack-usage__usage tool once and reply with its raw result only." --model haiku --plugin-dir <repository root>/packages/s-stack/.apm/skills/sam-mode/assets/usage-mod --allowedTools mcp__s-stack-usage__usage --output-format stream-json --verbose < /dev/null` under a 300-second bound. The prompt goes first, because `--allowedTools` takes every word after it. Expected: exit `0`; the `init` message lists `mcp__s-stack-usage__usage` among its tools; a `tool_use` of that name; and its `tool_result` is a JSON list whose items each have `kind` `five_hour` or `seven_day`, a numeric `percentUsed` and a `resetsAt`, or `[]`, which the reference reads as unknown. A session without the tool, or a reply with no `tool_use`, fails.

### Keep-awake with the real `caffeinate`

This shows that `keep-awake` holds a real sleep assertion for the session's lifetime and that `stop-keep-awake` and the session's exit both end it. As in the unit test, copy `/bin/bash` to `<tmp>/session/claude`, sign it ad hoc with `codesign -f -s -`, and start it with a pipe as its standard input. From it run `afk-watchdog.sh keep-awake`: it prints `awake claude=<session pid> caffeinate=<pid>`, and `pmset -g assertions` lists `PreventUserIdleSystemSleep` for that `caffeinate` pid. Run `stop-keep-awake`: it prints `stopped caffeinate=<pid>`, and the pid is gone. Run `keep-awake` again, then end the session: the new `caffeinate` exits by itself within a few seconds. Afterwards no `caffeinate -i -s -w` that the run started is left.
