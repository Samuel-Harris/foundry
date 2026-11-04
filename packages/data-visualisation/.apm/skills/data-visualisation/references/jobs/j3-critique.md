---
id: j3
kind: job-node
title: "J3 Critique a Visualisation"
pdf_pages: [91, 362]
printed_pages: [66, 337]
toc: []
fidelity: summary
---

# J3 Critique a Visualisation

The route for reviewing or improving an existing chart, dashboard or tool. First say at which of the four nested levels it fails, since errors cascade downstream and each level has its own threat and evidence [pp.92-93] [pp.99-100]. Then check the idiom against the perceptual and cognitive principles of chapters 5 and 6, the book's immediate idiom-level validation [p.103] [pp.141-142]. Children are grouped by complaint.

[NOT FROM BOOK] The book does not discuss dual-axis charts; no file here covers them.

## Children

### Where it fails

- [4.5 Threats to Validity](../ch04-analysis-four-levels-validation/s04-05-threats-validity.md) · ~291 words. **Use when** naming the kind of failure: misunderstood users, the wrong data or task shown, an encoding that does not work, or code that is too slow [pp.99-100]
- [4.3 Four Levels of Design](../ch04-analysis-four-levels-validation/s04-03-four-levels-design/node.md) · ~460 words. **Use when** placing a flaw at one level and tracing how it cascades, for example a fine chart of the wrong abstraction [pp.92-98]

### Is the evidence enough?

- [4.6.1 Domain Validation](../ch04-analysis-four-levels-validation/s04-06-validation-approaches/s04-06-01-domain-validation.md) · ~757 words. **Use when** the evidence is interviews or observation of target users, or adoption rates: do they really have the claimed problem? [pp.102-103]
- [4.6.2 Abstraction Validation](../ch04-analysis-four-levels-validation/s04-06-validation-approaches/s04-06-02-abstraction-validation.md) · ~296 words. **Use when** the evidence is target users trying the tool on their own work: anecdotes of insights found, or a field study after deployment [p.103]
- [4.6.3 Idiom Validation](../ch04-analysis-four-levels-validation/s04-06-validation-approaches/s04-06-03-idiom-validation.md) · ~620 words. **Use when** arguing whether an encoding works: perceptual justification, expert review, lab studies (time, errors, preferences), result images; also why usability studies are not validation [pp.103-105]
- [4.6.4 Algorithm Validation](../ch04-analysis-four-levels-validation/s04-06-validation-approaches/s04-06-04-algorithm-validation.md) · ~291 words. **Use when** the evidence is timings, memory use or complexity analysis, or the output may be incorrect [pp.105-106]
- [4.6.5 Mismatches](../ch04-analysis-four-levels-validation/s04-06-validation-approaches/s04-06-05-mismatches.md) · ~195 words. **Use when** a design's claimed benefit is backed by evidence from a different level, such as encoding claims argued from timings [p.106]
- [4.7 Validation Examples](../ch04-analysis-four-levels-validation/s04-07-validation-examples/node.md) · ~477 words. **Use when** you want a worked analysis of a published system to model the critique's structure on [pp.106-116]

### Rules of thumb, including 3D

- [6.1 The Big Picture](../ch06-rules-thumb/s06-01-big-picture.md) · ~271 words. **Use when** you want all eight rules of thumb as one checklist before reading the ones a design breaks [pp.141-142]
- [6.3 No Unjustified 3D](../ch06-rules-thumb/s06-03-no-unjustified-3d/node.md) · ~799 words. **Use when** the design shows non-spatial data in depth (3D bars, scatter, landscapes, tilted labels) with the arguments and the cases justifying 3D [pp.142-155]
- [6.3.4 Perspective Distortion Dangers](../ch06-rules-thumb/s06-03-no-unjustified-3d/s06-03-04-perspective-distortion-dangers.md) · ~371 words. **Use when** the specific complaint is that perspective makes bar heights or sizes impossible to compare, as in a 3D bar chart [pp.146-147]
- [6.4 No Unjustified 2D](../ch06-rules-thumb/s06-04-no-unjustified-2d.md) · ~240 words. **Use when** a 2D layout such as a node–link graph is used where a sorted 1D list would serve a lookup task better [p.156]
- [6.5 Eyes Beat Memory](../ch06-rules-thumb/s06-05-eyes-beat-memory.md) · ~866 words. **Use when** viewers must remember earlier frames or states: animation for comparison, navigation without overview, change blindness [pp.156-159]
- [6.7 Overview First, Zoom and Filter, Details on Demand](../ch06-rules-thumb/s06-07-overview-first-zoom-filter.md) · ~559 words. **Use when** a large-data design has no overview, or no path from overview to detail [pp.160-162]
- [6.8 Responsiveness Is Required](../ch06-rules-thumb/s06-08-responsiveness-required.md) · ~875 words. **Use when** interaction feels slow or gives no feedback, judged against the 0.1, 1 and 10 second latency classes [pp.162-165]
- [6.9 Get It Right in Black and White](../ch06-rules-thumb/s06-09-get-right-black-white.md) · ~175 words. **Use when** the most important attribute is carried by hue or saturation rather than luminance, so it may be illegible in black and white [p.165]
- [6.10 Function First, Form Next](../ch06-rules-thumb/s06-10-function-first-form-next.md) · ~285 words. **Use when** a design is attractive but ineffective, or a critique must decide between polishing and redesigning [pp.165-166]

### Channels and layout

- [5.4 Using Marks and Channels](../ch05-marks-channels/s05-04-using-marks-channels.md) · ~1,117 words. **Use when** checking expressiveness (does a channel imply order the data lacks?) and effectiveness (does the most important attribute get the best channel?) [pp.124-128]
- [5.5 Channel Effectiveness](../ch05-marks-channels/s05-05-channel-effectiveness/node.md) · ~495 words. **Use when** a specific encoding is hard to read: too many levels, interfering channel pairs, a target that does not pop out, or weak grouping [pp.128-137]
- [5.6 Relative versus Absolute Judgements](../ch05-marks-channels/s05-06-relative-absolute-judgements.md) · ~607 words. **Use when** lengths lack a common baseline, or the same colour reads differently against different backgrounds [pp.137-139]
- [7.6.3 Radial Layouts](../ch07-arrange-tables/s07-06-spatial-axis-orientation/s07-06-03-radial-layouts.md) · ~1,097 words. **Use when** critiquing a pie, polar area or other radial chart against a bar chart of the same data [pp.191-196]

### Too many items: overplotting and hidden data

- [13.2 Why Reduce?](../ch13-reduce-items-attributes/s13-02-why-reduce.md) · ~436 words. **Use when** a design hides data and the critique weighs filtering (out of sight is out of mind) against aggregation (somewhat safer, never complete) [pp.324-325]
- [Continuous Scatterplots](../idioms/continuous-scatterplots.md) · ~560 words. **Use when** a scatterplot has so many points that dots pile up on the same location; colour shows density per pixel instead [pp.332-333]
- [13.4 Aggregate](../ch13-reduce-items-attributes/s13-04-aggregate/node.md) · ~745 words. **Use when** too many items crowd a view and a summary should replace them: histograms, boxplots, cluster levels, regions or reduced dimensions [pp.330-345]
- [13.3 Filter](../ch13-reduce-items-attributes/s13-03-filter/node.md) · ~431 words. **Use when** the fix is to remove items or attributes by range or similarity, as with slider-driven dynamic queries [pp.325-330]

### Colour

- [10.2.3 Luminance, Saturation, and Hue](../ch10-map-color-other-channels/s10-02-color-theory/s10-02-03-luminance-saturation-hue.md) · ~647 words. **Use when** a chart uses hue for ordered data, too many hues, or text without enough luminance contrast [pp.248-249]
- [10.3.1 Categorical Colormaps](../ch10-map-color-other-channels/s10-03-colormaps/s10-03-01-categorical-colormaps.md) · ~1,066 words. **Use when** a palette has more categories than can be told apart, or colours of different saturation on marks of different size [pp.251-254]
- [10.3.2 Ordered Colormaps](../ch10-map-color-other-channels/s10-03-colormaps/s10-03-02-ordered-colormaps.md) · ~880 words. **Use when** a rainbow or other non-monotonic ramp encodes ordered data, or a diverging map lacks a neutral midpoint colour [pp.254-259]
- [10.3.4 Colorblind-Safe Colormap Design](../ch10-map-color-other-channels/s10-03-colormaps/s10-03-04-colorblind-safe-colormap-design.md) · ~247 words. **Use when** the palette relies on red–green contrast alone [p.260]

### Focus+context

- [14.6 Costs and Benefits: Distortion](../ch14-embed-focus-context/s14-06-costs-benefits-distortion.md) · ~817 words. **Use when** critiquing a fisheye or other distorted view, where length judgements and object constancy suffer [pp.359-362]

## Disambiguation

- **Threats to Validity vs Four Levels of Design.** 4.5 names the failure; 4.3 places it and shows its cascade. Start with 4.5 when a critique has a symptom, 4.3 when it has a design decision [pp.93-100].
- **Domain Validation vs Abstraction Validation vs Idiom Validation vs Algorithm Validation vs Mismatches.** A "users liked it in a survey" claim reports preferences, a subjective measure [p.104]; place it by who answered and on what work. Real use without being asked is adoption (4.6.1). Target users reporting insights from their own work give anecdotal evidence for the abstraction (4.6.2). Preferences from a lab study on designer-chosen tasks bear on the idiom only, and an informal usability study is not validation (4.6.3). Timings are algorithm evidence (4.6.4). Use 4.6.5 when the evidence's level differs from the claim's [pp.102-106].
- **Idiom Validation vs Validation Examples.** 4.6.3 lists evidence for idiom claims; 4.7 analyses published papers by level and method [pp.103-116].
- **The Big Picture vs No Unjustified 3D vs Perspective Distortion Dangers vs Radial Layouts.** 6.1 is the checklist; 6.3 the whole 3D argument; 6.3.4 the leaf for a 3D bar chart [pp.141-147]. The book never discusses a 3D pie; join 6.3.4 (perspective interferes with planar position and size [p.147]) with 7.6.3 (a flat pie's angle and area are already less accurate than bars [p.193]).
- **No Unjustified 3D vs No Unjustified 2D.** 6.3 weighs depth against the plane; 6.4 weighs a 2D layout against a 1D list [p.143] [p.156].
- **Perspective Distortion Dangers vs Costs and Benefits: Distortion.** 6.3.4 is the foreshortening of a 3D view; 14.6 is the deliberate distortion of focus+context views [pp.146-147] [pp.359-362].
- **Eyes Beat Memory vs Overview First, Zoom and Filter, Details on Demand vs Responsiveness Is Required.** 6.5 is about memory load and animation; 6.7 about how overviews and details connect; 6.8 about latency [pp.156-165].
- **Using Marks and Channels vs Channel Effectiveness vs Relative versus Absolute Judgements.** 5.4 checks the channel choice; 5.5 the channel's limits; 5.6 the frame or baseline [pp.124-139].
- **Get It Right in Black and White vs Luminance, Saturation, and Hue.** 6.9 is the rule; 10.2.3 explains which channel carries magnitude and how many levels each supports [p.165] [pp.248-249].
- **Categorical Colormaps vs Ordered Colormaps vs Colorblind-Safe Colormap Design.** Choose by the attribute type the colour encodes; check colour deficiency for either [pp.251-260].
- **Why Reduce? vs Continuous Scatterplots vs Aggregate vs Filter.** For overplotted points, Continuous Scatterplots is the direct fix; 13.4 holds the other summaries; 13.3 removes items instead; 13.2 weighs the two choices [pp.324-333].
- **Radial Layouts vs Using Marks and Channels.** 7.6.3 holds the pie-versus-bar evidence; 5.4 the general angle-versus-position ranking behind it [p.127] [pp.193-195].

## Related

- [1.12 Why Is Validation Difficult?](../ch01-whats-vis-why/s01-12-why-validation-difficult.md): the open questions any judgement of "better" must answer [p.39]
- [15.2 Why Analyze Case Studies?](../ch15-analysis-case-studies/s15-02-why-analyze-case-studies.md): the template a full analysis of a system follows [pp.366-367]
- [9.4 Costs and Benefits: Connection versus Matrix](../ch09-arrange-networks-trees/s09-04-costs-benefits-connection-matrix.md): critiquing a node–link or matrix choice for a network [pp.234-238]
