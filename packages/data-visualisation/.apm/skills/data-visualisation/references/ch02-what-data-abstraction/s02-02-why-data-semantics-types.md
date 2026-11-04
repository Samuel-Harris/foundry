---
id: s02.02
kind: section-leaf
title: "Why Do Data Semantics and Types Matter?"
pdf_pages: [46, 48]
printed_pages: [21, 23]
toc: [s02.02]
fidelity: mixed
---

# 2.2 Why Do Data Semantics and Types Matter?

## Data drives design

<!-- verbatim p.46 -->
> Many aspects of vis design are driven by the kind of data that you have at your disposal.
<!-- /verbatim -->

The book frames three questions: what kind of data you are given, what you can figure out from the data versus what meanings you must be told explicitly, and what high-level concepts split datasets into general and useful pieces [p.46].

## Uninterpretable data without meaning

- The sequence `14, 2.6, 30, 30, 15, 100001` cannot be interpreted without more information: it could be two far-apart points in 3D space, or two close points in 2D with 15 links between them carrying a weight of 100001 [pp.46-47].
- The line `Basil, 7, S, Pear` could describe a produce shipment, snow clearance in a neighbourhood, or a lab rat's attempts at a maze [p.47].

## Semantics versus type

<!-- verbatim p.47 -->
> To move beyond guesses, you need to know two crosscutting pieces of information about these terms: their semantics and their types. The semantics of the data is its real-world meaning.
<!-- /verbatim -->

Semantics answers questions such as whether a word is a first name, a shortened company name, a city or a fruit, and whether a number is a day of the month, an age, a height, a unique code, a postal code or a position in space [p.47].

<!-- verbatim p.47 -->
> The type of the data is its structural or mathematical interpretation. At the data level, what kind of thing is it: an item, a link, an attribute? At the dataset level, how are these data types combined into a larger structure: a table, a tree, a field of sampled values? At the attribute level, what kinds of mathematical operations are meaningful for it?
<!-- /verbatim -->

A count of detergent boxes is a quantity, so adding two counts makes sense. A postal code is a code, the name for a category that happens to be a number, so adding two of them does not make sense [p.47].

## Table 2.1 and metadata

- Table 2.1 lists people with the columns ID, Name, Age, Shirt Size and Favorite Fruit; the column titles supply the semantics, which the dataset's creator should provide [pp.47-48].
- The text calls the table "tiny, with only nine rows and four columns", but the printed table has ten rows and five columns including ID. The book does not reconcile the two counts [pp.47-48].
- Types and semantics can sometimes be inferred from a data file's syntax or variable names, but often must be supplied with the dataset; that extra information is sometimes called metadata [pp.47-48].
- The line between data and metadata is unclear, especially because original data is often derived and transformed, so the book refers to everything as data [p.48].
- The classification that follows aims to be general enough for the cases that matter in vis yet specific enough to guide design choices at the abstraction and idiom levels [p.48].

## Figures

## Related

- [2.3 Data Types](s02-03-data-types.md): the data-level types (item, link, attribute, position, grid) [p.47]
- [2.4 Dataset Types](s02-04-dataset-types/node.md): the dataset-level types (table, tree, field and others) [p.47]
- [2.5 Attribute Types](s02-05-attribute-types.md): the attribute-level types that decide which operations are meaningful [p.47]
- [2.6 Semantics](s02-06-semantics/node.md): the book's classification of semantics, with Table 2.1 reused to choose a key [p.60]
- [3.4.2.3 Derive](../ch03-why-task-abstraction/s03-04-actions/s03-04-02-produce.md#s03.04.02.03): deriving data, the reason data and metadata are not distinguished [p.48]
