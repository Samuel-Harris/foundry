---
phase: "launcher"
state: "Verify"
changed_at: "2026-11-21T16:15:48Z"
session: "s-stack-phase-launcher"
branch: "s-stack-phase-launcher"
code_head: "f657820ffa0fe1a25c7672d2776b419f86f6a4fd"
waits_for: null
verdicts: []
pull_requests: []
requests: []
decisions:
  - id: "launcher-d1"
    decision: "Answer to launcher-r1, option A, from the orchestrator: launch.sh --print-window prints window=<window id> for $TMUX_PANE, exit 3 without tmux and exit 1 outside tmux."
    door: "two-way"
    at: "2026-11-21T15:43:28Z"
  - id: "launcher-d2"
    decision: "From orchestrator-handbook-r2: launch.sh gains --close (strict name match only, absent when no pane matches) and --remove (refuses a dirty worktree, an unmerged branch, a live session or a missing worktree with exit 5, keeps the branch)."
    door: "two-way"
    at: "2026-11-21T15:43:28Z"
  - id: "launcher-d3"
    decision: "At the orchestrator's instruction, the launcher picks each session's conversation id, stores it in the worktree's git directory, starts claude with --session-id and resumes with --resume <id>, never --continue, so two sessions in one worktree never swap conversations. Measured: resume by id opens no picker and keeps the id and name."
    door: "two-way"
    at: "2026-11-21T15:43:28Z"
  - id: "launcher-d4"
    decision: "A claude process with no --name in a pane whose directory is the session's worktree counts as that session for start and --remove, because claude --continue restores the name but drops --name from its arguments (measured)."
    door: "two-way"
    at: "2026-11-21T15:43:28Z"
  - id: "launcher-d5"
    decision: "A resumed session receives the first prompt again, so it reloads sam-mode and its handbook and rereads its files."
    door: "two-way"
    at: "2026-11-21T15:43:28Z"
  - id: "launcher-d6"
    decision: "A nameless claude in the shared feature worktree counts as the orchestrator only, never as the first spec writer, because workmux resurrect restores only the orchestrator and the spec writer has ended by then. From the quick-review pass."
    door: "two-way"
    at: "2026-11-21T16:15:48Z"
  - id: "launcher-d7"
    decision: "Only a leading --name argument identifies a session, so prompt text containing --name never matches, and the pane command runs through /bin/sh directly so it does not depend on tmux's default shell. From the quick-review pass."
    door: "two-way"
    at: "2026-11-21T16:15:48Z"
---

# Phase launcher status

Implementation and its quick-review fix round are committed. The phase branch merged `s-stack-package` at 0b0938f before Verify. The suite has 35 tests and passes on macOS (tmux 3.8) and, per the fix-round delegate, in an Ubuntu 24.04 container (tmux 3.4).
