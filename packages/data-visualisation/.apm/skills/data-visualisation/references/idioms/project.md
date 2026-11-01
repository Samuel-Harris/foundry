---
id: "idiom:project"
kind: idiom-card
title: "Project"
pdf_pages: [268, 286]
printed_pages: [243, 261]
toc: []
fidelity: mixed
boxed: false
figures: []
---

# Project

## Idiom box

No idiom box in the book.

- **What: Data.** Spatial data, 3D scenes, the Earth's surface for maps, or abstract data, where it is called dimensional filtering [p.286].
- **Why: Tasks.** Reduce the number of dimensions shown while keeping every item visible [p.286].
- **How: Manipulate.** Navigate to reduce attributes by a transformation that drops the chosen dimensions, fully or partly [pp.268-269] [p.286].

## What it is

<!-- verbatim p.286 -->
> With the project design choice, all items are shown, but without the information for specific dimensions chosen to exclude.
<!-- /verbatim -->

- An object's shadow on a wall or floor is a projection from 3D to 2D. There are many types; some keep partial information about the removed dimensions, others eliminate it completely [p.286].
- **Orthographic projection.** The excluded dimensions' values are simply dropped and nothing about them is retained; from 3D to 2D all depth is lost [p.286]. Dimensional filtering, common with abstract data, is essentially a synonym [p.286].
- **Multiple views.** Projections are often used with a view per combination of dimensions, as architectural blueprints show floor plan (XY), side view (YZ) and front view (XZ) [p.286].
- **Perspective projection**, as in our eyes and the graphics camera, also loses much depth but keeps some through foreshortening: distant objects are closer together on the image plane [p.286].
- **Map projections**, such as Mercator, go from curved to flat space; most design choices concern whether distorting angles or areas matters less for the intended abstract task [p.286].

## Use when / avoid when

- **Use** when every item should stay visible while dimensions are removed; slicing and cutting instead discard items [pp.283-286].
- **Choose a map projection** by whether distorted angles or distorted areas are less problematic for the task [p.286].
- A footnote cautions that cartographic projections go from a 2D curved surface embedded in 3D to a 2D flat space, so they do not cleanly fit the idea of projection as dimensionality reduction [p.286].

## Figures

## Alternatives and disambiguation

- **Slice** keeps only items at one value of the eliminated dimension; project keeps every item [pp.283-286].
- **Cut** removes the half of a volume nearest the camera; project removes dimensions, not items [pp.285-286].
- **Dimensional filtering** with abstract data is essentially orthographic projection [p.286].
- **HyperSlice** also gives one view per dimension pair, but each view is a slice rather than a projection [pp.284-286].

## Related

- [11.6 Navigate: Reducing Attributes](../ch11-manipulate-view/s11-06-navigate-reducing-attributes.md#s11.06.03): the idiom in context [p.286]
- [Slice](slice.md): the item-selecting alternative [p.286]
- [13.3.2 Attribute Filtering](../ch13-reduce-items-attributes/s13-03-filter/s13-03-02-attribute-filtering.md): filtering attributes, the abstract-data counterpart of orthographic projection [p.286]
- [6.3 No Unjustified 3D](../ch06-rules-thumb/s06-03-no-unjustified-3d/node.md): the costs of perspective projection's lost depth [p.286]

## Implementation hints [NOT FROM BOOK]

### matplotlib

Orthographic projections are column selection; three panels give the blueprint views.

```python
import numpy as np, matplotlib.pyplot as plt
rng = np.random.default_rng(4)
pts = rng.normal(size=(300, 3)) * [3, 1, 2]
fig, axes = plt.subplots(1, 3, figsize=(9, 3))
for ax, (i, j), name in zip(axes, [(0, 1), (1, 2), (0, 2)], ["plan XY", "side YZ", "front XZ"]):
    ax.scatter(pts[:, i], pts[:, j], s=4); ax.set_title(name); ax.set_aspect("equal")
```

Use `ax.set_proj_type("ortho")` or `"persp"` on a 3D axes to compare projections; for maps use Cartopy (`ccrs.Mercator()`, `ccrs.EqualEarth()`).

### D3

```js
// map projections: swap the projection to trade angle distortion for area distortion
const projection = d3.geoMercator().fitSize([w, h], land);   // conformal
// const projection = d3.geoEqualEarth().fitSize([w, h], land); // equal-area
svg.append("path").attr("d", d3.geoPath(projection)(land));
```
