---
id: ch04
kind: chapter-node
title: "Analysis: Four Levels for Validation"
pdf_pages: [91, 118]
printed_pages: [66, 93]
toc: [ch04]
fidelity: summary
---

# 4 Analysis: Four Levels for Validation

The book's framework for judging whether a vis design succeeds. Design splits into four nested levels: domain situation, task and data abstraction, visual encoding and interaction idiom, and algorithm. A wrong choice upstream cascades to every level below it [pp.92-93]. Each level has its own threat to validity (wrong problem, wrong abstraction, wrong idiom, wrong algorithm) and its own validation methods, and considering each level separately helps sort the many questions about validating a design [pp.99-101]. A common problem in weak projects is validating at a different level from the one where the benefit is claimed [p.106]. Six research papers are analysed this way as worked examples [pp.106-116].

## Children

- [4.1 The Big Picture](s04-01-big-picture.md) · ~323 words. **Use when** you need the one-figure map that pairs each of the four levels with the validation methods suited to it, before choosing a method or a critique angle [pp.91-92]
- [4.2 Why Validate?](s04-02-why-validate.md) · ~182 words. **Use when** justifying why validation must be planned from the start of a design rather than added at the end, or why the book adds levels above and below what–why–how [p.92]
- [4.3 Four Levels of Design](s04-03-four-levels-design/node.md) · ~460 words. **Use when** locating a design decision or a flaw at one level (users and their questions, task and data abstraction, encoding and interaction, or computation), or explaining how an upstream error cascades downstream [pp.92-98]
- [4.4 Angles of Attack](s04-04-angles-attack.md) · ~475 words. **Use when** a design started from a user problem (problem-driven, design study) or from a new technique (technique-driven), and you need to check for skipped levels, such as jumping straight to idiom design on an unexamined abstraction [pp.98-99]
- [4.5 Threats to Validity](s04-05-threats-validity.md) · ~291 words. **Use when** critiquing a chart or tool and you must name the kind of failure: users' needs misunderstood, the wrong thing shown, the way it is shown does not work, or the code is too slow [pp.99-100]
- [4.6 Validation Approaches](s04-06-validation-approaches/node.md) · ~475 words. **Use when** choosing what evidence would show a design works at a given level (interviews, adoption, field study, lab study, image analysis, complexity, timings), or judging whether claimed evidence matches the level of the claim [pp.100-106]
- [4.7 Validation Examples](s04-07-validation-examples/node.md) · ~477 words. **Use when** you want a worked analysis of a real system by level and validation method, to model your own critique on (genealogical graphs, MatrixExplorer, flow maps, LiveRAC, LinLog, horizon graphs) [pp.106-116]
- [4.8 Further Reading](s04-08-further-reading.md) · ~374 words. **Use when** you need a citation the chapter only names: the original nested-model papers and McGrath on experimental methods; how to run a design study (nine stages, 32 pitfalls) or a MILC long-term case study; requirements elicitation for the abstraction level; algorithm textbooks and complexity analysis; HCI textbooks; surveys of evaluation methods and when to run user studies; contextual inquiry for field studies; experiment design and analysis for lab studies [pp.116-118]

## Disambiguation

- **The Big Picture vs Threats to Validity vs Validation Approaches.** 4.1 is the summary map (Figure 4.1); 4.5 names the one threat per level; 4.6 explains each validation method, immediate versus downstream timing, and level mismatches [pp.91-106].
- **Four Levels of Design vs Threats to Validity.** 4.3 says what each level decides and whether its blocks are identified or designed; 4.5 says what goes wrong at each level. Go to 4.3 to place a decision, 4.5 to name a failure [pp.93-100].
- **Four Levels of Design vs Angles of Attack.** 4.3 describes the levels themselves; 4.4 describes the order in which a project moves through them and the pitfall of skipping the domain and abstraction levels [pp.92-99].
- **Validation Approaches vs Validation Examples.** 4.6 describes the methods in general; 4.7 shows which methods six specific papers used and at which levels [pp.100-116].

## Related

- [1.12 Why Is Validation Difficult?](../ch01-whats-vis-why/s01-12-why-validation-difficult.md): the questions to consider when validating, which this chapter's levels organise [p.99]
- [1.11 Why Are Most Designs Ineffective?](../ch01-whats-vis-why/s01-11-why-most-designs-ineffective.md): the huge design space that makes validation necessary [p.92]
- [3 Why: Task Abstraction](../ch03-why-task-abstraction/node.md): the abstract tasks used at the abstraction level [p.95]
- [2 What: Data Abstraction](../ch02-what-data-abstraction/node.md): the abstract data types chosen at the abstraction level [p.96]
- [6 Rules of Thumb](../ch06-rules-thumb/node.md): perceptual and cognitive principles used to justify and validate idiom choices [p.103]
- [5 Marks and Channels](../ch05-marks-channels/node.md): perception principles behind idiom-level justification [p.103]
- [15 Analysis Case Studies](../ch15-analysis-case-studies/node.md): further systems analysed in the book's framework; the book says chapters 7 to 14 cover the idiom design space [p.96]
