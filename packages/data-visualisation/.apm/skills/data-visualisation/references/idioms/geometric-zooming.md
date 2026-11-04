---
id: "idiom:geometric-zooming"
kind: idiom-card
title: "Geometric Zooming"
pdf_pages: [268, 282]
printed_pages: [243, 257]
toc: []
fidelity: mixed
boxed: false
figures: []
---

# Geometric Zooming

## Idiom box

No idiom box in the book.

- **What: Data.** Any view with a fixed spatial layout [p.279].
- **Why: Tasks.** See fewer items in more detail, or more items as an overview; zooming in filters by spatial layout and zooming out can aggregate [pp.279-280].
- **How: Manipulate.** Navigate by moving the camera closer to or farther from the image plane, with object appearance fixed [pp.279-280].

## What it is

Zooming moves the camera closer to or farther from the plane: closer shows fewer items, drawn larger; farther shows more items, drawn smaller [p.279]. Geometric zooming matches the semantics of real-world motion [p.268]. It corresponds almost exactly to walking closer to objects or bringing them nearer the eyes; in 2D the metaphor is moving a piece of paper closer to or farther from the eyes while keeping it parallel to the face [p.280].

<!-- verbatim p.280 -->
> With geometric zooming, the fundamental appearance of objects is fixed, and moving the viewpoint simply changes the size at which they are drawn in image space.
<!-- /verbatim -->

Panning, the other camera translation, moves the camera parallel to the image plane; it is straightforward, and zooming is the more complex case [pp.279-280].

## Use when / avoid when

- **Use** as an intuitive form of navigation that matches real-world experience [p.280].
- **Use** to filter by spatial layout when zoomed in, or as aggregation that creates an overview when zoomed out [pp.279-280].
- **Limitation.** Because appearance is fixed, content such as several lines of text becomes illegible when its box is small; semantic zooming addresses this by changing the representation [p.280].
- **Beware** unconstrained pan and zoom, which can leave the camera pointed at nothing, even in 2D; limiting the zoom range is one of the simplest constrained approaches in 2D, and a reset-view button is far from a complete solution [p.282].

## Figures

## Alternatives and disambiguation

- **Semantic Zooming** changes the representation with available pixels; geometric zooming changes only drawn size [p.280].
- **Constrained Navigation** limits where a geometric zoom may go, such as a bounded zoom range [p.282].

## Related

- [11.5 Navigate: Changing Viewpoint](../ch11-manipulate-view/s11-05-navigate-changing-viewpoint.md#s11.05.01): the idiom in context [p.280]
- [Semantic Zooming](semantic-zooming.md): the nongeometric alternative [p.280]
- [Constrained Navigation](constrained-navigation.md): limiting zoom range and framing items [p.282]
- [13 Reduce Items and Attributes](../ch13-reduce-items-attributes/node.md): filtering and aggregation, which zooming amounts to [p.280]

## Implementation hints [NOT FROM BOOK]

### matplotlib

The toolbar already zooms and pans geometrically; this adds scroll-wheel zoom about the cursor.

```python
import numpy as np, matplotlib.pyplot as plt
rng = np.random.default_rng(1)
fig, ax = plt.subplots()
ax.scatter(*rng.normal(size=(2, 500)), s=8)

def on_scroll(event):
    if event.inaxes is not ax:
        return
    f = 0.8 if event.button == "up" else 1.25
    (x0, x1), (y0, y1) = ax.get_xlim(), ax.get_ylim()
    ax.set_xlim(event.xdata + (x0 - event.xdata) * f, event.xdata + (x1 - event.xdata) * f)
    ax.set_ylim(event.ydata + (y0 - event.ydata) * f, event.ydata + (y1 - event.ydata) * f)
    fig.canvas.draw_idle()

fig.canvas.mpl_connect("scroll_event", on_scroll)
```

### D3

```js
// geometric: scale the whole layer, so marks and strokes grow with k
const zoom = d3.zoom().scaleExtent([1, 20]).on("zoom", ({ transform }) => g.attr("transform", transform));
svg.call(zoom);
```

For a zoomable scatterplot whose dots should keep their radius, rescale the scales instead and move the points; clip the plot area so points outside it are hidden.

```js
// constant radius: rescale x and y with the transform, redraw the axes, reposition the dots
const zoomed = ({ transform }) => {
  const zx = transform.rescaleX(x);
  const zy = transform.rescaleY(y);
  gx.call(d3.axisBottom(zx));
  gy.call(d3.axisLeft(zy));
  dots.attr("cx", (d) => zx(d.x)).attr("cy", (d) => zy(d.y));
};
svg.call(d3.zoom().scaleExtent([1, 20]).on("zoom", zoomed));
```
