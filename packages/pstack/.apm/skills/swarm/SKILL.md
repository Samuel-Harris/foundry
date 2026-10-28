---
name: swarm
description: "Fan out N parallel workers, drain them, and return one report. Use for /swarm, 'swarm this', or parallel coverage, races, gauntlets, and exploration."
disable-model-invocation: true
---

# Swarm

## Start

Open a todo list with one entry per phase before launching anything. Use the host's todo tool if it offers one. Otherwise keep the list in your reply and update it at each phase.

1. Frame
2. Fan out
3. Aggregate
4. Report

## Phase A: Frame

1. State the done predicate and the artefact or report the swarm must return.
2. Choose the shape. Partition into slices, race N workers on identical briefs, or mix both. For a race or mixed shape, declare `first pass`, `rank all`, or `best-of` before spawning.
3. Pick the worker model from the `swarm workers` line in the `pstack-models` rule that the **setup-pstack** skill writes (`~/.cursor/rules/pstack-models.mdc` in Cursor, `~/.claude/rules/pstack-models.md` in Claude Code). If the rule or that line is missing, use Grok 4.7 at xhigh effort, fast (`grok-4.7-xhigh-fast`), a model choice the host maps to its own model and effort settings. For `auto` or `inherit-parent`, leave the model unset so the workers run on the parent model. If the host's subagent tool rejects a model, use the default and say so. If it rejects the default, use the closest valid model of the same family from its error message. Where a model is unavailable on the host, run the workers on the session model and say so. For a model race, name each arm's model up front. Pick each subagent's reasoning level and fast or standard speed for the job, per the Subagents section of the **poteto-mode** skill.
4. Give each worker its own writable output when it writes. When workers verify or measure commits, each brief names the exact SHAs. A measurement brief also names the method (sample count, what one sample is, order). The worker records both in its result.

## Phase B: Fan out

Spawn all N workers in one message as general-purpose subagents, each in an isolated worktree or cloud agent where the host offers one, in the background where the host supports background subagents, and on the step 3 model, left unset for `auto` or `inherit-parent`. Run a worker in the local checkout only when it needs access to something on the user's computer.

When a worker must start from a non-default pushed branch, name that branch in the brief and tell the worker to check it out first.

Every brief stands alone. Include the goal, scope, exact slice or race arm, how to verify, and what to report. Reports use `PASS`, `ISSUES`, or `BLOCKED` with evidence. A worker that can prove a defect reports `ISSUES` and lists every issue it can prove, not only the first.

If a worker drops out, proceed with N-1 and note it.

## Phase C: Aggregate

Read the terminal results. Drop a result that does not record the SHAs and method its brief names, and respawn that worker once. After a second miss, record a gap. A gap does not count as a pass. For coverage, every required slice needs a result. For a race, apply the selection rule declared up front. Use first pass, rank all, or best-of. Do not paste raw worker dumps.

## Phase D: Report

Return one consolidated in-chat report with a result table, issue one-liners, gaps or dropouts, and the race rule when used.
