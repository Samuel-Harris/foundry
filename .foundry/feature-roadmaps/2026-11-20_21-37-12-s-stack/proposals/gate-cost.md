# Proposal: gate cost

Status: agreed with the developer on 2026-11-22. The orchestrator decides how to route it to phases.

## The worry

The developer: "I'm worried about reviews and verifications getting expensive as in the current design, they seem like they might re-review and re-verify already reviewed and verified code."

## What the current design does

The worry is right for Verify and for the post-merge check. It is wrong for Review.

### Review covers only new work

- `reviewer.md` line 11, on `s-stack-package`: every review after the first covers "what changed since the most recent review's code head, and only the phase's own work". Code from another phase arrives through merges, "and its own gate reviewed it". Only the phase's own conflict resolution is read, with `git show --remerge-diff`.
- `reviewer.md` line 12: the probe of each earlier significant finding runs again. That is cheap.
- Review is costly through its round count, not its scope. On `s-stack-phase-orchestrator-handbook`, the status file records 14 reviews, and none is CLEAR. Each SIGNIFICANT review leads to a fix and another full Verify.

### Verify re-runs everything every round

- `workflow.md` States rule 5 (line 77): "After a fix, verification runs again in full."
- `phase-session.md` line 26 repeats it: any commit that moves the code head, a merge included, needs new verdicts, and "never carry an old verdict forward because the change looks small".
- `verifier.md` line 52: the verifier runs the whole verification skill, including the `## Rerun` section of every phase's check file, then its own `## Evidence` checks.
- The skill (`tests/s-stack/verify-s-stack/SKILL.md`) runs Tier 1, about three minutes, in check 7, and every phase's check file in check 8.
- So every Verify re-runs other phases' checks on code this phase does not own.

Measured on the phase branches:

| Phase | Verify verdicts | Review verdicts | `## Rerun` checks in its own file | Of which cold reads |
| --- | --- | --- | --- | --- |
| `orchestrator-handbook` | 30 (34 rounds in its evidence file) | 14, none CLEAR | 60 | 56 |
| `pr-handbook` | 16 | 5 | 4, mostly scratch-repository scripts | 1 |
| `launcher` | 10 | 6 | 3 | 0 |

Example. `orchestrator-handbook` Verify 34 (its evidence file, "Verify 34") followed a fix to one paragraph, `orchestrator.md` line 148. It ran 65 cold reads, Tier 1, every scratch-repository script and the board's 50 Chrome scenarios. Nine of the cold reads belong to `foundation`, `phase-handbooks` and `spec-planner-handbooks`, which had merged and did not change. Across 34 rounds at about 60 cold reads each, that is roughly 2,000 cold-read subagents for one phase.

The verifier also commits its check file in most rounds (`verifier.md` line 46). That commit moves the code head, so the next review must cover it too.

### The post-merge check re-runs everything every merge

- `workflow.md` Branches step 6 (line 118) and decision D9 (`decisions.md` line 80): after a merge into the orchestrator branch, a fresh subagent runs the whole verification skill.
- `orchestrator.md` line 95, on `s-stack-phase-orchestrator-handbook`, says the same.
- The tracker's "Merged phases" table lists 10 such checks so far. Each takes about 4 to 10 minutes with Opus graders.

### What the run already limits

Run decisions limit how often a gate restarts: the version-only code head, `launcher-r3`, the minor-findings rule, the board check-gap limits and the common-path bar. None limits how much one Verify re-runs.

## Options considered

1. **Scope each gate to the change.** Re-run only what the change can affect. Chosen.
2. **Keep full runs and make each cheaper,** with fewer readers per cold read or cheaper graders. Rejected: the cost grows with check count times rounds, and this cuts only a constant.
3. **Verify less often,** for example once after Review settles. Rejected: the gates exist so that Review sees verified code.

For who decides that a change carries no risk:

1. **The existing verifier and reviewers decide.** Chosen. No new role, handbook or message. The verifier already maps changed files to checks, so waiving is the same step as choosing what to re-run.
2. **A new triage agent before both gates.** Rejected. It saves one short agent per waived round, but adds a role and a step, judges without knowing the checks, and makes one agent decide both gates, which loses their independence.
3. **The phase session decides from a fixed list.** Rejected. The author is the worst judge of its own change's risk.

For the post-merge check:

1. **Keep it full as the backstop.** Rejected by the developer.
2. **Scope it to the merge's diff, plus one full run per feature.** Chosen. The developer trusts agents to judge a change's blast radius.

## The change

### 1. Verify is scoped to the blast radius

- The verifier reads the diff since the last `VERIFIED` code head of the phase, outside `.foundry/`. The first Verify of a phase reads the whole phase diff.
- It works out the blast radius: every behaviour the diff can affect. A check is in the radius when any file it names or reads changed. That is the minimum. A change to a shared helper also takes in every check whose behaviour runs through that helper.
- It re-runs every check in the radius, from any phase's check file, and every new or changed check. It runs no check outside the radius.
- Its report lists the checks it ran and, for each check file, why the rest are outside the radius. A reader can then audit the call.
- This replaces "verification runs again in full" in `workflow.md` and `phase-session.md`.

### 2. Review stays incremental

`reviewer.md` line 11's scope does not change. The baseline for "since the last review" is the last `CLEAR` or `SIGNIFICANT` code head, never a `WAIVED` one (see rule 4).

### 3. A gate agent may waive its gate

The verifier, or the first reviewer, may return a new verdict, `WAIVED`, instead of running its gate. It may do so only when the diff in its scope changes nothing that a user, a program or an agent reading the file would act on differently. It writes the reason, and the phase session records it in the evidence file.

Waivable, for ordinary feature work:

- generated files only, such as lockfiles, regenerated clients, or snapshots a generator rebuilt from unchanged input;
- formatting, import order, or a linter's auto-fix;
- a complete rename of a local variable or private function, with every use in the diff;
- comments, docstrings, log message wording, or a typo in a user-facing string that no test asserts;
- a small, isolated and clear change whose whole effect the agent can state from the diff, and that no existing check or probe exercises. Examples are tightening a type annotation, deleting code the diff shows unreachable, or raising a log level.

Never waivable:

- any change to logic or control flow, however small, such as a condition, a default, an error path or a retry;
- a change to a public interface or contract: an API, a CLI flag, a schema, a migration, a config key, an event or message format;
- a dependency added or bumped by hand, as opposed to a lockfile regenerated from an unchanged manifest;
- anything touching authentication, permissions, secrets, input handling or the commands the code runs;
- a test or check change that alters an expected result;
- a change to instructions an agent follows, such as a prompt, skill or handbook.

"Cannot be verified" has two cases:

- **Nothing can observe the change.** The verifier may waive, with that reason. This extends `verifier.md`'s "None" (line 22) from a whole phase to one change.
- **Something could observe it, but no check can run here.** The verdict stays `INCONCLUSIVE` (`verifier.md` line 64). A risk nobody covered is not low risk.

### 4. A waiver never moves the baseline

The next scoped Verify covers everything since the last `VERIFIED` head, and the next Review everything since the last `CLEAR` or `SIGNIFICANT` head. Every waived change is therefore looked at again as soon as a real round runs.

### 5. How Review waives

The phase session starts one reviewer first. That reviewer reads the scope and either returns `WAIVED` with its reason, or carries on reviewing under `interrogate`. In the second case the phase session then starts the second adversary on the other model family, as today.

### 6. The merge rule accepts `WAIVED`

A phase may move to PR, and the orchestrator may merge it, when the newest `verify` verdict is `VERIFIED` or `WAIVED`, and the newest `review` verdict is `CLEAR` or `WAIVED`, both naming the current code head. The roadmap's "No skipped gate" criterion still holds, because `WAIVED` is a verdict a fresh gate agent gave.

### 7. Merged-in code counts as verified and reviewed

- Code that a merge brings in, from the orchestrator branch, the default branch or the base of a pull request the phase depends on, counts as verified and reviewed. A clean merge needs no gate of its own, even when it touches the phase's owned paths. This generalises run decision `launcher-r3`.
- The exceptions, where incoming code is treated as the phase's own work:
  - the orchestrator branch is frozen after a failed post-merge check;
  - the merge brings commits that no gate or human review covered, such as a delegate's branch merged by mistake.
- A red default branch is ignored, unless the failure is in something the phase builds on or changes. The developer who broke it is assumed to fix it. If it does affect the phase, the phase treats the incoming code as unverified, and sends a decision request if it is blocked.
- The phase's own conflict resolution is the phase's work. It goes through the scoped gates, and rule 3 applies. A regenerated lockfile-only conflict would usually be waived.
- Whether two verified branches work together is the post-merge check's job. A phase does not re-run its checks only because a merge changed a file they read.

### 8. The post-merge check is scoped to the merge's diff

- After a merge into the orchestrator branch, a fresh subagent works out the blast radius of the merge's first-parent diff, as rule 1 says, and runs the checks in it.
- A merge that changes only `.foundry/`, or only generated paths and lines, needs no post-merge check.
- No waiver applies to the post-merge check.
- A failure is handled as today: the orchestrator branch freezes and the phase moves back.

### 9. One full run per feature

Once the last phase has merged into the orchestrator branch, a fresh subagent runs the whole verification skill there, before the orchestrator reports the feature finished. A failure is handled like a failed post-merge check, by moving back the phase that owns the failing paths. The developer may also ask for a full run at any time.

## Risks

- Scoping relies on the agent's blast-radius call. A wrong call is caught only by a later scoped run whose radius includes it, or by the full run in rule 9. Rule 1's audit list makes a wrong call visible.
- Under rule 7, a cross-phase break can surface at the post-merge check, after the phase merged, not before. That costs one `move-back`. It has happened in 0 of the 10 post-merge checks so far.

## Files this touches

Roadmap, by the spec writer in a roadmap update:

- `workflow.md`: States rule 5 (line 77) and the verdict list; rule 6 (line 78) for `WAIVED`; Branches step 6 (line 118) for the scoped post-merge check and the full run once per feature; Fix rounds step 2 (line 164).
- `decisions.md`: D9 (lines 76 to 84), its decision and cost lines. A new decision records this proposal.
- `roles.md`: Verifier (lines 96 to 107) for scoping and waiving; Reviewer (lines 109 to 117) for the first reviewer's waiver.
- `coordination.md`: tick step 3, Merge (line 104), for the scoped check and `WAIVED`.
- `README.md`: the "No skipped gate" criterion (line 71) names `WAIVED`.
- `run-decisions.md`: the orchestrator folds `launcher-r3` into rule 7 and retires it.

Handbooks and references, by the phases that own them:

- `handbooks/verifier.md`: "Run the checks" (line 52) scoped to the blast radius, with the audit list; the waiver test; the "cannot be verified" split next to "None" (line 22); `WAIVED` in the verdict table (line 60).
- `handbooks/reviewer.md`: the first reviewer's waiver, and the review baseline after a waiver (line 11).
- `handbooks/phase-session.md`: line 26 replaced; Verify and Review steps start one reviewer first and record `WAIVED`; "Merge the orchestrator branch" states rule 7.
- `handbooks/orchestrator.md`, on its phase branch: the post-merge check (line 95) scoped, skipped for `.foundry/`-only and generated-only merges, and the full run once per feature.
- `handbooks/pr-creator.md`, on its phase branch: "Check the gates" (line 11) accepts `WAIVED`.
- `references/status-and-messages.md`: the merge rule (line 61) and the allowed `result` values accept `WAIVED`.
- `SKILL.md` line 85 needs no change. It only points to the reference file for the merge rule, and `WAIVED` is still a new verdict for a new code head.
- `tests/s-stack/verify-s-stack/SKILL.md`: a section that tells a scoped run how to choose checks, and says the full run is for the end of the feature.
