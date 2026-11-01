---
id: s08.04
kind: section-node
title: "Scalar Fields: One Value"
pdf_pages: [207, 214]
printed_pages: [182, 189]
toc: [s08.04]
fidelity: summary
---

# 8.4 Scalar Fields: One Value

A scalar spatial field has one value per spatially defined cell, often from medical imaging such as CT or MRI scans [p.207]. The book gives three idiom families: slicing, which shows two dimensions at once as an image; isocontours, which derive lower-dimensional surface geometry; and direct volume rendering, which uses the whole 3D field to make an image. Geometric navigation is the usual interaction, and the idioms can be combined [pp.207-208].

## Children

- [8.4.1 Isocontours](s08-04-01-isocontours.md) · ~904 words. **Use when** you want to derive lines (2D field) or surfaces (3D field) at chosen levels of a scalar field, or need the chapter's scalar-field overview and the slicing idiom; covers contour plots, occlusion of nested isosurfaces and choosing the level [pp.207-211]
- [8.4.2 Direct Volume Rendering](s08-04-02-direct-volume-rendering.md) · ~549 words. **Use when** a 3D scalar field should be rendered whole, without deriving surfaces, and the problem is choosing the transfer function that maps value to colour and opacity [pp.211-214]
- [Topographic Terrain Map](../../idioms/topographic-terrain-map.md) · ~511 words. **Use when** a 2D field on a geographic base, such as elevation, should be shown as dozens of isoline levels for querying shape [pp.208-209]
- [Flexible Isosurfaces](../../idioms/flexible-isosurfaces.md) · ~682 words. **Use when** a 3D field's isosurfaces split, merge or appear as the level changes, and a simplified contour tree should guide which to show [pp.210-211]
- [Multidimensional Transfer Functions](../../idioms/multidimensional-transfer-functions.md) · ~733 words. **Use when** a 1D transfer function cannot isolate features in volume rendering, so a 2D value by gradient-magnitude histogram is used to pick materials and their boundaries [pp.212-213]

## Disambiguation

- **Isocontours vs Direct Volume Rendering.** Isocontours derive intermediate surface or line geometry at a level and draw it; direct volume rendering creates the image from the full field with no intermediate geometry, so the key choice moves from the isovalue to the transfer function [pp.207-212].
- **Isocontours vs Topographic Terrain Map vs Flexible Isosurfaces.** 8.4.1 holds the whole isocontour narrative; the terrain map card is the 2D isoline idiom on geographic data, where many levels coexist; the flexible isosurfaces card is the 3D idiom, where outer surfaces occlude inner ones and a contour tree selects among them [pp.208-211].
- **Direct Volume Rendering vs Multidimensional Transfer Functions.** 8.4.2 covers the idiom and the transfer-function problem; the card holds the Simian box and the joint-histogram encoding [pp.211-212].

## Related

- [11.6.1 Slice](../../ch11-manipulate-view/s11-06-navigate-reducing-attributes.md#s11.06.01): slicing among other attribute-reduction idioms [p.208]
- [11.5 Navigate: Changing Viewpoint](../../ch11-manipulate-view/s11-05-navigate-changing-viewpoint.md): geometric navigation, the usual interaction for these idioms [p.208]
- [8.5 Vector Fields: Multiple Values](../s08-05-vector-fields-multiple-values/node.md): a vector field reduced to a scalar field can use these idioms [p.215]
- [6.3 No Unjustified 3D](../../ch06-rules-thumb/s06-03-no-unjustified-3d/node.md): Figure 6.9(c), which the book cites as a contour plot [p.208]
- [2.4.3 Fields](../../ch02-what-data-abstraction/s02-04-dataset-types/s02-04-03-fields.md): the spatial field dataset type [p.207]
