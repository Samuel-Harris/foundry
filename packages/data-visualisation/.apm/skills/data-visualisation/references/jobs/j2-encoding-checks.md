---
id: j2b
kind: job-node
title: "J2 Encoding Checks"
pdf_pages: [119, 313]
printed_pages: [94, 288]
toc: []
fidelity: summary
---

# J2 Encoding Checks

The book's encoding rules that a plotting call has to get right once the idiom's card is open: channel choice by attribute type, aligned baselines, region ordering, aspect ratio and colormap construction [pp.124-128] [pp.137-139] [pp.250-260]. Pick the child whose use-when names the setting you are about to write; each is independent of the others. To find the idiom's card, go back to [J2 Write Plotting Code](j2-write-plotting-code.md) [p.171].

## Children

- [7.5.1 List Alignment: One Key](../ch07-arrange-tables/s07-05-separate-order-align-categorical/s07-05-01-list-alignment-one-key.md) · ~1,470 words. **Use when** deciding in code how to sort the bars or regions, or how to set a line chart's width-to-height ratio (banking to 45°) [pp.174-182]
- [12.4.2 List Alignments](../ch12-facet-into-multiple-views/s12-04-partition-into-views/s12-04-02-list-alignments.md) · ~335 words. **Use when** a second key must be drawn either as grouped bars side by side or as one small bar chart per group [pp.306-307]
- [5.4 Using Marks and Channels](../ch05-marks-channels/s05-04-using-marks-channels.md) · ~1,117 words. **Use when** mapping each data column to an encoding argument (x, y, colour, size, marker) and you must check that ordered columns get magnitude channels and categorical columns identity channels [pp.124-128]
- [5.6 Relative versus Absolute Judgements](../ch05-marks-channels/s05-06-relative-absolute-judgements.md) · ~607 words. **Use when** setting axes and baselines: bars aligned or framed against a common scale are judged far more precisely than unaligned ones, and surrounding colour shifts perceived colour [pp.137-139]
- [5.5 Channel Effectiveness](../ch05-marks-channels/s05-05-channel-effectiveness/node.md) · ~495 words. **Use when** a column has many levels for its channel (line widths, marker shapes) or two columns share one mark (size plus hue) [pp.128-137]
- [Shape Channel](../idioms/shape-channel.md) · ~514 words. **Use when** a categorical column goes on marker shape for point marks, and the bin limit depends on mark size [p.263]
- [Colorblind-Safe Colormaps](../idioms/colorblind-safe-colormaps.md) · ~407 words. **Use when** any palette must remain distinguishable for viewers with red–green colour deficiency [p.260]
- [6.9 Get It Right in Black and White](../ch06-rules-thumb/s06-09-get-right-black-white.md) · ~175 words. **Use when** checking that the code's most important marks stay distinguishable by luminance alone [p.165]
- [10.2.3 Luminance, Saturation, and Hue](../ch10-map-color-other-channels/s10-02-color-theory/s10-02-03-luminance-saturation-hue.md) · ~647 words. **Use when** setting how many hue, saturation or luminance steps a palette may use, or the contrast of text over coloured areas [pp.248-249]
- [10.2.2 Color Spaces](../ch10-map-color-other-channels/s10-02-color-theory/s10-02-02-color-spaces.md) · ~717 words. **Use when** a ramp is built by interpolating between two colours, where RGB interpolation misleads and L\*a\*b\* suits it [pp.245-248]

## Disambiguation

- **Using Marks and Channels vs Channel Effectiveness vs Relative versus Absolute Judgements.** 5.4 picks the channel; 5.5 checks its limits; 5.6 sets up the frame or baseline that makes it readable [pp.124-139].
- **List Alignment: One Key vs List Alignments.** 7.5.1 orders and shapes one chart along one key; 12.4.2 decides how a second key splits it into groups or separate charts [pp.174-182] [pp.306-307].
- **Shape Channel vs Channel Effectiveness.** The card gives shape's bin limits by mark size; 5.5 covers distinguishable levels and interference for every channel [pp.128-137] [p.263].
- **Colorblind-Safe Colormaps vs Get It Right in Black and White vs Luminance, Saturation, and Hue.** The colorblind card avoids hue-only and red–green encodings; 6.9 checks that the most important attribute survives black and white; 10.2.3 gives the levels each colour channel supports [p.165] [pp.248-249] [p.260].
- **Luminance, Saturation, and Hue vs Color Spaces.** 10.2.3 counts the steps a palette may use; 10.2.2 says how to interpolate between them [pp.245-249].

## Related

- [10.3 Colormaps](../ch10-map-color-other-channels/s10-03-colormaps/node.md): the colormap cards these checks apply to [pp.250-260]
- [6.3 No Unjustified 3D](../ch06-rules-thumb/s06-03-no-unjustified-3d/node.md): why a library's 3D chart option should not be used for abstract data [pp.142-143]
- [12.5 Superimpose Layers](../ch12-facet-into-multiple-views/s12-05-superimpose-layers/node.md): how many layers or lines one frame can carry [pp.313-315]
