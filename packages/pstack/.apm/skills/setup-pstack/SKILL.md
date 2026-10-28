---
name: setup-pstack
description: Configure which models pstack uses per role and at what reasoning budget. Detects your available models and writes an always-applied rule that overrides the skill defaults. Use for /setup-pstack, "configure pstack models", "pstack budget", or changing pstack's model choices.
---

# Setup pstack

Write the `pstack-models` rule, an always-applied, user-level rule that sets pstack's model per role. Where it lives depends on the host:

- **Cursor.** `~/.cursor/rules/pstack-models.mdc`, with the frontmatter shown in step 5.
- **Claude Code.** `~/.claude/rules/pstack-models.md`, with no frontmatter. Claude Code loads every `.md` file in `~/.claude/rules/` into each new session, so its role lines are already in context. Never put the role lines in `CLAUDE.md` or `AGENTS.md`.
- **GitHub Copilot.** The rule is per user, so never write it to the project-level `.github/instructions/` directory. If the host supports a user-level instructions file that applies to every chat, write the rule there as `pstack-models.instructions.md` with `applyTo: "**"` frontmatter. Otherwise, tell the user that a user-level model rule is unsupported on this host, show them the rule body from step 5, skip steps 5 and 6, and go on to step 7. The skills then run on their defaults, or on the session model where a default is unavailable.

The rest of this skill calls that file "the rule".

## Steps

### 1. Detect available models

Enumerate the models you can pass to a subagent in this session. That is the dependable source.

- **Cursor.** The model slugs that the subagent tool (`Task`) accepts. If Cursor also exposes a models API or CLI that lists the user's entitled models, prefer it for completeness.
- **Claude Code.** The `model` values that the subagent tool (`Agent`) schema lists, each with an effort from its `effort` values. Write a real model as `<model> <effort>`, such as `opus xhigh`. The effort is the last token, so the budget step works as written.

If you cannot detect any, ask the user to paste the models they have access to. Never write a real model you have not confirmed is available. The aliases `inherit-parent` and `auto` are always valid even though they are not detected models.

### 2. Load current state

The default role-to-model mapping is the rule shape shown in step 5 below. In Claude Code, map each default slug first: `claude-opus-5-5-xhigh` is `opus xhigh`, and `grok-4.7-xhigh-fast` is `inherit-parent`, because Grok is not available there. If the rule already exists, read it and treat its `# budget` line and its role values as the current choices. Otherwise start from those defaults. A line whose role is not in step 5, such as `how critics`, is from a retired role. Drop it.

### 3. Budget, map, and confirm

**(a) Ask for a budget.** Prefer the host's structured-question tool over free text, and ask in plain text when none is available. Offer these four options with these exact labels, and name the current budget when the rule records one. With no rule, say that `large` matches the skill defaults.

- `unlimited — max reasoning`
- `large — xhigh reasoning`
- `medium — high reasoning`
- `small — medium reasoning`

**(b) Apply it.** Build the working table from the skill defaults, and on a re-run keep any role you changed by family, list, or alias (`inherit-parent`, `auto`). `unlimited`, `large`, `medium`, and `small` set the effort token of every real slug, panel entries included, to `max`, `xhigh`, `high`, or `medium`. The effort token is the last token, or the one before a trailing `fast`, on the ladder `max` > `xhigh` > `high` > `medium` > `low`. If the result is not a detected slug, use the same family's detected slug with the highest effort at or below the target, else mark the role as needing a choice. `inherit-parent` and `auto` do not change. So `unlimited` turns `claude-opus-5-5-xhigh` into `claude-opus-5-5-max`. Grok slugs top out at `xhigh`, so under `unlimited` the fallback puts Grok at `xhigh` and keeps `grok-4.7-xhigh-fast` as it is. `large` keeps both defaults. `small` turns them into `claude-opus-5-5-medium` and `grok-4.7-medium-fast`. In Claude Code the same ladder applies to the `<model> <effort>` form, so `unlimited` turns `opus xhigh` into `opus max`.

**(c) Show the roles and confirm.** Show every role with its model, marking any real slug not in the detected set as needing a choice. Also list each line step 2 dropped. Ask whether to accept as-is or change specific roles, offering the detected models plus `inherit-parent` and `auto` (both mean: this role runs on the parent chat model, which is how Cursor's Auto users stay on Auto) as the options. Prefer the host's structured-question tool over free text. For panel roles (arena runners, architect runners, interrogate reviewers) the value is a list, and one subagent runs per entry, alias entries included, so the list length sets the count. `arena cross-judge pool` is also a list, but Arena runs one judge. It tries only values from a family other than the parent's, in list order, so order it by preference. An `inherit-parent` or `auto` value never judges. `swarm workers` is the default model for every worker unless a race or comparison assigns another model per arm.

### 4. Validate

Every real slug written must be in the detected set. `inherit-parent` and `auto` always pass. If a chosen real slug is not available, stop and ask again.

### 5. Write the rule

Write the rule with a `# budget` line with the chosen label and its target effort, and one line per role, using the same labels poteto-mode uses. Overwrite the whole file so re-runs stay idempotent.

- **Cursor.** Write `~/.cursor/rules/pstack-models.mdc` with `alwaysApply: true`, in the shape below.
- **Claude Code.** Write `~/.claude/rules/pstack-models.md` with no frontmatter: only the comment lines, the `# budget` line, and the role lines, with each value in the `<model> <effort>` form or an alias.
- **GitHub Copilot.** Where a user-level instructions file is supported, write `pstack-models.instructions.md` there with `applyTo: "**"` frontmatter in place of the Cursor frontmatter, then the same body.

Shape:

```
---
description: pstack per-role model choices (overrides skill defaults)
alwaysApply: true
---
# pstack model configuration. One line per role. Delete a line to fall back to the skill default.
# `inherit-parent` or `auto` as a value: the role runs on the parent chat model (omit the subagent's `model`). Alias entries in a panel list still count toward its fan-out.
# budget: large (xhigh)
feature, refactoring: grok-4.7-xhigh-fast
bug-fix: grok-4.7-xhigh-fast
perf-issue: grok-4.7-xhigh-fast
hillclimb: grok-4.7-xhigh-fast
judgment and prose: claude-opus-5-5-xhigh
hardest tasks: claude-opus-5-5-xhigh
how explorer: grok-4.7-xhigh-fast
how explainer: claude-opus-5-5-xhigh
why investigators: grok-4.7-xhigh-fast
why synthesizer: claude-opus-5-5-xhigh
reflect tooling: grok-4.7-xhigh-fast
reflect judgment, divergent, synthesizer: claude-opus-5-5-xhigh
arena runners: claude-opus-5-5-xhigh, grok-4.7-xhigh-fast
arena cross-judge pool: claude-opus-5-5-xhigh, grok-4.7-xhigh-fast
swarm workers: grok-4.7-xhigh-fast
architect runners: claude-opus-5-5-xhigh, grok-4.7-xhigh-fast
interrogate reviewers: claude-opus-5-5-xhigh, grok-4.7-xhigh-fast
```

### 6. Confirm

Tell the user the rule was written and that it applies to new sessions. Re-running this skill updates it.

### 7. Offer a verification skill (optional)

Check whether the project has a way to drive the real app for proof (a `verify-*` skill, or an existing harness). If not, offer once: "Want a project-local verification skill, so agents can drive the app the way a user does and prove changes work? I can generate one with /create-verification-skill." On yes, use the `create-verification-skill` skill (it resolves wherever it is deployed: the project's skills directory, `.agents/skills/` or `.claude/skills/`, or the user-level equivalent). On no, move on without pushing.

### 8. Offer a formal verification skill (optional)

Check whether the project already has a formal verification skill (a project skill that runs a model checker, a proof, or another verifier against the code). If not, offer once: "Want a formal verification skill, so agents can prove a key property of your code holds in every case in scope, not only the cases tests reach? I can generate one with /create-formal-verification-skill." On yes, use the `create-formal-verification-skill` skill (it resolves wherever it is deployed: the project's skills directory, `.agents/skills/` or `.claude/skills/`, or the user-level equivalent). On no, move on without pushing.
