---
id: ch13
kind: chapter-node
title: "Reduce Items and Attributes"
pdf_pages: [323, 346]
printed_pages: [298, 321]
toc: [ch13]
fidelity: summary
---

# 13 Reduce Items and Attributes

How to reduce, or interactively increase, what a view shows at once. Two design choices, each applicable to items or to attributes: filtering eliminates elements, and aggregation replaces many elements with one derived stand-in [p.324]. Filtering is easy to understand but users tend to forget what was filtered out; aggregation can be somewhat safer cognitively but cannot convey everything it replaces [pp.324-325].

## Children

- [13.1 The Big Picture](s13-01-big-picture.md) · ~179 words. **Use when** you need the two-by-two map of filter versus aggregate crossed with items versus attributes before descending [pp.323-324]
- [13.2 Why Reduce?](s13-02-why-reduce.md) · ~436 words. **Use when** weighing filtering against aggregation for a task, or placing reduction among the five strategies for managing visual complexity [pp.324-325]
- [13.3 Filter](s13-03-filter/node.md) · ~431 words. **Use when** some items or attributes can simply be removed from view: range selection, dynamic queries with sliders, scented widgets, or dropping attributes by a similarity score [pp.325-330]
- [13.4 Aggregate](s13-04-aggregate/node.md) · ~745 words. **Use when** too many items or attributes must be summarised rather than hidden: distributions (histograms, boxplots), overplotted scatterplots, cluster hierarchies, geographic regions, or dimensionality reduction [pp.330-345]
- [13.5 Further Reading](s13-05-further-reading.md) · ~335 words. **Use when** looking for primary sources on dynamic queries, scented widgets, boxplots, hierarchical aggregation, the MAUP, attribute reduction or MDS [pp.345-346]

## Disambiguation

- **The Big Picture vs Why Reduce?.** 13.1 is the map of choices from Figure 13.1; 13.2 explains the trade-off between filtering and aggregating and how reduction relates to the other complexity strategies [pp.324-325].
- **Filter vs Aggregate.** Filtering eliminates elements, so fewer are shown and the user may forget them; aggregation merges a group into a new derived element that stands in for it. Both apply to items and attributes and can be combined [pp.324-325] [p.330].

## Related

- [3 Why: Task Abstraction](../ch03-why-task-abstraction/node.md): deriving new data, another complexity strategy; aggregation typically involves a derived attribute [p.324] [p.330]
- [11 Manipulate View](../ch11-manipulate-view/node.md): changing a view over time, another complexity strategy; in the dynamic case reduction idioms can also increase what is shown [p.324]
- [12 Facet into Multiple Views](../ch12-facet-into-multiple-views/node.md): faceting into multiple views, another complexity strategy [p.324]
- [14 Embed: Focus+Context](../ch14-embed-focus-context/node.md): the third Reduce choice in Figure 13.1 [p.324]
- [8.3 Geometry](../ch08-arrange-spatial-data/s08-03-geometry.md#s08.03.01): cartographic generalisation, a complex combination of aggregation and filtering, and the choropleth maps that spatial aggregation affects [p.330] [p.340]
- [6.3 No Unjustified 3D](../ch06-rules-thumb/s06-03-no-unjustified-3d/node.md): why dimensionally reduced data should not be shown in 3D [p.345]
