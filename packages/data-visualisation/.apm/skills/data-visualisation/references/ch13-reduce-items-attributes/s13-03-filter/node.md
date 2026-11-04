---
id: s13.03
kind: section-node
title: "Filter"
pdf_pages: [325, 330]
printed_pages: [300, 305]
toc: [s13.03]
fidelity: summary
---

# 13.3 Filter

Filtering reduces the number of elements shown by simply eliminating some, applied to items or attributes; a straightforward approach lets the user select ranges of interest [p.325]. In interactive vis it is often done with dynamic queries, a tightly coupled loop between encoding and widgets so the display updates immediately [p.325].

## Children

- [13.3.1 Item Filtering](s13-03-01-item-filtering.md) · ~885 words. **Use when** a table has too many items and you want to drop those outside chosen attribute ranges while keeping every attribute; covers why typed min/max fails, dynamic queries, scented widgets and filter examples [pp.325-328]
- [13.3.2 Attribute Filtering](s13-03-02-attribute-filtering.md) · ~493 words. **Use when** a table has too many attributes (dimensions) and you want to keep every item but drop attributes, often by ordering them on a similarity measure such as variance [pp.328-330]
- [DOSFA](../../idioms/dosfa.md) · ~569 words. **Use when** a table has so many attributes that its display is too dense to show structure (the book's example: 215 word-count attributes drawn as star plots), and attributes should be ordered by similarity and filtered by similarity and importance thresholds [p.329]
- [FilmFinder](../../idioms/filmfinder.md) · ~640 words. **Use when** designing browsing of a multi-attribute table with a scatterplot overview, sliders and buttons that filter items immediately, and a popup detail view [pp.326-328]

## Disambiguation

- **Item Filtering vs Attribute Filtering.** Item filtering shows fewer items with all attributes; attribute filtering shows all items with fewer attributes; they can be combined [pp.326-329].
- **Item Filtering vs FilmFinder.** Open 13.3.1 to design filtering controls in general: why typed min/max ranges fail, dynamic queries, scented widgets and the book's other filtering examples. Open the FilmFinder card when a scatterplot overview with sliders and buttons that filter items immediately is already the candidate design and you need its System box, use conditions and code [pp.325-328].
- **Attribute Filtering vs DOSFA.** Open 13.3.2 to choose how to drop attributes in general: similarity measures such as variance, global versus partial matching, and combining with item filtering. Open the DOSFA card when a concrete many-attribute display is too dense to read and you want the worked star-plot example with ordering and filtering thresholds, plus code [pp.328-330].

## Related

- [13.2 Why Reduce?](../s13-02-why-reduce.md): the "out of sight, out of mind" risk of filtering, against aggregation [pp.324-325]
- [13.4 Aggregate](../s13-04-aggregate/node.md): the alternative that merges rather than eliminates elements [p.330]
- [7.6.3 Radial Layouts](../../ch07-arrange-tables/s07-06-spatial-axis-orientation/s07-06-03-radial-layouts.md): star plots, used in DOSFA [p.329]
- [Improvise](../../idioms/improvise.md): a coordinated-view system that uses checkbox filtering (Figure 12.7) [p.328]
- [Multiform Overview–Detail Microarrays](../../idioms/multiform-overview-detail-microarrays.md): range sliders and a line-chart range selection that filters a scatterplot (Figure 12.4) [p.328]
