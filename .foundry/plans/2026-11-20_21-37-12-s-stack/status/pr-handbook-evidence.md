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
