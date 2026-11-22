---
name: claude-code-cost-review
description: Analyse local Claude Code session files to find where Claude Code spend goes and which changes would cut it without lowering engineering quality. Use when the user asks why their Claude Code costs or usage are high, wants a spend breakdown by model, effort, subagent or skill, or wants to reduce Claude Code, Opus, token, cache or subagent spend.
---

# Claude Code Cost Review

Explain where a period's Claude Code spend went and rank the changes that would reduce it, each with an evidence label. The deliverable is a private Artifact page (or a Markdown report) plus a short chat summary. Nothing is changed without explicit approval.

**Bundled files** (paths relative to this skill's directory):

- `scripts/summarise_sessions.py`: spend by model, model and effort, speed, main chat against each subagent type and its routing, skill, request context size, day and project; each model's cost split between fresh input, output, cache reads and 5-minute and 1-hour cache writes; the costliest main chats and subagents; fitted rates and a reconciliation against Claude Code's own totals.
- `references/cost-levers.md`: catalogue of cost levers, the evidence each one needs, and interpretation pitfalls.

The script uses only the Python standard library and prints aggregates and subagent descriptions, never transcript content.

## Inputs

- **Read automatically:** session files under `~/.claude/projects/`. No export is needed.
- **Optional:** a period. The default is the seven UTC days ending today. Pass `--since`/`--until` (inclusive `YYYY-MM-DD`) when the user names one.
- **Routing configuration:** the `model` and effort settings in `~/.claude/settings.json` and the project's `.claude/settings.json` and `.claude/settings.local.json`; the `model` frontmatter of subagent definitions in `~/.claude/agents/` and `.claude/agents/`; skills that spawn subagents with an explicit model; and model-routing rules in `CLAUDE.md`, `~/.claude/rules/` and `.claude/rules/`.

## Workflow

Copy this checklist and track progress:

```text
- [ ] 1. Summarise the sessions
- [ ] 2. Read the model-routing configuration
- [ ] 3. Attribute spend and rank levers
- [ ] 4. Publish the report and write the chat summary
- [ ] 5. Offer configuration changes
```

### 1. Summarise the sessions

```bash
python3 scripts/summarise_sessions.py [--since YYYY-MM-DD] [--until YYYY-MM-DD] --json /tmp/claude-code-usage.json
```

Note the total and $/week, the share per model and per effort tier, the cost split for the dominant model, the main-chat share against each subagent bucket (every `inherited` bucket especially), the context-size distribution, and the costliest chats and skills.

Check the trust lines before using any figure:

- `rates_per_million_tokens`: a model with `fitted: false` is priced from standard ratios scaled to its recorded total, so its per-request split is an estimate.
- `reconciliation`: the gap between `cost_state_total` and `priced_requests_total` is spend Claude Code recorded but no transcript request holds. It cannot be placed in the window. Report it as a caveat.

### 2. Read the model-routing configuration

Find every place that decides which model runs: the main-chat model and effort, explicit `model` values in subagent definitions and skills, and per-role routing rules. Record each role, its model and its effort. Treat whatever routing exists as the configuration under review; do not assume any particular skill pack.

### 3. Attribute spend and rank levers

Work through `references/cost-levers.md`. For each lever:

- Compute the period spend it touches and the plausible saving, scaled to **$/week**.
- Label every figure **measured** (read directly from script output), **estimated** (derived from a share or a bound) or **guess** (an unverified cause or a prediction).
- Name the quality risk. Keep the strongest models on work where mistakes are expensive (hard implementation, design, adversarial review); move cheap-to-verify or mechanical work (exploration, summarising, CI watching, write-ups) down a tier.

Rank by saving × confidence. A lever counts as material only if its estimated saving is at least **5% of the period's spend**.

**Stop condition.** If no lever is material, say plainly that the configuration is already cost-efficient, show the evidence, and do not invent recommendations.

### 4. Publish the report and write the chat summary

The report contains, in this order:

1. Headline: total spend, $/week, period, and the one-sentence answer to "where did the money go".
2. Spend by model and by day (charts with titles, axis units and the session files as source).
3. Cost split for the dominant model, and spend by request context size.
4. Attribution table: main chat against each subagent bucket, and the costliest skills.
5. Ranked levers: change, $/week, evidence label, quality risk.
6. Caveats: window length, unfitted models, the reconciliation gap, no baseline period.

Omit any section with no data. When the Artifact tool is available, follow the host's artifact guidance and publish the report as a private Artifact. Otherwise write it as Markdown to `claude-code-cost-review-<end date>.md` in the current directory.

The chat summary leads with the answer, links the report, lists the top three levers with $/week, and states the caveats in one or two sentences.

### 5. Offer configuration changes

List each concrete edit (file, line, before and after) and ask which to apply using the host's structured question tool. Apply only the approved edits, then show the resulting diff. Never edit anything before approval. Behavioural levers (shorter chats, fewer verify rounds) are advice only.

## Verification

The run is correct when:

- Every number in the report traces to script output or to an arithmetic step shown in the report.
- Every saving carries a measured, estimated or guess label.
- The Artifact (or the Markdown fallback) exists and the chat links it.
- No file was edited without approval.

**Reference test case.** On the seven days to 2026-11-22, totalling about $6,342 across 50,408 requests, a correct run reports Opus 5.5 at about 91% of spend, almost all at medium effort, and 5-minute cache writes as Opus's largest cost component (about $2,817 of $5,780). It shows the main chat at about 45% of spend, subagents pinned to Opus at about 37% and inherited subagents at about 9%, with many main-chat requests above 500k tokens of context. It notes Haiku as unfitted and a reconciliation gap of about 3%, and offers routing edits without applying them.
