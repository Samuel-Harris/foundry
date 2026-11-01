---
id: ch07
kind: chapter-node
title: "Arrange Tables"
pdf_pages: [169, 201]
printed_pages: [144, 176]
toc: [ch07]
fidelity: summary
---

# 7 Arrange Tables

How to use space to encode tabular data, the most crucial visual encoding choice. Four design choices: express quantitative values with position; separate, order and align categorical regions; orient the axes rectilinearly, in parallel or radially; and choose layout density [pp.169-170]. Which idiom fits turns first on how many key and value attributes the table has: no keys and two values for scatterplots, one key for bar charts, two keys for heatmaps, many for scatterplot matrices [p.171].

## Children

- [7.1 The Big Picture](s07-01-big-picture.md) · ~279 words. **Use when** you need the map of all four table-arrangement choices and their sub-options (list, matrix, volume, subdivision; rectilinear, parallel, radial; dense, space-filling) before descending [pp.169-170]
- [7.2 Why Arrange?](s07-02-why-arrange.md) · ~217 words. **Use when** justifying why the spatial channels are the most crucial encoding choice, and why no nonspatial channel is highly effective for every attribute type [p.170]
- [7.3 Arrange by Keys and Values](s07-03-arrange-keys-values.md) · ~314 words. **Use when** you have a table and must first count its key and value attributes to pick an idiom family; defines keys, values and levels [pp.170-171]
- [7.4 Express: Quantitative Values](s07-04-express-quantitative-values.md) · ~493 words. **Use when** the table has quantitative value attributes and no keys to place, such as two quantitative attributes to compare for correlation, outliers or distribution; covers position along an axis, glyphs and the scatterplot narrative [pp.171-173]
- [7.5 Separate, Order, and Align: Categorical Regions](s07-05-separate-order-align-categorical/node.md) · ~1,253 words. **Use when** the table has one or more key attributes that split items into regions. One key: bar, dot and line charts [pp.175-181]. Two keys: stacked bar charts and streamgraphs, which list one key along the axis and stack the second inside each bar or layer (the book places them under 7.5.1 list alignment), or heatmaps and cluster heatmaps in a matrix [pp.176-185]. Many attributes compared pairwise: SPLOMs [p.186]. Three or more keys: volumetric grids and recursive subdivision [p.186]
- [7.6 Spatial Axis Orientation](s07-06-spatial-axis-orientation/node.md) · ~725 words. **Use when** choosing between perpendicular, parallel and radial axes: many quantitative attributes at once (parallel coordinates), periodic data, or part-to-whole charts (pie, polar area, normalized stacked bar) [pp.187-196]
- [7.7 Spatial Layout Density](s07-07-spatial-layout-density.md) · ~718 words. **Use when** showing as many items as possible in one overview with tiny marks (dense, pixel-oriented layouts), or weighing space-filling layouts against the loss of white space [pp.196-200]
- [7.8 Further Reading](s07-08-further-reading.md) · ~354 words. **Use when** looking for primary sources on chart taxonomies, statistical graphics, streamgraphs, banking to 45°, matrix reordering, parallel coordinates, radial or dense layouts [pp.200-201]
- [Scatterplots](../idioms/scatterplots.md) · ~654 words. **Use when** a table has two quantitative value attributes and the task is to find trends, outliers, distribution or correlation, or locate clusters, for up to hundreds of items; box, use conditions and code [p.173]
- [Dense Software Overviews](../idioms/dense-software-overviews.md) · ~861 words. **Use when** text with numbered lines, such as source code or a test log, needs an overview of up to ten thousand lines to locate faults or summarise results and coverage; box, use conditions and code [p.199]

## Disambiguation

- **The Big Picture vs Arrange by Keys and Values.** 7.1 lists the design choices; 7.3 says which one a given table needs by counting its keys and values [pp.170-171].
- **The Big Picture vs Why Arrange?.** 7.1 maps the options; 7.2 argues why space is the dominant channel, with no idioms [p.170].
- **Express: Quantitative Values vs Scatterplots.** 7.4 holds the narrative on expressing values, glyphs and the scatterplot example; the card holds the idiom box, use and avoid conditions, and code [pp.171-173].
- **Scatterplots vs Separate, Order, and Align: Categorical Regions vs Spatial Axis Orientation.** All handle quantitative attributes. Two attributes: Scatterplots. Up to about a dozen attributes, compared pairwise for correlation: the scatterplot matrix under 7.5. Dozens of attributes, for ranges, outliers and overview: parallel coordinates under 7.6, where the book notes SPLOMs are easier for correlation [pp.173-188].
- **Separate, Order, and Align: Categorical Regions vs Spatial Axis Orientation.** Both contain bar-family charts. 7.5 sorts idioms by how many keys define the regions (one key: bar, dot, line; two keys: stacked bar, streamgraph, heatmap); 7.6 sorts them by axis orientation, and holds radial bar charts, pie charts, polar area charts and normalized stacked bar charts for part-to-whole tasks [pp.174-195].
- **Spatial Layout Density vs Dense Software Overviews.** 7.7 covers dense and space-filling layouts in general; the card is the Tarantula example for numbered text, with its box [pp.196-199].

## Related

- [2.6.1 Key versus Value Semantics](../ch02-what-data-abstraction/s02-06-semantics/s02-06-01-key-value-semantics.md): the key and value distinction this chapter's choices depend on [p.170]
- [5 Marks and Channels](../ch05-marks-channels/node.md): the effectiveness and expressiveness principles and the primacy of spatial position [p.170]
- [6.3 No Unjustified 3D](../ch06-rules-thumb/s06-03-no-unjustified-3d/node.md): why volumetric grids and third spatial axes are avoided for nonspatial tables [p.186]
- [8 Arrange Spatial Data](../ch08-arrange-spatial-data/node.md): the fifth arrangement choice, using a given spatial layout, for spatial data [p.170]
- [9 Arrange Networks and Trees](../ch09-arrange-networks-trees/node.md): arrangements for networks and trees, including the space-filling tree layouts cited in 7.7.2 [p.199]
- [10.3 Colormaps](../ch10-map-color-other-channels/s10-03-colormaps/node.md): colormap design for heatmaps [p.183]
- [12.4 Partition into Views](../ch12-facet-into-multiple-views/s12-04-partition-into-views/node.md): glyphs, views and partitioning by multiple keys [pp.171-186]
- [13.4.1 Item Aggregation](../ch13-reduce-items-attributes/s13-04-aggregate/s13-04-01-item-aggregation.md): histograms, hierarchical clustering and hierarchical parallel coordinates for larger tables [pp.180-189]
- [15 Analysis Case Studies](../ch15-analysis-case-studies/node.md): scagnostics, VisDB and the Hierarchical Clustering Explorer extend this chapter's idioms [pp.186-197]
