---
id: s06.07
kind: section-leaf
title: "Overview First, Zoom and Filter, Details on Demand"
pdf_pages: [160, 162]
printed_pages: [135, 137]
toc: [s06.07]
fidelity: mixed
---

# 6.7 Overview First, Zoom and Filter, Details on Demand

## The rule

<!-- verbatim p.160 -->
> Ben Shneiderman's influential mantra of Overview First, Zoom and Filter, Details on Demand [Shneiderman 96] is a heavily cited design guideline that emphasizes the interplay between the need for overview and the need to see details, and the role of data reduction in general and navigation in particular in supporting both.
<!-- /verbatim -->

## What an overview is

- **Purpose.** An overview gives broad awareness of the entire information space; in the what–why–how framework its goal is summarize [pp.160-161].
- **Common design goal.** Show all items at once, with no need to pan or scroll [p.161].
- **Use.** Overviews help users find regions worth investigating in more detail. They are often shown first, but users commonly switch back and forth between overview and detail views many times [p.161].

## How overviews are built

- **Geometric zoom out.** The simplest overview zooms out until the whole dataset fits in the frame, each object drawn smaller with less detail. In this sense an overview removes all filtering, moving from a zoomed-in view where some items are filtered out to one where all are shown [p.161].
- **Aggregation when items outnumber pixels.** When there are more items than pixels, even single-pixel marks cannot show them all, so the number of marks must be reduced by aggregation [p.161].
- **Custom overviews.** Even for medium-sized datasets, designing an overview more carefully than simple geometric zooming can be fruitful. Such overviews resemble semantic zooming, representing items in a qualitatively different way, and often use dynamic aggregation driven implicitly by navigation rather than chosen by the user [p.161].

## Overview versus detail

No crisp line separates an overview from an ordinary idiom, but a relative distinction is useful: the less detailed view summarising a lot of data is the overview, and the view showing fewer items with more information each is the detail view [p.161]. Three families of idioms support overviewing [pp.161-162]:

- **Multiple views.** The distinction is most obvious here; the mantra fits especially well when a detail view pops up in response to a select action, though a permanently visible detail view beside the overview is also common [pp.161-162].
- **A single changing view.** One view supports reduce actions such as zooming and filtering, acting sometimes as overview and sometimes as detail [p.162].
- **Embedding.** Detailed focus and overview context are embedded together in a single view [p.162].

## Limits of the mantra

The mantra helps most with datasets of moderate size; for enormous datasets a useful overview for top-down exploration may not be feasible [p.162].

<!-- verbatim p.162 -->
> In slogan form, an alternative approach is Search, Show Context, Expand on Demand [van Ham and Perer 09], where search results provide the starting point for browsing of local neighborhoods.
<!-- /verbatim -->

## Figures

## Related

- [13.4 Aggregate](../ch13-reduce-items-attributes/s13-04-aggregate/node.md): aggregation, discussed there [p.161]
- [11.5 Navigate: Changing Viewpoint](../ch11-manipulate-view/s11-05-navigate-changing-viewpoint.md): geometric and semantic zooming, discussed there [p.161]
- [12 Facet into Multiple Views](../ch12-facet-into-multiple-views/node.md): the multiple-view family [p.162]
- [13 Reduce Items and Attributes](../ch13-reduce-items-attributes/node.md): data reduction for the single changing view [p.162]
- [14 Embed: Focus+Context](../ch14-embed-focus-context/node.md): the embedding family [p.162]
- [3.4.4 Query](../ch03-why-task-abstraction/s03-04-actions/s03-04-04-query.md): the summarize goal that an overview serves [p.161]
- [6.5 Eyes Beat Memory](s06-05-eyes-beat-memory.md): an overview window as an external aid to orientation [p.161]
