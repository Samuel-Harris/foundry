---
id: "idiom:colorblind-safe-colormaps"
kind: idiom-card
title: "Colorblind-Safe Colormaps"
pdf_pages: [245, 260]
printed_pages: [220, 235]
toc: []
fidelity: mixed
boxed: false
figures: []
---

# Colorblind-Safe Colormaps

## Idiom box

No idiom box in the book.

- **What: Data.** Any attribute encoded with colour [p.260].
- **Why: Tasks.** Keeping colour-coded information distinguishable for viewers with red–green colour deficiency, 8% of males and 0.5% of females [p.260].
- **How: Encode.** Colormaps that vary luminance or saturation as well as hue, avoid red–green emphasis, and are checked in a simulator [p.260].

## What it is

<!-- verbatim p.260 -->
> On the theoretical side, the safest strategy is to avoid using only the hue channel to encode information: design categorical colormaps that vary in luminance or saturation, in addition to hue.
<!-- /verbatim -->

In common colour blindness, sensing along the red–green opponent axis is limited or absent [p.260]; the blue–yellow channel still works fully [p.245].

## Use when / avoid when

- **Use** whenever designing with colour: the problem is common [p.260].
- **Use** luminance differences between reds and greens where a domain's conventions require red and green [p.260].
- **Use** a colour blindness simulator to check the design, built into tools such as Adobe Illustrator and Photoshop or on sites such as <http://www.rehue.net>, <http://www.color-blindness.com> and <http://www.etre.com/tools/colourblindsimulator> [p.260].
- **Avoid** colormaps that emphasise red–green, especially divergent red–green ramps [p.260].
- **Avoid** assuming the problem is only red versus green: red and black, blue and purple, light green and white, and brown and green are also confused [p.260].

## Figures

## Alternatives and disambiguation

- This is a constraint on **Categorical Colormaps**, **Ordered Colormaps** and **Bivariate Colormaps**, not a separate colormap type [p.260].

## Related

- [10.3.4 Colorblind-Safe Colormap Design](../ch10-map-color-other-channels/s10-03-colormaps/s10-03-04-colorblind-safe-colormap-design.md): the full section [p.260]
- [10.2.1 Color Vision](../ch10-map-color-other-channels/s10-02-color-theory/s10-02-01-color-vision.md): opponent channels and the forms of colour deficiency [p.260]
- [7.5.2 Matrix Alignment: Two Keys](../ch07-arrange-tables/s07-05-separate-order-align-categorical/s07-05-02-matrix-alignment-two-keys.md): why bioinformatics uses red–green [p.260]

## Implementation hints [NOT FROM BOOK]

### matplotlib

```python
import matplotlib.pyplot as plt
import numpy as np
okabe_ito = ["#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7", "#000000"]
def rel_luminance(hex_):
    rgb = np.array([int(hex_[i:i + 2], 16) for i in (1, 3, 5)]) / 255
    lin = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    return lin @ [0.2126, 0.7152, 0.0722]
lum = [rel_luminance(c) for c in okabe_ito]
fig, ax = plt.subplots()
ax.bar(range(len(okabe_ito)), lum, color=okabe_ito)
ax.set_ylabel("relative luminance")
```

For diverging data prefer `cmap="PuOr"` or `"RdBu"` over `"RdYlGn"`; simulate with `colorspacious.cspace_convert(rgb, {"name": "sRGB1+CVD", "cvd_type": "deuteranomaly", "severity": 100}, "sRGB1")`.

### D3

`d3.schemeTableau10`, `d3.interpolateCividis`, `d3.interpolatePuOr`. Check each pair's `d3.lab(c).l` differs, since lightness survives red–green deficiency.
