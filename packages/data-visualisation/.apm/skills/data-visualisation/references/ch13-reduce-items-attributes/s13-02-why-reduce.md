---
id: s13.02
kind: section-leaf
title: "Why Reduce?"
pdf_pages: [324, 325]
printed_pages: [299, 300]
toc: [s13.02]
fidelity: mixed
---

# 13.2 Why Reduce?

## One of five strategies for managing complexity

Reduction is one of five major strategies for managing complexity in visualisations; the five are not mutually exclusive, and combinations of them are common [p.324]. The margin note names the other four and where they are covered: deriving new data (Chapter 3), changing a view over time (Chapter 11), faceting data into multiple views (Chapter 12) and embedding focus and context together within one view (Chapter 14) [p.324].

## Reduction idioms are bidirectional

Static data reduction idioms typically only reduce what is shown, but in the dynamic case changing a parameter or choice may increase the number of visible elements [p.324]. Many of the chapter's idioms are therefore bidirectional, though all are named after the reduction action for brevity [p.324].

## The challenge, and the word "element"

<!-- verbatim p.324 -->
> Reducing the amount of data shown in a view is an obvious way to reduce its visual complexity. Of course, the devil is in the details, where the challenge is to minimize the chances that information important to the task is hidden from the user.
<!-- /verbatim -->

Reduction applies to both items and attributes; the book uses **element** for either when a design choice applies to both [p.324].

## Filter versus aggregate: the trade-off

<!-- verbatim p.324 -->
> Filtering simply eliminates elements, whereas aggregation creates a single new element that stands in for multiple others that it replaces.
<!-- /verbatim -->

The book calls it useful to consider the trade-offs between the two explicitly when making design choices [p.324]:

- **Filtering** is very straightforward for users to understand, and typically to compute [p.324]. But people tend to have an "out of sight, out of mind" mentality: they forget to take filtered-out elements into account, even when the filtering was quite recent [pp.324-325].
- **Aggregation** can be somewhat safer cognitively, because the stand-in element is designed to convey information about the whole set it replaces [p.325]. By definition it cannot convey all the omitted information; the challenge is how and what to summarise so that it matches the dataset and task [p.325].

## Figures

## Related

- [13.3 Filter](s13-03-filter/node.md): the filtering choice in detail [p.325]
- [13.4 Aggregate](s13-04-aggregate/node.md): the aggregation choice in detail [p.325]
- [3 Why: Task Abstraction](../ch03-why-task-abstraction/node.md): deriving new data, another of the five strategies [p.324]
- [11 Manipulate View](../ch11-manipulate-view/node.md): changing a view over time, another of the five strategies [p.324]
- [12 Facet into Multiple Views](../ch12-facet-into-multiple-views/node.md): faceting into multiple views, another of the five strategies [p.324]
- [14 Embed: Focus+Context](../ch14-embed-focus-context/node.md): embedding focus and context, the fifth strategy [p.324]
