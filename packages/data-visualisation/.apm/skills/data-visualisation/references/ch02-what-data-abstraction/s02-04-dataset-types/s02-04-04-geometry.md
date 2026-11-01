---
id: s02.04.04
kind: subsection-leaf
title: "Geometry"
pdf_pages: [54, 55]
printed_pages: [29, 30]
toc: [s02.04.04]
fidelity: mixed
---

# 2.4.4 Geometry

## Definition

<!-- verbatim p.54 -->
> The geometry dataset type specifies information about the shape of items with explicit spatial positions. The items could be points, or one-dimensional lines or curves, or 2D surfaces or regions, or 3D volumes.
<!-- /verbatim -->

## Properties

- **Spatial and shape-oriented.** Geometry datasets are intrinsically spatial and, like spatial fields, typically occur with tasks that require shape understanding [p.54].
- **Hierarchy.** Spatial data often has hierarchical structure at multiple scales, either provided with the dataset or derived from the original data [pp.54-55].
- **No attributes needed.** Unlike the other three basic dataset types, geometry datasets do not necessarily have attributes, while many vis design issues concern how to encode attributes [p.55].

## When geometry is a vis problem

<!-- verbatim p.55 -->
> Purely geometric data is interesting in a vis context only when it is derived or transformed in a way that requires consideration of design choices.
<!-- /verbatim -->

- **Classic examples.** Contours derived from a spatial field, and shapes generated at a level of detail suited to the task from raw geographic data, such as the boundaries of a forest, city or country or the curve of a road [p.55].
- **Not computer graphics.** Creating images from a geometric description of a scene belongs to computer graphics; vis draws on its algorithms but has different concerns, and simply showing a geometric dataset is not an interesting vis design problem [p.55].
- **Two roles.** Geometric data is sometimes shown alone, particularly when shape understanding is the primary task; otherwise it is the backdrop against which other information is overlaid [p.55].

## Figures

## Related

- [8.4 Scalar Fields: One Value](../../ch08-arrange-spatial-data/s08-04-scalar-fields-one-value/node.md): generating contours from scalar fields [p.55]
- [3.4.2.3 Derive](../../ch03-why-task-abstraction/s03-04-actions/s03-04-02-produce.md#s03.04.02.03): deriving data, the condition under which geometry becomes a design problem [p.55]
- [8.3 Geometry](../../ch08-arrange-spatial-data/s08-03-geometry.md): visual encoding of the geometry dataset type [p.55]
- [2.4.3 Fields](s02-04-03-fields.md): spatial fields, the source of derived contours [p.55]
