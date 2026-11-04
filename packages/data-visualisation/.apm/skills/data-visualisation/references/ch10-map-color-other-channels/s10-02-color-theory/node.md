---
id: s10.02
kind: section-node
title: "Color Theory"
pdf_pages: [244, 250]
printed_pages: [219, 225]
toc: [s10.02]
fidelity: summary
---

# 10.2 Color Theory

The aspects of colour that matter most for vis: how the eye splits colour into a high-resolution luminance channel and two lower-resolution chromatic channels, which colour spaces match perception, how the book's three colour channels (luminance, saturation, hue) behave when encoding data, and transparency as a fourth channel [pp.244-250]. Use it to decide which colour channel can carry an attribute and how many levels it will support; to build a colormap for an attribute, go to 10.3 [pp.248-250].

## Children

- [10.2.1 Color Vision](s10-02-01-color-vision.md) · ~267 words. **Use when** you need the physiological reason edges and fine detail need luminance contrast, or the facts on red–green colour deficiency (about 8% of men) and its rarer blue–yellow form [pp.244-245]
- [10.2.2 Color Spaces](s10-02-02-color-spaces.md) · ~717 words. **Use when** choosing a space to compute or interpolate colours in: why RGB is integral and HSL lightness is pseudoperceptual, why perceived luminance depends on wavelength, and why L\*a\*b\* suits interpolation and colour differences [pp.245-248]
- [10.2.3 Luminance, Saturation, and Hue](s10-02-03-luminance-saturation-hue.md) · ~647 words. **Use when** deciding which colour channel encodes an attribute, or critiquing a chart's colour use: magnitude versus identity, bin limits (luminance fewer than five, saturation about three, hue six or seven in small separated regions), 10:1 and 3:1 text contrast ratios, saturation by region size [pp.248-249]
- [10.2.4 Transparency](s10-02-04-transparency.md) · ~168 words. **Use when** encoding with opacity or using it to separate a foreground layer, and you need to know which colour channels it may combine with and how many steps it supports [p.250]

## Disambiguation

- **Color Vision vs Luminance, Saturation, and Hue.** 10.2.1 explains why luminance carries edges and how colour deficiency arises; 10.2.3 turns that into encoding rules such as contrast ratios and bin counts [pp.245-248].
- **Color Spaces vs Luminance, Saturation, and Hue.** 10.2.2 is about computational models (RGB, HSL, L\*a\*b\*) and where the book's terms come from; 10.2.3 is about the perceptual channels as used in encoding [pp.245-249].
- **Luminance, Saturation, and Hue vs Transparency.** Opacity is a fourth channel that must not be combined with luminance or saturation coding, and with hue only for about two steps [p.250].

## Related

- [10.3 Colormaps](../s10-03-colormaps/node.md): building colour mappings for categorical, ordered and bivariate attributes from these channels [p.250]
- [5.5.1 Accuracy](../../ch05-marks-channels/s05-05-channel-effectiveness/s05-05-01-accuracy.md): the power-law curve behind compressed luminance perception [p.247]
- [12.5 Superimpose Layers](../../ch12-facet-into-multiple-views/s12-05-superimpose-layers/node.md): layering, the main use of transparency [p.250]
- [10.3.4 Colorblind-Safe Colormap Design](../s10-03-colormaps/s10-03-04-colorblind-safe-colormap-design.md): designing for the red–green colour deficiency that opponent channels explain [p.245]
