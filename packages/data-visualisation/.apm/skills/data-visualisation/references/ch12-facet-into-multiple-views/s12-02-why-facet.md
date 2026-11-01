---
id: s12.02
kind: section-leaf
title: "Why Facet?"
pdf_pages: [290, 292]
printed_pages: [265, 267]
toc: [s12.02]
fidelity: mixed
---

# 12.2 Why Facet?

## Faceting as one of five approaches to visual complexity

<!-- verbatim p.290 -->
> The verb facet means to split; this chapter covers the design choices that pertain to splitting up the display, into either multiple views or layers.
<!-- /verbatim -->

Faceting is one of the five major approaches to handling visual complexity: juxtaposing coordinated views side by side and superimposing layers within a single view. In both cases the data must be partitioned into the views or layers [p.290]. The other four approaches are deriving new data (Chapter 3), changing a single view over time (Chapter 11), reducing the data shown (Chapter 13) and embedding focus and context in the same view (Chapter 14) [p.290].

## Juxtaposed views versus a changing view

Juxtaposed views spread information out in space, an alternative to a changing view that spreads it out over time. Comparing two simultaneously visible views is relatively easy, because the eyes can move back and forth between them; comparing a changing view's current state with its previous one requires working memory, a scarce internal resource [pp.290-291].

## Multiform views and linked highlighting

The multiform choice uses a different encoding in each view to show the same data. Its rationale is that no single visual encoding is optimal for all possible tasks, so a multiform tool can support more tasks, or faster switching between tasks, than a single view. Coordinating multiform views with linked highlighting shows whether a spatial neighbourhood in one view also falls into contiguous regions in the others or is distributed differently [p.291].

## Small multiples and partitioning

The small multiples choice partitions the data between views. Partitioning is a powerful and general idea, especially when used hierarchically with a succession of attributes to slice and dice the dataset [p.291].

<!-- verbatim p.291 -->
> The choice of which attributes to partition versus which to directly encode with, as well as the order of partitioning, has a profound effect on what aspects of the dataset are visually salient.
<!-- /verbatim -->

## The cost of juxtaposing

The obvious and significant cost of juxtaposed views is display area: two views side by side each get only half the area a single view could have. Display area is a scarce external resource [p.291].

<!-- verbatim p.291 -->
> The trade-off between the scarcity of display area and working memory is a major issue in choosing between juxtaposing additional views and changing an existing view.
<!-- /verbatim -->

## Superimposing layers

Superimposing layers needs no more screen space. Visual layering controls clutter in complex encodings, giving a less cluttered view than a single view without layers. Superimposing and changing the view over time are not mutually exclusive and are often used together; dynamically constructed layers necessarily imply an interactive view that changes [p.291].

One limitation is that visually distinguishable layers impose serious constraints on encoding choices [p.291].

## How many views or layers

The number of layers that can be superimposed before clutter becomes overwhelming is strongly limited: two is very feasible, three is possible with care, and more would be difficult. Juxtaposition accommodates many more views: several is straightforward and up to a few dozen is viable with care [pp.291-292].

## Figures

## Related

- [6.5 Eyes Beat Memory](../ch06-rules-thumb/s06-05-eyes-beat-memory.md): the slogan behind preferring side-by-side comparison to working memory [p.291]
- [11.3 Change View over Time](../ch11-manipulate-view/s11-03-change-view-over-time.md): the changing-view alternative weighed against juxtaposition [p.290]
- [12.3 Juxtapose and Coordinate Views](s12-03-juxtapose-coordinate-views/node.md): multiform views and linked highlighting in detail [p.291]
- [12.4 Partition into Views](s12-04-partition-into-views/node.md): small multiples and the order of partitioning in detail [p.291]
- [12.5 Superimpose Layers](s12-05-superimpose-layers/node.md): layer count and distinguishability in detail [p.291]
- [Superimposed Line Charts](../idioms/superimposed-line-charts.md): the exception to two or three layers; the limit holds for layers of many area marks, and thin, mostly disjoint lines stay usable up to nearly a dozen [pp.314-315]
- [13 Reduce Items and Attributes](../ch13-reduce-items-attributes/node.md): reducing data, another of the five approaches [p.290]
- [14 Embed: Focus+Context](../ch14-embed-focus-context/node.md): embedding focus and context, another of the five approaches [p.290]
