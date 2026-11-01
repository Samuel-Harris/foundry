---
id: ch01
kind: chapter-node
title: "What’s Vis, and Why Do It?"
pdf_pages: [26, 44]
printed_pages: [1, 19]
toc: [ch01]
fidelity: summary
---

# 1 What’s Vis, and Why Do It?

The book's definition of vis and the rationale behind each part of it, posed as a series of "why" questions: why keep a human and a computer in the loop, why rely on vision, detail and interaction, why the idiom design space is huge, why tasks and effectiveness matter, why most designs fail and validation is hard, why resources are limited, and why analyse existing systems with the what–why–how framework [pp.26-27]. It is orientation for the whole book rather than guidance on any one idiom; the later chapters hold the detailed design choices [pp.42-43].

## Children

- [1.1 The Big Picture](s01-01-big-picture.md) · ~370 words. **Use when** you only need to state what vis is or when it suits a problem, in the book's own words, without the argument behind each claim: the verbatim definition (visual representations of datasets that help people carry out tasks more effectively) and the chapter summary (augment rather than replace people, a huge design space where most choices are ineffective, three kinds of resource limits, analysis by why, what and how) [p.26]
- [1.2 Why Have a Human in the Loop?](s01-02-why-have-human-loop.md) · ~615 words. **Use when** deciding whether a problem needs vis at all or a fully automatic computational solution, or which transitional, long-term or presentation use a tool serves [pp.27-29]
- [1.3 Why Have a Computer in the Loop?](s01-03-why-have-computer-loop.md) · ~392 words. **Use when** arguing for automatic rather than hand-drawn layout: datasets of hundreds to millions of items, or data that changes over time [pp.29-31]
- [1.4 Why Use an External Representation?](s01-04-why-use-external-representation.md) · ~259 words. **Use when** explaining how diagrams offload cognition and memory to perception, and how spatial grouping speeds search and recognition or misleads when nonoptimal [p.31]
- [1.5 Why Depend on Vision?](s01-05-why-depend-vision.md) · ~307 words. **Use when** asked why sound, touch, taste or smell are not used instead of sight; covers bandwidth, parallel preconscious processing and popout [pp.31-32]
- [1.6 Why Show the Data in Detail?](s01-06-why-show-data-detail.md) · ~353 words. **Use when** justifying plotting raw items instead of reporting summary statistics, or checking whether a statistical model fits; Anscombe's Quartet [pp.32-34]
- [1.7 Why Use Interactivity?](s01-07-why-use-interactivity.md) · ~249 words. **Use when** a dataset is too large or complex to show at once in one static view and you must justify changing the view in response to user actions [p.34]
- [1.8 Why Is the Vis Idiom Design Space Huge?](s01-08-why-vis-idiom-design.md) · ~369 words. **Use when** you need the book's definition of an idiom, or the design choices it uses to organise the space: spatial encoding, faceting into views, filtering and aggregation [pp.35-36]
- [1.9 Why Focus on Tasks?](s01-09-why-focus-tasks.md) · ~185 words. **Use when** the same dataset needs different tools for different users, and you must reframe a domain-specific task abstractly: presentation, discovery, enjoyment or producing information [p.36]
- [1.10 Why Focus on Effectiveness?](s01-10-why-focus-effectiveness.md) · ~273 words. **Use when** weighing beauty, narrative or persuasion against correctness and accuracy, or explaining why any depiction is an abstraction that emphasises some aspects [pp.36-37]
- [1.11 Why Are Most Designs Ineffective?](s01-11-why-most-designs-ineffective.md) · ~482 words. **Use when** planning how to search for a design: satisfy rather than optimise, widen the consideration space and generate several alternatives in parallel [pp.37-39]
- [1.12 Why Is Validation Difficult?](s01-12-why-validation-difficult.md) · ~294 words. **Use when** listing the open questions in judging whether a design works: what better means, compared with what, for which task, user and benchmark data [p.39]
- [1.13 Why Are There Resource Limitations?](s01-13-why-there-resource-limitations.md) · ~665 words. **Use when** a design must respect computer time and memory, human memory and attention, or screen pixels; covers scalability, change blindness and information density [pp.39-41]
- [1.14 Why Analyze?](s01-14-why-analyze.md) · ~464 words. **Use when** breaking an existing or proposed system into what data, why task and how idiom, or chaining several such instances to separate means from ends [pp.41-43]
- [1.15 Further Reading](s01-15-further-reading.md) · ~236 words. **Use when** you need a source to cite or read further on why diagrams work as external memory (Larkin and Simon, Zhang), why to show raw data rather than summary statistics (Anscombe, Cleveland and McGill), how to move from loose to crisp user requirements in a design study (Sedlmair et al.), or human perception, memory, change blindness and graphic density limits (Ware, Simons, Bertin, Tufte) [p.44]

## Disambiguation

- **Why Have a Human in the Loop vs Why Have a Computer in the Loop.** 1.2 asks whether people must stay in the decision loop at all, versus full automation; 1.3 asks why the drawing should be generated by computer rather than by hand [pp.27-31].
- **Why Use an External Representation vs Why Depend on Vision.** 1.4 covers diagrams as external memory organised by spatial location; 1.5 covers why the visual channel beats other senses [pp.31-32].
- **Why Show the Data in Detail vs Why Use Interactivity vs Why Are There Resource Limitations.** 1.6 argues for showing structure rather than summaries; 1.7 argues for changing views when everything cannot be shown at once; 1.13 names the computational, human and display limits and the information density trade-off behind both [pp.32-41].
- **Why Focus on Tasks vs Why Focus on Effectiveness.** Go to 1.9 when the question is why the same dataset needs different tools for different tasks, or how to restate a domain task abstractly; go to 1.10 when it is why correctness and accuracy outrank beauty, narrative or persuasion, or why every depiction emphasises some aspects over others [pp.36-37].
- **Why Have a Human in the Loop vs Why Focus on Tasks.** Both mention presentation and discovery. 1.2 classifies tools by whether the human is meant to be replaced (early, middle and late transitional use, long-term use, presentation); 1.9 lists abstract task goals (present, discover, enjoy, produce) and splits discovery into generating versus confirming hypotheses [pp.28-29] [p.36].
- **Why Is the Vis Idiom Design Space Huge vs Why Are Most Designs Ineffective vs Why Analyze.** 1.8 defines idioms and the size of the space; 1.11 explains how to search it; 1.14 gives the what–why–how framework that structures it [pp.35-43].
- **Why Are Most Designs Ineffective vs Why Is Validation Difficult.** 1.11 is about choosing among alternatives during design; 1.12 is about the questions in judging afterwards whether a design met its goals [pp.37-39].

## Related

- [2 What: Data Abstraction](../ch02-what-data-abstraction/node.md): the question of what data is shown, from the analysis framework [p.42]
- [3 Why: Task Abstraction](../ch03-why-task-abstraction/node.md): the space of task abstractions, the question of why [p.36] [p.42]
- [4 Analysis: Four Levels for Validation](../ch04-analysis-four-levels-validation/node.md): the four-level design model for trade-offs and the framework for when to use which validation methods [pp.38-39]
- [5 Marks and Channels](../ch05-marks-channels/node.md): implications of visual perception for vis design [p.32]
- [6.5 Eyes Beat Memory](../ch06-rules-thumb/s06-05-eyes-beat-memory.md): further aspects of memory and attention [p.40]
- [9.5 Containment: Hierarchy Marks](../ch09-arrange-networks-trees/s09-05-containment-hierarchy-marks.md): compound networks such as the one in the Grouse example [p.36]
- [7 Arrange Tables](../ch07-arrange-tables/node.md): the first of Chapters 7 to 14, which answer the question of how idioms are designed [p.42]
