---
id: ch14
kind: chapter-node
title: "Embed: Focus+Context"
pdf_pages: [347, 363]
printed_pages: [322, 338]
toc: [ch14]
fidelity: summary
---

# 14 Embed: Focus+Context

How to embed detailed information about a selected focus set within a single view that also shows overview context for more of the data, combining filtering and aggregation [p.348]. Three design choices: elide items, superimpose a local layer, or distort the geometry; each has single or multiple foci, and distortion adds choices of region shape, extent and interaction metaphor [p.348]. Distortion has measurable costs, so the chapter closes by weighing it against occlusion and other interaction [pp.359-362]. On semantic zooming versus distortion, the book gives no ranking: it calls focus+context nonliteral navigation in the same spirit as semantic zooming [p.349], and Figure 11.7, Chapter 11's semantic-zooming example, is cited here as stretch and squish navigation [p.356]. What it does state is when distortion fits badly: it severely impairs distance and length judgements, so it is a poor match for any task that needs them, while topology tasks on node–link layouts are likely robust to it [p.359]; mental tracking costs rise with the amount of distortion [p.360]. Some focus+context idioms avoid geometric distortion altogether [p.349].

## Children

- [14.1 The Big Picture](s14-01-big-picture.md) · ~346 words. **Use when** you need the map of the three embedding choices (elide, superimpose, distort) and the many near-synonym names for focus+context before descending [pp.347-348]
- [14.2 Why Embed?](s14-02-why-embed.md) · ~336 words. **Use when** justifying focus+context over geometric zooming: the user loses orientation in a zoomed single view and needs landmarks kept in the same view [pp.348-349]
- [14.3 Elide](s14-03-elide.md) · ~373 words. **Use when** some items can be filtered out entirely and others aggregated for context, driven by a degree-of-interest function, often over hierarchical structure [pp.349-350]
- [14.4 Superimpose](s14-04-superimpose.md) · ~243 words. **Use when** focus details should appear in a movable local layer over an unchanged background, accepting that the layer occludes what lies beneath [p.351]
- [14.5 Distort](s14-05-distort.md) · ~1,227 words. **Use when** context regions should be compressed geometrically to make room for magnified focus; covers the four design choices (number of foci, shape, extent, interaction metaphor) and five distortion examples [pp.352-359]
- [14.6 Costs and Benefits: Distortion](s14-06-costs-benefits-distortion.md) · ~817 words. **Use when** deciding whether distortion suits a task or a non-distorting option such as semantic zooming or layering would serve better, or critiquing a distorted view: impaired distance and length judgements, unnoticed distortion, object constancy, and fisheye versus magnifying lens versus neighbourhood highlighting [pp.359-362]
- [14.7 Further Reading](s14-07-further-reading.md) · ~280 words. **Use when** looking for primary sources on focus+context surveys, early bifocal and polyfocal displays, generalised fisheye views, frameworks, hyperbolic trees or stretch and squish navigation [pp.362-363]
- [3D Perspective](../idioms/3d-perspective.md) · ~556 words. **Use when** assessing a tree shown in 3D perspective (Cone Trees) as a global single-focus distortion with geometric navigation; System box, history and code [pp.352-353]
- [DOITrees Revisited](../idioms/doitrees-revisited.md) · ~596 words. **Use when** a very large tree (hundreds of thousands of nodes) must show several focus nodes with elided subtrees aggregated as triangles; System box and code [p.350]
- [Fisheye Lens](../idioms/fisheye-lens.md) · ~854 words. **Use when** any layout needs a single draggable local radial magnifier that keeps the focus embedded in its surroundings, such as labels in a dense scatterplot [pp.353-354]
- [Hyperbolic Geometry](../idioms/hyperbolic-geometry.md) · ~704 words. **Use when** a tree or network grows exponentially and needs a single global radial focus moved by hyperbolic translation [pp.354-356]
- [Nonlinear Magnification Fields](../idioms/nonlinear-magnification-fields.md) · ~550 words. **Use when** any layout needs multiple foci of arbitrary shape and magnification level in local regions, including data-driven magnification [pp.358-359]
- [Stretch and Squish Navigation](../idioms/stretch-and-squish-navigation.md) · ~742 words. **Use when** any layout needs multiple rectangular foci of global extent with all items kept in the viewport, often with guaranteed visibility of important marks [pp.356-358]
- [Toolglass and Magic Lenses](../idioms/toolglass-and-magic-lenses.md) · ~526 words. **Use when** a see-through lens should show a different encoding of the data beneath it in a local foreground layer; System box and code [p.351]

## Disambiguation

- **Elide vs Superimpose vs Distort.** Elide omits items and aggregates others for context; superimpose adds a local focus layer over an unchanged background; distort compresses context geometrically to enlarge the focus [pp.348-352].
- **Distort vs Costs and Benefits: Distortion.** 14.5 describes the design choices and five idioms; 14.6 judges when distortion helps or hurts, by task [pp.352-362].
- **Elide vs DOITrees Revisited.** 14.3 holds the degree-of-interest framework; the card is its worked tree example with the System box [pp.349-350].
- **Superimpose vs Toolglass and Magic Lenses.** 14.4 is the design choice; the card is its example system [p.351].
- **Fisheye Lens vs Hyperbolic Geometry.** Both have a single radial focus; the fisheye lens is local and moved by 2D translation, hyperbolic geometry is global, suits trees or networks and moves by hyperbolic translation [pp.353-356].
- **Stretch and Squish Navigation vs Nonlinear Magnification Fields.** Both allow multiple foci; stretch and squish uses global rectangular regions on a rubber sheet, magnification fields allow local regions of arbitrary shape and level, with lens, stretch or data-driven metaphors [pp.356-359].
- **3D Perspective vs Hyperbolic Geometry.** Both are global single-focus distortions of trees; 3D perspective uses standard graphics transformations and geometric navigation, hyperbolic geometry projects non-Euclidean space and uses hyperbolic translation [pp.352-356].
- **Fisheye Lens vs Costs and Benefits: Distortion.** The card is the idiom itself, with its box and code; 14.6 is where the book compares a fisheye lens with a magnifying lens and neighbourhood highlighting on one graph and finds the fisheye may be harder to use [pp.360-361].
- **Fisheye Lens vs Toolglass and Magic Lenses.** Both are movable lenses whose layer replaces what is beneath; the fisheye distorts geometry continuously, the magic lens shows different information undistorted [pp.351-353].

## Related

- [11.5 Navigate: Changing Viewpoint](../ch11-manipulate-view/s11-05-navigate-changing-viewpoint.md): geometric zooming, whose disorientation focus+context tries to mitigate, and semantic zooming, its nonliteral sibling [pp.348-349]
- [Semantic Zooming](../idioms/semantic-zooming.md): the nonliteral navigation idiom the book names alongside focus+context, a non-distorting option to weigh when distortion's costs bite [p.349]
- [12.5 Superimpose Layers](../ch12-facet-into-multiple-views/s12-05-superimpose-layers/node.md): global superimposed layers, as opposed to the local focus layer here [p.351]
- [6.3 No Unjustified 3D](../ch06-rules-thumb/s06-03-no-unjustified-3d/node.md): the costs and benefits of 3D that undermined 3D perspective for abstract data [p.353]
- [13 Reduce Items and Attributes](../ch13-reduce-items-attributes/node.md): the filtering and aggregation that embedding combines [p.348]
- [9 Arrange Networks and Trees](../ch09-arrange-networks-trees/node.md): node–link and containment layouts, the most successful use of geometric distortion [p.359]
- [12 Facet into Multiple Views](../ch12-facet-into-multiple-views/node.md): one of the four alternatives to embedding for showing complex information [p.359]
