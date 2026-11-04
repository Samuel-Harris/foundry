---
id: s02.04.02
kind: subsection-leaf
title: "Networks and Trees"
pdf_pages: [51, 52]
printed_pages: [26, 27]
toc: [s02.04.02, s02.04.02.01]
fidelity: mixed
---

# 2.4.2 Networks and Trees

## Networks

<!-- verbatim p.51 -->
> The dataset type of networks is well suited for specifying that there is some kind of relationship between two or more items.
<!-- /verbatim -->

<!-- verbatim p.51 -->
> An item in a network is often called a node.
<!-- /verbatim -->

<!-- verbatim p.51 -->
> A link is a relation between two items.
<!-- /verbatim -->

- **Examples.** In a social network, nodes are people and links mean friendship; in a gene interaction network, nodes are genes and links mean they have been observed to interact; in a computer network, nodes are computers and links are the ability to send messages directly between two of them [p.51].
- **Attributes.** Nodes can have attributes, just like table items. Links can also have attributes, which may be partly or wholly disjoint from the node attributes [p.51].
- **Synonyms.** Network is also called graph, a word overloaded in vis: graph drawing and graph theory use it to mean network, but statistical graphics uses it to mean chart, as in bar graphs and line graphs. Node is also called vertex, and link is also called edge [p.51].
- **Abstract versus layout.** The abstract network is distinct from any particular visual layout that gives nodes and edges spatial positions; this chapter concentrates on the abstract network [p.52].

<a id="s02.04.02.01"></a>

### 2.4.2.1 Trees

<!-- verbatim p.52 -->
> Networks with hierarchical structure are more specifically called trees. In contrast to a general network, trees do not have cycles: each child node has only one parent node pointing to it.
<!-- /verbatim -->

Examples are a company's organisation chart showing who reports to whom, and the biological tree of life, where humans and monkeys share the parent node of primates [p.52].

## Figures

## Related

- [9 Arrange Networks and Trees](../../ch09-arrange-networks-trees/node.md): the spatial arrangement of networks and trees [p.52]
- [2.4.5 Other Combinations](s02-04-05-other-combinations.md): paths and compound networks, built on top of the basic network type [p.55]
- [2.4.1 Tables](s02-04-01-tables.md): items with attributes, which network nodes resemble [p.51]
