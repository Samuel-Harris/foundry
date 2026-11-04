---
id: s12.03
kind: section-node
title: "Juxtapose and Coordinate Views"
pdf_pages: [292, 304]
printed_pages: [267, 279]
toc: [s12.03]
fidelity: summary
---

# 12.3 Juxtapose and Coordinate Views

How to link views shown side by side. There are four major choices: whether the views share the same visual encoding, whether highlighting is linked, whether they show the same data, a subset or a disjoint partition, and whether navigation is synchronised [p.292]. Two further choices do not involve coordination: when to show each view and how to arrange them [p.303]. Linked views, multiple views, coordinated views, coordinated multiple views and coupled views are synonyms [p.292].

## Children

- [12.3.1 Share Encoding: Same/Different](s12-03-01-share-encoding-same-different.md) · ~628 words. **Use when** deciding whether views use identical channels or differ (multiform), whether to link highlighting (brushing, cross-filtering) across views, or why a single view cannot carry all attributes [pp.292-294]
- [12.3.2 Share Data: All, Subset, None](s12-03-02-share-data-all-subset.md) · ~1,218 words. **Use when** deciding whether each view shows all items, one view shows a selected subset of another (overview–detail, detail on demand), or views show disjoint partitions (small multiples); covers how many views, window sizes and the small-multiple screen limit [pp.294-301]
- [12.3.3 Share Navigation: Synchronize](s12-03-03-share-navigation-synchronize.md) · ~112 words. **Use when** panning or zooming in one view should move the viewpoint in others, as with a bird's-eye overview driving a detail map [p.301]
- [12.3.4 Combinations](s12-03-04-combinations.md) · ~511 words. **Use when** classifying or designing a multiple-view system along both axes at once (same or different encoding by all, subset or no shared data), including which two combinations are useless [pp.301-303]
- [12.3.5 Juxtapose Views](s12-03-05-juxtapose-views.md) · ~228 words. **Use when** deciding whether views are permanently visible or pop up on demand, and whether to leave arrangement to the window system or align views automatically in a list or matrix [pp.303-304]
- [Exploratory Data Visualizer (EDV)](../../idioms/exploratory-data-visualizer-edv.md) · ~654 words. **Use when** a table needs multiform views (bar charts, scatterplots, histograms) with linked highlighting so a selection in one view shows its distribution in the others [pp.293-294]
- [Bird's-Eye Maps](../../idioms/birds-eye-maps.md) · ~703 words. **Use when** a geographic map needs a large detail view plus a small orienting overview with the same encoding, linked by navigation [pp.295-296]
- [Multiform Overview–Detail Microarrays](../../idioms/multiform-overview-detail-microarrays.md) · ~853 words. **Use when** time-series data with a categorical key needs an overview line chart whose selected time window drives a differently encoded detail view, plus a text list for lookup [pp.296-298]
- [Cerebral](../../idioms/cerebral.md) · ~894 words. **Use when** a network carries values per experimental condition and you need one small-multiple network view per condition, a main view of a derived difference, and linked highlighting and navigation [pp.299-301]
- [Improvise](../../idioms/improvise.md) · ~669 words. **Use when** a geographic and multidimensional table needs many coordinated views at once: multiform views with one shared colormap, small multiples, overview–detail maps and linked highlighting [pp.302-303]

## Disambiguation

- **Share Encoding: Same/Different vs Share Data: All, Subset, None vs Combinations.** 12.3.1 and 12.3.2 each cover one axis of coordination; 12.3.4 crosses the two and says which combinations are useful [p.292] [p.294] [p.301].
- **Share Data: All, Subset, None vs Share Navigation: Synchronize.** One popular overview–detail idiom adds navigation support, but 12.3.2 covers what subset each view shows and how many views to use, while 12.3.3 covers only synchronising viewpoint movement [pp.294-295] [p.301].
- **Share Navigation: Synchronize vs Bird's-Eye Maps.** The bird's-eye map is the book's worked case of linked navigation, with unidirectional and bidirectional linkage; 12.3.3 states the general choice [p.296] [p.301].
- **Juxtapose Views vs Combinations.** 12.3.5 covers showing and arranging views, which does not involve coordination; 12.3.4 covers coordination [p.301] [p.303].
- **Share Encoding: Same/Different vs Exploratory Data Visualizer (EDV) vs Improvise.** For linked highlighting (brushing), 12.3.1 gives the choice and its rationale; the cards are worked systems. EDV is a compact case of multiform views with linked highlighting; Improvise combines multiform, small-multiple and overview–detail views with a shared bivariate colormap and linked navigation [p.294] [pp.302-303].
- **Share Data: All, Subset, None vs Bird's-Eye Maps vs Multiform Overview–Detail Microarrays vs Cerebral.** 12.3.2 gives the three data-sharing choices, how many views to use and the small-multiple screen limit; the cards are its worked cases. Bird's-Eye Maps is overview–detail with the same encoding on geographic data; the microarray tool is multiform overview–detail, with a differently encoded detail view; Cerebral is small multiples of a network partitioned by condition [pp.294-299].
- **Share Data: All, Subset, None vs Juxtapose Views.** A detail-on-demand view may be a popup near the cursor or a fixed window: 12.3.2 covers what such a view shows, 12.3.5 the choice between permanently visible and temporarily popped-up views [p.296] [p.303].
- **Multiform Overview–Detail Microarrays vs Cerebral.** Both are bioinformatics microarray systems; the microarray tool links a time-series overview to a scatterplot detail view, while Cerebral partitions a network by condition into small multiples [pp.296-300].

## Related

- [12.4 Partition into Views](../s12-04-partition-into-views/node.md): how to divide the data between small-multiple views [p.298]
- [12.5.2 Static Layers](../s12-05-superimpose-layers/s12-05-02-static-layers.md): the superimposed line charts used in the microarray overview [p.297]
- [7.5 Separate, Order, and Align: Categorical Regions](../../ch07-arrange-tables/s07-05-separate-order-align-categorical/node.md): aligning small multiples into lists or matrices [p.298]
- [11.5 Navigate: Changing Viewpoint](../../ch11-manipulate-view/s11-05-navigate-changing-viewpoint.md): the viewpoint changes that overview–detail and linked navigation coordinate [p.294] [p.301]
- [11.4.2 Highlighting](../../ch11-manipulate-view/s11-04-select-elements/s11-04-02-highlighting.md): the selection highlighting that linked highlighting propagates across views [p.292]
- [6.5 Eyes Beat Memory](../../ch06-rules-thumb/s06-05-eyes-beat-memory.md): why small multiples beat animation for complex change [p.299]
- [10.3.3 Bivariate Colormaps](../../ch10-map-color-other-channels/s10-03-colormaps/s10-03-03-bivariate-colormaps.md): the colormap Improvise shares across views [p.302]
