---
description: Use when creating or refining implementation plans, especially handoff-ready plans another agent will execute.
applyTo: ".foundry/plans/**/*.md"
---

# Plan Handoff Standard

When writing a plan, assume a different agent will execute it later. The plan must be a self-contained handoff, not just a list of edits.

## Before Finalising A Plan

- If the intended behaviour, design, constraints, or success criteria are ambiguous, stop and use the `deep-interview` skill before finalising the plan.
- Before presenting the plan, search it for `implementer should`, `verify`, `confirm`, `TBD`, `if needed`, `as appropriate`, `one option is` and open questions ending in `?`. For each hit, either resolve it now by reading the file, config or code that answers it, or ask the user. Do not hand a fact you can look up, or a design choice, to the implementing agent.
- If the user intentionally leaves an area open, record the open question explicitly and explain the consequences of each option.
- If multiple designs are possible, the plan must either:
  - record the user’s chosen design and explain why it was chosen, or
  - stop and ask the user to decide before finalising the plan.
- The implementing agent should be able to execute the plan mechanically and make only local coding judgements, not product, API, migration, rollout, or architectural decisions.

## Every Plan Must Include

- The problem being solved and why it matters.
- The intended behaviour after the change, including user-visible behaviour, system behaviour, edge cases, and failure handling where relevant.
- Non-goals, constraints, compatibility expectations, migration expectations, rollout assumptions, and any other boundaries that affect implementation.
- The intended design: key models, contracts, data flow, state transitions, invariants, and why this design was chosen.
- The blast radius: known callers, affected files, schemas, APIs, database objects, generated artefacts, and tests.
- A concrete execution order that another agent can follow directly.
- Verification: tests, manual checks, downgrade or rollback checks where relevant, and the exact evidence that will prove the work is correct.
- A `quick-review` pass over the written code, then a refactor from that review: on a stacked PR, one review per layer of that layer's own diff, before the next layer is started; on a single PR, one review of the whole diff at the end. Do not collapse per-layer reviews into a review of the finished stack.

## Required Level Of Detail

- Include exact names when they matter: fields, routes, enums, tables, config keys, validation rules, mapping tables, and compatibility rules.
- Include code snippets for parts where precise structure matters.
- Include mermaid diagrams when they materially clarify architecture, data flow, migrations, ownership, or state changes.
- Explain both `what` and `why`. The implementing agent should understand the intent well enough to make nuanced decisions without re-discovering the design.
- When a feature has multiple plausible implementations, document the rejected alternatives briefly and state why the chosen design was selected.
- State exact preconditions and postconditions for any exceptional path, override, migration, replay path, or operator-only workflow.
- Define what must remain unchanged as clearly as what must change.

## Quality Bar

Before you finish a plan, ask: could another agent implement this without guessing about:

- the core intent,
- the intended behaviour,
- the chosen design,
- the compatibility strategy,
- the rollout strategy,
- the verification standard, or
- any material trade-off or safety constraint?

If yes, the plan is incomplete.
