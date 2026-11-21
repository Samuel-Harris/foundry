# Phase `board` checks

Phase `board` ships `packages/s-stack/.apm/skills/sam-mode/assets/status-board.html`, the status board template. An orchestrator publishes it once per feature and then writes only to the page's database. The behavioural checks render the template with a stubbed database in headless Chrome and read the result back from the DOM.

## Rerun

### Rendered board in a 400 px frame

The script below writes its harness to a fresh `mktemp` directory and never writes into the repository. It wraps the template in the skeleton the Artifact tool publishes, which includes `[hidden]{display:none!important}`, and defines `window.claude.use("db")` as a stub that serves placeholder documents with `fromCache: false`. Headless Chrome will not make a window narrower than 500 px, so the harness hosts the page in a 400 px `iframe` and reads the frame's own `scrollWidth` and `clientWidth`. Each scenario sets the theme with `data-theme` on the root element, and the tick age in minutes.

The fixture holds three draft pull requests: #11 (rank 1, depends on #12), #12 (rank 2) and #13 (rank 3, depends on #11 and #12), plus a merged #9 that must stay out of Ready for your review. #13's title carries `<b>not bold</b>` and its `url` is `javascript:alert(1)`, so a data value that reached `innerHTML` or an unchecked link would show.

Run it from the repository root. It needs Google Chrome at `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`, or the path in `CHROME`. Without Chrome it prints `PENDING: Google Chrome not found at <path>, so the board cannot be rendered here` and exits `0`.

```bash
bash <<'EOF'
set -euo pipefail
template="$PWD/packages/s-stack/.apm/skills/sam-mode/assets/status-board.html"
chrome="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
if [ ! -x "$chrome" ]; then echo "PENDING: Google Chrome not found at $chrome, so the board cannot be rendered here"; exit 0; fi
[ -f "$template" ] || { echo "FAIL: $template is missing"; exit 1; }
dir="$(mktemp -d)"
trap 'rm -rf "$dir"' EXIT

cat > "$dir/stub.js" <<'JS'
(() => {
  const params = new URLSearchParams(location.search);
  document.documentElement.setAttribute("data-theme", params.get("theme"));
  const now = Date.now();
  const ago = (min) => new Date(now - min * 60000).toISOString();
  const full = {
    "board/meta": {feature: "placeholder-feature", orchestrator_branch: "placeholder-feature-orchestrator-with-a-long-branch-name",
      default_branch: "main", architecture_url: "https://example.com/architecture", tick_at: ago(Number(params.get("tick"))), stale_after_min: 40},
    "board/recent": {items: [
      {at: ago(3), phase: "beta", from: "Plan", to: "Implement"},
      {at: ago(20), phase: "alpha", from: "Verify", to: "PR"},
      {at: ago(90), phase: "gamma", from: null, to: "Spec"}]},
    phases: [
      {phase: "alpha", state: "PR", scheduling: "live", waits_for: null, session_live: true, pane: "%12", changed_at: ago(20)},
      {phase: "beta", state: "Implement", scheduling: "live", waits_for: null, session_live: true, pane: "%14", changed_at: ago(3)},
      {phase: "gamma", state: "Spec", scheduling: "blocked", waits_for: "alpha", session_live: false, pane: null, changed_at: ago(90)}],
    prs: [
      {number: 11, url: "https://example.com/pull/11", title: "Pull request A, with a title long enough to wrap at phone width", phase: "alpha", state: "draft", checks: "passing", base: "main", depends_on: [12], review_rank: 1, needs_update: true},
      {number: 12, url: "https://example.com/pull/12", title: "Pull request B", phase: "alpha", state: "draft", checks: "pending", base: "main", depends_on: [], review_rank: 2, needs_update: false},
      {number: 13, url: "javascript:alert(1)", title: "Pull request C <b>not bold</b>", phase: "beta", state: "draft", checks: "failing", base: "placeholder-feature-orchestrator-with-a-long-branch-name", depends_on: [11, 12], review_rank: 3, needs_update: false},
      {number: 9, url: "https://example.com/pull/9", title: "Merged groundwork", phase: "alpha", state: "merged", checks: "passing", base: "main", depends_on: [], review_rank: null, needs_update: false}],
    needs: [
      {kind: "prompt", phase: "beta", summary: "A permission prompt waits in the session.", door: null, pane: "%14", since: ago(4)},
      {kind: "decision", phase: "gamma", summary: "Choose the storage layout before Plan.", door: "one-way", pane: null, since: ago(23)}],
  };
  const data = params.get("fixture") === "empty" ? {} : full;
  const metadata = {fromCache: false, hasPendingWrites: false};
  const docSnap = (path) => ({id: path.split("/")[1], exists: path in data, data: () => data[path], metadata});
  const colSnap = (path) => {
    const docs = (data[path] || []).map((body, i) => ({id: String(i), exists: true, data: () => body, metadata}));
    return {docs, size: docs.length, empty: !docs.length, docChanges: () => [], metadata};
  };
  const listen = (snap) => (path) => ({onSnapshot: (next) => { setTimeout(() => next(snap(path)), 20); return () => {}; }});
  const db = {doc: listen(docSnap), collection: listen(colSnap)};
  window.claude = {use: async (name) => (name === "db" ? db : null)};
})();
JS

cat > "$dir/collect.js" <<'JS'
setTimeout(() => {
  const root = document.documentElement;
  const visible = (el) => el && !el.closest("[hidden]");
  const result = {
    headings: [...document.querySelectorAll("main > section h2")].map((h) => h.textContent),
    noHorizontalScroll: root.scrollWidth <= root.clientWidth,
    width: root.clientWidth,
    reviewOrder: [...document.querySelectorAll("#review-list > li")].map((li) => li.dataset.number),
    stale: visible(document.getElementById("stale-banner")),
    heartbeat: document.getElementById("s-heartbeat").textContent,
    empties: [...document.querySelectorAll("main > section")].map((s) => [...s.querySelectorAll(".empty")].map((p) => p.textContent).join("")),
    injected: document.querySelectorAll("main b").length,
    unsafeLinks: [...document.querySelectorAll("a")].filter((a) => !a.href.startsWith("https://")).length,
    background: getComputedStyle(document.body).backgroundColor,
  };
  parent.postMessage(JSON.stringify(result), "*");
}, 1500);
JS

cat > "$dir/frame.html" <<'HTML'
<!doctype html><html><body style="margin:0"><script>
const f = document.createElement("iframe");
f.style.cssText = "border:0;width:400px;height:1200px";
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

for scenario in "theme=light&tick=5" "theme=dark&tick=5" "theme=light&tick=41" "theme=dark&tick=41" "theme=light&tick=5&fixture=empty"; do
  echo "$scenario"
  "$chrome" --headless --disable-gpu --hide-scrollbars --user-data-dir="$dir/profile" --window-size=500,1300 \
    --virtual-time-budget=4000 --dump-dom "file://$dir/frame.html?$scenario" 2>/dev/null
done > "$dir/out.txt"

python3 - "$dir/out.txt" <<'PY'
import html, json, re, sys
headings = ["Needs you", "Ready for your review", "Pull requests", "Phases", "Recent changes", "Heartbeat"]
empties = ["Nothing needs you.", "No draft pull requests yet.", "No pull requests yet.",
           "No phases yet. The orchestrator adds them once the feature plan exists.", "No state changes yet.", "No tick recorded yet."]
chunks = re.split(r"^(theme=\S+)$", open(sys.argv[1]).read(), flags=re.M)[1:]
failures, backgrounds = [], {}
for scenario, dom in zip(chunks[::2], chunks[1::2]):
    m = re.search(r'data-result="([^"]*)"', dom)
    if not m:
        failures.append(f"{scenario}: the page produced no result")
        continue
    r = json.loads(html.unescape(m.group(1)))
    q = dict(p.split("=") for p in scenario.split("&"))
    checks = {
        "six headings in order": r["headings"] == headings,
        "400 px frame": r["width"] == 400,
        "no horizontal scroll": r["noHorizontalScroll"],
    }
    if q.get("fixture") == "empty":
        checks["every section shows its empty state"] = r["empties"] == empties
    else:
        backgrounds[q["theme"]] = r["background"]
        checks["review order 12, 11, 13"] = r["reviewOrder"] == ["12", "11", "13"]
        checks["stale only past 40 minutes"] = r["stale"] == (q["tick"] == "41")
        checks["heartbeat chip"] = ("Stale" if q["tick"] == "41" else "Fresh") in r["heartbeat"]
        checks["no data reaches markup or an unsafe link"] = r["injected"] == 0 and r["unsafeLinks"] == 0
    bad = [name for name, ok in checks.items() if not ok]
    print(f"{'FAIL' if bad else 'ok  '} {scenario}: {', '.join(bad) or 'all checks hold'}")
    failures += [f"{scenario}: {name} ({json.dumps(r)})" for name in bad]
if backgrounds.get("light") == backgrounds.get("dark"):
    failures.append(f"light and dark render the same background {backgrounds}")
print("\n".join(failures) or "board renders as specified in light and dark at 400 px")
sys.exit(1 if failures else 0)
PY
EOF
```

Expected: exit `0`, one `ok` line for each of the five scenarios, then `board renders as specified in light and dark at 400 px`. A failing assertion prints `FAIL` on its scenario's line, the failed check with the page's full result, and exits `1`.

## Evidence

All of these ran on 21 November 2026 against the template at `f3d0e320e924679e78a3e08f3e2903853d36f060` (sha256 `3e22a1f0a64c8faa8f6c5ea4c5d60aa90b7008bac4dbb457852ea7b83809ac13`). Every page, row and name is placeholder data.

### Rerun harness fails when the template is wrong

The `## Rerun` script passed on the template, with five `ok` lines and exit `0`. It was then run against five mutated copies of the template outside the repository. Each mutation failed the scenarios it should fail, and one of them was confirmed to exit `1`:

| Mutation | Failed check |
| --- | --- |
| Phone table layout disabled (`max-width: 600px` changed to `1px`) | no horizontal scroll, all four fixture scenarios |
| Dependencies ignored in the review order | review order 12, 11, 13 |
| Stale threshold fixed at 60 minutes | stale only past 40 minutes and heartbeat chip, at a 41-minute tick only |
| Section headings upper-cased in the DOM | six headings in order |
| Text values appended through `innerHTML` | no data reaches markup or an unsafe link |

With `CHROME=/nonexistent` it printed the PENDING line and exited `0`.

### Published test page

The template was copied unchanged to a scratch file and published once with the Artifact tool, private, with `capabilities: {db: {rules: [{path: "", read: "view", write: "admin"}]}}`, `icon: "status"` and `title: "placeholder-feature status board"`. The service stored contract 0.2.98, the one root rule, and page version `1795276653-7230`. The page stays private and is not shared.

### Batch 1

One `ArtifactData` batch of 10 `set` writes, committed atomically:

- `board/meta`: feature `placeholder-feature`, orchestrator branch `placeholder-feature`, default branch `main`, architecture URL `https://example.com/architecture`, `tick_at` `2026-11-21T15:55:00Z`, `stale_after_min` 40.
- `board/recent`: three items, newest first. beta Plan to Implement at 15:50, alpha Verify to PR at 15:30, gamma null to Spec at 14:00.
- `phases/alpha` (PR, live, pane `%12`), `phases/beta` (Implement, live, pane `%14`), `phases/gamma` (Spec, blocked, waits for alpha, not live).
- `prs/11` (draft, rank 1, depends on 12, needs update), `prs/12` (draft, rank 2, no dependencies), `prs/13` (draft, rank 3, depends on 11 and 12), all with `https://example.com/pull/<n>` links.
- `needs/gamma-d1` (decision, one-way door, since 15:35) and `needs/beta-prompt` (prompt, pane `%14`, since 15:54).

### How the page was read

No browser tool could open the live page in this session, because the Claude in Chrome extension was not connected. The live render with the live database was therefore not observed. Three reads stand in for it, and each shows only what is stated:

1. The Artifact tool's `read` with `page: true` returned the served HTML. It is the template byte for byte inside the publish skeleton, under the stored `db` declaration. This shows what the viewer serves, but nothing about rendering.
2. `ArtifactData` `list` of `board`, `phases`, `prs` and `needs` at `as_level: "view"` returned every row written, so a viewer can read them. A `set` at `as_level: "interact"` was refused by the access rules, so only an editor writes.
3. The rows from step 2 were served, unchanged and with `fromCache: false`, to the template inside the served skeleton copied from step 1. The page was rendered in headless Chrome in a 400 px frame, and its DOM was read back, along with a screenshot. This shows how the template renders those exact rows. It does not exercise the live database transport or the claude.ai viewer.

Result after batch 1, in light and in dark: the six headings in order (Needs you, Ready for your review, Pull requests, Phases, Recent changes, Heartbeat). Ready for your review is ordered #12, #11 ("after #12"), #13 ("after #11, #12"). The Pull requests table has three rows, with #13's Depends on reading `#11, #12`. The heartbeat reads Fresh, there is no stale banner, the tab title is `placeholder-feature status board`, and there is no horizontal scroll (`scrollWidth <= clientWidth` at 400 px). The body background was `rgb(245, 247, 250)` in light and `rgb(16, 20, 27)` in dark.

### Batch 2

One `ArtifactData` batch of one write: `update` of `board/meta` with `tick_at` `2026-11-21T15:17:47Z` (41 minutes before the write), pinned to version 1, which committed as version 2. Read back the same way, the page showed the banner "The orchestrator has not ticked for 41 minutes." and the heartbeat chip Stale, in light and in dark, with no horizontal scroll. Afterwards the artifact's version was still `1795276653-7230`, so nothing was published again.

### Schema comment

- Every field of C5's five documents appears in the schema comment, in C5's order, with C5's allowed values. That was checked by a script over the comment's field lists, and by reading the allowed values. The comment contains no `--`.
- Cold read: a fresh subagent given only the comment (lines 1 to 80 of the template) and a two-phase scenario wrote a first batch of five `set` writes: `board/meta`, `board/recent` with two items, `phases/alpha` (Spec, live, pane `%3`), `phases/beta` (Spec, queued, waits for alpha) and `needs/alpha-keep-old-data-format` (decision, one-way). The batch was checked against the comment. Every collection, document id, field and value is valid, `recent` is one document, and no `prs` document was invented. Its open questions were all minor. They covered which op to use on later ticks, the order of items that share a time, whether a decision carries a pane, the format of `waits_for`, the rule for `needs` ids, and whether to send `stale_after_min`.

### Static checks

- `grep -n innerHTML` on the template printed nothing and exited `1`. No value is assigned through `innerHTML`.
- In `packages/s-stack`, `apm audit --ci` (apm-cli 0.32.0, run outside the sandbox) passed all 10 checks with no drift and exited `0`. It ran on the committed lockfile, which `git diff` showed unchanged and which holds no absolute `/Users/` path.
