---
id: s10.03
kind: section-node
title: "Colormaps"
pdf_pages: [250, 260]
printed_pages: [225, 235]
toc: [s10.03]
fidelity: summary
---

# 10.3 Colormaps

A colormap maps data values to colours. Its taxonomy mirrors the data types: categorical attributes take categorical colormaps; ordinal and quantitative attributes take ordered colormaps, sequential (minimum to maximum) or diverging (two hues around a neutral zero point); two attributes at once take bivariate colormaps [pp.250-251]. Ordered colormaps should use luminance and saturation, because hue has no implicit order; continuous colormaps suit quantitative and spatial-field data, segmented ones suit categorical data, and ordinal data can go either way depending on whether its discreteness or its order matters [p.250]. The Section 10.3 introduction is summarised at the top of 10.3.1 [p.250].

## Children

- [10.3.1 Categorical Colormaps](s10-03-01-categorical-colormaps.md) · ~1,066 words. **Use when** a categorical attribute is coloured and you need the full reasoning and worked examples: the six-to-twelve-colour limit for small separated regions, nameable colours, saturation by mark size, ColorBrewer, and what to do when there are more categories than colours (21 genome colours collapsing to 12; 27 workflow levels moved to shape and glyphs) [pp.250-256]
- [10.3.2 Ordered Colormaps](s10-03-02-ordered-colormaps.md) · ~880 words. **Use when** an ordinal or quantitative attribute is coloured and you need the reasoning: sequential versus diverging construction, how many hues for which level of structure, the rainbow's three problems, monotonic-luminance fixes and segmented rainbows [pp.254-259]
- [10.3.3 Bivariate Colormaps](s10-03-03-bivariate-colormaps.md) · ~296 words. **Use when** two attributes must share the colour channel; which combinations (binary, hierarchical, sequential, diverging, categorical) are safe, risky or poor [pp.259-260]
- [10.3.4 Colorblind-Safe Colormap Design](s10-03-04-colorblind-safe-colormap-design.md) · ~247 words. **Use when** checking any colormap for red–green colour deficiency: the confusable pairs, varying luminance or saturation as well as hue, and simulators [p.260]
- [Categorical Colormaps](../../idioms/categorical-colormaps.md) · ~891 words. **Use when** choosing or critiquing a palette for a categorical attribute or groupings and you want the decision rules (bin limits, saturation by mark size, remedies for too many categories) plus code [pp.250-256]
- [Ordered Colormaps](../../idioms/ordered-colormaps.md) · ~912 words. **Use when** choosing or critiquing a sequential or diverging colour ramp for ordinal or quantitative values, including whether a rainbow is acceptable, plus code [pp.250-259]
- [Bivariate Colormaps](../../idioms/bivariate-colormaps.md) · ~468 words. **Use when** deciding whether to encode a second attribute in colour, or building a binary-split or two-ramp colour grid, plus code [pp.259-260]
- [Colorblind-Safe Colormaps](../../idioms/colorblind-safe-colormaps.md) · ~407 words. **Use when** making a palette usable by viewers with red–green deficiency, or auditing one, with code [p.260]

## Disambiguation

- **Categorical Colormaps vs Ordered Colormaps.** Decided by attribute type: categorical data takes hue-based segmented maps; ordinal and quantitative data take luminance or saturation ramps. Ordinal data may use either, segmented to stress discreteness or continuous to stress order; a segmented rainbow is a fine categorical map for few categories. For each topic the 10.3.x leaf holds the book's reasoning and worked examples, and the same-named card holds compact decision rules, alternatives and code [pp.250-259].
- **Ordered Colormaps vs Bivariate Colormaps.** One ordered attribute versus two attributes in one colour; bivariate maps reuse sequential and diverging ramps [pp.259-260].
- **Categorical Colormaps vs Bivariate Colormaps.** A single categorical attribute with hierarchical structure can use the bivariate fixed-hue, varied-saturation scheme; two multi-level categorical attributes give poor results [p.260].
- **Colorblind-Safe Colormap Design vs Colorblind-Safe Colormaps vs Categorical Colormaps vs Ordered Colormaps vs Bivariate Colormaps.** Colour-deficiency safety is a check applied on top of any categorical, ordered or bivariate choice, not an alternative to them; the leaf gives the reasoning, the card the checklist and code [p.260].

## Related

- [10.2.3 Luminance, Saturation, and Hue](../s10-02-color-theory/s10-02-03-luminance-saturation-hue.md): the channel properties (ordering, bin counts) every colormap rule rests on [p.250]
- [5.4.1 Expressiveness and Effectiveness](../../ch05-marks-channels/s05-04-using-marks-channels.md#s05.04.01): the expressiveness principle behind matching colormap to data type [p.250]
- [2.4.3 Fields](../../ch02-what-data-abstraction/s02-04-dataset-types/s02-04-03-fields.md): continuous versus discrete semantics, behind continuous versus segmented colormaps [p.250]
- [2.5 Attribute Types](../../ch02-what-data-abstraction/s02-05-attribute-types.md): the categorical, ordered, sequential and diverging distinctions the colormap taxonomy mirrors [p.250]
- [15.8 Constellation](../../ch15-analysis-case-studies/s15-08-constellation.md): a few dozen link categories filtered and aggregated to eight colours [p.254]
- [13 Reduce Items and Attributes](../../ch13-reduce-items-attributes/node.md): aggregation and filtering to cut categories down to the number of distinguishable colours [p.254]
- [7.5.2 Matrix Alignment: Two Keys](../../ch07-arrange-tables/s07-05-separate-order-align-categorical/s07-05-02-matrix-alignment-two-keys.md): the historical and technical reasons for red–green use in bioinformatics [p.260]
- [10.4 Other Channels](../s10-04-other-channels.md): shape, size and texture when colour alone runs out of bins [p.254]
