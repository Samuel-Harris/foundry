---
name: design-skill
description: Design, draft, validate, and iterate on agent skills. Use when the user asks to create, design, improve, or test a skill, especially when the skill's goal, behaviour, triggers, location, or verification case need to be clarified before authoring SKILL.md.
---

# Design Skill

Use this workflow to turn a vague or partly specified skill idea into a well-structured agent skill.

## Required Guidance

Before drafting a skill:

1. Read and follow the `deep-interview` skill to clarify requirements.
2. Read and follow the `optimise-agent-config` skill for placement, progressive disclosure, artefact validation, and avoiding misplaced host configuration.
3. Apply the skill-authoring standard in [Skill-authoring standard](#skill-authoring-standard) below.

## Skill-authoring standard

A skill is a directory containing `SKILL.md` plus optional sibling assets. `SKILL.md` is the entry point and is the only file always loaded; everything else loads on demand.

### Frontmatter

Required:

```yaml
---
name: skill-name
description: Specific third-person description covering what the skill does and when to use it
---
```

- `name` must equal the skill directory name, and must be lowercase words joined by hyphens.
- `description` must be third person, state what the skill does and when to use it, and include the concrete trigger terms that should make it discoverable.

Optional:

- `disable-model-invocation: true` marks the skill as manually invoked rather than auto-discovered. Always restate the manual-only intent in `description`, because some hosts ignore the key.

### Body structure

- Open with a one-line purpose statement.
- Give a step-by-step workflow.
- State clear stop conditions and escalation paths.
- Include verification instructions with a concrete test case.
- List required references or scripts.

### Authoring rules

- Keep `SKILL.md` concise. Move long examples, checklists, or domain material into `references/`.
- Keep file references one level deep from `SKILL.md`.
- Use `references/` for long examples or detailed policy, and `scripts/` for repeatable validation or fragile operations.
- Use one canonical contract for the skill unless the user explicitly requires compatibility with an existing public workflow.
- Do not create a broad always-on instruction when directory-scoped `AGENTS.md` guidance or a skill is the correct artefact.
- Do not add per-host skill wrapper directories unless the user explicitly chooses multi-target parity.
- Keep terminology consistent across the description, instructions, test case, and file names.
- Write each instruction as when-then: the condition that triggers it and the exact action. Name the specific items it refers to, give one tool call per step, and do not write `consider`, `as appropriate` or an unconditional order that may not apply.

## Workflow

### 1. Discover Context

Determine whether the request is brownfield or greenfield.

- Brownfield: inspect existing skill directories, naming patterns, related instructions, prompts, AGENTS.md files, and validation scripts before asking the user about repo facts.
- Greenfield: ask where the skill should live and which conventions should be followed.

For an APM package, default project skills to `.apm/skills/<skill-name>/SKILL.md` unless the user chooses another location. For a repository that deploys through APM, that is the authored source; the per-host directories are generated output and must not be edited directly.

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

Create or update the skill according to the [skill-authoring standard](#skill-authoring-standard).

Before editing, search the repository for every other skill, prompt, chart or template that names this skill, its outputs, its labels or the tools and paths it changes, and update each in the same change. When the new skill overlaps an existing one, decide which owns the behaviour and remove or point the other at it; never leave two skills that both own one prompt, save location or rule.

### 5. Validate the Draft

Run the repository's own artefact validator when it has one. Otherwise run the `optimise-agent-config` skill's `scripts/validate-artefacts.sh` from the project root. Do not use `apm compile --validate` as a skill check: it inspects no skill.

Also manually check that:

- Every tool, argument, enum value, schema field, template, script and file the skill names exists in the form the skill uses. Open each one's definition (tool schema, model class, registry, script source, cited regulation) and confirm the name, the accepted values, list limits and what it can actually do. Fix or remove any instruction a tool or script cannot satisfy, and give a fallback for a tool the host may not attach.
- After any edit, reread the whole skill, not only the changed lines. No two sections, and no rule and its worked example, disagree; one outcome has one label; no sentence appears twice; and every reference to a step or section by number or name still points at the right one after renumbering. Prefer referring to steps by name rather than number.
- For each branch or condition, list the cases that can reach it. Every reachable case has exactly one branch; branches do not overlap through a catch-all `Otherwise`; a step runs only after the decision it depends on; each branch takes every later required step its siblings take; and no branch writes final state before the user confirms it.
- The description is specific and includes trigger terms.
- The skill body stays under 500 lines unless there is a deliberate reason.
- File references are one level deep from `SKILL.md`.
- The workflow has a concrete test case.
- The skill does not duplicate existing AGENTS.md or instruction guidance.

## 6. Ask Before Realistic Subagent Testing

After drafting and validating, ask the user whether to run a fresh subagent test or stop there. If testing is approved, ask what realistic test case the subagent should use unless the user has already provided one explicitly.

Ask as a single question with these options (use the host's structured-question capability if available, otherwise plain chat):

- Run realistic subagent test: dispatch a fresh subagent as if the user is genuinely invoking the drafted skill on the chosen test case.
- Stop there: assume the user will manually test the skill.

Never run the subagent test without this confirmation.
Never invent the test case when the user has not provided enough detail; ask for the exact scenario, inputs, target files or branches, and success evidence.

## 7. Realistic Subagent Test Protocol

When the user approves automated testing:

1. Dispatch a fresh subagent; do not reuse a previous test subagent.
2. Prompt the subagent as a normal user would. Invoke the drafted skill and describe the chosen task, but do not tell the subagent that it is testing or evaluating the skill.
3. Include only the real task constraints the user would have given, such as target branches, files, desired outputs, stop conditions, and approval gates.
4. Let the subagent attempt the workflow naturally. Do not ask it to produce a meta-evaluation or a test report.
5. After the subagent completes or is interrupted, inspect the produced artefacts, git state, command evidence, and final response yourself.
6. Compare the observed result with the agreed success evidence: correct trigger behaviour, expected files or outputs, preserved safety gates, no forbidden side effects, and useful user-facing result.
7. Summarise the observed result to the user, including pass/fail, artefact paths, behavioural gaps, side effects, and recommended skill changes.

Where the host cannot dispatch named agents or subagents, execute the test role inline instead and state that limitation in the summary.

## Completion Criteria

The workflow is complete when:

- The skill file exists in the agreed location.
- Validation passes or any validation gap is clearly reported.
- The user has either run or declined the subagent test.
- Any requested feedback iteration has been applied.
- The final response states the created files, validation evidence, and whether automated testing was run.
