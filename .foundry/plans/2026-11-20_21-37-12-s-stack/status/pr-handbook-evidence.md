# Phase `pr-handbook` evidence

## Verify: NOT VERIFIED at `a42cd47ca1eb9cbcfc5dc51e6b608b4864b31d22`

A fresh verifier wrote `tests/s-stack/verify-s-stack/checks/pr-handbook.md` and committed it alone at `a42cd47`. That file extracts the handbook's parameter block, carry loop, proof and merge procedure at run time and runs 14 scratch-repository cases. The verifier then ran `verify-s-stack` in full.

- Checks 1, 2, 3, 5 and 7 passed. Tier 1 printed `all Tier 1 structural checks passed across 20 packages`, outside the sandbox with the pinned 0.32.0 CLI. Checks 4 and 6 were PENDING, as expected while other phases are in flight.
- Check 8 failed. `foundation.md`'s three cold reads and its C2 comparison passed. `pr-handbook.md` passed 12 cases and failed 2.
- Every **Done when** case gave its expected result, and so did the `quick-review` round's cases.
- The two failures are one defect. `git diff-tree --quiet` without `-r` compares only top-level entries, so a commit that changes only `pkg/apm.lock.yaml` (and `.foundry/`) counts as non-empty. The carry loop then feeds `git apply` an empty patch and exits 1, and the proof prints `does not apply`. It is at handbook lines 63 and 112, introduced in `589411b`. The phase session reproduced it independently: without `-r` the check exits 1, with `-r` 0.

## Verify: NOT VERIFIED at `e5f37b81960b7fc447e65ab7cf06bf282db462f4`

A second fresh verifier reran everything at `f66ec2c` (status commit `3710a1d`), and every check passed, Tier 1 included (`all Tier 1 structural checks passed across 20 packages`). It then extended `checks/pr-handbook.md` at `e5f37b8` with one case and found two defects.

- **An add/add conflict empties the file.** A parent pull request adds a package's `apm.yml`. It is squash-merged, and `main` then raises that package's version. The child's merge of `main` conflicts add/add with no stage 1. `side()` fails on `:1:pkg/apm.yml`, `side theirs` truncates the file, it is staged empty, and the script exits 0. This is the shape every middle phase meets once pull request 81 is squash-merged. The new Rerun case fails: `FAIL squash-merged parent that added apm.yml: exit 0, staged pkg/apm.yml is 0 bytes`.
- **The proof is path-relative.** Run from a subdirectory, its `-- .` pathspecs cover only that subdirectory, so a dropped root-level file prints `EQUAL`. The carry loop has the same weakness.

Every other verify-s-stack check passed. Checks 4 and 6 are PENDING, as expected.

## Verify: NOT VERIFIED at `d7efc941b0d361189e023ccb4846dfca78c5c186`

A fourth fresh verifier covered `40334e4` plus its own check-file commit `d7efc94`, which adds a `rounds` scratch repository for repeated generated-only rounds. Checks 1, 2, 3, 5 and 7 passed, Tier 1 among them (`all Tier 1 structural checks passed across 20 packages`). Checks 4 and 6 were PENDING. Check 8 passed for `foundation.md` and `spec-planner-handbooks.md`. Every **Done when** case passed, and so did the four repeated-round cases the orchestrator asked for. `pr-handbook.md` failed one added case.

- **A later round discards a default-branch change.** The round said to pass the squash-merged parent with no limit to the first merge after the squash. In a later round, the squash step then kept the child's side of a real conflict with a newer `main` change, and the proof printed `EQUAL`, because the merge check compares against `merge-tree -X ours`.
- **Minor: an interrupted round never finishes.** If a round stops after its merge commit, the next round's up-to-date test passes, so the regenerate commit and the push never happen.

## Verify: VERIFIED at `412a91d852ac3d59e38fa95a6aa366d5e59a3e91`

A fifth fresh verifier covered handbook head `25e6ef4` plus its own check-file commit `412a91d`. That commit makes the harness follow the round's four steps and adds an interrupted-round case, which it mutation-tested against the old early return. Results:

- **verify-s-stack.** Checks 1, 2, 3, 5 and 7 passed. Tier 1 printed `all Tier 1 structural checks passed across 20 packages`. Checks 4 and 6 were PENDING. Check 8 passed: the `foundation` and `spec-planner-handbooks` cold reads, the C2 comparison, and `pr-handbook.md`'s 27 scratch cases with `0 failed`.
- **Done when.** Every item and every repeated-round case held.

Findings carried to the fix round after Review:

- **Misleads a reader.** A pull request stacked on a parent merges `origin/<default>` directly, so until the parent merges the same tip its diff against the parent shows the default branch's changes. Later the two branches have two merge bases. The proof still passes. Merging the parent's branch into a stacked child keeps the diff to its own change.
- **Minor.** The squash step is skipped when the child merged a default-branch tip its parent never merged. The merge then aborts safely. Under this run's `needs_update` rule the case cannot arise.
- **Minor.** Step 4 pushes before it runs the proof, so a round interrupted between the two skips the proof on the next round.
- **Minor.** The check file's `## Evidence` section still describes failures at `391d9a8` that are long fixed.

## Review: SIGNIFICANT at `412a91d852ac3d59e38fa95a6aa366d5e59a3e91`

p-stack's `interrogate` ran two adversaries, Opus and Fable, on the phase diff, with no access to `.foundry/`. The Gemini seat was dropped because this host does not offer it. The phase session reran each Opus repro, and each reproduced. Verified findings, merged by root cause:

- **Breaks a real run, silently.** On the first merge after a squash, the squash step takes the child's side in every conflicting hunk of the parent's files. It reverts another pull request's change on the same line, or a later default-branch fix to the parent's line, and the proof prints `EQUAL`, because its merge check uses the same rule (Opus 1, Fable 1).
- **Breaks a real run.** The carry loop cannot apply a hunk whose context holds a `version:` line that differs on the target branch: another phase's bump on the orchestrator branch, a regenerate commit in a fix round, or a version change in the commit itself (Opus 2, Fable 2).
- **Breaks a real run.** The proof's replay fails for a correct split once the phase branch has merged a newer orchestrator branch (Opus 3).
- **Breaks a real run.** More than one squash-merged ancestor between rounds cannot be merged, and the wording names the parent rather than the squash-merged ancestor (Fable 3).
- **Breaks a real run, safe stop.** A phase merge that resolved a hand-written conflict cannot be carried (Fable 4).
- **Misleads a reader.** A stacked child merges the default branch rather than its parent's branch (Opus 4, and the verifier). The proof's default argument must be `origin/<default>`, and the order is bottom of the stack first (Fable 5).
- **Minor.** Paths with spaces split in the merge procedure's loops (Fable 6).

The phase session raised `pr-handbook-r1`, because the common root is the premise of merging the default branch and repairing conflicts by heuristic.

## Verify: NOT VERIFIED at `200f342aa307c118f504d438bb6e5ae988ac3791`

A sixth fresh verifier rewrote `checks/pr-handbook.md` for the rebuild design. It committed `5f1fc10`, where everything passed, Tier 1 included. Probing then found a defect, so it added a case in `200f342` and verified there.

- **verify-s-stack.** Checks 1, 2, 3, 5 and 7 passed, and Tier 1 printed `all Tier 1 structural checks passed across 20 packages`. Check 4 lists only `orchestrator.md` as PENDING. Check 6 is PENDING. Check 8 passed for `foundation.md`, `phase-handbooks.md` and `spec-planner-handbooks.md`, with ten cold reads in all. For `pr-handbook.md`, `bash -n` passed, the restacking cold read agreed, and the scratch repositories gave 23 PASS and 1 FAIL.
- **The six Review findings** each fail on the old procedure from `412a91d` and pass now. The squash revert gave `EQUAL` with `main`'s fix lost on the old procedure, and keeps the fix now. The version-context carry gave `patch failed` and now carries. The newer orchestrator merge gave `does not apply` and now gives `EQUAL`. Several squash-merged ancestors gave `FAIL b.txt` and now merge. The stacked child showed `c.txt p.txt` with 2 merge bases, and now shows `c.txt` with 1. The path with spaces gave `FAIL docs` and now merges.
- **Mutations.** Five mutated copies of the script each fail the check: no `--3way`, no `IFS`, no per-pull-request check, a forced merge every round, and a no-op `gen_as`.
- **Rounds.** The repeated rounds, the interrupted round, the hand-edit merge and the forge rewrite of a child's head all gave their required results.
- **The forge rewrite in this run.** On GitHub, #82 moved from `78162e9` to `04e239a` five seconds after #81 merged. Both commits have tree `6a826c3c`.

Defects:

- **Breaks a real run, silently.** A pull request cut from another phase's open pull request, but given a spec without that dependency, carries the other phase's commits as its own. `git apply --3way` absorbs them in the phase-level replay, because the orchestrator branch already holds them, so the proof prints `EQUAL` while the diff holds another phase's files.
- **Minor.** Git quotes non-ASCII paths, so a `STOP` line names `"caf\303\251.md"`.
- **Minor.** A missing open-dependency ref gives a `fatal:` line instead of a `STOP` line. The round still stops safely.
- **Minor, misleads a reader.** The handbook does not say that a child GitHub moved to the default branch after its parent merged is not leaving a stack.

## Verify: VERIFIED at `f5c99ae57b1715a0ceb8f5442426c74d433af3c9`

A seventh fresh verifier covered `3c8b9b7` plus its own check-file commit `f5c99ae`. That commit adds a non-ASCII conflict, a non-ASCII `.foundry/` path and a missing dependency branch, and makes the undeclared-dependency case require the proof's own line. All four new cases failed against the script at `200f342`.

- **verify-s-stack.** Checks 1, 2, 3, 5 and 7 passed. Tier 1 printed `all Tier 1 structural checks passed across 20 packages`. Check 4 lists only `orchestrator.md` as PENDING. Check 6 is PENDING.
- **Check 8.** Passed for `foundation.md` (three cold reads and C2), `phase-handbooks.md` (four cold reads), `spec-planner-handbooks.md` (two cold reads) and `pr-handbook.md`. For `pr-handbook.md`, `bash -n` passed, the 27 scratch cases printed `0 failed`, the line budget is 127/200, and the restacking cold read agreed.
- **Independent rerun.** The phase session reran the scratch cases at `f5c99ae`: 27 PASS, `0 failed`, clean tree.
- **Done when.** Every item holds, and so do decisions d1 to d8 and the four round guarantees.
- **Minor finding, recorded and not fixed.** When a merged dependency's ref is gone, `prove` says "undeclared dependency" instead of naming the missing ref. It fails closed, `refresh` prints a clear `STOP` for the same spec, and the handbook says to restore the ref.
- **Probed and rejected.** A fix round after the orchestrator merged the phase gives `EQUAL`, because carried commits are new objects. A non-ASCII package path resolves correctly.

## Review: SIGNIFICANT at `f5c99ae57b1715a0ceb8f5442426c74d433af3c9`

The second `interrogate` run used Opus and Fable, with the brief in `handbooks/reviewer.md`. Its scope was the commits since `412a91d` plus merge `5821887`'s lockfile-only resolution. The earlier findings' probe, cases `review 1` to `review 6`, passed for both adversaries: 27 PASS, `0 failed`. The new findings, merged by root cause, are below. Significance follows the reviewer brief.

**Significant.**

- **A refresh cannot get past an old commit that conflicts with the default branch** (Opus 1, Fable 1). Once a pull request's existing commit conflicts with a later default-branch change, every refresh stops. That stays true after the phase resolves the conflict, because the refresh replays the old commit first. The documented remedy, an ordinary resolution commit on the phase, never carries.
- **The proof's phase-level replay is wrong once the phase holds content its orchestrator merge base lacks** (Opus 2, Fable 2). That happens after a clean merge of the default branch into the phase (`m.txt` listed), or after the orchestrator merged the phase and two own commits share a line or one deletes a file.
- **A pull request merged with a merge commit drops out of the proof** (Opus 3, Fable 4). This breaks the "squash-merged or not" statement.
- **Moving from row 3 to row 2 under another phase's parent that has not absorbed the default branch** either pushes a tree that reverts a merged dependency or stops falsely (Opus 4).
- **A grandchild whose parent the forge rewrote** stops unless its spec also lists the merged grandparent (Opus 5). This depends on how GitHub rewrites stacks.
- **A phase that deletes a package** leaves the package's lockfile in the pull request, and the proof prints `EQUAL` (Fable 3).

**Not significant alone.**

- A same-phase branch with an undeclared dependency proves `EQUAL` (Fable 6).
- A parent's fix next to a child's change cannot be carried, and the stop is clean (Fable 5).

The phase session raised `pr-handbook-r3`, because the common root is defining a pull request by replaying its commits onto a moving base.

## Verify: VERIFIED at `b4da68bfd86af51de95f4abfd87c63225920817e`

An eighth fresh verifier rewrote `checks/pr-handbook.md` for the path overlay in `b4da68b`, on top of `3ccad64`.

- **verify-s-stack.** Checks 1, 2, 3, 5 and 7 passed, and Tier 1 printed `all Tier 1 structural checks passed across 20 packages`. Checks 4 and 6 are PENDING: `orchestrator.md` and the launcher tests.
- **Check 8.** Every cold read of the three other phases agreed, and so did a new `STOP` cold read on `pr-creator.md`. `pr-handbook.md`'s scratch block printed 46 PASS and `0 failed`, and the phase session reran it with the same result.
- **Done when.** Every item holds, and so do the guarantees and the repeated, interrupted and forge-rewrite rounds.
- **The cases against `f5c99ae`.** Nine of the ten round-two finding cases fail there; the adjacent-line stop already stopped cleanly, and d10 keeps it one. The uncarried-commit and identity cases also fail there.
- **The round-one cases pass at `f5c99ae` too,** because that design already fixed them. d9's wording that they fail on `f5c99ae` cannot hold. They stay as regression cases.

Findings, both misleading a reader:

- A path that landed through a merged pull request, then changed again on `main`, makes the proof say "needs a new pull request" when the merged pull request is not listed. The handbook says merged pull requests need not be listed.
- A pull request opened for an uncarried fix after its parent was squash-merged fails unless the merged one is named in the spec's fourth field, and the handbook does not say so.

Minor: the proof does not catch a deleted package's lockfile being kept or restored on a pull request, because the head comparison excludes generated files.

Not this phase's: `tests/s-stack/verify-s-stack/SKILL.md` check 8 still says `## Evidence` records results.

## Review: SIGNIFICANT at `b4da68bfd86af51de95f4abfd87c63225920817e`

The third `interrogate` run used Opus and Fable, with the brief in `handbooks/reviewer.md`. Its scope was `3ccad64` and `b4da68b`. The earlier findings' probe, the check file's scratch block, printed 46 PASS and `0 failed` for both adversaries.

**Significant, in the overlay premise.**

- **A shared path that conflicts with the default branch is a permanent stop** (Opus 1, Fable 1). It happens with another phase's line in the same file, or with two pull requests of one stack. Neither the phase's merge resolution nor an ordinary resolution commit ever reaches the pull request, because shared paths only replay the phase's original commits.
- **A clean default-branch change to an owned path stops the round** (Opus 3). This is the routine round after another pull request merges. The stop sends the phase to merge the default branch, which moves its code head and reruns both gates, while `phase-session.md` says that round runs no gate.

**Significant, in the implementation or the wording.**

- **The proof prints `EQUAL` for a pull request that still holds a change the phase later reverted** (Opus 2), when the reverting commit is not carried, because the ownership check skips paths that equal the default branch.
- **After the forge rewrites another phase's dependency in row 3, the proof prints `NOT EQUAL` for good,** although the pull request's content is right (Fable 2).
- **The base table yields a split the proof rejects** (Fable 3). Two pull requests that touch one path must be chained, and the handbook never says so.

**Lesser.**

- A delegate branch merged into the phase is dropped, and the proof names the wrong cause (Fable 4).
- `origin/` on a pull request's name gives a false `FAIL` (Fable 5).
- A file replaced by a directory breaks the proof (Fable 6).

**Fallback.** Under `pr-handbook-d9` condition 4, a defect in the overlay premise ends redesigning. The current design ships. Each history it does not handle becomes a documented `STOP` that the phase session sends to the orchestrator as a decision request. The two wrong-result defects, the false `EQUAL` and the `origin/` false `FAIL`, are fixed in the implementation, because a false result cannot be a documented stop.
