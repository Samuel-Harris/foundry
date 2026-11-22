# Cost levers

Each lever lists the evidence that shows it applies, how to size it, and the quality risk. Size savings over the window, then scale to $/week.

## How Claude Code spend accrues

- Each request re-sends the whole conversation, so cost grows with **context size × number of requests**, roughly quadratically in chat length.
- Re-sent context that is still cached is billed as **cache reads** (cheap per token, huge volume). Context that is new, changed or whose cache has expired is billed as **cache writes**. A 5-minute write costs 25 times a cache read and a 1-hour write 40 times, at the rates fitted on the reference data. Output, including thinking, is the most expensive per token but usually the smallest volume.
- Each subagent starts a fresh context and writes its own cache, so many short subagents pay many cache writes.
- **Effort** mainly changes output and thinking tokens, and secondarily how many requests a task takes. When the output share is small, effort changes can only reach that small share.
- **Fast mode** (`speed: fast`) is billed at a higher rate. If `by_speed` shows any fast spend, size it separately.

## Levers

### 1. Long main chats

- **Evidence:** spend concentrated in the `200k-500k` and `500k+` context buckets; top main chats with hundreds of requests and peaks near the context limit.
- **Size:** estimated. Spend in the highest buckets is the ceiling. Splitting a chat in half roughly halves the per-request context for the second half.
- **Remedy:** a fresh session per phase, PR or loop iteration, carrying state in a handoff file; move bulky reading into subagents; avoid loops that accumulate every iteration in one session.
- **Risk:** low, provided handoffs carry decisions and open questions.

### 2. Cache writes

- **Evidence:** cache writes above about 40% of the dominant model's cost in `cost_components`.
- **Size:** estimated for subagent-driven writes (many subagents × their first-request context), guess for idle expiry.
- **Causes:** returning to a long chat after the 5-minute cache has expired, which re-writes the whole context; and wide subagent fan-out, where each subagent writes its own context.
- **Remedy:** lever 1 for long chats; fewer, longer-lived subagents for repeated small tasks; lever 6 for fan-out.
- **Risk:** none for the chat remedies; see lever 6 for fan-out.

### 3. Subagents that inherit the main chat's model

- **Evidence:** `(inherited)` buckets in `by_agent`.
- **Size:** measured. The bucket's cost is the spend; the saving is that cost × (1 − cheaper model's rate ÷ current rate), using the fitted rates.
- **Remedy:** pin an explicit model in the subagent definition or the spawning skill: a cheap model for exploration, CI watching and summarising; the routing table's implementation model for code-writing delegates.
- **Risk:** low for exploration and watching; keep reviewers on a strong model.

### 4. Top effort tier

- **Evidence:** spend at `high`, `xhigh` or `max` in `by_model_effort`.
- **Size:** measured spend; the saving is most of the output share of that spend if the work moves one tier down.
- **Risk:** low for routine work. Keep the top tier for hard problems, chosen deliberately.

### 5. Main-chat and pinned-role models

- **Evidence:** the main chat or a pinned bucket holds most spend on an expensive model.
- **Size:** estimated. Bucket cost × (1 − cheaper rate ÷ current rate). The fitted rates make this a like-for-like token comparison; the risk is the work itself changing.
- **Remedy:** lower effort on synthesis, write-up and retrospective roles; keep hard implementation, design and adversarial review on the strongest setting.
- **Risk:** medium for the main chat, which makes judgement calls and reviews subagent output. Name the risk per role.

### 6. Fan-out width and repeated rounds

- **Evidence:** many subagents with near-identical descriptions in `top_subagents` (numbered verify or review rounds, panels of adversaries); skills with high spend in `by_skill`.
- **Size:** estimated. Each extra round or panel member costs about one run of that subagent.
- **Remedy:** cap verify or review rounds, fix the cause of repeated failures, drop the most expensive panel member when the others already provide model diversity.
- **Risk:** medium; diversity and repeated verification are often the point.

## Interpretation pitfalls

- Fitted rates apply only to models marked `fitted: true`. Others are priced from standard ratios and their component split is an estimate.
- The reconciliation gap is recorded spend with no matching transcript request. It cannot be dated, so it is outside every window.
- A short window has no baseline. Do not attribute a cost rise to a new tool without a comparable earlier period; run the script again on that period.
- Project names are Claude Code's folder names for the working directory, so worktrees of one repository appear separately.
