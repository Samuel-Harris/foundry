---
id: ch08
kind: chapter-node
title: "Arrange Spatial Data"
pdf_pages: [203, 223]
printed_pages: [178, 198]
toc: [ch08]
fidelity: summary
---

# 8 Arrange Spatial Data

How to arrange datasets with spatial semantics. The usual choice is to use the given spatial information as the layout, so express, separate, order and align do not apply [p.204]. The two data types are geometry, either geographic or derived, and spatial fields: scalar fields with one value per cell, and vector and tensor fields with several [p.204].

## Children

- [8.1 The Big Picture](s08-01-big-picture.md) · ~340 words. **Use when** you need the map of spatial idiom families, by data type (geometry, scalar, vector or tensor field), before descending [pp.203-204]
- [8.2 Why Use Given?](s08-02-why-use-given.md) · ~248 words. **Use when** deciding whether spatial position should show the given layout or encode other attributes, depending on whether spatial relationships are the central task [pp.204-205]
- [8.3 Geometry](s08-03-geometry.md) · ~485 words. **Use when** the data is geographic or other shape geometry: cartographic generalization, level of detail, adding nonspatial attributes to maps [pp.205-207]
- [8.4 Scalar Fields: One Value](s08-04-scalar-fields-one-value/node.md) · ~458 words. **Use when** a 2D or 3D field has one value per cell, such as CT, MRI or elevation, and you must choose slicing, isocontours or direct volume rendering [pp.207-214]
- [8.5 Vector Fields: Multiple Values](s08-05-vector-fields-multiple-values/node.md) · ~445 words. **Use when** a field has direction and magnitude per cell, such as a flow simulation, and you must choose glyphs, sparse or dense trajectories, or explicit features [pp.214-219]
- [8.6 Tensor Fields: Many Values](s08-06-tensor-fields-many-values.md) · ~606 words. **Use when** each cell holds a matrix, such as diffusion tensor MRI or stress, and shape and orientation must be shown [pp.219-222]
- [8.7 Further Reading](s08-07-further-reading.md) · ~356 words. **Use when** looking for sources on thematic cartography, spatial fields, isosurfaces, volume rendering, flow vis or tensor fields [pp.222-223]
- [Choropleth Map](../idioms/choropleth-map.md) · ~572 words. **Use when** a geographic dataset has one quantitative attribute per region, to be shown as colour over the given region shapes [p.206]
- [Ellipsoid Tensor Glyphs](../idioms/ellipsoid-tensor-glyphs.md) · ~718 words. **Use when** a 3D tensor field's shape and orientation per cell should be shown with ellipsoid glyphs, possibly filtering out isotropic cells [pp.219-221]

## Disambiguation

- **Why Use Given? vs The Big Picture.** 8.1 maps the idiom families; 8.2 argues whether the given layout should take spatial position at all [pp.204-205].
- **Geometry vs Scalar Fields: One Value.** Geometry conveys shape directly and need not carry attributes; a field has attribute values at each cell. Geometry is often derived from fields, as isolines and isosurfaces, which 8.4 covers [pp.204-207].
- **Geometry vs Choropleth Map.** 8.3 covers geographic data in general; the card is the one idiom for colouring given regions by a quantitative value [pp.205-206].
- **Scalar Fields: One Value vs Vector Fields: Multiple Values vs Tensor Fields: Many Values.** Choose by values per cell: one, a direction and magnitude, or a matrix. A vector field can be reduced to a scalar field to use 8.4's idioms, and tensor fields reuse 8.5's four families [pp.207-219].
- **Tensor Fields: Many Values vs Ellipsoid Tensor Glyphs.** 8.6 covers tensor fields and all their idiom families; the card is the ellipsoid glyph idiom with its box [pp.219-222].

## Related

- [2.4.3 Fields](../ch02-what-data-abstraction/s02-04-dataset-types/s02-04-03-fields.md): the spatial field dataset type [p.204]
- [2.4.4 Geometry](../ch02-what-data-abstraction/s02-04-dataset-types/s02-04-04-geometry.md): the geometry dataset type [p.204]
- [5.4.1 Expressiveness and Effectiveness](../ch05-marks-channels/s05-04-using-marks-channels.md#s05.04.01): why spatial position goes to the given layout [p.205]
- [7 Arrange Tables](../ch07-arrange-tables/node.md): the express, separate, order and align choices that do not apply here [p.204]
- [10.3.2 Ordered Colormaps](../ch10-map-color-other-channels/s10-03-colormaps/s10-03-02-ordered-colormaps.md): sequential colormaps for choropleths and contour plots [p.206]
- [11.5 Navigate: Changing Viewpoint](../ch11-manipulate-view/s11-05-navigate-changing-viewpoint.md): geometric navigation, the usual interaction for spatial fields [p.208]
- [13 Reduce Items and Attributes](../ch13-reduce-items-attributes/node.md): filtering, aggregation and level of detail in cartographic generalization [p.205]
- [13.4.2 Spatial Aggregation](../ch13-reduce-items-attributes/s13-04-aggregate/s13-04-02-spatial-aggregation.md): region boundaries and aggregation [p.206]
