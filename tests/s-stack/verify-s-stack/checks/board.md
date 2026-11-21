# Phase `board` checks

Phase `board` ships `packages/s-stack/.apm/skills/sam-mode/assets/status-board.html`, the status board template. An orchestrator publishes it once per feature and then writes only to the page's database. The behavioural checks render the template with a stubbed database in headless Chrome and compare what the page shows with exact expected values.

## Rerun

### Rendered board in headless Chrome

The script writes its harness to a fresh `mktemp` directory and never writes into the repository. It wraps the template in the skeleton the Artifact tool publishes, which includes `[hidden]{display:none!important}`, and defines `window.claude.use("db")` as a stub. The stub serves placeholder documents, live (`fromCache: false`) or cached (`fromCache: true`), on a timeline the scenario sets. The database and every reference are proxies: `onSnapshot`, `get`, `doc`, `collection`, `where`, `orderBy`, `limit`, `id` and `path` read, and any other member, such as `set`, `update`, `delete`, `add`, `acquire` or one not yet in the API, records a write. The stub also records each subscription. The page's clock starts at 2026-01-31T09:05:00Z and runs with Chrome's virtual time, or stands still with `freeze`, so every age is exact. Headless Chrome will not make a window narrower than 500 px, so the page runs in an `iframe` of width `w` (400 by default) and height `h` (1400 by default), and the script reads that frame's own sizes. Chrome resolves no host name, so the run touches nothing outside the machine, the template's web fonts never load, and every measurement uses the fallback faces a viewer sees when Google Fonts does not answer. A line break inside a word counts only between two letters or digits, because the browser may break between punctuation marks such as `>` and `<` and the line still reads.

Every Chrome call runs under a 30-second wall-clock bound, through `timeout`, `gtimeout` or a `perl` fallback that runs Chrome in its own process group, in the order `tests/structural/run-tier1.sh` uses. A call that times out has its process group killed and runs once more. A second timeout fails that scenario, and every later scenario is reported as skipped and fails. An exit trap kills any Chrome process still using the run's profile directories and removes the directory, also after an interrupt.

Each line of the `LIST` block is one scenario: a virtual-time budget in milliseconds, extra Chrome flags (`-` for none) and the query string the stub and collector read.

- `theme` is `light` or `dark`, set as `data-theme`, or `os`, which sets no `data-theme` and runs Chrome with `--blink-settings=preferredColorScheme=0` so the page's own `prefers-color-scheme: dark` block must apply.
- `tick` is the age of `tick_at` in minutes (5 by default), `tickms` the age in milliseconds, or `bad` for an unreadable 71-character string. `stale` sends `stale_after_min`; without it the field is absent.
- `fixture` names the first data set (`full` by default). `deliver` is `live` (data after 20 ms), `silent` (never), `late` (after 11 s), `cached` (cached only), `live-cached` (live, then the same data cached at 300 ms), `live-cached-error` (that, then the failing listeners fail at 600 ms), `nodb` (`use("db")` resolves `null`), `error-before` or `error-after` (at 300 ms). `error` lists the sources whose listeners fail with `permission-denied`. `swap` sends every source the data of another fixture, live, at 300 ms, and `tick2` sends the same fixture again at 300 ms with a new tick age.
- `at` lists the virtual times at which the page is read. `interact=focus` focuses the `#11` link in Ready for your review, scrolls the map to 80 px and the page to its end, then sends every listener a second, identical snapshot, and reads the page again after it and after the 30-second re-render. `interact=scroll` widens both tables to 1200 px with a test style, scrolls the Pull requests table to its end, the Phases table to 37 px and the map to its end, then does the same. `words` checks word breaks.

| Fixture | Holds |
| --- | --- |
| `full` | A 66-character orchestrator branch with no hyphen or other break point. This run's phase shape: `foundation` with `[]`, six middle phases on `foundation` until `merged`, `default-stack` on the other seven until `done`, unsorted, every state tone and all four scheduling values. Drafts #11 (rank 1, on `12`), `"12"` (rank 2, a digit string) and #13 (rank 3, on `[11, "12", 100, 9]`, markup in its title, a `javascript:` URL), open `"100"` with an `http:` URL, merged #9. Four needs out of order, one with a `javascript:` link in its summary, one prompt with a 61-character pane, a decision with a pane and a restack with a door. 22 recent items, two out of time order. |
| `review` | Seven pull requests, unsorted: null rank, a rank tie between two drafts that can go, a two-draft dependency cycle, a dependency on a closed pull request and a missing `needs_update`. |
| `lanes-a`, `lanes-b` | Five phases in three columns and two skipping edges. They differ only in which first-column phase each skipping edge leaves from. |
| `share` | Four columns and three skipping edges: two share a source, two share a target, and two overlap without sharing an end. Solid and dashed edges share each end. |
| `long` | Ids of 40 characters that share their first 39, one of 41 characters, and `spec-planner-handbooks`, and a recent item with an unreadable 71-character time. |
| `missing`, `cycle`, `unreadable`, `flat`, `empty` | A dependency with no phase document and unknown state and scheduling values; a dependency cycle; unreadable `depends_on` entries, among them one of 102 characters and a string `depends_on`; phases with no dependencies; no documents. |

| Promise | Scenarios that assert it |
| --- | --- |
| Six sections, in order, under exact headings | every scenario |
| No `<title>` element, and the tab title from `board/meta.feature` | every scenario; `full` |
| Header: feature, both branches, an `https` architecture link | `full` |
| Needs you: every item, sorted by kind then oldest first, door chip only on decisions, pane only on prompts, waiting time, count, empty state | `full`, `empty`, `swap` |
| Ready for your review: drafts only, rank order with null last and ties by number, dependencies first, cycle fallback, "after" notes for draft and open dependencies, chips, empty state | `full`, `review`, `empty` |
| Pull requests: every row and cell, ordered by number, digit strings read as numbers, empty state | `full`, `review`, `empty` |
| Phases: every row and cell, scheduling phrases, unknown values, Depends on, relative time with its `datetime`, empty state | `full`, `missing`, `unreadable`, `cycle`, `flat`, `empty` |
| Recent changes: first 20 in stored order, each time's `datetime`, null `from`, empty state | `full`, `empty` |
| Heartbeat: last tick's `datetime`, age, Fresh or Stale chip, banner minutes, no tick, unreadable tick | every scenario with `board/meta` |
| Staleness: more than 40 minutes by default and more than `stale_after_min` when sent, exact to the millisecond | `tickms` scenarios with `freeze` |
| Staleness re-judged every 30 seconds with no write | `tickms=2380000` read at 29.9 s and 30.1 s |
| A later live tick replaces the verdict either way; a cached tick never judges; a live verdict survives cached data and a dead listener | `tick2`, `cached`, `live-cached`, `live-cached-error`, `error-after`, `error-before` with `meta` |
| Every section follows later snapshots | `swap` both ways |
| No database, data unreachable after 10 s and cleared by data, cached data counted as unreachable | `nodb`, `silent`, `late`, `cached`, `live-cached` |
| A failed subscription marks only its section, before and after data, for every source | `error-before`, `error-after` |
| Exactly one subscription per source, never renewed | every scenario |
| The page never writes | every scenario |
| Only text, never markup, from data; only `https://` links | every scenario |
| Chip tones, the same palette for state chips and map nodes, in light, dark and OS dark | every scenario |
| Phone tables show column names; wider tables show a header | every scenario |
| No page scroll at 320, 400, 601, 700 and 1000 px; at 1000 px no line break between two letters or digits of a word of up to 16 characters, and no clipped chip | width scenarios, `words` |
| Map columns by layer, ids sorted in each column, columns centred, 168 by 44 nodes, gaps 56 and 12, padding 12 | every map |
| One 24-unit lane per skipping edge, including shared sources, shared targets and overlaps, above every node | `full`, `lanes-a`, `lanes-b`, `share` |
| SVG size equal to the layout and holding every node and edge; nodes as wide as labels up to 40 characters and at most 20 units wider; a cut with "…" above 40 | every map, `long` |
| Edges from the source's right middle to distinct points on the target's left side, dashed exactly for `done`, with arrowheads, crossing no other node | every map |
| Node state line and tone; unknown nodes; the legend; the cycle line; unreadable entries; no map without edges | `full`, `missing`, `cycle`, `unreadable`, `flat` |
| The map scrolls inside its own box | every map |
| Focus, page scroll and the scroll of the map and both tables kept across a snapshot and the 30-second re-render | `interact=focus`, `interact=scroll` |

Run it from the repository root. It needs Google Chrome at `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`, or the path in `CHROME`. Without Chrome it prints `PENDING: Google Chrome not found at <path>, so the board cannot be rendered here` and exits `0`. `TEMPLATE` points it at another copy of the template, which is how the mutation proof under Evidence runs it.

```bash
bash <<'EOF'
set -euo pipefail
template="${TEMPLATE:-$PWD/packages/s-stack/.apm/skills/sam-mode/assets/status-board.html}"
chrome="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
if [ ! -x "$chrome" ]; then echo "PENDING: Google Chrome not found at $chrome, so the board cannot be rendered here"; exit 0; fi
[ -f "$template" ] || { echo "FAIL: $template is missing"; exit 1; }
dir="$(mktemp -d)"
trap 'pkill -KILL -f "user-data-dir=$dir/" 2>/dev/null || true; rm -rf "$dir"' EXIT
trap 'exit 1' INT TERM HUP
limit=30

bounded() {
  if command -v timeout >/dev/null 2>&1; then
    timeout -k 5 "$limit" "$@"
  elif command -v gtimeout >/dev/null 2>&1; then
    gtimeout -k 5 "$limit" "$@"
  else
    perl -e 'my $t = shift; my $pid = fork // die "fork: $!";
      if (!$pid) { setpgrp(0, 0); exec @ARGV or exit 127 }
      setpgrp($pid, $pid);
      $SIG{ALRM} = sub { kill "KILL", -$pid; waitpid($pid, 0); exit 124 };
      alarm $t; waitpid($pid, 0); kill "KILL", -$pid;
      exit($? & 127 ? 128 + ($? & 127) : $? >> 8)' "$limit" "$@"
  fi
}

cat > "$dir/stub.js" <<'JS'
(() => {
  const q = new URLSearchParams(location.search);
  const theme = q.get("theme") || "light";
  if (theme !== "os") document.documentElement.setAttribute("data-theme", theme);
  const T0 = Date.UTC(2026, 0, 31, 9, 5);
  const RealDate = Date;
  const started = performance.now();
  const now = () => (q.has("freeze") ? T0 : T0 + Math.floor(performance.now() - started));
  window.Date = class extends RealDate {
    constructor(...args) { super(...(args.length ? args : [now()])); }
    static now() { return now(); }
  };
  window.__T0 = T0;
  const iso = (ms) => new RealDate(T0 - ms).toISOString();
  const ago = (min) => iso(Math.round(min * 60000));
  const metaWith = (tick, tickms) => {
    const meta = {feature: "placeholder-feature", orchestrator_branch: "placeholder_feature_orchestrator_with_a_long_unbroken_branch_name", default_branch: "main",
      architecture_url: "https://example.com/architecture",
      tick_at: tickms != null ? iso(Number(tickms)) : tick === "bad" ? "unreadable-" + "0123456789".repeat(6) : ago(Number(tick || 5))};
    if (q.has("stale")) meta.stale_after_min = Number(q.get("stale"));
    return meta;
  };
  const dep = (phase, until) => ({phase, until});
  const middle = ["launcher", "board", "orchestrator-handbook", "phase-handbooks", "pr-handbook", "spec-planner-handbooks"];
  const onFoundation = [dep("foundation", "merged")];
  const phase = (id, state, scheduling, min, depends_on, more) =>
    ({phase: id, state, scheduling, waits_for: null, session_live: false, pane: null, changed_at: ago(min), depends_on, ...more});
  const plan = (id, depends_on, state = "Plan") => phase(id, state, "queued", 5, depends_on);
  const LONG = "orchestrator-handbook-and-phase-handboo";
  const lanes = (skips) => [plan("a1", []), plan("a2", []), plan("b1", [dep("a1", "merged")]), plan("b2", [dep("a2", "merged")]),
    ...skips.map(([c, a]) => plan(c, [dep("b" + c[1], "merged"), dep(a, "merged")]))];
  const pr = (number, state, review_rank, depends_on, checks, needs_update) => ({number, url: "https://example.com/pull/" + number,
    title: "Review fixture " + number, phase: "alpha", state, checks, base: "main", depends_on, review_rank, needs_update});
  const recentItems = Array.from({length: 22}, (_, i) => ({
    at: ago([0, 10, 5][i] ?? i * 5), phase: "p" + String(i + 1).padStart(2, "0"), from: i === 0 ? null : "Plan", to: "Implement"}));
  const build = (meta) => ({
    full: {
      "board/meta": meta,
      "board/recent": {items: recentItems},
      phases: [
        phase("pr-handbook", "Plan", "queued", 50, onFoundation),
        phase("default-stack", "Spec", "blocked", 90, ["foundation", ...middle].map((p) => dep(p, "done"))),
        phase("foundation", "PR", "closed", 120, []),
        phase("launcher", "Implement", "live", 3, onFoundation, {session_live: true, pane: "%12"}),
        phase("board", "Verify", "live", 20, onFoundation, {session_live: true, pane: "%14"}),
        phase("orchestrator-handbook", "Review", "queued", 30, onFoundation),
        phase("phase-handbooks", "Spec", "blocked", 45, onFoundation, {waits_for: "a decision on the handbook layout"}),
        phase("spec-planner-handbooks", "Done", "closed", 240, onFoundation)],
      prs: [
        {number: 13, url: "javascript:alert(1)", title: "Pull request C <b>not bold</b><img src=x>", phase: "board", state: "draft", checks: "failing", base: "main", depends_on: [11, "12", 100, 9], review_rank: 3, needs_update: false},
        {number: 11, url: "https://example.com/pull/11", title: "Pull request A", phase: "launcher", state: "draft", checks: "passing", base: "placeholder-feature-orchestrator", depends_on: [12], review_rank: 1, needs_update: true},
        {number: "100", url: "http://example.com/pull/100", title: "Ready for a human", phase: "foundation", state: "open", checks: "none", base: "main", depends_on: [9], review_rank: null, needs_update: true},
        {number: "12", url: "https://example.com/pull/12", title: "Pull request B", phase: "launcher", state: "draft", checks: "pending", base: "main", depends_on: [], review_rank: 2, needs_update: false},
        {number: 9, url: "https://example.com/pull/9", title: "Merged groundwork", phase: "foundation", state: "merged", checks: "passing", base: "main", depends_on: [], review_rank: null, needs_update: false}],
      needs: [
        {kind: "restack", phase: "launcher", summary: "Restack launcher onto the merged foundation.", door: "two-way", pane: null, since: ago(50)},
        {kind: "prompt", phase: "board", summary: "A permission prompt waits in the session.", door: null, pane: "%" + "1234567890".repeat(6), since: ago(4)},
        {kind: "decision", phase: "phase-handbooks", summary: "Choose the handbook layout.", door: "two-way", pane: "%7", since: ago(10)},
        {kind: "decision", phase: "default-stack", summary: "Approve the tag <a href=\"javascript:alert(2)\">now</a>", door: "one-way", pane: null, since: ago(23)}],
    },
    review: {"board/meta": meta, prs: [pr(36, "draft", 2, [], "passing", false), pr(30, "draft", null, [], "none", false),
      pr(34, "draft", 2, [], "passing", false), pr(31, "draft", 2, [32], "passing", true), pr(32, "draft", 3, [31], "pending", undefined),
      pr(33, "draft", 1, [35], "failing", false), pr(35, "closed", 0, [], "none", false)]},
    missing: {"board/meta": meta, phases: [phase("alpha", "Shipping", "weird", 5, [dep("ghost", "merged"), dep("<b>ghost</b>", "done")])]},
    cycle: {"board/meta": meta, phases: [plan("alpha", [dep("beta", "merged")]), plan("beta", [dep("alpha", "done")]), plan("gamma", [dep("alpha", "merged")])]},
    unreadable: {"board/meta": meta, phases: [
      plan("alpha", [{phase: 5, until: "merged"}, dep("beta", "later"), "beta", dep("x".repeat(80), "soon")]),
      plan("beta", "alpha"), plan("gamma", [dep("alpha", "merged")])]},
    flat: {"board/meta": meta, phases: [plan("alpha", []), plan("beta", null), {...plan("gamma", []), depends_on: undefined}]},
    "lanes-a": {"board/meta": meta, phases: lanes([["c1", "a1"], ["c2", "a2"]])},
    "lanes-b": {"board/meta": meta, phases: lanes([["c1", "a2"], ["c2", "a1"]])},
    share: {"board/meta": meta, phases: [plan("a", [], "Done"), plan("b", [dep("a", "merged")], "PR"),
      plan("c", [dep("b", "merged"), dep("a", "done")], "Implement"), plan("d", [dep("c", "merged"), dep("a", "merged"), dep("b", "done")], "Verify")]},
    long: {"board/meta": meta, "board/recent": {items: [{at: "unreadable-" + "0123456789".repeat(6), phase: LONG + "cd", from: "Review", to: "Implement"}]},
      phases: [plan(LONG + "a", []), plan(LONG + "b", [dep(LONG + "a", "merged")], "Review"),
      plan("spec-planner-handbooks", [dep(LONG + "a", "done")], "Done"), plan(LONG + "cd", [dep(LONG + "b", "merged")], "Implement")]},
    empty: {},
  });
  const name = q.get("fixture") || "full";
  const data = build(metaWith(q.get("tick"), q.get("tickms")))[name];
  const later = q.has("swap") || q.has("tick2") ? build(metaWith(q.get("tick2") ?? q.get("tick"), null))[q.get("swap") || name] : null;
  const deliver = q.get("deliver") || "live";
  const failing = (q.get("error") || "").split(",").map((s) => ({meta: "board/meta", recent: "board/recent"}[s] || s));
  window.__writes = [];
  window.__subs = [];
  const listeners = [];
  const snapshotOf = (set, path, fromCache) => {
    const metadata = {fromCache, hasPendingWrites: false};
    if (path.includes("/")) return {id: path.split("/")[1], exists: path in set, data: () => structuredClone(set[path]), metadata};
    const docs = (set[path] || []).map((body, i) => ({id: String(i), exists: true, data: () => structuredClone(body), metadata}));
    return {docs, size: docs.length, empty: !docs.length, docChanges: () => [], metadata};
  };
  const ref = (path) => ({
    id: path.split("/").pop(),
    path,
    onSnapshot(next, fail) {
      window.__subs.push(path);
      const emit = (set, fromCache = false) => () => next(snapshotOf(set, path, fromCache));
      const error = () => fail({code: "permission-denied", message: "stub"});
      const fails = failing.includes(path);
      listeners.push(emit(later || data));
      if (["live", "error-after", "live-cached", "live-cached-error"].includes(deliver)) setTimeout(emit(data), 20);
      if (deliver === "error-before") setTimeout(fails ? error : emit(data), 20);
      if (deliver === "cached") setTimeout(emit(data, true), 20);
      if (deliver === "late") setTimeout(emit(data), 11000);
      if (deliver.startsWith("live-cached")) setTimeout(emit(data, true), 300);
      if (deliver === "error-after" && fails) setTimeout(error, 300);
      if (deliver === "live-cached-error" && fails) setTimeout(error, 600);
      if (later) setTimeout(emit(later), 300);
      return () => {};
    },
    get: async () => snapshotOf(data, path, false),
  });
  const READS = new Set(["onSnapshot", "get", "doc", "collection", "where", "orderBy", "limit", "id", "path"]);
  const guarded = (target) => new Proxy(target, {
    has: () => true,
    get(t, key) {
      if (typeof key !== "string" || key === "then" || READS.has(key)) return t[key];
      return () => { window.__writes.push(key); return Promise.resolve({ok: true}); };
    },
  });
  const collection = (p) => guarded(Object.assign(ref(p), {doc: (id) => guarded(ref(p + "/" + id)),
    where: () => collection(p), orderBy: () => collection(p), limit: () => collection(p)}));
  const db = guarded({doc: (p) => guarded(ref(p)), collection});
  window.__reemit = () => listeners.forEach((emit) => emit());
  window.claude = {use: async (n) => (n === "db" && deliver !== "nodb" ? db : null)};
})();
JS

cat > "$dir/collect.js" <<'JS'
(() => {
  const q = new URLSearchParams(location.search);
  const text = (n) => (n ? n.innerText.trim().replace(/\s*\n\s*/g, " | ") : null);
  const shown = (n) => !!n && !n.closest("[hidden]") && n.getClientRects().length > 0;
  const bySection = (title) => [...document.querySelectorAll("main section")].find((s) => s.querySelector("h2")?.textContent === title);
  const cs = (n, pseudo) => getComputedStyle(n, pseudo);
  function tokens() {
    const probe = document.createElement("div");
    document.body.append(probe);
    const out = {};
    for (const t of ["chip-bg", "chip-fg", "line", "accent", "accent-bg", "good", "good-bg", "warn", "warn-bg", "crit", "crit-bg"]) {
      probe.style.color = `var(--${t})`;
      out[t] = cs(probe).color;
    }
    probe.remove();
    return out;
  }
  function mapOf(section) {
    const svg = section.querySelector("svg");
    if (!svg) return null;
    const W = Number(svg.getAttribute("width")), H = Number(svg.getAttribute("height"));
    const nodes = [...svg.querySelectorAll("g")].filter((g) => g.querySelector("rect")).map((g) => {
      const texts = [...g.querySelectorAll("text")];
      const rect = g.querySelector("rect");
      const m = g.transform.baseVal.consolidate()?.matrix || {e: 0, f: 0};
      return {id: g.querySelector("title")?.textContent, lines: texts.map((t) => t.textContent), fill: cs(rect).fill, stroke: cs(rect).stroke,
        textFill: texts.map((t) => cs(t).fill), x: m.e + rect.x.baseVal.value, y: m.f + rect.y.baseVal.value,
        w: rect.width.baseVal.value, h: rect.height.baseVal.value,
        fits: texts.every((t) => t.x.baseVal[0].value + t.getComputedTextLength() <= rect.width.baseVal.value - 2),
        labelEnd: texts[0] ? texts[0].x.baseVal[0].value + texts[0].getComputedTextLength() : 0};
    });
    const xs = [...new Set(nodes.map((n) => n.x))].sort((a, b) => a - b);
    const at = (p, side) => nodes.find((n) => Math.abs((side === "out" ? n.x + n.w : n.x) - p.x) < 0.5 && p.y > n.y && p.y < n.y + n.h);
    const geometry = new Set();
    const edges = [...svg.querySelectorAll("path")].filter((p) => !p.closest("marker")).map((p) => {
      const len = p.getTotalLength();
      const start = p.getPointAtLength(0), end = p.getPointAtLength(len);
      const from = at(start, "out"), to = at(end, "in");
      const crosses = new Set();
      const pts = [];
      let outside = false;
      for (let i = 0; i <= 400; i++) {
        const pt = p.getPointAtLength((len * i) / 400);
        pts.push(pt);
        geometry.add(Math.round(pt.x) + "," + Math.round(pt.y));
        if (pt.x < -0.5 || pt.y < -0.5 || pt.x > W + 0.5 || pt.y > H + 0.5) outside = true;
        for (const n of nodes) {
          if (n === from || n === to) continue;
          if (pt.x > n.x + 1 && pt.x < n.x + n.w - 1 && pt.y > n.y + 1 && pt.y < n.y + n.h - 1) crosses.add(n.id);
        }
      }
      let run = null;
      for (let i = 0, j = 0; i < pts.length; i = j) {
        for (j = i + 1; j < pts.length && Math.abs(pts[j].y - pts[i].y) < 0.05; j++);
        const r = {y: pts[i].y, x1: pts[i].x, x2: pts[j - 1].x};
        if (!run || r.x2 - r.x1 > run.x2 - run.x1) run = r;
      }
      const dash = cs(p).strokeDasharray;
      const marker = (p.getAttribute("marker-end") || "").match(/^url\(#(.+)\)$/);
      return {from: from && from.id, to: to && to.id, dashed: dash !== "none" && dash !== "", crosses: [...crosses], outside, run,
        start: {x: start.x, y: start.y}, end: {x: end.x, y: end.y},
        arrow: !!marker && !!svg.querySelector(`marker[id="${CSS.escape(marker[1])}"] path`),
        skips: !!(from && to) && xs.indexOf(to.x) - xs.indexOf(from.x) > 1};
    });
    const box = svg.parentElement;
    return {W, H, viewBox: svg.getAttribute("viewBox"), nodes, edges, xs, geometry: [...geometry].sort().join(" "),
      overflowX: cs(box).overflowX, clientWidth: box.clientWidth, scrollWidth: box.scrollWidth,
      mainWidth: document.querySelector("main").clientWidth};
  }
  const chips = (root) => [...root.querySelectorAll(".chip")].filter(shown).map((c) =>
    ({text: c.textContent, bg: cs(c).backgroundColor, fg: cs(c).color, clipped: c.scrollWidth > c.clientWidth}));
  function depChips() {
    const box = document.querySelector("main").getBoundingClientRect();
    return [...document.querySelectorAll("main .deps .chip")].filter(shown).map((c) => {
      const r = c.getBoundingClientRect();
      return {text: c.textContent, clipped: c.scrollWidth > c.clientWidth, inside: r.left >= box.left - 0.5 && r.right <= box.right + 0.5};
    });
  }
  function brokenWords() {
    const broken = [];
    const walker = document.createTreeWalker(document.querySelector("main"), NodeFilter.SHOW_TEXT);
    for (let node = walker.nextNode(); node; node = walker.nextNode()) {
      if (!shown(node.parentElement) || node.parentElement.closest("svg")) continue;
      for (const m of node.data.matchAll(/\S+/g)) {
        if (m[0].length > 16) continue;
        const range = document.createRange();
        range.setStart(node, m.index);
        range.setEnd(node, m.index + m[0].length);
        if (new Set([...range.getClientRects()].filter((r) => r.width > 0).map((r) => Math.round(r.top))).size < 2) continue;
        const tops = [...m[0]].map((_, k) => {
          const one = document.createRange();
          one.setStart(node, m.index + k);
          one.setEnd(node, m.index + k + 1);
          return Math.round(one.getBoundingClientRect().top);
        });
        const inWord = (k) => /[\p{L}\p{N}]/u.test(m[0][k - 1]) && /[\p{L}\p{N}]/u.test(m[0][k]);
        if (tops.some((top, k) => k > 0 && top !== tops[k - 1] && inWord(k))) broken.push(m[0]);
      }
    }
    return broken;
  }
  const scroller = (n, keep) => n && {left: n.scrollLeft, overflow: n.scrollWidth - n.clientWidth, replaced: n !== keep};
  function snapshot() {
    const root = document.documentElement;
    const noHorizontalScroll = root.scrollWidth <= root.clientWidth;
    const kept = window.__kept || {};
    const sections = [...document.querySelectorAll("main section")].map((s) => ({
      title: s.querySelector("h2") && s.querySelector("h2").textContent,
      count: text(s.querySelector("h2 + *")),
      shown: shown(s),
      text: text(s),
      items: [...s.querySelectorAll("ul > li, ol > li")].map(text),
      rows: [...s.querySelectorAll("tbody tr")].map((tr) => [...tr.cells].map(text)),
      times: [...s.querySelectorAll("time")].map((t) => t.getAttribute("datetime")),
      chips: chips(s),
      tables: [...s.querySelectorAll("table")].map((t) => ({head: [...t.querySelectorAll("th")].map((th) => th.textContent),
        headShown: shown(t.tHead), labels: [...(t.tBodies[0]?.rows[0]?.cells || [])].map((td) => cs(td, "::before").content)})),
      mapHeading: [...s.querySelectorAll("h3")].map(text),
      map: mapOf(s),
    }));
    const focused = document.activeElement && document.activeElement !== document.body ? document.activeElement : null;
    return {
      T0: window.__T0,
      width: root.clientWidth,
      noHorizontalScroll,
      htmlTitles: [...document.body.getElementsByTagName("title")].filter((t) => t.namespaceURI === "http://www.w3.org/1999/xhtml").length,
      title: document.title,
      h1: text(document.querySelector("h1")),
      metaLine: text(document.querySelector("header h1 + *")),
      headerLinks: [...document.querySelectorAll("header a")].map((a) => a.href),
      banner: [...document.querySelectorAll("header *")].filter((n) => shown(n) && /ticked|tick yet/.test(n.textContent) && !n.children.length).map(text),
      notices: [...document.querySelectorAll("body *")].filter((n) => shown(n) && !n.closest("main") && !n.closest("header") && n.children.length === 0 && n.textContent.trim()).map(text),
      sections,
      headerChips: chips(document.querySelector("header")),
      injected: document.querySelectorAll("main b, main img, main script, main a:not([href^='https://'])").length,
      links: [...document.querySelectorAll("a")].map((a) => a.getAttribute("href")),
      tokens: tokens(),
      depChips: depChips(),
      fg: cs(document.body).color,
      bg: cs(document.body).backgroundColor,
      dark: matchMedia("(prefers-color-scheme: dark)").matches,
      broken: q.get("words") ? brokenWords() : [],
      writes: window.__writes.slice(),
      subs: window.__subs.slice(),
      scrollY: window.scrollY,
      focus: focused && {section: focused.closest("section")?.querySelector("h2")?.textContent, text: text(focused), replaced: focused !== kept.focused},
      scrollers: {
        map: scroller(bySection("Phases")?.querySelector("svg")?.parentElement, kept.map),
        prs: scroller(bySection("Pull requests")?.querySelector("table")?.parentElement, kept.prs),
        phases: scroller(bySection("Phases")?.querySelector("table")?.parentElement, kept.phases),
      },
    };
  }
  const times = (q.get("at") || "1500").split(",").map(Number);
  const out = {};
  times.forEach((t) => setTimeout(() => { out[t] = snapshot(); }, t));
  const last = times[times.length - 1];
  const mode = q.get("interact");
  const send = (t) => setTimeout(() => parent.postMessage(JSON.stringify(out), "*"), t);
  if (!mode) {
    send(last + 50);
    return;
  }
  setTimeout(() => {
    const map = bySection("Phases").querySelector("svg").parentElement;
    if (mode === "scroll") {
      document.head.append(Object.assign(document.createElement("style"), {textContent: "main table { min-width: 1200px; }"}));
      const [prs, phases] = ["Pull requests", "Phases"].map((t) => bySection(t).querySelector("table").parentElement);
      prs.scrollLeft = prs.scrollWidth;
      phases.scrollLeft = 37;
      map.scrollLeft = map.scrollWidth;
      window.__kept = {prs, phases, map};
    } else {
      [...bySection("Ready for your review").querySelectorAll("a")].find((a) => a.textContent === "#11").focus();
      map.scrollLeft = 80;
      window.scrollTo(0, document.documentElement.scrollHeight);
      window.__kept = {focused: document.activeElement, map};
    }
    out.before = snapshot();
    window.__reemit();
  }, last + 100);
  setTimeout(() => { out.after = snapshot(); }, last + 600);
  setTimeout(() => { out.later = snapshot(); }, 31000);
  send(31100);
})();
JS

cat > "$dir/frame.html" <<'HTML'
<!doctype html><html><body style="margin:0"><script>
const q = new URLSearchParams(location.search);
const f = document.createElement("iframe");
f.style.cssText = "border:0;height:" + (q.get("h") || 1400) + "px;width:" + (q.get("w") || 400) + "px";
f.src = "harness.html" + location.search;
addEventListener("message", (e) => { document.body.dataset.result = e.data; });
document.body.append(f);
</script></body></html>
HTML

{
  printf '<!doctype html><html><head><meta charset=utf8><meta name=viewport content="width=device-width,initial-scale=1,viewport-fit=cover"><style>:root{padding-top:env(safe-area-inset-top);padding-bottom:env(safe-area-inset-bottom)}body{margin:0}img{max-width:100%%}[hidden]{display:none!important}</style>'
  printf '<script>'; cat "$dir/stub.js"; printf '</script></head><body>'
  cat "$template"
  printf '<script>'; cat "$dir/collect.js"; printf '</script></body></html>'
} > "$dir/harness.html"

n=0
stop=""
while read -r budget flags scenario; do
  n=$((n + 1))
  echo "== $scenario"
  if [ -n "$stop" ]; then echo "-- skipped: $stop"; continue; fi
  [ "$flags" = - ] && flags=""
  for attempt in 1 2; do
    profile="$dir/p$n-$attempt"
    code=0
    TZ=UTC bounded "$chrome" --headless --disable-gpu --hide-scrollbars --host-resolver-rules="MAP * ~NOTFOUND" \
      --user-data-dir="$profile" $flags --window-size=1100,1500 \
      --virtual-time-budget="$budget" --dump-dom "file://$dir/frame.html?$scenario" < /dev/null > "$dir/dom" 2>/dev/null || code=$?
    pkill -KILL -f "user-data-dir=$profile( |$)" 2>/dev/null || true
    [ "$code" -eq 124 ] || [ "$code" -eq 137 ] || break
  done
  cat "$dir/dom"
  echo
  echo "-- exit $code"
  if [ "$code" -eq 124 ] || [ "$code" -eq 137 ]; then stop="Chrome timed out twice after $limit s in $scenario"; fi
done > "$dir/out.txt" <<'LIST'
5000 - theme=light
5000 - theme=dark&w=320
5000 --blink-settings=preferredColorScheme=0 theme=os&w=601
5000 - theme=light&w=700
5000 - theme=light&w=1000&words=1
5000 - theme=dark&w=1000&words=1
5000 - theme=light&freeze=1&tickms=2400000
5000 - theme=light&freeze=1&tickms=2400001
5000 - theme=light&freeze=1&stale=60&tickms=3600000
5000 - theme=light&freeze=1&stale=60&tickms=3600001
35000 - theme=light&tickms=2380000&at=1500,29900,30100
5000 - theme=dark&tick=bad
5000 - theme=light&tick=41&tick2=5&at=100,1500
5000 - theme=light&tick=5&tick2=41&at=100,1500
20000 - theme=light&deliver=cached&tick=180&at=5000,12000
20000 - theme=dark&deliver=live-cached&tick=41&at=5000,12000
5000 - theme=light&deliver=live-cached-error&error=meta&tick=41
5000 - theme=light&deliver=error-after&error=meta&tick=41
5000 - theme=light&deliver=error-before&error=meta
5000 - theme=light&deliver=nodb
20000 - theme=light&deliver=silent&at=9900,10100
20000 - theme=light&deliver=late&at=9900,10500,12500
5000 - theme=light&deliver=error-before&error=prs
5000 - theme=light&deliver=error-before&error=needs,recent,phases
5000 - theme=light&deliver=error-after&error=needs,recent,phases,prs
5000 - theme=light&fixture=empty&swap=full&at=100,1500
5000 - theme=dark&fixture=full&swap=empty&at=100,1500
35000 - theme=light&h=700&interact=focus
35000 - theme=light&w=700&interact=scroll
5000 - theme=light&fixture=empty
5000 - theme=light&fixture=review
5000 - theme=dark&fixture=missing
5000 - theme=light&fixture=cycle
5000 - theme=light&fixture=flat
5000 - theme=light&fixture=unreadable
5000 - theme=light&fixture=unreadable&w=601
5000 - theme=dark&fixture=unreadable&w=1000
5000 - theme=light&fixture=lanes-a
5000 - theme=light&fixture=lanes-b
5000 - theme=light&fixture=share
5000 --blink-settings=preferredColorScheme=0 theme=os&fixture=share&w=1000
5000 - theme=dark&fixture=long
5000 - theme=light&fixture=long&w=320
5000 - theme=light&fixture=long&w=1000
LIST

cat > "$dir/check.py" <<'PY'
import html, json, re, sys
from datetime import datetime, timezone

HEADINGS = ["Needs you", "Ready for your review", "Pull requests", "Phases", "Recent changes", "Heartbeat"]
SOURCES = ["board/meta", "board/recent", "needs", "phases", "prs"]
NEEDS = [
    'decision | one-way | default-stack | waiting 23 min | Approve the tag <a href="javascript:alert(2)">now</a>',
    "decision | two-way | phase-handbooks | waiting 10 min | Choose the handbook layout.",
    "prompt | board | waiting 4 min | A permission prompt waits in the session. | pane %" + "1234567890" * 6,
    "restack | launcher | waiting 50 min | Restack launcher onto the merged foundation."]
REVIEW = [
    "#12 | Pull request B | launcher | pending | Up to date",
    "#11 | Pull request A | launcher | passing | Needs update | after #12",
    "#13 | Pull request C <b>not bold</b><img src=x> | board | failing | Up to date | after #11, #12, #100"]
PRS = [
    ["#9", "Merged groundwork", "foundation", "merged", "passing", "main", "none", "Up to date"],
    ["#11", "Pull request A", "launcher", "draft", "passing", "placeholder-feature-orchestrator", "#12", "Needs update"],
    ["#12", "Pull request B", "launcher", "draft", "pending", "main", "none", "Up to date"],
    ["#13", "Pull request C <b>not bold</b><img src=x>", "board", "draft", "failing", "main", "#11, #12, #100, #9", "Up to date"],
    ["#100", "Ready for a human", "foundation", "open", "none", "main", "#9", "Needs update"]]
REVIEW_FIXTURE = [
    "#33 | Review fixture 33 | alpha | failing | Up to date",
    "#34 | Review fixture 34 | alpha | passing | Up to date",
    "#36 | Review fixture 36 | alpha | passing | Up to date",
    "#30 | Review fixture 30 | alpha | none | Up to date",
    "#31 | Review fixture 31 | alpha | passing | Needs update | after #32",
    "#32 | Review fixture 32 | alpha | pending | after #31"]
PRS_FIXTURE = [[f"#{n}", f"Review fixture {n}", "alpha", state, checks, "main", deps, update] for n, state, checks, deps, update in [
    (30, "draft", "none", "none", "Up to date"), (31, "draft", "passing", "#32", "Needs update"), (32, "draft", "pending", "#31", ""),
    (33, "draft", "failing", "#35", "Up to date"), (34, "draft", "passing", "none", "Up to date"), (35, "closed", "none", "none", "Up to date"),
    (36, "draft", "passing", "none", "Up to date")]]
MIDDLE = ["launcher", "board", "orchestrator-handbook", "phase-handbooks", "pr-handbook", "spec-planner-handbooks"]
PHASES = [
    ["board", "Verify", "session live", "nothing", "foundation (merged)", "live in pane %14", "20 min ago"],
    ["default-stack", "Spec", "blocked", "nothing", " | ".join(p + " (done)" for p in ["foundation"] + MIDDLE), "not live", "1 h 30 min ago"],
    ["foundation", "PR", "session closed", "nothing", "none", "not live", "2 h 0 min ago"],
    ["launcher", "Implement", "session live", "nothing", "foundation (merged)", "live in pane %12", "3 min ago"],
    ["orchestrator-handbook", "Review", "queued to start", "nothing", "foundation (merged)", "not live", "30 min ago"],
    ["phase-handbooks", "Spec", "blocked", "a decision on the handbook layout", "foundation (merged)", "not live", "45 min ago"],
    ["pr-handbook", "Plan", "queued to start", "nothing", "foundation (merged)", "not live", "50 min ago"],
    ["spec-planner-handbooks", "Done", "session closed", "nothing", "foundation (merged)", "not live", "4 h 0 min ago"]]
PHASE_AGES = [20, 90, 120, 3, 30, 45, 50, 240]
RECENT = ["p01 | → Implement"] + [f"p{i:02d} | Plan → Implement" for i in range(2, 21)]
RECENT_AGES = [0, 10, 5] + [i * 5 for i in range(3, 20)]
PR_COLS = ["Number", "Title", "Phase", "State", "Checks", "Base", "Depends on", "Update"]
PHASE_COLS = ["Phase", "State", "Scheduling", "Waits for", "Depends on", "Session", "Last change"]
EMPTIES = ["Nothing needs you.", "No draft pull requests yet.", "No pull requests yet.",
           "No phases yet. The orchestrator adds them once the feature plan exists.", "No state changes yet.", "No tick recorded yet."]
STOPPED = "This section stopped updating (permission-denied). Reload the page to try again."
NODB = "This board reads its data from the page's database, which this view cannot open. Open the board in Claude."
SLOW = "The board's data can't be reached yet. What is shown may be out of date."
NO_TICK = "The orchestrator has not recorded a readable tick yet."
LEGEND = ("Solid line: needed merged into the orchestrator branch. "
          "Dashed line: needed with every pull request merged into the default branch.")
CYCLE = "The phases depend on each other in a cycle: alpha, beta. Fix depends_on in the feature plan."
LONG = "orchestrator-handbook-and-phase-handboo"
def STALE(n): return f"The orchestrator has not ticked for {n} minutes."

TONES = {
    "plain": ["decision", "prompt", "restack", "two-way", "draft", "open", "closed", "none", "Spec", "Plan",
              "session live", "session closed", "queued to start"],
    "accent": ["Implement"], "warn": ["Verify", "Review", "pending", "Needs update", "blocked"],
    "good": ["PR", "Done", "merged", "passing", "Up to date", "Fresh"], "crit": ["one-way", "failing", "Stale"]}
TONE_OF = {text: tone for tone, texts in TONES.items() for text in texts}
CHIP_TOKENS = {"plain": ("chip-bg", "chip-fg"), "accent": ("accent-bg", "accent"), "warn": ("warn-bg", "warn"),
               "good": ("good-bg", "good"), "crit": ("crit-bg", "crit")}
NODE_TOKENS = {"plain": ("chip-bg", "line"), "accent": ("accent-bg", "accent"), "warn": ("warn-bg", "warn"),
               "good": ("good-bg", "good"), "crit": ("crit-bg", "crit")}

def tone(label):
    return "crit" if label.startswith("unknown") else TONE_OF.get(label)

def edges(pairs, dashed=()):
    return {(a, b, (a, b) in dashed) for a, b in pairs}

PLAN = "Plan"
MAPS = {
    "full": {"columns": [["foundation"], sorted(MIDDLE), ["default-stack"]], "lanes": 1,
             "edges": edges([("foundation", p) for p in MIDDLE] + [(p, "default-stack") for p in ["foundation"] + MIDDLE],
                            [(p, "default-stack") for p in ["foundation"] + MIDDLE]),
             "states": {r[0]: r[1] for r in PHASES}},
    "lanes-a": {"columns": [["a1", "a2"], ["b1", "b2"], ["c1", "c2"]], "lanes": 2,
                "edges": edges([("a1", "b1"), ("a2", "b2"), ("b1", "c1"), ("b2", "c2"), ("a1", "c1"), ("a2", "c2")])},
    "lanes-b": {"columns": [["a1", "a2"], ["b1", "b2"], ["c1", "c2"]], "lanes": 2,
                "edges": edges([("a1", "b1"), ("a2", "b2"), ("b1", "c1"), ("b2", "c2"), ("a2", "c1"), ("a1", "c2")])},
    "share": {"columns": [["a"], ["b"], ["c"], ["d"]], "lanes": 3,
              "edges": edges([("a", "b"), ("b", "c"), ("c", "d"), ("a", "c"), ("a", "d"), ("b", "d")], [("a", "c"), ("b", "d")]),
              "states": {"a": "Done", "b": "PR", "c": "Implement", "d": "Verify"}},
    "long": {"columns": [[LONG + "a"], [LONG + "b", "spec-planner-handbooks"], [LONG + "cd"]], "lanes": 0,
             "edges": edges([(LONG + "a", LONG + "b"), (LONG + "a", "spec-planner-handbooks"), (LONG + "b", LONG + "cd")],
                            [(LONG + "a", "spec-planner-handbooks")]),
             "states": {LONG + "a": PLAN, LONG + "b": "Review", "spec-planner-handbooks": "Done", LONG + "cd": "Implement"}},
    "missing": {"columns": [["<b>ghost</b>", "ghost"], ["alpha"]], "lanes": 0,
                "edges": edges([("ghost", "alpha"), ("<b>ghost</b>", "alpha")], [("<b>ghost</b>", "alpha")]),
                "states": {"alpha": "unknown: Shipping", "ghost": "unknown", "<b>ghost</b>": "unknown"}},
    "unreadable": {"columns": [["alpha", "beta"], ["gamma"]], "lanes": 0, "edges": edges([("alpha", "gamma")])},
}
NODE_W, NODE_H, COL_GAP, ROW_GAP, PAD, LANE = 168, 44, 56, 12, 12, 24


def iso(t0, ms):
    d = datetime.fromtimestamp((t0 - ms) // 1000, timezone.utc)
    return d.strftime("%Y-%m-%dT%H:%M:%S.") + f"{(t0 - ms) % 1000:03d}Z"


def contrast(a, b):
    def lum(rgb):
        c = [int(v) / 255 for v in re.findall(r"[\d.]+", rgb)[:3]]
        c = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    hi, lo = sorted((lum(a), lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def sec(snap, title):
    missing = {"title": title, "count": None, "shown": False, "text": "", "items": [], "rows": [], "times": [], "chips": [],
               "tables": [], "mapHeading": [], "map": None}
    return next((s for s in snap["sections"] if s["title"] == title), missing)


def near(a, b):
    return abs(a - b) < 0.01


def map_layout(c, m, spec):
    columns = spec["columns"]
    ids = {i for col in columns for i in col}
    nodes = {n["id"]: n for n in m["nodes"]}
    c("map: one node per phase and per missing id", set(nodes) == ids and len(m["nodes"]) == len(ids))
    if set(nodes) != ids:
        return
    W = m["nodes"][0]["w"]
    longest = max(len(i) for i in ids)
    c("map: nodes 44 high, one width, at least 168", all(n["w"] == W and n["h"] == NODE_H for n in m["nodes"]) and W >= NODE_W
      and (W == NODE_W or longest > 20))
    c("map: a grown node ends at most 20 units past its longest label", W == NODE_W or W - max(n["labelEnd"] for n in m["nodes"]) <= 20)
    lanes = spec["lanes"]
    top = PAD + LANE * lanes
    heights = [len(col) * NODE_H + (len(col) - 1) * ROW_GAP for col in columns]
    tallest = max(heights)
    for ci, col in enumerate(columns):
        for i, nid in enumerate(col):
            n = nodes[nid]
            c(f"map: {nid} in column {ci}, row {i}, column centred", near(n["x"], PAD + ci * (W + COL_GAP))
              and near(n["y"], top + (tallest - heights[ci]) / 2 + i * (NODE_H + ROW_GAP)))
    width, height = 2 * PAD + len(columns) * W + (len(columns) - 1) * COL_GAP, top + tallest + PAD
    c("map: SVG sized to its layout", near(m["W"], width) and near(m["H"], height)
      and m["viewBox"] == f"0 0 {m['W']:g} {m['H']:g}")
    found = {(e["from"], e["to"], e["dashed"]) for e in m["edges"]}
    c("map: every edge between its ends, dashed exactly when until is done", found == spec["edges"] and len(m["edges"]) == len(spec["edges"]))
    c("map: every edge has an arrowhead and stays inside the SVG", all(e["arrow"] and not e["outside"] for e in m["edges"]))
    c("map: no edge crosses another node", all(not e["crosses"] for e in m["edges"]))
    c("map: edges leave from the source's right middle", all(e["from"] and near(e["start"]["x"], nodes[e["from"]]["x"] + W)
      and near(e["start"]["y"], nodes[e["from"]]["y"] + NODE_H / 2) for e in m["edges"]))
    ends = {}
    for e in m["edges"]:
        ends.setdefault(e["to"], []).append(e["end"]["y"])
    c("map: edges into one node arrive at distinct points on its left side", all(
        e["to"] and near(e["end"]["x"], nodes[e["to"]]["x"]) for e in m["edges"])
      and all(len({round(y, 1) for y in ys}) == len(ys) for ys in ends.values()))
    skips = [e for e in m["edges"] if e["skips"]]
    lane_ys = sorted(e["run"]["y"] for e in skips)
    c(f"map: {lanes} skipping edges, each on its own 24-unit lane above every node",
      len(skips) == lanes and all(abs(y - (PAD + LANE * (k + 0.5))) < 0.25 for k, y in enumerate(lane_ys))
      and all(e["run"]["x2"] - e["run"]["x1"] > 20 for e in skips))
    expected_states = spec.get("states", {})
    tokens = m["tokens"]
    for nid, n in nodes.items():
        state = expected_states.get(nid, PLAN)
        label = nid if len(nid) <= 40 else nid[:39] + "…"
        c(f"map: {nid[:20]} labelled, cut above 40 characters, with its state", n["lines"] == [label, state[:23] + "…" if len(state) > 24 else state])
        fill, stroke = NODE_TOKENS[tone(state)]
        c(f"map: {nid[:20]} coloured for {state}", n["fill"] == tokens[fill] and n["stroke"] == tokens[stroke])
        c(f"map: {nid[:20]} label fits and reads on its fill", n["fits"] and contrast(n["textFill"][0], n["fill"]) >= 4.5
          and contrast(n["textFill"][1], n["fill"]) >= 3)


def map_box(c, s, m):
    c("map: scrolls inside its own box", m["overflowX"] in ("auto", "scroll") and m["clientWidth"] <= m["mainWidth"]
      and m["scrollWidth"] == max(round(m["W"]), m["clientWidth"]))
    phases = sec(s, "Phases")
    c("map: heading and legend", phases["mapHeading"] == ["Dependency map"] and LEGEND in phases["text"])


def chips_ok(c, s, chips):
    t = s["tokens"]
    for chip in chips:
        kind = tone(chip["text"])
        c(f"chip {chip['text'][:30]!r} has a known tone", kind is not None)
        if kind:
            bg, fg = CHIP_TOKENS[kind]
            c(f"chip {chip['text'][:30]!r} is {kind}", chip["bg"] == t[bg] and chip["fg"] == t[fg])


def common(c, snap, q):
    c("the page never writes", snap["writes"] == [])
    c("one subscription per source, never renewed", sorted(snap["subs"]) == ([] if q.get("deliver") == "nodb" else SOURCES))
    c("six headings in order", [x["title"] for x in snap["sections"]] == HEADINGS)
    c("no <title> element", snap["htmlTitles"] == 0)
    c("frame at the asked width with no horizontal page scroll", snap["width"] == int(q.get("w", 400)) and snap["noHorizontalScroll"])
    c("unknown dependency chips wrap inside the page", all(not d["clipped"] and d["inside"] for d in snap["depChips"]))
    c("no data becomes markup or an unsafe link", snap["injected"] == 0 and all(h.startswith("https://") for h in snap["links"]))
    chips_ok(c, snap, [ch for x in snap["sections"] for ch in x["chips"]] + snap["headerChips"])
    for x in snap["sections"]:
        for t in x["tables"]:
            cols = PR_COLS if x["title"] == "Pull requests" else PHASE_COLS
            if snap["width"] <= 600:
                c(f"{x['title']}: phone rows name their columns", not t["headShown"] and t["labels"] == [json.dumps(col) for col in cols])
            else:
                c(f"{x['title']}: table header", t["headShown"] and t["head"] == cols)
    m = sec(snap, "Phases")["map"]
    if m:
        m["tokens"] = snap["tokens"]
        spec = MAPS.get(q.get("fixture", "full"))
        if spec:
            map_layout(c, m, spec)
        map_box(c, snap, m)
    if q.get("theme") in ("dark", "os"):
        c("dark theme: dark ground, light text", snap["dark"] and snap["bg"] == "rgb(16, 20, 27)" and contrast(snap["fg"], snap["bg"]) >= 7)
    if q.get("theme") == "light":
        c("light theme: light ground, dark text", snap["bg"] == "rgb(245, 247, 250)" and contrast(snap["fg"], snap["bg"]) >= 7)


def full_content(c, s):
    t0 = s["T0"]
    c("header names the feature, both branches and the architecture page", s["h1"] == "placeholder-feature"
      and s["title"] == "placeholder-feature status board" and s["headerLinks"] == ["https://example.com/architecture"]
      and s["metaLine"] == "orchestrator placeholder_feature_orchestrator_with_a_long_unbroken_branch_name | default main | Architecture")
    c("Needs you: decisions first, then prompts, then restacks, oldest first", sec(s, "Needs you")["items"] == NEEDS)
    c("Needs you count", sec(s, "Needs you")["count"] == "4")
    c("Ready for your review: drafts in dependency order with after notes", sec(s, "Ready for your review")["items"] == REVIEW
      and sec(s, "Ready for your review")["count"] == "3")
    c("Pull requests: every row, ordered by number", sec(s, "Pull requests")["rows"] == PRS and sec(s, "Pull requests")["count"] == "5")
    phases = sec(s, "Phases")
    c("Phases: every row with scheduling labels and Depends on", phases["rows"] == PHASES and phases["count"] == "8")
    c("Phases: each last change dated", phases["times"] == [iso(t0, a * 60000) for a in PHASE_AGES])
    recent = sec(s, "Recent changes")
    c("Recent changes: first 20 in stored order", [i.split(" | ", 1)[1] for i in recent["items"]] == RECENT and recent["count"] == "20")
    c("Recent changes: each time dated", recent["times"] == [iso(t0, a * 60000) for a in RECENT_AGES])


def age_text(minutes):
    return f"{minutes} min ago" if minutes < 60 else f"{minutes // 60} h {minutes % 60} min ago"


def heartbeat(c, s, label, tick_ms, verdict, age_ms=None):
    hb = sec(s, "Heartbeat")
    chips = {"stale": ["Stale"], "fresh": ["Fresh"], None: []}[verdict]
    ok = [x["text"] for x in hb["chips"]] == chips and hb["times"] == [iso(s["T0"], tick_ms)]
    if age_ms is None:
        ok = ok and (s["banner"] == [] if verdict != "stale" else len(s["banner"]) == 1)
    else:
        minutes = age_ms // 60000
        ok = ok and s["banner"] == ([STALE(minutes)] if verdict == "stale" else []) and hb["text"].endswith(age_text(minutes))
    c(f"{label}: {verdict or 'no verdict'}", ok)


def check(name, r):
    failures = []
    def c(label, ok):
        if not ok:
            failures.append(label)
    q = dict(p.split("=", 1) for p in name.split("&"))
    snaps = [r[k] for k in sorted((k for k in r if k.isdigit()), key=int)]
    s = snaps[-1]
    for snap in snaps + [r[k] for k in ("before", "after", "later") if k in r]:
        common(c, snap, q)
    deliver = q.get("deliver", "live")
    fixture = q.get("fixture", "full")
    tick_ms = int(q["tickms"]) if "tickms" in q else round(float(q.get("tick", 5)) * 60000) if q.get("tick") != "bad" else None
    limit = float(q.get("stale", 40)) * 60000
    plain_live = deliver == "live" and fixture == "full" and "swap" not in q and "tick2" not in q
    if plain_live and tick_ms is not None:
        full_content(c, s)
        c("no notice once every source is live", s["notices"] == [])
        if "at" not in q:
            heartbeat(c, s, "heartbeat", tick_ms, "stale" if tick_ms > limit else "fresh", tick_ms)
    if deliver in ("cached", "live-cached"):
        full_content(c, snaps[0])
    if q.get("at") == "1500,29900,30100":
        heartbeat(c, snaps[0], "before the 30-second re-render", tick_ms, "fresh", tick_ms)
        heartbeat(c, snaps[1], "just before 30 s", tick_ms, "fresh")
        heartbeat(c, snaps[2], "after the 30-second re-render", tick_ms, "stale", tick_ms + 30000)
    if q.get("tick") == "bad":
        c("an unreadable tick is stale and shown raw", s["banner"] == [NO_TICK] and [x["text"] for x in sec(s, "Heartbeat")["chips"]] == ["Stale"]
          and sec(s, "Heartbeat")["text"].endswith("No tick recorded yet. | unreadable-" + "0123456789" * 6))
    if "tick2" in q:
        first, second = round(float(q["tick"]) * 60000), round(float(q["tick2"]) * 60000)
        heartbeat(c, snaps[0], "first live tick", first, "stale" if first > limit else "fresh", first)
        heartbeat(c, snaps[1], "second live tick", second, "stale" if second > limit else "fresh", second)
    if q.get("interact") == "scroll":
        b = r["before"]["scrollers"]
        c("both tables and the map can scroll inside their boxes at 700 px", b["prs"]["overflow"] > 0
          and b["prs"]["left"] == b["prs"]["overflow"] and b["phases"]["left"] == 37 and b["map"]["left"] == b["map"]["overflow"] > 0)
        for k in ("after", "later"):
            a = r[k]["scrollers"]
            for key in ("prs", "phases", "map"):
                c(f"{key} scroll kept after the {k} render", a[key]["replaced"] and a[key]["left"] == b[key]["left"])
    elif q.get("interact"):
        b = r["before"]
        c("focus, map scroll and page scroll set before the second snapshot", b["focus"] and b["focus"]["text"] == "#11"
          and b["scrollers"]["map"]["left"] == 80 and b["scrollY"] > 0)
        for k in ("after", "later"):
            a = r[k]
            c(f"focus kept after the {k} render", a["focus"] == {"section": "Ready for your review", "text": "#11", "replaced": True})
            c(f"map scroll kept after the {k} render", a["scrollers"]["map"]["replaced"] and a["scrollers"]["map"]["left"] == 80)
            c(f"page scroll kept after the {k} render", a["scrollY"] == b["scrollY"])
    if q.get("words"):
        c("no short word broken between letters and no chip clipped at 1000 px", s["broken"] == []
          and not any(ch["clipped"] for x in s["sections"] for ch in x["chips"]))
    if fixture == "empty" and "swap" not in q:
        c("every section shows its empty state", [x["text"].split(" | ")[-1] for x in s["sections"]] == EMPTIES and s["banner"] == [NO_TICK])
    if "swap" in q:
        if fixture == "empty":
            c("empty first", [x["text"].split(" | ")[-1] for x in snaps[0]["sections"]] == EMPTIES)
            full_content(c, snaps[1])
            heartbeat(c, snaps[1], "after the swap", tick_ms, "fresh", tick_ms)
        else:
            full_content(c, snaps[0])
            c("every section empties when its documents go", [x["text"].split(" | ")[-1] for x in snaps[1]["sections"]] == EMPTIES
              and snaps[1]["banner"] == [NO_TICK])
    if fixture == "review":
        c("review order: rank, null last, ties by number, dependencies first, a cycle in rank order",
          sec(s, "Ready for your review")["items"] == REVIEW_FIXTURE)
        c("review fixture: every pull request row", sec(s, "Pull requests")["rows"] == PRS_FIXTURE)
    phases = sec(s, "Phases")
    deps = {row[0]: row[4] for row in phases["rows"]}
    if fixture == "long":
        c("an unreadable recent time shown raw", sec(s, "Recent changes")["items"] == [
            "unreadable-" + "0123456789" * 6 + " | " + LONG + "cd | Review → Implement"])
    if fixture == "missing":
        c("an unknown state and scheduling read as unknown", phases["rows"][0][1:3] == ["unknown: Shipping", "unknown: weird"])
    if fixture == "cycle":
        c("a cycle shows the error line and no map", phases["map"] is None and phases["mapHeading"] == [] and CYCLE in phases["text"])
        c("a cycle still lists every dependency", deps == {"alpha": "beta (merged)", "beta": "alpha (done)", "gamma": "alpha (merged)"})
    if fixture == "flat":
        c("no map without dependencies", phases["map"] is None and phases["mapHeading"] == [] and LEGEND not in phases["text"]
          and deps == {"alpha": "none", "beta": "none", "gamma": "none"})
    if fixture == "unreadable":
        long_entry = 'unknown: {"phase":"' + "x" * 80 + '","until":"soon"}'
        c("unreadable depends_on entries show as unknown", deps == {
            "alpha": 'unknown: {"phase":5,"until":"merged"} | unknown: {"phase":"beta","until":"later"} | unknown: "beta" | ' + long_entry,
            "beta": 'unknown: "alpha"', "gamma": "alpha (merged)"})
        c("every unknown entry is a chip", len(s["depChips"]) == 5)
    if deliver == "nodb":
        c("no database: one notice and no sections", s["notices"] == [NODB] and not any(x["shown"] for x in s["sections"]))
    if deliver == "silent":
        c("no notice before 10 s", snaps[0]["notices"] == [])
        c("unreachable notice after 10 s", s["notices"] == [SLOW])
    if deliver == "late":
        c("no notice before 10 s", snaps[0]["notices"] == [])
        c("unreachable notice after 10 s", snaps[1]["notices"] == [SLOW])
        c("the first live data clears the notice", s["notices"] == [] and sec(s, "Ready for your review")["items"] == REVIEW)
    failed = [x for x in q.get("error", "").split(",") if x]
    titles = {"needs": ["Needs you"], "prs": ["Ready for your review", "Pull requests"], "phases": ["Phases"],
              "recent": ["Recent changes"], "meta": ["Heartbeat"]}
    if deliver == "error-before":
        for source in failed:
            for title in titles[source]:
                c(f"{title}: error before data", sec(s, title)["text"] == title.upper() + " | " + STOPPED)
        if "prs" not in failed:
            c("Ready for your review and Pull requests keep working", sec(s, "Ready for your review")["items"] == REVIEW
              and sec(s, "Pull requests")["rows"] == PRS)
        if "needs" not in failed:
            c("Needs you and Phases keep working", sec(s, "Needs you")["items"] == NEEDS and sec(s, "Phases")["rows"] == PHASES)
        if "meta" in failed:
            c("no verdict without a live tick", s["banner"] == [] and sec(s, "Heartbeat")["chips"] == [])
    if deliver == "error-after":
        for source in failed:
            for title in titles[source]:
                c(f"{title}: error after data keeps what it showed", STOPPED in sec(s, title)["text"])
        if "needs" in failed:
            c("rows kept under the error lines", sec(s, "Needs you")["items"] == NEEDS and sec(s, "Phases")["rows"] == PHASES
              and sec(s, "Pull requests")["rows"] == PRS and sec(s, "Ready for your review")["items"] == REVIEW
              and [i.split(" | ", 1)[1] for i in sec(s, "Recent changes")["items"]] == RECENT and sec(s, "Phases")["map"] is not None)
        if "meta" in failed:
            heartbeat(c, s, "heartbeat after its listener died", tick_ms, "stale", tick_ms)
    if deliver == "cached":
        c("a cached tick never calls the board stale or fresh", all(x["banner"] == [] and sec(x, "Heartbeat")["chips"] == [] for x in snaps)
          and sec(s, "Heartbeat")["text"].endswith(age_text(180)))
        c("cached data: no notice before 10 s, the unreachable notice after", snaps[0]["notices"] == [] and s["notices"] == [SLOW])
    if deliver in ("live-cached", "live-cached-error"):
        for x in snaps:
            heartbeat(c, x, "live verdict kept after cached data", tick_ms, "stale", tick_ms + (10000 if x is s and len(snaps) > 1 else 0))
    if deliver == "live-cached":
        c("cached data after live: no notice before 10 s, the unreachable notice after", snaps[0]["notices"] == [] and s["notices"] == [SLOW])
    if deliver == "live-cached-error":
        c("the heartbeat shows the error after cached data", STOPPED in sec(s, "Heartbeat")["text"])
    return failures


chunks = re.split(r"^== (\S+)$", open(sys.argv[1]).read(), flags=re.M)[1:]
failures = []
results = {}
for name, dom in zip(chunks[::2], chunks[1::2]):
    m = re.search(r'data-result="([^"]*)"', dom)
    status = re.search(r"^-- (.*)$", dom, flags=re.M).group(1)
    try:
        if status.startswith("skipped"):
            bad = [status]
        elif status in ("exit 124", "exit 137"):
            bad = ["Chrome timed out twice"]
        else:
            results[name] = json.loads(html.unescape(m.group(1))) if m else None
            bad = check(name, results[name]) if m else [f"the page produced no result ({status})"]
    except Exception as exc:
        bad = [f"the page result could not be read ({exc!r})"]
    print(f"{'FAIL' if bad else 'ok  '} {name}" + (": " + "; ".join(bad) if bad else ""))
    failures += bad
try:
    a, b = (sec(results[f"theme=light&fixture=lanes-{x}"]["1500"], "Phases")["map"]["geometry"] for x in "ab")
    lanes = ["two graphs that differ only in their skipping edges draw the same map"] if a == b else []
except Exception as exc:
    lanes = [f"the two lane graphs could not be compared ({exc!r})"]
print(f"{'FAIL' if lanes else 'ok  '} lanes-a against lanes-b" + (": " + "; ".join(lanes) if lanes else ""))
failures += lanes
print(f"{len(failures)} failed checks" if failures else "board renders as specified")
sys.exit(1 if failures else 0)
PY
python3 "$dir/check.py" "$dir/out.txt"
EOF
```

Expected: exit `0`, one `ok` line for each of the 44 scenarios and one for `lanes-a against lanes-b`, then `board renders as specified`. A failing assertion prints `FAIL`, the scenario and the name of each failed check, then `<n> failed checks`, and exits `1`. A page that crashes, produces no result or times out twice fails its scenario the same way.

## Evidence

The phase's verifier runs these at every code head it verifies and puts every result in its report, never in this file. Every page, row and name is placeholder data.

### Mutation proof

This shows that the `## Rerun` check fails a broken template. Extract the one bash block between `## Rerun` and `## Evidence` from this file into a script outside the repository. Run it once on the real template, which must exit `0`, and once with `CHROME=/nonexistent`, which must print the PENDING line and exit `0`. Then, in a scratch directory outside the repository, write each mutant as a copy of the current template with one text replacement, refusing any replacement whose target text does not occur exactly once, and run the extracted script on each copy through `TEMPLATE`. Every mutant must make it exit `1`, or be shown equivalent: its collected results and rendered page body equal the real template's in every scenario.

The mutants include at least one for each row of the promise table above, every broken template that a review gate has reported, and a systematic pass: for each comparison operator, numeric constant and arithmetic term in the map's lane positions, its width, height, top and column layout, the stale verdict, `staleness` and the view-state keeper, one mutant flips `<` and `<=` or `+` and `-`, moves the constant by one unit, or drops the term. A mutant whose target text the template no longer holds is rewritten by hand as the same fault against the current code. A template that hangs must fail within the wall-clock bound and leave no Chrome process behind.

### Published test page

This shows that the template works as a published page fed only through its database. Copy the template unchanged to a scratch file and publish it once with the Artifact tool, private, with the capabilities and icon its schema comment names and `title: "placeholder-feature status board"`. The page stays private. A later verifier may reuse a test page published from a byte-identical template, after reading the served page to confirm it.

Batch 1 is one `ArtifactData` batch of `set` writes in this run's shape:

- `board/meta`, with an `https://example.com/` architecture URL and a fresh `tick_at`;
- `board/recent` with a few items, newest first;
- eight `phases` with mixed states and scheduling values: `foundation` with `depends_on: []`, `launcher`, `board`, `orchestrator-handbook`, `phase-handbooks`, `pr-handbook` and `spec-planner-handbooks` each on `foundation` until `merged`, and `default-stack` on the other seven until `done`;
- three `prs`, one of which depends on the other two;
- two `needs`, a one-way decision and a prompt with a pane.

Batch 2 is one `update` of `board/meta` that sets `tick_at` 41 minutes back. The page must then show the stale banner and the Stale chip, and the artifact's version must not change, which shows nothing was published again. On a reused page, batch 1 may be a single `update` of `board/meta` that sets a fresh `tick_at`, and the page must then show Fresh.

### How the page is read

Read the page after each batch in every way available, and report which ran:

1. The Artifact tool's `read` with `page: true`, to show that the served page is the template byte for byte under the publish skeleton, with the stored `db` declaration.
2. `ArtifactData` reads of every collection at `as_level: "view"`, to show a viewer reads every row, and one write at `as_level: "interact"`, which the access rules must refuse.
3. The rows from step 2, served unchanged and live to the template inside the served skeleton, rendered in headless Chrome at 400 px in light and dark and read back with the Rerun check's collector. This shows how the template renders exactly those rows, not the claude.ai viewer or its database transport.
4. When a browser tool can open claude.ai, one look at the live page itself, which is the only read that exercises the viewer.

### Cold read of the schema comment

This shows the comment is enough to write the board's data. Give a fresh subagent only the schema comment, the HTML comment at the top of the template, and tell it to read nothing else. Ask it for the first `ArtifactData` batch of a two-phase feature in which `beta` cannot start until every pull request of `alpha` is merged into the default branch, with one permission prompt waiting in `alpha`'s session. The expected answer, in substance: `set` writes only, at most 50; `board/meta` with every field and a UTC `Z` time; `board/recent` as one document with `items` newest first, `from` null for a first state; `phases/alpha` with `depends_on: []` and `phases/beta` with `depends_on: [{"phase": "alpha", "until": "done"}]`, each with a state name and a scheduling value from the lists; a `needs` document of kind `prompt` with its pane and a null door; no `prs` documents invented; every document id as the comment gives it.

### Static checks

- `grep -n innerHTML` on the template must print nothing.
- `apm audit --ci` in `packages/s-stack`, run outside the sandbox with apm-cli 0.32.0, must pass, and the committed lockfile must hold no absolute path.
