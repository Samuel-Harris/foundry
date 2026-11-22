# Phase `default-stack` plan

This is the phase plan for `default-stack`, written by the session `s-stack-phase-default-stack` on 22 November 2026 against `s-stack-phase-default-stack` at `ac04bb4`, whose code equals `main` at `7747021`. The feature plan's entry for `default-stack` (`../README.md`, "Phase `default-stack`") sets the scope, the owned paths and the **Done when** list. This file adds detail and never contradicts it.

## The problem

Every other phase is Done, so `main` holds a complete s-stack package. Nothing installs it by default: `packages/default-stack/apm.yml` lists `../planning` and not `../s-stack`. Four documents and one test comment count the default stack's packages, and some counts were already wrong before this phase.

## The intended outcome

- A consumer that installs `default-stack` gains the `sam-mode` skill on every target, and loses no file it had before.
- `default-stack`'s lockfile, regenerated and relativised, resolves eleven packages: its nine direct dependencies plus `planning` and `deep-interview`, which it now reaches through s-stack. Every count below comes from that lockfile's distinct `repo_url` values, not from the feature plan, whose numbers were measured at `2c02803`.
- Tier 1's default-stack inventory check covers every package the meta-package deploys.
- The docs state the new graph, the corrected counts, and the latent audit drift that Experiment 1 found, with commands a reader can rerun.

## Commits and the pull request

One pull request, `feat(default-stack): install s-stack`, targeting `main` with no dependencies. Its commits, in order:

1. `feat(default-stack): depend on s-stack instead of planning`. `packages/default-stack/apm.yml` replaces `- path: ../planning` with `- path: ../s-stack`, keeping the other eight entries and their order. `packages/default-stack/apm.lock.yaml` is regenerated with `apm install --target cursor,claude,copilot` and relativised in the same commit.
2. `test(tier1): check every package default-stack deploys`. In `tests/structural/run-tier1.sh`, `DEFAULT_STACK_DEPLOYED` gains `s-stack` (the plan) and `p-stack` (decision `default-stack-d2`), the comment above it names the transitive packages and the count, and the inventory success line stops hard-coding "nine".
3. `docs: describe default-stack's s-stack edge`. `AGENTS.md`: the sentence on which packages `default-stack` reaches twice, and "its nine dependencies" stays true. `docs/COMPATIBILITY.md`: the `default-stack` row, the package count in the sentence after the table, and line 126's "nine dependency-bearing packages", which is six on `main`. `docs/DEPENDENCY-CONTRACTS.md`: the meta-package section's counts and tree, the dependency graph's `default-stack` edge, the doubly reached packages in the audit-defect section, and a new subsection that reproduces the relativised-lockfile drift and says why CI stays green.
3b. `docs: count s-stack in the acceptance doc and default-stack's README`. Added by decision `default-stack-d3`, the orchestrator's answer to `default-stack-r1`: `tests/acceptance.md` lines 41 and 51, and the "Depends on" list in `packages/default-stack/README.md`, which still named `planning` and lacked `p-stack`.
4. `chore(s-stack): regenerate generated files`. `python3 scripts/versioning.py bump` against `origin/main` (decision `default-stack-d1`). It touches only `version:` lines and lockfiles, so it moves no code head.

The verifier then commits `tests/s-stack/verify-s-stack/checks/default-stack.md`. It goes with the work it checks, in the same pull request.

## Verification

The feature plan's **Done when** list, with these specifics:

- Tier 1 across 20 packages, with s-stack's and p-stack's files in each target's scratch-consumer inventory.
- The consumer audit: install `packages/default-stack` by path into an empty `mktemp -d` directory on all three targets and run `apm audit --ci` there.
- The strict route check: every `handbooks/<role>.md` code span in `SKILL.md` names a file that exists, and a missing one fails.
- Additions only: the deployed file list of a scratch consumer installed from `default-stack` at `main` (`7747021`) before this phase, against one installed from the phase branch. Both lists go into the evidence file. The baseline was taken at the start of the phase: 374 files, `apm audit --ci` passing all 10 checks.
- The drift reproduction in `docs/DEPENDENCY-CONTRACTS.md`, rerun as written.

After commit 4, `quick-review` runs once on the whole diff, which is one pull request, and its findings are fixed before Verify.

Rollback is the feature plan's: revert the pull request on `main` and bump `default-stack` again.

## Decisions

- `default-stack-d1`, two-way. The phase branch runs `versioning.py bump` against `origin/main`, contrary to C7's rule that no phase branch bumps. C7 exists so that parallel phases do not pick the same version, and this phase runs alone. The developer's brief asks for the bump, and the **Done when** list checks it. The PR creator's regenerate commit then finds `default-stack` already ahead and changes nothing it does not need to.
- `default-stack-d2`, two-way. `DEFAULT_STACK_DEPLOYED` also gains `p-stack`. #70 made `p-stack` a direct dependency of `default-stack` without adding it to the inventory list, so Tier 1 has not checked p-stack's files in the default-stack consumer since. The file is this phase's, and the comment's count must match the lockfile.

## Non-goals

- No change to s-stack, p-stack or any other package's manifest. Only `default-stack`'s lockfile and version change.
- No change to the root `apm.yml`. `default-stack` stays unlisted, and s-stack is already listed.
