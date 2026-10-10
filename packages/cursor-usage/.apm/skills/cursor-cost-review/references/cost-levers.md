# Cost levers

Each lever lists the evidence that shows it applies, how to size it, and the quality risk. Size savings over the CSV's period, then scale to $/week.

## How Cursor spend accrues

- Each CSV row is one billed request. One agent turn re-sends the whole conversation, so cost grows with **conversation length × number of turns**, roughly quadratically in chat length.
- Re-sent context is billed as **cache reads** (cheap per token, huge volume). Context that changes or whose cache has expired is billed as **cache writes** (several times the cache-read rate). Output, including reasoning tokens, is the most expensive per token but usually the smallest volume.
- **Reasoning effort** (the `-low`/`-medium`/`-high`/`-xhigh`/`-max` suffix) mainly changes output and reasoning tokens, and secondarily how many turns a task takes. When the fitted output share is small, effort changes can only reach that small share.
- Cursor's **Max Mode** column is a separate large-context mode, distinct from a `-max` effort tier in the model slug.

## Levers

### 1. Top effort tier on the main chat

- **Evidence:** spend in the `max` (or `xhigh`) effort tier from `summarise_usage_csv.py`; high $/request for those models.
- **Size:** measured. The saving is most of that tier's spend if the same work moves to the next tier down (assume that tier's $/request).
- **Risk:** low for routine work. Keep the top tier for one-off hard problems, chosen deliberately.

### 2. Long main chats

- **Evidence:** spend concentrated in high cumulative-context buckets (6M+ tokens per request); many chats over 200 turns; skills, commands or loops with high average turns.
- **Size:** estimated. Spend in the highest buckets is the ceiling. Splitting a chat in half roughly halves the per-turn context for the second half.
- **Remedy:** a fresh chat per phase, PR layer or loop iteration, carrying state in a handoff file; move bulky reading into subagents; avoid `/loop` patterns that accumulate every iteration in one chat.
- **Risk:** low, provided handoffs carry decisions and open questions.

### 3. Cache writes

- **Evidence:** a large fitted cache-write share (above about 30%) for the dominant model.
- **Size:** guess unless backed by timing evidence. A likely cause is returning to a long chat after the prompt cache expires, which re-writes the whole context.
- **Remedy:** the same as lever 2; long chats make every cache miss expensive.
- **Risk:** none.

### 4. Main-chat model and effort

- **Evidence:** main chats hold most assistant turns; the main-chat model dominates spend.
- **Size:** estimated. Main-chat spend × (1 − cheaper model's $/request ÷ current $/request). Treat $/request ratios across models as rough, because different tasks ran on each.
- **Risk:** medium. The main chat makes judgement calls and reviews subagent output. Prefer a lower effort tier of the same model family over switching family for orchestration-heavy work.

### 5. Subagents that inherit the main chat's model

- **Evidence:** `model=inherit` buckets and the largest inherited subagents from `summarise_transcripts.py`.
- **Size:** estimated. That bucket's turn share × the main-chat model's spend is an upper bound, because subagents start with small contexts.
- **Remedy:** pin an explicit model in the subagent definition or the spawning skill: a fast or cheap model for exploration, CI watching and summarising; the routing table's implementation model for code-writing delegates.
- **Risk:** low for exploration and watching; keep reviewers on a strong model.

### 6. Pinned subagent roles and effort

- **Evidence:** explicit-model buckets for expensive models in `summarise_transcripts.py`; per-role routing in the configuration.
- **Size:** estimated. These are often a small share; say so rather than overselling.
- **Remedy:** lower effort on synthesis, write-up and retrospective roles; keep hard implementation, design and adversarial review on the strongest setting.
- **Risk:** depends on the role; name it per role.

### 7. Fan-out width

- **Evidence:** panels or swarms spawning several subagents per decision (many Task calls per chat with near-identical descriptions).
- **Size:** estimated. Each panel member costs roughly one run of that model.
- **Remedy:** drop the most expensive panel member when the others already provide model diversity, or reserve panels for contested decisions.
- **Risk:** medium; diversity is the point of a panel.

## Interpretation pitfalls

- Transcripts store tool calls but not tool results, so character counts understate context. Use assistant turns, not characters.
- Turn share is not dollar share: main-chat turns carry far larger contexts than fresh subagent turns.
- A short window has no baseline. Do not attribute a cost rise to a new tool without a comparable earlier period.
- Unmatched subagents (spawned outside the parsed `Task` call shapes) belong in the caveats, not silently in a bucket.
- Free or `-` cost rows are excluded from the totals; they are not savings.
