---
id: s04.07
kind: section-node
title: "Validation Examples"
pdf_pages: [106, 116]
printed_pages: [81, 91]
toc: [s04.07]
fidelity: summary
---

# 4.7 Validation Examples

Six vis research papers analysed by the levels they target and the methods used to validate their benefits; they also preview approaches covered later in the book [p.106]. Each leaf gives the paper's contribution, how it handles each level, and its validation-methods figure [pp.106-116].

## Children

- [4.7.1 Genealogical Graphs](s04-07-01-genealogical-graphs.md) · ~434 words. **Use when** you want a model of a paper that covers all four levels, with a strong abstraction argument (a "family tree" is really a constrained graph) validated by idiom justification, result images and anecdotal target-user testing [pp.106-108]
- [4.7.2 MatrixExplorer](s04-07-02-matrixexplorer.md) · ~324 words. **Use when** you want an example whose requirements came from interviews and participatory design sessions with target users, which also validate its domain level, for a tool combining node–link and matrix views of social networks [pp.108-110]
- [4.7.3 Flow Maps](s04-07-03-flow-maps.md) · ~408 words. **Use when** you want an algorithm-focused paper validated by complexity analysis, timings and result images used to argue correctness, with a domain level addressed only implicitly [pp.110-112]
- [4.7.4 LiveRAC](s04-07-04-liverac.md) · ~450 words. **Use when** you want an example of iterative design with interviews after a prototype and a longitudinal field study validating the abstraction level, for time-series monitoring with semantic zooming [pp.112-114]
- [4.7.5 LinLog](s04-07-05-linlog.md) · ~442 words. **Use when** a contribution looks algorithmic but is really an encoding idiom, validated by qualitative and quantitative image analysis including mathematical proof [pp.114-115]
- [4.7.6 Sizing the Horizon](s04-07-06-sizing-horizon.md) · ~202 words. **Use when** you want an example of lab studies measuring time and error to validate specific encoding choices, here chart height in line charts versus horizon graphs [pp.115-116]

## Disambiguation

- **Genealogical Graphs vs MatrixExplorer vs LiveRAC.** All address every or nearly every level. Genealogical graphs is strongest at abstraction and validates it with one target-user anecdote; MatrixExplorer validates the domain with interviews and participatory design; LiveRAC is the one with a deployed longitudinal field study [pp.107-114].
- **Flow Maps vs LinLog.** Both are layout papers on graph-like data. Flow maps' contribution is the algorithm and its result images argue correctness; LinLog's contribution is the idiom (an energy model) and it leaves the algorithm to prior work [pp.110-115].
- **LinLog vs Sizing the Horizon.** Both validate at the idiom level. LinLog uses image analysis and proof; Sizing the Horizon uses lab studies of human time and error [pp.114-116].

## Related

- [4.6 Validation Approaches](../s04-06-validation-approaches/node.md): the methods these papers use [p.106]
- [4.6.5 Mismatches](../s04-06-validation-approaches/s04-06-05-mismatches.md): why each paper uses only a subset of methods matched to its claims [p.106]
- [9.4 Costs and Benefits: Connection versus Matrix](../../ch09-arrange-networks-trees/s09-04-costs-benefits-connection-matrix.md): the matrix versus node–link trade-off behind MatrixExplorer [p.109]
- [8.3.1 Geographic Data](../../ch08-arrange-spatial-data/s08-03-geometry.md#s08.03.01): visual encoding of geographic data, as in flow maps [p.110]
- [9.2 Connection: Link Marks](../../ch09-arrange-networks-trees/s09-02-connection-link-marks.md): force-directed placement, the family LinLog belongs to [p.114]
- [15 Analysis Case Studies](../../ch15-analysis-case-studies/node.md): further systems analysed with the book's framework [p.106]
