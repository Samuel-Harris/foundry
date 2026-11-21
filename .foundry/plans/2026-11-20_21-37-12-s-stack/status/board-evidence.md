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
