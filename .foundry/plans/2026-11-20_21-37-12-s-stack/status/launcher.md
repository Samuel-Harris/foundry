---
phase: "launcher"
state: "Implement"
changed_at: "2026-11-21T15:43:28Z"
session: "s-stack-phase-launcher"
branch: "s-stack-phase-launcher"
code_head: "50e26eebaa31524a81e0cc00d99edf4bdad0e2dc"
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
---

# Phase launcher status

The phase plan is committed at `phases/launcher.md`. Implementation has started.
