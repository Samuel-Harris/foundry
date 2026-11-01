---
id: ch15
kind: chapter-node
title: "Analysis Case Studies"
pdf_pages: [365, 393]
printed_pages: [340, 368]
toc: [ch15]
fidelity: summary
---

# 15 Analysis Case Studies

Six full vis systems, each given a complete analysis with the book's framework now that every design choice has been introduced: the data abstraction with any derived data, the task abstraction, the idiom choices for how to encode, facet and reduce, and scalability against a 1000 by 1000 pixel screen [pp.365-367]. Most have complex data abstractions, transform the original data into derived data, combine several basic dataset types and support structure at multiple levels [p.367]. The analyses are descriptive, not prescriptive; the book suggests generating alternatives for each choice and weighing their pros and cons [p.367].

## Children

- [15.1 The Big Picture](s15-01-big-picture.md) · ~309 words. **Use when** you need a one-line summary of all six systems to pick the case study whose data and problem resemble yours [pp.365-366]
- [15.2 Why Analyze Case Studies?](s15-02-why-analyze-case-studies.md) · ~401 words. **Use when** you want the template a full analysis follows (abstraction level, idiom level, scalability) before applying it to a design you are critiquing [pp.366-367]
- [15.3 Graph-Theoretic Scagnostics](s15-03-graph-theoretic-scagnostics.md) · ~660 words. **Use when** a table has too many attributes for a scatterplot matrix to scale, and you want derived summary measures of every pairwise scatterplot to guide the user to unusual ones; models a derived overview driving a popup detail view [pp.367-371]
- [15.4 VisDB](s15-04-visdb.md) · ~924 words. **Use when** a very large table is shown against a query with dense, space-filling colour-coded marks, or you must choose between partitioning space by attribute and by item to suit different tasks; models the limits of information density [pp.372-375]
- [15.5 Hierarchical Clustering Explorer](s15-05-hierarchical-clustering-explorer.md) · ~1,145 words. **Use when** designing a multi-view dashboard for a large two-key table with a cluster hierarchy, combining overview–detail cluster heatmaps, interactive aggregation and filtering, and rank-by-feature orderings of attributes and attribute pairs [pp.376-380]
- [15.6 PivotGraph](s15-06-pivotgraph.md) · ~714 words. **Use when** you are critiquing or explaining a roll-up network view and want the book's walkthrough: why a derived network replaces the original data abstraction, the gender-by-division and gender-by-location worked examples, and why visual complexity depends only on the number of attribute levels [pp.380-383]
- [15.7 InterRing](s15-07-interring.md) · ~520 words. **Use when** a tree needs a space-filling radial view with multifocus distortion, editing, and structure-based colour shared with linked views; models a hierarchy view inside a multi-view system [pp.383-384]
- [15.8 Constellation](s15-08-constellation.md) · ~1,438 words. **Use when** a specialised, label-heavy multilevel network must show ranked query results, using spatial position for attributes and dynamic layers instead of crossing minimisation, with semantic zooming across three viewing levels [pp.385-391]
- [15.9 Further Reading](s15-09-further-reading.md) · ~201 words. **Use when** you need the primary papers behind one of the six systems, or the earlier Tukey ideas that scagnostics builds on, to read beyond the book's analysis [pp.391-392]
- [PivotGraph](../idioms/pivotgraph.md) · ~871 words. **Use when** a network has categorical node attributes, the question is how attribute groups compare rather than what its topology is, and you must decide whether to use a roll-up view or build one: idiom box, when the book calls it well or poorly suited, node–link and matrix alternatives, and code [pp.380-383]

## Disambiguation

- **Why Analyze Case Studies? vs The Big Picture.** 15.1 summarises what each system does; 15.2 explains what every analysis covers and how to read it [pp.366-367].
- **Graph-Theoretic Scagnostics vs Hierarchical Clustering Explorer.** Both help explore pairwise attribute combinations through a SPLOM-like matrix. Scagnostics derives nine shape measures per scatterplot and plots a scatterplot of scatterplots; HCE's rank-by-feature orders attributes and pairs by a user-chosen criterion in colour-coded matrix and list overviews, alongside cluster heatmaps of a two-key table [p.369] [pp.376-379].
- **VisDB vs Hierarchical Clustering Explorer.** Both handle tables too large for one static view. VisDB reduces by filtering on query relevance in dense spiral layouts; HCE combines interactive aggregation, filtering and navigation with coordinated overview–detail views [p.374] [p.376].
- **PivotGraph vs Constellation.** Both are network case studies. PivotGraph aggregates any large network into a small derived network for comparing attribute groups; Constellation keeps a specialised multilevel network and supports browsing ranked paths and reading labels [pp.380-386].
- **15.6 PivotGraph vs PivotGraph.** Same idiom, same pages. Open the PivotGraph card to choose or build a roll-up view: it holds the idiom box fields, the tasks the book calls it well and poorly suited for, the alternatives and code. Open 15.6 to follow the book's reasoning: the roll-up mechanics step by step, the two worked examples, the scale argument and its possible role among linked multiform views [pp.380-383].
- **InterRing vs Constellation.** Both are interactive views of structure at several levels. InterRing shows a plain tree in a radial space-filling layout with multifocus distortion; Constellation shows a three-level network with containment and connection marks, dynamic layers and semantic zooming [p.383] [p.391].

## Related

- [7.4 Express: Quantitative Values](../ch07-arrange-tables/s07-04-express-quantitative-values.md): scatterplots, the base idiom scagnostics scales up [p.367]
- [7.5.2 Matrix Alignment: Two Keys](../ch07-arrange-tables/s07-05-separate-order-align-categorical/s07-05-02-matrix-alignment-two-keys.md): SPLOMs and cluster heatmaps, used by Scagnostics and HCE [p.367]
- [12.3.2 Share Data: All, Subset, None](../ch12-facet-into-multiple-views/s12-03-juxtapose-coordinate-views/s12-03-02-share-data-all-subset.md): small multiples and overview–detail, which Scagnostics, VisDB and HCE use [p.367]
- [9.4 Costs and Benefits: Connection versus Matrix](../ch09-arrange-networks-trees/s09-04-costs-benefits-connection-matrix.md): the standard network layouts PivotGraph complements [p.383]
- [3 Why: Task Abstraction](../ch03-why-task-abstraction/node.md): the task vocabulary every analysis uses [p.367]
- [2 What: Data Abstraction](../ch02-what-data-abstraction/node.md): the data and derived-data vocabulary every analysis uses [p.367]
- [12 Facet into Multiple Views](../ch12-facet-into-multiple-views/node.md): the facet choices analysed in each system [p.367]
- [13 Reduce Items and Attributes](../ch13-reduce-items-attributes/node.md): the reduce choices analysed in each system [p.367]
