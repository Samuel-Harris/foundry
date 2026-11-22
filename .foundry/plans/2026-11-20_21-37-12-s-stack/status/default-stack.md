---
phase: "default-stack"
state: "PR"
changed_at: "2026-11-22T19:14:58Z"
session: "s-stack-phase-default-stack"
branch: "s-stack-phase-default-stack"
code_head: "acaba0e6fcd36b38e2c6061c6fc7ede046844cae"
waits_for: null
verdicts:
  - gate: "verify"
    result: "VERIFIED"
    code_head: "9095235fd831608032a251232927ca6f85496768"
    at: "2026-11-22T18:22:02Z"
    evidence: ".foundry/plans/2026-11-20_21-37-12-s-stack/status/default-stack-evidence.md"
  - gate: "review"
    result: "SIGNIFICANT"
    code_head: "9095235fd831608032a251232927ca6f85496768"
    at: "2026-11-22T18:30:39Z"
    evidence: ".foundry/plans/2026-11-20_21-37-12-s-stack/status/default-stack-evidence.md"
  - gate: "verify"
    result: "VERIFIED"
    code_head: "acaba0e6fcd36b38e2c6061c6fc7ede046844cae"
    at: "2026-11-22T19:02:05Z"
    evidence: ".foundry/plans/2026-11-20_21-37-12-s-stack/status/default-stack-evidence.md"
  - gate: "review"
    result: "CLEAR"
    code_head: "acaba0e6fcd36b38e2c6061c6fc7ede046844cae"
    at: "2026-11-22T19:14:58Z"
    evidence: ".foundry/plans/2026-11-20_21-37-12-s-stack/status/default-stack-evidence.md"
pull_requests: []
pushed: null
requests: []
decisions:
  - id: "default-stack-d1"
    decision: "The phase branch runs versioning.py bump against origin/main, because the developer's brief asks for it and no parallel phase can pick the same version."
    door: "two-way"
    at: "2026-11-22T18:02:06Z"
  - id: "default-stack-d2"
    decision: "DEFAULT_STACK_DEPLOYED in run-tier1.sh also gains p-stack, which has been a direct dependency of default-stack since #70 without an inventory check."
    door: "two-way"
    at: "2026-11-22T18:02:06Z"
  - id: "default-stack-d3"
    decision: "Answer to default-stack-r1, option A: tests/acceptance.md and packages/default-stack/README.md join the phase's owned paths for this round and are fixed in the one pull request."
    door: "two-way"
    at: "2026-11-22T18:05:50Z"
  - id: "default-stack-d4"
    decision: "Answer to default-stack-r2, option B: scripts/relativise_lockfiles.py and a new unit test join the owned paths. The fix ships in its own draft pull request against main, and the default-stack pull request stacks on it. Rerunning the relativiser must change no other committed lockfile. Before prs-open, apm audit --ci and Tier 1's stability check must pass on lockfiles produced at two checkout paths."
    door: "two-way"
    at: "2026-11-22T18:31:49Z"
---

# Phase `default-stack` status
