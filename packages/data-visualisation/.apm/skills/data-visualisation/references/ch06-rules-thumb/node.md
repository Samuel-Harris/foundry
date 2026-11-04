---
id: ch06
kind: chapter-node
title: "Rules of Thumb"
pdf_pages: [141, 167]
printed_pages: [116, 142]
toc: [ch06]
fidelity: summary
---

# 6 Rules of Thumb

Eight rules of thumb, each a piece of advice with a catchy slogan for a title: No Unjustified 3D, No Unjustified 2D, Eyes Beat Memory, Resolution over Immersion, Overview First, Zoom and Filter, Details on Demand, Responsiveness Is Required, Get It Right in Black and White, and Function First, Form Next [pp.141-142]. The author presents them as a synthesis of current knowledge, drawn from empirical studies, his own experience and earlier work, and calls them deeply incomplete [p.142]. Each rule's section gives the reasons and evidence behind it [pp.142-166].

## Children

- [6.1 The Big Picture](s06-01-big-picture.md) · ~271 words. **Use when** you want all eight rules on one page, for example as a critique checklist, before choosing which rule to read in full [pp.141-142]
- [6.2 Why and When to Follow Rules of Thumb?](s06-02-why-when-follow-rules.md) · ~210 words. **Use when** deciding how much weight a rule should carry in an argument: what evidence the rules rest on and how settled they are [p.142]
- [6.3 No Unjustified 3D](s06-03-no-unjustified-3d/node.md) · ~799 words. **Use when** a design encodes data with depth: 3D bar charts, 3D scatter or node–link layouts, 3D landscapes, perspective views, tilted 3D labels; or when inherently 3D spatial data and a shape-understanding task may justify 3D [pp.142-155]
- [6.4 No Unjustified 2D](s06-04-no-unjustified-2d.md) · ~240 words. **Use when** data is laid out in 2D (such as a node–link diagram) and a 1D ordered list might serve the task better, especially label lookup [p.156]
- [6.5 Eyes Beat Memory](s06-05-eyes-beat-memory.md) · ~866 words. **Use when** a design makes viewers remember what they saw before: navigation without an overview, multiframe animation instead of side-by-side views, animated transitions, change blindness [pp.156-159]
- [6.6 Resolution over Immersion](s06-06-resolution-over-immersion.md) · ~435 words. **Use when** weighing an immersive display (head-mounted, projection room, stereo with head tracking) against a desktop display's pixels and workflow integration [pp.159-160]
- [6.7 Overview First, Zoom and Filter, Details on Demand](s06-07-overview-first-zoom-filter.md) · ~559 words. **Use when** designing or critiquing how users move between an overview and details, how an overview is built for a large dataset, or what to do when no useful overview is feasible [pp.160-162]
- [6.8 Responsiveness Is Required](s06-08-responsiveness-required.md) · ~875 words. **Use when** setting or diagnosing interaction latency: the 0.1, 1 and 10 second classes, visual feedback, progress indicators, click versus hover, detail pane versus popup versus highlight, and the human cost of interaction [pp.162-165]
- [6.9 Get It Right in Black and White](s06-09-get-right-black-white.md) · ~175 words. **Use when** checking whether the most important information stays legible without hue, by giving it luminance contrast [p.165]
- [6.10 Function First, Form Next](s06-10-function-first-form-next.md) · ~285 words. **Use when** trading visual beauty against effectiveness, or deciding whether to refine a design or start again [pp.165-166]
- [6.11 Further Reading](s06-11-further-reading.md) · ~328 words. **Use when** you need a source to cite or read beyond the book for one rule: Ware and St. John et al. on depth cues and 2D versus 3D studies; Ware and Scarr et al. on memory and spatial memory; Tversky et al. and Robertson et al. on animation versus small multiples; Simons on change blindness; Shneiderman and Hornbæk and Hertzum on overviews; Card et al., Johnson, Lam and Yi et al. on latency and interaction costs; Stone on black and white; Williams on graphic design. It lists nothing for No Unjustified 2D or Resolution over Immersion [pp.166-167]

## Disambiguation

- **The Big Picture vs Why and When to Follow Rules of Thumb?.** 6.1 lists the rules; 6.2 says where they come from and that they are incomplete [p.142].
- **No Unjustified 3D vs No Unjustified 2D.** 6.3 weighs three spatial dimensions against two for a visual encoding; 6.4 weighs a 2D layout against a 1D list [pp.142-143] [p.156].
- **No Unjustified 3D vs Resolution over Immersion.** 6.3 is about encoding data in depth on any display; 6.6 is about immersive display hardware, which costs resolution and workflow integration and needs even more justification than 3D for abstract data [pp.159-160].
- **Eyes Beat Memory vs Overview First, Zoom and Filter, Details on Demand.** Both involve overviews. 6.5 argues from memory load, with an overview window as an external aid to orientation; 6.7 covers how overviews are built through reduction and how they pair with detail views [p.156] [pp.160-162].
- **Eyes Beat Memory vs Responsiveness Is Required.** Both touch animated transitions. 6.5 says when animation helps or burdens memory; 6.8 places the length of a transition in the one-second latency class [pp.157-158] [p.162].

## Related

- [5.5.1 Accuracy](../ch05-marks-channels/s05-05-channel-effectiveness/s05-05-01-accuracy.md): the channel rankings and power-law exponents that No Unjustified 3D builds on [p.143]
- [1.13 Why Are There Resource Limitations?](../ch01-whats-vis-why/s01-13-why-there-resource-limitations.md): display resolution as the scarce resource behind Resolution over Immersion [p.159]
- [12.3.2 Share Data: All, Subset, None](../ch12-facet-into-multiple-views/s12-03-juxtapose-coordinate-views/s12-03-02-share-data-all-subset.md): small multiples, the side-by-side alternative to animation [p.158]
- [11.5 Navigate: Changing Viewpoint](../ch11-manipulate-view/s11-05-navigate-changing-viewpoint.md): geometric navigation for 3D and geometric and semantic zooming for overviews [p.150] [p.161]
- [13.4 Aggregate](../ch13-reduce-items-attributes/s13-04-aggregate/node.md): aggregation, needed when items outnumber pixels in an overview [p.161]
- [10.2 Color Theory](../ch10-map-color-other-channels/s10-02-color-theory/node.md): the colour principles behind Get It Right in Black and White [p.165]
- [12 Facet into Multiple Views](../ch12-facet-into-multiple-views/node.md): multiple views, one way to pair overview and detail [p.162]
- [14 Embed: Focus+Context](../ch14-embed-focus-context/node.md): embedding focus and context in one view, the third overview family [p.162]
- [1.11 Why Are Most Designs Ineffective?](../ch01-whats-vis-why/s01-11-why-most-designs-ineffective.md): the size of the design space and the ineffectiveness of most designs, which Function First, Form Next mirrors [p.166]
