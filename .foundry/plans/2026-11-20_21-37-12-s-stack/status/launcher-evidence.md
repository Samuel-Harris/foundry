# Phase launcher evidence

## Verify, code head `c1ec2d3d85a9f5f9535101e63ac9956ebaa32371`, VERIFIED

A fresh verifier ran on 21 November 2026. The behavioural checks and their results are in `tests/s-stack/verify-s-stack/checks/launcher.md` at that head.

- The verification skill passed in full. That covers primitives (94 valid), the root manifest (`12 listed, 19 reached`), Markdown lint, line budgets and package isolation. The launcher suite ran 35 tests, all OK. Tier 1 printed `all Tier 1 structural checks passed across 20 packages`. The foundation cold reads passed. Handbook routes were pending, as expected.
- Nine mutations of `launch.sh` each failed at least one named test.
- Live check, with the real `claude` and the real `workmux` on a private tmux server in a scratch repository. The phase pane showed `Unknown command: /sam-mode` with the arguments `phase feature=probe phase=live ...`, because `sam-mode` is not deployed there. So the first prompt's first words were `/sam-mode phase`. A second launch printed `alive probe-phase-live pane=%1`, and the panes were unchanged. On `/exit`, Claude printed the conversation id that the launcher had stored.
- Minor gaps the verifier recorded. The real `sam-mode` did not load in the scratch repository. A real `--resume` relaunch was not run, so resume is proven by the unit suite and the `/exit` id. Roadmap `coordination.md` and C4 still say restarts use `claude --continue`, and neither lists `--print-window`, `--close`, `--remove` or exit 5. That text is owned outside this phase.

This verdict is superseded by the merge of `s-stack-package` at `4739703`, which brings new files and so a new code head.

## Verify, code head `2726205c5a71584501fb366f588125c64af9cfbd`, VERIFIED

A second fresh verifier ran at the merged head on 21 November 2026, in full. The results are recorded under "Rerun at `2ecc9f0`" in `tests/s-stack/verify-s-stack/checks/launcher.md`.

- The verification skill passed in full, including Tier 1 across 20 packages and the cold reads of the newly merged `planner.md` and `spec-writer.md`. The suite ran 35 tests, all OK.
- Four mutations each failed named tests.
- Every launcher call written in `SKILL.md` and `spec-writer.md` was run against the launcher with stubs, and each was accepted.
- Live check with the real `claude` and `workmux`. The first prompt began `/sam-mode phase`, and the second launch printed `alive`. After `/exit`, a relaunch ran `claude --name probe-phase-live --resume <the stored id>` and showed the earlier conversation.
- Minor findings, recorded and not fixed, under the orchestrator's minor-findings rule:
  - A pane left at its shell after `claude` exits is not reused. A relaunch splits a new pane, and `--close` does not clear a dead pane.
  - `SKILL.md`'s `start` form covers only the first spec writer. A restart needs `--window`, as C4 says.
  - The real `sam-mode` did not load in the scratch repository.

## Review, code head `2726205c5a71584501fb366f588125c64af9cfbd`, SIGNIFICANT

The review ran p-stack's `interrogate` skill with two adversaries, on Opus and on Fable. The Gemini seat was dropped, because this host has no Gemini model. The phase session reran every finding below on macOS, and each reproduced. Repros are in the adversaries' worktrees under `.claude/worktrees/` in the main checkout.

1. Outside a UTF-8 locale, tmux replaces the tab separators in `list-panes -F` output with `_`, so no live session is ever detected. Under `LC_ALL=C` a second launch starts a second copy, `--close` reports `absent`, and `--remove` deletes the worktree under two live sessions. Found by Fable.
2. Derived names collide across features. The planner of `a-phase` and phase `planner` of `a` are both `a-phase-planner`. The planner of `trip` reuses, and `--remove` deletes, feature `trip-planner`'s worktree. Found by both. Settled as `launcher-d8`.
3. Two concurrent launches of one name, with the worktree present, start two copies. Found by both.
4. A launch into a zoomed window unzooms it and shrinks the zoomed pane. Found by both.
5. `--print-window` with a stale `TMUX_PANE` prints `window=` and exits 0. Found by Fable.
6. With no tmux server running, `--close` and `--remove` exit 1 instead of `absent` and a normal removal. Found by Fable.
7. `--remove` removes a worktree whose detached HEAD holds commits that are on no branch, and a worktree in which another `claude` is still working. Found by Fable.

## Verify, code head `15bb919f5f9e85fca556362ac5bdb2897900b955`, VERIFIED

A third fresh verifier ran after the review fix round and the merge of phase-handbooks. Its results are under "Rerun at 8839699" in `tests/s-stack/verify-s-stack/checks/launcher.md`.

- The full skill passed, with Tier 1 across 20 packages and nine cold reads. 47 tests pass, and they pass again under `LC_ALL=C`.
- Each of the seven review defects was reproduced against the fixed launcher with stubs and is fixed.
- Six mutations each failed named tests. All three launcher calls in `SKILL.md` and the handbooks were accepted.
- Live check with the real `claude`. The first launch took 0.75 s, then `alive`, then `/exit` and a relaunch with `--resume <stored id>` showing the earlier conversation.
- Minor findings, recorded:
  - `verifier.md` says `## Evidence` holds no results, which contradicts C6.
  - With no tmux server, tmux's own `no server running` line reaches standard error.
  - Cold readers found small ambiguities in `SKILL.md` and `phase-session.md`.

This verdict is superseded. The developer's pane placement rule (`launcher-d9`) is a scope change, so the phase moves back to Implement.

## Verify, code head `13104cc935a923cc9511d71570ac51683a012246`, VERIFIED

A fourth fresh verifier ran after the placement rule, pane reuse, their quick-review fixes and the merge of `s-stack-package` at `c18fb91`. It committed nothing. Its report, summarised:

- The full verification skill passed. Primitives were valid (94), the root manifest printed `12 listed, 19 reached`, lint and budgets passed, and isolation passed. The suite ran 83 tests, all OK, and again under `LC_ALL=C` with `LANG` and `LC_CTYPE` removed. Tier 1 printed `all Tier 1 structural checks passed across 20 packages`. All nine cold reads passed.
- Twelve mutations each failed named tests. They covered select-layout, liveness, the session lock, `--resume`, the orchestrator's column, the sidebar, the window lock, unzooming, re-zoom on failure, reuse, the resumed-nameless rule and the dirty-worktree guard.
- Placement was reproduced with the stubs on a 240x60 private server, with and without a sidebar. Each pane went where the rule says. The sidebar and an untagged developer pane in the orchestrator's column never changed. A zoomed orchestrator stayed zoomed and kept its width. Three concurrent phase launches all started with the orchestrator's width unchanged. A restart reused the same pane and resumed the stored id. A planner with no orchestrator exited 1, and an orchestrator with no spec writer split the topmost pane of the first column.
- All three launcher calls in `SKILL.md` and `spec-writer.md` were accepted.
- Live check with the real `claude` and `workmux`. The first launch took 1.09 s and placed the pane right of the orchestrator. The first prompt began `/sam-mode phase`. A second launch printed `alive` in 0.25 s. `/exit` and a relaunch put `claude --resume <stored id>` in the same pane, with the earlier conversation shown.
- Minor gaps recorded:
  - While the orchestrator shares its column (spec writer alive, or a pane below it), the right-hand area is only as tall as the orchestrator's pane, so space runs out early and launches exit 4.
  - A launch that exits 4 has already created its worktree.
  - The scratch repository has no `sam-mode`.
  - `checks/launcher.md` has no one-off layout reproduction, though the unit tests cover each case.
  - `tests/s-stack/verify-s-stack/SKILL.md` check 8 still says `## Evidence` holds results.

## Review, code head `13104cc935a923cc9511d71570ac51683a012246`, SIGNIFICANT

p-stack's `interrogate` skill ran with two adversaries, on Opus and on Fable. The Gemini seat was dropped, because this host has none. The phase session reran each finding below, and each reproduced. Repros are in the adversaries' worktrees under `.claude/worktrees/` in the main checkout.

1. A restart in the session's own pane kills a command the developer runs there. The pane counted as idle when no `claude` ran in it. Found by both.
2. A plain `claude` in the feature worktree beside the named orchestrator makes every planner, phase and update spec writer launch exit 1. With no orchestrator ever launched, the same plain `claude` is reported as the orchestrator, `alive`. Found by both.
3. Under `LC_ALL=C`, tmux prints a non-ASCII character in `#{pane_current_path}` as `_`, so a worktree under such a path never matches. The first launch fails after `workmux add`, and a resurrected orchestrator is duplicated. Found by both.
4. The first spec writer is respawned into the workmux sidebar when the sidebar is the new window's first pane. Modelled with a stub workmux. Found by both.
5. Two launches that each add a worktree fail when `workmux add` takes over 10 seconds, because the worktree lock waits 10 seconds. Found by Fable.
6. A `claude` that exits at once is reported as `started` with exit 0, after a wait of about 15 seconds. Found by Fable.
7. `--close` in a zoomed window unzooms it. Found by Fable.
8. Run outside a git repository, the launcher creates its lock directory in the working directory. Found by Fable.

Recorded, not fixed:

- A `claude` running outside tmux is invisible to liveness and to `--remove`. The launcher manages tmux sessions only. Found by both.

Dismissed:

- `scripts/versioning.py check` fails on the phase branch. Under C7 a phase branch never bumps, and the PR creator's regenerate commit raises the version on the pull request branch.

## Verify, code head `310d2dff457fe1e8e4163280000f93242feab154`, NOT VERIFIED

A fresh verifier ran the full skill, Tier 1, the cold reads, the live check and 18 mutations. Two checks failed.

1. Dropping the window placement lock left all 98 tests passing. The concurrency test asserted only that each new pane lay right of the orchestrator and that the orchestrator stayed at least as wide. Without the lock, three launches each made their own full-span column, and two of those columns were 1 cell wide.
2. With no tmux socket directory at all, `--close` and `--remove` exited 1. tmux then prints `error connecting to ... (No such file or directory)`, not `no server running`.

Everything else passed. That covered all other review defects, full-height placement with and without a sidebar, the named-orchestrator precedence, a busy pane surviving a relaunch, a non-ASCII path under `LC_ALL=C`, stale and live locks, and a real `claude` launched in 0.52 s, then alive, then resumed in its own pane.

Minor findings:

- A concurrent launch can print a `holder: No such file or directory` line on standard error.
- `checks/launcher.md` lacks newer mutations, a layout and stale-lock reproduction, and the note that the trust dialog's cursor starts on "No, exit".

## Verify, code head `42d3ced56004988cc8e3db84280237636fc19491`, VERIFIED

A fresh verifier ran with nothing committed. Its report, summarised:

- The full verification skill passed. Primitives were valid (94), the root manifest printed `12 listed, 19 reached`, and lint, budgets and isolation passed. 100 tests passed, and again under `LC_ALL=C`. Tier 1 passed across 20 packages, and all nine cold reads passed.
- All 16 mutations listed in `checks/launcher.md` and 3 extra ones each failed named tests, with an unmutated control passing beside them.
- The layout reproduction ran on 240x60 private servers, with and without a sidebar. The sidebar stayed 20 wide. The first phase column was full height, and the orchestrator's column stayed at least as wide (120 against 119, 109 against 109). Later phases tiled inside that column, and the developer pane was never split. With a developer's unnamed `claude` below the named orchestrator, phases were placed by the named one and `alive` named the right pane.
- A SIGKILLed holder's lock was taken over in 0.61 s.
- Both findings at 310d2df are fixed. The window-lock mutant failed 5 runs of 5. With tmux never run, `--close` printed `absent` and `--remove` removed the worktree, kept the branch and refused a second time with exit 5.
- All three launcher calls in the handbooks were accepted.
- Live check with the real `claude` 2.1.330 and `workmux` 0.1.283. The first launch took 0.41 s, and its first prompt began `/sam-mode phase`. The second launch printed `alive` with no pane change. `/exit` and a relaunch took 0.19 s, used the same pane, ran `--resume` with the stored id, and showed the earlier conversation.
- Minor gaps recorded and not fixed, under the minor-findings rule:
  - Before tmux has ever run, tmux's own `error connecting to` line still reaches standard error.
  - `checks/launcher.md` does not say how to hold a launch inside its lock (`tmux set-environment -g STUB_CLAUDE_DELAY`).
  - It does not say how to make a macOS sidebar stub (codesign the copied `sleep`).
  - It still asks for the developer's server to have exactly its earlier sessions, not just none of the verifier's.

## Review, code head `42d3ced56004988cc8e3db84280237636fc19491`, SIGNIFICANT

p-stack's `interrogate` skill ran with adversaries on Opus and Fable. The Gemini seat was dropped, because this host has none. The phase session reran each finding below, and each reproduced. Repros are in the adversaries' worktrees under `.claude/worktrees/` in the main checkout.

1. **Stale-lock takeover races.** A waiter can move aside a fresh lock that another launch has just taken. With a stale session lock and eight concurrent launches, two or three copies of one session started, and other launches exited 1 with `cannot record the holder`. With a stale window lock and six phase launches, several full-span columns opened, some 1 column wide. Found by Fable.
2. **Start times depend on time zone and locale.** `ps -o lstart=` is formatted in the caller's time zone, and on macOS in its locale too. Two launches with different `TZ` or locale each misread the other's live lock as stale and both started the session. Found by both.
3. **The first spec writer is duplicated after a hand resume.** Resumed by hand with `claude --continue` in its own tagged pane, it is not seen as alive, and a relaunch starts a second copy. Found by Opus.
4. **Prompt helpers make an idle pane look busy.** A zsh helper such as gitstatusd gives the shell a background child at its prompt, so the pane counts as busy and every restart splits a new pane. Found by Opus.
5. **A developer's command can still be killed.** `--close` kills a command the developer runs in the session's left-over pane. A restart kills a command started with `exec` in that pane. Found by Fable.

Accepted, not a defect:

- A developer pane spanning the full width under the orchestrator narrows with the full-span split, as `launcher-d11` accepted.

## Verify, code head `061f71e3849fa779879183f90ff825a3071525a2`, NOT VERIFIED

A fresh verifier ran the full skill, Tier 1, the board's rendered check, every cold read, 22 mutations and the live check. Every behaviour it ran passed. That covered all five defects from the third review, fixed in its own reproductions, and the `launcher-d16` idle rule at runtime, with `bash build.sh` and `sh -c` panes surviving and `bash`, `zsh -l` and `-zsh` reused. A real `claude` launched in 0.42 s, reported `alive`, and resumed by id in the same pane.

It failed one check. Deleting the argument rule in `pane_is_idle` left all 113 tests passing, and that launcher kills a developer's shell script on restart and on `--close`, which the verifier reproduced. The busy-shell tests ran `sleep` as a child, and that child made the pane busy by itself.

The phase session fixed the tests. The shells now block in the `read` builtin, and both tests fail against that mutant. `checks/launcher.md` now lists the idle-rule and lock mutations, says to wait for the trust dialog to draw, and checks only that nothing of the check's is left on the developer's server.

## Verify, code head `0ad72927067f8875e5db62d10156c4c867b9291b`, VERIFIED

A fresh verifier ran with nothing committed. Its report, summarised:

- The full skill passed: primitives, the root manifest, lint, budgets and isolation. 113 tests passed, and again under `LC_ALL=C`. Tier 1 passed across 20 packages. The board's rendered check passed, and all nine cold reads passed.
- 31 mutants ran on scratch copies, with a control passing beside them. Every mutant fails named tests, except one equivalent mutant: dropping only the branch-merged guard in `--remove`, which the HEAD-merged guard covers.
- The fix for 061f71e holds: deleting the argument rule in `pane_is_idle` fails both busy-shell tests.
- Reproductions, with and without a sidebar:
  - The shared-column layout kept the sidebar at 20 columns. The first phase column was full height, and later phases tiled in it.
  - With a developer's unnamed `claude` present, the named orchestrator took precedence.
  - A SIGKILLed lock was taken over in 0.67 s.
  - Under the `launcher-d16` idle rule, `bash build.sh` and `sh -c` panes survived a restart and `--close`, while `bash`, `zsh -l` and `-zsh` panes were reused.
  - All five defects from the third review stay fixed.
- Live check with the real `claude` 2.1.330. The first launch took 0.44 s, `alive` came in 0.18 s, and a relaunch after `/exit` in 0.30 s reused the same pane with `--resume <stored id>`.
- Minor gaps recorded and not fixed:
  - The stale-lock and sidebar recipes in `checks/launcher.md`.
  - The equivalent mutant.
  - The `## Evidence` wording in the verification skill's check 8.
  - The real `sam-mode` does not load in a scratch repository.

## Review, code head `0ad72927067f8875e5db62d10156c4c867b9291b`, SIGNIFICANT

p-stack's `interrogate` skill ran at 481497e with adversaries on Opus and Fable. The Gemini seat was dropped, because this host has none. Findings were judged by the orchestrator's bar: a finding is significant only if it breaks the common path. Anything needing a rare or adversarial setup is recorded here and not fixed.

Significant, to be fixed:

1. **The first right-hand column can be squashed to 1 column.** When a pane spans beyond the orchestrator's pane, the restore after the full-span split gives it back its full width, so the new column ends 1 column wide while the launch reports `started`. Such a pane is the full-width spec writer above an orchestrator with a developer shell opened beside it, or a full-width developer pane above or below the orchestrator. Found by both. Placement is on the common path.
2. **`COLUMNS` blinds the launcher on Ubuntu.** procps truncates `ps -A -o args=` to `COLUMNS` even into a pipe. A caller that exports `COLUMNS` therefore makes the launcher miss live sessions: every launch fails with `claude did not start` and leaves another copy running. Found by Fable. It is a duplicate session on the common path when the caller's environment exports `COLUMNS`.

Recorded, not fixed (rare or adversarial setups):

- A script fed to bash on standard input (`bash < build.sh`, or `curl … | bash` once the left side exits) in a session's left-over pane reads as idle, so a restart or `--close` kills it. Found by Opus.
- A stale breaker lock, left only by a SIGKILL inside its brief window, can let two copies start under twelve concurrent launches. Found by Opus.
- `/sam-mode start` when no tmux server has ever run exits 1 before `workmux add`. It was shown with the stub only, and whether the real workmux would start the server is unverified. Found by Opus.
- A background or suspended job in a session's left-over pane is killed by a restart or `--close` on macOS, because idleness looks at the foreground group only. Found by Fable.
- A command started in the left-over pane during a slow `workmux add`, after a `--remove`, is killed, because the idle check ran before the add. Found by Fable.
- Under a Latin-1 locale on macOS, Bash 3.2's `[a-z]` follows collation, so names that are not kebab-case pass validation. Found by Fable.

## Verify, code head `e8bc6e10bacd2b790df9b238975ae24750d61bb9`, VERIFIED

A fresh verifier ran with nothing committed. Its report, summarised:

- The full skill passed, with 118 tests on macOS (also under `LC_ALL=C`) and on Ubuntu 24.04. Ubuntu skipped 4: three need zsh, and one needs a locale-sensitive `ps`. Tier 1 passed across 20 packages, the board's rendered check passed, and every cold read passed.
- All 21 listed mutations and 3 extra ones fail named tests. The `-ww` mutant is killed on Ubuntu only, because macOS `ps` never truncates.
- Both fixes held:
  - With a pane spanning the orchestrator's column, the first phase column was full height, 40 to 94 columns wide and no wider than the orchestrator's column, with and without a sidebar. Developer columns kept their widths.
  - `test_an_exported_columns_does_not_hide_a_live_session` passes on Ubuntu.
- Parallel relaunch after a simulated crash: four phases had their `claude` SIGKILLed, with stale locks planted, including a reused PID and a stale window lock. Twelve concurrent launches gave exactly one `started` per name, each in its own earlier pane with `--resume`, plus eight `alive`, twelve exits of 0, an unchanged pane count and one `claude` per name.
- The idle rule, the named-orchestrator precedence and stale-lock takeover all held.
- Live check with the real `claude` 2.1.330. The first launch took 0.63 s, `alive` came in 0.18 s, and a relaunch after `/exit` in 0.34 s used the same pane with `--resume <stored id>`.
- Minor gaps recorded:
  - `checks/launcher.md` has no mutation or reproduction for this round's two fixes, though the suite catches both.
  - The `-ww` regression is caught only on Linux.
  - Cold readers flagged ambiguities in files the launcher does not own.

## Review, code head `e8bc6e10bacd2b790df9b238975ae24750d61bb9`, SIGNIFICANT

p-stack's `interrogate` skill ran at 79c8715 with adversaries on Opus and Fable, under the orchestrator's common-path bar. Both adversaries found the same two defects independently, and the phase session reran both.

1. **A developer's own `claude` was taken for the orchestrator.** After the orchestrator's `claude` exited, a plain `claude` the developer opened in an untagged pane of the feature worktree counted as the resurrected orchestrator. A relaunch printed `alive` at the developer's pane instead of restarting the orchestrator in its own idle pane. The next update spec writer then split the developer's pane, and the next planner was placed against it. After a real resurrect, the same developer `claude` made every planner and phase launch exit 1 with `more than one pane runs`.
2. **The documented spec-writer call could not restart it.** `launch.sh --feature <f> --role spec`, the only spec call `SKILL.md` documents, exited 2 with the usage text on every run after the first, alive or not. With the caller's own window passed, it split the developer's pane instead of reusing the spec writer's own idle pane.

Both held up everywhere else: the full documented flow, parallel launches and relaunches after crashes and after a resurrect, developer splits around the orchestrator, and zsh panes.

## Verify, code head `5ba7c2d20de90afed4b569e9b297f146c730a8af`, VERIFIED

A fresh verifier ran with nothing committed. Its report, summarised:

- The full skill passed: 122 tests on macOS in both locales and in the Ubuntu container, with four skips that need zsh or a locale-sensitive `ps`. Tier 1 passed across 20 packages, the board's rendered check passed, and all nine cold reads passed.
- 23 mutants, including two new ones for this round's fixes, each failed named tests.
- **Developer's `claude` fix.** After the orchestrator's `claude` was killed beside a developer's plain `claude`, a relaunch restarted the orchestrator in its own pane with `--resume`, and the developer's `claude` kept its PID. The update spec writer and planner were placed by the orchestrator, and the developer's pane was never split. After a simulated resurrect (`claude --continue`) beside the developer's `claude`, planner and phase launches succeeded and the orchestrator was reported `alive` at the resurrected pane.
- **Spec-writer restart fix.** `--role spec` with no `--window` printed `alive` while the spec writer lived, restarted it in its own pane with `--resume` after its `claude` died, and exited 2 naming `--window` when its pane was gone or busy.
- **Parallel relaunch after a crash.** With panes kept and stale locks planted, eight launches gave one `started` per name in its earlier pane with `--resume`, plus four `alive`. With every pane gone and a resurrected orchestrator, four launches shared one full-height column.
- Live check with the real `claude` 2.1.330. The first launch took 0.88 s, `alive` came in 0.13 s, and a relaunch in 0.25 s used the same pane with `--resume`.
- Minor gaps recorded:
  - The check file lacks this round's mutations and the lock-holding recipe.
  - A launch SIGKILLed between starting its pane and `claude` appearing in `ps` can lead to a duplicate. This was seen only with the stub's 3 s delay.
  - The exit-2 message says no pane is left when the pane is busy.
  - `-ww` regressions are caught on Linux only.

## Review, code head `5ba7c2d20de90afed4b569e9b297f146c730a8af`, SIGNIFICANT

p-stack's `interrogate` skill ran at 5ebe77d with adversaries on Opus and Fable, under the orchestrator's common-path bar. The phase session reran or checked each finding below.

1. **A named session restarted with other options first goes unrecognised.** A session restarted as `claude --continue --name <session>` was classed `other`, because the strict rule wanted `--name` as the first argument. A relaunch therefore started a second copy, and `--close` left the first running. A read-only `ps` on the developer's machine shows a live s-stack session in exactly this shape. Found by Fable.
2. **A plain `claude` in a session's own pane counts as the session.** A plain `claude` the developer types into a session's own tagged pane after its `claude` exits was counted as the live session. The session was never restarted, and after a restart in a new pane every launch exited 1 with `more than one pane runs`. Found by Opus.
3. **Open/close cycles squeeze the orchestrator's column.** With a developer column right of the orchestrator's column, as the developer's workmux layout gives (a shell pane beside the agent pane), `--close` of a phase handed its width to the developer column, never back. Four open/close cycles left the orchestrator and the new phase 5 columns wide, with exit 0. Found by Fable.
4. **A resurrected spec writer goes unrecognised.** After `workmux resurrect` during the spec interview, the resurrected spec writer is an untagged `claude --continue` in the feature worktree. `launch.sh --feature <f> --role spec` exited 2, and with `--window` started a second copy on the same conversation. Found by Fable.

Recorded, not fixed:

- A resurrect leaving both a spec writer and an orchestrator as `claude --continue` in the feature worktree blocks every launch with `more than one pane runs`. `workmux resurrect` compacts recovery to one candidate per working directory, so the real tool does not produce two. Found by Fable.

## Verify, code head `e7405c5c33a60d71a726f857443b44b7587c9fe6`, VERIFIED

A fresh verifier ran with nothing committed. Its report, summarised:

- The full skill passed: 127 tests on macOS in both locales and in the Ubuntu container in both locales (four environmental skips). Tier 1 passed across 20 packages, the board's rendered check passed, and all nine cold reads passed.
- Of 26 mutants, 25 are killed on macOS. The `-ww` mutant is killed on Ubuntu. The four undone fixes are each killed by their own test.
- All four fixes reproduced:
  - `claude --continue --name <s>` and `claude --model m --name <s>` are recognised and closed.
  - A plain `claude` in the orchestrator's own pane is left running, and the orchestrator restarts with `--resume`.
  - A resurrected spec writer is reported `alive` by the documented call.
  - Four open and close cycles leave the sidebar, orchestrator and developer column exactly at their starting widths.
- Parallel relaunch after a simulated crash: ten launches gave one `started` per name, in its earlier pane with `--resume`, plus one `alive` each.
- Layout with and without a sidebar, precedence and stale-lock takeover all held.
- Live check with the real `claude` 2.1.330. The first launch took 1.35 s and `alive` came in 0.37 s. A message got the reply `acknowledged`. A relaunch after `/exit` used the same pane with `--resume` and showed that earlier exchange.
- Minor gaps recorded:
  - The check file lacks this round's mutations and a parallel-relaunch recipe.
  - `-ww` regressions are caught on Linux only.
  - `sam-mode` does not load in a scratch repository.
  - After a plain `claude` takes the orchestrator's old pane, the relaunched orchestrator splits that pane, and both panes then carry the `f-orchestrator` tag. The developer's `claude` is untouched and placement uses the new pane.

## Review, code head `e7405c5c33a60d71a726f857443b44b7587c9fe6`, SIGNIFICANT

p-stack's `interrogate` skill ran at 986b6e5 with adversaries on Opus and Fable, under the orchestrator's common-path bar.

1. **An orchestrator started by a resurrected spec writer cannot be restarted.** After a resurrect during the spec phase, the resurrected spec writer (an untagged `claude --continue`) started the orchestrator as `spec-writer.md` says, and kept running. When the orchestrator crashed, a relaunch reported it `alive` at the spec writer's pane, and it could never be restarted. Found by Opus.
2. **`--close` misplaces freed width with two developer columns.** With two developer columns right of the orchestrator's column, the width a closed phase freed stopped in the developer column nearest the orchestrator. Three open and close cycles left the orchestrator 11 columns wide. Found by Fable.
3. **`--close` narrows a sibling in a shared column.** Closing a session whose pane the developer had split side by side resized the whole stacked column, so a live phase in the same column lost half its width. Found by Fable.

## Verify, code head `cf378d80b95d4e250c2a5473876db547b2f72d24`, VERIFIED

A fresh verifier ran with nothing committed. Its report, summarised:

- The full skill passed: 130 tests on macOS in both locales and on Ubuntu in both locales (four environmental skips). Tier 1 passed across 20 packages, the board's rendered check passed, and all nine cold reads passed.
- All 21 listed mutants and the three undone fixes are killed. One extra mutant survives: dropping only the `[ -z "$matches" ]` guard lets an untagged `--continue` claude replace a hand-started named orchestrator in an untagged pane. A launcher-started orchestrator is tagged, so this is off the common path.
- All three fixes held:
  - The orchestrator started by a resurrected spec writer restarts in its own pane with `--resume`, and the spec writer is untouched.
  - Three cycles past two developer columns leave every width exactly unchanged.
  - Closing a phase beside a developer split leaves phase b and the orchestrator unchanged.
- Relaunches held:
  - Parallel relaunch after a crash with stale locks: ten launches gave one copy per name in its own pane in 0.58 s.
  - Resurrect relaunch: every session was placed in one full-height column.
- Live check with the real `claude` 2.1.330. The first launch took 0.49 s, `alive` came in 0.22 s, and a relaunch after `/exit` in 0.33 s used the same pane with `--resume`.
- **Safety incident.** One of the verifier's setup scripts set `TMUX_TMPDIR` to a directory not yet created. tmux then fell back to the default socket, and a `new-session -d` created session `$4` on the developer's server: one window holding a shell and the workmux sidebar, both in the verifier's scratch repository. The verifier's kill was refused by the permission check. The phase session confirmed the contents read-only and asked the developer to remove it. Later briefs require creating `TMUX_TMPDIR` before any tmux call, and confirming that `tmux list-sessions` cannot connect there before creating a server.
- Minor gaps recorded:
  - The check file lacks this round's mutations and the relaunch recipes.
  - Its safety advice checks the socket only after a server is created.

## Review, code head `cf378d80b95d4e250c2a5473876db547b2f72d24`, CLEAR

The review ran under the gate-cost rules. Its scope was the diff since the last reviewed head, e7405c5 to cf378d8: the width hand-back in `--close` and the untagged `--continue` fallback. Being logic, it could not be waived. The first reviewer (Opus) reviewed and returned CLEAR. The second adversary (Fable) then joined, as rule 5 requires, and also returned CLEAR.

- **Opus.** Seven repro scenarios all ended with the orchestrator and developer columns within one column of their starting widths: a full-width developer pane at the bottom; overlapping phases in a 400-column window; phases side by side; a planner plus two phases; an update spec writer; the real start order with parallel phases; and a simulated resurrect with parallel phase relaunch.
- **Fable.** It covered what Opus did not, and every case behaved as intended:
  - a zoomed orchestrator or developer pane during closes;
  - a developer column between the orchestrator and three stacked phases;
  - an update spec writer beside a split developer column;
  - parallel starts and closes;
  - a 420-column window with developer splits under and beside phases;
  - the real start order with idle tagged panes;
  - a zoomed phase closed;
  - a resurrect with a developer column;
  - a dead orchestrator beside a developer's `claude --continue`.
- **One cosmetic observation.** Closing the zoomed pane itself prints `can't find pane` on standard error from the re-zoom, with exit 0 and correct output. That code predates this diff.

## Verify, code head `36ea9023e2a6dc555a8e7d4b65e2d630440fec01`, VERIFIED

This round ran under the gate-cost rules. The scope was the diff since cf378d8. Its only phase change is one line in `build_system_bin` in `packages/s-stack/tests/launcher_case.py`: `not link.exists()` became `not os.path.lexists(link)`. The other files in the diff came in by merges, and they count as verified. The verifier did not waive, because a condition is control flow.

- Blast radius: every check that runs the unit suite, which is the two Rerun suite checks and the mutations in `checks/launcher.md`. The other check files never name or run the tests, and are out of scope.
- macOS: 130 tests passed, also under `LC_ALL=C`.
- Ubuntu container with dangling links planted in `/usr/bin` and `/bin`, as on the GitHub runner: 130 tests passed. The fixture at cf378d8 ran 0 tests in the same run and failed with 18 `setUpClass` errors, each a `FileExistsError`, reproducing CI run 45021884353.
- All listed mutants are killed in the container. One narrower breaker mutant survives: it keeps the re-read but skips taking `$lock.break`, and no test forces that race. The race needs a stale breaker, a rare setup already recorded as an accepted limit.

## Verifier results moved from the check file

The run decision that verifiers do not commit results into `checks/<phase>.md` moved these records here unchanged, apart from their heading level.

### Mutations at `b7b211d`

Each mutation was applied to `launch.sh`, the unit suite was run, and the file was restored with `git checkout`. The unmutated suite ran 35 tests, all passing.

| Mutation | Failing tests |
| --- | --- |
| `tmux select-layout -t "$window" tiled` after the split | `test_largest_session_pane_is_split`, `test_panes_other_than_the_split_one_keep_their_size` |
| Liveness never matches (`live_pane=""`) | `test_second_launch_reports_alive_and_changes_nothing`, `test_a_resumed_claude_in_the_feature_worktree_is_the_orchestrator_not_the_spec_writer`, `test_a_claude_named_for_the_session_is_alive_outside_its_worktree`, `test_live_session_is_refused`, `test_resumed_nameless_session_is_refused` |
| No nameless-in-worktree rule (`resumed=0` always) | `test_a_resumed_claude_in_the_feature_worktree_is_the_orchestrator_not_the_spec_writer`, `test_resumed_nameless_session_is_refused` |
| No dirty-worktree guard in `--remove` | `test_dirty_worktree_is_refused` |
| No `--resume`, so every start is `--session-id` | `test_restart_resumes_its_own_conversation_unless_fresh`, `test_two_sessions_in_the_feature_worktree_keep_their_own_conversations` |
| No merged-branch guard in `--remove` | `test_unmerged_branch_is_refused` |
| A split failure exits `1` instead of `4` | `test_full_window_exits_4_with_the_tmux_error` |
| `--close` also matches a nameless `claude` | `test_a_resumed_nameless_claude_is_not_closed` |
| Phase worktree added without `--headless` | `test_phase_session_gets_a_pane_in_the_window_and_its_prompt` and three others |

### Live session at `b7b211d`

Claude Code 2.1.330, workmux 0.1.283 and tmux 3.8 on macOS, 21 November 2026. A scratch repository outside this one: a bare `origin` with `main`, a clone with `refs/remotes/origin/HEAD` set to `origin/main`, and a local branch `probe` holding `.foundry/feature-roadmaps/2026-11-21_00-00-00-probe/README.md`. A private server from `env -u TMUX -u TMUX_PANE TMUX_TMPDIR=$(mktemp -d) tmux -f /dev/null new-session -d -x 200 -y 50`, whose `#{socket_path}` was under that `TMUX_TMPDIR`. The real `workmux` and `claude` were on `PATH`.

First launch, from the scratch clone:

```text
$ env -u TMUX -u TMUX_PANE launch.sh --feature probe --role phase --phase live --window @0
✓ Successfully provisioned headless worktree for 'probe-phase-live'
started probe-phase-live pane=%1 worktree=<scratch>/repo__worktrees/probe-phase-live
```

The pane showed Claude Code's folder-trust dialog for the new worktree. It was accepted in the private pane. The pane then showed, with the scratch path shortened:

```text
 ▐▛███▛█   Claude Code v2.1.330
 ▝▝   ▝▝   /…/repo__worktrees/probe-phase-live
⏺ Unknown command: /sam-mode
⏺ Args from unknown skill: phase feature=probe phase=live update=-
  roadmap=.foundry/feature-roadmaps/2026-11-21_00-00-00-probe
  plan=.foundry/plans/2026-11-21_00-00-00-probe/README.md orchestrator=probe-orchestrator
──────────────────────────────────── probe-phase-live ─
❯
```

The first prompt's first words are `/sam-mode phase`: Claude Code read `/sam-mode` as the command and `phase feature=probe ...` as its arguments. `sam-mode` is not deployed in a scratch repository, so Claude Code reports it as unknown, and the session is not shown loading the skill. The session name `probe-phase-live` is on the input box.

Second launch, same command:

```text
alive probe-phase-live pane=%1
```

Exit `0`. Panes `%0 100x50` and `%1 99x50`, and window `@0`, were the same before and after.

On `/exit`, Claude Code printed `claude --resume 7d3af64e-1a98-4978-9637-1f3c2d183b5b`, the id the launcher had written to `s-stack-sessions/probe-phase-live` in the worktree's git directory. The private server was then killed and the worktree removed with `workmux remove probe-phase-live --keep-branch --force` in the scratch clone.

### Rerun at `2ecc9f0`, after the merge of `s-stack-package`

The merge brought `handbooks/planner.md` and `handbooks/spec-writer.md`. The unit suite ran 35 tests, all passing.

| Mutation | Failing tests |
| --- | --- |
| `tmux select-layout -t "$window" tiled` after the split | `test_largest_session_pane_is_split`, `test_panes_other_than_the_split_one_keep_their_size` |
| Liveness never matches (`live_pane=""`) | `test_second_launch_reports_alive_and_changes_nothing`, `test_a_resumed_claude_in_the_feature_worktree_is_the_orchestrator_not_the_spec_writer`, `test_a_claude_named_for_the_session_is_alive_outside_its_worktree`, `test_live_session_is_refused`, `test_resumed_nameless_session_is_refused` |
| No `--resume`, so every start is `--session-id` | `test_restart_resumes_its_own_conversation_unless_fresh`, `test_two_sessions_in_the_feature_worktree_keep_their_own_conversations` |
| No dirty-worktree guard in `--remove` | `test_dirty_worktree_is_refused` |

Every launcher command in the handbooks ran against the stubs on a private server and was accepted. `SKILL.md`'s `launch.sh --feature hb --role spec`, run from the repository root, printed `started hb-spec`. `spec-writer.md`'s `launch.sh --print-window`, run from the feature worktree with `TMUX_PANE` set to the spec writer's pane, printed `window=@1`. Its `launch.sh --feature hb --role orchestrator --window @1` printed `started hb-orchestrator` while the spec writer was still alive in the same worktree. A second run printed `alive hb-orchestrator`.

The live check ran again with the same tools and scratch layout as above. The first launch printed `started probe-phase-live pane=%1`. After the trust dialog was accepted, the pane showed `Unknown command: /sam-mode` and `Args from unknown skill: phase feature=probe phase=live update=- ...`, as above. The second launch printed `alive probe-phase-live pane=%1`, and panes and windows were unchanged. The pane's `claude` ran `claude --name probe-phase-live --session-id 11809bd4-aa1b-450b-9f2e-aeef4c27bdc6`, the id in `s-stack-sessions/probe-phase-live`.

Restart. `/exit` in the pane printed `claude --resume 11809bd4-aa1b-450b-9f2e-aeef4c27bdc6` and left the pane at a shell. The same launch command then printed `started probe-phase-live pane=%2`, and the new pane ran `claude --name probe-phase-live --resume 11809bd4-aa1b-450b-9f2e-aeef4c27bdc6`. That pane showed the earlier `Unknown command: /sam-mode` exchange above the new one, with `probe-phase-live` on the input box. The marker file was unchanged. The worktree was removed with `workmux remove probe-phase-live --keep-branch --force`, and the private server was killed.

### Rerun at `8839699`, after the review fix round and the merge of `s-stack-package`

The merge brought `handbooks/phase-session.md`, `handbooks/verifier.md` and `handbooks/reviewer.md`. The unit suite ran 47 tests, all passing, both as written in `## Rerun` and with `LC_ALL=C` and no `LANG` or `LC_CTYPE`.

Each defect the review at `2726205` found was reproduced against the launcher with the stubs in `packages/s-stack/tests/stubs` on a private server, and none recurred:

| Defect | Reproduction | Result |
| --- | --- | --- |
| C locale hid live sessions | Launcher run with `LC_ALL=C` and no `LANG` or `LC_CTYPE`: start a phase session, launch it again, `--remove`, `--close` twice. Also a nameless `claude --continue` in the worktree, then `--remove` and a start | `alive`, panes unchanged; `--remove` exit `5` naming the live pane; `closed`, then `absent`; nameless case `refused` and `alive` |
| Names collide across features | `--feature` `a-phase`, `a-phase-x`, `trip-planner`, `x-orchestrator`, `x-spec`, `x-spec-3` | Each exit `2` with usage; `ok-feature` accepted |
| Concurrent launches start two copies | Two simultaneous launches of an existing phase worktree, with the stub `claude` delayed 2 s, three rounds | One `started` and one `alive` each round, one `claude` process |
| A zoomed window is unzoomed | Window zoomed on `%0` beside a 30-column pane, then a phase launch | Still zoomed, `%0` still 200x50, the 30-column pane unchanged; an unzoomed window stayed unzoomed |
| Stale `TMUX_PANE` | `--print-window` with `TMUX_PANE=%999` | `launch.sh: no window for pane %999`, exit `1` |
| No tmux server | `--close` and `--remove` after `kill-server` | `absent`, exit `0`; `removed`, exit `0`, branch kept |
| `--remove` loses work | Detached HEAD with a commit on no branch; a `claude --name someone-else` in the worktree; one in a subdirectory of it | Each exit `5` with a `refused` reason; the clean case then removed the worktree and kept the branch |

| Mutation | Failing tests |
| --- | --- |
| `tmux select-layout -t "$window" tiled` after the split | `test_a_zoomed_window_stays_zoomed`, `test_largest_session_pane_is_split`, `test_panes_other_than_the_split_one_keep_their_size` |
| Liveness never matches (`live_pane=""`) | `test_a_claude_named_for_the_session_is_alive_outside_its_worktree`, `test_a_live_session_is_alive`, `test_a_resumed_claude_in_the_feature_worktree_is_the_orchestrator_not_the_spec_writer`, `test_concurrent_launches_of_an_existing_worktree_start_one_copy`, `test_second_launch_reports_alive_and_changes_nothing` |
| No session lock | `test_concurrent_launches_of_an_existing_worktree_start_one_copy`, in five of five runs; it passed five of five unmutated |
| No `--resume`, so every start is `--session-id` | `test_restart_resumes_its_own_conversation_unless_fresh`, `test_two_sessions_in_the_feature_worktree_keep_their_own_conversations` |
| No `-Z` for a zoomed window | `test_a_zoomed_window_stays_zoomed` |
| No detached-HEAD guard in `--remove` | `test_commits_on_a_detached_head_are_refused` |

Every launcher command in `SKILL.md` and the handbooks ran against the stubs and was accepted. `SKILL.md`'s `launch.sh --feature hb --role spec` printed `started hb-spec`. `spec-writer.md`'s `launch.sh --print-window`, from the feature worktree with `TMUX_PANE` set to the spec writer's pane, printed `window=@1`, and its `launch.sh --feature hb --role orchestrator --window @1` printed `started hb-orchestrator`, then `alive hb-orchestrator`. The three new handbooks call no launcher command.

The live check ran again with Claude Code 2.1.330, workmux 0.1.283 and tmux 3.8, in the scratch layout above. The first launch printed `started probe-phase-live pane=%1` and took 0.75 s, including the headless `workmux add` and the wait until `ps` showed the new `claude`. After the trust dialog was accepted, the pane showed `Unknown command: /sam-mode` and `Args from unknown skill: phase feature=probe phase=live update=- ...`. The second launch printed `alive probe-phase-live pane=%1`, with panes `%0 100x50` and `%1 99x50` unchanged. `/exit` printed `claude --resume 1bdcc2c1-1ae8-4bca-9d84-7276e597311b`, the id in `s-stack-sessions/probe-phase-live`. The relaunch took 0.49 s, printed `started probe-phase-live pane=%2`, ran `claude --name probe-phase-live --resume 1bdcc2c1-1ae8-4bca-9d84-7276e597311b`, and showed the earlier `Unknown command: /sam-mode` exchange above the new one. The worktree was removed with `workmux remove probe-phase-live --keep-branch --force`, and the private server was killed.
