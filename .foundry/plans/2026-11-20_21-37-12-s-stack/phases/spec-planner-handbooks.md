# Phase `spec-planner-handbooks` plan

This is the phase plan for `spec-planner-handbooks`, written by the phase session `s-stack-phase-spec-planner-handbooks` on 21 November 2026 against `s-stack-package` at `dcdda28`. The feature plan's entry for this phase (`../README.md`, "Phase `spec-planner-handbooks`") sets the scope, the owned paths and the **Done when** list. This file adds the implementation detail. Where the two disagree, the feature plan wins and the session tells the orchestrator.

## The problem

`SKILL.md` routes the `spec` role to `handbooks/spec-writer.md` and the `planner` role to `handbooks/planner.md`. Neither file exists, so a session started with `/sam-mode spec ...` or `/sam-mode planner ...` finds no handbook and falls back on whatever the roadmap happens to say. The November run showed what that costs: the protocol was rebuilt by hand each time. These two roles open every feature. The spec writer produces the document everything else depends on, and the planner produces the phase split, the owned paths and the contracts that let phases run in parallel.

## The intended outcome

After this phase, on the phase branch:

- `packages/s-stack/.apm/skills/sam-mode/handbooks/spec-writer.md` tells a spec writer session, new or update, what it owns, how it interviews, what goes in a roadmap, how it records decisions, how it hands over, and what it reads again after a restart.
- `packages/s-stack/.apm/skills/sam-mode/handbooks/planner.md` tells a planner session what the feature plan must hold, how it settles open questions, how it shapes phases for parallel work, what the other handbooks take from the plan, how it hands over, and what it reads again after a restart.
- `tests/s-stack/verify-s-stack/checks/spec-planner-handbooks.md` holds the two cold-read scenarios with their expected answers in `## Rerun`. The verifier writes it.
- Each handbook is at most 200 lines, passes `markdownlint-cli2`, and has no relative link that leaves `packages/s-stack`.

## Non-goals and boundaries

- No change to `SKILL.md`, the reference file or any other handbook. Facts that live there are pointed to, not restated (feature plan rule 9, C1 "Each fact has one home").
- No workmux, tmux or `claude` command line in either handbook. The launcher is called only through the C4 interface.
- No relative link into another package. Other packages' skills are named in words, for example "the `deep-interview` package's `deep-interview` skill" or "p-stack's Prototype playbook" (feature plan rule 8).
- No `versioning.py bump` on the phase branch (C7). The lockfile is regenerated only if `.apm/` changes need it, and the regenerate commit is the PR creator's.
- No pointer from `planner.md` to this run's feature plan as a worked example. That file lives under `.foundry/` on Foundry's orchestrator branch and never reaches a consuming repository, so a pointer would be dead text there. The feature plan says the handbook *may* point to it, so leaving it out is within scope. Recorded as decision `spec-planner-handbooks-d1`.
- Nothing about this run's own exceptions (option B code-head exemption, `s-stack-package` branch name). Handbooks state general behaviour.

## Design

Both handbooks share one shape, so a reader of one can navigate the other. Each section states only what s-stack adds and points to the owner of every other rule.

| Section | Holds |
| --- | --- |
| Title and one paragraph | What the role is for, its inputs and the one thing it hands over |
| What you own | The files it writes, the branch and the paths the branch may change. Everything else is read-only. |
| Steps | Numbered, in the order the session runs them |
| Messages | Which kinds from the reference file it sends, and when |
| After a restart | What it reads again |

### `handbooks/spec-writer.md`

Sources: roadmap `roles.md` "Spec writer", `workflow.md` "Shared artefacts", "Roadmap updates", "One-way and two-way doors", `coordination.md` "Session names", "Messages", "Restarts", and `README.md` "What is still open" item 3 (public repositories).

Content, in order:

1. **Role.** It turns the developer's idea into a feature roadmap, the specification every other session reads. It is one of the developer's two contact points, so it asks the developer directly and sends no decision request.
2. **Two modes**, chosen by the first prompt. `update=-`: a new roadmap, in the feature worktree on the orchestrator branch `<feature>`, session name `<feature>-spec`. `update=<n>`: a roadmap update, in its own worktree cut from the orchestrator branch, session name `<feature>-spec-<n>`.
3. **What you own.** Files under `.foundry/feature-roadmaps/<id>/`, except `run-decisions.md`, which belongs to the orchestrator. An update's branch changes nothing outside `.foundry/feature-roadmaps/`.
4. **New roadmap steps.**
   1. Gather context with read-only subagents and keep their conclusions.
   2. Interview with the `deep-interview` skill from the `deep-interview` package. The roadmap takes the place of that skill's crystallised spec file, so write the result into the roadmap directory instead of `.foundry/interviews/`.
   3. Ask the developer about every one-way door, and about every ambiguity in the specification, even when the ambiguity is a two-way door. A spec writer never decides an ambiguity itself.
   4. Record every answer in the roadmap's `decisions.md` with its door type, who decided and why. The roadmap's two decision files hold feature-wide decisions; phase-only decisions go in status files later.
   5. Write the roadmap at `.foundry/feature-roadmaps/<id>/`, `<date-time>` from `date '+%Y-%m-%d_%H-%M-%S'`. It holds the problems, the intended behaviour, the significant architectural decisions and the key constraints, and leaves out implementation detail and implementation order. `README.md` is the entry point and routes to the other files so a reader loads only what they need. Open questions that need an experiment go in a list for the planner.
   6. Before the first commit, check whether the repository is public. In a public repository, keep the names of private repositories, their features and their pages out of every file.
   7. Commit the roadmap on the orchestrator branch as each part is written, files under `.foundry/` only.
   8. Wait for the developer's review and make the changes they ask for. Each change of decision goes into `decisions.md`.
   9. On the developer's explicit approval, get this session's own window by running `<this skill's directory>/scripts/launch.sh --print-window` from the main session, not a subagent, and reading `window=<window id>` from its output. Then start the orchestrator through the launcher: `<this skill's directory>/scripts/launch.sh --feature <feature> --role orchestrator --window <window id>`. Report the launcher's output line to the developer. The first spec writer then stops working, so the feature worktree has one live session; the developer can close its pane.
5. **Roadmap update steps.** Read the approved roadmap and `run-decisions.md`. Interview about the change the same way, asking about every one-way door and ambiguity. Edit the roadmap on the update branch only; the sessions at work keep reading the approved one. Fold the run decisions that the update covers into the main text, never editing `run-decisions.md`, and name the folded rows in the message so the orchestrator can retire them. When the developer approves, commit and send a `roadmap-update` message with the branch, the commit, what changed and which behaviour the change affects. The orchestrator merges the branch.
6. **Messages.** A new-roadmap spec writer sends none: it starts the orchestrator itself. An update spec writer sends `started` and `roadmap-update`, and `blocked` when it waits on something other than the developer. Kinds and forms: the reference file.
7. **After a restart.** Read the committed roadmap files on your branch, and `run-decisions.md` for an update. The launcher resumes the conversation, so an interview continues where it stopped.

### `handbooks/planner.md`

Sources: roadmap `roles.md` "Planner", `workflow.md` "Shared artefacts" (feature plan), "Pull requests", `coordination.md` "Messages", "Parallel work", "Restarts", `package.md` (experiments), the plan handoff standard in the `planning` package, and the C7 duties that the orchestrator and PR creator handbooks take from the feature plan.

Content, in order:

1. **Role.** It receives the approved roadmap and writes the feature plan, which splits the work into phases that one Claude Code session each can implement, as many as possible in parallel.
2. **What you own.** `.foundry/plans/<id>/README.md` only, on the branch `<feature>-planner` in its own worktree, cut from the orchestrator branch. The branch changes nothing outside `.foundry/plans/`. Prototypes live in throwaway worktrees, branches or scratch repositories and are never pushed or merged.
3. **Steps.**
   1. Read the roadmap's `README.md` and `run-decisions.md` together, then the files the README routes to.
   2. Explore the code with subagents. Keep conclusions with the file and line they came from.
   3. List the open questions: the roadmap's experiments for the planner, plus any fact the plan would otherwise guess. Settle each by experiment with p-stack's Prototype playbook, in a throwaway worktree or scratch repository, never against state the developer is using such as their tmux server or a shared local stack. Record each as question, answer, how it was measured and where the evidence lives.
   4. Shape the phases (next section).
   5. Write the plan to the plan handoff standard, which the `planning` package applies to every Markdown file under `.foundry/plans/`. A "Who reads what" table at the top routes each reader (orchestrator, phase session, verifier, PR creator) to the sections they need.
   6. Send every one-way door to the orchestrator as a decision request and continue with the work it does not affect. Decide two-way doors and record them in a "Decisions taken by the planner" table with their reasons; raise one when it is architectural, nuanced or not obvious.
   7. Commit, files under `.foundry/plans/` only, and send `done-planning` with the branch and commit. The orchestrator merges it.
4. **Shaping the phases.**
   - Each phase fits one session. Group work that shares context.
   - Give each phase owned paths. No two phases that can run at the same time own the same file. A file that many phases touch (a lockfile, a version line, a shared index) is generated and owned by none, regenerated by a named command.
   - Name each exclusive resource, such as a port, a local stack or a GPU, and the phases that need it. Name shared resources that are not exclusive and say why.
   - Make the feature's verification skill the first phase when no existing skill covers the feature. Give every phase its own check file in that skill, so no two phases edit one verification file.
   - Read the pull request rules before drawing dependencies: the PR creator's handbook, and `SKILL.md` for drafts and branches. A pull request stacks cleanly on one parent only, so a phase that depends on two open phases gets a pull request that carries both diffs.
   - Write the contracts between phases (interfaces, file layout, data schemas, command lines) so a phase builds against a neighbour that does not exist yet. A phase that needs to change a contract sends a decision request.
5. **What each phase entry holds.** Scope, the phases it depends on, owned paths, paths it must not touch, exclusive resources, planned pull requests with their dependencies, and a **Done when** checklist naming the evidence that proves it.
6. **What other handbooks take from the plan.** A table:

   | Reader | Takes from the plan |
   | --- | --- |
   | Every phase session | Generated paths whose commits move no code head, if any (the reference file's code-head rule allows them) |
   | Orchestrator | Start conditions and merge order, the exclusive resources, the repository's check command for merges and the merged-branch check |
   | PR creator | The generated paths, the regenerate command and the regenerate commit's subject |
   | Verifier | The verification skill's path and each phase's check file |

   When the repository has no generated files, the plan says so.
7. **Messages.** `started`, `decision-request`, `blocked`, `done-planning`. Kinds and forms: the reference file.
8. **When you are started again.** The orchestrator restarts the planner when a roadmap update or a discovery changes the phases. Edit only the entries that change and say in `done-planning` which phases changed, because each one moves back to Plan.
9. **After a restart.** Read the committed feature plan on your branch and your recorded experiment results. Throwaway worktrees may be gone; re-run an experiment rather than trust an unrecorded result.

## Settled interface question

The spec writer passes `--window` when it starts the orchestrator, and C4 bars any handbook from naming a tmux command. The orchestrator settled request `launcher-r1` as option A on 21 November: C4 gains `launch.sh --print-window`, which takes no other flag, prints `window=<window id>` for the caller's pane and exits 0, exits 1 when the caller is not in tmux and 3 when tmux is missing. It must run from a main session, because a subagent can lack the pane. Recorded on this phase as `spec-planner-handbooks-d2`.

## Blast radius

| Path | Change |
| --- | --- |
| `packages/s-stack/.apm/skills/sam-mode/handbooks/spec-writer.md` | New |
| `packages/s-stack/.apm/skills/sam-mode/handbooks/planner.md` | New |
| `packages/s-stack/apm.lock.yaml` | Regenerated, about 22 lines for each new file (feature plan Blast radius) |
| `tests/s-stack/verify-s-stack/checks/spec-planner-handbooks.md` | New, written by the verifier |

Nothing reads the handbooks programmatically. The verification skill's check 4 turns the two routes from PENDING to present.

## Execution order

1. Write `spec-writer.md`. Lint it and count its lines. Commit it with the regenerated lockfile as `feat(s-stack): add the spec writer handbook`.
2. Write `planner.md`. Lint, count, regenerate, commit as `feat(s-stack): add the planner handbook`.
3. Run `quick-review` on the phase diff (one layer, one pull request) and fix its findings in a further commit.
4. Commit the status file at Implement after step 1 starts, and send `state`.
5. Merge `s-stack-package` into the phase branch with the C7 procedure. Commit the status file at Verify and send `state`.
6. Verify gate, with a fresh verifier subagent (below).
7. Review gate, with p-stack's `interrogate` skill and the reviewer brief from roadmap `roles.md`.
8. PR creator subagent. Then status at PR, `prs-open`.

## Verification

Commands for the session's own checks while it builds:

```bash
npx --yes markdownlint-cli2@0.14.0 "packages/s-stack/**/*.md"
wc -l packages/s-stack/.apm/skills/sam-mode/handbooks/*.md
PATH="$PWD/.venv-apm/bin:$PATH" python3 tests/structural/validate_primitives.py
```

The verifier writes `checks/spec-planner-handbooks.md` with these two cold reads in `## Rerun`, each run by a fresh subagent given only the named file and the scenario:

1. **Planner.** Given `planner.md` and a two-paragraph placeholder roadmap for a feature with two independent parts and one part that needs both, the subagent produces a phase table. Expected: every phase has scope, depends on, owned paths, exclusive resources, planned pull requests and the evidence that proves it done; no two phases that can run together share an owned path; the third phase depends on both others.
2. **Spec writer.** Given `spec-writer.md` and a placeholder idea that hides one one-way door (a migration that drops a column) and one ambiguity (whether an export is daily or on demand), the subagent says it asks the developer about both, records each answer in the roadmap's `decisions.md` with its door type, and starts the orchestrator through the launcher only after the developer approves the roadmap.

The verifier then runs the verification skill and the feature plan's **Done when** list, and returns VERIFIED, NOT VERIFIED or INCONCLUSIVE.

## Pull requests

One pull request, holding both handbook commits and the check file commit. It depends on each `foundation` pull request still open when the PR creator runs (81 and 82 at the time of writing), and its base follows the feature plan's "Pull request rules for this run".
