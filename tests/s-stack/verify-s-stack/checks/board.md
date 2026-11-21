# Phase `board` checks

Phase `board` ships `packages/s-stack/.apm/skills/sam-mode/assets/status-board.html`, the status board template. An orchestrator publishes it once per feature and then writes only to the page's database. The behavioural checks render the template with a stubbed database in headless Chrome and compare what the page shows with exact expected values.

## Rerun

### Rendered board in headless Chrome

The script writes its harness to a fresh `mktemp` directory and never writes into the repository. It wraps the template in the skeleton the Artifact tool publishes, which includes `[hidden]{display:none!important}`, and defines `window.claude.use("db")` as a stub. The stub serves placeholder documents with `fromCache: false`, and its `doc` and `collection` references also expose `set`, `update`, `delete` and `add`, which record every call. Headless Chrome will not make a window narrower than 500 px, so the page runs in an `iframe` 400 px wide (1000 px for the word-break scenarios), and the script reads that frame's own `scrollWidth` and `clientWidth`. Chrome's virtual time runs the 10-second and 30-second timers without waiting.

Each line of the `LIST` block is one scenario: a virtual-time budget in milliseconds, extra Chrome flags (`-` for none) and the query string the stub and collector read.

- `theme` is `light` or `dark`, set as `data-theme` on the root element, or `os`, which sets no `data-theme` and runs Chrome with `--blink-settings=preferredColorScheme=0` so the page's own `prefers-color-scheme: dark` block must apply.
- `tick` is the age of `tick_at` in minutes, or `bad` for an unreadable 71-character string. `stale` sends `stale_after_min`; without it the field is absent.
- `fixture` is `full` (the default), `empty`, `missing`, `cycle` or `unreadable`. `deliver` is `live` (the default, data after 20 ms), `silent` (never), `late` (after 11 s), `nodb` (`use("db")` resolves `null`), `error-before` or `error-after`, with `error` naming the source whose listener fails with `permission-denied`.
- `at` lists the virtual times at which the page is read. `interact` focuses the `#11` link in Ready for your review, scrolls the dependency map to 80 px, then sends every listener a second, identical snapshot. `words` checks word breaks.

The full fixture uses this run's phase shape. `foundation` has `depends_on: []`. `launcher`, `board`, `orchestrator-handbook`, `phase-handbooks`, `pr-handbook` and `spec-planner-handbooks` each depend on `foundation` until `merged`. `default-stack` depends on the other seven until `done`. The phases mix every state colour and all four scheduling values, and arrive unsorted. It has five pull requests: drafts #11 (rank 1, depends on `12`), `"12"` (rank 2, its number a digit string) and #13 (rank 3, depends on `[11, "12", 100, 9]`), open `"100"` and merged #9. #13's title carries `<b>` and `<img>` markup and its `url` is `javascript:alert(1)`. Four needs arrive out of order, one of them with a `javascript:` link in its summary and one with a 61-character pane. `board/recent` holds 22 items, with the second and third out of time order, so a page that re-sorts or fails to cap them shows it.

The checker asserts, with exact expected values:

- the six section headings in order, in every scenario, and no page-level horizontal scroll in every 400 px scenario, light, dark and OS dark;
- Needs you: one-way decision, two-way decision, prompt (with its pane), restack, each with kind and door chips, phase, waiting time and summary, and a count of 4;
- Ready for your review: #12, #11 ("after #12"), #13 ("after #11, #12, #100"), with checks and update chips;
- Pull requests: all eight cells of each row, ordered #9, #11, #12, #13, #100, so digit-string numbers order as numbers;
- Phases: all seven cells of each of the eight rows, including the labels "session live", "session closed", "queued to start" and "blocked", and every Depends on entry;
- Recent changes: the first 20 items in stored order, with "→ Implement" for a null `from`;
- the dependency map: three columns, every node's state line, 13 edges with 7 dashed (computed `stroke-dasharray`) into `default-stack` and 6 solid from `foundation`, each edge identified by its end points, and no edge passing through any node other than its own two, sampled at 401 points with `getPointAtLength`;
- staleness with `stale_after_min` absent (fresh at 39 minutes, stale at 41) and sent as 60 (fresh at 50, stale at 61), the banner text, the Fresh or Stale chip and the age; a 39.5-minute tick that turns stale after 61 s of virtual time with no write; an unreadable tick shown as stale;
- the no-database notice with every section hidden, the 10-second unreachable notice absent at 5 s and shown at 12 s with a silent stub, and cleared by data arriving at 11 s;
- a subscription error before data (Ready for your review and Pull requests show only the error line, the other sections keep their data) and after data (the error line above the rows already shown, and a heartbeat that stays stale when the `board/meta` listener dies);
- no call to any write verb in any scenario;
- dark ground and light text in `dark` and OS dark, light ground in `light`;
- at 1000 px, no word of up to 16 characters split across lines and no chip clipped;
- `#11` still focused, on a new element, and the map's `scrollLeft` still 80, on a new map, after the second snapshot;
- no `b`, `img`, `script` or non-`https://` link in the page, and the markup shown as literal text;
- a missing dependency drawn as an "unknown" node coloured like an unknown state, a cycle shown as the line "The phases depend on each other in a cycle: alpha, beta. Fix depends_on in the feature plan." with no map and every dependency still listed, and unreadable entries, including a `depends_on` that is a string, listed as `unknown: <JSON>`.

Run it from the repository root. It needs Google Chrome at `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`, or the path in `CHROME`. Without Chrome it prints `PENDING: Google Chrome not found at <path>, so the board cannot be rendered here` and exits `0`. `TEMPLATE` points it at another copy of the template, which is how the mutation evidence below was produced.

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
    empty: {},
  };
  const data = fixtures[q.get("fixture") || "full"];
  const deliver = q.get("deliver") || "live";
  const errSource = q.get("error");
  window.__writes = [];
  const listeners = [];
  const snapshotOf = (path) => {
    const metadata = {fromCache: false, hasPendingWrites: false};
    if (path.includes("/")) return {id: path.split("/")[1], exists: path in data, data: () => data[path], metadata};
    const docs = (data[path] || []).map((body, i) => ({id: String(i), exists: true, data: () => structuredClone(body), metadata}));
    return {docs, size: docs.length, empty: !docs.length, docChanges: () => [], metadata};
  };
  const source = (path) => ({meta: "board/meta", recent: "board/recent"}[errSource] || errSource) === path;
  const ref = (path) => ({
    onSnapshot(next, fail) {
      const emit = () => next(snapshotOf(path));
      listeners.push(emit);
      const error = {code: "permission-denied", message: "stub"};
      if (deliver === "live" || deliver === "error-after") setTimeout(emit, 20);
      if (deliver === "late") setTimeout(emit, 11000);
      if (deliver === "error-before" && source(path)) setTimeout(() => fail(error), 20);
      else if (deliver === "error-before") setTimeout(emit, 20);
      if (deliver === "error-after" && source(path)) setTimeout(() => fail(error), 300);
      return () => {};
    },
    get: async () => snapshotOf(path),
  });
  const write = (verb) => (...args) => { window.__writes.push(verb); return Promise.resolve(); };
  const writable = (r) => Object.assign(r, {set: write("set"), update: write("update"), delete: write("delete"), add: write("add")});
  const db = writable({doc: (p) => writable(ref(p)), collection: (p) => writable(Object.assign(ref(p), {doc: (id) => writable(ref(p + "/" + id))}))});
  window.__reemit = () => listeners.forEach((emit) => emit());
  window.claude = {use: async (name) => (name === "db" && deliver !== "nodb" ? db : null)};
})();
JS

cat > "$dir/collect.js" <<'JS'
(() => {
  const q = new URLSearchParams(location.search);
  const text = (n) => (n ? n.innerText.trim().replace(/\s*\n\s*/g, " | ") : null);
  const shown = (n) => !!n && !n.closest("[hidden]") && n.getClientRects().length > 0;
  const svgBox = (g) => {
    const m = g.transform.baseVal.consolidate().matrix;
    const r = g.querySelector("rect");
    return {x: m.e, y: m.f, w: r.width.baseVal.value, h: r.height.baseVal.value};
  };
  function mapOf(section) {
    const svg = section.querySelector("svg");
    if (!svg) return null;
    const nodes = [...svg.querySelectorAll("g")].filter((g) => g.querySelector("rect")).map((g) => ({
      id: g.querySelector("title").textContent, lines: [...g.querySelectorAll("text")].map((t) => t.textContent),
      fill: getComputedStyle(g.querySelector("rect")).fill, ...svgBox(g)}));
    const at = (p, side) => nodes.find((n) => Math.abs((side === "out" ? n.x + n.w : n.x) - p.x) < 0.5 && p.y >= n.y && p.y <= n.y + n.h);
    const edges = [...svg.querySelectorAll("path")].filter((p) => p.getAttribute("marker-end")).map((p) => {
      const len = p.getTotalLength();
      const from = at(p.getPointAtLength(0), "out"), to = at(p.getPointAtLength(len), "in");
      const crosses = new Set();
      for (let i = 0; i <= 400; i++) {
        const pt = p.getPointAtLength((len * i) / 400);
        for (const n of nodes) {
          if (n === from || n === to) continue;
          if (pt.x > n.x + 1 && pt.x < n.x + n.w - 1 && pt.y > n.y + 1 && pt.y < n.y + n.h - 1) crosses.add(n.id);
        }
      }
      const dash = getComputedStyle(p).strokeDasharray;
      return {from: from && from.id, to: to && to.id, dashed: dash !== "none" && dash !== "", crosses: [...crosses]};
    });
    return {columns: new Set(nodes.map((n) => n.x)).size, nodes, edges, scrollLeft: svg.parentElement.scrollLeft,
      scrollable: svg.parentElement.scrollWidth > svg.parentElement.clientWidth};
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
      const review = [...document.querySelectorAll("main section")].find((s) => s.querySelector("h2").textContent === "Ready for your review");
      [...review.querySelectorAll("a")].find((a) => a.textContent === "#11").focus();
      document.querySelector("main svg").parentElement.scrollLeft = 80;
      window.__focused = document.activeElement;
      window.__map = document.querySelector("main svg");
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
def STALE(n): return f"The orchestrator has not ticked for {n} minutes."


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
        c("only readable entries are drawn", m is not None and [(e["from"], e["to"]) for e in m["edges"]] == [("alpha", "gamma")])


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
        if q.get("w") != "1000":
            c("400 px frame with no horizontal scroll", snap["width"] == 400 and snap["noHorizontalScroll"])
    deliver = q.get("deliver", "live")
    fixture = q.get("fixture", "full")
    if deliver == "live" and fixture == "full" and q.get("tick") != "bad":
        full_content(c, snaps[0])
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
    if q.get("interact"):
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
    if deliver == "error-after" and q["error"] == "meta":
        c("heartbeat error after data keeps the stale verdict", STOPPED in sec(s, "Heartbeat")["text"] and s["banner"] == [STALE(41)]
          and "Stale" in sec(s, "Heartbeat")["text"])
    return failures


chunks = re.split(r"^== (\S+)$", open(sys.argv[1]).read(), flags=re.M)[1:]
failures = []
for name, dom in zip(chunks[::2], chunks[1::2]):
    m = re.search(r'data-result="([^"]*)"', dom)
    try:
        bad = check(name, json.loads(html.unescape(m.group(1)))) if m else ["the page produced no result"]
    except Exception as exc:
        bad = [f"the page result could not be read ({exc!r})"]
    print(f"{'FAIL' if bad else 'ok  '} {name}" + (": " + "; ".join(bad) if bad else ""))
    failures += bad
print(f"{len(failures)} failed checks" if failures else "board renders as specified")
sys.exit(1 if failures else 0)
PY
python3 "$dir/check.py" "$dir/out.txt"
EOF
```

Expected: exit `0`, one `ok` line for each of the 19 scenarios, then `board renders as specified`. A failing assertion prints `FAIL`, the scenario and the name of each failed check, then `<n> failed checks`, and exits `1`. A page that crashes or produces no result fails its scenario the same way.

## Evidence

All of these ran on 21 November 2026 against the template last changed in `2f575c8fb5afa5e9ce3c6b7f35531ad0c4abed66` (sha256 `01415b6ea1cc91034d881faae184eba48ecdf89d350698d2cbee5b30e360871a`), with Google Chrome 158.0.8127.37. Every page, row and name is placeholder data.

### The Rerun check fails when the template is wrong

The `## Rerun` script, extracted from this file, exited `0` on the template with 19 `ok` lines. With `CHROME=/nonexistent` it printed the PENDING line and exited `0`. Each mutation below is a single text replacement in a copy of the template written outside the repository. The same extracted script, given each copy through `TEMPLATE`, exited `1` for every one of them. The last column counts the scenarios that printed `FAIL`.

| Mutation | Exit | Scenarios with FAIL |
| --- | --- | --- |
| stale threshold fixed at 30 | 1 | 3 of 19 |
| `stale_after_min` ignored | 1 | 1 of 19 |
| default stale limit 45 | 1 | 3 of 19 |
| stale two minutes early | 1 | 2 of 19 |
| 30-second re-render removed | 1 | 1 of 19 |
| Recent changes always empty | 1 | 8 of 19 |
| Recent changes not capped | 1 | 8 of 19 |
| Recent changes re-sorted by time | 1 | 8 of 19 |
| missing-database notice never shown | 1 | 1 of 19 |
| subscription errors ignored | 1 | 3 of 19 |
| error after data drops the rows | 1 | 2 of 19 |
| error line reworded | 1 | 3 of 19 |
| Pull requests table drops a row | 1 | 9 of 19 |
| Pull requests sorted as strings | 1 | 9 of 19 |
| slow-load notice never shown | 1 | 2 of 19 |
| slow-load notice shown at once | 1 | 2 of 19 |
| slow-load notice never cleared | 1 | 2 of 19 |
| page writes | 1 | 18 of 19 |
| OS dark block removed | 1 | 1 of 19 |
| OS dark text same as ground | 1 | 1 of 19 |
| every phase shown as Done | 1 | 10 of 19 |
| Phases not sorted | 1 | 9 of 19 |
| scheduling shown raw | 1 | 9 of 19 |
| session closed styled as done | 1 | 8 of 19 |
| Depends on column blank | 1 | 11 of 19 |
| needs not sorted by kind | 1 | 9 of 19 |
| one-way door not critical | 1 | 8 of 19 |
| after note dropped | 1 | 10 of 19 |
| after note counts merged pull requests | 1 | 10 of 19 |
| review order ignores dependencies | 1 | 10 of 19 |
| review lists open pull requests | 1 | 10 of 19 |
| digit-string numbers not normalised | 1 | 10 of 19 |
| headings upper-cased in the DOM | 1 | 19 of 19 |
| text appended as markup | 1 | 14 of 19 |
| unsafe links allowed | 1 | 12 of 19 |
| architecture link dropped | 1 | 8 of 19 |
| phone table layout disabled | 1 | 14 of 19 |
| long pane widens the page | 1 | 11 of 19 |
| unreadable tick widens the page | 1 | 1 of 19 |
| stale verdict lost when meta dies | 1 | 1 of 19 |
| focus not restored | 1 | 1 of 19 |
| map scroll not restored | 1 | 1 of 19 |
| chips wrap mid-word | 1 | 2 of 19 |
| table cells break anywhere | 1 | 2 of 19 |
| map: one column | 1 | 8 of 19 |
| map: all edges solid | 1 | 8 of 19 |
| map: skip edges not laned | 1 | 8 of 19 |
| map: missing node gets a state | 1 | 1 of 19 |
| map: node shows no state | 1 | 9 of 19 |
| map: cycle drawn instead of reported | 1 | 1 of 19 |
| map: unreadable entry reads as none | 1 | 1 of 19 |
| map: non-list `depends_on` dropped | 1 | 1 of 19 |
| map: label through innerHTML | 1 | 1 of 19 |

The table covers every mutation the review gate at `45f0689` listed that still applies to the code: the stale threshold fixed at 30, `stale_after_min` ignored, Recent changes always empty, the missing-database notice never shown, subscription errors ignored, Pull requests rows removed, the slow-load notice never shown, a page that writes, the OS dark block removed, every phase shown as Done, needs sorted wrongly and the after note dropped. It also covers the four minor findings that review sent back and the implementer fixed: a long pane and an unreadable tick widening the page, the stale verdict lost when the `board/meta` listener dies, digit-string pull request numbers, and focus lost on re-render.

### Published test page

The template was copied unchanged (same sha256) to a scratch file and published once with the Artifact tool, private, with `capabilities: {db: {rules: [{path: "", read: "view", write: "admin"}]}}`, `icon: "status"` and `title: "placeholder-feature status board"`. The service stored contract 0.2.98, the one root rule, and page version `1795279300-128b`. The page stays private and is not shared.

### Batch 1

One `ArtifactData` batch of 15 `set` writes, committed atomically at 16:41 UTC:

- `board/meta`: feature `placeholder-feature`, orchestrator branch `placeholder-feature-orchestrator`, default branch `main`, architecture URL `https://example.com/architecture`, `tick_at` `2026-11-21T16:41:00Z`, `stale_after_min` 40.
- `board/recent`: three items, newest first. `board` Implement to Verify at 16:30, `launcher` Plan to Implement at 16:10, `foundation` Review to PR at 15:00.
- `phases`, in this run's shape. `foundation` (PR, closed, `depends_on: []`). `launcher` (Implement, live, pane `%12`), `board` (Verify, live, pane `%14`), `orchestrator-handbook` (Review, queued), `phase-handbooks` (Spec, blocked, waits for "a decision on the handbook layout"), `pr-handbook` (Plan, queued) and `spec-planner-handbooks` (Done, closed), each depending on `foundation` until `merged`. `default-stack` (Spec, blocked) depending on the other seven until `done`.
- `prs/21` (draft, rank 1, depends on 22, needs update, checks passing), `prs/22` (draft, rank 2, no dependencies, checks pending) and `prs/23` (draft, rank 3, depends on 21 and 22, checks failing), each with an `https://example.com/pull/<n>` link and base `main`.
- `needs/default-stack-d1` (decision, one-way door, since 16:18) and `needs/board-prompt` (prompt, pane `%14`, since 16:37).

### How the page was read

No browser could open the live page. The `claude-in-chrome` skill reported that the Claude in Chrome extension is not set up, and no other browser tool was available. So the claude.ai viewer and its live database transport were not observed. Three reads stand in for them, and each shows only what is stated:

1. The Artifact tool's `read` with `page: true` returned the served document: the publish skeleton, the stored `db` declaration and the template byte for byte. This shows what the viewer serves, not how it renders.
2. `ArtifactData` `list` of `board`, `phases`, `prs` and `needs` at `as_level: "view"` returned all 15 documents as written, so a viewer can read them. An `update` of `board/meta` at `as_level: "interact"` was refused by the access rules, so only an editor writes.
3. The rows from step 2 were served unchanged, with `fromCache: false`, to the template inside the served skeleton from step 1, and rendered in headless Chrome in a 400 px frame, light and dark. The DOM was read back with the Rerun check's collector, and a screenshot of the frame was looked at. This shows how the template renders exactly those rows. It does not exercise the claude.ai viewer, `claude.use("db")` or real `onSnapshot` delivery.

Result after batch 1, in light and in dark: the six headings in order. Needs you lists the one-way decision then the prompt with pane `%14`. Ready for your review lists #22, #21 ("after #22"), #23 ("after #21, #22"). The Pull requests table has three rows, and #23's Depends on reads `#21, #22`. Phases has eight rows with "session live", "session closed", "queued to start" and "blocked", and `default-stack`'s Depends on lists all seven phases with `(done)`. The map has three columns and 13 edges, 7 of them dashed, and none crosses a node. Recent changes shows the three items in stored order. Heartbeat reads Fresh, 1 minute ago, with no stale banner. The tab title is `placeholder-feature status board`, nothing was written, and there is no horizontal scroll at 400 px. The body background was `rgb(245, 247, 250)` in light and `rgb(16, 20, 27)` in dark.

### Batch 2

One `ArtifactData` batch of one write at 16:43 UTC: `update` of `board/meta` with `tick_at` `2026-11-21T16:02:00Z`, 41 minutes earlier, pinned to version 1, which committed as version 2. `board` was read again at `as_level: "view"` and showed version 2 with the new `tick_at`. Rendered the same way, with the other collections as read after batch 1 (batch 2 did not touch them), the page showed the banner "The orchestrator has not ticked for 41 minutes." and the Stale chip with "41 min ago", in light and in dark, with no horizontal scroll. Afterwards the artifact's version was still `1795279300-128b`, so nothing was published again.

### Schema comment

Cold read: a fresh subagent was given only the schema comment (lines 1 to 93 of the template) and a two-phase scenario in which `beta` cannot start until all of `alpha`'s pull requests are merged into `main`. It wrote a first batch of five `set` writes: `board/meta` with `architecture_url: null`, `board/recent` with three items newest first, `phases/alpha` with `depends_on: []`, `phases/beta` with `depends_on: [{"phase": "alpha", "until": "done"}]`, and `needs/alpha-prompt` (prompt, pane `%7`). Checked against the comment, every collection, document id, field and value is valid, `recent` is one document, `depends_on` is present on both phases with the right `until`, and no `prs` document was invented. It also put the prompt in `alpha`'s `waits_for`, which the comment allows but which repeats the needs item. Its open questions: what the four `scheduling` values mean (`queued` against `blocked`), how `scheduling: "live"` relates to `session_live`, whether `waits_for` should repeat a needs item, the order of items with the same time, whether to backfill `recent`, a convention for needs ids, whether `door` applies to prompts, whether to send `stale_after_min`, and whether `until: "done"` means the state Done.

### Static checks

- `grep -n innerHTML` on the template printed nothing and exited `1`.
- In `packages/s-stack`, `apm audit --ci` (apm-cli 0.32.0, outside the sandbox) passed all 10 checks with no drift and exited `0`. The committed lockfile holds no `/Users/` path.
