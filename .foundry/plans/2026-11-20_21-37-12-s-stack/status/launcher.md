---
phase: "launcher"
state: "Implement"
changed_at: "2026-11-21T17:23:01Z"
session: "s-stack-phase-launcher"
branch: "s-stack-phase-launcher"
code_head: "15bb919f5f9e85fca556362ac5bdb2897900b955"
waits_for: null
verdicts:
  - gate: "verify"
    result: "VERIFIED"
    code_head: "c1ec2d3d85a9f5f9535101e63ac9956ebaa32371"
    at: "2026-11-21T16:26:38Z"
    evidence: ".foundry/plans/2026-11-20_21-37-12-s-stack/status/launcher-evidence.md"
  - gate: "verify"
    result: "VERIFIED"
    code_head: "2726205c5a71584501fb366f588125c64af9cfbd"
    at: "2026-11-21T16:36:06Z"
    evidence: ".foundry/plans/2026-11-20_21-37-12-s-stack/status/launcher-evidence.md"
  - gate: "review"
    result: "SIGNIFICANT"
    code_head: "2726205c5a71584501fb366f588125c64af9cfbd"
    at: "2026-11-21T16:49:21Z"
    evidence: ".foundry/plans/2026-11-20_21-37-12-s-stack/status/launcher-evidence.md"
  - gate: "verify"
    result: "VERIFIED"
    code_head: "15bb919f5f9e85fca556362ac5bdb2897900b955"
    at: "2026-11-21T17:23:01Z"
    evidence: ".foundry/plans/2026-11-20_21-37-12-s-stack/status/launcher-evidence.md"
pull_requests:
  - id: "launcher-r2"
    question: "Session and worktree names are joined with hyphens, so two features can collide: the planner of feature a-phase and phase planner of feature a are both a-phase-planner, and the planner of feature query takes the feature worktree of a feature named query-planner. Should the launcher refuse feature names that can collide?"
    options: ["A. The launcher exits 2 for a feature name that contains -phase- or ends with -phase, -planner, -orchestrator, -spec or -spec-<n>, and its usage text says so.", "B. Change the naming scheme in the roadmap so names cannot collide, for example a separator that a kebab-case name cannot contain.", "C. Accept the collision and document it."]
    recommendation: "A"
    door: "two-way"
    waiting_work: "The launcher's feature-name validation and its test. Every other review fix goes ahead."
    since: "2026-11-21T16:43:47Z"
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
  - id: "launcher-d8"
    decision: "Answer to launcher-r2, option A, from the orchestrator: the launcher exits 2 for a feature name that is not kebab-case, contains -phase-, or ends with -phase, -planner, -orchestrator, -spec or -spec-<n>, so derived names never collide."
    door: "two-way"
    at: "2026-11-21T16:44:12Z"
  - id: "launcher-d9"
    decision: "From the developer, relayed by the orchestrator, with the edge cases decided here and accepted: launcher panes carry @s-stack-session tags, the orchestrator holds the first column after the workmux sidebar, update spec writers go in its column, planner and phase sessions go to its right, a resurrected orchestrator found by liveness counts as the launcher's, an orchestrator with no spec pane splits the topmost pane of the leftmost column, and a planner, phase or update spec writer with no orchestrator pane is exit 1."
    door: "two-way"
    at: "2026-11-21T17:23:01Z"
---

# Phase launcher status

Implementation and its quick-review fix round are committed. The phase branch merged `s-stack-package` at 0b0938f before Verify, and again at 2ecc9f0 (bringing spec-planner-handbooks), which is a new code head, so Verify ran again and passed at 2726205. The suite has 35 tests and passes on macOS (tmux 3.8) and, per the fix-round delegate, in an Ubuntu 24.04 container (tmux 3.4).

The review fix round (seven findings, 47 tests, also green under `LC_ALL=C`) is committed, and `s-stack-package` is merged at 8839699 with the phase-handbooks phase. Verify runs again at that head.

The developer's pane placement rule (launcher-d9) moved the phase back to Implement after the third Verify.
