---
phase: "spec-planner-handbooks"
state: "Verify"
changed_at: "2026-11-21T15:44:39Z"
session: "s-stack-phase-spec-planner-handbooks"
branch: "s-stack-phase-spec-planner-handbooks"
code_head: "f0542648c3b4372b8b8b4d05cb306c58ac8303a0"
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

The phase plan is `phases/spec-planner-handbooks.md`. Both handbooks are built, quick-review findings are fixed at `f054264`, and `s-stack-package` is merged at `3bb77e4`. The Verify gate is running.
