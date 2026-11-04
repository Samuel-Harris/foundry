---
id: j4
kind: job-node
title: "J4 Design Interactive and Multi-View Dashboards"
pdf_pages: [150, 392]
printed_pages: [125, 367]
toc: []
fidelity: summary
---

# J4 Design Interactive and Multi-View Dashboards

The route for a tool with several views, interaction or more data than one static view can hold. The book names five ways to handle such complexity: derive new data, change a view over time, facet into multiple views, reduce what is shown, and embed focus and context together [p.269] [p.290]. The five can be combined; children are grouped by approach [pp.290-292]. Choose each view's idiom with [J1 Choose a Chart or Idiom](j1-choose-idiom.md) [p.171].

## Children

### Facet into views or layers

- [12.2 Why Facet?](../ch12-facet-into-multiple-views/s12-02-why-facet.md) · ~671 words. **Use when** first deciding between side-by-side views, one view that changes over time, and layers in one view, with the limits on how many views or layers are workable [pp.290-292]
- [12.3 Juxtapose and Coordinate Views](../ch12-facet-into-multiple-views/s12-03-juxtapose-coordinate-views/node.md) · ~877 words. **Use when** several views must be linked by encoding, data shown or navigation, and arranged on screen [pp.292-304]
- [12.3.1 Share Encoding: Same/Different](../ch12-facet-into-multiple-views/s12-03-juxtapose-coordinate-views/s12-03-01-share-encoding-same-different.md) · ~628 words. **Use when** a selection in one view should highlight the same items in the others (linked highlighting, brushing), or views should use different encodings of the same data [pp.292-294]
- [12.3.2 Share Data: All, Subset, None](../ch12-facet-into-multiple-views/s12-03-juxtapose-coordinate-views/s12-03-02-share-data-all-subset.md) · ~1,218 words. **Use when** one view is an overview and others show a selected subset in detail, such as a time window picked by slider from an overview of long time series; or each view shows one partition as small multiples [pp.294-301]
- [12.3.3 Share Navigation: Synchronize](../ch12-facet-into-multiple-views/s12-03-juxtapose-coordinate-views/s12-03-03-share-navigation-synchronize.md) · ~112 words. **Use when** panning or zooming one view must move the others, as with an overview map driving a detail map (Bird's-Eye Maps) [p.301] [pp.295-296]
- [12.4 Partition into Views](../ch12-facet-into-multiple-views/s12-04-partition-into-views/node.md) · ~535 words. **Use when** categorical attributes should split one large table into a grid or list of aligned small charts, and their order must be chosen [pp.304-313]
- [12.5 Superimpose Layers](../ch12-facet-into-multiple-views/s12-05-superimpose-layers/node.md) · ~585 words. **Use when** screen space is short and two or three layers of area marks can share one frame, or a selection should draw a dynamic foreground layer [pp.313-320]
- [Superimposed Line Charts](../idioms/superimposed-line-charts.md) · ~697 words. **Use when** time series for up to nearly a dozen items should share one frame for comparisons at nearby time points [pp.315-317]
- [Exploratory Data Visualizer (EDV)](../idioms/exploratory-data-visualizer-edv.md) · ~654 words. **Use when** a table needs a few multiform views (bars, scatterplots, histograms) where a selection in one shows its distribution in the rest [pp.293-294]
- [Improvise](../idioms/improvise.md) · ~669 words. **Use when** a geographic and multidimensional dataset needs many coordinated views at once, mixing small multiples, overview–detail and linked highlighting [pp.302-303]

### Interaction within a view

- [11.3 Change View over Time](../ch11-manipulate-view/s11-03-change-view-over-time.md) · ~1,234 words. **Use when** users should re-sort, re-encode, re-align or switch idiom within a view, with animated transitions between states [pp.269-274]
- [11.4 Select Elements](../ch11-manipulate-view/s11-04-select-elements/node.md) · ~488 words. **Use when** designing click and hover targets, selection highlighting, and what a selection triggers in this and other views [pp.274-279]
- [11.5 Navigate: Changing Viewpoint](../ch11-manipulate-view/s11-05-navigate-changing-viewpoint.md) · ~1,213 words. **Use when** users zoom and pan a fixed layout, and items should change representation with their pixels (semantic zooming) or the camera should be constrained [pp.279-283]

### Rules of thumb

- [6.5 Eyes Beat Memory](../ch06-rules-thumb/s06-05-eyes-beat-memory.md) · ~866 words. **Use when** justifying side-by-side views over animation or flipping between states, since comparison by eye beats comparison from memory [pp.156-159]
- [6.7 Overview First, Zoom and Filter, Details on Demand](../ch06-rules-thumb/s06-07-overview-first-zoom-filter.md) · ~559 words. **Use when** planning the dashboard's overall flow from an overview to filtered and detailed views [pp.160-162]
- [6.8 Responsiveness Is Required](../ch06-rules-thumb/s06-08-responsiveness-required.md) · ~875 words. **Use when** setting latency budgets for filtering, brushing and transitions, and choosing click or hover for details [pp.162-165]

### Reduce: filter and aggregate

- [13.3 Filter](../ch13-reduce-items-attributes/s13-03-filter/node.md) · ~431 words. **Use when** sliders, buttons or other controls should remove items or attributes immediately (dynamic queries, scented widgets) [pp.325-330]
- [FilmFinder](../idioms/filmfinder.md) · ~640 words. **Use when** you want the book's example of a scatterplot overview filtered by sliders with a popup detail view [pp.326-328]
- [13.4 Aggregate](../ch13-reduce-items-attributes/s13-04-aggregate/node.md) · ~745 words. **Use when** a view must summarise far more items than pixels, or let users change the aggregation level interactively [pp.330-345]
- [SolarPlot](../idioms/solarplot.md) · ~663 words. **Use when** users should change the aggregation level of a long time series on the fly: a small circle shows 30 years of ticket sales as a rising trend, an enlarged one shows seasons within each year [pp.335-336]
- [Cluster–Calendar Time-Series Vis](../idioms/cluster-calendar-time-series-vis.md) · ~974 words. **Use when** a year of daily curves should be clustered into a few average curves linked to a calendar, showing seasonal and smaller-scale patterns [pp.150-152] [p.336]

### Embed focus in context

- [14.3 Elide](../ch14-embed-focus-context/s14-03-elide.md) · ~373 words. **Use when** focus items should stay detailed while context is aggregated and the rest omitted, by a degree-of-interest function often built on hierarchical structure [pp.349-350]
- [DOITrees Revisited](../idioms/doitrees-revisited.md) · ~596 words. **Use when** a tree of hundreds of thousands of nodes needs several foci, with elided subtrees drawn as triangles [p.350]
- [14.4 Superimpose](../ch14-embed-focus-context/s14-04-superimpose.md) · ~243 words. **Use when** a movable lens should show detail in a local layer over an unchanged background [p.351]
- [Hyperbolic Geometry](../idioms/hyperbolic-geometry.md) · ~704 words. **Use when** a huge tree or network needs one focus magnified at the centre and the rest shrunk at the periphery [pp.354-356]
- [Stretch and Squish Navigation](../idioms/stretch-and-squish-navigation.md) · ~742 words. **Use when** several rectangular regions of a large tree should be stretched while everything else squishes but stays in the viewport [pp.356-358]
- [Fisheye Lens](../idioms/fisheye-lens.md) · ~854 words. **Use when** a draggable local lens should magnify labels or nodes under it in any layout, a scatterplot or a node–link graph [pp.353-354] [pp.360-361]
- [14.5 Distort](../ch14-embed-focus-context/s14-05-distort.md) · ~1,227 words. **Use when** weighing distortion's design choices, or the remaining idioms: 3D perspective for trees (Cone Trees) and nonlinear magnification fields [pp.352-359]

## Disambiguation

- **Eyes Beat Memory vs Juxtapose and Coordinate Views.** 6.5 is the argument for side-by-side comparison over remembering earlier frames; 12.3 is how to build and link those views [pp.157-158] [pp.292-304].
- **Why Facet? vs Change View over Time.** 12.2 chooses among juxtaposition, change over time and layering; 11.3 designs the change once it is chosen [p.269] [pp.290-292].
- **Share Data: All, Subset, None vs Partition into Views.** Both produce small multiples; 12.3.2 decides how the views share data, 12.4 how to split the data and align the pieces [p.298] [p.304].
- **Juxtapose and Coordinate Views vs Superimpose Layers vs Superimposed Line Charts.** Juxtaposed views cost screen space, with up to a few dozen viable with care; layers cost none but two are feasible, three with care [pp.291-292]. Layering many is feasible only when each layer holds very little, such as one line, so superimposed line charts stay usable to nearly a dozen [pp.314-315], though juxtaposed small multiples did better for tasks spanning the whole series [p.317].
- **Elide vs DOITrees Revisited vs Superimpose vs Distort.** Elision omits and aggregates items by degree of interest, often over a hierarchy, with DOITrees as its worked tree; superimposing puts a local lens layer over the context; distortion compresses context geometrically [pp.349-352].
- **Hyperbolic Geometry vs Stretch and Squish Navigation vs Fisheye Lens.** Hyperbolic geometry has one global radial focus and fits structures that grow exponentially; stretch and squish has several global rectangular foci; the fisheye has one local radial focus, and on a graph may be harder to use than a magnifying lens [pp.353-358] [p.361]. Distortion suits topology tasks on node–link or containment layouts but impairs distance and length judgements [p.359].
- **Navigate: Changing Viewpoint vs Distort.** 11.5 changes the camera over the whole view; 14.5 enlarges a focus in place and compresses its surroundings [p.280] [pp.352-353].
- **Overview First, Zoom and Filter, Details on Demand vs Share Data: All, Subset, None.** 6.7 is the overall strategy; 12.3.2 is the overview–detail view pairing that implements it [pp.160-162] [pp.294-298].
- **Select Elements vs Share Encoding: Same/Different.** 11.4 designs the selection and its highlight within one view; 12.3.1 carries that highlight into the other views as linked highlighting [pp.274-279] [p.293].
- **Filter vs Aggregate vs SolarPlot vs Cluster–Calendar Time-Series Vis.** Filters remove items, which users may forget; aggregates replace groups with a derived summary; SolarPlot lets users change one histogram's bin count, while the cluster–calendar system aggregates hierarchically [pp.324-325] [pp.335-336].
- **Exploratory Data Visualizer (EDV) vs Improvise.** EDV is a few multiform views of a table linked by highlighting; Improvise coordinates many views of geographic and multidimensional data [pp.293-294] [pp.302-303].

## Related

- [11.6 Navigate: Reducing Attributes](../ch11-manipulate-view/s11-06-navigate-reducing-attributes.md): slicing, cutting or projecting dimensions interactively [pp.283-286]
- [14 Embed: Focus+Context](../ch14-embed-focus-context/node.md): why embed, magic lenses and the cost of distortion [pp.347-348]
- [Animated Transitions](../idioms/animated-transitions.md): tracking items across a change of state in one view [pp.273-274]
- [Highlighting](../idioms/highlighting.md): how a selected item is shown in linked views [pp.276-278]
- [15 Analysis Case Studies](../ch15-analysis-case-studies/node.md): whole systems to model a dashboard on; 15.5 Hierarchical Clustering Explorer is the most dashboard-like [pp.365-366] [pp.376-380]
- [3.4.2 Produce](../ch03-why-task-abstraction/s03-04-actions/s03-04-02-produce.md#s03.04.02.03): deriving new data, the fifth way to handle complexity [p.269] [p.290]
