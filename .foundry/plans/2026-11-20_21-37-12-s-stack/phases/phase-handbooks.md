# Phase `phase-handbooks` plan

This is the phase plan for `phase-handbooks`, written by the phase session `s-stack-phase-phase-handbooks` on 21 November 2026 against `s-stack-package` at `42c54ee`. The feature plan's entry for `phase-handbooks` (`../README.md`, "Phase `phase-handbooks`") sets the scope, the owned paths and the **Done when** list. This file adds the implementation detail. Where the two disagree, the feature plan wins and the session tells the orchestrator.

## The problem

`SKILL.md` routes a phase session to `handbooks/phase-session.md`, and the phase session points its verifier and reviewers at `handbooks/verifier.md` and `handbooks/reviewer.md`. None of the three exists. Without them a phase session has to rebuild the gate chain from the roadmap, which is the November run's first problem: the workflow lived only in transcripts, agent review was optional, and no phase opened a pull request early.

## The intended outcome

After this phase, on the phase branch:

- A phase session that reads `phase-session.md` knows, in order, how to take its phase from Plan to Done: write the phase plan, implement along the planned pull request split with `quick-review` on each layer, merge the orchestrator branch before Verify, run the Verify gate and then the Review gate with fresh subagents, hand the split to a PR creator, commit its status file and message the orchestrator at each change of state, run fix rounds, and move back to Plan or Spec when told. It knows what it reads again after a restart and what it does with a direct instruction from the developer.
- A fresh verifier that reads `verifier.md` knows its inputs, which p-stack verification skills it reads and runs, the one check file it writes, how it commits that file, and how it chooses between VERIFIED, NOT VERIFIED and INCONCLUSIVE. It does not return before every subagent it started has reported.
- `reviewer.md` holds the brief for the adversaries of p-stack's `interrogate` skill, and the phase session's part of the Review gate: the scope, how the intent is stated without a plan, what counts as a significant finding, and the verdict.
- Each handbook is 200 lines or fewer and passes `validate_primitives.py`, `markdownlint-cli2` and the verification skill.

## Non-goals and boundaries

- No edit outside the owned paths: the three handbooks, `tests/s-stack/verify-s-stack/checks/phase-handbooks.md`, and the generated `packages/s-stack/apm.lock.yaml`.
- No change to `SKILL.md` or `references/status-and-messages.md`, which `foundation` owns. The handbooks point to them and restate nothing they say. If a handbook needs a fact they lack, the session sends a decision request.
- No PR creator detail. `pr-creator.md` belongs to `pr-handbook`. `phase-session.md` says when to start the PR creator and what to give it, and nothing about the split, `gh stack` or the equality proof.
- No rule specific to this run. The generated-files code-head exemption and the generated-only fix round are this run's decisions (feature plan C7). The handbooks say only "when the feature plan names generated paths" or "when the feature plan defines a generated-only fix round", and point there.
- No workmux, tmux or `claude` command line. Only `launch.sh` holds those (feature plan C4).
- No `versioning.py bump` on the phase branch (feature plan C7).

## Design

All three files live under `packages/s-stack/.apm/skills/sam-mode/handbooks/`. They follow `SKILL.md`'s style: one paragraph per line, short declarative sentences, British English, tables for mappings. Paths inside `sam-mode` are written relative to the skill's directory in code spans, except the existing reference file, which gets a relative link. Other packages' skills are named in words. p-stack's `interrogate`, `create-verification-skill`, `maintain-verification-skill`, `create-formal-verification-skill` and `maintain-formal-verification-skill` all set `disable-model-invocation: true`, so each handbook tells the agent to read `../<skill>/SKILL.md` from the `sam-mode` directory, as `SKILL.md` does for `poteto-mode`. Review's `quick-review` can be invoked as a skill.

### `phase-session.md`

Sections, in order:

1. **Your job.** One phase from Plan to Done. You orchestrate. Delegates write code inside the owned paths. You alone change the phase's state.
2. **Read first.** The roadmap `README.md` and the parts it routes a phase session to, `run-decisions.md`, the feature plan's rules for every phase, its contracts and your phase's entry. The reference file for the status header and messages.
3. **Start.** Commit the status file in state Plan before anything else, then send `started`.
4. **Plan.** Write the phase plan at `.foundry/plans/<id>/phases/<phase>.md` against the code as it stands, under the plan handoff standard. It names the pull request split before code exists. Commit it, then move to Implement.
5. **Implement.** Commit along the planned split. Never mix `.foundry/` with other files. Run `quick-review` on each planned pull request layer and fix its findings before starting the next. Regenerate generated files the way the feature plan says. You may run the verification skill at any time.
6. **Merge the orchestrator branch before Verify.** Use the feature plan's merge procedure when it names one. Resolve conflicts only in owned paths. A conflict in another phase's hand-written file is a `blocked` message. The merge is a new code head.
7. **The code head and verdicts.** The command lives in the reference file. Add an exclude clause for each generated path the feature plan names. A verdict covers one code head. After a fix, verification runs again in full, and review covers the commits since the last reviewed code head.
8. **Verify.** Move to Verify. Start a fresh verifier with a brief that names `handbooks/verifier.md`, the roadmap, the feature plan, the phase plan, both branches and the verification skill. Wait for its report. Record the verdict in the status file and its evidence in `<phase>-evidence.md`. VERIFIED moves to Review. NOT VERIFIED and INCONCLUSIVE move back to Implement.
9. **Review.** Move to Review. Run the gate as `handbooks/reviewer.md` says. CLEAR moves to PR. SIGNIFICANT moves back to Implement.
10. **PR.** Start a PR creator with `handbooks/pr-creator.md`, the roadmap, the feature plan and the phase plan. Record each pull request in the status file and send `prs-open`. Stay in PR until every pull request has merged. The orchestrator moves nothing; Done is written when the orchestrator reports the last merge, or by a later session.
11. **Messages from the orchestrator.** A table: `answer`, `instruction`, `merge-orchestrator-branch`, `fix-round`, `restack`, `move-back`, `stop`, each with the action.
12. **Fix rounds.** The four steps of roadmap `workflow.md`. A generated-only fix round, when the feature plan defines one.
13. **Moving back to Plan or Spec.** Commit what you have, stop the work the change could invalidate, record the new state, and wait or re-plan.
14. **Decisions and the developer.** Doors per `SKILL.md`. A direct instruction from the developer: follow it, record a decision when it changes one, and send `instruction` when it changes the phase's scope or a recorded decision.
15. **After a restart.** Read again the phase plan, the status file and the phase branch, including uncommitted changes and commits after the recorded code head. Continue from the recorded state. A gate whose verdict is not in the status file runs again.

### `verifier.md`

1. **Who you are.** A fresh subagent that has not seen the implementation. You edit verification code and nothing else. You never fix product code.
2. **Inputs.** The brief gives the roadmap, the feature plan, the phase plan, the phase branch, the orchestrator branch and the verification skill's path. The phase diff is `git diff <orchestrator branch>...<phase branch> -- . ':(exclude).foundry'`.
3. **Decide the kind.** Behavioural by default: drive the real code the way its user does. Formal, through `create-formal-verification-skill` or `maintain-formal-verification-skill`, where the phase adds concurrency, retries, a state machine or a parser that tests reach poorly. None is rare, and the report states the reason.
4. **The verification skill.** If none covers the feature, create it with `create-verification-skill`. If it lacks a path the phase needs, update it within `maintain-verification-skill`'s edit scope and proof rules, without opening a pull request. Prose is checked by cold reads: a fresh subagent gets only the file and a scenario, and its answer is compared with an expected answer written down first.
5. **The check file.** `checks/<phase>.md` beside the verification skill's `SKILL.md`. Only this phase writes it. `## Rerun` for cheap, repeatable, local checks. `## Evidence` for one-off checks with their results. Commit it alone, outside `.foundry/`, before running anything; it becomes the code head. Recommit and rerun everything after any later change.
6. **Run.** The whole verification skill, then the phase's **Done when** list, against the phase branch after its merge of the orchestrator branch.
7. **Wait.** Do not return until every subagent you started has reported. Nested subagents run in the background and can outlive their parent's report.
8. **Verdict.** VERIFIED when every check ran and passed. NOT VERIFIED when a check ran and failed. INCONCLUSIVE when nothing failed but a check could not run. INCONCLUSIVE is not a pass.
9. **Report.** The verdict, the code head it covers, and for each check the command, its output and pass or fail. The verifier writes nothing under `.foundry/`. The phase session records the verdict.

### `reviewer.md`

Two parts.

**For the phase session.** Run p-stack's `interrogate` skill by reading `../interrogate/SKILL.md`. The scope is the phase diff, or after a fix the commits since the last reviewed code head, always without `.foundry/`. State the intent from the commit messages and the code alone, never from the roadmap or a plan. Add the brief below to each adversary's brief. Classify each verified finding. The verdict is SIGNIFICANT when any verified finding is significant, else CLEAR, and names the code head reviewed. Record findings that are not significant in the evidence file.

**For each reviewer.** You get the diff and the repository. Do not read `.foundry/`, a roadmap, a plan or the implementer's notes; the code must explain itself. A finding is significant when a run shows that the change breaks its intent, a documented contract, or the repository's own checks: a crash or wrong result on valid input, data loss, a security hole, a broken build, test or check, or a change that a reader of the diff cannot tell was intended. Not significant: naming, style, structure preferences, and risks that need a future change to matter. Interrogate already drops what was not run.

### Decisions taken in this plan

- `phase-handbooks-d1`, two-way. `verifier.md` makes `checks/<phase>.md` beside the verification skill's `SKILL.md`, with `## Rerun` and `## Evidence` sections, the general s-stack rule. Feature plan C6 sets it for this run, and roadmap `roles.md` requires a file only the phase owns without naming it. One rule lets the orchestrator's merged-branch check rerun every phase's checks the same way.
- `phase-handbooks-d2`, two-way. One pull request. The three handbooks are one gate chain that refers to itself, and a reviewer cannot judge the phase session's gate steps without the gate handbooks. About 500 hand-written lines.
- `phase-handbooks-d3`, two-way. The reviewers' intent comes from commit messages and the code alone. `interrogate` would otherwise state it from the user's message, which for a phase session is the plan, and the roadmap forbids the reviewers any plan.

## Pull requests

One draft pull request, depending on each `foundation` pull request still open when the PR creator runs, with the base the feature plan's "Pull request rules for this run" gives. It carries the three handbooks and `checks/phase-handbooks.md`, and ends with the regenerate commit of C7.

Commits on the phase branch, in order. Each commit that changes `.apm/` also carries the regenerated, relativised `packages/s-stack/apm.lock.yaml`, because the pre-commit hook refuses a stale lockfile.

1. `docs(s-stack): add the verifier handbook`
2. `docs(s-stack): add the reviewer handbook`
3. `docs(s-stack): add the phase session handbook`
4. Fixes from `quick-review` on the whole layer.
5. The verifier's `test(s-stack): add the phase-handbooks checks`.

## Execution order

1. Commit this plan and the status file (state Plan), then the status file at Implement. Send `started` and `state`.
2. Create `.venv-apm/` as feature plan rule 7 says.
3. Write each handbook, regenerate the lockfile with `apm install --target cursor,claude,copilot` in `packages/s-stack`, relativise it, and commit, in the order above.
4. Run `validate_primitives.py`, `markdownlint-cli2` on the new files, and `wc -l`.
5. Run `quick-review` on the diff and fix its findings.
6. Merge `s-stack-package` with C7's procedure.
7. Verify gate with a fresh verifier, then Review gate with `interrogate`, then the PR creator, each recorded in the status file and messaged to the orchestrator.

## Verification

The feature plan's **Done when** list for this phase is the standard. The verifier writes each cold-read scenario with its expected answer into `checks/phase-handbooks.md` under `## Rerun`:

1. `phase-session.md` and a status file at Verify whose newest verdict names an older code head. Expected: the verdict does not cover the new code head, and verification runs again in full.
2. `verifier.md` and a placeholder diff. Expected: it names `checks/<phase>.md` beside the verification skill's `SKILL.md`, and returns INCONCLUSIVE for a check that could not run.
3. `reviewer.md` and a placeholder diff. Expected: it will not read `.foundry/` or any plan, a crash on valid input is significant, and a naming preference is not.
4. `phase-session.md`. Expected: after a restart it reads the phase plan, the status file and the phase branch, and a direct instruction from the developer that changes scope is followed and reported to the orchestrator with an `instruction` message.

Plus `wc -l` at 200 or fewer for each handbook, and the whole verification skill.
