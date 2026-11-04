---
id: s02.04.03
kind: subsection-leaf
title: "Fields"
pdf_pages: [52, 54]
printed_pages: [27, 29]
toc: [s02.04.03, s02.04.03.01, s02.04.03.02]
fidelity: mixed
---

# 2.4.3 Fields

## Continuous data in cells

<!-- verbatim p.52 -->
> Each cell in a field contains measurements or calculations from a continuous domain: there are conceptually infinitely many values that you might measure, so you could always take a new measurement between any two existing ones.
<!-- /verbatim -->

- **Examples of continuous phenomena.** Temperature, pressure, speed, force and density, measured or simulated; mathematical functions can also be continuous [p.52].
- **Worked example.** A medical scan measuring tissue density at sample points spread regularly through a 3D volume; a low-resolution scan has 262,144 cells, 64 bins in each direction, each cell tied to a region of space. A finer or coarser grid places measurements closer together or further apart [p.52].
- **Sampling and interpolation.** Continuous data needs careful treatment of sampling (how often to measure) and interpolation (how to show values between samples without misleading). Appropriate interpolation lets you reconstruct a faithful view from an arbitrary viewpoint; these problems are studied in areas such as signal processing and statistics [pp.52-53].
- **Contrast with tables and networks.** Tables and networks are discrete data: a finite number of individual items exist and interpolation between them is not meaningful; where a mathematical framework is necessary, areas such as graph theory and combinatorics provide relevant ideas [p.53].
- **Terminology.** The book's "field" is related to, but not identical with, the mathematical mapping from a domain to a range; used without an adjective it emphasises the continuous domain rather than whether the range holds scalars, vectors or tensors [p.52].
- **Discrete storage.** All data in a computer is technically discrete; the question is whether the stored bits represent samples of a continuous phenomenon or intrinsically discrete data [p.53].

<a id="s02.04.03.01"></a>

### 2.4.3.1 Spatial Fields

<!-- verbatim p.53 -->
> Continuous data is often found in the form of a spatial field, where the cell structure of the field is based on sampling at spatial positions. Most datasets that contain inherently spatial data occur in the context of tasks that require understanding aspects of its spatial structure, especially shape.
<!-- /verbatim -->

- **Medical imaging.** The task could be to locate suspected tumours by shape or density; an obvious encoding shows something that looks like an X-ray of the body and uses colour coding to highlight suspected tumours [p.53].
- **Wind tunnel.** Temperature and pressure of air flowing over wings, with the task of comparing flow patterns across regions; one encoding uses the wing's geometry as the spatial substrate and shows the values with size-coded arrows [p.53].
- **Design consequence.** Users' likely tasks on spatial field data constrain many choices about the use of space, and many choices for nonspatial data (also called abstract data) are unsuitable [p.53].

<!-- verbatim p.54 -->
> Thus, the question of whether a dataset has the type of a spatial field or a nonspatial table has extensive and far-reaching implications for idiom design.
<!-- /verbatim -->

- **Scivis.** Scientific visualisation concerns situations where spatial position is given with the dataset; a central concern is handling continuous data within signal processing [p.54].
- **Infovis.** Information visualisation concerns situations where the designer chooses the use of space; a central concern is whether the chosen idiom suits the combination of data and task, drawing on human–computer interaction and design [p.54].

<a id="s02.04.03.02"></a>

### 2.4.3.2 Grid Types

| Grid | What is stored | Use | Cite |
| --- | --- | --- | --- |
| Uniform | Neither grid geometry nor topology needs storing | Sampling at completely regular intervals | [p.54] |
| Rectilinear | Some geometric location information for each row | Nonuniform sampling; efficient where complexity is high in some areas and low in others | [p.54] |
| Structured | The geometric location of each cell | Curvilinear shapes | [p.54] |
| Unstructured | Spatial positions plus explicit topology of how cells connect | Complete flexibility | [p.54] |

## Figures

## Related

- [8 Arrange Spatial Data](../../ch08-arrange-spatial-data/node.md): idioms for spatial fields, where spatial position is given [p.54]
- [2.6.1 Key versus Value Semantics](../s02-06-semantics/s02-06-01-key-value-semantics.md): keys and values in fields, and scalar, vector and tensor fields [p.52]
- [2.4.4 Geometry](s02-04-04-geometry.md): the other intrinsically spatial dataset type, also tied to shape understanding [p.53]
