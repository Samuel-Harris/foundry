# Phase `spec-planner-handbooks` evidence

## Verify, code head `0d7b25d0a0156ac524a6a32e7e221ad4fed9e1ee`

A fresh verifier subagent wrote `tests/s-stack/verify-s-stack/checks/spec-planner-handbooks.md` in commits `7c59af5` and `0d7b25d`. The second commit fixed the check rather than the handbook: the first expected answer assumed a front end that `planner.md` rightly split in two. The verifier then ran `tests/s-stack/verify-s-stack/SKILL.md` end to end at `0d7b25d`.

| Check | Result |
| --- | --- |
| 1. Primitives and root manifest | PASS. `94 primitives valid`, `12 listed, 19 reached` |
| 2. Markdown lint | PASS. 8 files, 0 errors |
| 3. Line budgets | PASS. `SKILL.md` 103/150, `planner.md` 64/200, `spec-writer.md` 61/200 |
| 4. Routes | PENDING. `planner.md` and `spec-writer.md` present, five other handbooks pending |
| 5. Package isolation | PASS |
| 6. Launcher tests | PENDING. `packages/s-stack/tests` missing |
| 7. Tier 1 | PASS. `all Tier 1 structural checks passed across 20 packages`, exit 0, checked by the phase session in the log |
| 8. Check files | PASS. Three foundation cold reads, the C2 comparison and both spec-planner-handbooks cold reads |

Verdict: VERIFIED. The verifier noted two small gaps, which the phase session fixes in a new code head: `planner.md` did not say what happens when a phase must depend on two open phases, and `spec-writer.md` did not say which command's output to report.

## Verify, code head `08874f390fa5e43df00cb90946b113b92f1fb1e0`

A second fresh verifier ran the full skill again at HEAD `8d22ba0` and left the check file unchanged. Checks 1, 2, 3, 5, 7 and 8 passed. Check 4 is pending on the five handbooks other phases own, and check 6 is pending on the launcher's tests. Tier 1 printed `all Tier 1 structural checks passed across 20 packages`, exit 0, which the phase session confirmed in the log. All four Done-when items passed, and both cold reads matched their expected answers point by point. Verdict: VERIFIED. Minor note: in `planner.md` the sentence that gives every phase its own check file sits inside the "no existing verification skill" bullet.

## Review, code head `08874f390fa5e43df00cb90946b113b92f1fb1e0`

p-stack's `interrogate` skill ran with two adversaries, on Opus and on Fable, each in its own detached worktree at `08874f3`. Each got only the diff and the repository and was told not to read `.foundry/`. The configured Gemini seat is not available on this host. Neither adversary found a significant issue. Their cold reads covered roadmap updates, soft approvals, launcher failures, one-way doors, a typed developer instruction and a restart, and in every one the session acted correctly. The phase session reran each minor finding's command and confirmed it. Verdict: CLEAR.

Minor findings fixed in the next code head:

- The planner sent decision requests only after writing the plan.
- The planner's record of a developer's answer lacked the door type and who decided.
- Nothing stopped the planner sending `done-planning` while a request was open.
- An update spec writer skipped the visibility check.
- In the check file, the first cold read cites roadmap `workflow.md`, which never ships, and leaves out **Must not touch**. The next verifier fixes that.

Findings dismissed, with reasons:

- A restarted planner can still find answers. The orchestrator records each decision in `run-decisions.md` (roadmap `coordination.md`, tick step 5), and the planner reads that file after a restart.
- The spec writer asks the developer directly and sends no decision request, as roadmap `roles.md` and `workflow.md` design it. The reference file still lists the spec writer as a sender, and that gap is with the orchestrator as a `foundation` follow-up.
- Session names and branch names belong to the launcher.

## Verify, code head `6f70b3707c6c24f174c333817b3a17f37a5d9f63`

A third fresh verifier made the check-file fix the review asked for at `6f70b37`. Cold read 1's expected fields now come from `planner.md`'s own table and include **Must not touch**. It then ran the full skill. Checks 1, 2, 3, 5, 7 and 8 passed. Checks 4 and 6 are pending, as the skill allows. Tier 1 printed `all Tier 1 structural checks passed across 20 packages`, exit 0, which the phase session confirmed in the log. All Done-when items passed. Verdict: VERIFIED.

Minor notes, recorded and not fixed, under the orchestrator's instruction to fix only what would mislead a reader or break a real run:

- `spec-writer.md` does not define `<this skill's directory>`. `SKILL.md` lines 16 and 24 do.
- `spec-writer.md` does not say who to record as decider for a two-way door the spec writer decides itself.
- `planner.md` does not say where each phase's check file lives. The plan names it.

## Review, code head `6f70b3707c6c24f174c333817b3a17f37a5d9f63`

p-stack's `interrogate` skill ran again with two adversaries, on Opus and on Fable, over the commits since `08874f3`. Each worked in its own detached worktree at `6f70b37`, got only the diff and the repository, and was told not to read `.foundry/`. Neither found anything, significant or minor. Their seven cold reads covered decisions met before the plan existed, a request still open at the end of planning, a restart mid-request, a restarted planner with an old-format plan, an update spec writer in a public repository given private names, and the check file's cold read 1. Every session acted correctly. Fable's mechanical checks found the lockfile hashes in step and `versioning.py check` clean. Verdict: CLEAR.

## Pull request 84

https://github.com/Samuel-Harris/foundry/pull/84. Draft, branch `s-stack-spec-planner-handbooks`, base `main`, head `dede1c5`. It depends on 81 and 82, both open, so it is cut from `s-stack-verify-skill` at `78162e9` and carries both parents' commits. It is not stacked.

- **Equality proof.** The PR creator ran the Experiment 7 commands on `s-stack-package`, the phase branch, `origin/main`, and `s-stack-spec-planner-handbooks:origin/s-stack-foundation-package,origin/s-stack-verify-skill`, and they printed `EQUAL`. The regenerate check, the `.foundry` check and the `apm.yml` check printed nothing. The phase session confirmed three things: the three content files on the pull request branch are byte-identical to `6f70b37`, `git diff --name-only origin/main...origin/s-stack-spec-planner-handbooks -- .foundry` is empty, and the pull request is a draft against `main`.
- **Regenerate commit.** `dede1c5` changes only `packages/s-stack/apm.lock.yaml`. `versioning.py bump` raised no version, because s-stack is not on `main` yet.
- **Size.** 166 hand-written lines against `s-stack-verify-skill`, and 802 added and 26 removed against `main` including both parents, lockfiles excluded.
- **CI.** Pre-commit checks, Package versions, Detect changed paths, data-visualisation tools tests and foundry-maintenance script tests passed. The p-stack tests and Tag package versions were skipped by their path and event conditions.

## Fix round after #81 merged, generated files only

#81 was squash-merged into `main` as `d7e036c`, and #84 conflicted with `main`. The phase branch merged `s-stack-package` at `2dff76b`. That merge changed nothing outside `.foundry/`, so the code head stays `6f70b37` and no gate ran.

A fresh PR creator rebuilt #84 under `pr-handbook-r1`.

- **Rebuild.** It replayed the eight own commits with `git apply --3way` onto `origin/s-stack-verify-skill` (`04e239a`), with no conflict. The rebuilt tree differed only in `packages/s-stack/apm.lock.yaml`. It recorded the tree as merge commit `3b15a0a` (`git commit-tree -p dede1c5 -p origin/s-stack-verify-skill`), then added regenerate commit `49df8c3`, which raised s-stack from 0.1.0 to 0.1.1. It pushed as a fast-forward, with no force.
- **Base.** #85 is already stacked on #82, so #84 keeps base `main` and carries #82's commits. It depends on [82] and is not stacked.
- **Equality proof.** The rebuild-form proof printed `EQUAL`. The phase session confirmed four things:
  - The three content files are byte-identical to `6f70b37`.
  - The diff against `s-stack-verify-skill` adds only `packages/s-stack/apm.lock.yaml` and the `version:` line of `packages/s-stack/apm.yml`.
  - No `.foundry/` path is on the branch.
  - GitHub reports #84 as mergeable and CLEAN.
- **Size.** 167 added and 1 removed against `s-stack-verify-skill`.
- **CI at `49df8c3`.** Pre-commit checks, Package versions, Detect changed paths and both tools test jobs passed.

## Follow-up round: Verify, code head `49f295936b38922510b53242717c6098f6ea5ec2`

The round rewords cold read 1's expected point 5 so it requires port 5432 only on the sharing back-end phase. A fresh verifier ran the full skill at HEAD `1580847`, where only `.foundry/` differs from `49f2959`.

- Checks 1, 2, 3, 5, 7 and 8 passed. Check 4 is pending on `orchestrator.md` and `pr-creator.md`, and check 6 on the launcher's tests.
- Tier 1 printed `all Tier 1 structural checks passed across 20 packages`, exit 0, which the phase session confirmed in the log.
- Check 8 covered every check file's Rerun section: `board.md`'s headless Chrome script, `foundation.md`, `phase-handbooks.md` and this phase's file. All passed.
- This phase's cold read 1 ran three times, and point 5 passed in all three. Two runs named the port for a second phase under a stated assumption, which the new wording treats as neutral.
- All Done-when items passed. Verdict: VERIFIED.

Minor note, recorded and not fixed under `spec-planner-handbooks-d3`. Point 3 does not say that port contention under a stated assumption leaves "can run at the same time" intact. One run hedged on it and was graded PASS.

## Follow-up round: Review, code head `49f295936b38922510b53242717c6098f6ea5ec2`

Two adversaries ran `interrogate`, on Opus and on Fable, scoped to the one-line point 5 change. They graded real planner answers and hand-written variants with fresh grader subagents.

- **Significant (Opus).** Answer C names the port on the sharing phase and lists none for the import phase. Its own stated assumption has the import tests use that database, and it still runs the two phases at the same time. The new point passed it, while the old point failed it ("P2's tests use port 5432 and the port is not named as P2's exclusive resource"). An orchestrator following that plan would schedule a port collision.
- **Minor (both).** An answer that names "the local test database" on the sharing phase but not the number 5432 now fails. The old point accepted it with "or the local test database on it".
- Both reviewers confirmed the change's aims hold. Answers with the port off the sharing phase, or with no port at all, fail. Real answers that give the port to a second phase under an assumption pass.

Verdict: SIGNIFICANT. The phase moves back to Implement. The fix restores the database alternative and fails an answer whose own assumptions put a concurrent phase on the database without naming it there.

## Follow-up round: Verify, code head `ba02397c72378fd5d5a54389d49b9ee7011f52ee`

A fresh verifier ran the full skill and four point 5 probes, each graded by a fresh subagent.

- **Probes.** All four came out as intended:
  - (C) A concurrent import phase uses the database by its own assumption but lists "none". FAIL.
  - (E) The database is named without the port number. PASS.
  - (A) The port is on the import phase only. FAIL.
  - (D) The port is on both phases under a stated assumption. PASS.
- **Tier 1 and check files.** Tier 1 passed across 20 packages. Every check file's Rerun passed.
- **Failure.** One of three extra runs of cold read 1 failed point 3. It gave the port to both the sharing and import phases under a stated assumption, and so ran them one after the other. Roadmap `roles.md` says the orchestrator "never runs two phases that need the same exclusive resource", so that reading is right, and point 3 was too strict.

Verdict: NOT VERIFIED. Fix: point 3 also accepts the two phases running one after the other when the answer's own stated assumption gives both the same exclusive resource. `planner.md` does not change.

## Follow-up round: Verify, code head `1f6216019e8b1c657d52e1c360285e2bc2516ef5`

A fresh verifier ran the full skill. It passed, apart from checks 4 and 6, which are pending by design. Tier 1 passed across 20 packages, and every check file's Rerun passed.

- **Point 5 probes.** A and C fail and E passes, as required. F passes points 3 and 5: it gives the port to both phases under an assumption and runs them one after the other.
- **Planner runs.** All five real runs of cold read 1 pass point 5.

Verdict: VERIFIED.

**Gap the verifier found.** Probe D and real run 3 give the port to both phases and still say they run at the same time. Two graders out of two failed D on point 3, while the literal first sentence of point 3 would pass it. Roadmap `roles.md` line 46 says the orchestrator never runs two phases that need the same exclusive resource, so D's claim is wrong. The source is `planner.md`: it asks for exclusive resources but never says they serialise the phases that share them. That misled run 3 into saying test runs "take turns". The phase moves back to Implement. `planner.md`'s exclusive-resources bullet gets that sentence, and point 3 says outright that phases sharing an exclusive resource run one after the other.

## Follow-up round: Verify, code head `47f792f2110fc8b49158a7305c703ec5de9f6c91`

A fresh verifier ran the full skill, apart from checks 4 and 6, which are pending by design. Tier 1 passed across 20 packages, which the phase session confirmed in the log, and every check file's Rerun passed.

- **Planner runs.** Six real runs of cold read 1 passed all five points. Every run that gave port 5432 to two phases ran them one after the other, quoting the new `planner.md` sentence or reasoning from it. None ran them together.
- **Probes.** Every probe graded as required:
  - A fails point 5.
  - C fails points 3 and 5.
  - D fails point 3 and passes point 5.
  - E and F pass.

Verdict: VERIFIED.

## Follow-up round: Review, code head `47f792f2110fc8b49158a7305c703ec5de9f6c91`

Two adversaries ran `interrogate`, on Opus and on Fable, scoped by the orchestrator to `49f2959..47f792f` on this phase's owned paths. They produced 8 real planner answers and 13 hand-written answers, and graded them with more than 30 fresh graders.

- **Planner runs.** Every real plan could be scheduled. Every plan that put port 5432 on two phases ran them one after the other, without a made-up dependency.
- **Wrong answers failed.** These included:
  - a concurrent phase on the database with "none" listed;
  - the same, argued as "shared, not exclusive";
  - the same, with the use implicit in Done when;
  - "test runs take turns" with the phases running together.
- **Correct answers passed.** These included the database named without the number. Verdict: CLEAR.

Minor findings, recorded and not fixed under `spec-planner-handbooks-d3`:

- Point 3 passes an answer that serialises the two phases through a made-up dependency. That plan can still be scheduled, just later.
- Sonnet graders failed one correct answer on point 3 in two of three runs. Their reasons were not in point 3 (open pull requests, a note about a falsified assumption), and Opus and default graders passed it. Use Opus graders for this check.

## Follow-up round: PR creator STOP

The PR creator built `s-stack-spec-planner-port-rule` from `origin/main` (`51f334e`) with the pr-handbook phase's `pr.sh`, which it ran unchanged.

- **The branch.** It carried the five phase commits with cherry-pick trailers, then added regenerate commit `25173f8`, which bumps s-stack from 0.1.3 to 0.1.4 and refreshes the lockfile hashes.
- **What passed.** `git diff 47f792f HEAD` on both files printed nothing. Against `main`, the change is 2 hand-written files with +3/-3, plus the `version:` line. The hook exited 0. `versioning.py check` printed `1 changed package(s), none without a version bump`.
- **What failed.** `pr.sh prove` printed NOT EQUAL. Every FAIL is about the merged #84 branch. It was built under commit replay before cherry-pick trailers existed, and it carries #81's and #82's pre-merge commits. So the proof cannot match the earlier phase commits on the three owned files to anything, although their content is on `main` through #84's squash.
- **Where it stopped.** Nothing was pushed, and the local branch was deleted. The PR creator stopped because this history is not in the handbook's STOP table. The phase sent decision request `spec-planner-handbooks-r1`.

## Follow-up round: pull request evidence under `spec-planner-handbooks-r1`, option A

The orchestrator answered `spec-planner-handbooks-r1` with option A: ship on equivalent evidence. A fresh PR creator rebuilt `s-stack-spec-planner-port-rule` from `origin/main` (`51f334e`). It used `pr.sh` refresh, carrying the five phase commits with cherry-pick trailers, then added regenerate commit `5da7f5d`, which bumps s-stack from 0.1.3 to 0.1.4. The branch head is `5da7f5dcd4e4df46c289fec470f409d7996d8fb5`. The phase session checked the stat, the version diff, the byte identity and the `.foundry` check itself.

**Proof FAIL lines.** `OWN=s-stack-spec-planner-port-rule bash pr.sh prove s-stack-package s-stack-phase-spec-planner-handbooks origin/main s-stack-spec-planner-handbooks:main s-stack-spec-planner-port-rule:main::s-stack-spec-planner-handbooks` exited 1 with NOT EQUAL. Every FAIL line is about the merged #84 branch or the phase commits it carries without trailers:

```text
FAIL packages/s-stack/.apm/skills/sam-mode/handbooks/planner.md: s-stack-spec-planner-port-rule lacks phase commits a6652c7 fix(s-stack): record planner decisions as met, with door and decider, and check visibility on updates;08874f3 fix(s-stack): cover an unavoidable two-parent dependency and the l
FAIL packages/s-stack/.apm/skills/sam-mode/handbooks/spec-writer.md: s-stack-spec-planner-handbooks lacks phase commits a6652c7 fix(s-stack): record planner decisions as met, with door and decider, and check visibility on updates;08874f3 fix(s-stack): cover an unavoidable two-parent dependency and t
FAIL s-stack-spec-planner-handbooks: it changes AGENTS.md, which the phase does not
FAIL s-stack-spec-planner-handbooks: it changes apm.yml, which the phase does not
FAIL s-stack-spec-planner-handbooks: it changes docs/COMPATIBILITY.md, which the phase does not
FAIL s-stack-spec-planner-handbooks: it changes docs/DEPENDENCY-CONTRACTS.md, which the phase does not
FAIL s-stack-spec-planner-handbooks: it changes packages/s-stack/.apm/skills/sam-mode/references/status-and-messages.md, which the phase does not
FAIL s-stack-spec-planner-handbooks: it changes packages/s-stack/.apm/skills/sam-mode/SKILL.md, which the phase does not
FAIL s-stack-spec-planner-handbooks: it changes packages/s-stack/.gitignore, which the phase does not
FAIL s-stack-spec-planner-handbooks: it changes packages/s-stack/apm.yml, which the phase does not
FAIL s-stack-spec-planner-handbooks: it changes packages/s-stack/README.md, which the phase does not
FAIL s-stack-spec-planner-handbooks: it changes README.md, which the phase does not
FAIL s-stack-spec-planner-handbooks: it changes tests/acceptance.md, which the phase does not
FAIL s-stack-spec-planner-handbooks: it changes tests/s-stack/verify-s-stack/checks/foundation.md, which the phase does not
FAIL s-stack-spec-planner-handbooks: it changes tests/s-stack/verify-s-stack/SKILL.md, which the phase does not
FAIL s-stack-spec-planner-handbooks: it changes tests/structural/run-tier1.sh, which the phase does not
FAIL s-stack-spec-planner-handbooks: its head differs from its target tree
FAIL tests/s-stack/verify-s-stack/checks/spec-planner-handbooks.md: s-stack-spec-planner-port-rule lacks phase commits 6f70b37 test(s-stack): check the planner's phase fields against the handbook;0d7b25d test(s-stack): keep the planner cold read's front end in one phase;7c59af5 test(s-stack): add th
NOT EQUAL
```

**Head versus target, by direct comparison.** The proof prints no head line for this branch, so the PR creator built the expected tree in a temporary index: `origin/main`, plus the two files' blobs from `47f792f`, plus the regenerate commit's diff. The expected tree and the branch tree are both `96e80cfd84d6a49423a6b3d0b85d80fe0b0868d3`, and `git diff` printed nothing.

**`git diff origin/main 5da7f5d --stat`:**

```text
 packages/s-stack/.apm/skills/sam-mode/handbooks/planner.md    | 2 +-
 packages/s-stack/apm.lock.yaml                                | 8 ++++----
 packages/s-stack/apm.yml                                      | 2 +-
 tests/s-stack/verify-s-stack/checks/spec-planner-handbooks.md | 4 ++--
 4 files changed, 8 insertions(+), 8 deletions(-)
```

The `apm.yml` change is only `version: "0.1.3"` to `version: "0.1.4"`.

**Byte identity with `47f792f`.** `git diff 47f792f 5da7f5d` over both files printed nothing. The blobs are `planner.md` `3bf6a664668eb38b78dabb8e929189110027b9f3` and `spec-planner-handbooks.md` `c625d6763c55a8ab9c1a1e38117e95129bb6cb7e` on both sides. No `.foundry/` path is on the branch. The hook exited 0, and `versioning.py check origin/main` printed `1 changed package(s), none without a version bump`. The full command log is the PR creator's `r1-evidence.md` in the phase session's scratchpad.
