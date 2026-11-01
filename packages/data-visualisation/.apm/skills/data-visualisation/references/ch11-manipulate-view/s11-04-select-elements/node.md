---
id: s11.04
kind: section-node
title: "Select Elements"
pdf_pages: [274, 279]
printed_pages: [249, 254]
toc: [s11.04]
fidelity: summary
---

# 11.4 Select Elements

Letting users select one or more elements of interest is a fundamental action that supports nearly every interactive idiom; the output of a selection is often the input to a later operation, and the change choice usually depends on a previous select result [p.274]. This section covers what can be selected and how many, how a selection is highlighted, and what it triggers [pp.275-279].

## Children

- [11.4.1 Selection Design Choices](s11-04-01-selection-design-choices.md) · ~590 words. **Use when** deciding what can be a selection target (items, links, attributes, attribute levels, views), how many selection types (click, hover, keys, touch) and how many elements a set may hold, including empty, primary versus secondary, and groups stored as attributes [pp.275-276]
- [11.4.2 Highlighting](s11-04-02-highlighting.md) · ~577 words. **Use when** choosing how selected items, links, attributes or views are shown: colour, outline, size, dash shape, motion, or link marks, and the trade-offs of each [pp.276-278]
- [11.4.3 Selection Outcomes](s11-04-03-selection-outcomes.md) · ~212 words. **Use when** a selection should trigger a further action such as filtering, aggregating, re-encoding, reordering, or navigating to centre the selected item [p.279]
- [Highlighting](../../idioms/highlighting.md) · ~701 words. **Use when** the selection is settled and you must pick its highlight quickly: an outline rather than a colour change when the existing colour coding must survive, outlines for large marks rather than small ones, motion as the unusual strong option; with code [pp.276-278]
- [Context-Preserving Visual Links](../../idioms/context-preserving-visual-links.md) · ~511 words. **Use when** selected items or regions in juxtaposed views must be connected by drawn link curves routed around salient content [p.278]

## Disambiguation

- **Selection Design Choices vs Highlighting.** The interaction idiom of how a user selects and the encoding idiom of how selected elements are highlighted are two choices that vary independently: 11.4.1 is the first, 11.4.2 the second [p.276].
- **11.4.2 Highlighting vs Highlighting.** Both cover the same choices; the card states them as use and avoid rules with code, and the leaf gives the book's reasoning in full, including the routed-link example [pp.276-278].
- **Highlighting vs Context-Preserving Visual Links.** Most highlighting changes existing marks (colour, outline, size, shape, motion); context-preserving visual links add new connection marks routed between selected items across juxtaposed views [pp.277-278].
- **Selection Outcomes vs Selection Design Choices.** 11.4.1 is about the selection set itself; 11.4.3 is about what the selected set feeds into next [pp.275-279].

## Related

- [11.3 Change View over Time](../s11-03-change-view-over-time.md): the change choices a selection usually feeds [p.274]
- [11.5 Navigate: Changing Viewpoint](../s11-05-navigate-changing-viewpoint.md): navigation trajectories that frame a selected item [p.279]
- [6.8 Responsiveness Is Required](../../ch06-rules-thumb/s06-08-responsiveness-required.md): timing requirements for highlight feedback [p.276]
- [5.5.4 Popout](../../ch05-marks-channels/s05-05-channel-effectiveness/s05-05-04-popout.md): why highlight colours need enough contrast to pop out [p.277]
- [12.5.2 Static Layers](../../ch12-facet-into-multiple-views/s12-05-superimpose-layers/s12-05-02-static-layers.md): edge bundling, used by visual links [p.278]
- [12 Facet into Multiple Views](../../ch12-facet-into-multiple-views/node.md): multiple views, where a view can be a selection target [p.275]
- [12.3 Juxtapose and Coordinate Views](../../ch12-facet-into-multiple-views/s12-03-juxtapose-coordinate-views/node.md): linked views across which selections and highlights are coordinated [p.278]
