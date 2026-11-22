# Phase `orchestrator-handbook` plan

This is the phase plan for `orchestrator-handbook`, written by the phase session `s-stack-phase-orchestrator-handbook` on 21 November 2026 against `s-stack-package` at `42c54ee`. The feature plan's entry for this phase (`../README.md`, "Phase `orchestrator-handbook`") sets the scope, the owned paths and the **Done when** list. This file adds the implementation detail. Where the two disagree, the feature plan wins and the session tells the orchestrator.

## The problem

`SKILL.md` routes the `orchestrator` role to `handbooks/orchestrator.md`, which does not exist. Without it, an orchestrator started by the launcher has no tick checklist, no merge rules and no instructions for the two pages. The November run showed what that costs: the developer asked four times for status pages to be updated, and designed the loop prompt by hand.

## The intended outcome

After this phase, `packages/s-stack/.apm/skills/sam-mode/handbooks/orchestrator.md` exists, at most 200 lines. An orchestrator session that reads it, together with `SKILL.md` and `references/status-and-messages.md`, can do these things without asking:

- Start: record its window in the tracker, arm the tick, publish the status board from the template and the first architecture page, and start the planner through the launcher.
- Run one tick: reconcile from files and the forge, start ready phases, merge eligible phases, unblock, record, publish and report.
- Decide whether a phase may merge, from the status header's verdicts and the code head.
- Merge the default branch into the orchestrator branch with the stop-before-commit procedure, resolving only conflicts confined to generated files.
- After any merge into the default branch, send generated-only fix rounds, set `needs_update`, and clear it only under the readiness rule.
- Notify the developer of a waiting permission prompt, recover after a restart, and end the feature.

`tests/s-stack/verify-s-stack/checks/orchestrator-handbook.md` holds two cold-read scenarios with expected answers in `## Rerun`. The verifier writes it.

## Non-goals and boundaries

- No file outside the two owned paths, except the generated `packages/s-stack/apm.lock.yaml` (feature plan C7).
- No workmux, tmux or `claude` command line in the handbook (C4). The handbook names the launcher by its flags only.
- No copy of the board schema. The handbook points to the comment at the top of `assets/status-board.html` and names only which collections a tick writes.
- No copy of the status header, the code-head command or the message tables. The handbook points to `references/status-and-messages.md`.
- No run-specific rule as a general rule. The generated-files code-head exemption, the tick minutes 7, 27 and 47, and `s-stack-package` stay in this run's files. The handbook says "the generated paths the feature plan names".
- No `versioning.py bump` on the phase branch.

## Design

The handbook is a checklist-shaped document for one reader, the orchestrator. Sections, in order, with what each owns:

| Section | Owns | Sources |
| --- | --- | --- |
| Opening | What the orchestrator is and is not; supervision rules or pointer (see the open request) | roadmap `roles.md` Orchestrator |
| What you write | Tracker, `run-decisions.md`, merges on the orchestrator branch, the two pages; what it never writes | `workflow.md` artefacts, `roles.md` |
| Starting the feature | Window from `launch.sh --print-window` run in the main session (launcher-r1, option A), tick arming, first board publish, first architecture page, planner start, `started` handling | `coordination.md` tick, board, architecture page |
| Starting a session | Launcher flags per role, outputs, exit code 4, `--fresh` | C4 |
| The tracker | Fields | `coordination.md` tracker |
| The tick | The fixed prompt sentence and the seven-step checklist, including which board documents change | `coordination.md` tick, C5 |
| Merging a phase | Merge condition, clean merge only, abort on conflict, post-merge check, failure rule, follow-up messages, closing the pane | `workflow.md` branches, reference file |
| Merging the default branch | Stop-before-commit procedure, generated-only conflict resolution, checks, abort | C7, run decisions |
| After a merge into the default branch | Generated-only fix rounds, `needs_update`, readiness, Done and worktree removal | C7 |
| Fix rounds and restacks | Sources of feedback, messages, re-merge, dependants | `workflow.md` fix rounds |
| Decisions | Requests from status headers, asking the developer, recording in `run-decisions.md`, `answer` | `workflow.md` doors |
| Permission prompts | Push notification naming pane and action, `needs` item, never relaying approval | `coordination.md` |
| The status board | Publish once from the template, `db` capability, one batch per tick, at most 50 writes, schema pointer | `coordination.md`, C5, D12 |
| The architecture page | Subagent writes it, edit the file then publish the same path, never inline `edits`, when to update | `coordination.md`, Experiment 3 |
| Restarts and stalls | Re-read the record, re-arm, reconcile, relaunch; stalled sessions | `coordination.md` restarts |
| Ending the feature | Final page update, delete the tick, remove worktrees and panes | `roles.md` |

The tick prompt is fixed: "Run the tick checklist in sam-mode's orchestrator handbook." It is armed with Claude Code's recurring scheduled task, every 20 minutes, recreated at every start and before seven days pass.

Merge condition, stated by pointing to the reference file's verdict rule: the newest `verify` verdict is `VERIFIED`, the newest `review` verdict is `CLEAR`, both name the current code head computed with the reference's command (plus the feature plan's generated-path excludes), and the status header lists the phase's pull requests.

The default-branch merge procedure is the one in feature plan C7, given in the handbook as general steps: fetch, `git merge --no-ff --no-commit origin/<default>`, take the other side for conflicted generated files only, abort on any hand-written conflict or an `apm.yml`-like manifest conflict outside the version line, run the feature plan's regenerate command, run the feature plan's checks, commit with the hook on, abort and tell the developer if the checks fail.

Board documents per tick: `board/meta` always (`tick_at`), `board/recent` when a state changed, one `phases/<id>` per changed phase, one `prs/<number>` per changed pull request, and `needs` items added or removed.

## Blast radius

| Path | Change |
| --- | --- |
| `packages/s-stack/.apm/skills/sam-mode/handbooks/orchestrator.md` | New |
| `tests/s-stack/verify-s-stack/checks/orchestrator-handbook.md` | New, written by the verifier |
| `packages/s-stack/apm.lock.yaml` | Generated, gains the handbook's deployments |

## Execution order

1. Commit this plan and the status file (Plan), then move to Implement.
2. Write the handbook. Run the validator, markdownlint and the line budget. Commit it alone.
3. Regenerate `packages/s-stack/apm.lock.yaml` with the venv APM 0.32.0 and relativise. Commit it alone.
4. Run `quick-review` on the single pull request layer and fix the findings.
5. Merge `s-stack-package` into the phase branch with C7's procedure.
6. Verify with a fresh verifier, then Review with `interrogate`, then the PR creator.

## Pull requests

One pull request, holding the handbook and the check file. It depends on each `foundation` pull request still open when the PR creator runs. At planning time both 81 and 82 are open, so it targets `main`, its branch contains their commits, and its description lists them (feature plan, "Pull request rules for this run").

## Verification

- Validator, root manifest check, markdownlint, line budget, and a grep showing no `workmux`, `tmux` or `claude` command line.
- The two cold reads from the **Done when** list, recorded in the check file with placeholder data.
- The C6 verification skill on the phase branch after the merge of `s-stack-package`.
- `quick-review` before Verify, `interrogate` for Review.

## Rejected alternatives

- **Copying the board schema into the handbook.** Two homes for one schema drift. C5 gives the template's comment as its home.
- **Restating the code-head command and message tables.** `references/status-and-messages.md` owns them (C1).
- **Writing this run's code-head exemption and tick minutes as general rules.** They are decisions for this run. The handbook ships to every consuming repository.

## Open request

`orchestrator-handbook-r1`: the Orchestrate playbook that the roadmap points to does not exist in Foundry's p-stack. The recommendation is to state the needed supervision rules in the handbook. The status file holds the request.
