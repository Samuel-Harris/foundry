---
phase: "launcher"
state: "Plan"
changed_at: "2026-11-21T15:36:29Z"
session: "s-stack-phase-launcher"
branch: "s-stack-phase-launcher"
code_head: "50e26eebaa31524a81e0cc00d99edf4bdad0e2dc"
waits_for: null
verdicts: []
pull_requests:
  - id: "launcher-r1"
    question: "C4 gives no way for a handbook to learn its own tmux window id without naming a tmux command. Should launch.sh gain a mode that prints the caller's window id?"
    options: ["A. Add launch.sh --print-window, which prints window=<window id> for the pane in $TMUX_PANE and exits 0, exit 3 when tmux is missing and exit 1 when the caller is not in tmux. It takes no other flag.", "B. Default --window to the caller's window when $TMUX_PANE is set.", "C. Leave C4 unchanged and let handbooks name tmux display-message."]
    recommendation: "A"
    door: "two-way"
    waiting_work: "The window wording in spec-writer.md and orchestrator.md, and the launcher's argument parsing and its tests for that mode."
    since: "2026-11-21T15:37:58Z"
requests:
  - id: "launcher-r1"
    question: "C4 gives no way for a handbook to learn its own tmux window id without naming a tmux command. Should launch.sh gain a mode that prints the caller's window id?"
    options: ["A. Add launch.sh --print-window, which prints window=<window id> for the pane in $TMUX_PANE and exits 0, exit 3 when tmux is missing and exit 1 when the caller is not in tmux. It takes no other flag.", "B. Default --window to the caller's window when $TMUX_PANE is set.", "C. Leave C4 unchanged and let handbooks name tmux display-message."]
    recommendation: "A"
    door: "two-way"
    waiting_work: "The window wording in spec-writer.md and orchestrator.md, and the launcher's argument parsing and its tests for that mode."
    since: "2026-11-21T15:37:58Z"
decisions: []
---

# Phase launcher status

The phase session started and is writing the phase plan.
