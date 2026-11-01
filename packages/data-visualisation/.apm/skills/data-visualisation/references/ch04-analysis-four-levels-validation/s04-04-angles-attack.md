---
id: s04.04
kind: section-leaf
title: "Angles of Attack"
pdf_pages: [98, 99]
printed_pages: [73, 74]
toc: [s04.04]
fidelity: mixed
---

# 4.4 Angles of Attack

There are two common angles of attack: top down or bottom up. Problem-driven work starts at the domain situation level and works down through abstraction, idiom and algorithm. Technique-driven work starts at one of the bottom two levels, inventing new idioms that better support existing abstractions or new algorithms that better support existing idioms [p.98].

## Problem-driven work

In problem-driven vis you begin with a real-world user's problems and design a solution that helps them work more effectively; the literature often calls this a design study [p.98]. Often existing idioms suffice and much of the challenge lies at the abstraction level, though sometimes no existing idiom adequately solves the abstracted problem and a new one is designed [p.98].

**The skipped-levels pitfall.** Some designers skip the domain situation level entirely, short-circuit the abstraction level by assuming the first abstraction that comes to mind is correct, and jump straight to idiom design [pp.98-99]. The book argues against this:

<!-- verbatim p.99 -->
> I argue against this approach; the abstraction stage is often the hardest to get right.
<!-- /verbatim -->

A designer struggling to find the right abstraction may realise the domain situation is not yet adequately characterised and go back up to it. Problem-driven design is almost never strictly linear; it involves iterative refinement at all levels [p.99].

## Technique-driven work

Here the starting point is an idea for a new encoding or interaction idiom or a new algorithm, and design starts directly at that level [p.99]. The nested model helps you articulate your assumptions at the level just above: the abstraction requirements for a new idiom, or the idiom requirements for a new algorithm [p.99].

## How the book's framework serves each direction

The book's analysis framework focuses on the what–why abstraction and how idiom levels and works in either direction [p.99]. Problem-driven work goes downward, searching for existing idioms by analysing which design choices suit the identified task and chosen data abstraction. Technique-driven work goes upward, classifying a proposed idiom within the design choices to discuss its relationship to previous idioms [p.99]. A new algorithm should likewise be analysed against the idioms it supports, which can be tricky to untangle [p.99]:

<!-- verbatim p.99 -->
> Can your new algorithm simply be switched for a previous one, providing a faster way to compute the same visual encoding? Or does your new algorithm result in a visual encoding different enough to constitutes a new idiom that requires justification to show it's a good match for human capabilities and the intended task?
<!-- /verbatim -->

## Figures

## Related

- [4.3 Four Levels of Design](s04-03-four-levels-design/node.md): the levels these angles move through [p.98]
- [4.7.5 LinLog](s04-07-validation-examples/s04-07-05-linlog.md): a worked case where an apparent algorithm contribution is really an idiom [p.99]
- [4.8 Further Reading](s04-08-further-reading.md): design study methodology and its 32 pitfalls [p.98]
