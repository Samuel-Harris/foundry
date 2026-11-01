# Self-check

Written by `tools/check.py`: one row per gate of the build rubric. NOT-CHECKABLE gates passed their mechanical part and name what a judge must read.

| Gate | Status | Evidence |
| --- | --- | --- |
| A1 | PASS | 326/326 TOC entries mapped; plan and disk agree |
| A2 | PASS | 299/299 files reachable from SKILL.md (lookup.md not expanded) |
| A3 | PASS | 43 idiom boxes, each with a boxed card |
| A4 | PASS | chapter 10: 10 cards (references/idioms/angle-channel.md, references/idioms/bivariate-colormaps.md, references/idioms/categorical-colormaps.md, references/idioms/colorblind-safe-colormaps.md, references/idioms/curvature-channel.md, references/idioms/motion-channels.md, references/idioms/ordered-colormaps.md, references/idioms/shape-channel.md, references/idioms/size-channels.md, references/idioms/texture-and-stippling.md) (+1 more) |
| A5 | PASS | lookup links 131 chapters and sections and 76 idiom cards |
| B1 | NOT-CHECKABLE | 443 use-when criteria carry at least 6 non-title content words (+1 more) |
| B2 | PASS | 443 child items with exact sizes; every file within its size limit |
| B3 | PASS | every node has related links; 137 book cross-references seeded |
| B4 | NOT-CHECKABLE | 221 disambiguation notes name only real siblings (+1 more) |
| B5 | PASS | router lists 4 job entry points and a 12-row routing table |
| B6 | NOT-CHECKABLE | every node has Children, Disambiguation and Related sections (+1 more) |
| C1 | PASS | 646 verbatim blocks match their cited pages |
| C2 | PASS | 4827 paragraphs, items and rows cited within range |
| C3 | PASS | 299 files carry valid metadata and leaf page ranges |
| C4 | PASS | markers are well placed; unmarked text is traced by C1 and C2 |
| C5 | PASS | ledger documents every level and each file's fidelity matches it |
| C6 | NOT-CHECKABLE | 3886 cited summary units across 256 leaves and idiom cards (+1 more) |
| D1 | PASS | 197 figures referenced with matching number, page and caption |
| D2 | PASS | 197 manifest entries with number, page, file, caption and referencing files |
| D3 | PASS | every extracted figure records embedded or a crop of at least 150 DPI |
| D4 | PASS | 197 figures; 0 unextracted, each with a reason |
| D5 | PASS | 76 idiom cards show their planned figures |
| D6 | PASS | 314 image links resolve; file names follow fig-NN-MM |
| E1 | PASS | j1: reaches 108 files in chapters [2, 3, 5, 7, 8, 9, 10, 12, 13] (+3 more) |
| E2 | PASS | 76 idiom cards carry matplotlib and D3 hints |
| E3 | PASS | 212 hint units, none cited |
| E4 | PASS | hints sit in their own sections or items, never in verbatim or summary text |
| E5 | PASS | every file keeps its book structure with hints removed |
| F1 | PASS | coverage.json maps 326 entries with level, path and PDF range |
| F2 | PASS | 2576 links resolve, 0 external links not fetched |
| F3 | PASS | 0 orphans among 299 files |
| F4 | PASS | provenance.md records word counts per kind and the C1 results |

## A1 PASS

- 326/326 TOC entries mapped; plan and disk agree

## A2 PASS

- 299/299 files reachable from SKILL.md (lookup.md not expanded)

## A3 PASS

- 43 idiom boxes, each with a boxed card

## A4 PASS

- chapter 10: 10 cards (references/idioms/angle-channel.md, references/idioms/bivariate-colormaps.md, references/idioms/categorical-colormaps.md, references/idioms/colorblind-safe-colormaps.md, references/idioms/curvature-channel.md, references/idioms/motion-channels.md, references/idioms/ordered-colormaps.md, references/idioms/shape-channel.md, references/idioms/size-channels.md, references/idioms/texture-and-stippling.md)
- chapter 11: 12 cards (references/idioms/animated-transitions.md, references/idioms/change-view-over-time.md, references/idioms/constrained-navigation.md, references/idioms/context-preserving-visual-links.md, references/idioms/cut.md, references/idioms/geometric-zooming.md, references/idioms/highlighting.md, references/idioms/hyperslice.md, references/idioms/lineup.md, references/idioms/project.md, references/idioms/semantic-zooming.md, references/idioms/slice.md)

## A5 PASS

- lookup links 131 chapters and sections and 76 idiom cards

## B1 NOT-CHECKABLE

- 443 use-when criteria carry at least 6 non-title content words
- Judge: read every ## Children item and confirm each use-when names a data type, task or situation rather than paraphrasing the title. Files: SKILL.md, references/ch01-whats-vis-why/node.md, references/ch02-what-data-abstraction/node.md, references/ch02-what-data-abstraction/s02-04-dataset-types/node.md, references/ch02-what-data-abstraction/s02-06-semantics/node.md, references/ch03-why-task-abstraction/node.md, references/ch03-why-task-abstraction/s03-04-actions/node.md, references/ch03-why-task-abstraction/s03-07-analyzing-deriving-examples/node.md, references/ch04-analysis-four-levels-validation/node.md, references/ch04-analysis-four-levels-validation/s04-03-four-levels-design/node.md, references/ch04-analysis-four-levels-validation/s04-06-validation-approaches/node.md, references/ch04-analysis-four-levels-validation/s04-07-validation-examples/node.md, references/ch05-marks-channels/node.md, references/ch05-marks-channels/s05-05-channel-effectiveness/node.md, references/ch06-rules-thumb/node.md, references/ch06-rules-thumb/s06-03-no-unjustified-3d/node.md, references/ch07-arrange-tables/node.md, references/ch07-arrange-tables/s07-05-separate-order-align-categorical/node.md, references/ch07-arrange-tables/s07-06-spatial-axis-orientation/node.md, references/ch08-arrange-spatial-data/node.md, references/ch08-arrange-spatial-data/s08-04-scalar-fields-one-value/node.md, references/ch08-arrange-spatial-data/s08-05-vector-fields-multiple-values/node.md, references/ch09-arrange-networks-trees/node.md, references/ch10-map-color-other-channels/node.md, references/ch10-map-color-other-channels/s10-02-color-theory/node.md, references/ch10-map-color-other-channels/s10-03-colormaps/node.md, references/ch11-manipulate-view/node.md, references/ch11-manipulate-view/s11-04-select-elements/node.md, references/ch12-facet-into-multiple-views/node.md, references/ch12-facet-into-multiple-views/s12-03-juxtapose-coordinate-views/node.md, references/ch12-facet-into-multiple-views/s12-04-partition-into-views/node.md, references/ch12-facet-into-multiple-views/s12-05-superimpose-layers/node.md, references/ch13-reduce-items-attributes/node.md, references/ch13-reduce-items-attributes/s13-03-filter/node.md, references/ch13-reduce-items-attributes/s13-04-aggregate/node.md, references/ch14-embed-focus-context/node.md, references/ch15-analysis-case-studies/node.md, references/jobs/j1-choose-idiom.md, references/jobs/j2-encoding-checks.md, references/jobs/j2-write-plotting-code.md, references/jobs/j3-critique.md, references/jobs/j4-dashboards.md, references/lookup.md

## B2 PASS

- 443 child items with exact sizes; every file within its size limit

## B3 PASS

- every node has related links; 137 book cross-references seeded

## B4 NOT-CHECKABLE

- 221 disambiguation notes name only real siblings
- Judge: confirm every group of children whose use-when conditions overlap has a note, and that each 'No overlapping children.' is true. Files: SKILL.md, references/ch01-whats-vis-why/node.md, references/ch02-what-data-abstraction/node.md, references/ch02-what-data-abstraction/s02-04-dataset-types/node.md, references/ch02-what-data-abstraction/s02-06-semantics/node.md, references/ch03-why-task-abstraction/node.md, references/ch03-why-task-abstraction/s03-04-actions/node.md, references/ch03-why-task-abstraction/s03-07-analyzing-deriving-examples/node.md, references/ch04-analysis-four-levels-validation/node.md, references/ch04-analysis-four-levels-validation/s04-03-four-levels-design/node.md, references/ch04-analysis-four-levels-validation/s04-06-validation-approaches/node.md, references/ch04-analysis-four-levels-validation/s04-07-validation-examples/node.md, references/ch05-marks-channels/node.md, references/ch05-marks-channels/s05-05-channel-effectiveness/node.md, references/ch06-rules-thumb/node.md, references/ch06-rules-thumb/s06-03-no-unjustified-3d/node.md, references/ch07-arrange-tables/node.md, references/ch07-arrange-tables/s07-05-separate-order-align-categorical/node.md, references/ch07-arrange-tables/s07-06-spatial-axis-orientation/node.md, references/ch08-arrange-spatial-data/node.md, references/ch08-arrange-spatial-data/s08-04-scalar-fields-one-value/node.md, references/ch08-arrange-spatial-data/s08-05-vector-fields-multiple-values/node.md, references/ch09-arrange-networks-trees/node.md, references/ch10-map-color-other-channels/node.md, references/ch10-map-color-other-channels/s10-02-color-theory/node.md, references/ch10-map-color-other-channels/s10-03-colormaps/node.md, references/ch11-manipulate-view/node.md, references/ch11-manipulate-view/s11-04-select-elements/node.md, references/ch12-facet-into-multiple-views/node.md, references/ch12-facet-into-multiple-views/s12-03-juxtapose-coordinate-views/node.md, references/ch12-facet-into-multiple-views/s12-04-partition-into-views/node.md, references/ch12-facet-into-multiple-views/s12-05-superimpose-layers/node.md, references/ch13-reduce-items-attributes/node.md, references/ch13-reduce-items-attributes/s13-03-filter/node.md, references/ch13-reduce-items-attributes/s13-04-aggregate/node.md, references/ch14-embed-focus-context/node.md, references/ch15-analysis-case-studies/node.md, references/jobs/j1-choose-idiom.md, references/jobs/j2-encoding-checks.md, references/jobs/j2-write-plotting-code.md, references/jobs/j3-critique.md, references/jobs/j4-dashboards.md, references/lookup.md

## B5 PASS

- router lists 4 job entry points and a 12-row routing table

## B6 NOT-CHECKABLE

- every node has Children, Disambiguation and Related sections
- Judge: for each node, pick a realistic query per child and confirm the node alone settles the next hop without opening a child. Files: SKILL.md, references/ch01-whats-vis-why/node.md, references/ch02-what-data-abstraction/node.md, references/ch02-what-data-abstraction/s02-04-dataset-types/node.md, references/ch02-what-data-abstraction/s02-06-semantics/node.md, references/ch03-why-task-abstraction/node.md, references/ch03-why-task-abstraction/s03-04-actions/node.md, references/ch03-why-task-abstraction/s03-07-analyzing-deriving-examples/node.md, references/ch04-analysis-four-levels-validation/node.md, references/ch04-analysis-four-levels-validation/s04-03-four-levels-design/node.md, references/ch04-analysis-four-levels-validation/s04-06-validation-approaches/node.md, references/ch04-analysis-four-levels-validation/s04-07-validation-examples/node.md, references/ch05-marks-channels/node.md, references/ch05-marks-channels/s05-05-channel-effectiveness/node.md, references/ch06-rules-thumb/node.md, references/ch06-rules-thumb/s06-03-no-unjustified-3d/node.md, references/ch07-arrange-tables/node.md, references/ch07-arrange-tables/s07-05-separate-order-align-categorical/node.md, references/ch07-arrange-tables/s07-06-spatial-axis-orientation/node.md, references/ch08-arrange-spatial-data/node.md, references/ch08-arrange-spatial-data/s08-04-scalar-fields-one-value/node.md, references/ch08-arrange-spatial-data/s08-05-vector-fields-multiple-values/node.md, references/ch09-arrange-networks-trees/node.md, references/ch10-map-color-other-channels/node.md, references/ch10-map-color-other-channels/s10-02-color-theory/node.md, references/ch10-map-color-other-channels/s10-03-colormaps/node.md, references/ch11-manipulate-view/node.md, references/ch11-manipulate-view/s11-04-select-elements/node.md, references/ch12-facet-into-multiple-views/node.md, references/ch12-facet-into-multiple-views/s12-03-juxtapose-coordinate-views/node.md, references/ch12-facet-into-multiple-views/s12-04-partition-into-views/node.md, references/ch12-facet-into-multiple-views/s12-05-superimpose-layers/node.md, references/ch13-reduce-items-attributes/node.md, references/ch13-reduce-items-attributes/s13-03-filter/node.md, references/ch13-reduce-items-attributes/s13-04-aggregate/node.md, references/ch14-embed-focus-context/node.md, references/ch15-analysis-case-studies/node.md, references/jobs/j1-choose-idiom.md, references/jobs/j2-encoding-checks.md, references/jobs/j2-write-plotting-code.md, references/jobs/j3-critique.md, references/jobs/j4-dashboards.md, references/lookup.md

## C1 PASS

- 646 verbatim blocks match their cited pages

## C2 PASS

- 4827 paragraphs, items and rows cited within range

## C3 PASS

- 299 files carry valid metadata and leaf page ranges

## C4 PASS

- markers are well placed; unmarked text is traced by C1 and C2

## C5 PASS

- ledger documents every level and each file's fidelity matches it

## C6 NOT-CHECKABLE

- 3886 cited summary units across 256 leaves and idiom cards
- Judge: compare each cited summary with its cited page text in build/pages and flag any added, resolved or contradicted claim. Start with references/**/*.md leaves and references/idioms/*.md.

## D1 PASS

- 197 figures referenced with matching number, page and caption

## D2 PASS

- 197 manifest entries with number, page, file, caption and referencing files

## D3 PASS

- every extracted figure records embedded or a crop of at least 150 DPI

## D4 PASS

- 197 figures; 0 unextracted, each with a reason

## D5 PASS

- 76 idiom cards show their planned figures

## D6 PASS

- 314 image links resolve; file names follow fig-NN-MM

## E1 PASS

- j1: reaches 108 files in chapters [2, 3, 5, 7, 8, 9, 10, 12, 13]
- j2: reaches 199 files in chapters [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
- j3: reaches 68 files in chapters [4, 5, 6, 7, 10, 13, 14]
- j4: reaches 60 files in chapters [6, 11, 12, 13, 14]

## E2 PASS

- 76 idiom cards carry matplotlib and D3 hints

## E3 PASS

- 212 hint units, none cited

## E4 PASS

- hints sit in their own sections or items, never in verbatim or summary text

## E5 PASS

- every file keeps its book structure with hints removed

## F1 PASS

- coverage.json maps 326 entries with level, path and PDF range

## F2 PASS

- 2576 links resolve, 0 external links not fetched

## F3 PASS

- 0 orphans among 299 files

## F4 PASS

- provenance.md records word counts per kind and the C1 results

## Judged gates

Judge records: 10 files in `reports/judge/`; handoff resolutions in `reports/judge-handoffs.tsv`.

| Gate | Action | Findings |
| --- | --- | --- |
| B1 | fixed | 32 |
| B1 | kept | 6 |
| B4 | fixed | 40 |
| B4 | kept | 8 |
| B6 | fixed | 34 |
| B6 | kept | 16 |
| C2 | fixed | 2 |
| C3 | kept | 1 |
| C6 | deleted | 1 |
| C6 | fixed | 200 |
| C6 | handoff | 3 |
| C6 | kept | 33 |
| E5 | fixed | 1 |
| Hints | fixed | 12 |
| Hints | kept | 12 |
| handoff | handoff | 1 |
| hints | fixed | 1 |
| hints | kept | 1 |
