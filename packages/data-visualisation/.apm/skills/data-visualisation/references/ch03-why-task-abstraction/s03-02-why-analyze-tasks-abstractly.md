---
id: s03.02
kind: section-leaf
title: "Why Analyze Tasks Abstractly?"
pdf_pages: [68, 69]
printed_pages: [43, 44]
toc: [s03.02]
fidelity: mixed
---

# 3.2 Why Analyze Tasks Abstractly?

## Translate domain language into generic terms

<!-- verbatim p.68 -->
> This framework encourages you to consider tasks in abstract form, rather than the domain-specific way that users typically think about them.
<!-- /verbatim -->

Translating task descriptions from domain-specific language into abstract form lets you reason about their similarities and differences. Without that translation everything appears different, which is misleading: once the surface language is stripped away, there are many similarities in what people want to do [pp.68-69].

**Example.** An epidemiologist asks to "contrast the prognosis" of patients intubated more than a month after exposure with patients hospitalised within the first week; a biologist asks to "see if the results" for tissue samples treated with LL-37 "match up with" those without it. The different words ("contrast" versus "match up") hide the common task [p.69]:

<!-- verbatim p.69 -->
> If you transform these into descriptions using a consistent set of generic terms, then you can spot that these two tasks are just two instances of the same thing: “compare values between two groups”.
<!-- /verbatim -->

## A small vocabulary of verbs and nouns

The framework has a small set of carefully chosen words for why people use vis, designed to distinguish goals crisply and concisely: verbs describe actions and nouns describe targets [p.69]. You may add terms to describe a user's goals completely and precisely; if so, translate domain-specific terms into words that are as generic as possible [p.69].

## One goal at a time, or a chain

The same vis tool may serve many goals. Considering one goal at a time makes it easier to ask how a particular idiom supports that goal [p.69].

<!-- verbatim p.69 -->
> To describe complex activities, you can specify a chained sequence of tasks, where the output of one becomes the input to the next.
<!-- /verbatim -->

## Task guides data

Analysing the task also tells you whether and how to transform the user's original data by deriving new data [p.69].

<!-- verbatim p.69 -->
> That is, the task abstraction can and should guide the data abstraction.
<!-- /verbatim -->

## Figures

## Related

- [3.4.2 Produce](s03-04-actions/s03-04-02-produce.md): the derive action that the task abstraction guides [p.69]
- [3.7 Analyzing and Deriving: Examples](s03-07-analyzing-deriving-examples/node.md): chained sequences of tasks worked through for real systems [p.69]
- [2 What: Data Abstraction](../ch02-what-data-abstraction/node.md): the data abstraction that the task abstraction should guide [p.69]
