# Phase `pr-handbook` evidence

## Verify: NOT VERIFIED at `a42cd47ca1eb9cbcfc5dc51e6b608b4864b31d22`

A fresh verifier wrote `tests/s-stack/verify-s-stack/checks/pr-handbook.md` and committed it alone at `a42cd47`. That file extracts the handbook's parameter block, carry loop, proof and merge procedure at run time and runs 14 scratch-repository cases. The verifier then ran `verify-s-stack` in full.

- Checks 1, 2, 3, 5 and 7 passed. Tier 1 printed `all Tier 1 structural checks passed across 20 packages`, outside the sandbox with the pinned 0.32.0 CLI. Checks 4 and 6 were PENDING, as expected while other phases are in flight.
- Check 8 failed. `foundation.md`'s three cold reads and its C2 comparison passed. `pr-handbook.md` passed 12 cases and failed 2.
- Every **Done when** case gave its expected result, and so did the `quick-review` round's cases.
- The two failures are one defect. `git diff-tree --quiet` without `-r` compares only top-level entries, so a commit that changes only `pkg/apm.lock.yaml` (and `.foundry/`) counts as non-empty. The carry loop then feeds `git apply` an empty patch and exits 1, and the proof prints `does not apply`. It is at handbook lines 63 and 112, introduced in `589411b`. The phase session reproduced it independently: without `-r` the check exits 1, with `-r` 0.
