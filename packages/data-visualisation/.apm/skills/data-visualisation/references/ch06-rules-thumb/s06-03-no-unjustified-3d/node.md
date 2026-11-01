---
id: s06.03
kind: section-node
title: "No Unjustified 3D"
pdf_pages: [142, 155]
printed_pages: [117, 130]
toc: [s06.03]
fidelity: summary
---

# 6.3 No Unjustified 3D

The first rule of thumb: encoding data with the third spatial dimension, depth, has costs that the two planar dimensions do not, so 3D must be justified [p.142]. The section covers the costs of each depth cue (occlusion, perspective distortion, shadows and lighting, familiar size, stereoscopic disparity), text legibility, the one case where 3D is easy to justify, and the empirical evidence [pp.142-143] [p.154].

In brief: 3D is easy to justify when the task is shape understanding of inherently three-dimensional structures, which frequently occurs with inherently spatial data; in all other contexts 3D needs careful justification, and usually a 2D spatial encoding, often reached through a different data abstraction with derived data, is the better answer [pp.142-143]. The rule's exact wording is quoted at the top of 6.3.1 [p.142].

## Children

- [6.3.1 The Power of the Plane](s06-03-01-power-plane.md) · ~455 words. **Use when** you need the verbatim statement of No Unjustified 3D to quote in a critique, or the question is which planar axis (vertical or horizontal) to give priority to, or why channel rankings for position apply only in the plane [pp.142-143]
- [6.3.2 The Disparity of Depth](s06-03-02-disparity-depth.md) · ~430 words. **Use when** you need the perceptual argument against depth position: the 0.67 power-law exponent for depth, line-of-sight ambiguity, "we see in 2.05D" [pp.143-145]
- [6.3.3 Occlusion Hides Information](s06-03-03-occlusion-hides-information.md) · ~423 words. **Use when** marks in a 3D view hide one another, as in a 3D node–link graph, and users must navigate to see behind them [pp.145-146]
- [6.3.4 Perspective Distortion Dangers](s06-03-04-perspective-distortion-dangers.md) · ~371 words. **Use when** critiquing a 3D bar chart or any perspective view where bar heights or sizes must be compared [pp.146-147]
- [6.3.5 Other Depth Cues](s06-03-05-other-depth-cues.md) · ~390 words. **Use when** a design adds shadows, shading, highlights, atmospheric perspective or stereo display, or relies on familiar size [pp.148-149]
- [6.3.6 Tilted Text Isn't Legibile](s06-03-06-tilted-text-legibile.md) · ~195 words. **Use when** labels are placed in 3D space and tilted off the image plane [p.149]
- [6.3.7 Benefits of 3D: Shape Perception](s06-03-07-benefits-3d-shape-perception.md) · ~370 words. **Use when** the data is inherently 3D spatial (fluid flow, medical tomography, molecules) and the task is understanding 3D shape, the case that justifies 3D [pp.149-150]
- [6.3.8 Justification and Alternatives](s06-03-08-justification-alternatives.md) · ~596 words. **Use when** looking for a 2D alternative to a 3D design for abstract data, or for what careful, justified 3D looks like, through two worked examples [pp.150-153]
- [6.3.9 Empirical Evidence](s06-03-09-empirical-evidence.md) · ~502 words. **Use when** you need study results on 2D versus 3D (cone trees, Data Mountain, 3D landscapes versus points) or are judging a study that claims a 3D benefit [pp.154-155]
- [Cluster–Calendar Time-Series Vis](../../idioms/cluster-calendar-time-series-vis.md) · ~974 words. **Use when** a year of daily time series (one curve per day) tempts a 3D extruded surface; shows the linked 2D clustered-curves and calendar alternative [pp.150-152]
- [Layer-Oriented Time-Series Vis](../../idioms/layer-oriented-time-series-vis.md) · ~599 words. **Use when** overlapping time-series traces (an eye diagram) need spreading apart, and you want an example of constrained, justified 3D [p.153]

## Disambiguation

- **The Power of the Plane vs The Disparity of Depth.** 6.3.1 compares the two planar axes with each other; 6.3.2 compares planar position with depth [pp.143-145].
- **Occlusion Hides Information vs Perspective Distortion Dangers vs Other Depth Cues.** Each covers different cues: occlusion and motion parallax in 6.3.3; foreshortening of position and size in 6.3.4; familiar size, shadows, shading, stereo and atmospheric perspective in 6.3.5. A 3D bar chart suffers from both occlusion and perspective distortion [pp.145-149].
- **Benefits of 3D: Shape Perception vs Justification and Alternatives vs Empirical Evidence.** 6.3.7 states when 3D is justified (shape understanding of 3D spatial data); 6.3.8 gives the history and two examples, one 2D replacement and one careful 3D design; 6.3.9 gives the study results and warns about confounded comparisons [pp.149-155].
- **Justification and Alternatives vs Cluster–Calendar Time-Series Vis vs Layer-Oriented Time-Series Vis.** 6.3.8 tells both examples in context; the cards hold each one as an idiom with use conditions and code. Cluster–calendar replaces 3D with linked 2D views; layer-oriented keeps 3D but constrains it [pp.150-153].

## Related

- [5.5.1 Accuracy](../../ch05-marks-channels/s05-05-channel-effectiveness/s05-05-01-accuracy.md): the channel rankings (Figure 5.6) and power-law exponents (Figure 5.7) that 6.3.1 and 6.3.2 qualify [p.143]
- [6.4 No Unjustified 2D](../s06-04-no-unjustified-2d.md): the same justification argument one dimension down [p.156]
- [6.6 Resolution over Immersion](../s06-06-resolution-over-immersion.md): immersive displays need even more justification than 3D for abstract data [p.160]
- [8.5 Vector Fields: Multiple Values](../../ch08-arrange-spatial-data/s08-05-vector-fields-multiple-values/node.md): streamlines, the example of justified 3D [p.150]
- [11.5 Navigate: Changing Viewpoint](../../ch11-manipulate-view/s11-05-navigate-changing-viewpoint.md): geometric navigation used to explore 3D shapes [p.150]
- [8.4.1 Isocontours](../../ch08-arrange-spatial-data/s08-04-scalar-fields-one-value/s08-04-01-isocontours.md): contour plots, a 2D alternative to 3D landscapes [p.154]
- [13.4.3 Attribute Aggregation: Dimensionality Reduction](../../ch13-reduce-items-attributes/s13-04-aggregate/s13-04-03-attribute-aggregation-dimensionality-reduction.md): the dimensionally reduced data shown as 3D landscapes in the study [p.155]
- [9 Arrange Networks and Trees](../../ch09-arrange-networks-trees/node.md): node–link layouts, whose 3D form is the occlusion example [p.145]
