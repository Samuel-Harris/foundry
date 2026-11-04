---
id: s06.03.05
kind: subsection-leaf
title: "Other Depth Cues"
pdf_pages: [148, 149]
printed_pages: [123, 124]
toc: [s06.03.05]
fidelity: mixed
---

# 6.3.5 Other Depth Cues

## Familiar size

In realistic scenes we can estimate depth from objects of known size, such as a car. When every object in the scene is a visual encoding of abstract information, this strong cue is unavailable [p.148].

## Shadows and surface shading

Cast shadows help resolve depth ambiguity by showing an object's height above a ground plane, and shading and self-shadowing show 3D shape [p.148]. For abstract data these lighting cues bring four problems [p.148]:

- **Clutter.** They create visual clutter that distracts from the meaningful parts of the scene [p.148].
- **False marks.** Cast shadows, self-shadowed regions or highlights could be mistaken for true marks carrying attribute information [p.148].
- **Occlusion.** Cast shadows could occlude true marks [p.148].
- **Colour interference.** Surface shading interferes with the colour channels, in the book's words below [p.148].

<!-- verbatim p.148 -->
> highlights can change the hue or saturation, and shadows change the luminance.
<!-- /verbatim -->

## Stereoscopic depth

Stereo depth comes from the disparity between two images taken from slightly separated viewpoints, like our two eyes; the cues above are all pictorial cues from a single camera [p.148].

<!-- verbatim p.148 -->
> Although many people assume that stereo vision is the strongest depth cue, it is in fact a relatively weak one compared with the others listed above and contributes little for distant objects.
<!-- /verbatim -->

- **Where stereo helps.** It is most useful for nearby objects at roughly the same depth, guiding the manipulation of things within arm's reach [p.148].
- **Stereo displays.** They help people resolve depth better and do not directly interfere with the main visual channels, but depth still cannot be perceived as accurately as planar position [p.148].
- **No cure for perspective.** Stereo cannot solve any of the problems of perspective distortion [p.148].

## Atmospheric perspective

Atmospheric perspective, a relatively subtle cue that shifts the colour of distant objects towards blue, would conflict with colour encoding [p.149].

## Figures

## Related

- [6.3.3 Occlusion Hides Information](s06-03-03-occlusion-hides-information.md): occlusion, the most powerful depth cue [p.148]
- [6.3.4 Perspective Distortion Dangers](s06-03-04-perspective-distortion-dangers.md): the distortion that stereo cannot fix [p.148]
- [6.6 Resolution over Immersion](../s06-06-resolution-over-immersion.md): immersive displays that deliver stereo imagery and their costs [p.148]
- [10.2 Color Theory](../../ch10-map-color-other-channels/s10-02-color-theory/node.md): the hue, saturation and luminance channels that shading and atmospheric perspective disrupt [p.148]
