---
id: s04.03
kind: section-node
title: "Four Levels of Design"
pdf_pages: [92, 98]
printed_pages: [67, 73]
toc: [s04.03]
fidelity: summary
---

# 4.3 Four Levels of Design

The nested model splits vis design into four cascading levels so each concern can be analysed separately: domain situation, what–why abstraction, how idiom, and algorithm [pp.92-93]. The output of each upstream level is the input to the one below, and a wrong choice upstream cascades to every downstream level; a poor abstraction defeats even perfect idiom and algorithm choices [p.93]. Situation and task blocks are identified; data, idiom and algorithm blocks are designed [pp.94-97].

## Children

- [4.3.1 Domain Situation](s04-03-01-domain-situation.md) · ~683 words. **Use when** the question is who the target users are, what they actually ask of their data, and whether those needs were observed rather than assumed; also holds the nesting, blocks and cascade definitions [pp.92-95]
- [4.3.2 Task and Data Abstraction](s04-03-02-task-data-abstraction.md) · ~431 words. **Use when** a chart may be showing the wrong thing: domain questions not mapped to abstract tasks, data not transformed into a type that suits the task, or an abstraction made implicitly without justification [pp.95-96]
- [4.3.3 Visual Encoding and Interaction Idiom](s04-03-03-visual-encoding-interaction-idiom.md) · ~402 words. **Use when** judging how the data is drawn and manipulated, separating the encoding idiom (what users see) from the interaction idiom (how they change it), and ruling out idioms that mismatch the task [pp.96-97]
- [4.3.4 Algorithm](s04-03-04-algorithm.md) · ~240 words. **Use when** the concern is computation: speed, memory or exactness of the procedure that draws an idiom, or an interaction too slow to respond to the mouse [pp.97-98]

## Disambiguation

- **Task and Data Abstraction vs Visual Encoding and Interaction Idiom.** A chart that is well drawn but answers the wrong question fails at the abstraction level; one that shows the right data in a way people cannot read fails at the idiom level. Abstraction decides what to show and why; idiom decides how [pp.95-97].
- **Visual Encoding and Interaction Idiom vs Algorithm.** Idiom design is about human perception; algorithm design is about computation. Many algorithms can instantiate one idiom, and their trade-offs (speed, memory, exact versus approximate) belong to the algorithm level [pp.97-98].
- **Domain Situation vs Task and Data Abstraction.** Domain situation records the users' own questions in their own vocabulary; the abstraction level translates them into domain-independent tasks and data types [pp.94-95].

## Related

- [4.4 Angles of Attack](../s04-04-angles-attack.md): moving through these levels top down or bottom up [p.98]
- [4.5 Threats to Validity](../s04-05-threats-validity.md): the threat that applies at each of these levels [p.99]
- [3 Why: Task Abstraction](../../ch03-why-task-abstraction/node.md): abstract tasks in detail [p.95]
- [2 What: Data Abstraction](../../ch02-what-data-abstraction/node.md): abstract data types [p.96]
- [3.4.2.3 Derive](../../ch03-why-task-abstraction/s03-04-actions/s03-04-02-produce.md#s03.04.02.03): transforming and deriving data at the abstraction level [p.96]
- [5 Marks and Channels](../../ch05-marks-channels/node.md): perception principles for idiom choices [p.97]
- [6 Rules of Thumb](../../ch06-rules-thumb/node.md): perception and memory principles for idiom choices [p.97]
