---
id: j1
kind: job-node
title: "J1 Choose a Chart or Idiom"
pdf_pages: [45, 345]
printed_pages: [20, 320]
toc: []
fidelity: summary
---

# J1 Choose a Chart or Idiom

The route from a dataset and a question to an idiom, following the book's what–why–how analysis: abstract the data, abstract the task, then make the how choices of channels, spatial arrangement, colour, faceting and any reduction [pp.82-83]. The book asks you to let the task guide the data abstraction, translate domain questions into generic actions and targets, and treat one goal at a time, and it treats design as iterative refinement rather than a strict sequence [p.69] [p.93]. Children are grouped by the choice they settle: jump to the group for whatever is still unknown and pick by use-when, skipping the rest. With data and task already classified, start at the arrangement groups [p.171].

## Children

### Classify the data and the question

- [2.4 Dataset Types](../ch02-what-data-abstraction/s02-04-dataset-types/node.md) · ~617 words. **Use when** first classifying the whole dataset: rows of items with attributes (table), items joined by links (network or tree), continuous measurements (field), or shapes with positions (geometry) [pp.49-56]
- [2.5 Attribute Types](../ch02-what-data-abstraction/s02-05-attribute-types.md) · ~766 words. **Use when** each column must be labelled categorical, ordinal or quantitative, and ordered ones as sequential, diverging or cyclic, because channel and colormap choices depend on it [pp.56-59]
- [2.6.1 Key versus Value Semantics](../ch02-what-data-abstraction/s02-06-semantics/s02-06-01-key-value-semantics.md) · ~1,082 words. **Use when** a table's columns must be split into keys that index items and values looked up, since the count of each is the core choice for encoding a table [pp.59-63] [p.171]
- [2.6.2 Temporal Semantics](../ch02-what-data-abstraction/s02-06-semantics/s02-06-02-temporal-semantics.md) · ~532 words. **Use when** a column is a date or time and you must decide whether it is a key (a time series) or a value such as a duration [pp.63-65]
- [3.4 Actions](../ch03-why-task-abstraction/s03-04-actions/node.md) · ~413 words. **Use when** turning the user's question into verbs: present or discover, lookup versus browse versus explore, and identify one, compare some or summarize all [pp.70-80]
- [3.5 Targets](../ch03-why-task-abstraction/s03-05-targets.md) · ~703 words. **Use when** naming what the question is about: trends, outliers, extremes, a distribution, correlation between attributes, network paths or topology, or spatial shape [pp.80-82]

### Assign channels

- [5.4 Using Marks and Channels](../ch05-marks-channels/s05-04-using-marks-channels.md) · ~1,117 words. **Use when** assigning each attribute to a channel: ordered attributes to magnitude channels, categorical to identity channels, the most important to the highest-ranked channel [pp.124-128]
- [5.5 Channel Effectiveness](../ch05-marks-channels/s05-05-channel-effectiveness/node.md) · ~495 words. **Use when** a candidate channel may fail: too many values to distinguish, two channels on one mark that interfere, or one item that must pop out [pp.128-137]

### Arrange a table

- [7.3 Arrange by Keys and Values](../ch07-arrange-tables/s07-03-arrange-keys-values.md) · ~314 words. **Use when** the data is a table and the key and value counts are known: no keys suggests a scatterplot, one key a bar chart, two keys a heatmap [pp.170-171]
- [Scatterplots](../idioms/scatterplots.md) · ~654 words. **Use when** a table has two quantitative values and no key, and the question concerns correlation, trends, outliers or clusters among up to hundreds of items [p.173]
- [Line Charts](../idioms/line-charts.md) · ~771 words. **Use when** one quantitative value is shown against an ordered key such as time, with up to hundreds of key levels, and the question is its trend [pp.180-182]
- [Superimposed Line Charts](../idioms/superimposed-line-charts.md) · ~697 words. **Use when** several time series, from a few up to nearly a dozen, are compared at nearby points in one shared frame [pp.315-317]
- [7.5 Separate, Order, and Align: Categorical Regions](../ch07-arrange-tables/s07-05-separate-order-align-categorical/node.md) · ~1,253 words. **Use when** one or two categorical or ordered keys split items into regions: bar, stacked bar and dot charts, streamgraphs, heatmaps [pp.174-186]
- [Scatterplot Matrix (SPLOM)](../idioms/scatterplot-matrix-splom.md) · ~634 words. **Use when** relationships among up to about a dozen quantitative attributes are wanted pairwise, over dozens to hundreds of items [pp.185-186]
- [Parallel Coordinates](../idioms/parallel-coordinates.md) · ~935 words. **Use when** dozens of quantitative attributes must be seen at once to find trends, outliers, extremes or correlation, over hundreds of items [pp.187-191]
- [7.6 Spatial Axis Orientation](../ch07-arrange-tables/s07-06-spatial-axis-orientation/node.md) · ~725 words. **Use when** a part-to-whole or periodic question suggests a radial chart such as a pie, polar area or radial bar chart [pp.192-196]

### Arrange spatial data, networks and trees

- [8 Arrange Spatial Data](../ch08-arrange-spatial-data/node.md) · ~617 words. **Use when** the dataset is geographic or a spatial field, so its given positions take the planar layout and the choice is among maps, isocontours, volume rendering or flow idioms [p.204]
- [9.4 Costs and Benefits: Connection versus Matrix](../ch09-arrange-networks-trees/s09-04-costs-benefits-connection-matrix.md) · ~993 words. **Use when** the dataset is a network and node–link must be weighed against an adjacency matrix by node count, link density and task [pp.234-238]
- [9.5 Containment: Hierarchy Marks](../ch09-arrange-networks-trees/s09-05-containment-hierarchy-marks.md) · ~921 words. **Use when** the dataset is a tree or hierarchy, or a network with a cluster hierarchy, and the question concerns attributes at the leaves, so containment (treemaps, nested circles) is a candidate [pp.238-241]

### Colour and other channels

- [10.3 Colormaps](../ch10-map-color-other-channels/s10-03-colormaps/node.md) · ~700 words. **Use when** an attribute will be coloured and you must choose categorical, sequential, diverging or bivariate colour by attribute type and number of levels; its colormap cards add code hints beside the leaves [pp.250-260]
- [10.4 Other Channels](../ch10-map-color-other-channels/s10-04-other-channels.md) · ~1,403 words. **Use when** colour and position are taken and another attribute needs size, angle, shape, motion or texture [pp.261-265]

### Several views, layers, or too much data

- [12.4 Partition into Views](../ch12-facet-into-multiple-views/s12-04-partition-into-views/node.md) · ~535 words. **Use when** a second or third categorical attribute should split the chart into groups or separate small charts, such as grouped bars or a Trellis matrix [pp.304-313]
- [12.5 Superimpose Layers](../ch12-facet-into-multiple-views/s12-05-superimpose-layers/node.md) · ~585 words. **Use when** a few layers should share one frame, such as a foreground over a background, or you need the other layered idioms [pp.313-320]
- [13.3 Filter](../ch13-reduce-items-attributes/s13-03-filter/node.md) · ~431 words. **Use when** the chosen idiom cannot show every item or attribute and some can be removed by range or by similarity [pp.325-330]
- [13.4 Aggregate](../ch13-reduce-items-attributes/s13-04-aggregate/node.md) · ~745 words. **Use when** items or attributes must be summarised rather than removed: a distribution (histogram, boxplot), an overplotted scatterplot, regions or reduced dimensions [pp.330-345]

## Disambiguation

- **Dataset Types vs Key versus Value Semantics.** 2.4 says what structure the data has; 2.6.1 says, for a table or field, which attributes index it. Do 2.4 first, then 2.6.1 for tables [pp.49-50] [pp.59-62].
- **Actions vs Targets.** Actions are the verbs and targets the nouns they refer to; describe the question with both, as the router's routing table does [p.80].
- **Using Marks and Channels vs Channel Effectiveness.** 5.4 gives the rankings to apply; 5.5 explains the limits that can overrule a rank, such as too few distinguishable levels [pp.126-131].
- **Arrange by Keys and Values vs Separate, Order, and Align: Categorical Regions vs Scatterplots vs Line Charts.** 7.3 is the decision step by key count; Scatterplots is the zero-key answer, Line Charts the one-ordered-key answer, and 7.5 holds every other one- and two-key chart [pp.170-182].
- **Scatterplots vs Scatterplot Matrix (SPLOM) vs Parallel Coordinates vs Aggregate.** Two attributes: one scatterplot; up to about a dozen: SPLOM; dozens: parallel coordinates. Each card's scale is hundreds of items; when dots overplot, 13.4 holds continuous scatterplots [p.173] [p.186] [p.191] [p.332].
- **Line Charts vs Superimposed Line Charts vs Superimpose Layers vs Partition into Views.** One series: Line Charts. Up to nearly a dozen series compared locally: Superimposed Line Charts, usable because thin lines are mostly disjoint, while layers of area marks stay at two or three. For tasks spanning the whole period, especially with more series, juxtaposed small multiples did better; 12.4 builds them [pp.314-317].
- **Separate, Order, and Align: Categorical Regions vs Partition into Views.** 7.5 aligns one bar per key value in a single list; 12.4 applies when another categorical attribute splits those bars into grouped bars or a chart per group [pp.174-176] [pp.304-307].
- **Separate, Order, and Align: Categorical Regions vs Spatial Axis Orientation.** 7.5 uses perpendicular rectilinear axes; 7.6 parallel and radial axes, and the evidence that pies are read less accurately than bars [pp.174-196].
- **Colormaps vs Other Channels.** Hue gives only six to twelve distinguishable bins for small regions; shape and texture can give more bins, and size and angle are magnitude channels for ordered data [pp.251-265].
- **Costs and Benefits: Connection versus Matrix vs Containment: Hierarchy Marks.** 9.4 chooses node–link or matrix for a general network; for a tree, 9.5 weighs containment, which suits attributes at the leaves, against connection, which suits topology [pp.234-241].
- **Filter vs Aggregate.** Filtering removes elements from view; aggregation replaces a group with a derived element that stands for it [pp.324-325].

## Related

- [1.11 Why Are Most Designs Ineffective?](../ch01-whats-vis-why/s01-11-why-most-designs-ineffective.md): consider several alternatives rather than the first chart that fits [pp.37-39]
- [3.7.1 Comparing Two Idioms](../ch03-why-task-abstraction/s03-07-analyzing-deriving-examples/s03-07-01-comparing-two-idioms.md): a worked comparison of two idioms for the same data and task [pp.84-85]
- [3.4.2 Produce](../ch03-why-task-abstraction/s03-04-actions/s03-04-02-produce.md#s03.04.02.03): deriving a new attribute, such as a difference, so the chart shows it directly [pp.75-78]
- [6.3 No Unjustified 3D](../ch06-rules-thumb/s06-03-no-unjustified-3d/node.md): why 3D is rarely the right answer for abstract data [pp.142-143]
- [11 Manipulate View](../ch11-manipulate-view/node.md): when the chosen idiom needs interaction to cope with size or complexity [p.269]
