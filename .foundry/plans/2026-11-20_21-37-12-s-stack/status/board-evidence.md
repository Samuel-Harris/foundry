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
