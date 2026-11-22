# Phase `board` evidence

## Verify gate, code head `45f0689499b3a4ea0dbe0001949e8a54ba184509`, VERIFIED

A fresh verifier wrote `tests/s-stack/verify-s-stack/checks/board.md` and committed it as `45f0689`, which became the code head. It then ran the whole verification skill and the board's **Done when** lists. The detail of every live check is in that file's `## Evidence` section.

- Verification skill on `45f0689`: checks 1, 2, 3, 5, 7 and 8 PASS. Tier 1 printed `all Tier 1 structural checks passed across 20 packages`. Checks 4 (handbook routes) and 6 (launcher tests) are PENDING, which the skill allows until those phases land.
- Test page: https://claude.ai/artifact/CGRk5V7xJEA9xcgjB1wwx5, private, placeholder data only, published once with the capabilities, icon and title the schema comment names. Batch 1 wrote ten documents. Batch 2 set `tick_at` 41 minutes back, and the page version did not change.
- Six sections in order, review order #12, #11, #13, a three-row pull request table with #13 depending on #11 and #12, and the stale banner after batch 2. These were read by rendering the rows read back from the live store, unchanged, in the served skeleton in headless Chrome. The Artifact read showed the served page is the template byte for byte. `ArtifactData` at `as_level: "view"` read every row, and a write at `interact` was refused.
- No horizontal scroll at 400 px in light and dark. The phase session reran the `## Rerun` check at 2026-11-21T16:04:25Z and got five `ok` lines and exit 0.
- A cold reader given only the schema comment wrote a valid first batch for a two-phase feature.
- `grep -n innerHTML` finds nothing. `apm audit --ci` in `packages/s-stack` passes all 10 checks.

Known gap: no browser in the verifier's session could open the live page, so nobody has yet watched the claude.ai viewer render the live store. One look at the test page closes it. It should show the stale banner.

Note for `foundation`: a cold read flagged that `SKILL.md` line 16 says to read `poteto-mode` "before anything else" while the `start` form says "Do nothing else".

## Review gate, code head `45f0689499b3a4ea0dbe0001949e8a54ba184509`, SIGNIFICANT

p-stack's `interrogate` ran two adversaries, Opus and Fable, each at medium effort in its own worktree, with the diff and the repository only. The configured Gemini seat is not available in Claude Code and was dropped. The phase session reran every finding below and saw the same output.

Significant, found by both adversaries:

- The `## Rerun` check in `checks/board.md` passes templates that break specified behaviour. The Opus adversary's seven sed mutations all exit 0, including a stale threshold fixed at 30, `stale_after_min` ignored, Recent changes always empty, the missing-database notice never shown, subscription errors ignored, Pull requests table rows removed, and the slow-load notice never shown. The Fable adversary's fifteen mutations also all exit 0, adding a page that writes, the dark-mode block removed, every phase shown as Done, needs sorted wrongly and the after-dependency note dropped. The causes: the fixture always sends `stale_after_min: 40` and ticks of 5 and 41 minutes; the section contents are never asserted; the stub database has no write verbs; every scenario delivers live snapshots in 20 ms. This goes to the next verifier, who owns the file.

Minor, to be fixed in the current Implement round:

- A prompt's `pane` of about 50 or more unbroken characters (scrollWidth 529 at 400 px) and an unparsable `tick_at` shown raw in Heartbeat (scrollWidth 529) widen the page.
- The stale banner and Stale chip disappear when the `board/meta` listener dies after data arrived.
- Pull request numbers written as strings (`number: "11"`, `depends_on: ["12"]`) silently drop the dependency order. The review order reads 11, 12, and Ready for your review and Pull requests disagree.
- Every re-render drops keyboard focus (focused `A:#11`, then `BODY` after the 30-second timer). The code-quality review also found this one.

Minor, recorded and not fixed:

- A `tick_at` with no time zone (`2026-11-21T16:03:00`) is read as local time, so the stale verdict depends on the viewer's time zone. The schema requires UTC with `Z`, and the orchestrator writes `Z` times.

## Verify gate, code head `a678a49d30e83b4d65ce068b8120ac192e61595c`, VERIFIED

A fresh verifier rewrote `tests/s-stack/verify-s-stack/checks/board.md` at `a678a49` and verified the template as of `2f575c8`, which is unchanged since.

- The `## Rerun` check runs 19 scenarios. They assert every section's content, `stale_after_min` at its boundaries (39 and 41 minutes with the default, 50 and 61 minutes with 60 sent), the no-database, unreachable and subscription-error states, that the page never writes, the OS dark theme, no page scroll at 400 px, no broken word at 1000 px, the dependency map in this run's shape (three columns, 13 edges, 7 dashed, no crossings), unknown nodes, cycles and unreadable entries, digit-string numbers, focus and `scrollLeft` surviving a snapshot, and no injection.
- 53 single-replacement mutants of the template each make the Rerun exit 1, including all twelve mutations listed by the earlier Review gate. The phase session checked the mutant summary (53 rows, every exit code 1) and reran the Rerun at 2026-11-21T16:53:47Z: exit 0, tree clean.
- Verification skill: checks 1, 2, 3, 5, 7 and 8 PASS. Tier 1 passed across 20 packages. Checks 4 and 6 are PENDING, as the skill allows.
- Second private test page: https://claude.ai/artifact/G7cbKuJYQXZruLTazZqpLJ, placeholder rows only. Batch 1 wrote 15 documents, including this run's eight-phase dependency shape. Batch 2 set `tick_at` 39 minutes back and then the page showed 41 minutes stale, with the version unchanged. The page was read the same way as before (served HTML, view-level reads, the rows rendered in the served skeleton).
- A cold reader given only the schema comment wrote a valid first batch with `depends_on`. `grep innerHTML` finds nothing. `apm audit --ci` passes.

Known gap, unchanged: no browser tool was available, so nobody has watched the claude.ai viewer render either test page.

## Review gate, code head `a678a49d30e83b4d65ce068b8120ac192e61595c`, SIGNIFICANT

`interrogate` again ran two adversaries, Opus and Fable, at medium effort, over `45f0689..a678a49` for the template and `checks/board.md`. The Gemini seat was dropped as before. The phase session reran each finding below.

Significant, found by both adversaries:

- Edges that skip layers share one lane, so two different dependency sets draw the same map. The Opus adversary's graphs 1 and 2 screenshot identically (194 of 200,000 pixels differ, antialiasing only), and the phase session compared the two images by eye. A "done" edge under a "merged" edge also draws solid along the lane.
- The `## Rerun` check passes broken templates. The phase session reran nine mutants and each exits 0: a cached tick trusted, nodes not coloured by state, the map not scrollable, the table scroll not kept, an `acquire` write, the legend swapped, the chip palette differing from the map, dark text on dark nodes, and no notice over cached data. The causes: the stub never serves `fromCache: true` and has no `acquire`, the legend is never read, node fill is compared only between unknown nodes, `scrollable` is collected but never asserted, and only the map's scroll position is checked.

Minor, to be fixed in Implement:

- Map labels are cut at 20 characters, so two ids that share 19 characters render the same, and this run's `spec-planner-handbooks` is cut.
- An `unknown:` dependency chip is clipped at 400 px and runs into the gutter.
- A tick proved stale by a live read loses its banner when a cached snapshot follows.

Minor, recorded and not fixed:

- Text selection is lost on each re-render.
- `review_rank` and `stale_after_min` sent as digit strings are ignored. The schema says number for both.
- At 700 px the Pull requests table scrolls sideways by 4 px inside its own wrapper.

## Verify gate, code head `b2deb4dc95214b6039608c7c3b7f949aae752bce`, VERIFIED

A fresh verifier, following `handbooks/verifier.md`, rewrote `checks/board.md` at `b2deb4d`. Its `## Evidence` section now describes the one-off checks without their results, as the run decision on check files requires. The template is unchanged since `66118de`.

- `## Rerun`: 26 scenarios plus a comparison of the two lane graphs. It exits 0 on the real template, prints PENDING and exits 0 without Chrome, and leaves the tree clean. The phase session reran it at 2026-11-21T17:42:45Z and got exit 0.
- Mutation proof: 73 single-replacement mutants of the current template, written outside the repository. Every one makes the Rerun exit 1. They include every surviving mutant from both Review gates (two of them rewritten by hand because their target code had changed) and four for this round: shared lanes, labels cut at 20 characters, unknown chips that do not wrap, and a live stale verdict lost to a cached snapshot. The phase session ran one, the OS dark-text mutant, directly: it printed two FAIL lines and exited 1.
- Verification skill: checks 1, 2, 3, 5, 7 and 8 PASS. Tier 1 passed across 20 packages. Check 4 is PENDING for `orchestrator.md` and `pr-creator.md`, and check 6 is PENDING with no launcher tests yet; the skill allows both.
- Third private test page: https://claude.ai/artifact/G9DR3pgSxrcgiWkPRh897c, placeholder rows only, with this run's eight-phase shape. Batch 1 wrote 15 documents. Batch 2 set `tick_at` 41 minutes back. The page then showed the stale banner, and its version was unchanged. It was read from the served HTML and from view-level reads, and its rows were rendered in the served skeleton in light and dark. A write at `interact` level was refused.
- A cold reader given only the schema comment wrote a valid six-write first batch with `depends_on`. `grep innerHTML` finds nothing. `apm audit --ci` passes, and the lockfile holds no absolute path.

Known gap, unchanged: no browser tool was available, so nobody has watched the claude.ai viewer render a test page.

Found by the verifier, outside this phase's paths: `tests/s-stack/verify-s-stack/SKILL.md` check 8 and feature plan C6 still say `## Evidence` records results, which contradicts the run decision and `verifier.md`.

## Review gate, code head `b2deb4dc95214b6039608c7c3b7f949aae752bce`, SIGNIFICANT

`interrogate` ran two adversaries, Opus and Fable, at medium effort, under `handbooks/reviewer.md`. The scope was `66118de`, `b2deb4d` and the conflict resolution of `eff112d`. Both reran the earlier probes: every one of the 74 provided mutants exits 1, and the two lane graphs now draw differently. Both found the template correct, and the merge's lockfile matches the template's hash. The phase session reran each significant finding below and saw the same exit code.

Significant, all gaps in the `## Rerun` check (each mutant exits 0, where 1 is required):

- Skipping edges sharing a lane per source or per target. Found by both adversaries. No fixture has two skipping edges that share a source or a target, so the dashed-under-solid defect that `66118de` fixed can return unnoticed.
- A template that hangs makes the Rerun hang. A busy loop ran past a 150-second bound. The Chrome call has no wall-clock bound, and the `mktemp` directory and Chrome process were left behind; the phase session removed its own.
- A `<title>` element, which the schema comment says the file must not have.
- The Phases table losing its scroll position on re-render.
- A first live tick that never updates. The banner stays "41 minutes" after a fresh live tick, and no scenario sends a second live `board/meta`.
- Lane space reserved for only one lane, so a lane runs through a node.
- An SVG height that ignores the lanes, and a width that ignores grown nodes, which clips the map.
- Unknown chips that wrap only below 600 px.

Minor, recorded:

- No fixture has an id over 40 characters, so a missing cut at 40 passes.
- A 40-character id in wide glyphs overflows its node, because node width assumes 7.4 units per character. Phase ids are slugs in practice.
- The stub records the read-only query builders `where`, `orderBy` and `limit` as writes. This fails safe.
- The Fable adversary saw one headless Chrome launch sit idle for nine minutes, in about 2,300 launches. It is the same unbounded call as above.

## Verify gate, code head `a5b3a9c8a79a19b3d65691765019a0e6adb28279`, VERIFIED

Two verifiers worked on this gate.

The first committed `checks/board.md` at `e21d7e8`. That version maps every template promise to a scenario and gives every Chrome call a wall-clock bound, where a timeout fails. It ran 225 mutants in two rounds, and three survived. The phase session stopped it at 20:10 under the orchestrator's 15-minute limit, because it had started a further edit. The phase session then merged `s-stack-package` at `cc362c4`.

A fresh verifier, scoped by the orchestrator to one representative mutant per assertion, committed `a5b3a9c` and verified it.

- Fallback fonts: with Google Fonts blocked, the 1000 px word check failed on one break, `bold</b>|<img`, inside the fixture's adversarial markup title. That is a legitimate break between two punctuation marks, not a split word. No word in data that follows the schema breaks, with or without the web fonts. The check now blocks host resolution, so it is deterministic and offline, and it counts a break only between two letters or digits.
- `## Rerun`: 45 scenarios. The phase session reran it at 2026-11-21T20:31:13Z: exit 0 in 27 s, the tree clean, and the OS dark-text mutant from the earlier set exited 1.
- Mutation proof: 41 mutants, one or more per promise row, including every mutant from the third Review gate. All 41 exit 1; the phase session counted the exit column. The hang mutant fails with "Chrome timed out twice" in 61 s and leaves no Chrome process behind. The three survivors from the first verifier (an `orderBy` read, and two dropped guards in `keepViewState`) render identically to the real template in all 44 recorded scenarios, so they are equivalent.
- Verification skill: checks 1, 2, 3, 5, 7 and 8 PASS. Tier 1 passed across 20 packages in 153 s. Check 4 is PENDING for `orchestrator.md` and `pr-creator.md`, and check 6 is PENDING with no launcher tests yet.
- Live page https://claude.ai/artifact/G9DR3pgSxrcgiWkPRh897c serves the current template byte for byte. A batch with a fresh `tick_at` rendered Fresh. A batch with `tick_at` 41 minutes old rendered the stale banner, with no publish. A write at `interact` level was refused.
- The cold reader wrote a valid first batch with `depends_on`. `grep innerHTML` finds nothing. `apm audit --ci` passes.

Known gaps:

- No browser tool could open the claude.ai viewer.
- The first verifier's 225-mutant rounds were not re-checked, apart from its three survivors.
- The cold readers noted that the schema comment shows no batch wire format and names no state for a phase that has not started. Both are minor.

## Review gate, code head `a5b3a9c8a79a19b3d65691765019a0e6adb28279`, SIGNIFICANT

`interrogate` ran Opus and Fable at medium effort under `handbooks/reviewer.md`, over `e21d7e8`, `a5b3a9c` and the resolution of `cc362c4`.

What passed:

- Every earlier probe now exits 1.
- The busy-loop mutant fails in about 60 s and leaves no Chrome process.
- The real template passes three times in a row, and six times in parallel.
- The merge's lockfile hashes match the files.

Both adversaries found the template correct. The phase session reran each mutant below against the Rerun at `a5b3a9c`. Each exits 0 where 1 is required.

Significant under `board-d6`, because each misleads the developer on the live board, or because it is an injection:

- Wrong staleness:
  - `m01-rerender-once`: the 30-second re-judge runs once, and the board stays Fresh.
  - `m11-stale-limit-never-below-40`: a `stale_after_min` below 40 is ignored.
  - `m04-cached-tick-judges-after-live`: a cached tick judges after a live one.
- Lost or misattributed data:
  - `m2-no-time-of-day`, `m4-time-an-hour-late` and `m02-absolute-time-is-now`: the visible time text of Recent changes and of the last tick is never asserted.
  - `m06-normalise-in-place`: on frozen snapshot bodies, as `db.d.ts` describes them, a dependency is lost and the review order changes. The stub hands out mutable bodies.
- Wrong state:
  - `m03-no-loading-state`: the sections read "Nothing needs you." and similar before any data has arrived.
  - `m05-live-without-pane-not-live`: a live session with `pane: null` reads "not live".
- Injection:
  - `m1-arch-any-scheme`: a `javascript:` architecture link becomes clickable.
  - `m23-feature-as-markup`: markup in `board/meta.feature` is parsed into the heading, which sits outside `main`, where the text check does not look.

Minor, recorded:

- The banner rounds minutes where it should floor them. No scenario has a fractional minute of 0.5 or more.
- An unreadable needs `since` reads "waiting 0 min", or the need is dropped.
- No scenario covers a page without `window.claude`.
- A pull request focus key could collide. Its effect was not shown.
- Ctrl-C waits up to the 30-second Chrome bound before cleanup. Cleanup is complete.


## Verify gate, code head `afd3f270ba9c2ddc689b0afe12927591941ccc7f`, VERIFIED

A narrowly scoped verifier closed the twelve gaps of the fourth Review gate in `checks/board.md` at `afd3f27`. The template is unchanged since `66118de`.

- What the Rerun now asserts:
  - the exact visible time text, under UTC and `en-GB`;
  - a Fresh-to-Stale change that needs a second 30-second render;
  - a `stale_after_min` of 10;
  - cached ticks after live ones, both ways round;
  - a live session with no pane;
  - the loading text while the store is silent;
  - frozen snapshot bodies in every scenario;
  - a `javascript:` architecture link shown as plain text;
  - no markup anywhere on the page, including the heading.
- It runs 49 scenarios plus the lanes comparison.
- Every one of the twelve mutants exits 1, and so do all 41 mutants from the previous Verify gate. The phase session reran four of the twelve at 2026-11-21T21:28:58Z and each exited 1. The real template exited 0, and no Chrome process was left behind.
- Verification skill: checks 1, 2, 3, 5, 7 and 8 PASS. Tier 1 passed across 20 packages. Checks 4 and 6 are PENDING, which the skill allows.
- Live page https://claude.ai/artifact/G9DR3pgSxrcgiWkPRh897c showed Fresh, then the stale banner, with no publish in between. The verifier skipped the write probe at `interact` level because the auto-mode classifier denied it, so the stored `write: "admin"` rule is the evidence that viewers cannot write.
- `grep innerHTML` finds nothing. `apm audit --ci` passes.

Known gaps:

- No browser view of claude.ai.
- The en-GB locale is pinned in the stub, because headless Chrome on macOS ignores `--lang` for `Intl`.
- After a cached tick, the heartbeat shows the cached tick's time while the verdict stays live. The check does not assert that time.


## Review gate, code head `afd3f270ba9c2ddc689b0afe12927591941ccc7f`, CLEAR

`interrogate` ran Opus and Fable at medium effort under `handbooks/reviewer.md`, over `afd3f27` and the template it checks. Under `board-d7`, only a template defect is significant.

- Both adversaries ran the Rerun on the real template and got exit 0 with 50 `ok` lines.
- Both ran all eleven probe mutants from the fourth Review gate. Each exits 1, on the assertion that names its fault.
- Neither found a template defect. The Fable adversary also exercised these on the real template, and none rendered markup or failed:
  - markup in `waits_for`;
  - `javascript:…//https://` URLs;
  - 90-character unbroken strings in every field at 320 and 1000 px;
  - duplicate edges, future times and digit-string numbers.
- Every finding is a minor template behaviour or a check gap. Both are listed in the check hardening backlog. The phase session took the adversaries' exit codes as reported and did not rerun these findings, because none of them holds the phase.


## Follow-up round, Verify gate, code head `284ad88a3929192851895e2650198266bcddca75`, VERIFIED

The round removes the restack need kind (`73251d3`) and makes the `needs_update` rule match `orchestrator.md` (`5fc142f`). The verifier updated `checks/board.md` at `284ad88`:

- Unknown need kinds, including a leftover `restack`, now sort last, oldest first.
- A pull request with `needs_update: null` shows no update chip.

Results:

- **Mutants.** Every one exits 1, and the real template exits 0. The set covers:
  - "restack" kept in the rank;
  - "Up to date" shown for null;
  - the eleven probe mutants from the earlier Review gates, re-applied to the current template.

  At 2026-11-22T01:01:30Z the phase session reran the real template (exit 0), the restack mutant (exit 1) and `m04` (exit 1).
- **Cold read.** A cold reader given only the schema comment answered the `needs_update` question as expected, naming no restack need.
- **Verification skill.** Checks 1, 2, 3, 5, 7 and 8 PASS, and Tier 1 passed across 20 packages. Check 4 is PENDING, because `orchestrator.md` and `pr-creator.md` are not on `s-stack-package` yet, and check 6 is PENDING.
- **Live page.** https://claude.ai/artifact/2DKwc7LqGBu5pfjoGrZmhH serves the current template byte for byte. It rendered Fresh after batch 1, and the stale banner after batch 2, with no publish in between. A write at `interact` level was refused.
- **Static checks.** `grep innerHTML` finds nothing, and `apm audit --ci` passes.

## Check hardening backlog

`board-d7` sends every check gap found from the fifth Review gate on to this list, for a future hardening pass. These are not fixed in this phase.

- From the fourth Review gate (minor):
  - The banner rounds minutes where it should floor them. No scenario has a fractional minute of 0.5 or more.
  - An unreadable needs `since` reads "waiting 0 min", or the need is dropped.
  - No scenario covers a page without `window.claude`.
  - A pull request focus key could collide; its effect was not shown.
  - Ctrl-C waits up to the 30-second Chrome bound before cleanup, though cleanup is complete.
- From the third Review gate (minor):
  - No fixture has an id over 40 characters.
  - Node width assumes 7.4 units per character, so wide glyphs overflow their node.
  - The stub records read-only query builders as writes.
- From the second Review gate (minor):
  - Text selection is lost on re-render.
  - `review_rank` and `stale_after_min` sent as digit strings are ignored.
  - At 700 px the Pull requests table scrolls by 4 px inside its wrapper.
- From the Verify gate at `afd3f27`:
  - After a cached tick, the heartbeat's tick time is not asserted.
  - The `interact`-level write probe was not run.
- From the fifth Review gate (template behaviours, minor):
  - A dependency cycle among draft pull requests turns off dependency order for drafts outside the cycle.
  - After every source has been live once, a store that falls silent with no error makes the banner blame the orchestrator, and no notice appears. The db API gives the page no way to tell the two apart.
  - Text selection is lost on each re-render.
- From the fifth Review gate (check gaps):
  - Markup is tested only in `feature`, a pull request title, a need summary and the dependency ids. A template that parses markup from `waits_for`, a recent item's states or `orchestrator_branch` passes, and so does the `grep innerHTML` check.
  - A link test of "contains https://" passes, because no unsafe fixture URL contains `https://`.
  - Times are checked only under `TZ=UTC`, so forcing UTC passes.
  - The stub freezes snapshot bodies but not the snapshot or its `docs` array.
- From the follow-up round's Verify gate:
  - The review fixture's closed #35 still has `needs_update: false`, where the new schema says a closed pull request is null.
  - The live render used the verifier's own collector, not the Rerun collector.
