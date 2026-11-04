---
id: ch11
kind: chapter-node
title: "Manipulate View"
pdf_pages: [267, 288]
printed_pages: [242, 263]
toc: [ch11]
fidelity: summary
---

# 11 Manipulate View

How a view changes over time in response to the user. Three design choices: change any aspect of the view, select elements within it, and navigate to a different viewpoint, including the attribute-reducing navigation idioms slice, cut and project [pp.267-269]. This is the chapter for the interaction layer of any interactive tool or dashboard; it is one of five options for handling complexity, alongside deriving data, faceting, reducing and embedding [p.269].

## Children

- [11.1 The Big Picture](s11-01-big-picture.md) · ~448 words. **Use when** you need the map of change, select and navigate choices, with what each covers, before choosing an interaction for a view [pp.267-269]
- [11.2 Why Change?](s11-02-why-change.md) · ~283 words. **Use when** justifying interactivity at all: a dataset too large or complex for one static view, and how change over time sits beside the other four complexity-handling options [p.269]
- [11.3 Change View over Time](s11-03-change-view-over-time.md) · ~1,234 words. **Use when** you need the worked examples of a changing view in full: Tableau switching between bars, stacked bars and a map by drag and drop, LineUp's ranking columns and four alignments, and the frame-by-frame zoom of an adjacency matrix with the limits of animated transitions [pp.269-274]
- [11.4 Select Elements](s11-04-select-elements/node.md) · ~488 words. **Use when** designing what a user can click or hover (items, links, attributes, levels, views), how many may be selected, how the selection is highlighted, and what it triggers next [pp.274-279]
- [11.5 Navigate: Changing Viewpoint](s11-05-navigate-changing-viewpoint.md) · ~1,213 words. **Use when** the layout is fixed and the user must zoom, pan or rotate a camera over it; covers geometric versus semantic zooming and constrained versus unconstrained navigation [pp.279-283]. Also the hop for semantic zooming versus Chapter 14's distortion: semantic zooming changes what an item draws for the pixels it gets, so text too small to read becomes a short label, while stretching and squishing changes how much space rows and columns get; the book does not rank the two, and LiveRAC uses both at once [pp.280-281]
- [11.6 Navigate: Reducing Attributes](s11-06-navigate-reducing-attributes.md) · ~1,016 words. **Use when** spatial field data, or abstract data with many dimensions, must be cut down to fewer dimensions interactively by slicing, cutting or projecting [pp.283-286]
- [11.7 Further Reading](s11-07-further-reading.md) · ~204 words. **Use when** looking for primary sources on change, animated transitions, selection across linked views, semantic zooming or constrained navigation [pp.286-287]
- [Change over Time](../idioms/change-view-over-time.md) · ~833 words. **Use when** deciding quickly which aspect of a view to make changeable (idiom, encoding parameter, order, alignment, amount of data) and whether it suits the data, such as reordering only categorical attributes; a compact use and avoid list with code, without the worked examples [pp.269-274]
- [LineUp](../idioms/lineup.md) · ~717 words. **Use when** a table with many attributes must be ranked by user-weighted combinations of attributes and several rankings compared; a System box with reorder and realign [pp.271-273]
- [Animated Transitions](../idioms/animated-transitions.md) · ~658 words. **Use when** a view changes state (navigation, reorder, filter, re-encode, value updates) and users must keep track of items across the change; limited amounts of change only [pp.273-274]
- [Geometric Zooming](../idioms/geometric-zooming.md) · ~598 words. **Use when** zooming should behave like moving closer to a physical object: appearance fixed, only drawn size changes [pp.279-280]
- [Semantic Zooming](../idioms/semantic-zooming.md) · ~671 words. **Use when** an item's representation should change with the pixels it gets, such as label, then title, then summary, or colour, then sparkline, then axes, because its content would be illegible if simply shrunk [p.280]. The book does not set it against distortion; LiveRAC pairs it with stretch-and-squish navigation [pp.280-281]
- [Constrained Navigation](../idioms/constrained-navigation.md) · ~771 words. **Use when** free camera motion risks lost or empty views: limit the zoom range, animate to a selected item, or drive navigation from a linked list view [pp.281-283]
- [Slice](../idioms/slice.md) · ~729 words. **Use when** one value of a dimension is chosen and only matching items are shown, such as one cross-section of a 3D scan, axis-aligned or arbitrary [pp.283-284]
- [HyperSlice](../idioms/hyperslice.md) · ~570 words. **Use when** a scalar function of many variables is explored through a matrix of linked orthogonal 2D slices [pp.284-285]
- [Cut](../idioms/cut.md) · ~569 words. **Use when** the interior of a 3D volume must be seen while keeping the 3D context behind a cutting plane [p.285]
- [Project](../idioms/project.md) · ~575 words. **Use when** all items stay visible but chosen dimensions are dropped (orthographic) or partly kept (perspective, map projections) [p.286]

## Disambiguation

- **Change over Time vs 11.3 Change View over Time.** Both cover section 11.3. Open the card to decide which aspect of a view to make changeable and whether it fits the data, such as reordering only categorical attributes; open the leaf when you need the worked examples (Tableau's encodings, LineUp's columns and alignments, the animated adjacency-matrix zoom) in full [pp.269-274].
- **LineUp vs Animated Transitions vs Change over Time.** LineUp is a system for reordering and realigning multi-attribute rankings; Animated Transitions is the idiom for showing any change smoothly, which LineUp also uses when alignment changes; Change over Time is the general choice of what to change [pp.271-274].
- **Geometric Zooming vs Semantic Zooming.** Geometric zooming keeps an object's appearance fixed and changes only its size; semantic zooming changes the representation itself as available pixels change [p.280].
- **Constrained Navigation vs Geometric Zooming vs Semantic Zooming.** Zooming types say how items are drawn as the camera moves; constrained navigation limits where the camera may go, and can be combined with either [pp.280-282].
- **11.5 Navigate: Changing Viewpoint vs 11.6 Navigate: Reducing Attributes.** 11.5 moves a camera over a fixed layout (zoom, pan, rotate); 11.6 uses the same camera intuition to remove dimensions [pp.279-283].
- **Slice vs Cut vs Project vs HyperSlice.** Slice keeps only items at one value of a dimension; cut hides everything on the near side of a plane but keeps the 3D context behind it; project keeps every item but drops dimensions; HyperSlice is a system applying slices to many-variable abstract data [pp.283-286].
- **11.4 Select Elements vs Animated Transitions vs Constrained Navigation.** Choose 11.4 to decide what the user can pick, how many, and how the pick is highlighted [pp.274-278]; Animated Transitions to decide how any change between two states is shown, whatever triggered it [p.273]; Constrained Navigation to decide where the camera may go, such as a bounded zoom range or a computed path to frame an item [p.282].

## Related

- [6.5 Eyes Beat Memory](../ch06-rules-thumb/s06-05-eyes-beat-memory.md): the strengths and weaknesses of animation [p.273]
- [6.8 Responsiveness Is Required](../ch06-rules-thumb/s06-08-responsiveness-required.md): timing requirements for selection feedback [p.276]
- [7.5 Separate, Order, and Align: Categorical Regions](../ch07-arrange-tables/s07-05-separate-order-align-categorical/node.md): ordering regions that hold categorical data, which reordering changes [p.271]
- [12 Facet into Multiple Views](../ch12-facet-into-multiple-views/node.md): faceting into juxtaposed views or superimposed layers, another option for handling complexity [p.269]
- [13 Reduce Items and Attributes](../ch13-reduce-items-attributes/node.md): filtering and aggregation, which change over time often drives and navigation often amounts to [p.273] [p.280]
- [14 Embed: Focus+Context](../ch14-embed-focus-context/node.md): focus+context approaches such as stretch-and-squish navigation [p.281]
- [3 Why: Task Abstraction](../ch03-why-task-abstraction/node.md): deriving new data, the remaining option for handling complexity [p.269]
- [8.4 Scalar Fields: One Value](../ch08-arrange-spatial-data/s08-04-scalar-fields-one-value/node.md): sampling and interpolation questions raised by arbitrary slices [p.283]
