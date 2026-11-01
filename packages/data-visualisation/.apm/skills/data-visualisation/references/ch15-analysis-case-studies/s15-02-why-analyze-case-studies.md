---
id: s15.02
kind: section-leaf
title: "Why Analyze Case Studies?"
pdf_pages: [366, 367]
printed_pages: [341, 342]
toc: [s15.02]
fidelity: mixed
---

# 15.2 Why Analyze Case Studies?

## Purpose

<!-- verbatim p.366 -->
> The ability to concisely describe existing systems gives you a firm foundation for considering the full array of possibilities when you generate new systems.
<!-- /verbatim -->

The case studies show how to use the book's analysis framework to decompose a vis approach, however complex, into pieces you can think about systematically and compare with other approaches [pp.366-367]. They continue the analysis introduced gradually in earlier chapters; now that every design choice has been introduced, each example gets a complete analysis [p.367].

## What each analysis covers

- **Abstraction level.** The types and semantics of the data abstraction, including any derived data, and the targeted task abstraction [p.367].
- **Idiom level.** The design choices of how to encode data, facet data between multiple views, and reduce the data shown within a view [p.367].
- **Scalability.** A discussion of scale, still assuming an available screen of one million pixels in a standard 1000 by 1000 format [p.367].

## Data abstractions in real systems

A few of the systems have simple data abstractions that can be classified unambiguously as one simple dataset type: tables, networks or spatial data [p.367]. Most have more complex data abstractions, which is the common case in real-world problems: many carry out significant transformations of the original data to create derived data, handle combinations of multiple basic types, and are designed to support exploration of interesting structure at multiple levels [p.367].

## How to read them

<!-- verbatim p.367 -->
> The following analyses are descriptive examinations of the final design of each system, not prescriptive statements that the particular choices made by these designers are the only good solution that fits the requirements.
<!-- /verbatim -->

<!-- verbatim p.367 -->
> As you read through this chapter, it is a useful exercise to generate a set of alternatives for each choice made by these designers and to consider the pros and cons of each.
<!-- /verbatim -->

## Figures

## Related

- [1.14 Why Analyze?](../ch01-whats-vis-why/s01-14-why-analyze.md): the case for analysing vis systems with a shared framework, which this chapter applies in full [p.366]
- [2 What: Data Abstraction](../ch02-what-data-abstraction/node.md): dataset types, attribute types and derived data, the abstraction-level vocabulary [p.367]
- [3 Why: Task Abstraction](../ch03-why-task-abstraction/node.md): the task abstraction each analysis names [p.367]
- [4.3 Four Levels of Design](../ch04-analysis-four-levels-validation/s04-03-four-levels-design/node.md): the abstraction and idiom levels each analysis separates [p.367]
