---
phase: "spec-planner-handbooks"
state: "Implement"
changed_at: "2026-11-21T15:39:10Z"
session: "s-stack-phase-spec-planner-handbooks"
branch: "s-stack-phase-spec-planner-handbooks"
code_head: "50e26eebaa31524a81e0cc00d99edf4bdad0e2dc"
waits_for: null
verdicts: []
pull_requests: []
requests: []
decisions:
  - id: "spec-planner-handbooks-d1"
    decision: "planner.md does not point to this run's feature plan as a worked example, because that file lives under .foundry/ on Foundry's orchestrator branch and never reaches a consuming repository. The feature plan allows the pointer but does not require it."
    door: "two-way"
    at: "2026-11-21T15:39:10Z"
  - id: "spec-planner-handbooks-d2"
    decision: "Answer to launcher-r1, option A, from the orchestrator. spec-writer.md gets its own window from launch.sh --print-window, run from the main session, before it passes --window to start the orchestrator, and names no tmux command."
    door: "two-way"
    at: "2026-11-21T15:39:10Z"
---

# Phase `spec-planner-handbooks` status

The session started on 21 November 2026 on `s-stack-package` at `dcdda28`. The phase plan is committed at `phases/spec-planner-handbooks.md`, and the session is writing the two handbooks.
