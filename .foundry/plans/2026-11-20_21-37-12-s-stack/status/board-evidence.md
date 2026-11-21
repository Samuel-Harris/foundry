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
