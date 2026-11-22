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

## Verify: NOT VERIFIED at `cff49f82534b3d132232b232060000fd5a9fd5bb`

A ninth fresh verifier extended `checks/pr-handbook.md` in `cff49f8`, on top of `9b1493c`. It added ten scratch cases, updated the `STOP` cold read to eleven items, and verified there.

- **verify-s-stack.** Checks 1, 2, 3, 5 and 7 passed, and Tier 1 printed `all Tier 1 structural checks passed across 20 packages`. Checks 4 and 6 are PENDING. In check 8, `foundation` and `phase-handbooks` agreed, and the `STOP` cold read agreed on all eleven items.
- **`spec-planner-handbooks.md` cold read 1** failed expected point 3 twice: both readers said the two phases cannot run together, because both need port 5432. That check belongs to another phase.
- **`pr-handbook.md` scratch block.** It printed 59 PASS and `5 failed`.
- **What passes.** Both wrong-result cases pass now and fail at `b4da68b`: the revert, and `origin/` names. The shared-path and owned-path stops print exactly their documented output and leave the branch unchanged. The chained rule and the merged-listing cases pass. Every **Done when** item holds.

Defects:

- **Misleads a reader, and the round pushes a wrong tree.** `pr-creator.md`'s table says that for every unhandled history the branch is left alone and nothing is pushed. For the forge-rewritten row-3 dependency, the delegate merge and the file replaced by a directory, the refresh exits 0. The round pushes, and only the proof after it fails. In the delegate case the pushed branch lacks the delegate's file.
- **A directory replaced by a file** prints different output from the table's. The script ignores a failed `put`, pushes a tree that deletes `notes/one.md` without adding `notes`, and the proof's `FAIL` sends the reader to open a new pull request.
- **Minor.** `prove` reads a plain `<pr>` as the local branch, although the script's prose says it prefers `origin/<branch>`.
- **Not this phase's.** The `spec-planner-handbooks` cold read above.

## Verify: NOT VERIFIED at `345764ca0ca2270b7b958d21acc55125655bc08b`

A tenth fresh verifier updated `checks/pr-handbook.md` in `345764c`, on top of `262027f`, so the five unhandled histories assert the refresh's new stops.

- **verify-s-stack.** Checks 1, 2, 3, 5 and 7 passed, and Tier 1 printed `all Tier 1 structural checks passed across 20 packages`. Checks 4 and 6 are PENDING. Check 8 passed for every file. `pr-handbook.md`'s scratch block printed 64 PASS and `0 failed`, the `STOP` cold read agreed on all eleven points, and `spec-planner-handbooks` cold read 1 agreed this time.
- **The new stops.** No false `STOP` came from the "would carry" check on a correct history: a fix round after the orchestrator merged the phase, a squash-merged parent, stacked children, and a whole-stack forge rewrite all passed.

Defects:

- **Significant: a false `EQUAL` and a pushed wrong tree after a delegate merge.** If the round is given only the phase's first-parent commits, the refresh pushes `pr1` without the delegate's `d.txt`, and the proof prints `EQUAL`. The proof only looks at first-parent paths, so it contradicts `pr-commands.md`'s statement that a broken assumption gives `NOT EQUAL`.
- **Significant: the table's delegate remedy never reaches `EQUAL`.** After reverting the merge and taking the commits with `git cherry-pick -x`, the revert commit carries nothing on the pull request, and the proof then counts it as uncarried in every round.
- **Misleads a reader.** `pr-commands.md` still says a file replaced by a directory gets through the refresh, which is no longer true.
- **Minor.** A stacked child of another phase's rewritten parent hits the "would carry" stop, which the table names only for row 3.
- **Minor.** A stopped first build cannot be retried as written, because step 1 uses `-b` on a branch the stop left behind.

The phase session's judgement: whether a failed check pushes anything should not depend on the refresh catching every history. The round should refresh, regenerate and prove every branch locally, and push only after `EQUAL`.

## Verify: NOT VERIFIED at `2168718a942213f1163caf2369ee389837065d31`

The eleventh verifier was stopped before any verdict, because `pr-handbook-d12` changed the script. A twelfth fresh verifier then covered `0a30b0a` plus its own check-file commit `2168718`. That commit makes the harness refresh and regenerate every branch, prove locally, and push only on `EQUAL`. On any failing round it asserts that nothing on `origin` moved.

- **verify-s-stack.** Checks 1, 2, 3, 5 and 7 passed, and Tier 1 printed `all Tier 1 structural checks passed across 20 packages`. Checks 4 and 6 are PENDING. In check 8, `board`, `foundation`, `phase-handbooks` and `spec-planner-handbooks` passed. `pr-handbook.md` parsed, met its budget and agreed on all eleven cold-read points, but its scratch block printed 77 PASS and `6 failed`.
- **What passes.** Every `STOP` and proof `FAIL` pushed nothing. Also passing:
  - the delegate cases, the first-parent-only round, the rebuild remedy and the round after a push;
  - the own-phase stack on an unpushed parent;
  - d12's required case, where another phase's local parent ahead of `origin` is ignored;
  - the retries;
  - the stale-owned-path remedy through another phase's branch.

Defects:

- **Significant: a regression from `f87a03f`.** A new branch starts from `origin/<default>`, so a same-phase stacked child that extends its parent's file hits a false permanent shared-path `STOP` on its first build. That was cases `r2-adjacent` and `r2-grandchild`. Started from the local parent, it proves `EQUAL`.
- **Significant, rare: d12 breached.** `mine_branch` treats a branch that carries even one of this phase's commits as this phase's own. Another phase's branch stacked on ours, left ahead of `origin` by a crash, was read locally. The child then pushed the other phase's unproved file, and the proof printed `EQUAL`.
- **Minor: the delegate check is exempted once the orchestrator branch holds the delegate merge.** A fix round after that proves `EQUAL` without the delegate's file.
- **Check file, for the next verifier.** Cold-read expected point 10 still says "reverts that merge".

## Verify: NOT VERIFIED at `e57cbea4424987fc86c14904b0ea81839b3fa895`

A thirteenth fresh verifier covered `cd15544` plus its own check-file commit `e57cbea`. That commit makes the harness follow the new start point, corrects cold-read point 10, and adds `c_extend`, `c_foreign_above` and `c_delegate_after_orch`.

- **verify-s-stack.** Checks 1, 2, 3, 5 and 7 passed, and Tier 1 printed `all Tier 1 structural checks passed across 20 packages`. Checks 4 and 6 are PENDING. Check 8 passed for every file, and `pr-handbook.md`'s scratch block printed 82 PASS and `0 failed`.
- **The cases.** The three previous reproductions now give their required results. `c_foreign_above` and `c_delegate_after_orch` fail against the `2168718` script.

Defects, both significant, both in `mine_branch`:

- **Defect 1: a false `STOP` that recurs every round, or a stale child.** In the stack `x` (another phase) ← `pr1` (ours) ← `pr2` (ours), `pr1`'s round can merge `x` without carrying a commit. Its newest reachable commit is then `x`'s, so `pr1` is read from `origin`. `pr2` stops with `pr1 does not hold origin/main` every round. When `main` has not moved, `pr2` is pushed without `pr1`'s new head.
- **Defect 2: another phase's unproved local branch reaches our pushed pull request.** In the stack `pr1` (ours) ← `x` (another phase) ← `pr2` (ours), `x`'s newest reachable non-merge commit can be our carried fix. A crashed round that left `x` ahead with `u.txt` is then read locally, the proof prints `EQUAL`, and `origin/pr2` holds `u.txt`.

The phase session's judgement: two heuristics for "this phase's branch" have failed. The PR creator creates its own branches, so the round should name them instead of inferring them.

## Verify: VERIFIED at `697c739bd6e0f74b9de3e8d918196ea947afd469`

A fourteenth fresh verifier covered `e81ff27` plus its own check-file commit `697c739`. That commit makes the harness export `OWN`, and adds three cases: a mixed stack where the parent only merges, a crashed foreign branch, and a branch missing from `OWN`. All three fail on the `e57cbea` script.

- **verify-s-stack.** Checks 1, 2, 3, 5 and 7 passed, and Tier 1 printed `all Tier 1 structural checks passed across 20 packages`. Checks 4 and 6 are PENDING.
- **Check 8.** It passed for `board`, with 50 `ok` lines, and for `foundation`, `phase-handbooks` and `spec-planner-handbooks`. For `pr-handbook.md`, `bash -n` passed, the scratch block printed 85 PASS and `0 failed`, the budget is 153/200, and the `STOP` cold read agreed on all eleven points.
- **Independent rerun.** The phase session reran the scratch block from outside the repository: 85 PASS and `0 failed`, with the branch list unchanged.
- **Every Done when item and decisions d1 to d13 hold.**

Findings, carried to the round after Review:

- **Minor, could mislead.** `pr-creator.md` defines `<own branches>` as "the ones you create", but a fresh PR creator in a later fix round did not create the earlier branches. Leaving them out gives a false `STOP`, or a child pushed without its parent's new head, which the next round heals. Suggested wording: every pull request branch of this phase, including those opened in earlier rounds.
- **Minor.** An empty or missing `OWN` is accepted silently. The script could refuse a refresh whose `<pr>` is not in `OWN`.

## Review: SIGNIFICANT at `697c739bd6e0f74b9de3e8d918196ea947afd469`

The fourth `interrogate` run used Opus and Fable, with the brief in `handbooks/reviewer.md`. Its scope was the eleven commits from `9b1493c` to `697c739`. The earlier findings' probe, the check file's scratch block, passed for both adversaries, with 85 and 86 PASS and `0 failed`.

**Significant, in the implementation.**

- **Carry before merge** (Fable 1, 2 and 3). The refresh carries new commits before it brings in the base. So a child's fix that builds on its parent's fix in the same round, a new third-row pull request that edits its dependency's file, and a fix commit that spans two pull requests all get a false permanent shared-path `STOP`. Two refreshes, the first with no commits, go through. A fix that spans two unchained pull requests is also misdiagnosed as a permanent stop, when it is a split fault.
- **`outside()` still infers phase ownership from trailers** (Opus 1). A child stacked on another phase's branch that itself sits on our branch silently reverts that phase's later change to a file the child owns, and the proof prints `EQUAL`.
- **Paths with glob characters are expanded** (Opus 2, Fable 8). `app/[id]/page.tsx` becomes `app/i/page.tsx` when that file exists. The real file is never carried, and the proof prints `EQUAL`.

**Significant, in the premise, and silent.**

- **A developer's commit on a pull request branch is reverted with `EQUAL`** (Fable 4), as for GitHub's "Apply suggestions" button.
- **A hand edit made inside the phase's merge of the orchestrator branch reaches no pull request, and the proof prints `EQUAL`** (Fable 5). This holds on a shared path or on a path no phase commit touches.

**Not significant alone.**

- `not()` excludes a stale local copy of another phase's branch, so the documented forge-rewrite `STOP` does not fire and the round pushes. The pushed tree is right (Fable 6).
- A merged pull request reverted on the default branch still proves `EQUAL` (Fable 7).
- A never-pushed local branch outside `OWN` is read locally.
- The handbook does not say to skip merged pull requests in a round.

**Fallback.** Under d9 condition 4 and d11 the design is not changed. The implementation bugs are fixed. The two premise defects are turned into proof `FAIL`s that push nothing and are documented as unhandled histories, because a wrong `EQUAL` is never acceptable.

## Verify: NOT VERIFIED at `c3a5c5baf8915f8868535de60b90781e8be4c4d6`

A fifteenth fresh verifier covered `85bb0a5` plus its own check-file commit `c3a5c5b`. That commit adds seventeen cases and corrects the merged-dependency restore command in the cold read.

- **verify-s-stack.** Checks 1, 2, 3, 5 and 7 passed, and Tier 1 printed `all Tier 1 structural checks passed across 20 packages`. Checks 4 and 6 are PENDING. Check 8 passed for `board`, `foundation`, `phase-handbooks` and `spec-planner-handbooks`. For `pr-handbook.md`, the parse, the budget (159/200) and the eleven-point cold read passed, but the scratch block printed 101 PASS and `2 failed`.
- **New cases.** Fifteen of them fail at `697c739` and pass now: the refresh order, the split fault, `outside()` and `not()` through `OWN`, the glob path, the local-only branch, the `OWN` refusal, both merge-edit cases, the developer commit, and landed content without the merged pull request listed.

Defects:

- **Significant: a developer's edit inside a merge on a pull request branch is reverted with `EQUAL`, against d15.** `own()` skips merges, so the refresh rebuilds the tree and undoes the edit, and the proof checks only the new head.
- **Significant: d16's history fails when the handbook is followed.** Listing the merged pull request, built without trailers, reports its old commit as `DEVELOPER-COMMITS` and fails its head against a target tree.
- **Minor, could mislead.** A developer commit that adds a new file gets the delegate and forge `STOP` "would carry" instead of `DEVELOPER-COMMITS`.
- **Not run.** The two `## Evidence` checks need GitHub.

## Verify: NOT VERIFIED at `0305089fca6946a7631acacd073d7206a0d3656f`

A sixteenth fresh verifier covered `3d475ad` plus its own check-file commit `0305089`.

- **verify-s-stack.** Checks 1, 2, 3, 5 and 7 passed, and Tier 1 printed `all Tier 1 structural checks passed across 20 packages`. Checks 4 and 6 are PENDING. Check 8 passed for every file. `pr-handbook.md`'s scratch block printed 107 PASS and `0 failed`, and the eleven-point cold read agreed.
- **New cases.** A developer edit inside a merge with its remedy, the merged pull request listed in `c_landed`, and a developer's new file with its remedy all fail at `85bb0a5` and pass now. "Update branch" on a stacked child passes at both heads, because `85bb0a5` never inspected merges, and a mutation shows that case can fail.
- **Done when and decisions d1 to d16 hold.**

Defects, all present at `85bb0a5` too:

- **Significant: the developer rewrites a pull request branch.** The developer amends a carried commit and force-pushes. The commit keeps its trailer, so it matches its phase commit, and the round reverts the change and pushes with `EQUAL`.
- **Minor: GitHub's "Update with rebase" re-hashes a developer commit the phase already took.** The round stops safely, but its documented remedy, `cherry-pick -x`, has nothing to commit.
- **Minor: a developer squash and force-push without trailers** gets "lacks phase commits" instead of `DEVELOPER-COMMITS`. Nothing is pushed.

Request `pr-handbook-r4` asks whether developer rewrites of pull request branches are in scope.

## Verify: VERIFIED at `d6067a3f3535f5366eb22b1115b2ce4459a77426`

A seventeenth fresh verifier, under the common-path bar of `pr-handbook-d17`, covered `9a3f721` plus its own check-file commit `d6067a3`. That commit adds cold-read item 12 on a rewritten pull request branch.

- **verify-s-stack.** Checks 1, 2, 3, 5 and 7 passed, and Tier 1 printed `all Tier 1 structural checks passed across 20 packages`. Checks 4 and 6 are PENDING. Check 8 passed for every file. `pr-handbook.md`'s scratch block printed 107 PASS and `0 failed`, and the twelve-item cold read agreed.
- **Common-path probes.** Five new probes found no false `EQUAL`, `FAIL` or `STOP`, no unproven push and no lost developer change. They covered:
  - a developer commit on a stacked parent, with its remedy;
  - "Update branch" followed by a developer commit;
  - a later review fix on a suggested line;
  - a parent merged with a merge commit;
  - a parent merged by rebase with the child rewritten.
- **Rewrite probes.** They behave as at `0305089`. Under d17 that history is a precondition and an undetected history.
- **Done when and decisions d1 to d17 hold.**
- **Independent rerun.** The phase session reran the scratch block: 107 PASS and `0 failed`. It took about 85 minutes, against about 10 earlier, because the machine's load average was about 10 while other sessions ran their own scratch suites. It was not a hang, and every assertion passed in order.
- **Minor, off the common path.** The rewrite row does not name the "lacks phase commits" `FAIL` that a squash without trailers gives. Nothing is pushed. Carried to the round after Review.

## Review: SIGNIFICANT at `d6067a3f3535f5366eb22b1115b2ce4459a77426`

The fifth `interrogate` run used Opus and Fable under the common-path bar of `pr-handbook-d17`. Its scope was the nine commits from `5538053` to `d6067a3`. The earlier findings' probe, the check file's scratch block, printed 107 PASS and `0 failed` for both adversaries.

**Significant, all where merged pull requests meet developer commits.**

- **A developer commit on a pull request that merged before the phase took it** (Opus 1 and 2). After a squash merge the proof prints a false `EQUAL`, because the merged pull request counts as owning the path. After a true merge it prints "needs a new pull request", which no new pull request clears.
- **A squash-merged pull request listed in the proof, after `main` changes its file and the phase takes `main`** (Fable 2). The proof prints `neither the phase's nor main's` and a head `FAIL` for good, so later rounds are blocked. The same happens at `697c739`.
- **An independent merged pull request still takes the developer check** (Fable 3). Its result depends on a local branch nobody updates, and after the phase takes `main` the remedy is an empty pick.
- **A developer commit the phase took is reported again after GitHub rebases the child onto `main`** (Fable 1). The rebase gives it a new hash, and the documented `cherry-pick -x` remedy is empty.

**Minor.**

- A hand deletion inside a local developer merge, of a file the phase lacks, is reverted (Fable 4).
- Taking a suggestion on a manifest line next to `version:` conflicts on the phase (Fable 5).

**Root causes.**

- A merged pull request is recognised only through a fourth field or ancestry, so independent squash merges are treated as open.
- Developer commits are matched only by hash and trailer, so a rebased one is not recognised.

## Verify: NOT VERIFIED at `df49f2906ccbdd6bcc56d3ab3ca3415fc1916df9`

An eighteenth fresh verifier covered `cef8140` plus its own check-file commit `df49f29`. That commit adds `MERGED` to the harness and the five fifth-Review findings as cases.

- **verify-s-stack.** Checks 1, 2, 3, 5 and 7 passed, and Tier 1 printed `all Tier 1 structural checks passed across 20 packages`. Checks 4 and 6 are PENDING. Check 8 passed for every file. `pr-handbook.md`'s scratch block printed 115 PASS and `0 failed` in 2 hours 11 minutes on a loaded machine, and the twelve-point cold read agreed.
- **The five new cases** fail at `d6067a3` and pass now.

Findings:

- **Significant: a regression from `cef8140`.** Patch-id matching ignores line numbers. A later developer commit with the same hunk as a taken one, elsewhere in the same file, matched it, so the round reverted the second change and pushed with `EQUAL`. At `d6067a3` the same history is reported.
- **Minor.** The handbook says an empty `MERGED` gives a false `FAIL`. It can also give a false `EQUAL` that hides a developer commit merged before the phase took it.

The phase session's fix: a patch-id match counts only when the trailer-named commit is not an ancestor of the candidate, which is true after GitHub's rebase and false for a twin on the same branch. It also adds the `MERGED` wording. The twin probe now reports `DEVELOPER-COMMITS` with nothing pushed, and the distinct-context control is unchanged.

## Known integration item for pr-handbook-d18

The phase session recording each pull request branch's pushed head, and passing it as `PUSHED` in the PR creator's brief, is not yet described in `handbooks/phase-session.md` or `references/status-and-messages.md`. Those files belong to phases that are Done, and the orchestrator has put the gap on its cross-handbook read-through list. It is a known integration item owned elsewhere, not a finding against pr-handbook.

## Verify 21, NOT VERIFIED at `d7f2260`

The verifier's check-file commits are `af0fc8b` and `d7f2260`, on top of code head `534c5ce`. The check block printed 128 PASS and `2 failed`, both from finding 1. Tier 1 passed across 20 packages. Every other verify-s-stack check passed, apart from the routes and launcher tests, which are pending and set no verdict.

- **Finding 1, significant on the common path.** A developer commits a suggestion on a stacked child. The phase takes it with `git cherry-pick -x`, and a round carries the pick. The carry skips it because the branch already holds the commit, so nothing is pushed, and `PUSHED` keeps the head from before the suggestion. After the parent's squash merge and GitHub's rebase, the recorded head lacks the developer's commit. The taken commit is then unaccounted. Every round prints `FAIL c.txt: child lacks phase commits ... Apply suggestions from code review;, so they need a pull request` and `NOT EQUAL`, with nothing pushed. The verifier's case is `taken developer commit, child rebased`.
- **Finding 2, fixed.** An empty `PUSHED` on a pushed branch stops in refresh and in prove, and never prints `EQUAL`.
- **Not a finding.** Recording pushed heads on the phase side is the known integration item owned elsewhere.

## Verify 22, NOT VERIFIED at `bce4cc8`

The verifier's check-file commit is `bce4cc8`, on top of code head `b0adfc6`. The gate was scoped to the phase's own diff since `d6067a3` under run decision `gate-cost`. Each check file's out-of-radius checks are listed with reasons in the verifier's report: routes, launcher tests, board, foundation cold reads, orchestrator-handbook, phase-handbooks and spec-planner-handbooks. In the radius:

- Primitives, lint, line budgets, isolation and `apm audit --ci` passed.
- Tier 1 passed across 20 packages.
- The STOP cold read passed, and so did a new cold read on which head to record after an `EQUAL` round that pushed nothing.
- The check block printed 129 PASS and `2 failed`, both from the finding below.

- **Finding, significant on the common path.** The history: the phase takes a developer commit `s` on a stack child as `p`, a round carries it without a push, the parent is squash-merged, and GitHub rebases the child. The first round after that proves `EQUAL` and records the rewritten head. Every round after it prints `FAIL c.txt: child lacks phase commits ... Apply suggestions from code review;, so they need a pull request` and `NOT EQUAL`. The cause: `p`'s trailer names `s`, and once the recorded head moves past the rebase, nothing reachable holds `s`. With the old push-only recording, the same case fails one round earlier. Two fixes have now failed on the same premise, that one recorded head per branch is enough.

## Verify 23, VERIFIED at `019ecea`

The verifier's check-file commit is `019ecea`, on top of code head `1223f1e`. The gate was scoped to the phase's own diff since `d6067a3` under run decision `gate-cost`, with orchestrator-handbook's check file left out, as the orchestrator ruled.

- verify-s-stack checks 1 to 5 passed. Tier 1 passed across 20 packages.
- The check block printed 137 PASS and `0 failed`. Its new cases fail on `b0adfc6`'s script.
- The STOP cold read and the new `PUSHED` cold read passed.
- Out of the radius: the launcher tests, foundation's and phase-handbooks' cold reads, spec-planner-handbooks, board's Rerun, and pr-handbook's two GitHub Evidence checks, each with its reason in the verifier's report.

Minor findings, not on the common path:

- After a failed push, the Report's "the proof's full output" includes the `RECORD` line, which step 5 says to leave out. The handbook does not say what else to do after a failed push.
- The STOP cold read inferred that a round pushes over a developer's amend. A rewritten branch is already documented as out of scope.

## Review 6, SIGNIFICANT at `019ecea`

Under run decision `gate-cost`, the first reviewer, on Opus, reviewed rather than waived, because the scope changes logic and agent instructions. The second reviewer, on Fable, then joined. The scope was the phase's own commits from `cef8140` to `019ecea` and the lockfile-only resolution of merge `3292aee`.

**Earlier probes.** Both reviewers ran the check file's scratch block: 137 PASS and `0 failed`. None of the fifth review's four significant findings still fails.

**Significant findings.** The phase session reran each command.

- **A developer's edit to a shared path on a rebased child is pushed over with `EQUAL`** (Opus 1, Fable 1). Both reviewers found it, in a parent, child and grandchild stack where the child and grandchild change one file. The developer commits a suggestion to that file on the child, before or after GitHub rebases the child onto `main`. The round prints `EQUAL` and pushes, and the suggestion is gone. Without a rebase the same commit gives `DEVELOPER-COMMITS`. The check for a rebased head skips shared paths. Commands: `/bin/bash /private/tmp/claude-501/-Users-samharris-projects-foundry--worktrees-s-stack-phase-pr-handbook/3c5c66d2-a34f-42e2-9aaa-69b896b4cb09/scratchpad/repro/r.sh`, and `bash /private/tmp/claude-501/-Users-samharris-projects-foundry--worktrees-s-stack-phase-pr-handbook/3c5c66d2-a34f-42e2-9aaa-69b896b4cb09/scratchpad/rev-aab0/mine/mk.sh p2.sh`.
- **A rebased child stays `NOT EQUAL` after the phase takes a developer commit and fixes the same file** (Fable 2). The check for a rebased head accepts a path only at the recorded head's or the phase tip's version, and the head holds neither. The documented remedy does not clear it. Command: `bash /private/tmp/claude-501/-Users-samharris-projects-foundry--worktrees-s-stack-phase-pr-handbook/3c5c66d2-a34f-42e2-9aaa-69b896b4cb09/scratchpad/rev-aab0/mine/mk.sh p3.sh`.

**Root cause.** For a rebased head, the developer check compares whole files instead of finding where the rebase ended and classifying the commits after it.

**Not counted.**

- `versioning.py check origin/main` reports `s-stack` at the base's version. The bump runs before the pull request, as `AGENTS.md` says.

## Verify 24 and 25

The twenty-fourth verifier was stopped before any verdict, when the developer decided against classifying a rewritten head (`pr-handbook-d23`). It left check-file commit `74c2411`.

### Verify 25, VERIFIED at `27d6f55`

The verifier's check-file commit is `27d6f55`, on top of code head `b366e26`. The gate was scoped under run decision `gate-cost` to the diff since `019ecea`: `29bf683`, `74c2411` and `b366e26`.

- The check block printed 145 PASS and `0 failed`. Every rebased child now asserts the rewrite STOP with nothing pushed and the developer's edits kept. The decision path proves `EQUAL` after the append and reports a later developer commit. The rebase-classification cases and the forge-keeps-the-tree Evidence check are dropped.
- Three cold reads passed: the STOP meanings, `PUSHED` and `RECORD`, and the new rewrite STOP.
- Tier 1 passed across 20 packages. verify-s-stack checks 1, 2, 3 and 5 also passed.
- Each check that did not run is outside the radius, and the verifier's report gives the reason for each.

Minor findings, off the common path:

- After a one-off rebuild the developer approved, which is the remedy for the shared-path and rewritten-dependency stops, the rebuilt head no longer descends from its recorded head. The next round therefore gives the rewrite STOP. Neither file says to record the rebuilt head. This is inferred and was not run.
- If the developer wrongly answers that a rewritten branch holds no edits, the next round can revert those edits. This is by design, because the answer is the developer's.

## Review 7, CLEAR at `27d6f55`

Under run decision `gate-cost`, the first reviewer, on Opus, reviewed instead of waiving, and the second reviewer, on Fable, then joined. The scope was `29bf683`, `74c2411`, `b366e26` and `27d6f55`, ending at phase branch commit `1d87f15`. Every commit after `27d6f55` in that range changes only `.foundry/`.

**Earlier probes.** Both reviewers reran the sixth review's repros. Every rebased history now gives the rewrite STOP, with nothing pushed and the developer's edit kept. The controls without a rebase still give `DEVELOPER-COMMITS`. The check block printed 145 PASS and `0 failed` for both reviewers.

**Findings.** Neither reviewer had any.

**Further probes.**
- Opus ran the decision path on a grandchild stack. With either the full or the short head sha appended, it proved `EQUAL`, and the next round changed nothing.
- Fable ran seven end-to-end histories of the decision path: shared paths, suggestions taken before and after the rebase, a later developer commit, and a force-pushed amend. Each gave the result the intent requires.
- Fable also ran a mutation of the check block. With the new ancestor check removed, it printed 132 PASS and failed the rewrite cases.
