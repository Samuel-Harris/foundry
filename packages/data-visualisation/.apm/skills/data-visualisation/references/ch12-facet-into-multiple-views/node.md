---
id: ch12
kind: chapter-node
title: "Facet into Multiple Views"
pdf_pages: [289, 322]
printed_pages: [264, 297]
toc: [ch12]
fidelity: summary
---

# 12 Facet into Multiple Views

How to split a display into multiple views or layers. Three families of choices: juxtapose views side by side and coordinate them, partition the data across those views, or superimpose layers within one view [pp.289-290]. Juxtaposing costs display area but lets the eyes compare views instead of working memory; superimposing costs no screen space but strongly limits the visual encoding and the number of layers [pp.290-292].

[NOT FROM BOOK] The book does not use the word dashboard; this chapter is where its multiple-view design choices live.

## Children

- [12.1 The Big Picture](s12-01-big-picture.md) · ~336 words. **Use when** you need the map of faceting choices (coordination for juxtaposed views, partitioning, layering) and Figure 12.1's design-choice tree before descending [pp.289-290]
- [12.2 Why Facet?](s12-02-why-facet.md) · ~671 words. **Use when** deciding between several views side by side, one view that changes over time, and layers in one view; it weighs display area against working memory and gives the view and layer count limits [pp.290-292]
- [12.3 Juxtapose and Coordinate Views](s12-03-juxtapose-coordinate-views/node.md) · ~877 words. **Use when** several views will sit side by side, as in a dashboard, and you must decide what links them: shared or different encoding, linked highlighting (brushing), whether each view shows all the data, a subset (overview–detail) or a partition (small multiples), synchronised navigation, and whether a view is always visible or pops up on demand [pp.292-304]
- [12.4 Partition into Views](s12-04-partition-into-views/node.md) · ~535 words. **Use when** a multiattribute table has categorical (or binned) attributes and you must decide which attributes split the data into regions or views, in what order, how far to split, and whether to align the pieces in a list, a matrix or nested regions; covers grouped versus small-multiple bars and Trellis [pp.304-313]
- [12.5 Superimpose Layers](s12-05-superimpose-layers/node.md) · ~585 words. **Use when** the information must share one frame rather than more screen space: two or three static layers distinguished by nonoverlapping channel ranges (maps, superimposed lines, edge bundles), or a dynamic layer built from the user's selection [pp.313-320]
- [12.6 Further Reading](s12-06-further-reading.md) · ~417 words. **Use when** looking for primary sources on composite views, coordinated multiple views, partitioning (HiVE), glyph design, brushing or layer design [pp.320-322]

## Disambiguation

- **Juxtapose and Coordinate Views vs Superimpose Layers.** Juxtaposing needs more display area but scales to several views easily and up to a few dozen with care; layering needs no extra space but only two layers are very feasible and three possible with care [pp.291-292]. The authors of an empirical study proposed superimposing for comparisons within a local visual span and juxtaposing for dispersed tasks needing large visual spans, especially as the number of series grows [p.317].
- **Juxtapose and Coordinate Views vs Partition into Views.** Small multiples appear in both: 12.3 treats them as one of three data-sharing choices for linking views (each view shows a disjoint partition); 12.4 covers how to divide the data, which attributes split it and in what order, and how to align the resulting regions [p.294] [p.298] [p.304].
- **Partition into Views vs Superimpose Layers.** Both divide items into groups; static layers are often divided like views, by attribute types and semantics, whereas dynamic layers follow the user's selection rather than dataset structure [p.314].
- **The Big Picture vs Why Facet?.** 12.1 lists the choices; 12.2 gives the rationale and costs for each family [pp.290-292].

## Related

- [6.5 Eyes Beat Memory](../ch06-rules-thumb/s06-05-eyes-beat-memory.md): the rationale for side-by-side comparison over a changing view [p.291]
- [11 Manipulate View](../ch11-manipulate-view/node.md): changing a single view over time, the main alternative to juxtaposing [p.290]
- [13 Reduce Items and Attributes](../ch13-reduce-items-attributes/node.md): reducing what is shown, another of the five approaches to visual complexity [p.290]
- [14 Embed: Focus+Context](../ch14-embed-focus-context/node.md): embedding focus and context in one view, another of the five approaches [p.290]
- [3 Why: Task Abstraction](../ch03-why-task-abstraction/node.md): deriving new data, another of the five approaches [p.290]
- [7.5 Separate, Order, and Align: Categorical Regions](../ch07-arrange-tables/s07-05-separate-order-align-categorical/node.md): the separate, order and align choices that partitioning into views applies [p.298] [p.304]
- [11.5 Navigate: Changing Viewpoint](../ch11-manipulate-view/s11-05-navigate-changing-viewpoint.md): the navigation that overview–detail and linked navigation synchronise [p.294] [p.301]
