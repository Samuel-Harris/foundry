---
id: s07.03
kind: section-leaf
title: "Arrange by Keys and Values"
pdf_pages: [170, 171]
printed_pages: [145, 146]
toc: [s07.03]
fidelity: mixed
---

# 7.3 Arrange by Keys and Values

## Keys, values and levels

<!-- verbatim p.170 -->
> A key is an independent attribute that can be used as a unique index to look up items in a table, while a value is a dependent attribute: the value of a cell in a table.
<!-- /verbatim -->

- Key attributes can be categorical or ordinal; values can be any of the three types: categorical, ordinal or quantitative [pp.170-171].
- The unique values of a categorical or ordered attribute are called **levels**, to avoid overloading the term value [p.171].

## Choosing by the number of keys and values

<!-- verbatim p.171 -->
> The core design choices for visually encoding tables directly relate to the semantics of the table's attributes: how many keys and how many values does it have?
<!-- /verbatim -->

| Keys and values | Canonical example | Citation |
| --- | --- | --- |
| No keys, two values | Scatterplots | [p.171] |
| One key, one value | Bar charts | [p.171] |
| Two keys, one value | Heatmaps | [p.171] |
| Many keys, many values | Scatterplot matrices, which recursively subdivide space into many regions | [p.171] |

Datasets can have only value attributes, but visually encoding a dataset with only key attributes would be rare [p.171]. Keys are typically used to define a region of space for each item, in which one or more value attributes are shown [p.171].

## Figures

## Related

- [2.6.1 Key versus Value Semantics](../ch02-what-data-abstraction/s02-06-semantics/s02-06-01-key-value-semantics.md): the book's fuller treatment of keys and values [p.170]
- [Scatterplots](../idioms/scatterplots.md): the canonical value-only idiom [p.171]
- [Bar Charts](../idioms/bar-charts.md): the canonical one-key, one-value idiom [p.171]
- [Heatmaps](../idioms/heatmaps.md): the canonical two-key, one-value idiom [p.171]
- [Scatterplot Matrix (SPLOM)](../idioms/scatterplot-matrix-splom.md): the many-keys, many-values example [p.171]
- [7.5 Separate, Order, and Align: Categorical Regions](s07-05-separate-order-align-categorical/node.md): how keys define regions [p.171]
