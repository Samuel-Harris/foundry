---
id: "idiom:texture-and-stippling"
kind: idiom-card
title: "Texture and Stippling"
pdf_pages: [251, 266]
printed_pages: [226, 241]
toc: []
fidelity: mixed
boxed: false
figures: []
---

# Texture and Stippling

## Idiom box

No idiom box in the book.

- **What: Data.** Categorical or ordered attributes [p.265].
- **Why: Tasks.** Distinguishing categories, or showing ordered levels, with patterns [p.265].
- **How: Encode.** Very small-scale patterns combining three channels: element orientation (angle), element scale (size) and contrast (luminance, related to element density). Stippling fills regions with short strokes [pp.264-265].
- **Scale.** At least one or two dozen categorical bins; three or four per subchannel, or about a dozen combined, for ordered data [p.265].

## What it is

Texture refers to very small-scale patterns, a complex perceptual phenomenon simplified as orientation, scale and contrast. Texture and stippling use combinations of multiple channels [pp.261-265].

<!-- verbatim p.265 -->
> The term stippling means to fill in regions of drawing with short strokes. It is a special case of texture.
<!-- /verbatim -->

Hatching and cross-hatching are synonyms for stippling in two-dimensional areas [p.265].

## Use when / avoid when

- **Use** for categorical attributes by combining all three dimensions; with sufficient care, at least one or two dozen bins are distinguishable [p.265].
- **Use** for ordered attributes, either one attribute per dimension (no more than three or four bins each) or all three dimensions for one attribute (around a dozen bins with careful design) [p.265].
- **Use** stippling on lines: dotted and dashed lines are a familiar, regular use [p.265].
- **Note** that area stippling, once heavily used to approximate gray with black ink, is less popular now that colour and grayscale printing are cheap [p.265].

## Figures

## Alternatives and disambiguation

- **Shape Channel**: on line marks, shape also produces dotted and dashed stipple patterns; on points it gives dozens of bins when large [p.263].
- **Categorical Colormaps**: six to twelve bins in small separated regions, versus texture's one or two dozen [pp.251-265].
- **Size Channels** and **Angle Channel** are the single channels that texture's scale and orientation map to [pp.264-265].

## Related

- [10.4 Other Channels](../ch10-map-color-other-channels/s10-04-other-channels.md#s10.04.06): the full subsection [p.264]
- [10.5 Further Reading](../ch10-map-color-other-channels/s10-05-further-reading.md): Ware's breakdown of texture into subchannels [p.266]
- [Shape Channel](shape-channel.md): stipple patterns on line marks [p.263]

## Implementation hints [NOT FROM BOOK]

### matplotlib

```python
import matplotlib.pyplot as plt
cats = ["A", "B", "C", "D"]
hatches = ["//", "\\\\", "xx", ".."]
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 3))
ax1.bar(cats, [4, 3, 5, 2], color="white", edgecolor="black", hatch=hatches)
for i, ls in enumerate(["-", "--", ":", "-."]):
    ax2.plot([0, 1], [i, i + 0.5], linestyle=ls, color="black")
```

### D3

```js
function addHatch(defs, id, angle, gap) {
  const p = defs.append("pattern").attr("id", id).attr("patternUnits", "userSpaceOnUse")
    .attr("width", gap).attr("height", gap).attr("patternTransform", `rotate(${angle})`);
  p.append("line").attr("y2", gap).attr("stroke", "black");
}
export { addHatch }; // then .attr("fill", "url(#id)"); dashed lines: .attr("stroke-dasharray", "4 2")
```
