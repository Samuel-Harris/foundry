---
id: ch02
kind: chapter-node
title: "What: Data Abstraction"
pdf_pages: [45, 66]
printed_pages: [20, 41]
toc: [ch02]
fidelity: summary
---

# 2 What: Data Abstraction

The vocabulary for describing what is visualised, independent of any visual representation. Five data types (items, attributes, links, positions, grids) combine into four basic dataset types (tables, networks, fields, geometry) plus clusters, sets and lists; any dataset can be static or dynamic; attributes are categorical or ordered (ordinal or quantitative) with a sequential, diverging or cyclic direction [pp.45-46]. Type (structural or mathematical interpretation) and semantics (real-world meaning, chiefly key versus value and temporal) are crosscutting, and you need both to interpret data rather than guess at it [p.47] [p.59].

## Children

- [2.1 The Big Picture](s02-01-big-picture.md) · ~349 words. **Use when** you need the whole data taxonomy in one paragraph and one figure, to classify a dataset quickly before descending to a specific type [pp.45-46]
- [2.2 Why Do Data Semantics and Types Matter?](s02-02-why-data-semantics-types.md) · ~586 words. **Use when** data arrives as bare numbers or words with no stated meaning, and you must separate what can be inferred from its syntax from what the data's creator must supply; defines semantics versus type at the data, dataset and attribute levels [pp.46-48]
- [2.3 Data Types](s02-03-data-types.md) · ~283 words. **Use when** deciding whether a piece of data is an item (discrete entity), an attribute (measured property), a link (relationship between items), a position (2D or 3D location) or a grid (sampling strategy for continuous data) [pp.48-49]
- [2.4 Dataset Types](s02-04-dataset-types/node.md) · ~617 words. **Use when** classifying the whole dataset's structure as a table, a network or tree, a continuous field, geometry, or a set, list, cluster, path or compound network, or deciding whether it is a static file or a dynamic stream [pp.49-56]
- [2.5 Attribute Types](s02-05-attribute-types.md) · ~766 words. **Use when** classifying one attribute (column) as categorical, ordinal or quantitative, deciding whether ordered values run sequentially, diverge from a zero point or wrap cyclically, or whether the attribute has hierarchical structure such as days to years [pp.56-59]
- [2.6 Semantics](s02-06-semantics/node.md) · ~309 words. **Use when** deciding which attributes are keys (indexes) and which are values in a table or field, whether a field is scalar, vector or tensor, or whether time is a key (time-varying data, time series) or a value [pp.59-65]
- [2.7 Further Reading](s02-07-further-reading.md) · ~246 words. **Use when** you need a source to cite or read further on where the book's data taxonomy comes from (Card et al., Tory and Möller, Shneiderman), how to visualise fields (Telea, Ward et al., Hansen and Johnson, the vtk book), where categorical, ordinal and quantitative come from (Stevens, Wilkinson, Card and Mackinlay), how Polaris/Tableau splits dimensions from measures (Stolte et al.), or time-oriented data (Aigner et al.) [p.65]

## Disambiguation

- **The Big Picture vs Data Types vs Dataset Types vs Attribute Types.** 2.1 only names every type in one quoted paragraph and Figure 2.1, with a pointer to the section that covers each; go to 2.3, 2.4 or 2.5 for definitions, examples and how to classify a given dataset or attribute [pp.45-46].
- **Why Do Data Semantics and Types Matter? vs Semantics.** 2.2 motivates the split between semantics and type with worked examples; 2.6 holds the book's actual classification of semantics, keys versus values and temporal attributes [pp.47-48] [p.59].
- **Data Types vs Dataset Types.** Data types are the five building blocks; dataset types are the structures those blocks combine into, for example a network is items (nodes) plus links plus attributes [p.49].
- **Dataset Types vs Semantics.** 2.4 introduces flat and multidimensional tables and fields by structure; 2.6 says which of their attributes act as keys and how many keys and values each has. Go to 2.6 for "how many keys" or "scalar, vector or tensor" questions [p.50] [pp.59-62]. The word "dynamic" splits across both: a stream that changes during the session is in 2.4, while time as a key attribute is time-varying semantics in 2.6 [p.65].
- **Attribute Types vs Semantics.** Type and semantics are crosscutting, so one does not dictate the other [p.59]. Cyclic time (hour, day, month) and hierarchical time aggregation are attribute-type questions in 2.5; whether time is a key or a value is in 2.6 [pp.58-59] [p.64].

## Related

- [3 Why: Task Abstraction](../ch03-why-task-abstraction/node.md): the "why" half of the analysis framework that pairs with this "what" half in Figure 2.1 [p.45]
- [3.4.2.3 Derive](../ch03-why-task-abstraction/s03-04-actions/s03-04-02-produce.md#s03.04.02.03): deriving and transforming data, which blurs the line between data and metadata and produces derived attributes [p.48] [p.55]
- [6.3 No Unjustified 3D](../ch06-rules-thumb/s06-03-no-unjustified-3d/node.md): why the book reserves "dimension" for the visual channels of spatial position rather than for attributes [p.48]
- [7 Arrange Tables](../ch07-arrange-tables/node.md): how to arrange table datasets spatially [p.50]
- [8 Arrange Spatial Data](../ch08-arrange-spatial-data/node.md): idioms for the spatial fields and geometry dataset types, where spatial position is given [pp.53-55]
- [9 Arrange Networks and Trees](../ch09-arrange-networks-trees/node.md): the spatial arrangement of network and tree datasets [p.52]
- [13.4 Aggregate](../ch13-reduce-items-attributes/s13-04-aggregate/node.md): hierarchical aggregation of attributes and temporal data [p.59] [p.64]
- [7.5 Separate, Order, and Align: Categorical Regions](../ch07-arrange-tables/s07-05-separate-order-align-categorical/node.md): visual encoding of attribute hierarchies [p.59]
- [6.5 Eyes Beat Memory](../ch06-rules-thumb/s06-05-eyes-beat-memory.md): vision versus memory, relevant when time-varying data is shown by animation [p.64]
