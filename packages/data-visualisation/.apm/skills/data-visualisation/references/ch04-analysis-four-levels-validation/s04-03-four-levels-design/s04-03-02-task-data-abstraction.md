---
id: s04.03.02
kind: subsection-leaf
title: "Task and Data Abstraction"
pdf_pages: [95, 96]
printed_pages: [70, 71]
toc: [s04.03.02]
fidelity: mixed
---

# 4.3.2 Task and Data Abstraction

## Task blocks are identified

This level abstracts the specific domain questions and data into a generic representation. The domain-independent vocabulary reveals that situations described in very different language might have similar reasons why the user needs a vis tool and what data it shows [p.95].

Questions from very different domain situations can map to the same abstract vis tasks, such as browsing, comparing and summarising. Task blocks are identified by the designer as suitable for a particular situation block, just as situation blocks are identified at the level above [p.95].

## Data blocks are designed

<!-- verbatim p.95 -->
> Abstract data blocks, however, are designed. Selecting a data block is a creative design step rather than simply an act of identification.
<!-- /verbatim -->

You may use the data exactly as identified in the domain situation, but you will often transform it into something quite different. The level asks whether and how the user's dataset should be transformed into another form [p.95]. Many idioms are specific to a data type: a table whose columns hold quantitative, ordered or categorical data; a node–link graph or tree; or a field of values at every point in space [p.95]. The goal is to find the data type that supports a visual representation addressing the user's problem; sometimes the original form matches, but often a transformation to another type gives a better solution [pp.95-96].

## Implicit abstraction is a failure mode

Explicitly considering the abstraction choices is very useful; the unfortunate alternative is to make them implicitly and without justification [p.96]. Example: many early web vis papers implicitly posited that the "lost in hyperspace" problem should be solved by showing the searcher the topological structure of the web's hyperlink graph. People do not need an internal mental representation of that structure to find a page [p.96].

<!-- verbatim p.96 -->
> Thus, no matter how cleverly the information was visually encoded at the idiom design level, the resulting vis tools all incurred additional cognitive load for the user rather than reducing it.
<!-- /verbatim -->

## Figures

## Related

- [3 Why: Task Abstraction](../../ch03-why-task-abstraction/node.md): abstract tasks in detail [p.95]
- [2 What: Data Abstraction](../../ch02-what-data-abstraction/node.md): the abstract data types a data block chooses among [p.96]
- [3.4.2.3 Derive](../../ch03-why-task-abstraction/s03-04-actions/s03-04-02-produce.md#s03.04.02.03): transforming and deriving data, the design step at this level [p.96]
- [4.6.2 Abstraction Validation](../s04-06-validation-approaches/s04-06-02-abstraction-validation.md): how to test that the chosen abstraction solves the users' problem [p.96]
- [4.3.3 Visual Encoding and Interaction Idiom](s04-03-03-visual-encoding-interaction-idiom.md): the level that uses these task and data blocks to rule idioms in or out [p.96]
