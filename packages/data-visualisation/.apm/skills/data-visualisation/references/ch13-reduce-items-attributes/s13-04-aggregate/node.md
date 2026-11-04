---
id: s13.04
kind: section-node
title: "Aggregate"
pdf_pages: [330, 345]
printed_pages: [305, 320]
toc: [s13.04]
fidelity: summary
---

# 13.4 Aggregate

Aggregation represents a group of elements with a new derived element that stands in for the whole group, for items or attributes, alone or with filtering [p.330]. Simple operators (average, minimum, maximum, count, sum) are rarely enough; the challenge is to keep the interesting signals while summarising, and the choice is particularly powerful in interactive idioms where the user changes the aggregation level on the fly [p.330].

## Children

- [13.4.1 Item Aggregation](s13-04-01-item-aggregation.md) · ~1,849 words. **Use when** many items of a table must be summarised: distributions of a quantitative attribute, overplotted scatterplots, interactive aggregation level, or cluster hierarchies; also the section's general aggregation guidance [pp.330-338]
- [13.4.2 Spatial Aggregation](s13-04-02-spatial-aggregation.md) · ~567 words. **Use when** aggregating geographic data into regions, where boundary and scale choices (the MAUP) change the result [pp.338-340]
- [13.4.3 Attribute Aggregation: Dimensionality Reduction](s13-04-03-attribute-aggregation-dimensionality-reduction.md) · ~1,172 words. **Use when** a table has many attributes (for example documents as word counts) to synthesise into a few, or you must show or interpret DR output such as MDS scatterplots [pp.340-345]
- [Boxplot Charts](../../idioms/boxplot-charts.md) · ~765 words. **Use when** comparing the distributions of one or many quantitative attributes across categories: spread, skew, outliers, with unlimited items [pp.333-335]
- [Continuous Scatterplots](../../idioms/continuous-scatterplots.md) · ~560 words. **Use when** two quantitative attributes have so many items that a scatterplot overplots, and density per pixel should be shown instead [pp.332-333]
- [Dimensionality Reduction for Document Collections](../../idioms/dimensionality-reduction-for-document-collections.md) · ~791 words. **Use when** a text collection of thousands to millions of documents should be reduced to a 2D scatterplot to verify or discover clusters [pp.341-344]
- [Geographically Weighted Boxplots](../../idioms/geographically-weighted-boxplots.md) · ~701 words. **Use when** regions with several quantitative attributes should be compared locally against the global distribution, at more than one spatial scale [pp.338-340]
- [Hierarchical Parallel Coordinates](../../idioms/hierarchical-parallel-coordinates.md) · ~740 words. **Use when** a multi-attribute table is too large for plain parallel coordinates and the user should move through cluster levels of detail with a slider [pp.336-337]
- [Histograms](../../idioms/histograms.md) · ~635 words. **Use when** showing the distribution of a single quantitative attribute by binning items and counting per bin [p.331]
- [SolarPlot](../../idioms/solarplot.md) · ~663 words. **Use when** the user should change a histogram's aggregation level directly, by resizing the base circle of a radial layout, to see patterns at more than one level (the book's example: ticket sales over 30 years) [pp.335-336]

## Disambiguation

- **Item Aggregation vs Spatial Aggregation vs Attribute Aggregation: Dimensionality Reduction.** Item aggregation merges items of a table; spatial aggregation merges items by geographic region and must respect boundaries and scale; attribute aggregation synthesises new attributes from many [p.330] [p.338] [p.340].
- **Histograms vs Boxplot Charts.** Both summarise a quantitative attribute's distribution. A histogram shows counts per bin and depends on bin size; a boxplot shows five derived numbers per attribute, compact enough to compare roughly hundreds of categories, but standard boxplots are designed for unimodal data [pp.331-334].
- **Histograms vs SolarPlot.** SolarPlot is a radial histogram whose bin count the user changes by resizing its circle [p.331] [p.335].
- **Boxplot Charts vs Geographically Weighted Boxplots.** Plain boxplots summarise whole attributes; gw-boxplots superimpose a local, geographically weighted boxplot on the global one for each region and scale [p.333] [p.340].
- **Continuous Scatterplots vs Dimensionality Reduction for Document Collections.** Both relieve dense scatterplots, but continuous scatterplots aggregate items into per-pixel density for two given attributes, whereas DR synthesises two attributes from thousands [pp.332-333] [p.344].
- **Item Aggregation vs Histograms vs Continuous Scatterplots vs Boxplot Charts vs SolarPlot vs Hierarchical Parallel Coordinates.** Open 13.4.1 to choose among item-aggregation approaches, or for the section's general guidance on operators, dynamic aggregation and hierarchical aggregation. Open a card once one idiom is the candidate and you need its box, use conditions, alternatives and code [pp.330-337].
- **SolarPlot vs Hierarchical Parallel Coordinates.** Both let the user change the aggregation level interactively. SolarPlot changes the bin count of one attribute's histogram by resizing a circle; hierarchical parallel coordinates change the cluster level of detail across a multi-attribute table with a slider [p.335] [pp.336-337].

## Related

- [13.3 Filter](../s13-03-filter/node.md): eliminating elements instead of merging them; the two combine [p.330]
- [1.6 Why Show the Data in Detail?](../../ch01-whats-vis-why/s01-06-why-show-data-detail.md): Anscombe's Quartet, the limits of static aggregation [p.330]
- [8.3 Geometry](../../ch08-arrange-spatial-data/s08-03-geometry.md#s08.03.01): cartographic generalisation and choropleth maps [p.330]
- [3.4.2 Produce](../../ch03-why-task-abstraction/s03-04-actions/s03-04-02-produce.md#s03.04.02.03): deriving new data, which every aggregation does [p.341]
- [6.3 No Unjustified 3D](../../ch06-rules-thumb/s06-03-no-unjustified-3d/node.md): why DR data should not be shown as 3D scatterplots [p.345]
- [Cluster–Calendar Time-Series Vis](../../idioms/cluster-calendar-time-series-vis.md): a hierarchical aggregation example from Figure 6.7 [p.336]
