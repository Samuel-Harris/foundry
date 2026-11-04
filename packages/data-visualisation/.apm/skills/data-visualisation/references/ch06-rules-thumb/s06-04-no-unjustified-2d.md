---
id: s06.04
kind: section-leaf
title: "No Unjustified 2D"
pdf_pages: [156, 156]
printed_pages: [131, 131]
toc: [s06.04]
fidelity: mixed
---

# 6.4 No Unjustified 2D

## The rule

<!-- verbatim p.156 -->
> Laying out data in 2D space should also be explicitly justified, compared with the alternative of simply showing the data with a 1D list.
<!-- /verbatim -->

## Strengths of lists

- **Information density.** Lists show the maximal amount of information, such as text labels, in minimal space; 2D layouts such as node–link representations of networks need considerably more space for the same number of labels, so their information density is notably lower [p.156].
- **Lookup.** Lists are excellent for lookup when ordered appropriately, for example alphabetically to find a known label; in a 2D node–link representation the user may have to hunt around the whole layout unless the tool has a search capability [p.156].

## When 2D is justified

When the task truly requires understanding the network's topological structure, the benefit of showing those relationships explicitly outweighs the space cost [p.156].

<!-- verbatim p.156 -->
> However, some tasks are handled well by linear lists, even if the original data has network structure.
<!-- /verbatim -->

## Figures

## Related

- [6.3 No Unjustified 3D](s06-03-no-unjustified-3d/node.md): the same justification argument for adding depth [p.156]
- [9.2 Connection: Link Marks](../ch09-arrange-networks-trees/s09-02-connection-link-marks.md): node–link diagrams and the topology tasks that justify them [p.156]
- [7.5 Separate, Order, and Align: Categorical Regions](../ch07-arrange-tables/s07-05-separate-order-align-categorical/node.md): ordering, which makes a list good for lookup [p.156]
- [3.4.3 Search](../ch03-why-task-abstraction/s03-04-actions/s03-04-03-search.md): the lookup task that lists support well [p.156]
