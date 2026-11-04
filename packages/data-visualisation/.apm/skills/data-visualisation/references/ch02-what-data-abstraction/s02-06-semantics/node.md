---
id: s02.06
kind: section-node
title: "Semantics"
pdf_pages: [59, 65]
printed_pages: [34, 40]
toc: [s02.06]
fidelity: summary
---

# 2.6 Semantics

Knowing an attribute's type does not tell you its semantics: the two questions are crosscutting [p.59]. The book's classification focuses on keys versus values, and the related questions of spatial and continuous versus nonspatial and discrete data, to match its idiom design framework; it also considers whether an attribute is temporal [p.59].

## Children

- [2.6.1 Key versus Value Semantics](s02-06-01-key-value-semantics.md) · ~1,082 words. **Use when** deciding which attributes index the data (keys) and which are looked up (values): choosing a unique key in a flat table, recognising a multidimensional table that needs several keys, treating spatial position as a quantitative key in a field, or classifying a field as scalar, vector or tensor by values per cell [pp.59-63]
- [2.6.2 Temporal Semantics](s02-06-02-temporal-semantics.md) · ~532 words. **Use when** an attribute relates to time and you must decide whether it is a key (time-varying data, a time series) or a value (a duration or transaction date), handle multiscale or periodic time, or resolve the two meanings of "dynamic" [pp.63-65]

## Disambiguation

- **Key versus Value Semantics vs Temporal Semantics.** Time is one possible key: a time series is a table with time as the key, and a time-varying scan has keys x, y, z, t. Use 2.6.2 for anything specific to time and 2.6.1 for keys in general [p.64].

## Related

- [2.5 Attribute Types](../s02-05-attribute-types.md): the attribute types that semantics crosscut [p.59]
- [2.4.6 Dataset Availability](../s02-04-dataset-types/s02-04-06-dataset-availability.md): dynamic streams versus static files, the other meaning of "dynamic" [p.65]
- [3.4.2.3 Derive](../../ch03-why-task-abstraction/s03-04-actions/s03-04-02-produce.md#s03.04.02.03): data transformation, often complex for temporal data [p.64]
- [13.4 Aggregate](../../ch13-reduce-items-attributes/s13-04-aggregate/node.md): aggregation, often complex for temporal data [p.64]
- [6.5 Eyes Beat Memory](../../ch06-rules-thumb/s06-05-eyes-beat-memory.md): vision versus memory, behind the point that animation is only one way to show change over time [p.64]
- [7.3 Arrange by Keys and Values](../../ch07-arrange-tables/s07-03-arrange-keys-values.md): how the key/value split drives the arrangement of tables [p.59]
