---
id: s02.04
kind: section-node
title: "Dataset Types"
pdf_pages: [49, 56]
printed_pages: [24, 31]
toc: [s02.04]
fidelity: summary
---

# 2.4 Dataset Types

A dataset is any collection of information that is the target of analysis. The four basic dataset types are tables, networks, fields and geometry; clusters, sets and lists are other ways to group items, and complex combinations are common in real-world situations [p.49]. Each type arises from a combination of the five data types (Figure 2.3), and Figure 2.4 shows the internal structure of the four basic ones [pp.49-50]. Figures 2.3 and 2.4 are homed in the Tables leaf [pp.49-50].

## Children

- [2.4.1 Tables](s02-04-01-tables.md) · ~416 words. **Use when** the data is discrete items each described by the same set of attributes, as rows and columns in a spreadsheet: a flat table with one row per item, or a multidimensional table whose cells need several keys to index [pp.50-51]
- [2.4.2 Networks and Trees](s02-04-02-networks-trees.md) · ~345 words. **Use when** the data specifies relationships between items: nodes joined by links, either of which may carry attributes, or a hierarchy with no cycles where each child has exactly one parent [pp.51-52]
- [2.4.3 Fields](s02-04-03-fields.md) · ~708 words. **Use when** cells hold measurements or calculations from a continuous domain, such as a medical scan or simulated airflow, so sampling and interpolation matter; also covers spatial fields, the scivis versus infovis split and uniform, rectilinear, structured and unstructured grids [pp.52-54]
- [2.4.4 Geometry](s02-04-04-geometry.md) · ~326 words. **Use when** items are shapes with explicit spatial positions (points, lines or curves, 2D regions, 3D volumes), possibly with no attributes, for shape understanding or as a backdrop for other data [pp.54-55]
- [2.4.5 Other Combinations](s02-04-05-other-combinations.md) · ~306 words. **Use when** items are grouped as an unordered set, an ordered list or a similarity-based cluster, when the data is a path through a network or a compound network (a network plus a tree over its nodes), or when describing a hybrid dataset in generic terms [pp.55-56]
- [2.4.6 Dataset Availability](s02-04-06-dataset-availability.md) · ~200 words. **Use when** the data arrives as a stream during the session, with items added, deleted or changed, rather than as a static file available all at once [p.56]

## Disambiguation

- **Tables vs Fields.** Both have cells holding attribute values. Table items are discrete, so interpolating between them is not meaningful; field cells sample a continuous domain, so new values can be interpolated between measurements [pp.52-53].
- **Fields vs Geometry.** Both are spatial and typically serve shape-understanding tasks. A field has a grid of positions whose cells contain attributes; geometry has only position information and need not have attributes [p.49] [pp.54-55].
- **Networks and Trees vs Other Combinations.** 2.4.2 covers plain networks and trees; paths and compound networks, structures built on top of the network type, are in 2.4.5 [pp.51-52] [p.55].
- **Tables vs Other Combinations.** Sets, lists and clusters group items without the item-by-attribute cell structure of a table; a cluster groups items by attribute similarity [p.49] [p.55].
- **Dataset Availability vs Tables vs Networks and Trees vs Fields vs Geometry.** Availability crosscuts the basic types: any of them can be static or dynamic, so classify structure first and availability separately [p.56].

## Related

- [2.3 Data Types](../s02-03-data-types.md): the five data types that combine into each dataset type [p.49]
- [2.6.1 Key versus Value Semantics](../s02-06-semantics/s02-06-01-key-value-semantics.md): keys and values in flat tables, multidimensional tables and fields [p.50]
- [7 Arrange Tables](../../ch07-arrange-tables/node.md): spatial arrangement of tables [p.50]
- [9 Arrange Networks and Trees](../../ch09-arrange-networks-trees/node.md): spatial arrangement of networks [p.52]
- [8 Arrange Spatial Data](../../ch08-arrange-spatial-data/node.md): idioms for spatial fields and geometry, where position is given with the dataset [pp.53-55]
- [8.4 Scalar Fields: One Value](../../ch08-arrange-spatial-data/s08-04-scalar-fields-one-value/node.md): generating contours from scalar fields, a classic derived geometry [p.55]
- [3.4.2.3 Derive](../../ch03-why-task-abstraction/s03-04-actions/s03-04-02-produce.md#s03.04.02.03): deriving data, including hierarchies and attributes derived from the original data [p.55]
