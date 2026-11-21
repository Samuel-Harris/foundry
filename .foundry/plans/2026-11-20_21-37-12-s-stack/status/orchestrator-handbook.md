---
phase: "orchestrator-handbook"
state: "Implement"
changed_at: "2026-11-21T15:38:33Z"
session: "s-stack-phase-orchestrator-handbook"
branch: "s-stack-phase-orchestrator-handbook"
code_head: "8bf296b43f079f6b8f93ad97626fb290f8a6f5f6"
waits_for: null
verdicts: []
pull_requests: []
requests:
  - id: "orchestrator-handbook-r2"
    question: "The orchestrator must close a phase's pane after merging it and remove worktrees at Done and at the end, but C4 gives the launcher no mode for either and the handbook may name no workmux or tmux command line (workmux close acts on a worktree's own window, not a pane in the feature window), so how should the handbook close panes and remove worktrees?"
    options: ["A. C4 gains two launcher modes, --close (closes the named session's pane, only a pane the launcher created) and --remove (removes the named session's worktree), and the handbook calls them by flag.", "B. The handbook says close the pane and remove the worktree in words only, and the orchestrator works out the command itself.", "C. The developer closes panes and removes worktrees, and the orchestrator lists them under Needs you."]
    recommendation: "A"
    door: "two-way"
    waiting_work: "Two sentences in the handbook (Merging a phase step 7, After a merge into the default branch, Ending the feature) and one cold-read expectation. Everything else proceeds."
    since: "2026-11-21T15:40:35Z"
decisions:
  - id: "orchestrator-handbook-d1"
    decision: "Answer to orchestrator-handbook-r1 from the orchestrator, option A. The handbook states its own supervision rules (read the evidence not the report, check live pull request state, judge a stall by commits and pull request activity and retry by cause, ask the developer only for a real decision) and names no Orchestrate playbook, because Foundry's p-stack has none."
    door: "two-way"
    at: "2026-11-21T15:40:35Z"
---

# Phase `orchestrator-handbook` status

The phase session started on 21 November 2026 on `s-stack-phase-orchestrator-handbook` at `42c54ee`. The phase plan is at `.foundry/plans/2026-11-20_21-37-12-s-stack/phases/orchestrator-handbook.md`.

The phase plan was committed at `86ae7dc`, and the phase moved to Implement.

The handbook was committed at `8bf296b` and the lockfile regenerated at `d021335`. `orchestrator-handbook-r1` is answered (`orchestrator-handbook-d1`). `orchestrator-handbook-r2` is open.
