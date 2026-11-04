---
id: s08.05
kind: section-node
title: "Vector Fields: Multiple Values"
pdf_pages: [214, 219]
printed_pages: [189, 194]
toc: [s08.05]
fidelity: summary
---

# 8.5 Vector Fields: Multiple Values

Vector fields, often from computational fluid dynamics, hold direction and magnitude at each cell; flow vis deals with velocity fields in 2D, in 3D, or on 2D surfaces in 3D, and with steady or unsteady (time-varying) flows [p.214]. The book gives four idiom families: local flow glyphs, geometric flow from sparse seeds, texture flow from dense seeds, and feature flow from global computation. A vector field can also be reduced to a scalar field [pp.214-215].

## Children

- [8.5.1 Flow Glyphs](s08-05-01-flow-glyphs.md) · ~748 words. **Use when** showing local direction and magnitude per cell with arrows or other glyphs, or when you need the section overview: critical point types, the four families and the empirical comparison of six 2D flow idioms [pp.214-216]
- [8.5.2 Geometric Flow](s08-05-02-geometric-flow.md) · ~528 words. **Use when** tracing particle trajectories from a sparse set of seeds and drawing them as streamlines, pathlines, streaklines, timelines or their surface counterparts, and choosing a seeding strategy [pp.216-218]
- [8.5.3 Texture Flow](s08-05-03-texture-flow.md) · ~261 words. **Use when** a 2D field or a field on a 2D surface should be covered densely, as in Line Integral Convolution [p.218]
- [8.5.4 Feature Flow](s08-05-04-feature-flow.md) · ~178 words. **Use when** structures such as critical points, vortices or shock waves should be computed and shown explicitly rather than inferred by the viewer [pp.218-219]
- [Similarity-Clustered Streamlines](../../idioms/similarity-clustered-streamlines.md) · ~772 words. **Use when** a 3D vector field of millions of samples needs hundreds of streamlines or pathlines, seeded, coloured and filtered by derived similarity clusters, to find features and query shape [pp.217-218]

## Disambiguation

- **Flow Glyphs vs Geometric Flow vs Texture Flow.** Glyphs show local information at each cell and suffer occlusion in 3D; geometric flow traces trajectories from a sparse set of seeds; texture flow traces from dense seeds across the whole field, mostly in 2D. In the Laidlaw et al. study no idiom won every task, but the two arrow-glyph idioms fared worst [pp.214-218].
- **Feature Flow vs Flow Glyphs vs Geometric Flow vs Texture Flow.** Feature flow computes and shows structures explicitly; the others help users infer them without necessarily showing them [p.219].
- **Geometric Flow vs Similarity-Clustered Streamlines.** 8.5.2 covers the whole family and its trajectory types; the card is one seeding strategy with its box [pp.216-218].

## Related

- [8.4 Scalar Fields: One Value](../s08-04-scalar-fields-one-value/node.md): scalar idioms for a vector field reduced to a scalar field [p.215]
- [8.6 Tensor Fields: Many Values](../s08-06-tensor-fields-many-values.md): tensor fields reuse all four families [p.219]
- [13.3 Filter](../../ch13-reduce-items-attributes/s13-03-filter/node.md): filtering streamlines by cluster [p.218]
- [12.5 Superimpose Layers](../../ch12-facet-into-multiple-views/s12-05-superimpose-layers/node.md): foreground and background layers for an emphasised cluster [p.218]
- [11.5 Navigate: Changing Viewpoint](../../ch11-manipulate-view/s11-05-navigate-changing-viewpoint.md): geometric navigation for 3D flow [p.216]
