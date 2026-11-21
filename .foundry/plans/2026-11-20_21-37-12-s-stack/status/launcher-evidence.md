# Phase launcher evidence

## Verify, code head `c1ec2d3d85a9f5f9535101e63ac9956ebaa32371`, VERIFIED

A fresh verifier ran on 21 November 2026. The behavioural checks and their results are in `tests/s-stack/verify-s-stack/checks/launcher.md` at that head.

- The verification skill passed in full. That covers primitives (94 valid), the root manifest (`12 listed, 19 reached`), Markdown lint, line budgets and package isolation. The launcher suite ran 35 tests, all OK. Tier 1 printed `all Tier 1 structural checks passed across 20 packages`. The foundation cold reads passed. Handbook routes were pending, as expected.
- Nine mutations of `launch.sh` each failed at least one named test.
- Live check, with the real `claude` and the real `workmux` on a private tmux server in a scratch repository. The phase pane showed `Unknown command: /sam-mode` with the arguments `phase feature=probe phase=live ...`, because `sam-mode` is not deployed there. So the first prompt's first words were `/sam-mode phase`. A second launch printed `alive probe-phase-live pane=%1`, and the panes were unchanged. On `/exit`, Claude printed the conversation id that the launcher had stored.
- Minor gaps the verifier recorded. The real `sam-mode` did not load in the scratch repository. A real `--resume` relaunch was not run, so resume is proven by the unit suite and the `/exit` id. Roadmap `coordination.md` and C4 still say restarts use `claude --continue`, and neither lists `--print-window`, `--close`, `--remove` or exit 5. That text is owned outside this phase.

This verdict is superseded by the merge of `s-stack-package` at `4739703`, which brings new files and so a new code head.
