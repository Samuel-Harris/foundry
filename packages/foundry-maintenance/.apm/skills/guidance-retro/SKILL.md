---
name: guidance-retro
description: "Mine a GitHub repository's PR review comments and the user's local Claude Code and Cursor transcripts over a window (default 30 days), fanned out across subagents, and publish a visual report of which Foundry skills, agents and instructions to add, update or delete so they fit how current models behave. Run from a Foundry checkout. Use when asked for a guidance retro, to refresh or prune Foundry's guidance, or which Foundry skills are out of date."
---

# Guidance Retro

Read recent evidence of how agents behave and recommend which of Foundry's own
guidance to add, update or delete. Never edit a file, open a PR or post anything.
The user reads the report and makes the changes.

`<skill>` below is this skill's directory. Run every command from the Foundry root.

## Inputs

- **Repository.** A GitHub `owner/name` whose PR reviews to mine. Without one, ask
  for it and stop.
- **Window.** Defaults to the 30 days ending today. The user may name another.
  `--since` is the first day and `--until` the day after the last (UTC).
- **Foundry.** The current directory must be a Foundry checkout. `guidance.py`
  stops otherwise. If it does, tell the user to run the skill from Foundry and stop.
- `gh auth status` must pass.

## Workflow

### 1. Collect

```bash
RUN=$(mktemp -d)
python3 <skill>/scripts/guidance.py inventory > "$RUN/inventory.md"
python3 <skill>/scripts/collect_transcripts.py --since <start> --out "$RUN/transcripts"
python3 <skill>/scripts/collect_reviews.py --repo <owner/name> --since <start> --out "$RUN/reviews"
```

Run the two collectors in parallel. Each prints its counts and writes
`summary.json`, whose `slices` list batches its digests. Never read a digest in the
main thread. Subagents read them.

### 2. Mine

Spawn one subagent per slice, in the background:

- each `transcripts/summary.json` slice gets [`references/transcript-miner.md`](references/transcript-miner.md),
  with output `$RUN/obs/t-<n>.jsonl`;
- each `reviews/summary.json` slice gets [`references/review-miner.md`](references/review-miner.md),
  with output `$RUN/obs/r-<n>.jsonl`.

Fill each brief's `{{...}}` placeholders. `{{SLICE}}` is the slice's 0-based index.
Launch up to 20 at once (Claude Code's default concurrency limit) and start the
next as each finishes. Miners do mechanical
reading, so a fast model serves. When every miner has reported:

```bash
python3 <skill>/scripts/guidance.py route "$RUN"
```

It splits the observations into `$RUN/routed/<package>.jsonl` and
`$RUN/routed/_unowned.jsonl`. If it rejects more than a tenth of the lines, rerun
the miners whose files those lines came from.

### 3. Synthesise

Spawn one subagent per Foundry package that ships guidance (every package in the
inventory), plus one for `_unowned`, with
[`references/package-synthesiser.md`](references/package-synthesiser.md). Output
is `$RUN/candidates/<package>.json`. Synthesis is judgement, so use the strongest
model available. Every package gets one even with no observations, so judgement
and silence deletes are still considered.

### 4. Render

```bash
python3 <skill>/scripts/build_report.py "$RUN" --format <html|canvas> > "$RUN/report.<html|canvas.tsx>"
```

The script applies the evidence bar and rejects a candidate whose path does not
exist. On a rejection, send that package's synthesiser the error and rerun it.

- **Claude Code.** Render `html` and publish it with the Artifact tool, icon `checklist`.
- **Cursor.** Render `canvas` and follow the host's canvas skill to write it as a canvas.
- **Elsewhere.** Render `html` and give the user its path.

### 5. Reply

Link the report. Give the window, the source counts, the number of add, update and
delete recommendations, and the report's coverage notes. Name the three
recommendations with the most sources. Give the `$RUN` path so the user can read
the digests or delete them. They hold transcript and review text.

## Stop conditions

- No repository given: ask and stop.
- Not run from Foundry, or `gh` is not authenticated: say so and stop.
- Both collectors found nothing in the window: say so and stop. Do not render an
  empty report.

## Verification

Unit tests: `python3 -m unittest discover -s packages/foundry-maintenance/tests`.

A run is correct when the report renders, every recommendation names a file that
exists in Foundry (or a package that exists, for an add), and every quote traces
to a digest under `$RUN`. `build_report.py`'s docstring owns the evidence bar.
