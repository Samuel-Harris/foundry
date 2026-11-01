---
id: ch10
kind: chapter-node
title: "Map Color and Other Channels"
pdf_pages: [243, 266]
printed_pages: [218, 241]
toc: [ch10]
fidelity: summary
---

# 10 Map Color and Other Channels

How to map attributes to colour and to the other nonspatial channels. Colour is three channels: luminance and saturation are magnitude channels for ordered data, hue an identity channel for categories [pp.244-248]. The main colormap choice is categorical versus ordered, with ordered split into sequential and diverging, plus bivariate maps for two attributes [p.244]. The other channels are the magnitude channels of size, angle and curvature, the identity channels of shape and motion, and texture as a combination [pp.244-261]. For any of these, the routing question is the attribute type, the number of levels to distinguish and the mark size [pp.248-265].

## Children

- [10.1 The Big Picture](s10-01-big-picture.md) · ~275 words. **Use when** you want the one-page map of the chapter's design choices (Figure 10.1) to decide whether a question is about colour channels, colormap type or another nonspatial channel [pp.243-244]
- [10.2 Color Theory](s10-02-color-theory/node.md) · ~413 words. **Use when** deciding which colour channel (luminance, saturation, hue, transparency) can carry an attribute and how many levels it supports, choosing a colour space to interpolate in, or setting text contrast [pp.244-250]
- [10.3 Colormaps](s10-03-colormaps/node.md) · ~703 words. **Use when** mapping an attribute to colour: categorical versus sequential versus diverging versus bivariate by attribute type, how many colours, rainbow pitfalls and colour-deficiency safety [pp.250-260]
- [10.4 Other Channels](s10-04-other-channels.md) · ~1,403 words. **Use when** you need all the non-colour, nonspatial channels compared in one place (accuracy, bin counts, which marks they apply to, interactions), for example to pick a second channel beside colour [pp.261-265]
- [10.5 Further Reading](s10-05-further-reading.md) · ~221 words. **Use when** looking for primary sources on colour, ColorBrewer, the case against rainbows, bivariate colormaps, motion highlighting or texture [pp.265-266]
- [Size Channels](../idioms/size-channels.md) · ~513 words. **Use when** an ordered attribute is shown by length, area or volume: length is extremely accurate, area mid-ranking (exponent 0.7), volume at the bottom; size also limits what other channels can show [pp.261-262]
- [Angle Channel](../idioms/angle-channel.md) · ~497 words. **Use when** an ordered attribute, including a diverging or cyclic one such as direction, could be shown by the orientation of line marks or arrow glyphs; more accurate than area, less than length [p.262]
- [Curvature Channel](../idioms/curvature-channel.md) · ~317 words. **Use when** weighing curvature for line marks; only about two or three bins, bottom of the ranking [p.263]
- [Shape Channel](../idioms/shape-channel.md) · ~514 words. **Use when** a categorical attribute goes on point marks (or dash patterns on lines): dozens or more bins for large points, roughly a dozen at 10×10 pixels with careful design, never on area marks [p.263]
- [Motion Channels](../idioms/motion-channels.md) · ~518 words. **Use when** a binary distinction such as selected versus not selected must grab attention, typically transitory highlighting on mouseover or click [pp.263-264]
- [Texture and Stippling](../idioms/texture-and-stippling.md) · ~448 words. **Use when** areas or lines need patterns instead of or beside colour: one or two dozen categorical bins, or three or four per subchannel for ordered data [pp.264-265]

## Disambiguation

- **Color Theory vs Colormaps.** 10.2 gives each colour channel's properties (ordering, bin counts, contrast, transparency); 10.3 applies them to build a mapping for a given attribute type [pp.248-251].
- **Other Channels vs Size Channels vs Angle Channel vs Curvature Channel vs Shape Channel vs Motion Channels vs Texture and Stippling.** 10.4 compares all six in one narrative; each card holds one channel's use and avoid conditions, alternatives and code [pp.261-265].
- **Size Channels vs Angle Channel vs Curvature Channel.** All magnitude channels for ordered data, ranked length, then angle, then area, with curvature and volume together at the bottom; angle also supports diverging and cyclic tiltmaps, and curvature can only be used with line marks [pp.261-263].
- **Shape Channel vs Texture and Stippling vs Motion Channels.** Shape is the identity channel for point and line marks; texture combines orientation, scale and contrast into patterns, with stippling for lines; motion carries only a binary distinction and is for highlighting [pp.263-265].
- **Colormaps vs Shape Channel vs Texture and Stippling.** Colour is the next best channel for categories after position but gives only six to twelve bins in small separated regions; shape and texture are the alternatives when there are more categories [pp.251-265].

## Related

- [5.5.1 Accuracy](../ch05-marks-channels/s05-05-channel-effectiveness/s05-05-01-accuracy.md): the channel effectiveness ranking and power-law exponents this chapter relies on [p.247]
- [5.4.1 Expressiveness and Effectiveness](../ch05-marks-channels/s05-04-using-marks-channels.md#s05.04.01): the expressiveness principle that matches colormap to data type [p.250]
- [2.5 Attribute Types](../ch02-what-data-abstraction/s02-05-attribute-types.md): the categorical and ordered types the colormap taxonomy mirrors [p.250]
- [2.4.3 Fields](../ch02-what-data-abstraction/s02-04-dataset-types/s02-04-03-fields.md): continuous versus discrete semantics behind continuous versus segmented colormaps [p.250]
- [12.5 Superimpose Layers](../ch12-facet-into-multiple-views/s12-05-superimpose-layers/node.md): layering, where transparency is mostly used [p.250]
- [15.8 Constellation](../ch15-analysis-case-studies/s15-08-constellation.md): link categories narrowed to eight colours [p.254]
- [7.5.2 Matrix Alignment: Two Keys](../ch07-arrange-tables/s07-05-separate-order-align-categorical/s07-05-02-matrix-alignment-two-keys.md): red–green colour conventions in bioinformatics [p.260]
- [11.4.2 Highlighting](../ch11-manipulate-view/s11-04-select-elements/s11-04-02-highlighting.md): the highlighting that motion channels suit [p.264]
- [13 Reduce Items and Attributes](../ch13-reduce-items-attributes/node.md): aggregation and filtering to fit categories into the available colours [p.254]
