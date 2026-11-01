---
id: ch09
kind: chapter-node
title: "Arrange Networks and Trees"
pdf_pages: [225, 242]
printed_pages: [200, 217]
toc: [ch09]
fidelity: summary
---

# 9 Arrange Networks and Trees

How to arrange network and tree data in space. Three design choices: node–link diagrams with connection marks, adjacency matrices built from a derived table, and enclosure with containment marks for trees and for hierarchies laid over networks [pp.225-226]. Choosing between them turns on the task (topology and path tracing versus lookup, counting and leaf attributes) and on network size and link density [pp.235-239].

## Children

- [9.1 The Big Picture](s09-01-big-picture.md) · ~232 words. **Use when** you need the three-way map of network and tree layouts, with which dataset type each choice applies to, before descending [pp.225-226]
- [9.2 Connection: Link Marks](s09-02-connection-link-marks.md) · ~1,393 words. **Use when** drawing a tree or small network with nodes as points and links as lines; covers tree layouts (triangular, radial, BubbleTree), hop distance, topology tasks, force-directed weaknesses and multilevel layouts [pp.226-233]
- [9.3 Matrix Views](s09-03-matrix-views.md) · ~436 words. **Use when** encoding a network as a derived two-key table of node pairs: cell colour, weighted or directed links, half-matrix for undirected graphs, density limits [pp.233-234]
- [9.4 Costs and Benefits: Connection versus Matrix](s09-04-costs-benefits-connection-matrix.md) · ~993 words. **Use when** deciding between node–link and matrix for a given network size, link density and task, or critiquing that choice; includes the empirical task-by-task study [pp.234-238]
- [9.5 Containment: Hierarchy Marks](s09-05-containment-hierarchy-marks.md) · ~921 words. **Use when** the data is a tree or a compound network with a cluster hierarchy and you want nesting; compares seven tree encodings including icicle, concentric circles and indented outline [pp.238-241]
- [9.6 Further Reading](s09-06-further-reading.md) · ~302 words. **Use when** you need a source to cite or read beyond the book: network vis surveys and McGuffin's node–link, matrix and hybrid tutorial; Melançon's edge-density readability limit; force-directed algorithms (Brandes, GEM); multilevel layouts (sfdp, FM3, TopoLayout); Ghoniem et al.'s matrix versus node–link study; tree-drawing design spaces (treevis.net, McGuffin and Robert); treemap origins and Kong et al.'s bar chart versus treemap density guidelines [pp.241-242]
- [Adjacency Matrix View](../idioms/adjacency-matrix-view.md) · ~704 words. **Use when** a large or dense network (up to about 1000 nodes, one million links) needs lookup, counting, cliques or degree rather than path tracing; box, uses and code [pp.233-238]
- [Force-Directed Placement](../idioms/force-directed-placement.md) · ~723 words. **Use when** laying out a general network of dozens to hundreds of nodes to explore topology and locate paths; box, pitfalls and code [pp.229-231]
- [GrouseFlocks](../idioms/grouseflocks.md) · ~579 words. **Use when** a network carries one or more cluster hierarchies that users should see and compare, drawn as containment over connection [pp.240-241]
- [Multilevel Force-Directed Placement (sfdp)](../idioms/multilevel-force-directed-placement-sfdp.md) · ~613 words. **Use when** a node–link layout must reach 1000 to 10,000 nodes and show clusters, via a derived coarsening hierarchy [pp.231-233]
- [Treemaps](../idioms/treemaps.md) · ~789 words. **Use when** a tree, often shallow, has a quantitative attribute at its leaves to query or scan for large outliers; area marks nested by containment [pp.238-239]

## Disambiguation

- **Connection: Link Marks vs Matrix Views vs Costs and Benefits: Connection versus Matrix.** 9.2 and 9.3 each describe one family; 9.4 is the head-to-head choice between them by size, density and task [pp.226-238].
- **Connection: Link Marks vs Force-Directed Placement vs Multilevel Force-Directed Placement (sfdp).** 9.2 holds the full narrative, including tree layouts; the two cards hold each idiom's box, use and avoid conditions and code. Pick force-directed placement for dozens to hundreds of nodes and sfdp for 1000 to 10,000 [pp.229-233].
- **Matrix Views vs Adjacency Matrix View.** 9.3 is the section narrative on deriving and encoding the matrix; the card holds the idiom box and the use and avoid conditions drawn from 9.3 and 9.4, plus code [pp.233-238].
- **Force-Directed Placement vs Adjacency Matrix View.** Node–link layouts suit small networks and topology tasks such as path tracing; matrices suit large or dense networks and lookup or counting tasks, but need trained users [pp.235-238].
- **Containment: Hierarchy Marks vs Treemaps vs GrouseFlocks.** 9.5 compares all containment and non-connection tree encodings; Treemaps is the card for a plain tree with sized leaves; GrouseFlocks is the card for a hierarchy laid over a network [pp.238-241].

## Related

- [2.4.2 Networks and Trees](../ch02-what-data-abstraction/s02-04-dataset-types/s02-04-02-networks-trees.md): the network and tree dataset types this chapter arranges [p.226]
- [3.7.2 Deriving One Attribute](../ch03-why-task-abstraction/s03-07-analyzing-deriving-examples/s03-07-02-deriving-one-attribute.md): the Strahler metric used to colour a node–link tree [p.227]
- [6.3 No Unjustified 3D](../ch06-rules-thumb/s06-03-no-unjustified-3d/node.md): why 3D network layouts need careful justification [p.229]
- [7.5 Separate, Order, and Align: Categorical Regions](../ch07-arrange-tables/s07-05-separate-order-align-categorical/node.md): reordering, which matrix views support [p.236]
- [7.5.2 Matrix Alignment: Two Keys](../ch07-arrange-tables/s07-05-separate-order-align-categorical/s07-05-02-matrix-alignment-two-keys.md): the 2D alignment and scalability shared by adjacency matrices, and cluster hierarchies [p.233]
- [13.4.1 Item Aggregation](../ch13-reduce-items-attributes/s13-04-aggregate/s13-04-01-item-aggregation.md): cluster hierarchies and aggregated multilevel matrices for very large networks [p.236]
- [13 Reduce Items and Attributes](../ch13-reduce-items-attributes/node.md): filtering and aggregation to relieve node–link clutter, at a cost in memory load [p.235]
- [14 Embed: Focus+Context](../ch14-embed-focus-context/node.md): the book's further node–link tree examples (DOITree, Cone Trees, H3, TreeJuxtaposer) [p.235]
- [12.3 Juxtapose and Coordinate Views](../ch12-facet-into-multiple-views/s12-03-juxtapose-coordinate-views/node.md): hybrid multiple-view systems that pair node–link and matrix views [p.237]
