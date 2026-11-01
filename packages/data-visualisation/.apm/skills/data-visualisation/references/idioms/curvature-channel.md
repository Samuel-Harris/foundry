---
id: "idiom:curvature-channel"
kind: idiom-card
title: "Curvature Channel"
pdf_pages: [261, 263]
printed_pages: [236, 238]
toc: []
fidelity: mixed
boxed: false
figures: []
---

# Curvature Channel

## Idiom box

No idiom box in the book.

- **What: Data.** Ordered attributes, as a magnitude channel [pp.261-263].
- **Why: Tasks.** Distinguishing a very small number of levels [p.263].
- **How: Encode.** Curvature of line marks [p.263].
- **Scale.** Probably around two or three distinguishable bins [p.263].

## What it is

<!-- verbatim p.263 -->
> The curvature channel is not very accurate, and it can only be used with line marks.
<!-- /verbatim -->

Point marks have no length and area marks have fully constrained shape, so neither can carry curvature. It sits with volume at the bottom of the magnitude channel ranking [pp.261-263].

## Use when / avoid when

- **Use** only with line marks, and only for about two or three levels [p.263].
- **Avoid** for accurate magnitude judgements: it is in the bottom equivalence class with volume [p.263].
- **Avoid** on point and area marks: it cannot be applied [p.263].

## Figures

## Alternatives and disambiguation

- **Angle Channel** also works on line marks and ranks above area, while curvature is at the bottom of the ranking [pp.262-263].
- **Size Channels**: length is extremely accurate; volume shares curvature's low ranking [p.261].

## Related

- [10.4 Other Channels](../ch10-map-color-other-channels/s10-04-other-channels.md#s10.04.03): the full subsection [p.263]
- [Angle Channel](angle-channel.md): a more accurate magnitude channel that also works with line marks [p.262]

## Implementation hints [NOT FROM BOOK]

### matplotlib

```python
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
fig, ax = plt.subplots()
for i, rad in enumerate([0.0, 0.3, 0.6]):  # two or three levels only
    ax.add_patch(FancyArrowPatch((i, 0), (i + 0.8, 1), connectionstyle=f"arc3,rad={rad}", arrowstyle="-"))
ax.set_xlim(-0.2, 3)
ax.set_ylim(-0.2, 1.2)
```

### D3

```js
import * as d3 from "d3";
const bend = d3.scaleOrdinal(["low", "mid", "high"], [0, 20, 40]);
const arc = (x0, y0, x1, y1, level) =>
  `M${x0},${y0} Q${(x0 + x1) / 2 + bend(level)},${(y0 + y1) / 2} ${x1},${y1}`;
console.log(arc(0, 0, 0, 100, "mid"));
```
