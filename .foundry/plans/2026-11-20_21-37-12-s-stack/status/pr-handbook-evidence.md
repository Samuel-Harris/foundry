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
