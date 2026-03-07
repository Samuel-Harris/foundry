---
name: cursor-sequential-ralplan
description: Iterative planning consensus loop executed entirely by the orchestrating agent. Adopts Planner, Architect, and Critic personas sequentially — no subagents. Use for complex tasks that need a validated plan before implementation.
---

# Sequential Ralplan — Iterative Planning Consensus (No Subagents)

Adopt **Planner**, **Architect**, and **Critic** personas in sequential phases until the Critic persona approves the plan or 5 iterations are exhausted. Everything runs in a single agent — no Task tool dispatches.

## When to Use

Large, ambiguous, or architecturally significant tasks that need a validated work plan before implementation begins.

## Persona Reference Prompts

Read the persona prompt at the start of each phase to adopt the correct mindset and constraints.

| Phase     | Persona file                       | Purpose                                            |
| --------- | ---------------------------------- | -------------------------------------------------- |
| Planner   | `references/planner-prompt.md`     | Create and refine the work plan                    |
| Architect | `references/architect-prompt.md`   | Validate design, answer architectural questions     |
| Critic    | `references/critic-prompt.md`      | Review the plan; issue OKAY or REJECT verdict       |

## Loop

```
Planner phase creates/refines plan
  → Architect phase validates design
  → Critic phase reviews               ← MANDATORY, never skip
  → OKAY → Done
  → REJECT → incorporate feedback, repeat from Planner phase
```

## Execution Protocol

### 1. Initialise

- Parse the user's task description
- Run `date '+%Y-%m-%d_%H-%M-%S'` in the terminal to get the current timestamp — use this for the plan filename
- Read `references/planner-prompt.md` to understand the Planner persona
- Create a TodoWrite to track iteration progress (iteration 1 of max 5)

### 2. Planner Phase

**Adopt the Planner persona.** Your goal is to produce a concrete work plan.

1. **Gather context** — use Glob, Grep, SemanticSearch, and Read to understand the codebase areas involved. Follow the research guidance in `references/planner-prompt.md`
2. **Draft the plan** — with:
   - **Context**: original request, research findings, any prior Critic feedback (if iterating)
   - **Objectives**: core objective, deliverables, definition of done
   - **Guardrails**: must have / must NOT have
   - **Tasks**: ordered steps with file paths, acceptance criteria, and dependencies
   - **Commit Strategy**: logical commit boundaries
   - **Verification**: how to confirm correctness
3. Write the plan:
   - **If in plan mode** (a `<system_reminder>` block in your context says "Plan mode is active") → use the `CreatePlan` tool. Capture the returned file path as `plan_path`.
   - **Otherwise** → write to `.cursor/plans/YYYY-MM-DD_HH-MM-SS_<feature-name>.md` (using the timestamp captured in the Initialise step). Set `plan_path` to that path.
4. If you encounter architectural questions you cannot confidently answer from the gathered context, note them for the Architect phase

**Constraint**: do not write any code files. Only produce the plan document.

### 3. Architect Phase

**Adopt the Architect persona.** Read `references/architect-prompt.md`, then validate the plan you just created.

1. **Re-read the plan** from the plan file
2. **Gather additional context** — read the actual files referenced in the plan. Verify patterns, imports, and dependencies exist as described
3. **Validate architecture** — check for:
   - Coupling and cohesion issues
   - Missing dependencies or import chains
   - Patterns that conflict with existing codebase conventions
   - Security or performance concerns
4. **Answer open questions** — resolve any architectural questions noted during the Planner phase
5. **Produce findings** — summarise as a list of observations and recommendations with `file:line` citations. If the plan needs changes, note the specific tasks and what should change

**Constraint**: do not modify the plan file. Only produce observations.

If findings require plan changes, incorporate them when you return to the Planner phase in the next iteration. If there are no significant findings, proceed directly to the Critic phase.

### 4. Critic Phase — MANDATORY

**Adopt the Critic persona.** Read `references/critic-prompt.md`, then evaluate the plan.

**Never skip this phase.** No plan is approved without a Critic verdict.

1. **Re-read the plan** from the plan file
2. **Apply the four evaluation criteria**:
   - **Clarity**: every task has clear reference sources, no ambiguity
   - **Verifiability**: every task has objective, testable success criteria
   - **Context completeness**: a developer unfamiliar with the codebase could execute with 90%+ confidence
   - **Big picture**: the plan explains WHY, WHAT, and HOW tasks connect
3. **Simulate implementation** — for 2–3 representative tasks, walk through execution using actual files (read them). Ask: "Does the worker have ALL the context they need?"
4. **Deep verification** — for every referenced file, read it. Verify that the patterns, functions, and line numbers mentioned actually exist
5. **Issue verdict**:

```
**[OKAY / REJECT]**

**Justification**: [Concise explanation]

**Summary**:
- Clarity: [Brief assessment]
- Verifiability: [Brief assessment]
- Completeness: [Brief assessment]
- Big Picture: [Brief assessment]

[If REJECT: top 3–5 critical improvements with specific suggestions]
```

### 5. Handle Verdict

| Verdict                    | Action                                                                            |
| -------------------------- | --------------------------------------------------------------------------------- |
| **OKAY**                   | Plan approved. Report to the user and offer to begin execution.                   |
| **REJECT** (iteration < 5) | Note the specific feedback. Increment iteration. Return to step 2 (Planner phase), incorporating the Critic's improvements and any Architect findings. |
| **REJECT** (iteration = 5) | Force-approve with warning. Recommend manual review before execution.             |

Update TodoWrite after each verdict.

## Rules

1. **No subagents** — execute everything in this agent. Never use the Task tool during ralplan
2. **Critic is mandatory** — no plan is approved without a Critic verdict
3. **One persona at a time** — complete each phase before moving to the next
4. **Feedback is specific** — every rejection includes actionable improvements with file references
5. **Max 5 iterations** — hard safety limit
6. **Sequential phases** — Planner → Architect → Critic, every iteration
7. **Plan file is the source of truth** — all changes to the plan are written to the file, not held in conversation alone
8. **Read persona prompts** — read the relevant `references/*.md` file at the start of each phase to maintain persona fidelity
