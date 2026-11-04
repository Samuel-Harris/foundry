---
id: s12.05.01
kind: subsection-leaf
title: "Visually Distinguishable Layers"
pdf_pages: [313, 314]
printed_pages: [288, 289]
toc: [s12.05.01]
fidelity: mixed
---

# 12.5.1 Visually Distinguishable Layers

## Superimposing and its choices

Superimposing stacks multiple layers directly on top of each other in one composite view. All drawings share the same horizontal and vertical extent and blend as if completely transparent where they have no marks; in graphics terms it is an image-space compositing operation with an identical coordinate system [p.313].

<!-- verbatim p.313 -->
> A visual layer is simply a set of objects spread out over a region, where the set of objects in each layer is a visually distinguishable group that can be told apart from objects in other layers at a perceptual level.
<!-- /verbatim -->

The region is typically the entire view, so layering views is a direct alternative to juxtaposing them side by side [p.313]. The choices: how many layers, how to distinguish them, whether a small static set or dynamically constructed from user selection [p.313], and how to partition items into layers. Static layers are commonly divided like views, by attribute types and semantics; dynamic layers often by a very lightweight choice driven by the user's changing selection rather than dataset structure [p.314].

## Distinguishing layers

<!-- verbatim p.314 -->
> One good way to make distinguishable layers is to ensure that each layer uses a different and nonoverlapping range of the visual channels active in the encoding.
<!-- /verbatim -->

A common choice is two layers, foreground versus background; with careful design, a few layers are possible [p.314].

## How many layers

<!-- verbatim p.314 -->
> The main limitation of layering is that the number of layers that can be visually distinguished is limited to very few if the layers contain a substantial number of area marks: two layers is deﬁnitely achievable, and three layers is possible with careful design.
<!-- /verbatim -->

Layering many views is feasible only if each layer contains very little, such as a single line [p.314]. A layer usually means objects spread through the region, intermixed with objects outside it, but a single highlighted object could be considered a very simple layer [p.314].

## Figures

## Related

- [12.5.2 Static Layers](s12-05-02-static-layers.md): these rules applied to maps, line charts and edge bundles [p.314]
- [12.5.3 Dynamic Layers](s12-05-03-dynamic-layers.md): layers built from user selection [p.314]
- [12.4 Partition into Views](../s12-04-partition-into-views/node.md): partitioning items, which static layers follow in spirit [p.314]
- [12.2 Why Facet?](../s12-02-why-facet.md): the costs of layering weighed against its direct alternative, juxtaposed views [p.313]
- [11.4.2 Highlighting](../../ch11-manipulate-view/s11-04-select-elements/s11-04-02-highlighting.md): highlighting, which can form a minimal layer [p.314]
