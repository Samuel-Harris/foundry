---
id: s11.04.01
kind: subsection-leaf
title: "Selection Design Choices"
pdf_pages: [274, 276]
printed_pages: [249, 251]
toc: [s11.04.01]
fidelity: mixed
---

# 11.4.1 Selection Design Choices

## Why selection matters

<!-- verbatim p.274 -->
> Allowing users to select one or more elements of interest in a vis is a fundamental action that supports nearly every interactive idiom.
<!-- /verbatim -->

The output of a selection is often the input to a later operation; in particular, the change choice usually depends on a previous select result [p.274].

## What can be selected

- **Data items** are the most common target; **links** are another in network data [p.275].
- **Attributes** are selectable in some vis tools [p.275].
- **Levels within an attribute**, meaning all items that share a unique value for it, are commonly selectable [p.275].
- **Views** themselves can be targets when the data is faceted across multiple views [p.275].

## How many selection types

- The simplest case has one kind: elements are selected or not [p.275].
- Two kinds are common, for example a mouse click producing one and a hover, where the cursor passes over the object, producing another; multiple kinds of clicks are also common [p.275].
- **Hardware matters.** Mice give clicks and hovers easily, and several buttons give several clicks; a keyboard adds key presses; some touch screens provide hover information and others do not; hardware that supports multiple levels of proximity, such as "nearby" between hover and distant, is much rarer [p.275].

## How many elements in the set

The book poses the questions: exactly one or many? Is zero acceptable? Is there a primary versus secondary selection? If many, only a spatially contiguous group, or adding and removing items over multiple passes [p.275]?

- **At most one.** For some tasks only one item is selected at a time, so a new choice replaces the old [p.275].
- **Empty allowed.** Occasionally the task requires a selected item at all times, but often the set can be empty; selection is then often a toggle, where one action such as a click switches between select and deselect [p.275].
- **Detail pane example.** A fixed-size view showing details of one selected item implies a detail selection set of at most one, and an empty set is handled by leaving the pane blank [pp.275-276].
- **Many.** When many items may be selected, there must be actions to add items, remove items and clear the set [p.276].

## Groups as attributes

- **Example.** A tool lets users assign items to any of seven groups, rename groups and recolour their items [p.276].
- **Design choice.** In that situation it is good to move beyond selection types to a design that explicitly tracks group membership with attributes: one categorical attribute if an element belongs to only one group, or one attribute per group, recording membership, if it can belong to many [p.276].
- Straightforward selection can then pick a group as the current target and add or remove items [p.276].
- Most users find groups more natural than attribute levels, but designers can usefully think about the underlying attribute structure [p.276].

## Primary and secondary selection

Some tasks need a distinction between primary and secondary selection, for example path traversal in a directed graph from a source to a target node; some tasks need one item in each set, others multi-item sets for one or both [p.276].

## Figures

## Related

- [11.4.2 Highlighting](s11-04-02-highlighting.md): how the selected set is shown, a separate choice [p.276]
- [11.4.3 Selection Outcomes](s11-04-03-selection-outcomes.md): what the selected set feeds into next [p.274]
- [12 Facet into Multiple Views](../../ch12-facet-into-multiple-views/node.md): multiple views, where a view can be a target [p.275]
