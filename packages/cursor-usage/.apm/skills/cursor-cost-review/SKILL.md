---
name: cursor-cost-review
description: Analyse an exported Cursor usage-events CSV together with local agent transcripts to find where Cursor spend goes and which changes would cut it without lowering engineering quality. Use when the user shares a Cursor usage or billing CSV, asks why their Cursor costs are high, or wants to reduce Cursor, model, token, Opus, Max or subagent spend.
---

# Cursor Cost Review

Explain where a period's Cursor spend went and rank the changes that would reduce it, each with an evidence label. The deliverable is a Cursor Canvas plus a short chat summary. Nothing is changed without explicit approval.

**Bundled files** (paths relative to this skill's directory):

- `scripts/summarise_usage_csv.py` — spend by model, effort tier, day and cumulative context size; least-squares estimate of each model's cost split between cache writes, cache reads, fresh input and output; most expensive requests.
- `scripts/summarise_transcripts.py` — assistant turns split between main chats and subagents (by requested model, including `inherit`), chat-length distribution, longest chats, turns per invoked skill or slash command, and the largest subagents that inherited the main chat's model.
- `references/cost-levers.md` — catalogue of cost levers, the evidence each one needs, and interpretation pitfalls.

Both scripts use only the Python standard library and print aggregates, never raw transcript content.

## Inputs

- **Required:** the path to a Cursor usage-events CSV (columns include `Date`, `Model`, `Max Mode`, `Input (w/ Cache Write)`, `Input (w/o Cache Write)`, `Cache Read`, `Output Tokens`, `Cost`). If the user has not given one, ask for it and stop.
- **Read automatically:** transcripts under `~/.cursor/projects/*/agent-transcripts/`, and the active model-routing configuration: user rules visible in context, `~/.cursor/rules/*.mdc`, project `.cursor/rules/`, and the `model` fields of subagent definitions (`.cursor/agents/`, `~/.cursor/agents/`) and of any skill that spawns subagents.

## Workflow

Copy this checklist and track progress:

```text
- [ ] 1. Summarise the CSV
- [ ] 2. Summarise transcripts for the same window
- [ ] 3. Read the model-routing configuration
- [ ] 4. Attribute spend and rank levers
- [ ] 5. Build the canvas and write the chat summary
- [ ] 6. Offer configuration changes
```

### 1. Summarise the CSV

```bash
python3 scripts/summarise_usage_csv.py USAGE.csv --json /tmp/cursor-usage.json
```

Note the total, the period and active days, the share per model and per effort tier, the estimated cost split for the dominant models, and how spend spreads across cumulative-context buckets. A `0%` component in the split means the fit could not separate it, not that it was free.

### 2. Summarise transcripts

Always run this; the CSV alone cannot say *who* spent the money.

```bash
python3 scripts/summarise_transcripts.py --csv USAGE.csv --json /tmp/cursor-transcripts.json
```

Note the main-chat share of turns, how many chats exceed 200 turns, which skills or commands have the highest average turns, and every subagent bucket whose model is `inherit`.

### 3. Read the model-routing configuration

Find every place that decides which model runs: the main-chat model the user picks, explicit `model` values in subagent definitions and skills, and per-role routing rules. Record each role, its model and its effort tier. Do not assume any particular skill pack; treat whatever routing exists as the configuration under review.

### 4. Attribute spend and rank levers

Work through `references/cost-levers.md`. For each lever:

- Compute the period spend it touches and the plausible saving, scaled to **$/week**.
- Label every figure **measured** (read directly from the CSV), **estimated** (derived from a fit or a turn-share bound) or **guess** (an unverified cause or a prediction).
- Name the quality risk. Keep the strongest models on work where mistakes are expensive (hard implementation, design, adversarial review); move cheap-to-verify or mechanical work (exploration, summarising, CI watching, write-ups) down a tier.

Rank by saving × confidence. A lever counts as material only if its estimated saving is at least **5% of the period's spend**.

**Stop condition.** If no lever is material, say plainly that the configuration is already cost-optimised, show the evidence, and do not invent recommendations.

### 5. Build the canvas and write the chat summary

Read and follow the host's Canvas skill before writing the file. The canvas contains, in this order:

1. Headline: total spend, period, and the one-sentence answer to "where did the money go".
2. Spend by model and by day (charts with titles, axis units and the CSV as source).
3. Cost split for the dominant model, and spend by cumulative-context bucket.
4. Attribution table: main chats against each subagent bucket, with turn share.
5. Ranked levers: change, $/week, evidence label, quality risk.
6. Caveats: window length, missing baseline, unmatched subagents, transcripts lacking tool results.

Omit any section with no data. If the host has no Canvas support, write the same content as a Markdown report next to the CSV instead.

The chat summary leads with the answer, links the canvas, lists the top three levers with $/week, and states the caveats in one or two sentences.

### 6. Offer configuration changes

List each concrete edit (file, line, before and after) and ask which to apply using the host's structured question tool. Apply only the approved edits, then show the resulting diff. Never edit anything before approval. Behavioural levers (shorter chats, not choosing Max) are advice only.

## Verification

The run is correct when:

- Every number in the canvas traces to script output or to an arithmetic step shown in the canvas.
- Every saving carries a measured, estimated or guess label.
- The canvas exists at the host's canvas path (or the Markdown fallback exists) and the chat links it.
- No file was edited without approval.

**Reference test case.** On a seven-day export totalling about $3,263, a correct run reports Opus as about 83% of spend and the `-max` effort tier at about $278 (Opus max about $242 across 13 requests). It shows main chats at roughly three-quarters of assistant turns, with chats over 200 turns as a top lever, and flags `inherit` subagents running on the main chat's model. It offers routing edits without applying them.
