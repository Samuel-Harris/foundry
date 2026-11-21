---
name: arena
description: "Spawn N parallel candidates at the same task, pick a base, graft the strongest parts of the losers into it. Use for /arena, 'arena this', 'throw it in the arena', or when one attempt at a non-trivial artefact would lock in the wrong shape."
disable-model-invocation: true
---

# Arena

Open a todo list with one entry per phase (Frame, Fan out, Cross-judge, Pick, Graft, Verify) before launching anything. Use the host's todo tool if it offers one. Otherwise keep the list in your reply and update it at each phase.

## Phase A: Frame

Every candidate gets the same prompt, so the prompt is the contract.

1. State the artefact each candidate is producing.
2. Derive the rubric, 3-6 concrete gradeable criteria for what success looks like on *this* task. It is the picker's tool in Phase D. Candidates only see the task.
3. Pick the runners from the `arena runners` line in the `pstack-models` rule that the **setup-pstack** skill writes (`~/.cursor/rules/pstack-models.mdc` in Cursor, `~/.claude/rules/pstack-models.md` in Claude Code), by default `claude-fable-5-2-high`, `claude-opus-5-5-high-fast`, and `gemini-4-neon-xhigh`. These are model choices the host maps to its own model and effort settings. An `auto` or `inherit-parent` entry is the parent model, so leave the model unset and spawn a general-purpose subagent. If the host's subagent tool rejects a model, use the nearest valid model of the same family or drop the seat, keep at least two runners, and say so. Where a model is unavailable on the host, that seat counts as dropped. Families go by prefix, and the longest match wins: `claude-fable-*`, `claude-*`, and `gemini-*`, after dropping a leading `cursor-`. Any other slug's family is its text before the first hyphen. Spawn more for multiple design directions, and repeat one model when the work is generation-bound, not judgement-sensitive. Pick each subagent's reasoning level per the Subagents section of the **poteto-mode** skill.
4. Give each candidate its own output location (a git worktree where possible, otherwise `/tmp/arena-<slug>/candidate-<n>/`), per the **separate-before-serializing-shared-state** principle skill.

## Phase B: Fan out

Spawn all N subagents in one message, in the background where the host supports background subagents, each with the task, the path to the shared grounding, its own output path, and instructions to produce the artefact and a short rationale naming the alternatives it considered and what it rejected.

If a candidate produces no output, proceed with N-1 and note the dropout.

## Phase C: Cross-judge

After all Phase B candidates complete, spawn one read-only judge (tell it not to edit files) from the `arena cross-judge pool` line in the `pstack-models` rule, by default `claude-opus-5-5-high-fast`, `gemini-4-neon-xhigh`. The judge is never from the parent's vendor, and Fable counts as Claude for that check, so use the first entry from another vendor. An `auto` or `inherit-parent` entry is the parent model. If you do not know the parent's model, use the first real model and say that the vendor check did not run. If the host's subagent tool rejects a model, use the nearest valid model of the same family, then the next such entry, or skip the judge, and say so. While you read in Phase D, the judge scores each candidate, by path label, on each rubric criterion and recommends a base.

## Phase D: Pick a base

Read every candidate end to end before picking. Score each against the rubric criterion by criterion, not on holistic feel, and compare with the cross-judge when Phase C ran one. Agreement on the base confirms the pick. Disagreement means one of you is biased or the rubric was ambiguous. Read both rationales before deciding.

Pick the base a future maintainer can extend most easily without breaking invariants. When two feel tied, prefer the cleaner boundary or smaller API, per the Laziness Protocol.

## Phase E: Graft

Walk each losing candidate once more for what is worth porting into the base, usually one or two things per candidate, not most of it. Fold each graft in by hand, per the **redesign-from-first-principles** principle skill, so the result stays coherent under one mental model. Don't paste mechanically.

If the candidates converge on one shape, that is strong agreement. Note it and ship the consensus shape. No graft is needed. If they wildly diverge, Phase A was under-specified. Reframe and re-run rather than averaging the divergence.

## Phase F: Verify

Verify the synthesised artefact like any other output, per the **prove-it-works** principle skill. If verification finds a problem the arena missed, either Phase A was wrong (re-frame and re-run) or a candidate caught it and you missed the graft (go back to Phase E). Don't paper over it.

## Outputs

One synthesised artefact, with a short synthesis note alongside naming the base and why, the cross-judge's verdict or that Phase C skipped the judge, each graft with its source candidate, what was rejected and why, any convergence or dropouts, and the verification result.
