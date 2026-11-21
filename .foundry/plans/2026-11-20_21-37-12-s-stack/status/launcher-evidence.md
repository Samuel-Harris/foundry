# Phase launcher evidence

## Verify, code head `c1ec2d3d85a9f5f9535101e63ac9956ebaa32371`, VERIFIED

A fresh verifier ran on 21 November 2026. The behavioural checks and their results are in `tests/s-stack/verify-s-stack/checks/launcher.md` at that head.

- The verification skill passed in full. That covers primitives (94 valid), the root manifest (`12 listed, 19 reached`), Markdown lint, line budgets and package isolation. The launcher suite ran 35 tests, all OK. Tier 1 printed `all Tier 1 structural checks passed across 20 packages`. The foundation cold reads passed. Handbook routes were pending, as expected.
- Nine mutations of `launch.sh` each failed at least one named test.
- Live check, with the real `claude` and the real `workmux` on a private tmux server in a scratch repository. The phase pane showed `Unknown command: /sam-mode` with the arguments `phase feature=probe phase=live ...`, because `sam-mode` is not deployed there. So the first prompt's first words were `/sam-mode phase`. A second launch printed `alive probe-phase-live pane=%1`, and the panes were unchanged. On `/exit`, Claude printed the conversation id that the launcher had stored.
- Minor gaps the verifier recorded. The real `sam-mode` did not load in the scratch repository. A real `--resume` relaunch was not run, so resume is proven by the unit suite and the `/exit` id. Roadmap `coordination.md` and C4 still say restarts use `claude --continue`, and neither lists `--print-window`, `--close`, `--remove` or exit 5. That text is owned outside this phase.

This verdict is superseded by the merge of `s-stack-package` at `4739703`, which brings new files and so a new code head.

## Verify, code head `2726205c5a71584501fb366f588125c64af9cfbd`, VERIFIED

A second fresh verifier ran at the merged head on 21 November 2026, in full. The results are recorded under "Rerun at `2ecc9f0`" in `tests/s-stack/verify-s-stack/checks/launcher.md`.

- The verification skill passed in full, including Tier 1 across 20 packages and the cold reads of the newly merged `planner.md` and `spec-writer.md`. The suite ran 35 tests, all OK.
- Four mutations each failed named tests.
- Every launcher call written in `SKILL.md` and `spec-writer.md` was run against the launcher with stubs, and each was accepted.
- Live check with the real `claude` and `workmux`. The first prompt began `/sam-mode phase`, and the second launch printed `alive`. After `/exit`, a relaunch ran `claude --name probe-phase-live --resume <the stored id>` and showed the earlier conversation.
- Minor findings, recorded and not fixed, under the orchestrator's minor-findings rule:
  - A pane left at its shell after `claude` exits is not reused. A relaunch splits a new pane, and `--close` does not clear a dead pane.
  - `SKILL.md`'s `start` form covers only the first spec writer. A restart needs `--window`, as C4 says.
  - The real `sam-mode` did not load in the scratch repository.
