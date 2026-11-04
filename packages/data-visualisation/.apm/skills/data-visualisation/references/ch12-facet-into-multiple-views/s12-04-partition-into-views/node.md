---
id: s12.04
kind: section-node
title: "Partition into Views"
pdf_pages: [304, 313]
printed_pages: [279, 288]
toc: [s12.04]
fidelity: summary
---

# 12.4 Partition into Views

How to partition a multiattribute dataset into meaningful groups placed in separate regions, which has major implications for what patterns are visible and encodes association through spatial proximity, a highly ranked channel [p.304]. The choices are how to divide the data given a hierarchy of attributes, how many splits to make, the order in which attributes split, and how many views to use [p.304]. A partitioning attribute is typically categorical with few levels, or a derived binned attribute, and may be a key or a value [p.304]. Grouping is the inverse, bottom-up term; conditioning, hierarchical partitioning and dimensional stacking are synonyms [p.304].

## Children

- [12.4.1 Regions, Glyphs, and Views](s12-04-01-regions-glyphs-views.md) · ~709 words. **Use when** connecting partitioning to spatial arrangement (separate, then order and align), choosing what to draw in each region (one mark, a glyph or a full view), or deciding whether something is a view or a glyph; covers macroglyphs and microglyphs [pp.304-306]
- [12.4.2 List Alignments](s12-04-02-list-alignments.md) · ~335 words. **Use when** a table with two categorical keys and one quantitative value must be shown as bars and you must choose between grouped bars (compare across attributes) and aligned small-multiple bar charts (compare within one attribute) [pp.306-307]
- [12.4.3 Matrix Alignments](s12-04-03-matrix-alignments.md) · ~540 words. **Use when** a table with several categorical keys (three in the barley example) is partitioned into a 2D matrix of small charts and you need to order the panels (main-effects ordering) so trends and outliers show; the Trellis barley example [pp.307-309]
- [12.4.4 Recursive Subdivision](s12-04-04-recursive-subdivision.md) · ~630 words. **Use when** partitioning recursively through several attributes, letting users reorder the splits, size regions by count (an implicit treemap) or switch a level to geographic maps; the HiVE example [pp.310-313]
- [Trellis](../../idioms/trellis.md) · ~793 words. **Use when** you need the Trellis System box (three categorical keys, one quantitative value, dot charts aligned in a 2D matrix, medians derived for each partition) or plotting hints for such a matrix [pp.307-309]

## Disambiguation

- **List Alignments vs Matrix Alignments vs Recursive Subdivision.** Split by how the partitions are laid out: 12.4.2 aligns regions in a 1D list, 12.4.3 in a 2D matrix, and 12.4.4 nests regions inside regions through several splits [p.304] [pp.306-313].
- **Matrix Alignments vs Trellis.** 12.4.3 holds the narrative of the barley example and main-effects ordering; the Trellis card holds its System box, use conditions and code [pp.307-309].
- **Regions, Glyphs, and Views vs List Alignments.** 12.4.1 gives the general region, glyph and view continuum; 12.4.2 applies it to grouped versus small-multiple bars, which can be read either as glyphs or as partitions [p.305] [p.307].

## Related

- [7.5 Separate, Order, and Align: Categorical Regions](../../ch07-arrange-tables/s07-05-separate-order-align-categorical/node.md): separation, ordering and alignment, which partitioning feeds [p.304]
- [7.5.1 List Alignment: One Key](../../ch07-arrange-tables/s07-05-separate-order-align-categorical/s07-05-01-list-alignment-one-key.md): dot charts, the views Trellis aligns [p.307]
- [7.5.4 Recursive Subdivision: Multiple Keys](../../ch07-arrange-tables/s07-05-separate-order-align-categorical/s07-05-04-recursive-subdivision-multiple-keys.md): recursive subdivision for tables with many keys [p.304]
- [9.5 Containment: Hierarchy Marks](../../ch09-arrange-networks-trees/s09-05-containment-hierarchy-marks.md): treemaps, which recursive subdivision sized by counts yields [p.313]
- [8.3 Geometry](../../ch08-arrange-spatial-data/s08-03-geometry.md#s08.03.01): choropleth maps, used at the second level in HiVE [p.313]
- [12.3.2 Share Data: All, Subset, None](../s12-03-juxtapose-coordinate-views/s12-03-02-share-data-all-subset.md): small multiples as a coordination choice [p.298]
- [12.3.5 Juxtapose Views](../s12-03-juxtapose-coordinate-views/s12-03-05-juxtapose-views.md): automatic alignment of views, common when data is partitioned [p.303]
