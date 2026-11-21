# Evidence

This file records what the decisions rest on. Each entry has a code that [decisions.md](decisions.md) cites.

Every entry says how it was checked. "Counted" means that the spec writer parsed the transcripts and counted tool calls. "Checked" means that the spec writer found the quoted words in the raw transcript, or read the file or command output directly. "Reported" means that a subagent read the source and the spec writer did not check that item.

## The November run

The run built a large feature in one of the developer's private repositories. Its transcripts are Claude Code JSONL files on the developer's machine, under `~/.claude/projects/`, in the project directories of that feature's worktrees. The orchestrator's session id begins `952d7852`. The other sessions' transcripts are in 25 sibling project directories, one for each worktree. Counts cover each session's own transcript and leave out its subagents' transcripts. Times are as the subagents reported them.

Quotes are word for word, except where square brackets replace a name or a detail from the private repository.

**R1. How the roadmap was made.** Reported. Session `b8210ef0` wrote it on 18 November with `/poteto-mode` and `deep-interview`. The interview took eight rounds and brought the ambiguity score from 100% to 16%. The result was 18 files under `feature-roadmap/`, with one file for each phase and an append-only numbered `decisions.md`. Two short review rounds followed.

**R2. How sessions were launched.** The orchestrator's first attempt was `workmux add <feature>-phase-2 --base <feature>-phase-1 -b -P <brief> --parent-session 0`. It then said: "The worktree setup failed because the project's workmux pane config doesn't start an agent." Checked. It settled on `workmux add <name> --base <ref> --headless --json` followed by `tmux new-window ... claude "$(cat <brief>)"`. Reported. The transcripts hold 7 `workmux add` calls and 25 `tmux new-window` calls. Counted. The first prompt of phase 3 begins "Goal: [the feature] (see feature-roadmap/README.md). Your phase: feature-roadmap/phases/[the phase file]." It does not begin with `/poteto-mode`. Checked. The developer started phases 0 and 1 by hand with `/poteto-mode`. Checked for phase 0.

**R3. Messaging.** The orchestrator made about 470 `SendMessage` calls. Reported, and consistent with 955 matches in a transcript that stores many records twice. All sessions together made 1,293 distinct `SendMessage` calls. Counted. Phase sessions reported in the form "Phase 03 ready to merge at [commit]". Reported.

**R4. A restart changed the address.** The orchestrator wrote: "my address changed from `[feature]-b3` to `[feature]-5b`… Any report sent to the old name in the meantime went nowhere". Checked. Phase 0 wrote: "I'm resending this from b3, which never replied to it." Checked.

**R5. Upkeep.** The developer wrote "Don't forget to regularly update the claude code feature map artefact" at 16:25, and sent similar reminders at 19:40, 21:49 and 08:17. The first quote is checked and the times are reported. At 19:43 the developer wrote: "To prevent you from letting the phase map artefact or feature map fall behind, design a loop prompt for me to give you". Checked. The developer later asked "Is your loop still running?" Checked. The loop was a scheduled task on `7,27,47 * * * *`. Checked. It was created at 19:44 and created again at 22:32 and 23:38 to add steps. Reported. The orchestrator made 42 `Artifact` publish calls. Counted.

**R6. Branches and pull requests.** At 13:02 the developer wrote: "when a phase completes, we don't need a PR for that phase. We can just merge that branch directly into this one." Checked. The transcripts hold 31 `git merge --no-ff` calls. They hold no `gh pr create`, `gh pr edit`, `gh pr ready` or `gh stack` call in any Bash command. Counted. One pull request went from the integration branch to the repository's default branch. Reported.

**R7. One session did every stage, and review was optional.** Reported. Each phase session implemented, ran the verification skill and handed its branch to the orchestrator. No separate verifier, reviewer or PR creator session existed. A review subagent ran in phases 3, 4 and 9h. The briefs did not require one.

**R8. Shared files.** The orchestrator told one phase: "your decision numbers are 18 to 21". Checked. `decisions.md` reached about 270 entries. Reported. Phase 0 kept one verification script in step after every merge. It sent 36 messages, reported, and described "verify.py, which is now 1,168 lines". Checked. Phase 11c made 36 `SendMessage` calls, counted from 72 matches in a transcript that stores records twice. Most of them agreed edit order and turns on a shared browser stack, reported, for example "Hand the browser-check turn to 11f". Checked.

**R9. Permission prompts and blocked writes.** The orchestrator asked the developer: "please approve its request in tmux window `@28`". Checked. Phase 7 told the orchestrator: "the user's approval of [a long-running job] is still pending in my window." Checked. A rejected command had partly run: "its first steps ran before your rejection took effect". Checked. Phase 11c wrote: "my edits to live worktrees were blocked". Checked.

**R10. Merging through a checker.** From about 19:30 the orchestrator gave merges to fresh subagents. Reported. One of them "caught a variable name that would have crashed [a] command". Checked.

**R11. A relayed skill instruction was declined.** The developer wrote: "In case it wasn't clear, every agent should be using the /poteto-mode playbook". Checked. Phase sessions declined the relayed instruction because it "came from one of my helper subagents" and because the skill "isn't in their sessions' skill lists". Checked. A first prompt that begins with `/poteto-mode` does load the skill. The transcripts of phases 9b, 11c and 11e record the command and then the skill's text. Checked.

**R12. Machine limits.** The developer wrote: "We are running out of memory". Checked. The subagent's report lists it among compute problems, next to stopped Docker containers and a duplicated compute job. It does not tie the memory pressure to the number of sessions. Reported.

**R13. The orchestrator's context.** The developer wrote: "Keep your context clean as you are the orchestrator agent". Checked. The context stood at "800.3k / 1m (80%)". Checked. The session was compacted at 19:42, and 14 of the 25 other sessions were compacted at least once. Reported.

**R14. What the developer liked.** The transcripts hold no explicit praise. Reported. The statement that the developer liked the pattern comes from the brief for this roadmap.

## Claude Code documentation

A subagent read each page. A second fetch confirmed the quotes in C1, C2 and C3 word for word.

**C1. Agent teams.** <https://code.claude.com/docs/en/agent-teams>

- "Agent teams are experimental and disabled by default."
- "`/resume` and `/rewind` do not restore in-process teammates."
- "No nested teams: teammates cannot spawn their own teammates."
- "One team per session: a session has exactly one team, scoped to that session."
- "Teammate permission prompts appear in the lead session, so approve them there yourself."
- "Two teammates editing the same file leads to overwrites. Break the work so each teammate owns a different set of files."
- The page does not say that a teammate gets its own worktree.

**C2. Cross-session messaging.** <https://code.claude.com/docs/en/cross-session-messaging>

- "A session answers to the name you set with the /rename command or the --name flag."
- "When the receiving session is idle, Claude Code starts a new turn with the message."
- "It can't approve anything: a message from another session never counts as your consent, so it can't answer a pending permission prompt on your behalf."
- "Claude Code holds at most 100 messages, and past that drops the oldest."
- Messages on one machine travel "Over a per-session socket on macOS and Linux, … never through Anthropic servers."

**C3. Scheduled tasks.** <https://code.claude.com/docs/en/scheduled-tasks>

- "Tasks only fire while Claude Code is running and idle."
- "Recurring tasks automatically expire 7 days after creation."

**C4. Subagents that start subagents.** <https://code.claude.com/docs/en/sub-agents> Not confirmed. The fetch returned a summary for this part of the page. The summary says: "By default, a subagent can spawn subagents of its own, up to three layers below the main conversation."

**C5. Reported and not checked again.**

- Cross-session messaging needs Claude Code 2.1.224 or later.
- A receiver in a bypass permission mode holds each message for approval unless the sender also bypasses. The `crossSessionInbound` setting overrides that.
- The Monitor tool watches for at most 30 minutes.
- `claude --bg` runs a session with no terminal.

## Experiments in this session

The spec writer ran these on 20 November 2026 in the worktree `foundry__worktrees/s-stack-package`, with workmux 0.1.283, and removed every probe afterwards.

**X1. workmux tracks a session in a pane of the current window.** `workmux add sstack-pane-probe --headless --json --base HEAD` created a worktree. `tmux split-window -d -h -t "$TMUX_PANE" -c <worktree> "claude ..."` started a session in a new pane of the same window. `workmux status sstack-pane-probe --json` then listed the session with `"status": "done"`, its pane, and `"window_name": " s-stack-package"`.

**X2. workmux reaches that session by its handle.** `workmux send --wait --timeout 80 sstack-pane-probe "..."` printed `sstack-pane-probe: done (1s)` and exited 0. The spec writer did not confirm the reply text in the pane.

**X3. `--name` keeps the address across a restart.** A session started with `claude --name sstack-name-probe` appeared in `ListAgents` as `sstack-name-probe [bb95fa]`. After the pane was killed and the same command run again, it appeared as `sstack-name-probe [5ec791]`. The name was identical and only the short identifier changed.

**X4. A new directory can stop a launch.** A session started in a scratch directory stopped at Claude Code's folder trust prompt. The session in X1, in a new worktree of this repository, did not.

**X5. A write through a link to another directory stops at a prompt.** In a probe worktree, `.foundry` was a link to a directory outside the worktree. A session in auto mode was told to write `.foundry/plans/probe/status/a.md`. It stopped with "This will modify … (outside working directory) via a symlink" and "Do you want to create a.md?" The only choices were Yes and No. `workmux status` showed `waiting`, and no file was written.

**X6. `--add-dir` removes that prompt.** The same session, started with `--add-dir <the directory>`, wrote the file with no prompt, and `workmux status` showed `done`. Its pane also showed "Loaded …/.claude/rules/plan-handoff-standard.md", so the rule scoped to `.foundry/plans/**/*.md` matched a file reached through the link.

**X7. `--add-dir` takes a following prompt as a directory.** With the prompt straight after `--add-dir <directory>`, Claude Code printed that the prompt "was read as a value of --add-dir, not as a prompt · put a prompt before --add-dir or after --". With `--` before the prompt, it worked.

**X8. An ignore pattern that ends in a slash does not match a link.** In a scratch repository with a link named `.foundry`, the pattern `.foundry/` left the link untracked in `git status`. The pattern `.foundry` ignored it.

**X9. Removing a worktree deletes its ignored files without a warning.** In a scratch repository, `git worktree remove` exited 0 for a worktree that held an ignored `.foundry/roadmap.md`, and the file was gone. For a worktree with an untracked file that was not ignored, the same command refused with "contains modified or untracked files, use --force to delete it".

The next three tests ran on 21 November 2026 in a separate tmux server, so the developer's own sessions were untouched. Killing that server stood in for a tmux crash.

**X10. `workmux resurrect` restores only a session in the workmux window of its own worktree.** Three sessions ran in the test server. `workmux add` started the first in its own window. The second was started with `claude --name` in a plain tmux window. The third was started with `claude --name` as a pane of the first session's window, in a headless worktree of its own, which is how the launcher starts a phase session. The server was killed and started again. `workmux resurrect --dry-run` listed the first worktree as "restoring" and counted the other two under "unmatched state file(s) ignored".

**X11. What `workmux resurrect` restores.** In the same server, `workmux resurrect` printed "Restored 2 worktree(s)". Each worktree came back as its own window with the project's pane layout. The process list showed `claude --continue`, and the restored pane showed the session's earlier exchange. A second run tested the orchestrator's case. A session was started with `claude --name sstack-orch-named` as a pane in the workmux window of its own worktree, after that window's first agent had ended. After a crash and `workmux resurrect`, the restored pane showed that session's conversation, and `ListAgents` listed `sstack-orch-named`.

**X12. `claude --continue` keeps the conversation and the name.** `claude --name sstack-res-probe3 --continue "<prompt>"`, run in the worktree of an ended session, showed the earlier exchange, answered from it, and appeared in `ListAgents` as `sstack-res-probe3`. `claude --continue` with no `--name`, run in the worktree of a session first started with `--name sstack-res-probe`, appeared as `sstack-res-probe`. Two sessions that never had a name came back with a new random suffix each time.

## Tools

**T1. workmux has no mode for a pane in the current window.** Checked. `workmux add --help` offers `--mode` with the values `window` and `session`. `--headless` creates the worktree "without a multiplexer target".

**T2. workmux tracks any Claude Code session through hooks.** Checked. `~/.claude/settings.json` runs `workmux register-agent` on session start and `workmux set-window-status` with `working`, `waiting` or `done` on later events.

**T3. Notes in the workmux skill.** Checked in `~/.claude/skills/workmux/SKILL.md`. "Background and agent tool invocations can omit `$TMUX_PANE`". "`send` refuses an agent waiting on a dialog", with the error `agent_waiting` and exit code 3.

**T4. `gh stack`.** Checked. `gh stack link --help` says that arguments "that belong to a different stack are rejected". The instructions for `gh stack` in one of the developer's private repositories state two rules. A stack is strictly linear, so a pull request has one parent and at most one child, and parallel work goes in separate stacks. A stack is planned before any file is written, and a finished change is not split into a stack afterwards. `gh stack submit --auto` opens draft pull requests.

**T5. `claude --add-dir`.** Checked. `claude --help` describes it as "More directories Claude can access".

**T6. How `workmux resurrect` works.** Checked in `workmux docs`. It reads workmux's agent state files, "Matches each state file's working directory to a git worktree in the current repo", "Skips worktrees that are already open or no longer exist", and "Opens each matched worktree with `--continue` to resume the agent". That it restarts an agent only where the project's pane layout starts one is an inference from R2, not a test.

## Foundry

All entries were checked on `origin/main` at commit `9ce8870` and confirmed again at `72f6d88`. The roadmap was written on the branch `s-stack-package` while that branch was four commits behind `origin/main`. Those commits renamed the `pstack` package to `p-stack` and added it to `default-stack`. The branch was fast-forwarded before the roadmap was committed.

**F1. Packaging rules.** `AGENTS.md` states the audit rule for a package reached twice, the rule for the root manifest and the version bump rule.

**F2. Manifests today.** The root `apm.yml` lists `p-stack` and `planning`. `packages/default-stack/apm.yml` depends on `coding-style`, `execution`, `git-diff`, `p-stack`, `planning`, `pr`, `repo-maintenance`, `review` and `skill-creation`. `planning` depends on `deep-interview` and `review`. `p-stack`, `pr`, `review`, `deep-interview` and `coding-style` have no dependencies.

**F3. The validator resolves relative links.** `tests/structural/validate_primitives.py` checks that "every relative markdown link inside a primitive resolves on disk". Other packages name a skill in words, for example "the `deep-interview` skill".

**F4. `poteto-mode` cannot be invoked by a model.** Its frontmatter in `packages/p-stack/.apm/skills/poteto-mode/SKILL.md` sets `disable-model-invocation: true`.

**F5. The plan handoff standard covers `.foundry/plans/`.** `packages/planning/.apm/instructions/plan-handoff-standard.instructions.md` sets `applyTo: ".foundry/plans/**/*.md"`.

**F6. A skill can ship scripts with tests.** `packages/foundry-maintenance/.apm/skills/guidance-retro/scripts/` holds Python scripts. `AGENTS.md` describes a `foundry-maintenance-tests` CI job for `packages/foundry-maintenance/tests`.

**F7. Skills that s-stack names.** `quick-review` is in `packages/review`. `summarise-pr` is in `packages/pr`. `interrogate`, `automate-me` and the four verification skills are in `packages/p-stack`. `interrogate` starts its own reviewer subagents and gives each one its own worktree. `quick-review` starts two review subagents.

**F8. The package count.** `AGENTS.md` and `docs/COMPATIBILITY.md` say that the repository has nineteen packages.

**F9. `.foundry/` is already where agents put working files.** `deep-interview` writes `.foundry/interviews/`, `handoff` writes `.foundry/handoffs/`, `masterplan` writes `.foundry/masterplans/`, and `aws-architecture-diagram` writes `.foundry/architecture-diagrams/`. The plan handoff standard matches `.foundry/plans/`. The repository's `.gitignore` has no entry for `.foundry`.

**F10. No repository of the developer's ignores `.foundry/`.** Checked with `git check-ignore` in the main checkouts of Foundry and of the developer's two private repositories. None of them tracks a file under `.foundry/` either.

**F11. Foundry is a public repository.** Checked. `gh repo view --json visibility` returned `PUBLIC` for `Samuel-Harris/foundry`. The first versions of this file named a private repository, its feature and two private pages. Those references were removed before the roadmap was first pushed.

## The status board

**B1. The prototype.** Reported. A subagent read the status page that the November orchestrator kept. The developer's first-draft rubric links to it. The page has no section for what needs the developer. It names one pull request. It stores each phase's state twice, as a coloured node in a graph and as prose in a table, and the two disagree for phases 11b to 11g, 09b and 09e. Its only sign of freshness is one hand-typed time. Its graph is 2,556 pixels wide and scrolls sideways. Demo scripts and compute notes sit among the status.

**B2. What a page can do on the developer's account.** Reported, from the `artifact-capabilities` skill. A page can have a database that survives a new publish, and a session updates rows without publishing the page again. One document holds at most 256 KiB, and one page's database at most 25,000 documents. One batch applies up to 50 writes under one approval. The skill advises against one document for each item of a growing log. The account has a page type named Data for dashboards and no type named Dashboard.

**B3. The November architecture page.** Reported. A subagent read the architecture page that the November orchestrator kept. It explains the system in numbered figures, among them a system map, the package boundaries, the data model and the main flows. It carries a tally of features by state and its own status chips. Its words for progress differ from the status page's, and the two pages were updated at different times. The developer's reminders in R5 name this page.
