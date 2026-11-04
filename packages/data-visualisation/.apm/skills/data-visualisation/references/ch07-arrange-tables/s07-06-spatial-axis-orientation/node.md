---
id: s07.06
kind: section-node
title: "Spatial Axis Orientation"
pdf_pages: [187, 196]
printed_pages: [162, 171]
toc: [s07.06]
fidelity: summary
---

# 7.6 Spatial Axis Orientation

How to orient the spatial axes: rectilinear, parallel or radial [p.187]. Rectilinear layouts underlie most common statistical charts; parallel layouts show many quantitative attributes at once; radial layouts add the less accurate, cyclic angle channel; they may show periodic patterns better, and they imply an asymmetry of importance between the two attributes [pp.187-192]. The section also compares the part-to-whole idioms: pie charts, polar area charts and normalized stacked bar charts [pp.193-195].

## Children

- [7.6.1 Rectilinear Layouts](s07-06-01-rectilinear-layouts.md) · ~125 words. **Use when** you need the definition of the default layout of two perpendicular position axes that every chart in 7.4 and 7.5 uses [p.187]
- [7.6.2 Parallel Layouts](s07-06-02-parallel-layouts.md) · ~692 words. **Use when** a table has more quantitative attributes than perpendicular axes can show, and you need the full narrative on parallel coordinates: reading correlation, axis order, scalability, training and linked views [pp.187-190]
- [7.6.3 Radial Layouts](s07-06-03-radial-layouts.md) · ~1,097 words. **Use when** deciding between radial and rectilinear layouts, for periodic data or a part-to-whole chart; covers polar coordinates, why pie charts are less accurate than bars, and the empirical studies [pp.191-196]
- [Parallel Coordinates](../../idioms/parallel-coordinates.md) · ~935 words. **Use when** a table has many value attributes (dozens) and hundreds of items, and the task is to find trends, outliers, extremes or correlation [p.191]
- [Radial Bar Charts](../../idioms/radial-bar-charts.md) · ~635 words. **Use when** a table has one quantitative and one categorical attribute and a radial layout is wanted, with bar length still encoding the value [p.193]
- [Pie Charts](../../idioms/pie-charts.md) · ~728 words. **Use when** one quantitative attribute over up to a dozen categories must show a part–whole relationship with wedge angle and area, accepting lower accuracy than bars [pp.193-195]
- [Polar Area Charts](../../idioms/polar-area-charts.md) · ~536 words. **Use when** one quantitative attribute over up to a dozen categories must show a part–whole relationship in a radial layout with wedge length rather than angle [p.195]
- [Normalized Stacked Bar Charts](../../idioms/normalized-stacked-bar-charts.md) · ~677 words. **Use when** a table has two categorical keys and the part–whole proportions within each of several dozen categories matter more than absolute counts, up to a dozen stacked categories [p.195]

## Disambiguation

- **Pie Charts vs Polar Area Charts vs Normalized Stacked Bar Charts.** All three carry the part–whole task and about a dozen categories. A pie uses angle on area marks, the least accurate; a polar area chart varies wedge length like a bar; a normalized stacked bar uses length in a rectilinear layout, which is more accurate, needs less area, and shows one whole per bar for several dozen bars where pies would need a list or matrix of pies [pp.193-195].
- **Radial Bar Charts vs Polar Area Charts.** Both encode one quantitative attribute by length in a radial layout. Radial bar charts use line marks and are a bar chart re-oriented; polar area charts use wedge area marks and their box names the part–whole task [pp.192-195].
- **Rectilinear Layouts vs Radial Layouts.** Rectilinear layouts better show linear versus nonlinear trends, and in one study of memorising positions they were faster and tended to be more accurate; radial layouts may better show cyclic patterns, and that study suggests they can be justified when one attribute matters more than the other, which then goes in the sectors [pp.191-196].
- **Parallel Layouts vs Parallel Coordinates.** 7.6.2 holds the narrative, figures and multiple-view advice; the card holds the idiom box, use and avoid conditions, and code [pp.187-191].
- **Radial Layouts vs Radial Bar Charts vs Pie Charts vs Polar Area Charts vs Normalized Stacked Bar Charts.** 7.6.3 compares these idioms in one place with the evidence; each card holds one idiom's box and code [pp.191-196].

## Related

- [7.5.1 List Alignment: One Key](../s07-05-separate-order-align-categorical/s07-05-01-list-alignment-one-key.md): bar charts and stacked bar charts, the rectilinear counterparts of the radial and normalized idioms here [p.194]
- [Scatterplot Matrix (SPLOM)](../../idioms/scatterplot-matrix-splom.md): the book's preferred idiom for finding correlation across many attributes [p.188]
- [5.5 Channel Effectiveness](../../ch05-marks-channels/s05-05-channel-effectiveness/node.md): the channel accuracy rankings behind the pie-versus-bar argument [p.193]
- [5.5.3 Separability](../../ch05-marks-channels/s05-05-channel-effectiveness/s05-05-03-separability.md): why nonspatial channels cannot replace extra spatial axes [p.187]
- [6.3 No Unjustified 3D](../../ch06-rules-thumb/s06-03-no-unjustified-3d/node.md): drawbacks of a third spatial axis for abstract data [p.187]
- [13.4.1 Item Aggregation](../../ch13-reduce-items-attributes/s13-04-aggregate/s13-04-01-item-aggregation.md): hierarchical parallel coordinates for larger datasets [p.189]
- [12.3 Juxtapose and Coordinate Views](../../ch12-facet-into-multiple-views/s12-03-juxtapose-coordinate-views/node.md): linked multiple views that pair parallel coordinates with scatterplots [p.190]
- [12.4 Partition into Views](../../ch12-facet-into-multiple-views/s12-04-partition-into-views/node.md): further multiple-view design choices [p.190]
