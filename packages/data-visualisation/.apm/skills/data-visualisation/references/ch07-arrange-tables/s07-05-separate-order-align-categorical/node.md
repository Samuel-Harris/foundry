---
id: s07.05
kind: section-node
title: "Separate, Order, and Align: Categorical Regions"
pdf_pages: [174, 186]
printed_pages: [149, 161]
toc: [s07.05]
fidelity: summary
---

# 7.5 Separate, Order, and Align: Categorical Regions

How to use space for categorical key attributes. Encoding them with spatial position would violate expressiveness, so items sharing a categorical value are drawn in the same region; the regions are then separated by a categorical attribute, ordered by an ordered attribute, and optionally aligned [p.174]. The children split by alignment: a list (7.5.1), a matrix for two keys (7.5.2), a volume for three keys (7.5.3) and recursive subdivision for multiple keys (7.5.4) [pp.174-186]. The key count and the alignment differ for stacked bar charts and streamgraphs: they take two keys but use list alignment, so the book places them under 7.5.1 [pp.176-179].

## Children

- [7.5.1 List Alignment: One Key](s07-05-01-list-alignment-one-key.md) · ~1,470 words. **Use when** items are laid out as a 1D list along one key and you need the full narrative: bar, dot and line charts (one key), and stacked bar charts and streamgraphs (a second key stacked inside each bar or layer); also region ordering, the Zacks and Tversky bar-versus-line study and line-chart aspect ratio (banking to 45°) [pp.174-183]
- [7.5.2 Matrix Alignment: Two Keys](s07-05-02-matrix-alignment-two-keys.md) · ~815 words. **Use when** a table has two keys laid out as rows and columns, or many attributes shown pairwise; narrative on heatmaps, matrix reordering, dendrograms and SPLOMs [pp.182-186]
- [7.5.3 Volumetric Grid: Three Keys](s07-05-03-volumetric-grid-three-keys.md) · ~136 words. **Use when** tempted to align a three-key nonspatial table in a 3D grid; the book advises against it [p.186]
- [7.5.4 Recursive Subdivision: Multiple Keys](s07-05-04-recursive-subdivision-multiple-keys.md) · ~131 words. **Use when** a table has three or more keys and cells of a list or matrix must be subdivided by containment [p.186]
- [Bar Charts](../../idioms/bar-charts.md) · ~801 words. **Use when** a table has one categorical key and one quantitative value, to look up and compare values, with dozens to hundreds of key levels [p.176]
- [Stacked Bar Charts](../../idioms/stacked-bar-charts.md) · ~799 words. **Use when** a table has two categorical keys and one quantitative value, for part-to-whole, lookup or trends; main key dozens to hundreds of levels, stacked key several to one dozen. Listed under 7.5.1 because the bars form a list along the primary key [pp.176-178]
- [Streamgraphs](../../idioms/streamgraphs.md) · ~634 words. **Use when** a table has two keys, an ordered time key with hundreds of time points and a categorical key with dozens to hundreds of levels, plus a count value, and the continuity of each category's layer over time matters [pp.178-179]
- [Dot Charts](../../idioms/dot-charts.md) · ~584 words. **Use when** one quantitative value is shown against an ordered key using aligned point marks rather than bars, with items separated and ordered into regions by the key and no connecting lines [p.180]
- [Line Charts](../../idioms/line-charts.md) · ~771 words. **Use when** one quantitative value is shown against an ordered key with up to hundreds of levels and the task is to show trend [p.181]
- [Heatmaps](../../idioms/heatmaps.md) · ~642 words. **Use when** a table has two categorical keys with up to hundreds of levels and one quantitative value, to find clusters and outliers or summarise up to a million items, with only 3 to 11 distinguishable value levels [p.185]
- [Cluster Heatmaps](../../idioms/cluster-heatmaps.md) · ~741 words. **Use when** a heatmap's rows and columns should be reordered by derived cluster hierarchies, shown as dendrograms, to group similar cells [p.185]
- [Scatterplot Matrix (SPLOM)](../../idioms/scatterplot-matrix-splom.md) · ~634 words. **Use when** a table has up to about a dozen attributes and dozens to hundreds of items, and every pair should be checked for correlation, trends and outliers [p.186]

## Disambiguation

- **Bar Charts vs Dot Charts vs Line Charts.** All show one value and one key in a rectilinear layout. Bar charts use line marks, suit a categorical key and invite discrete comparison and lookup. Dot charts use point marks. Line charts connect the points, imply a trend and suit the task of spotting trends; they should not be used for a categorical key [pp.175-181]. The book is ambiguous on the dot chart's key: its text describes a categorical attribute, while its idiom box and example use an ordered key (year) [p.180].
- **Bar Charts vs Stacked Bar Charts.** One key versus two. In a stacked bar only the lowest segment and the full bar sit on a common baseline; the other segments are harder to compare across bars, and the stacked key is limited to about a dozen categories [pp.176-177]. For proportions rather than absolute values, see normalized stacked bar charts under 7.6 [p.177].
- **Stacked Bar Charts vs Streamgraphs.** Both stack a value by a second key. Stacked bars use local glyphs per primary-key level and support lookup at each one; streamgraphs use globally derived geometry over an ordered time key, emphasise each layer's continuity, and scale to more categories because most layers do not span the timeline [pp.176-179].
- **Stacked Bar Charts vs Streamgraphs vs Heatmaps.** All three show one quantitative value against two keys. Stacked bars and streamgraphs list one key along an axis and stack the other key's values as lengths or layer heights, with several to one dozen stacked levels for stacked bars; a heatmap gives each key its own axis and encodes the value with colour, with hundreds of levels per key but only 3 to 11 distinguishable value levels [pp.176-185].
- **Line Charts vs Streamgraphs.** Both suit an ordered key such as time. A line chart shows one value per key level for trend; a streamgraph shows counts for many categories as stacked layers whose height encodes the count [pp.178-181].
- **Heatmaps vs Cluster Heatmaps.** A cluster heatmap is a heatmap whose rows and columns are reordered by two derived cluster hierarchies, drawn as juxtaposed dendrograms; use it when the goal is grouping similar cells [p.185].
- **Heatmaps vs Scatterplot Matrix (SPLOM).** A heatmap cell shows one value for two categorical keys; a SPLOM cell shows a whole scatterplot, its key is a derived list of the original attributes, and it scales to about a dozen attributes rather than hundreds of levels [pp.184-186].
- **List Alignment: One Key vs Bar Charts vs Stacked Bar Charts vs Streamgraphs vs Dot Charts vs Line Charts.** 7.5.1 holds the comparative narrative, ordering advice and banking to 45°; each card holds one idiom's box, use and avoid conditions, and code [pp.174-183].
- **Matrix Alignment: Two Keys vs Heatmaps vs Cluster Heatmaps vs Scatterplot Matrix (SPLOM).** 7.5.2 holds the narrative on matrix alignment, scalability and reordering; each card holds one idiom's box and code [pp.182-186].
- **Volumetric Grid: Three Keys vs Recursive Subdivision: Multiple Keys.** The book calls a 3D grid typically not recommended for nonspatial data because of occlusion and perspective distortion, and offers recursive subdivision as the alternative for three keys [p.186].

## Related

- [7.3 Arrange by Keys and Values](../s07-03-arrange-keys-values.md): how to count keys and values to arrive here [p.174]
- [7.6.3 Radial Layouts](../s07-06-spatial-axis-orientation/s07-06-03-radial-layouts.md): normalized stacked bar charts, pie charts and radial bar charts [p.177]
- [13.4.1 Item Aggregation](../../ch13-reduce-items-attributes/s13-04-aggregate/s13-04-01-item-aggregation.md): histograms, which Wilkinson's dot plot resembles, and hierarchical clustering [pp.180-185]
- [10.3 Colormaps](../../ch10-map-color-other-channels/s10-03-colormaps/node.md): colormap design for heatmaps [p.183]
- [10.3.4 Colorblind-Safe Colormap Design](../../ch10-map-color-other-channels/s10-03-colormaps/s10-03-04-colorblind-safe-colormap-design.md): the problem with red–green heatmaps [p.183]
- [12.3.2 Share Data: All, Subset, None](../../ch12-facet-into-multiple-views/s12-03-juxtapose-coordinate-views/s12-03-02-share-data-all-subset.md): small multiples, of which SPLOMs are an example [p.185]
- [15.3 Graph-Theoretic Scagnostics](../../ch15-analysis-case-studies/s15-03-graph-theoretic-scagnostics.md): a SPLOM extension with derived attributes [p.186]
- [15.5 Hierarchical Clustering Explorer](../../ch15-analysis-case-studies/s15-05-hierarchical-clustering-explorer.md): a compact heatmap-style SPLOM overview [p.186]
- [6.3 No Unjustified 3D](../../ch06-rules-thumb/s06-03-no-unjustified-3d/node.md): why volumetric grids are not recommended [p.186]
- [12.4 Partition into Views](../../ch12-facet-into-multiple-views/s12-04-partition-into-views/node.md): partitioning by multiple keys in depth [p.186]
- [9.3 Matrix Views](../../ch09-arrange-networks-trees/s09-03-matrix-views.md): the same 2D matrix alignment applied to networks [p.183]
