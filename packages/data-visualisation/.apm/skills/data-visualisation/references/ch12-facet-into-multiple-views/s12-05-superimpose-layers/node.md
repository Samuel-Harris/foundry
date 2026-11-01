---
id: s12.05
kind: section-node
title: "Superimpose Layers"
pdf_pages: [313, 320]
printed_pages: [288, 295]
toc: [s12.05]
fidelity: summary
---

# 12.5 Superimpose Layers

How to combine layers by stacking them in one composite view: simple drawings sharing one frame, with the same extent, blended as if transparent wherever they have no marks [p.313]. A visual layer is a set of objects spread over a region that can be told apart perceptually from objects in other layers; layering is a direct alternative to juxtaposing separate views [p.313]. The choices are how many layers, how to distinguish them, whether they are a small static set or constructed dynamically from user selection, and how to partition items into layers [pp.313-314].

## Children

- [12.5.1 Visually Distinguishable Layers](s12-05-01-visually-distinguishable-layers.md) · ~415 words. **Use when** deciding how many layers are feasible and how to keep them apart: nonoverlapping channel ranges, foreground versus background, and the limit of two or three layers when they hold many area marks [p.314]
- [12.5.2 Static Layers](s12-05-02-static-layers.md) · ~874 words. **Use when** all layers are shown at once and the viewer shifts attention among them: map layers separated by luminance contrast, many thin lines in one frame, hierarchy plus network, and the local versus global task evidence for superimposing versus juxtaposing [pp.314-319]
- [12.5.3 Dynamic Layers](s12-05-03-dynamic-layers.md) · ~289 words. **Use when** a foreground layer should be built on the fly from the user's selection or hover, such as a node's one-hop neighbourhood, so the number of possible layers can be huge [pp.319-320]
- [Cartographic Layering](../../idioms/cartographic-layering.md) · ~604 words. **Use when** geographic data needs area marks (water, parks, land) as an unsaturated background and line marks (roads) as a saturated foreground [pp.314-315]
- [Superimposed Line Charts](../../idioms/superimposed-line-charts.md) · ~697 words. **Use when** a table with an ordered key (time), a categorical key of up to about a dozen levels and one quantitative value should be compared in one frame, especially for tasks within a local visual span [pp.315-317]
- [Hierarchical Edge Bundles](../../idioms/hierarchical-edge-bundles.md) · ~658 words. **Use when** a compound graph (a network plus a hierarchy over its nodes) should show both structures at once, with bundled links layered over gray containment marks [pp.317-319]

## Disambiguation

- **Static Layers vs Dynamic Layers.** Static layers are a small fixed set shown simultaneously and divided by attribute types and semantics; dynamic layers are built interactively from the user's changing selection and can be numerous [p.314] [p.319].
- **Visually Distinguishable Layers vs Static Layers.** 12.5.1 gives the general rules for distinguishing layers and the layer-count limit; 12.5.2 shows them applied in three idioms [pp.314-319].
- **Cartographic Layering vs Superimposed Line Charts vs Hierarchical Edge Bundles.** Choose by data: geographic regions and roads; time series keyed by a categorical attribute; a compound graph [pp.315-319].
- **Static Layers vs Cartographic Layering vs Superimposed Line Charts vs Hierarchical Edge Bundles.** 12.5.2 narrates all three examples (layered maps included) plus the empirical study whose authors proposed superimposing for comparison within a local visual span and juxtaposing for dispersed tasks needing large visual spans, especially with more series; each card holds one idiom box (the line-chart card also the Scale field) and plotting hints [pp.314-319].

## Related

- [12.2 Why Facet?](../s12-02-why-facet.md): costs of layering against juxtaposing [p.291]
- [12.3 Juxtapose and Coordinate Views](../s12-03-juxtapose-coordinate-views/node.md): the side-by-side alternative to layers [p.313]
- [12.4 Partition into Views](../s12-04-partition-into-views/node.md): how static layers are partitioned, in a similar spirit to views [p.314]
- [6.9 Get It Right in Black and White](../../ch06-rules-thumb/s06-09-get-right-black-white.md): checking luminance contrast between layers [p.314]
- [9.5 Containment: Hierarchy Marks](../../ch09-arrange-networks-trees/s09-05-containment-hierarchy-marks.md): compound networks, the data for edge bundles [p.317]
- [11.4.2 Highlighting](../../ch11-manipulate-view/s11-04-select-elements/s11-04-02-highlighting.md): a single highlighted object as a minimal layer [p.314]
