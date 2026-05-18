---
name: design-skill
description: Design, draft, validate, and iterate on Cursor Agent Skills. Use when the user asks to create, design, improve, or test a skill, especially when the skill's goal, behaviour, triggers, location, or verification case need to be clarified before authoring SKILL.md.
---

# Design Skill

Use this workflow to turn a vague or partly specified skill idea into a well-structured Cursor skill.

## Required Guidance

Before drafting a skill:

1. Read and follow the `deep-interview` skill to clarify requirements.
2. Read and follow the `create-skill` skill for skill structure, frontmatter, storage, and validation.
3. Read and follow `.cursor/skills/optimise-cursor-repo/SKILL.md` for placement, progressive disclosure, artefact validation, and avoiding misplaced Cursor configuration.

If `create-skill` is not available, stop and ask the user for the skill-authoring standard instead of inventing one.

## Workflow

### 1. Discover Context

Determine whether the request is brownfield or greenfield.

- Brownfield: inspect existing skill directories, naming patterns, related rules, commands, AGENTS.md files, and validation scripts before asking the user about repo facts.
- Greenfield: ask where the skill should live and which Cursor conventions should be followed.

For this repository, default project skills to `.cursor/skills/<skill-name>/SKILL.md` unless the user chooses a personal skill or another location.

### 2. Interview the User

Use the `deep-interview` process before drafting. Ask one question at a time and target the weakest clarity dimension.

The interview must identify:

- The skill's primary goal and use case.
- Trigger scenarios for auto-discovery or explicit invocation.
- Intended behaviour from start to finish.
- Target storage location: project skill, personal skill, or another agreed location.
- Constraints, non-goals, compatibility expectations, and boundaries.
- Required guidance sources, reference files, scripts, or examples.
- At least one concrete test case with expected behaviour and pass/fail evidence.

Continue until ambiguity is 20% or lower, all material dimensions are clear, or the user explicitly stops the interview.

### 3. Confirm the Design

Before editing files, summarise the proposed skill design and ask for confirmation when any material choice remains ambiguous.

The confirmation must include:

- Skill name and storage path.
- Auto-discovery behaviour and frontmatter intent.
- Main workflow phases.
- Required inputs and outputs.
- Test case and verification standard.
- Any explicit non-goals.

Do not draft the skill while material design decisions are unresolved.

### 4. Draft the Skill

Create or update the skill using the `create-skill` structure:

```markdown
---
name: skill-name
description: Specific third-person description covering what the skill does and when to use it
---

# Skill Title

## Instructions

...
```

Keep `SKILL.md` concise. Use `references/` for detailed examples, long checklists, or domain material that does not need to load every time.

Use `disable-model-invocation: true` only when the user wants the skill to be manually invoked rather than auto-discovered.

### Drafting Guardrails

- Use one canonical contract for the skill unless the user explicitly requires compatibility with an existing public workflow.
- Do not create broad Cursor rules when directory-scoped AGENTS.md guidance or a skill is the correct artefact.
- Do not add a `.claude/skills/` wrapper unless the user explicitly chooses multi-agent parity.
- Preserve verbatim text the user asks to include.
- Keep terminology consistent across the description, instructions, test case, and file names.

### Required Sections

Every drafted skill must include:

- Frontmatter with `name` and `description`.
- A short purpose statement.
- A step-by-step workflow.
- Clear stop conditions or escalation paths.
- Verification instructions, including the agreed test case.
- Any required references or scripts.

### Optional Sections

Add these only when they are genuinely useful:

- `references/` for long examples or detailed policy.
- `scripts/` for repeatable validation or fragile operations.
- Example prompts or expected outputs.

## 5. Validate the Draft

Run the repo's artefact validator when available:

```bash
.cursor/skills/optimise-cursor-repo/scripts/validate-artefacts.sh
```

Also manually check that:

- The description is specific and includes trigger terms.
- The skill body stays under 500 lines unless there is a deliberate reason.
- File references are one level deep from `SKILL.md`.
- The workflow has a concrete test case.
- The skill does not duplicate existing AGENTS.md or rule guidance.

## 6. Ask Before Realistic Subagent Testing

After drafting and validating, ask the user whether to run a fresh subagent test or stop there. If testing is approved, ask what realistic test case the subagent should use unless the user has already provided one explicitly.

Use the AskQuestion tool when available:

- Run realistic subagent test: launch a fresh subagent as if the user is genuinely invoking the drafted skill on the chosen test case.
- Stop there: assume the user will manually test the skill.

Never run the subagent test without this confirmation.
Never invent the test case when the user has not provided enough detail; ask for the exact scenario, inputs, target files or branches, and success evidence.

## 7. Realistic Subagent Test Protocol

When the user approves automated testing:

1. Launch a fresh subagent; do not reuse a previous test subagent.
2. Prompt the subagent as a normal user would. Invoke the drafted skill and describe the chosen task, but do not tell the subagent that it is testing or evaluating the skill.
3. Include only the real task constraints the user would have given, such as target branches, files, desired outputs, stop conditions, and approval gates.
4. Let the subagent attempt the workflow naturally. Do not ask it to produce a meta-evaluation or a test report.
5. After the subagent completes or is interrupted, inspect the produced artefacts, git state, command evidence, and final response yourself.
6. Compare the observed result with the agreed success evidence: correct trigger behaviour, expected files or outputs, preserved safety gates, no forbidden side effects, and useful user-facing result.
7. Summarise the observed result to the user, including pass/fail, artefact paths, behavioural gaps, side effects, and recommended skill changes.

## 8. Iterate on Feedback

If the user wants changes:

1. Update the design summary and the skill draft.
2. Re-run validation.
3. Ask again whether to run a realistic subagent test and what test case to use.
4. If testing is approved, use a different fresh subagent for the next test.

Repeat until the user accepts the behaviour or asks to stop.

## Completion Criteria

The workflow is complete when:

- The skill file exists in the agreed location.
- Validation passes or any validation gap is clearly reported.
- The user has either run or declined the subagent test.
- Any requested feedback iteration has been applied.
- The final response states the created files, validation evidence, and whether automated testing was run.
