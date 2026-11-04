---
id: s06.03.01
kind: subsection-leaf
title: "The Power of the Plane"
pdf_pages: [142, 143]
printed_pages: [117, 118]
toc: [s06.03.01]
fidelity: mixed
---

# 6.3.1 The Power of the Plane

## The rule: No Unjustified 3D (Section 6.3 opening)

The section opens against the intuition that if two dimensions are good, three must be better because we live in a three-dimensional world; depth has important differences from the two planar dimensions that make encoding information with it difficult [p.142].

<!-- verbatim pp.142-143 -->
> In brief, 3D vis is easy to justify when the user's task involves shape understanding of inherently three-dimensional structures. In this case, which frequently occurs with inherently spatial data, the benefits of 3D absolutely outweigh the costs, and designers can use the many interaction idioms designed to mitigate those costs. In all other contexts, the use of 3D needs to be carefully justified. In most cases, rather than choosing a visual encoding using three dimensions of spatial position, a better answer is to visually encode using only two dimensions of spatial position. Often an appropriate 2D encoding follows from a different choice of data abstraction, where the original dataset is transformed by computing derived data.
<!-- /verbatim -->

The depth cues the section examines are occlusion, perspective distortion, shadows and lighting, familiar size and stereoscopic disparity, followed by text legibility, situations where the benefits of showing depth could outweigh its costs, and the need to justify that the situation has been correctly analysed [p.143].

## Planar position only

<!-- verbatim p.143 -->
> A crucial point when interpreting the channel rankings in Figure 5.6 is that the spatial position channels apply only to planar spatial position, not arbitrary 3D position.
<!-- /verbatim -->

## Vertical versus horizontal

- **One category.** Vertical and horizontal position share the category "planar" because the differences between the up–down and side-to-side axes are relatively subtle [p.143].
- **Vertical has slight priority.** Height differences along the up–down axis are perceived as more important than horizontal differences, which the author attributes to gravity [p.143].
- **Density can override it.** Standard displays have more horizontal than vertical pixels, so information density considerations sometimes override the vertical channel's priority [p.143].
- **Reading order.** For the perceived importance of items ordered within an axis, reading conventions probably dominate: most Western languages run left to right and top to bottom, Arabic and Hebrew right to left, and some Asian languages vertically [p.143].

## Figures

## Related

- [5.5.1 Accuracy](../../ch05-marks-channels/s05-05-channel-effectiveness/s05-05-01-accuracy.md): Figure 5.6's channel rankings, whose position channels this subsection limits to the plane [p.143]
- [6.3.2 The Disparity of Depth](s06-03-02-disparity-depth.md): why depth position is judged far less accurately than planar position [p.143]
- [6.3.7 Benefits of 3D: Shape Perception](s06-03-07-benefits-3d-shape-perception.md): the shape-understanding case where 3D is easy to justify [p.142]
- [6.3.8 Justification and Alternatives](s06-03-08-justification-alternatives.md): a worked example of reaching a 2D encoding through derived data [p.143]
