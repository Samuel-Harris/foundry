---
id: j2
kind: job-node
title: "J2 Write Plotting Code"
pdf_pages: [119, 392]
printed_pages: [94, 367]
toc: []
fidelity: summary
---

# J2 Write Plotting Code

The route for turning a decided idiom into code. Open the idiom's card: its idiom box says what the code must encode, and its last section holds implementation hints marked as not from the book [pp.124-128]. Every card is listed below or under a family node below. Then check the code with [J2 Encoding Checks](j2-encoding-checks.md) [pp.137-139]. If the idiom is not yet chosen, go to [J1 Choose a Chart or Idiom](j1-choose-idiom.md) first [p.171].

## Children

### Chart cards

- [Bar Charts](../idioms/bar-charts.md) · ~801 words. **Use when** coding one categorical key against one quantitative value, for lookup and comparison, with up to hundreds of bars [pp.175-176]
- [Stacked Bar Charts](../idioms/stacked-bar-charts.md) · ~799 words. **Use when** coding two categorical keys with one quantitative value as stacked segments showing absolute totals and parts [pp.176-178]
- [Line Charts](../idioms/line-charts.md) · ~771 words. **Use when** coding one series of a quantitative value against an ordered key such as time to show trend, including the aspect ratio [pp.180-182]
- [Superimposed Line Charts](../idioms/superimposed-line-charts.md) · ~697 words. **Use when** coding several series as lines in one shared frame, one colour per series, for a few and up to nearly a dozen lines [pp.315-317]
- [Dot Charts](../idioms/dot-charts.md) · ~584 words. **Use when** coding values against an ordered key with point marks and no connecting lines [pp.180-182]
- [Scatterplots](../idioms/scatterplots.md) · ~654 words. **Use when** coding two quantitative attributes as horizontal and vertical position of point marks; for zoom and pan add Geometric Zooming [pp.171-173] [pp.279-280]
- [Histograms](../idioms/histograms.md) · ~635 words. **Use when** coding the distribution of one quantitative attribute by binning items and counting per bin [p.331]
- [Boxplot Charts](../idioms/boxplot-charts.md) · ~765 words. **Use when** coding distributions of one or more quantitative attributes side by side, showing median, quartiles, spread and outliers [pp.333-335]
- [Heatmaps](../idioms/heatmaps.md) · ~642 words. **Use when** coding a matrix of two categorical keys with a quantitative value in each cell's colour [pp.185-186]
- [Cluster Heatmaps](../idioms/cluster-heatmaps.md) · ~741 words. **Use when** rows and columns of that matrix must be reordered by hierarchical clustering, with dendrograms drawn on the edges [pp.183-185]
- [Scatterplot Matrix (SPLOM)](../idioms/scatterplot-matrix-splom.md) · ~634 words. **Use when** coding a grid of every pairwise scatterplot for up to about a dozen attributes [pp.185-186]
- [Parallel Coordinates](../idioms/parallel-coordinates.md) · ~935 words. **Use when** coding many quantitative attributes as parallel vertical axes with one polyline per item [pp.187-191]
- [Pie Charts](../idioms/pie-charts.md) · ~728 words. **Use when** a part-to-whole chart with up to about a dozen wedges is required despite its lower accuracy than bars [pp.193-196]

### Interaction cards (zoom, pan, brush, select)

- [Geometric Zooming](../idioms/geometric-zooming.md) · ~598 words. **Use when** coding zoom and pan over any fixed layout, such as a zoomable scatterplot, where marks only change drawn size [pp.279-280]
- [Highlighting](../idioms/highlighting.md) · ~701 words. **Use when** coding how clicked, hovered or brushed items are shown, by outline, colour, size or motion, in one view or linked views [pp.276-278] [p.292]
- [11 Manipulate View](../ch11-manipulate-view/node.md) · ~1,185 words. **Use when** the interaction is anything else in one view: semantic zooming, constrained camera, animated transitions, re-sorting (LineUp), slicing, cutting or projecting [pp.267-269]
- [11.4 Select Elements](../ch11-manipulate-view/s11-04-select-elements/node.md) · ~488 words. **Use when** coding selection targets and outcomes, or drawn link curves joining selected items across views [pp.274-279]

### Colour and channel cards

- [Categorical Colormaps](../idioms/categorical-colormaps.md) · ~891 words. **Use when** coding a palette for a categorical column: how many colours, saturation by mark size, what to do with too many categories [pp.251-254]
- [Ordered Colormaps](../idioms/ordered-colormaps.md) · ~912 words. **Use when** coding a sequential or diverging ramp for an ordinal or quantitative column, or deciding against a rainbow map [pp.254-259]
- [10.3 Colormaps](../ch10-map-color-other-channels/s10-03-colormaps/node.md) · ~700 words. **Use when** two attributes share colour (Bivariate Colormaps card) or a palette must survive red–green deficiency (Colorblind-Safe card) [pp.259-260]
- [10 Map Color and Other Channels](../ch10-map-color-other-channels/node.md) · ~815 words. **Use when** an attribute goes on size, angle, shape, curvature, motion or texture, each with its own card [pp.261-265]

### Other idiom families

- [7 Arrange Tables](../ch07-arrange-tables/node.md) · ~885 words. **Use when** source code or a log needs a dense pixel overview (Dense Software Overviews) [p.199]
- [7.5 Separate, Order, and Align: Categorical Regions](../ch07-arrange-tables/s07-05-separate-order-align-categorical/node.md) · ~1,253 words. **Use when** a one- or two-key chart card is not listed above, such as Streamgraphs [pp.174-186]
- [7.6 Spatial Axis Orientation](../ch07-arrange-tables/s07-06-spatial-axis-orientation/node.md) · ~725 words. **Use when** coding radial alternatives to a pie: Radial Bar, Polar Area, or Normalized Stacked Bar Charts [pp.192-196]
- [8 Arrange Spatial Data](../ch08-arrange-spatial-data/node.md) · ~617 words. **Use when** coding a map coloured by region (Choropleth Map) or a tensor field of ellipsoid glyphs [p.206] [pp.219-221]
- [8.4 Scalar Fields: One Value](../ch08-arrange-spatial-data/s08-04-scalar-fields-one-value/node.md) · ~458 words. **Use when** a scalar field needs contour lines, isosurfaces or volume-rendering transfer functions [pp.207-214]
- [8.5 Vector Fields: Multiple Values](../ch08-arrange-spatial-data/s08-05-vector-fields-multiple-values/node.md) · ~445 words. **Use when** a flow field needs arrow glyphs, streamlines, texture or similarity-clustered streamlines [pp.214-219]
- [9 Arrange Networks and Trees](../ch09-arrange-networks-trees/node.md) · ~816 words. **Use when** coding a network or tree. Cards with hints: [Force-Directed Placement](../idioms/force-directed-placement.md), [sfdp](../idioms/multilevel-force-directed-placement-sfdp.md), [Adjacency Matrix View](../idioms/adjacency-matrix-view.md), [Treemaps](../idioms/treemaps.md) (nested rectangles), [GrouseFlocks](../idioms/grouseflocks.md) (hierarchies over networks) [pp.229-241]
- [12.3 Juxtapose and Coordinate Views](../ch12-facet-into-multiple-views/s12-03-juxtapose-coordinate-views/node.md) · ~877 words. **Use when** coding linked views: an overview map with detail (Bird's-Eye Maps), multiform views (EDV, Improvise), Cerebral or microarray overview–detail [pp.292-304]
- [12.4 Partition into Views](../ch12-facet-into-multiple-views/s12-04-partition-into-views/node.md) · ~535 words. **Use when** coding small multiples split by categorical keys, such as a Trellis matrix of dot charts [pp.304-313]
- [12.5 Superimpose Layers](../ch12-facet-into-multiple-views/s12-05-superimpose-layers/node.md) · ~585 words. **Use when** coding map layers told apart by luminance (Cartographic Layering) or bundled edges over a hierarchy [pp.313-320]
- [13.3 Filter](../ch13-reduce-items-attributes/s13-03-filter/node.md) · ~431 words. **Use when** coding slider-driven dynamic queries (FilmFinder) or attribute filtering by similarity (DOSFA) [pp.325-330]
- [13.4 Aggregate](../ch13-reduce-items-attributes/s13-04-aggregate/node.md) · ~745 words. **Use when** points overplot (Continuous Scatterplots), or coding interactive aggregation (SolarPlot), hierarchical parallel coordinates, dimensionality reduction or geographic boxplots [pp.330-345]
- [14 Embed: Focus+Context](../ch14-embed-focus-context/node.md) · ~1,062 words. **Use when** coding a fisheye lens, magic lens, hyperbolic tree, elided tree or stretch-and-squish navigation [pp.347-359]
- [15 Analysis Case Studies](../ch15-analysis-case-studies/node.md) · ~909 words. **Use when** coding a roll-up network of attribute groups (PivotGraph) [pp.380-383]
- [6.3 No Unjustified 3D](../ch06-rules-thumb/s06-03-no-unjustified-3d/node.md) · ~799 words. **Use when** asked for a 3D chart of abstract data; holds the 2D cluster–calendar and constrained 3D time-series cards [pp.142-143] [pp.150-153]

### Checks and lookup

- [J2 Encoding Checks](j2-encoding-checks.md) · ~589 words. **Use when** the card is open and the code must be checked: sort order, aspect ratio, baselines, channel limits, luminance contrast, colour interpolation [pp.124-139] [pp.245-249]
- [Idiom and Concept Lookup](../lookup.md) · ~3,032 words. **Use when** you know an idiom's name but not its family; maps all 76 card names to files [pp.6-15]

## Disambiguation

- **Bar Charts vs Dot Charts vs Line Charts.** Bars suit a categorical key; dots show values without bars; a line connects an ordered key and invites trend reading, so never draw lines across a categorical key [p.176] [pp.180-181].
- **Line Charts vs Superimposed Line Charts.** One series: Line Charts. Several series in one frame: Superimposed Line Charts, usable with nearly a dozen thin lines but not with many dozens; for tasks spanning the whole period, small multiples did better [pp.315-317].
- **Bar Charts vs Stacked Bar Charts vs Pie Charts.** A second key gives stacks for absolute part-to-whole; a pie needs angle and area judgements less accurate than bar length [p.178] [p.193]. Grouped bars have no card: use the Bar Charts hints and 12.4.2 in J2 Encoding Checks [pp.306-307].
- **Heatmaps vs Cluster Heatmaps.** Heatmaps is the basic matrix; Cluster Heatmaps adds reordering of rows and columns together by cluster hierarchies, to group similar cells, and draws the dendrograms [p.185].
- **Histograms vs Boxplot Charts.** A histogram bins one attribute's full distribution; a boxplot compresses each distribution to a few statistics so many sit side by side [p.331] [pp.333-335].
- **Scatterplots vs Scatterplot Matrix (SPLOM) vs Parallel Coordinates vs Aggregate.** Two attributes: scatterplot; up to a dozen: SPLOM; dozens: parallel coordinates; dots overplotting: Continuous Scatterplots under 13.4 [p.173] [p.186] [p.191] [p.332].
- **Geometric Zooming vs Manipulate View.** Geometric zooming only resizes marks; when items should change representation as they gain pixels, use semantic zooming, and when the camera must not get lost, constrained navigation, both under chapter 11 [p.280] [p.282].
- **Highlighting vs Select Elements vs Juxtapose and Coordinate Views.** Highlighting codes how a selection looks; 11.4 what can be selected and what it triggers; 12.3 carries it into other views as linked highlighting, also called brushing [pp.274-279] [p.292].
- **Categorical Colormaps vs Ordered Colormaps vs Colormaps.** Choose the card by the column's type; 10.3 holds the bivariate and colour-deficiency cards [p.250] [pp.259-260].
- **Separate, Order, and Align: Categorical Regions vs Partition into Views.** 7.5 lays one or two keys into regions of one chart; 12.4 splits the chart into separate small charts by further keys [pp.174-176] [pp.304-307].

## Related

- [12.3.2 Share Data: All, Subset, None](../ch12-facet-into-multiple-views/s12-03-juxtapose-coordinate-views/s12-03-02-share-data-all-subset.md): small multiples, the alternative to superimposed lines for whole-period tasks [p.317]
- [12.3.3 Share Navigation: Synchronize](../ch12-facet-into-multiple-views/s12-03-juxtapose-coordinate-views/s12-03-03-share-navigation-synchronize.md): one zoom or pan driving several views [p.301]
