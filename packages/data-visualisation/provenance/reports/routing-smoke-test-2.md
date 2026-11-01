# Routing smoke test 2

Method: start at `SKILL.md`, follow markdown links only, read each opened file in full, stop at the first file that answers or when lost. No grep, find, ls or wc. No skill file edited.

Word estimates: `SKILL.md` is about 3,400 words (not labelled; estimated from its size, mostly the routing table). Leaf files use the sizes in the links. Files with no label (Treemaps, Choropleth Map, 9.2, 8.5.1, 8.5.2) are my estimates. "Hops" means files opened after `SKILL.md`.

Paths below are relative to `references/` and abbreviated: `J2` is `jobs/j2-write-plotting-code.md`, and so on.

## Per-query table

| # | Query (short) | Files opened, in order | Hops | Words | Answered | Unsure |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 8 product lines, which grow | SKILL, superimposed-line-charts | 1 | 4,100 | partly | The "trends" cell says only "Line Charts" (one series). I picked the "compare some" cell. The card says juxtaposed small multiples beat it for whole-period tasks, but I did not open 12.3.2. |
| 2 | 2,000 people x 12 answers | SKILL, scatterplot-matrix-splom | 1 | 4,034 | partly | SPLOM scale is "dozens to hundreds" of items. 2,000 exceeds it and the card has no overplot pointer. |
| 3 | Org chart, 400 people, team sizes | SKILL, treemaps, 9.2 connection-link-marks | 2 | 5,700 | partly | Treemaps shows sizes but the card says avoid it for topology. 9.2 shows hierarchy but has no size or 400-node guidance. No file combines the two. |
| 4 | Temperature per US county | SKILL, choropleth-map | 1 | 4,000 | yes | None. The card's own example is US counties. |
| 5 | matplotlib clustered gene heatmap | SKILL, J2, cluster-heatmaps | 2 | 5,635 | yes | None. |
| 6 | D3 zoomable scatterplot | SKILL, J2, geometric-zooming | 2 | 5,417 | yes | The D3 hint scales the whole layer, so dots grow with zoom. A scatterplot usually wants constant dot size, and there is no semantic-zoom variant. |
| 7 | Colormap for correlation -1 to 1 | SKILL, J2, ordered-colormaps | 2 | 5,806 | yes | The code shows `TwoSlopeNorm(vcenter=0)` but not `vmin=-1, vmax=1`. |
| 8 | 6 categories as lines, how many colours | SKILL, J2, categorical-colormaps | 2 | 5,785 | yes | The card gives 6 to 12 for small separated regions. The line-specific "about a dozen" sits in the superimposed card, which I did not open. |
| 9 | 3D pie dashboard critique | SKILL, J3, 6.3.4 perspective, 7.6.3 radial | 3 | 6,360 | yes | None. A J3 disambiguation bullet tells you to join these two files. |
| 10 | Rainbow colormap for elevation | SKILL, J3, 10.3.2 ordered-colormaps | 2 | 5,772 | yes | None. |
| 11 | "Users liked it in a survey" | SKILL, J3, 4.6.3 idiom-validation | 2 | 5,512 | partly | No file names "liked it in a survey". I inferred from the "usability studies are not validation" paragraph and the preferences-from-lab-study line. 4.6.1 and 4.6.5 were not opened. |
| 12 | 50,000 overlapping points | SKILL, J3, continuous-scatterplots | 2 | 5,452 | yes | None. |
| 13 | Map selection highlights table rows | SKILL, J4, 12.3.1 share-encoding | 2 | 5,511 | yes | The concept is covered. The leaf has no code hints. The Highlighting card (with hints) is only in J4's "Related". |
| 14 | 10 years of logs, drill to a day | SKILL, J4, 6.7 overview-first | 2 | 5,442 | partly | 6.7 gives the mantra and aggregation but no concrete design. I did not open SolarPlot, 12.3.2 or 13.4. |
| 15 | Small multiples vs overlaid lines | SKILL, J4, superimposed-line-charts | 2 | 5,580 | yes | None. The J4 disambiguation bullet already answers it. The card confirms. |
| 16 | Focus on part of a huge network | SKILL, J4, 14.2 why-embed | 2 | 5,219 | partly | 14.2 gives rationale only. It names no idiom and says nothing about networks. I would need 14.5 or Hyperbolic Geometry. |
| 17 | Dual-axis line chart | SKILL, J3, 5.6 relative-absolute, lookup | 3 | 8,531 | no | Nothing covers dual axes. I guessed 5.6 (baselines and frames), then tried the lookup. No file says it is out of scope. |
| 18 | Wind flow from a simulation | SKILL, 8.5.1 flow-glyphs, 8.5.2 geometric-flow | 2 | 4,550 | yes | Concepts yes, code none. The "show the flow" cells do not tell you which of glyphs, streamlines or texture to pick. |
| 19 | KPI dashboard animates | SKILL, J3, 6.5 eyes-beat-memory | 2 | 5,758 | yes | None. |
| 20 | Distributions across 30 servers | SKILL, boxplot-charts | 1 | 4,165 | yes | None. |
| 21 | D3 nested rectangles, two levels | SKILL, treemaps | 1 | 4,100 | yes | None. The `paddingTop(12)` and `d3.hierarchy` hint fits. |
| 22 | How many views per screen | SKILL, J4, 12.2 why-facet | 2 | 5,554 | yes | None. "Up to a few dozen viable with care." |

## Routing problems

1. **SKILL.md, time-series row, "Explore" cell.** Exact text: `| trend: [Line Charts](references/idioms/line-charts.md) |`. That is the single-series card. A multi-series "which are growing" question has no cell. The multi-series advice (superimposed up to a dozen; small multiples for whole-span comparisons) sits in the "Compare some" cell. A reader going by task column lands in the wrong place.
2. **No dual-axis coverage (Q17).** Nothing in `SKILL.md`, J1 to J4 or the lookup mentions dual or secondary axes, and nothing says the book is silent on it. The agent has to burn about 8,500 words to learn that. A one-line "the book does not cover dual axes; see 5.6 and 5.4 for baselines" in J3 would fix it.
3. **SKILL.md, tree row.** Exact text: `attributes at the leaves: [Treemaps](references/idioms/treemaps.md); a path between two nodes: [3.7.1 Comparing Two Idioms]...` and `topology, paths: [9.2 Connection]...`. There is no cell for "show the hierarchy and sizes". Treemaps' own card says `Avoid for topological tasks`, while 9.2 has no size guidance. Q3 needs both files and neither settles it.
4. **SKILL.md, multi-attribute table row.** Exact text: `correlation among up to a dozen: [SPLOM](references/idioms/scatterplot-matrix-splom.md); dozens: [Parallel Coordinates](...)`. It gives an attribute count but no item count. The SPLOM card caps items at "dozens to hundreds", so a 2,000-row survey is borderline with no pointer to Continuous Scatterplots or aggregation.
5. **J2, "Other idiom families", chapter 9 line.** Exact text: `coding force-directed or multilevel node–link layouts, adjacency matrices, treemaps or cluster hierarchies over networks`. J2 links the chapter node for treemaps, not the Treemaps card, though the card holds the D3 `d3.treemap` hint that a "write code" query wants. The Q21 route worked only because the SKILL.md table links the card directly.
6. **J4, "Embed focus in context" group.** Exact text: `**Use when** users lose their place after zooming and need context kept in the same view rather than in a second view`. J4's first embed hop (14.2) is rationale only. Its only idiom card is DOITrees (trees). Hyperbolic Geometry, Fisheye and Stretch and Squish, the likely answers for a huge network, are not linked from J4 at all. Q16 stalled.
7. **J4, SolarPlot line.** Exact text: `as in 30 years of ticket sales seen as a trend or as seasons`. It is the closest thing to "10 years of logs, drill to a day" but is filed under "Reduce". The overview-to-detail query is better served by 12.3.2, with no sign in J4 that the two connect. 6.7 (the obvious first stop) has no worked design.
8. **Geometric Zooming, D3 hint.** Exact text: `// geometric: scale the whole layer, so marks and strokes grow with k`. The Q6 request is for a zoomable scatterplot, where dot growth is usually unwanted. The card has no counter-pattern, and J2's Scatterplots line points only at this card.
9. **J3 has no entry for subjective evidence.** Exact text: `**Use when** arguing whether an encoding works: perceptual justification, expert review, lab studies (time, errors, preferences), result images; also why usability studies are not validation`. A survey of "liked it" is not named. The agent has to infer that 4.6.3 is the place.
10. **Cost, not a defect in one line.** `SKILL.md` is about 3,400 words, roughly 60 to 80% of every query. The leaf is usually 400 to 1,500 words, so the router costs two to four times the answer.

## Summary

- Median hops: 2. Median words: about 5,510. Range 4,000 to 8,531; the high end is Q17, which failed.
- Queries 1 to 16: 10 yes (4, 5, 6, 7, 8, 9, 10, 12, 13, 15), 6 partly (1, 2, 3, 11, 14, 16), 0 no.
- Queries 17 to 22: 5 yes (18 to 22), 1 no (17).
- Three worst problems:
  1. Dual-axis (Q17): no coverage and no out-of-scope signal, costing about 8,500 words for a "no".
  2. Network focus+context (Q16) and log drill-down (Q14): J4 links the rationale pages but not the idioms (Hyperbolic, Fisheye, Stretch and Squish; SolarPlot with 12.3.2), so both stop at "partly".
  3. Table-cell gaps in `SKILL.md`: the multi-series trend question lands on the single-series Line Charts (Q1); there is no hierarchy-plus-size cell (Q3); and SPLOM has no item-count caveat (Q2). Together they account for three of the six partial answers.
