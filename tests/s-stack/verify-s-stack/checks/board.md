# Phase `board` checks

Phase `board` ships `packages/s-stack/.apm/skills/sam-mode/assets/status-board.html`, the status board template. An orchestrator publishes it once per feature and then writes only to the page's database. The behavioural checks render the template with a stubbed database in headless Chrome and compare what the page shows with exact expected values.

## Rerun

### Rendered board in headless Chrome

The script writes its harness to a fresh `mktemp` directory and never writes into the repository. It wraps the template in the skeleton the Artifact tool publishes, which includes `[hidden]{display:none!important}`, and defines `window.claude.use("db")` as a stub. The stub serves placeholder documents, live (`fromCache: false`) or cached (`fromCache: true`) as the scenario asks. The database and every `doc` and `collection` reference are proxies: `onSnapshot`, `get`, `doc` and `collection` read, and any other method, such as `set`, `update`, `delete`, `add`, `acquire` or one not yet in the API, records a write. Headless Chrome will not make a window narrower than 500 px, so the page runs in an `iframe` 400 px wide unless `w` sets another width, and the script reads that frame's own `scrollWidth` and `clientWidth`. Chrome's virtual time runs the 10-second and 30-second timers without waiting.

Each line of the `LIST` block is one scenario: a virtual-time budget in milliseconds, extra Chrome flags (`-` for none) and the query string the stub and collector read.

- `theme` is `light` or `dark`, set as `data-theme` on the root element, or `os`, which sets no `data-theme` and runs Chrome with `--blink-settings=preferredColorScheme=0` so the page's own `prefers-color-scheme: dark` block must apply.
- `tick` is the age of `tick_at` in minutes, or `bad` for an unreadable 71-character string. `stale` sends `stale_after_min`; without it the field is absent.
- `fixture` is `full` (the default), `empty`, `missing`, `cycle`, `unreadable`, `lanes-a`, `lanes-b` or `long`. `deliver` is `live` (the default, data after 20 ms), `silent` (never), `late` (after 11 s), `cached` (cached data only), `live-cached` (live data, then the same data cached at 300 ms), `live-cached-error` (that, then the `error` source's listener fails at 600 ms), `nodb` (`use("db")` resolves `null`), `error-before` or `error-after`, with `error` naming the source whose listener fails with `permission-denied`.
- `at` lists the virtual times at which the page is read. `interact=1` focuses the `#11` link in Ready for your review, scrolls the dependency map to 80 px, then sends every listener a second, identical snapshot. `interact=table` widens the Pull requests table to 1200 px with a test style, so it must scroll inside its own box, scrolls it to its end, then sends the second snapshot. `words` checks word breaks.

The full fixture uses this run's phase shape. `foundation` has `depends_on: []`. `launcher`, `board`, `orchestrator-handbook`, `phase-handbooks`, `pr-handbook` and `spec-planner-handbooks` each depend on `foundation` until `merged`. `default-stack` depends on the other seven until `done`. The phases mix every state colour and all four scheduling values, and arrive unsorted. It has five pull requests: drafts #11 (rank 1, depends on `12`), `"12"` (rank 2, its number a digit string) and #13 (rank 3, depends on `[11, "12", 100, 9]`), open `"100"` and merged #9. #13's title carries `<b>` and `<img>` markup and its `url` is `javascript:alert(1)`. Four needs arrive out of order, one of them with a `javascript:` link in its summary and one with a 61-character pane. `board/recent` holds 22 items, with the second and third out of time order, so a page that re-sorts or fails to cap them shows it.

The map fixtures isolate drawing. `lanes-a` and `lanes-b` have five phases in three columns and two edges that skip the middle column. They differ only in which first-column phase each skipping edge leaves from, so a map that draws both alike has lost information. `long` has two phase ids of 40 characters that share their first 39, and `spec-planner-handbooks`.

The checker asserts, with exact expected values:

- the six section headings in order, in every scenario, and no page-level horizontal scroll at the frame's width in every scenario, light, dark and OS dark;
- Needs you: one-way decision, two-way decision, prompt (with its pane), restack, each with kind and door chips, phase, waiting time and summary, and a count of 4;
- Ready for your review: #12, #11 ("after #12"), #13 ("after #11, #12, #100"), with checks and update chips;
- Pull requests: all eight cells of each row, ordered #9, #11, #12, #13, #100, so digit-string numbers order as numbers;
- Phases: all seven cells of each of the eight rows, including the labels "session live", "session closed", "queued to start" and "blocked", and every Depends on entry;
- Recent changes: the first 20 items in stored order, with "→ Implement" for a null `from`;
- the dependency map: three columns, every node's state line, 13 edges with 7 dashed (computed `stroke-dasharray`) into `default-stack` and 6 solid from `foundation`, each edge identified by its end points, and no edge passing through any node other than its own two, sampled at 401 points with `getPointAtLength`; only `foundation` to `default-stack` skips a column; every node shows its full id;
- the map legend's exact text;
- node fill by state: four different fills for the four state tones in the full fixture, and each node's fill equal to the background of the same phase's state chip in the Phases table, in light, dark and OS dark;
- in every scenario with a map, node labels fit inside their nodes, the id text has a contrast of at least 4.5 to its node's fill and the state line at least 3, and each skipping edge has a horizontal run of more than 20 units that no other skipping edge's run overlaps;
- `lanes-a` and `lanes-b` both draw two skipping edges, and their edge geometry, sampled and rounded, differs;
- every id in `long` shown whole;
- the map's computed `overflow-x` is `auto` or `scroll`, and at 400 px its `scrollWidth` exceeds its `clientWidth`;
- staleness with `stale_after_min` absent (fresh at 39 minutes, stale at 41) and sent as 60 (fresh at 50, stale at 61), the banner text, the Fresh or Stale chip and the age; a 39.5-minute tick that turns stale after 61 s of virtual time with no write; an unreadable tick shown as stale;
- the no-database notice with every section hidden, the 10-second unreachable notice absent at 5 s and shown at 12 s with a silent stub, and cleared by data arriving at 11 s;
- with cached data only, every section's content but no Fresh or Stale verdict and no banner for a 180-minute tick, the age still shown, and the unreachable notice absent at 5 s and shown at 12 s;
- a stale verdict from live data kept, banner and chip, after cached data follows, and after the `board/meta` listener then fails; with cached data after live data, the unreachable notice at 12 s;
- a subscription error before data (Ready for your review and Pull requests show only the error line, the other sections keep their data) and after data (the error line above the rows already shown, and a heartbeat that stays stale when the `board/meta` listener dies);
- no call to any method other than the four reads, in any scenario;
- dark ground and light text in `dark` and OS dark, light ground in `light`;
- at 1000 px, no word of up to 16 characters split across lines and no chip clipped;
- `#11` still focused, on a new element, and the map's `scrollLeft` still 80, on a new map, after the second snapshot;
- at 700 px, the Pull requests table scrolled to its end inside its own box, and the same `scrollLeft` on the new table after the second snapshot;
- unknown dependency chips not clipped and inside the content box, in every scenario;
- no `b`, `img`, `script` or non-`https://` link in the page, and the markup shown as literal text;
- a missing dependency drawn as an "unknown" node coloured like an unknown state, a cycle shown as the line "The phases depend on each other in a cycle: alpha, beta. Fix depends_on in the feature plan." with no map and every dependency still listed, and unreadable entries, including a `depends_on` that is a string, listed as `unknown: <JSON>`.

Run it from the repository root. It needs Google Chrome at `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`, or the path in `CHROME`. Without Chrome it prints `PENDING: Google Chrome not found at <path>, so the board cannot be rendered here` and exits `0`. `TEMPLATE` points it at another copy of the template, which is how the mutation proof under Evidence runs it.

```bash
bash <<'EOF'
set -euo pipefail
template="${TEMPLATE:-$PWD/packages/s-stack/.apm/skills/sam-mode/assets/status-board.html}"
chrome="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
if [ ! -x "$chrome" ]; then echo "PENDING: Google Chrome not found at $chrome, so the board cannot be rendered here"; exit 0; fi
[ -f "$template" ] || { echo "FAIL: $template is missing"; exit 1; }
dir="$(mktemp -d)"
trap 'rm -rf "$dir"' EXIT

cat > "$dir/stub.js" <<'JS'
(() => {
  const q = new URLSearchParams(location.search);
  const theme = q.get("theme") || "light";
  if (theme !== "os") document.documentElement.setAttribute("data-theme", theme);
  const now = Date.now();
  const ago = (min) => new Date(now - min * 60000).toISOString();
  const meta = {feature: "placeholder-feature", orchestrator_branch: "placeholder-feature-orchestrator", default_branch: "main",
    architecture_url: "https://example.com/architecture",
    tick_at: q.get("tick") === "bad" ? "unreadable-" + "0123456789".repeat(6) : ago(Number(q.get("tick") || 5))};
  if (q.has("stale")) meta.stale_after_min = Number(q.get("stale"));
  const dep = (phase, until) => ({phase, until});
  const middle = ["launcher", "board", "orchestrator-handbook", "phase-handbooks", "pr-handbook", "spec-planner-handbooks"];
  const onFoundation = [dep("foundation", "merged")];
  const phase = (id, state, scheduling, min, depends_on, more) =>
    ({phase: id, state, scheduling, waits_for: null, session_live: false, pane: null, changed_at: ago(min), depends_on, ...more});
  const LONG = "orchestrator-handbook-and-phase-handboo";
  const lanes = (skips) => [phase("a1", "Plan", "queued", 5, []), phase("a2", "Plan", "queued", 5, []),
    phase("b1", "Plan", "queued", 5, [dep("a1", "merged")]), phase("b2", "Plan", "queued", 5, [dep("a2", "merged")]),
    ...skips.map(([c, a]) => phase(c, "Plan", "queued", 5, [dep("b" + c[1], "merged"), dep(a, "merged")]))];
  const recentItems = Array.from({length: 22}, (_, i) => ({
    at: ago([0, 10, 5][i] ?? i * 5), phase: "p" + String(i + 1).padStart(2, "0"), from: i === 0 ? null : "Plan", to: "Implement"}));
  const fixtures = {
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
        {number: "100", url: "https://example.com/pull/100", title: "Ready for a human", phase: "foundation", state: "open", checks: "none", base: "main", depends_on: [9], review_rank: null, needs_update: true},
        {number: "12", url: "https://example.com/pull/12", title: "Pull request B", phase: "launcher", state: "draft", checks: "pending", base: "main", depends_on: [], review_rank: 2, needs_update: false},
        {number: 9, url: "https://example.com/pull/9", title: "Merged groundwork", phase: "foundation", state: "merged", checks: "passing", base: "main", depends_on: [], review_rank: null, needs_update: false}],
      needs: [
        {kind: "restack", phase: "launcher", summary: "Restack launcher onto the merged foundation.", door: null, pane: null, since: ago(50)},
        {kind: "prompt", phase: "board", summary: "A permission prompt waits in the session.", door: null, pane: "%" + "1234567890".repeat(6), since: ago(4)},
        {kind: "decision", phase: "phase-handbooks", summary: "Choose the handbook layout.", door: "two-way", pane: null, since: ago(10)},
        {kind: "decision", phase: "default-stack", summary: "Approve the tag <a href=\"javascript:alert(2)\">now</a>", door: "one-way", pane: null, since: ago(23)}],
    },
    missing: {"board/meta": meta, phases: [phase("alpha", "Shipping", "weird", 5, [dep("ghost", "merged"), dep("<b>ghost</b>", "done")])]},
    cycle: {"board/meta": meta, phases: [
      phase("alpha", "Plan", "queued", 5, [dep("beta", "merged")]),
      phase("beta", "Plan", "queued", 5, [dep("alpha", "done")]),
      phase("gamma", "Plan", "queued", 5, [dep("alpha", "merged")])]},
    unreadable: {"board/meta": meta, phases: [
      phase("alpha", "Plan", "queued", 5, [{phase: 5, until: "merged"}, dep("beta", "later"), "beta"]),
      phase("beta", "Plan", "queued", 5, "alpha"),
      phase("gamma", "Plan", "queued", 5, [dep("alpha", "merged")])]},
    "lanes-a": {"board/meta": meta, phases: lanes([["c1", "a1"], ["c2", "a2"]])},
    "lanes-b": {"board/meta": meta, phases: lanes([["c1", "a2"], ["c2", "a1"]])},
    long: {"board/meta": meta, phases: [
      phase(LONG + "a", "Plan", "queued", 5, []),
      phase(LONG + "b", "Review", "queued", 5, [dep(LONG + "a", "merged")]),
      phase("spec-planner-handbooks", "Done", "closed", 5, [dep(LONG + "a", "done")])]},
    empty: {},
  };
  const data = fixtures[q.get("fixture") || "full"];
  const deliver = q.get("deliver") || "live";
  const errSource = q.get("error");
  window.__writes = [];
  const listeners = [];
  const snapshotOf = (path, fromCache = false) => {
    const metadata = {fromCache, hasPendingWrites: false};
    if (path.includes("/")) return {id: path.split("/")[1], exists: path in data, data: () => data[path], metadata};
    const docs = (data[path] || []).map((body, i) => ({id: String(i), exists: true, data: () => structuredClone(body), metadata}));
    return {docs, size: docs.length, empty: !docs.length, docChanges: () => [], metadata};
  };
  const source = (path) => ({meta: "board/meta", recent: "board/recent"}[errSource] || errSource) === path;
  const ref = (path) => ({
    onSnapshot(next, fail) {
      const emit = () => next(snapshotOf(path));
      const cached = () => next(snapshotOf(path, true));
      listeners.push(emit);
      const error = {code: "permission-denied", message: "stub"};
      if (["live", "error-after", "live-cached", "live-cached-error"].includes(deliver)) setTimeout(emit, 20);
      if (deliver === "cached") setTimeout(cached, 20);
      if (deliver === "live-cached" || deliver === "live-cached-error") setTimeout(cached, 300);
      if (deliver === "late") setTimeout(emit, 11000);
      if (deliver === "error-before" && source(path)) setTimeout(() => fail(error), 20);
      else if (deliver === "error-before") setTimeout(emit, 20);
      if (deliver === "error-after" && source(path)) setTimeout(() => fail(error), 300);
      if (deliver === "live-cached-error" && source(path)) setTimeout(() => fail(error), 600);
      return () => {};
    },
    get: async () => snapshotOf(path),
  });
  const READS = new Set(["onSnapshot", "get", "doc", "collection"]);
  const guarded = (target) => new Proxy(target, {
    has: () => true,
    get(t, key) {
      if (typeof key !== "string" || key === "then" || READS.has(key)) return t[key];
      return (...args) => { window.__writes.push(key); return Promise.resolve({ok: true}); };
    },
  });
  const db = guarded({doc: (p) => guarded(ref(p)), collection: (p) => guarded(Object.assign(ref(p), {doc: (id) => guarded(ref(p + "/" + id))}))});
  window.__reemit = () => listeners.forEach((emit) => emit());
  window.claude = {use: async (name) => (name === "db" && deliver !== "nodb" ? db : null)};
})();
JS

cat > "$dir/collect.js" <<'JS'
(() => {
  const q = new URLSearchParams(location.search);
  const text = (n) => (n ? n.innerText.trim().replace(/\s*\n\s*/g, " | ") : null);
  const shown = (n) => !!n && !n.closest("[hidden]") && n.getClientRects().length > 0;
  const bySection = (title) => [...document.querySelectorAll("main section")].find((s) => s.querySelector("h2").textContent === title);
  const svgBox = (g) => {
    const m = g.transform.baseVal.consolidate().matrix;
    const r = g.querySelector("rect");
    return {x: m.e, y: m.f, w: r.width.baseVal.value, h: r.height.baseVal.value};
  };
  function mapOf(section) {
    const svg = section.querySelector("svg");
    if (!svg) return null;
    const nodes = [...svg.querySelectorAll("g")].filter((g) => g.querySelector("rect")).map((g) => {
      const texts = [...g.querySelectorAll("text")];
      const rect = g.querySelector("rect");
      return {id: g.querySelector("title").textContent, lines: texts.map((t) => t.textContent),
        fill: getComputedStyle(rect).fill, textFill: texts.map((t) => getComputedStyle(t).fill),
        fits: texts.every((t) => t.x.baseVal[0].value + t.getComputedTextLength() <= rect.width.baseVal.value - 2), ...svgBox(g)};
    });
    const xs = [...new Set(nodes.map((n) => n.x))].sort((a, b) => a - b);
    const at = (p, side) => nodes.find((n) => Math.abs((side === "out" ? n.x + n.w : n.x) - p.x) < 0.5 && p.y >= n.y && p.y <= n.y + n.h);
    const geometry = new Set();
    const edges = [...svg.querySelectorAll("path")].filter((p) => p.getAttribute("marker-end")).map((p) => {
      const len = p.getTotalLength();
      const from = at(p.getPointAtLength(0), "out"), to = at(p.getPointAtLength(len), "in");
      const crosses = new Set();
      const pts = [];
      for (let i = 0; i <= 400; i++) {
        const pt = p.getPointAtLength((len * i) / 400);
        pts.push(pt);
        geometry.add(Math.round(pt.x) + "," + Math.round(pt.y));
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
      const dash = getComputedStyle(p).strokeDasharray;
      const skips = !!(from && to) && xs.indexOf(to.x) - xs.indexOf(from.x) > 1;
      return {from: from && from.id, to: to && to.id, dashed: dash !== "none" && dash !== "", crosses: [...crosses], skips, run};
    });
    return {columns: xs.length, nodes, edges, scrollLeft: svg.parentElement.scrollLeft,
      scrollable: svg.parentElement.scrollWidth > svg.parentElement.clientWidth,
      overflowX: getComputedStyle(svg.parentElement).overflowX, geometry: [...geometry].sort().join(" ")};
  }
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
        const tops = new Set([...range.getClientRects()].filter((r) => r.width > 0).map((r) => Math.round(r.top)));
        if (tops.size > 1) broken.push(m[0]);
      }
    }
    for (const c of document.querySelectorAll(".chip")) if (shown(c) && c.scrollWidth > c.clientWidth) broken.push("chip:" + c.textContent);
    return broken;
  }
  function snapshot() {
    const root = document.documentElement;
    const sections = [...document.querySelectorAll("main section")].map((s) => ({
      title: s.querySelector("h2") && s.querySelector("h2").textContent,
      count: text(s.querySelector("h2 + *")),
      shown: shown(s),
      text: text(s),
      items: [...s.querySelectorAll("ul > li, ol > li")].map(text),
      rows: [...s.querySelectorAll("tbody tr")].map((tr) => [...tr.cells].map(text)),
      map: mapOf(s),
    }));
    const chipBg = (label) => {
      const c = [...document.querySelectorAll(".chip")].find((n) => n.textContent === label);
      return c ? getComputedStyle(c).backgroundColor : null;
    };
    return {
      width: root.clientWidth,
      noHorizontalScroll: root.scrollWidth <= root.clientWidth,
      title: document.title,
      h1: text(document.querySelector("h1")),
      headerLinks: [...document.querySelectorAll("header a")].map((a) => a.href),
      banner: [...document.querySelectorAll("header *")].filter((n) => shown(n) && /ticked|tick yet/.test(n.textContent) && !n.children.length).map(text),
      notices: [...document.querySelectorAll("body *")].filter((n) => shown(n) && !n.closest("main") && !n.closest("header") && n.children.length === 0 && n.textContent.trim()).map(text),
      sections,
      injected: document.querySelectorAll("main b, main img, main script, main a:not([href^='https://'])").length,
      links: [...document.querySelectorAll("a")].map((a) => a.getAttribute("href")),
      chipBg: Object.fromEntries(["one-way", "two-way", "session closed", "Spec", "Done", "blocked", "queued to start", "session live"].map((l) => [l, chipBg(l)])),
      stateChipBg: Object.fromEntries([...(bySection("Phases")?.querySelectorAll("tbody tr") || [])].map((tr) =>
        [tr.cells[0].textContent, tr.cells[1].querySelector(".chip") && getComputedStyle(tr.cells[1].querySelector(".chip")).backgroundColor])),
      depChips: depChips(),
      prTable: (() => {
        const wrap = bySection("Pull requests")?.querySelector("table")?.parentElement;
        return wrap && {scrollLeft: wrap.scrollLeft, overflow: wrap.scrollWidth - wrap.clientWidth, replaced: wrap !== window.__table};
      })(),
      fg: getComputedStyle(document.body).color,
      bg: getComputedStyle(document.body).backgroundColor,
      dark: matchMedia("(prefers-color-scheme: dark)").matches,
      broken: q.get("words") ? brokenWords() : [],
      writes: window.__writes.slice(),
      focus: document.activeElement && document.activeElement !== document.body
        ? {section: document.activeElement.closest("section").querySelector("h2").textContent, text: text(document.activeElement),
          replaced: document.activeElement !== window.__focused} : null,
      mapReplaced: document.querySelector("main svg") !== window.__map,
    };
  }
  const times = (q.get("at") || "1500").split(",").map(Number);
  const out = {};
  times.forEach((t) => setTimeout(() => { out[t] = snapshot(); }, t));
  const last = times[times.length - 1];
  if (q.get("interact")) {
    setTimeout(() => {
      if (q.get("interact") === "table") {
        document.head.append(Object.assign(document.createElement("style"), {textContent: ".table-wrap table { min-width: 1200px; }"}));
        window.__table = bySection("Pull requests").querySelector("table").parentElement;
        window.__table.scrollLeft = window.__table.scrollWidth;
      } else {
        [...bySection("Ready for your review").querySelectorAll("a")].find((a) => a.textContent === "#11").focus();
        document.querySelector("main svg").parentElement.scrollLeft = 80;
        window.__focused = document.activeElement;
        window.__map = document.querySelector("main svg");
      }
      out.before = snapshot();
      window.__reemit();
    }, last + 100);
    setTimeout(() => { out.after = snapshot(); parent.postMessage(JSON.stringify(out), "*"); }, last + 600);
  } else {
    setTimeout(() => parent.postMessage(JSON.stringify(out), "*"), last + 50);
  }
})();
JS

cat > "$dir/frame.html" <<'HTML'
<!doctype html><html><body style="margin:0"><script>
const q = new URLSearchParams(location.search);
const f = document.createElement("iframe");
f.style.cssText = "border:0;height:1400px;width:" + (q.get("w") || 400) + "px";
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

while read -r budget flags scenario; do
  echo "== $scenario"
  [ "$flags" = - ] && flags=""
  "$chrome" --headless --disable-gpu --hide-scrollbars --user-data-dir="$dir/profile" $flags --window-size=1100,1500 \
    --virtual-time-budget="$budget" --dump-dom "file://$dir/frame.html?$scenario" 2>/dev/null || true
done > "$dir/out.txt" <<'LIST'
5000 - theme=light&tick=41&interact=1
5000 - theme=dark&tick=39
5000 --blink-settings=preferredColorScheme=0 theme=os&tick=5
5000 - theme=light&stale=60&tick=50
5000 - theme=light&stale=60&tick=61
65000 - theme=light&tick=39.5&at=1500,61000
5000 - theme=dark&tick=bad
5000 - theme=light&tick=5&w=1000&words=1
5000 - theme=dark&tick=5&w=1000&words=1
5000 - theme=light&fixture=empty
5000 - theme=dark&fixture=missing
5000 - theme=light&fixture=cycle
5000 - theme=light&fixture=unreadable
5000 - theme=light&deliver=nodb
20000 - theme=light&deliver=silent&at=5000,12000
20000 - theme=light&deliver=late&at=5000,10500,12500
5000 - theme=light&deliver=error-before&error=prs
5000 - theme=light&deliver=error-after&error=prs
5000 - theme=light&deliver=error-after&error=meta&tick=41
20000 - theme=light&deliver=cached&tick=180&at=5000,12000
20000 - theme=dark&deliver=live-cached&tick=41&at=5000,12000
5000 - theme=light&deliver=live-cached-error&error=meta&tick=41
5000 - theme=light&w=700&interact=table
5000 - theme=light&fixture=lanes-a
5000 - theme=light&fixture=lanes-b
5000 - theme=dark&fixture=long
LIST

cat > "$dir/check.py" <<'PY'
import html, json, re, sys

HEADINGS = ["Needs you", "Ready for your review", "Pull requests", "Phases", "Recent changes", "Heartbeat"]
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
STATES = {row[0]: row[1] for row in PHASES}
EDGES = {("foundation", p, False) for p in MIDDLE} | {(p, "default-stack", True) for p in ["foundation"] + MIDDLE}
RECENT = ["p01 | → Implement"] + [f"p{i:02d} | Plan → Implement" for i in range(2, 21)]
EMPTIES = ["Nothing needs you.", "No draft pull requests yet.", "No pull requests yet.",
           "No phases yet. The orchestrator adds them once the feature plan exists.", "No state changes yet.", "No tick recorded yet."]
STOPPED = "This section stopped updating (permission-denied). Reload the page to try again."
NODB = "This board reads its data from the page's database, which this view cannot open. Open the board in Claude."
SLOW = "The board's data can't be reached yet. What is shown may be out of date."
LEGEND = ("Solid line: needed merged into the orchestrator branch. "
          "Dashed line: needed with every pull request merged into the default branch.")
LONG = "orchestrator-handbook-and-phase-handboo"
def STALE(n): return f"The orchestrator has not ticked for {n} minutes."


def contrast(a, b):
    def lum(rgb):
        c = [int(v) / 255 for v in re.findall(r"[\d.]+", rgb)[:3]]
        c = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    hi, lo = sorted((lum(a), lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def runs_overlap(a, b):
    return abs(a["y"] - b["y"]) < 1 and min(a["x2"], b["x2"]) - max(a["x1"], b["x1"]) > 1


def sec(snap, title):
    missing = {"title": title, "count": None, "shown": False, "text": "", "items": [], "rows": [], "map": None}
    return next((s for s in snap["sections"] if s["title"] == title), missing)


def full_content(c, s):
    c("header names the feature and links the architecture page", s["h1"] == "placeholder-feature"
      and s["title"] == "placeholder-feature status board" and s["headerLinks"] == ["https://example.com/architecture"])
    c("Needs you: decisions first, then prompts, then restacks, oldest first", sec(s, "Needs you")["items"] == NEEDS)
    c("Needs you count", sec(s, "Needs you")["count"] == "4")
    c("Ready for your review: drafts in dependency order with after notes", sec(s, "Ready for your review")["items"] == REVIEW)
    c("Pull requests: every row, ordered by number", sec(s, "Pull requests")["rows"] == PRS)
    c("Phases: every row with scheduling labels and Depends on", sec(s, "Phases")["rows"] == PHASES)
    recent = sec(s, "Recent changes")
    c("Recent changes: first 20 in stored order", [i.split(" | ", 1)[1] for i in recent["items"]] == RECENT and recent["count"] == "20")
    m = sec(s, "Phases")["map"] or {"columns": 0, "nodes": [], "edges": []}
    c("map: three columns", m["columns"] == 3)
    c("map: every node names its state", {n["id"]: n["lines"][1] for n in m["nodes"]} == STATES)
    edges = {(e["from"], e["to"], e["dashed"]) for e in m["edges"]}
    c("map: 13 edges, 7 dashed into default-stack and 6 solid from foundation", len(m["edges"]) == 13 and edges == EDGES)
    c("map: no edge crosses a node", all(not e["crosses"] for e in m["edges"]))
    c("map: one skipping edge, foundation to default-stack", [(e["from"], e["to"]) for e in m["edges"] if e["skips"]] == [("foundation", "default-stack")])
    c("map: every node names its full id", all(n["lines"][0] == n["id"] for n in m["nodes"]))
    c("map: legend explains solid and dashed lines", LEGEND in sec(s, "Phases")["text"])
    c("map: scrolls inside its own box at 400 px", m.get("overflowX") in ("auto", "scroll") and (m.get("scrollable") or s["width"] != 400))
    fills = {n["id"]: n["fill"] for n in m["nodes"]}
    c("map: node fill matches the state chip of the same phase", fills == s["stateChipBg"])
    c("map: node fill differs by state", len(set(fills.values())) == 4)
    bg = s["chipBg"]
    c("one-way door is critical, two-way is not", bg["one-way"] != bg["two-way"])
    c("session closed is neutral, not the done colour", bg["session closed"] == bg["Spec"] != bg["Done"] and bg["blocked"] != bg["session closed"])
    c("no data becomes markup or an unsafe link", s["injected"] == 0 and all(h.startswith("https://") for h in s["links"]))


def heartbeat(c, s, stale, minutes):
    hb = sec(s, "Heartbeat")["text"]
    c(f"{'stale' if stale else 'fresh'} at {minutes} min", s["banner"] == ([STALE(minutes)] if stale else [])
      and ("Stale" if stale else "Fresh") in hb and age_text(minutes) in hb)


def age_text(minutes):
    return f"{minutes} min ago" if minutes < 60 else f"{minutes // 60} h {minutes % 60} min ago"


def map_case(c, s, fixture):
    phases = sec(s, "Phases")
    m = phases["map"]
    deps = {r[0]: r[4] for r in phases["rows"]}
    if fixture == "missing":
        nodes = {n["id"]: n for n in (m or {"nodes": []})["nodes"]}
        c("a missing dependency draws an unknown node", set(nodes) == {"alpha", "ghost", "<b>ghost</b>"} and nodes["ghost"]["lines"] == ["ghost", "unknown"]
          and nodes["<b>ghost</b>"]["lines"] == ["<b>ghost</b>", "unknown"]
          and nodes["alpha"]["lines"][1] == "unknown: Shipping" and nodes["ghost"]["fill"] == nodes["alpha"]["fill"])
        c("an unknown state and scheduling read as unknown", phases["rows"][0][1:3] == ["unknown: Shipping", "unknown: weird"])
    if fixture == "cycle":
        c("a cycle shows the error line and no map", m is None
          and "The phases depend on each other in a cycle: alpha, beta. Fix depends_on in the feature plan." in phases["text"])
        c("a cycle still lists every dependency", deps == {"alpha": "beta (merged)", "beta": "alpha (done)", "gamma": "alpha (merged)"})
    if fixture == "unreadable":
        c("unreadable depends_on entries show as unknown", deps == {
            "alpha": 'unknown: {"phase":5,"until":"merged"} | unknown: {"phase":"beta","until":"later"} | unknown: "beta"',
            "beta": 'unknown: "alpha"', "gamma": "alpha (merged)"})
        c("every unknown entry is a chip", len(s["depChips"]) == 4)
        c("only readable entries are drawn", m is not None and [(e["from"], e["to"]) for e in m["edges"]] == [("alpha", "gamma")])


def map_drawing(c, s):
    m = sec(s, "Phases")["map"]
    if not m:
        return
    c("map: labels fit inside their nodes", all(n["fits"] for n in m["nodes"]))
    c("map: node text is readable on its fill", all(contrast(n["textFill"][0], n["fill"]) >= 4.5
      and contrast(n["textFill"][1], n["fill"]) >= 3 for n in m["nodes"]))
    skips = [e for e in m["edges"] if e["skips"]]
    c("map: each skipping edge has a horizontal run of its own", all(e["run"] and e["run"]["x2"] - e["run"]["x1"] > 20 for e in skips)
      and not any(runs_overlap(a["run"], b["run"]) for i, a in enumerate(skips) for b in skips[i + 1:]))


def check(name, r):
    failures = []
    def c(label, ok):
        if not ok:
            failures.append(label)
    q = dict(p.split("=", 1) for p in name.split("&"))
    snaps = [r[k] for k in sorted((k for k in r if k.isdigit()), key=int)]
    s = snaps[-1]
    for snap in snaps + [r[k] for k in ("before", "after") if k in r]:
        c("the page never writes", snap["writes"] == [])
        c("six headings in order", [x["title"] for x in snap["sections"]] == HEADINGS)
        c("frame at the asked width with no horizontal scroll", snap["width"] == int(q.get("w", 400)) and snap["noHorizontalScroll"])
        c("unknown dependency chips wrap inside the page", all(not d["clipped"] and d["inside"] for d in snap["depChips"]))
        map_drawing(c, snap)
    deliver = q.get("deliver", "live")
    fixture = q.get("fixture", "full")
    if deliver in ("live", "cached", "live-cached") and fixture == "full" and q.get("tick") != "bad":
        full_content(c, snaps[0])
    if deliver == "live" and fixture == "full" and q.get("tick") != "bad":
        c("no notice once every source is live", s["notices"] == [])
    if "stale" in q or (deliver == "live" and fixture == "full" and q.get("tick") not in (None, "bad") and "at" not in q):
        limit = float(q.get("stale", 40))
        heartbeat(c, s, float(q["tick"]) > limit, int(float(q["tick"])))
    if "at" in q and deliver == "live":
        heartbeat(c, snaps[0], False, 39)
        heartbeat(c, snaps[1], True, 40)
    if q.get("tick") == "bad":
        c("an unreadable tick is stale", s["banner"] == ["The orchestrator has not recorded a readable tick yet."]
          and "Stale" in sec(s, "Heartbeat")["text"])
    if q.get("interact") == "table":
        before, after = r["before"]["prTable"], r["after"]["prTable"]
        c("the Pull requests table scrolls inside its box between 601 and 960 px", before["overflow"] > 0 and before["scrollLeft"] == before["overflow"])
        c("table scrollLeft survives a second snapshot", after["replaced"] and after["scrollLeft"] == before["scrollLeft"])
    elif q.get("interact"):
        before, after = r["before"], r["after"]
        c("focus and map scroll set before the second snapshot", before["focus"]["text"] == "#11"
          and sec(before, "Phases")["map"]["scrollLeft"] == 80)
        c("focus survives a second snapshot", after["focus"] == {"section": "Ready for your review", "text": "#11", "replaced": True})
        c("map scrollLeft survives a second snapshot", after["mapReplaced"] and sec(after, "Phases")["map"]["scrollLeft"] == 80)
    if q.get("theme") in ("dark", "os"):
        c("dark theme: dark ground, light text", s["dark"] and s["bg"] == "rgb(16, 20, 27)" and s["fg"] != s["bg"])
    if q.get("theme") == "light":
        c("light theme: light ground", s["bg"] == "rgb(245, 247, 250)" and s["fg"] != s["bg"])
    if q.get("words"):
        c("no chip or short word broken at 1000 px", s["broken"] == [])
    if fixture == "empty":
        c("every section shows its empty state", [x["text"].split(" | ")[-1] for x in s["sections"]] == EMPTIES)
    c("no data becomes markup", s["injected"] == 0)
    if fixture in ("missing", "cycle", "unreadable"):
        map_case(c, s, fixture)
    if deliver == "nodb":
        c("no database: one notice and no sections", s["notices"] == [NODB] and not any(x["shown"] for x in s["sections"]))
    if deliver == "silent":
        c("no notice before 10 s", snaps[0]["notices"] == [])
        c("unreachable notice after 10 s", s["notices"] == [SLOW])
    if deliver == "late":
        c("no notice before 10 s", snaps[0]["notices"] == [])
        c("unreachable notice after 10 s", snaps[1]["notices"] == [SLOW])
        c("the first live data clears the notice", s["notices"] == [] and sec(s, "Ready for your review")["items"] == REVIEW)
    if deliver == "error-before":
        for title in ("Ready for your review", "Pull requests"):
            c(f"{title}: error before data", sec(s, title)["text"] == title.upper() + " | " + STOPPED)
        c("other sections keep working", sec(s, "Needs you")["items"] == NEEDS and sec(s, "Phases")["rows"] == PHASES)
    if deliver == "error-after" and q["error"] == "prs":
        c("Pull requests: error after data keeps the rows", STOPPED in sec(s, "Pull requests")["text"] and sec(s, "Pull requests")["rows"] == PRS)
        c("Ready for your review: error after data keeps the list", STOPPED in sec(s, "Ready for your review")["text"]
          and sec(s, "Ready for your review")["items"] == REVIEW)
    if deliver == "cached":
        hb = sec(s, "Heartbeat")["text"]
        c("a cached tick never calls the board stale or fresh", all(x["banner"] == [] and "Stale" not in sec(x, "Heartbeat")["text"]
          and "Fresh" not in sec(x, "Heartbeat")["text"] for x in snaps) and age_text(180) in hb)
        c("cached data: no notice before 10 s, the unreachable notice after", snaps[0]["notices"] == [] and s["notices"] == [SLOW])
    if deliver in ("live-cached", "live-cached-error"):
        c("a live stale verdict survives a cached snapshot", all(x["banner"] == [STALE(41)] and "Stale" in sec(x, "Heartbeat")["text"] for x in snaps))
    if deliver == "live-cached":
        c("cached data after live: no notice before 10 s, the unreachable notice after", snaps[0]["notices"] == [] and s["notices"] == [SLOW])
    if deliver == "live-cached-error":
        c("the heartbeat shows the error after cached data", STOPPED in sec(s, "Heartbeat")["text"])
    if fixture.startswith("lanes-"):
        m = sec(s, "Phases")["map"] or {"edges": []}
        c("lane graphs: two skipping edges", sum(e["skips"] for e in m["edges"]) == 2)
    if fixture == "long":
        nodes = {n["id"]: n["lines"][0] for n in (sec(s, "Phases")["map"] or {"nodes": []})["nodes"]}
        c("map: ids of up to 40 characters are shown whole", nodes == {LONG + "a": LONG + "a", LONG + "b": LONG + "b",
          "spec-planner-handbooks": "spec-planner-handbooks"})
    if deliver == "error-after" and q["error"] == "meta":
        c("heartbeat error after data keeps the stale verdict", STOPPED in sec(s, "Heartbeat")["text"] and s["banner"] == [STALE(41)]
          and "Stale" in sec(s, "Heartbeat")["text"])
    return failures


chunks = re.split(r"^== (\S+)$", open(sys.argv[1]).read(), flags=re.M)[1:]
failures = []
results = {}
for name, dom in zip(chunks[::2], chunks[1::2]):
    m = re.search(r'data-result="([^"]*)"', dom)
    try:
        results[name] = json.loads(html.unescape(m.group(1))) if m else None
        bad = check(name, results[name]) if m else ["the page produced no result"]
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

Expected: exit `0`, one `ok` line for each of the 26 scenarios and one for `lanes-a against lanes-b`, then `board renders as specified`. A failing assertion prints `FAIL`, the scenario and the name of each failed check, then `<n> failed checks`, and exits `1`. A page that crashes or produces no result fails its scenario the same way.

## Evidence

The phase's verifier runs these at every code head it verifies and puts every result in its report, never in this file. Every page, row and name is placeholder data.

### Mutation proof

This shows that the `## Rerun` check fails a broken template. Extract the one bash block between `## Rerun` and `## Evidence` from this file into a script outside the repository. Run it once on the real template, which must exit `0`, and once with `CHROME=/nonexistent`, which must print the PENDING line and exit `0`. Then, in a scratch directory outside the repository, write each mutant as a copy of the current template with one text replacement, refusing any replacement whose target text does not occur exactly once, and run the extracted script on each copy through `TEMPLATE`. Every mutant must make it exit `1`.

The mutants cover each behaviour the Rerun asserts, and every broken template that a review gate has reported: the stale threshold and its default, the 30-second re-render, Recent changes, the no-database, unreachable and subscription-error states, every table's rows, order and labels, the review order and its "after" notes, digit-string numbers, the page writing through any method, including `acquire` and a method not in the API, the light, dark and OS dark themes, the phone layout, long values widening the page, focus and both scroll positions across a re-render, injection, the dependency map's layers, dashes, lanes, node colours, labels, legend, scrolling, unknown nodes, cycles and unreadable entries, a cached tick trusted, cached data counted as live, cached data not raising the unreachable notice, and a live stale verdict lost when a cached snapshot follows. A mutant whose target text the template no longer holds is rewritten by hand as the same fault against the current code.

### Published test page

This shows that the template works as a published page fed only through its database. Copy the template unchanged to a scratch file and publish it once with the Artifact tool, private, with the capabilities and icon its schema comment names and `title: "placeholder-feature status board"`. The page stays private.

Batch 1 is one `ArtifactData` batch of `set` writes in this run's shape:

- `board/meta`, with an `https://example.com/` architecture URL and a fresh `tick_at`;
- `board/recent` with a few items, newest first;
- eight `phases` with mixed states and scheduling values: `foundation` with `depends_on: []`, `launcher`, `board`, `orchestrator-handbook`, `phase-handbooks`, `pr-handbook` and `spec-planner-handbooks` each on `foundation` until `merged`, and `default-stack` on the other seven until `done`;
- three `prs`, one of which depends on the other two;
- two `needs`, a one-way decision and a prompt with a pane.

Batch 2 is one `update` of `board/meta` that sets `tick_at` 41 minutes back. The page must then show the stale banner and the Stale chip, and the artifact's version must not change, which shows nothing was published again.

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
