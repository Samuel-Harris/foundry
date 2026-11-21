# Phase `board` plan

This is the phase plan for `board`, written by the phase session `s-stack-phase-board` on 21 November 2026 against `s-stack-package` at `42c54ee`. The feature plan's entry for `board` (`../README.md`, "Phase `board`") sets the scope, the owned paths and the **Done when** list. Contract C5 in the same file sets the data schema. This file adds the implementation detail. Where they disagree, the feature plan wins and the session tells the orchestrator.

## The problem

The orchestrator must keep a status board current without being reminded (roadmap `README.md`, "No upkeep reminders"). Roadmap decision D12 says the board is published once and then updated only through its database, so the orchestrator never republishes the page. That needs a template that reads every value from the database and renders the six sections of roadmap `coordination.md`, "The status board". Nothing in `packages/s-stack` provides it yet.

## The intended outcome

After this phase, on the phase branch:

- `packages/s-stack/.apm/skills/sam-mode/assets/status-board.html` exists. It is a page body in the form the Artifact tool publishes: no `<!doctype>`, `<html>`, `<head>` or `<body>` tags.
- An HTML comment at the top of the file is the one home of the board's data schema and of the publish call that goes with it.
- The orchestrator publishes the file once, with the capabilities the comment names, then writes documents with `ArtifactData`. Every open view updates live. A viewer never writes.
- With an empty database the page shows a designed empty state in each section. With the store unreachable for 10 seconds it says so. Without the `db` capability it says the board cannot load its data.
- The page marks itself stale when `tick_at` is more than `stale_after_min` minutes old, re-evaluated every 30 seconds with no write.
- `packages/s-stack/apm.lock.yaml` is regenerated, because the new file is deployed.
- `tests/s-stack/verify-s-stack/checks/board.md` exists, written by the verifier, not by the implementer.

What the developer sees: one private page that answers, top to bottom, what needs them, what to review, the pull requests, where each phase is, what changed recently, and whether the orchestrator is alive. It reads on a phone in both themes.

## Non-goals and boundaries

- No change to `SKILL.md`, the reference file, any handbook, the launcher or any other package. The orchestrator handbook phase points to the schema comment. This phase does not write that pointer.
- No Data page type (feature plan Experiment 4). No React or other library. The page is plain HTML, CSS and one inline script.
- No writes from the page. No `user`, `artifact`, `comments` or other capability beyond `db`.
- No `versioning.py bump` on the phase branch (feature plan C7).
- No placeholder data in the template. Placeholder rows go only into the private test page, through `ArtifactData`.
- No private repository, feature or page name anywhere, including the test page's rows.

## Design

### Data shape

The five sources are those of C5. The page subscribes once to each, with `onSnapshot`, and keeps the latest snapshot of each in one state object. Rendering is a pure function of that state plus the current time.

```js
const state = {
  meta:   null,        // board/meta body, or null until it exists
  recent: null,        // board/recent body
  phases: [],          // bodies of every document in `phases`
  prs:    [],          // bodies of every document in `prs`
  needs:  [],          // bodies of every document in `needs`
  loaded: {meta: false, recent: false, phases: false, prs: false, needs: false},
  errors: {},          // source name -> DbError code, after a terminal error
};
```

Every render rebuilds the six sections from `state` with `document.createElement` and `textContent`. Data never reaches `innerHTML`. A link's `href` is set only when the value is a string that starts with `https://`. Otherwise the value is shown as text with no link.

### The schema comment

The file opens with one HTML comment. It holds, in this order:

1. One sentence on what the file is and that this comment is the schema's one home.
2. The publish call: `capabilities: {db: {rules: [{path: "", read: "view", write: "admin"}]}}`, `icon: "status"`, and `title: "<feature> status board"`. The file deliberately has no `<title>`, so the Artifact tool takes the publish `title` (decision `board-d1` below). Publish once per feature, never again.
3. The collections and fields, as the C5 table gives them, with each field's type and allowed values:

   | Collection, document | Fields |
   | --- | --- |
   | `board`, `meta` | `feature` (string), `orchestrator_branch` (string), `default_branch` (string), `architecture_url` (https URL or null), `tick_at` (UTC ISO 8601 string), `stale_after_min` (number, 40) |
   | `board`, `recent` | `items`, a list of at most 20 `{at, phase, from, to}` objects, newest first. `at` is UTC ISO 8601, `from` and `to` are state names, `from` may be null for a phase's first state |
   | `phases`, one per phase id | `phase`, `state` (Spec, Plan, Implement, Verify, Review, PR or Done), `scheduling` (`queued`, `blocked`, `live` or `closed`), `waits_for` (string or null), `session_live` (boolean), `pane` (string or null), `changed_at` (UTC ISO 8601) |
   | `prs`, one per number, document id the number as a string | `number`, `url`, `title`, `phase`, `state` (`draft`, `open`, `merged` or `closed`), `checks` (`passing`, `failing`, `pending` or `none`), `base`, `depends_on` (list of numbers), `review_rank` (number or null), `needs_update` (boolean) |
   | `needs`, one per item, document id chosen by the orchestrator | `kind` (`decision`, `prompt` or `restack`), `phase`, `summary`, `door` (`one-way`, `two-way` or null), `pane` (string or null), `since` (UTC ISO 8601) |

4. The write rules: one `ArtifactData` batch per tick with at most 50 writes, only changed documents, `recent` kept as one document, and a resolved item in `needs` deleted rather than flagged.
5. What `needs_update` means, in one sentence: true until the pull request contains the default branch's tip and its checks have passed on that head.

The comment contains no `--` sequence, because that ends an HTML comment early in some parsers. It must stay valid English prose a cold reader can follow without the feature plan, because the orchestrator handbook points to it instead of copying it. It names no phase, branch or repository of this run.

### Page structure

```text
header     feature name, orchestrator branch, link to the architecture page,
           and a stale banner when the heartbeat is stale
section 1  Needs you
section 2  Ready for your review
section 3  Pull requests
section 4  Phases
section 5  Recent changes
section 6  Heartbeat
```

Each section is a `<section>` with an `<h2>` holding exactly the name above, so a check can read the order from the DOM. Each section shows a count beside its heading where it lists items.

**Needs you.** Every `needs` document. Sorted by kind (`decision`, then `prompt`, then `restack`), then by `since`, oldest first. Each item shows the kind as a chip, the phase, the summary, the door as a chip for a decision (one-way gets the critical colour), the pane for a prompt, and the waiting time ("waiting 23 min") from `since`. Empty state: "Nothing needs you."

**Ready for your review.** `prs` documents whose `state` is `draft`. Ordered by this procedure, written as a named function:

1. Sort by `review_rank` ascending, with null last, then by `number`.
2. Call a number unmerged when a `prs` document with that number has a `state` other than `merged`.
3. Emit, repeatedly, the first remaining pull request whose unmerged `depends_on` numbers that are also in this list have all been emitted.
4. If none qualifies (a cycle), emit the rest in the step 1 order.

Each row shows `#number` linked to `url`, the title, the phase, the checks chip, "after #a, #b" for unmerged dependencies, and a chip that reads "Needs update" when `needs_update` is true and "Up to date" otherwise. Empty state: "No draft pull requests yet."

**Pull requests.** Every `prs` document, sorted by `number`. Columns: number (linked), title, phase, state chip, checks chip, base, depends on (`#n` list or "none"), update ("Needs update" or "Up to date"). It is a real `<table>`. At 600 pixels and below each row becomes a block, and each cell shows its column name from a `data-label` attribute through `::before`, so the page never scrolls sideways. Empty state: "No pull requests yet."

**Phases.** Every `phases` document, sorted by phase id. Columns: phase, state chip, scheduling, waits for (or "nothing"), session ("live in pane %12" or "not live"), last change (relative, with the absolute local time in a `title` attribute and a `<time datetime>`). The same narrow-width table treatment as above. A `state` outside the seven names renders as a critical chip reading "unknown: <value>". Empty state: "No phases yet. The orchestrator adds them once the feature plan exists."

**Recent changes.** `recent.items`, at most the first 20, in stored order. Each line: time, phase, "from → to" (or "→ to" when `from` is null). Empty state: "No state changes yet."

**Heartbeat.** The last tick's local time and age ("last tick 12 min ago"). Fresh when the age is at most `stale_after_min` minutes, stale otherwise, and stale when `tick_at` is missing or unparsable. Stale shows the critical chip and the header banner "The orchestrator has not ticked for N minutes." `stale_after_min` defaults to 40 when absent.

A 30-second interval re-renders relative times and the stale state. It never writes.

### Dependency map (added by `board-d4`)

The developer asked, through the orchestrator, for a dependency map of the phases. The orchestrator recorded the C5 change in `run-decisions.md` on 21 November. Each `phases` document gains one field:

| Field | Type |
| --- | --- |
| `depends_on` | A list of `{phase, until}` objects. `phase` is a phase id. `until` is `"merged"` (the dependency must be merged into the orchestrator branch) or `"done"` (every pull request of the dependency must be merged into the default branch). A phase with no dependencies has `[]`. |

The schema comment gains this field under `phases/<phase id>`, worded for a cold reader with no access to this plan.

**Where it goes.** Inside the Phases section, directly after the Phases table, under a small subheading "Dependency map" (an `<h3>`, so the six `<h2>` sections and their order stay unchanged). It is drawn only when at least one phase has a non-empty `depends_on`. Otherwise it is left out, and the table's Depends on column reads "none" for every row.

**The Phases table gains a column.** "Depends on", between "Waits for" and "Session", listing each entry as `<phase> (merged)` or `<phase> (done)`, comma-separated, or "none". It is the readable equivalent of the map, so everything the map shows can be read on a phone without scrolling the diagram, and by a screen reader.

**Data shape.**

```js
// nodes: one per phase document, plus one per depends_on id with no phases document
// edges: {from: depId, to: phaseId, until: "merged" | "done"}; entries with another until value are dropped
// layer(p) = 0 when p has no edges in, else 1 + max(layer(from)) over its edges in
```

The layer is computed by a depth-first walk with an in-progress set. An edge that would close a cycle is ignored for layering and still drawn. A `depends_on` value that is not a list, an entry that is not an object, or a `phase` that is not a string is skipped. An id with no `phases` document becomes a node with the state "unknown", drawn like an unknown state.

**Layout.** Layers run left to right, one column per layer. Nodes within a column are sorted by phase id and stacked top to bottom, and each column is centred vertically. Constants: node 168 × 44 units, column gap 56, row gap 12, padding 12. The label is the phase id in the mono face at 12 px, cut to 20 characters with "…" when longer, with the full id in an SVG `<title>`. A second line in the text face at 11 px names the state. Colour is never the only signal.

**Edges.** A cubic Bézier from the right middle of the source to the left middle of the target. `until: "merged"` is a solid line. `until: "done"` is a dashed line (`stroke-dasharray: 5 4`). Each ends in an arrowhead marker. An edge that skips one or more layers would cross the nodes between, so it is routed through a lane above every node. The SVG adds 24 units of top padding for the lane when any such edge exists. The two control points sit at the lane's height, at the source's and target's x.

**Node colour by state.** Drawn with CSS classes on the node `<rect>`, using theme tokens only, so both themes work:

| State | Fill | Stroke |
| --- | --- | --- |
| Spec, Plan | `--chip-bg` | `--line` |
| Implement | an accent tint, new token `--accent-bg` | `--accent` |
| Verify, Review | `--warn-bg` | `--warn` |
| PR, Done | `--good-bg` | `--good` |
| unknown, or a value outside the seven names | `--crit-bg` | `--crit` |

`--accent-bg` is defined on bare `:root` and in both dark blocks, like every token.

**Size and phone.** The SVG is drawn at natural size (`width` and `height` attributes equal to the viewBox) inside a `<div class="map">` with `overflow-x: auto` and `max-width: 100%`. The page contract allows a diagram to scroll inside its own container. The page body never scrolls sideways. For this run's data (three layers) the diagram is about 650 units wide, so a phone shows two columns and the developer swipes inside the map. A one-line legend under the map reads "Solid line: needed merged into the orchestrator branch. Dashed line: needed with every pull request merged into the default branch."

**Build.** `document.createElementNS("http://www.w3.org/2000/svg", ...)` for every element, and `textContent` for every label. No data reaches `innerHTML` or an attribute other than `class`, `x`, `y`, `width`, `height`, `d`, `transform` and `marker-end`, all numeric or fixed except the class, which comes from a fixed state-to-class table.

**Rejected for the map.** Scaling the SVG to the container width: at 400 px this run's diagram shrinks to about 0.55, so 12 px labels fall to about 7 px. Layers running top to bottom: six middle phases in one row need about 1,100 units, which is worse. A graph library: a CDN dependency for some 80 lines of layout.

### Loading, absence and errors

- `await claude.use("db")` resolving `null` shows one notice in place of the sections: "This board reads its data from the page's database, which this view cannot open. Open the board in Claude." No other script runs.
- A 10-second timer starts at subscribe. If it fires before every source has delivered a snapshot with `fromCache: false`, a notice reads "The board's data can't be reached yet. What is shown may be out of date." The first full set of confirmed snapshots clears it.
- A terminal `onSnapshot` error marks that source's section with "This section stopped updating (<code>). Reload the page to try again." The other sections keep working. The page never resubscribes on its own.
- An unparsable time renders as the raw string.

### Visual design

A utilitarian treatment. Inter for text and JetBrains Mono for numbers, ids, panes and branches, from Google Fonts, with system fallback stacks. Tokens on bare `:root` for light, redefined in the two dark blocks the artifact page contract requires. A cool neutral ground with a slate-blue accent. Semantic colours for good, warning and critical, separate from the accent, used only by chips: checks passing is good, pending and needs update are warning, failing, one-way door, stale and unknown state are critical. State chips use a neutral tone, with PR and Done shown as good. `font-variant-numeric: tabular-nums` on times and numbers. Side gutter written with the two `max(16px, env(safe-area-inset-*, 0px))` paddings and `<meta name="claude:viewport-fit-sides" content="cover">`. Visible focus on links. No card shadows. Sections are separated by spacing and a hairline, not boxes. The page has no animation.

### Why this design

- One state object and a full re-render keep the code short and the ordering rules in one place. The data is small: tens of documents.
- Five subscriptions, one per C5 source, stay far below the 64-per-view limit, and a failure in one leaves the rest working.
- Root rule `read: "view", write: "admin"` gives C5's "only an editor writes, and every viewer reads". The orchestrator writes through `ArtifactData` as the owner. Viewers, Commenters and Contributors can only read.
- The table that turns into labelled blocks satisfies "reads on a phone" and the **Done when** item on horizontal scroll without hiding columns.

### Rejected alternatives

- **A `<title>` holding a fixed name.** Every feature's board would carry the same gallery name. A token that the orchestrator replaces would mean editing the template before each publish. The publish `title` parameter covers it with no edit.
- **Writing the page from a library such as React.** It adds a CDN dependency and a build idiom for a page of six lists.
- **One subscription to the whole store.** The API subscribes to one document or one collection, so five subscriptions is the minimum.
- **A horizontally scrolling table on phones.** Allowed by the page contract, but the developer reads this board on a phone, and a scrolled table hides the dependency column.

## Decisions for this phase

| Id | Decision | Door |
| --- | --- | --- |
| `board-d1` | The template has no `<title>`. The schema comment tells the orchestrator to publish with `title: "<feature> status board"`, and the script sets `document.title` from `meta.feature` for the tab. | Two-way |
| `board-d2` | The page declares only `db`, with the root rule `read: "view", write: "admin"`, and never writes. | Two-way |
| `board-d3` | Ready for your review lists only `draft` pull requests, as C5 says. A pull request the developer marked ready leaves that list and stays in Pull requests. | Two-way |
| `board-d4` | The developer's instruction, relayed by the orchestrator: add a dependency map of the phases from a new `depends_on` field. See [Dependency map](#dependency-map-added-by-board-d4). | Two-way |

## Blast radius

| Path | Change |
| --- | --- |
| `packages/s-stack/.apm/skills/sam-mode/assets/status-board.html` | New, hand-written, about 450 to 650 lines |
| `packages/s-stack/apm.lock.yaml` | Regenerated, about 22 lines more (feature plan Blast radius) |
| `tests/s-stack/verify-s-stack/checks/board.md` | New, written by the verifier |

The validator does not inspect files under `assets/`. Tier 1's scratch-consumer inventory covers only `default-stack`'s packages, which do not include s-stack until the last phase. No other file changes.

## Pull requests

One pull request, "Add the s-stack status board template", carrying the template, its lockfile regeneration and `checks/board.md`. Its dependencies are each `foundation` pull request still open when the PR creator runs, under feature plan "Pull request rules for this run". On 21 November those are 81 and 82, so it targets `main`, its branch carries their commits, and its description lists them.

## Execution order

1. Create `.venv-apm` if missing: `uv venv .venv-apm && uv pip install --python .venv-apm/bin/python apm-cli==0.32.0`.
2. Write `assets/status-board.html` to the design above, in one file.
3. Self-check locally with the harness in [Verification](#verification), at 400 pixels in light and dark, with the fixture and with an empty store.
4. Regenerate the lockfile: `(cd packages/s-stack && perl -e 'alarm shift; exec @ARGV' 300 ../../.venv-apm/bin/apm install --target cursor,claude,copilot)`, then `python3 scripts/relativise_lockfiles.py packages/s-stack/apm.lock.yaml`.
5. Commit the template and the lockfile together with the hook on: `feat(s-stack): add the status board template`. No file under `.foundry/` in that commit.
6. Run `quick-review` on the diff against `s-stack-package`, fix every finding that holds, commit the fixes, regenerate the lockfile again if the template changed.
7. Commit the status file at Implement on reaching step 2, and at Verify after step 8. Each status commit holds only `.foundry/` files.
8. Merge `s-stack-package` with feature plan C7's procedure (`<other>` is `s-stack-package`).
9. Verify gate, then Review gate, then the PR creator, each a fresh subagent, as roadmap `roles.md` and the feature plan's [Verification](../README.md#verification) say.

## Verification

**Local harness (the implementer's self-check, and the verifier's `## Rerun` candidate).** A scratch HTML file wraps the template in the publish skeleton and defines `window.claude = {use: async (name) => name === "db" ? stubDb : null}`. `stubDb` serves fixture documents through `doc(path).onSnapshot` and `collection(path).onSnapshot` with `fromCache: false`. After render, a script writes a JSON result into `document.body.dataset.result`: the six `<h2>` texts in order, `document.documentElement.scrollWidth` against `clientWidth`, the Ready for your review order, and whether the stale banner is visible. Run it with headless Chrome, which is installed at `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`: `--headless --window-size=400,1200 --virtual-time-budget=3000 --dump-dom file://<harness>`. Run it once with `data-theme="light"` and once with `data-theme="dark"` on the root element, which the page honours as an explicit theme choice. Expected: the six headings in order; `scrollWidth <= clientWidth`; with pull requests A (rank 1, depends on B), B (rank 2) and C (rank 3, depends on A and B), the order B, A, C; stale true for a `tick_at` 41 minutes old and false for 5 minutes old. With an empty store, every section shows its empty-state sentence.

**The feature plan's Done when list, owned by the verifier.**

- Publish the template once as a private test page with the schema comment's capabilities and `title: "placeholder-feature status board"`. Write placeholder rows in one `ArtifactData` batch: `board/meta`, `board/recent` with three items, three `phases`, three `prs` in which one depends on the other two, and two `needs` (a one-way decision and a prompt). Read the page and confirm all six sections in order.
- Write a second batch that sets `tick_at` to 41 minutes ago. Confirm the page marks itself stale with no new publish.
- Confirm no horizontal scroll at 400 pixels in light and dark (the harness above).
- Record the publish, both batches and how the page was read in `checks/board.md`, under `## Evidence`. Put the harness under `## Rerun`.

**The verification skill** `tests/s-stack/verify-s-stack/SKILL.md`, run in full on the phase branch after the merge in step 8.

## Done when

The feature plan's four **Done when** items for `board`, plus these:

- [ ] The schema comment matches C5 field for field, and a fresh subagent given only the template's comment can write a valid first `ArtifactData` batch for a two-phase feature.
- [ ] No data value reaches `innerHTML`: `grep -n innerHTML` on the template finds no line that assigns data.
- [ ] `apm audit --ci` passes in `packages/s-stack` on the committed, relativised lockfile.
- [ ] With this run's eight phases (`foundation` with `[]`, the six middle phases each with `foundation` until `merged`, `default-stack` with the other seven until `done`), the map shows three columns. The seven edges into `default-stack` are dashed, and the six from `foundation` into the middle phases are solid. The `foundation` to `default-stack` edge runs through the top lane and crosses no node. Every node names its state. The page body has no horizontal scroll at 400 px in light and dark.
- [ ] A `depends_on` naming a phase with no document draws an "unknown" node, and a cycle renders without hanging.
- [ ] The verifier extends `checks/board.md`'s `## Rerun` with the map cases above, and the published test page gains `depends_on` rows.
