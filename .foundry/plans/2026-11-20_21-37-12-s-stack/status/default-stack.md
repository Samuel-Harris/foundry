---
phase: "default-stack"
state: "Implement"
changed_at: "2026-11-22T18:30:39Z"
session: "s-stack-phase-default-stack"
branch: "s-stack-phase-default-stack"
code_head: "9095235fd831608032a251232927ca6f85496768"
waits_for: "The answer to default-stack-r2, on fixing scripts/relativise_lockfiles.py"
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
pull_requests:
  - id: "default-stack-r2"
    question: "Review found that default-stack's committed lockfile reproduces only at the author's checkout path, so CI's pre-commit job and Tier 1 fail elsewhere; may this phase fix it in scripts/relativise_lockfiles.py, which it does not own?"
    options: ["A. Yes: the relativiser also maps each _local/<sha256(absolute anchor)[:12]>/ slot to the hash of the relative anchor in the deployed files and recomputes those files' content hashes, with a unit test, in the same pull request. Prototyped: byte-identical lockfiles at two paths.", "B. Yes, but as its own pull request under this phase's, stacked, so the script change is reviewed alone.", "C. No: hold default-stack until APM stops hashing the absolute path, and close the phase without the s-stack edge."]
    recommendation: "A"
    door: "two-way"
    waiting_work: "The fix, the doc corrections that depend on it, and both gates. Nothing else is left."
    since: "2026-11-22T18:30:39Z"
pushed: null
requests:
  - id: "default-stack-r2"
    question: "Review found that default-stack's committed lockfile reproduces only at the author's checkout path, so CI's pre-commit job and Tier 1 fail elsewhere; may this phase fix it in scripts/relativise_lockfiles.py, which it does not own?"
    options: ["A. Yes: the relativiser also maps each _local/<sha256(absolute anchor)[:12]>/ slot to the hash of the relative anchor in the deployed files and recomputes those files' content hashes, with a unit test, in the same pull request. Prototyped: byte-identical lockfiles at two paths.", "B. Yes, but as its own pull request under this phase's, stacked, so the script change is reviewed alone.", "C. No: hold default-stack until APM stops hashing the absolute path, and close the phase without the s-stack edge."]
    recommendation: "A"
    door: "two-way"
    waiting_work: "The fix, the doc corrections that depend on it, and both gates. Nothing else is left."
    since: "2026-11-22T18:30:39Z"
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
---

# Phase `default-stack` status
