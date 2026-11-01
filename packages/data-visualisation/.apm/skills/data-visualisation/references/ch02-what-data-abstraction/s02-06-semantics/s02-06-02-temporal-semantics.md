---
id: s02.06.02
kind: subsection-leaf
title: "Temporal Semantics"
pdf_pages: [63, 65]
printed_pages: [38, 40]
toc: [s02.06.02, s02.06.02.01]
fidelity: mixed
---

# 2.6.2 Temporal Semantics

## Temporal attributes

<!-- verbatim p.63 -->
> A temporal attribute is simply any kind of information that relates to time.
<!-- /verbatim -->

- **Why time is hard.** Time has rich hierarchical structure and potential periodic structure. The hierarchy is deeply multiscale, from nanoseconds to millennia; even "time" and "date" partly specify the scale of interest [p.63].
- **Periodicity.** Temporal analysis tasks often involve finding or verifying periodicity, at a predetermined scale or one not known in advance [p.63].
- **Not a strict hierarchy.** Weeks do not fit cleanly into months, so transformation and aggregation are often particularly complex for temporal data [pp.63-64].
- **Encoding is open.** Data whose semantics involve change over time can be encoded in many ways, and animation is only one of them [p.64].

## Key or value

<!-- verbatim p.64 -->
> Temporal attributes can have either value or key semantics.
<!-- /verbatim -->

- **Value examples.** A duration of elapsed time, or the date on which a transaction occurred [p.64].
- **Key examples.** In spatial fields and abstract tables, time can be an independent key; a time-varying medical scan has keys x, y, z, t and the value density [p.64].
- **Type of a temporal key.** Usually quantitative, though it can be considered ordinal if the duration between events is not interesting [p.64].

<a id="s02.06.02.01"></a>

### 2.6.2.1 Time-Varying Data

<!-- verbatim p.64 -->
> A dataset has time-varying semantics when time is one of the key attributes, as opposed to when the temporal attribute is a value rather than a key.
<!-- /verbatim -->

- **Needs external knowledge.** Whether time is a key or a value cannot be decided from type information alone [p.64].
- **Time-varying example.** A sensor network recording each animal's location in a herd every second: time is an independent key and likely central to understanding the data [p.64].
- **Not time-varying.** A year of horse races with temporal value attributes such as start time and run duration deals with time but is not time-varying [p.64].

<!-- verbatim p.64 -->
> A common case of temporal data occurs in a time-series dataset, namely, an ordered sequence of time–value pairs. These datasets are a special case of tables, where time is the key.
<!-- /verbatim -->

- **Spacing.** Time-value pairs are often, but not always, at uniform intervals [p.64].
- **Tasks.** Typical time-series tasks are finding trends, correlations and variations at multiple time scales such as hourly, daily, weekly and seasonal [p.64].

### Two meanings of "dynamic"

The word dynamic is used ambiguously. Some mean time-varying semantics, where time is a key; others mean a stream, where items and attributes can be added or deleted and values change during a running session, as opposed to an unchanging file loaded all at once. The book keeps the two meanings distinct [p.65].

## Figures

## Related

- [2.4.6 Dataset Availability](../s02-04-dataset-types/s02-04-06-dataset-availability.md): dynamic streams versus static files [p.65]
- [3.4.2.3 Derive](../../ch03-why-task-abstraction/s03-04-actions/s03-04-02-produce.md#s03.04.02.03): the problem of data transformation [p.64]
- [13.4 Aggregate](../../ch13-reduce-items-attributes/s13-04-aggregate/node.md): aggregation in detail [p.64]
- [6.5 Eyes Beat Memory](../../ch06-rules-thumb/s06-05-eyes-beat-memory.md): vision versus memory, relevant to choosing animation for change over time [p.64]
- [2.5 Attribute Types](../s02-05-attribute-types.md): cyclic and hierarchical time as attribute-type properties [p.63]
