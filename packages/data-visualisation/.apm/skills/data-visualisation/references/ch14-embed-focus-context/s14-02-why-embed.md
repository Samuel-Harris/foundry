---
id: s14.02
kind: section-leaf
title: "Why Embed?"
pdf_pages: [348, 349]
printed_pages: [323, 324]
toc: [s14.02]
fidelity: mixed
---

# 14.2 Why Embed?

## The goal: orientation

<!-- verbatim p.348 -->
> The goal of embedding focus and context together is to mitigate the potential for disorientation that comes with standard navigation techniques such as geometric zooming.
<!-- /verbatim -->

With realistic camera motion, zooming in to see a small region in detail leaves only a small part of world space visible [p.348]. With geometric navigation and a single view that changes over time, the only way to stay oriented is to remember one's own navigation history internally [p.349]. Focus+context idioms instead provide contextual information meant to act as recognisable landmarks, using external memory to reduce internal cognitive load [p.349].

## Nonliteral navigation

Focus+context is an example of nonliteral navigation, in the same spirit as semantic zooming [p.349]. In all such idioms the user interactively chooses a subset of items as the focus, drawn in detail, and some or all of the rest of the dataset is shown for context, embedded in the same view [p.349]. Some idioms do this without geometric distortion; many use carefully chosen distortion to combine magnified focus regions and minimised context regions in one view [p.349].

## Encoding and interaction together

<!-- verbatim p.349 -->
> Embedding idioms cannot be fully understood when considered purely from the visual encoding point of view or purely from the interaction point of view; they are fundamentally a synthesis of both.
<!-- /verbatim -->

The focus set changes dynamically as the user interacts, so the visual representation changes too [p.349]. Many idioms use indirect control, inferring the focus set from the user's navigation choices combined with the dataset's inherent structure [p.349].

## Figures

## Related

- [11.5 Navigate: Changing Viewpoint](../ch11-manipulate-view/s11-05-navigate-changing-viewpoint.md): geometric zooming, the standard navigation whose disorientation embedding mitigates [p.348]
- [Semantic Zooming](../idioms/semantic-zooming.md): the other nonliteral navigation idiom named alongside focus+context [p.349]
- [6.5 Eyes Beat Memory](../ch06-rules-thumb/s06-05-eyes-beat-memory.md): the external-versus-internal memory trade-off that motivates landmarks in context [p.349]
- [14.5 Distort](s14-05-distort.md): the carefully chosen distortion many embedding idioms use to unify focus and context [p.349]
