---
id: s12.04.01
kind: subsection-leaf
title: "Regions, Glyphs, and Views"
pdf_pages: [304, 306]
printed_pages: [279, 281]
toc: [s12.04.01]
fidelity: mixed
---

# 12.4.1 Regions, Glyphs, and Views

## Partitioning the dataset

How a multiattribute dataset is partitioned into groups has major implications for what patterns the user sees; it encodes association between items through spatial proximity, a highly ranked channel [p.304]. The primary choice is how to divide the data between views given a hierarchy of attributes. Further choices: how many splits (down to one region per item, encoded with a single mark, or stopping higher where each region has more complex structure), the order in which attributes split, and how many views, often data driven but possibly fixed in advance [p.304].

A partitioning attribute is typically categorical with a limited number of levels, or derived, for example by binning a quantitative attribute. Key or value attributes can partition; an attribute can be categorical without being a key. Partitioning by keys can reach the item level, since all keys together index each item uniquely; with a value attribute, the final division may be a group of items [p.304].

Partitioning and grouping are inverse terms, top-down and bottom-up; conditioning is the statistics synonym, and hierarchical partitioning and dimensional stacking are further synonyms [p.304].

## Partitioning as spatial separation

<!-- verbatim p.304 -->
> To connect partioning to visual encoding choices, the crucial idea is that a partitioned group can be placed within a region of space, so partitioning is an action that addresses the separate choice when arranging data in space.
<!-- /verbatim -->

The regions then need ordering, and often aligning, for example in a 1D list or 2D matrix. Recursive subdivision nests regions inside each other, and the nested regions may use the same arrangement choices as their enclosing regions or different ones [pp.304-305].

With one key, separate into one region per item. With two keys X and Y, separate first by X then Y, first by Y then X, or by only one key with something more complex drawn inside each region [p.305]. What a region encodes falls on a continuum: a single mark, a glyph (an object with internal structure from multiple marks), or a full view with a complete encoding [p.305].

## Region, view or glyph

There is no strict dividing line between a region, a view and a glyph [p.305].

<!-- verbatim p.305 -->
> A view is a contiguous region in which visually encoded data is shown on the display.
<!-- /verbatim -->

A view may be an operating-system window, a panel or pane, or just a visually bounded region; display, window, panel and pane are synonyms [p.305]. Whether a region showing data in some idiom is called a glyph or a view depends on its screen size, how much information beyond the encoding it shows, and whether it is nested in another region. Large, stand-alone, highly detailed regions are likely to be called views, and small, nested, schematic ones glyphs [p.305]. An 800 by 400 pixel bar chart with labelled axes, confidence intervals, legend and title would usually be called a view; each of a set of 50 by 25 pixel schematic bar charts placed in map regions might be called a glyph [p.305]. The author notes that the word glyph is used very ambiguously and his definitions, including the mark versus glyph distinction, are not standard [p.305].

## Glyph sizes

- **Macroglyphs.** Larger structures like the schematic bar charts, or a complex 3D shape showing several aspects of local fluid flow at once; designing them is a microcosm of vis design [p.305].
- **Middle of the spectrum.** Simpler structures such as one multipart bar in a stacked bar chart [p.305].
- **Microglyphs.** So small their structure is not meant to be distinguished, such as five short connected segments whose angles encode a quantitative attribute within 15 by 4 pixels. They are typically used in a dense 2D array forming a sea of visual texture, in the hope that boundaries emerge where values change [pp.305-306].

## Figures

## Related

- [7.5 Separate, Order, and Align: Categorical Regions](../../ch07-arrange-tables/s07-05-separate-order-align-categorical/node.md): separation, ordering and alignment covered in full [p.304]
- [12.4.2 List Alignments](s12-04-02-list-alignments.md): grouped bars versus small multiples, read as glyphs or as partitions [p.306]
- [12.4.4 Recursive Subdivision](s12-04-04-recursive-subdivision.md): nested regions in practice [p.305]
- [Stacked Bar Charts](../../idioms/stacked-bar-charts.md): the multipart bar given as a mid-sized glyph [p.305]
