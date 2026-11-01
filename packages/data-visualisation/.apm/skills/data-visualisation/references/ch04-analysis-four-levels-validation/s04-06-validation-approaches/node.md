---
id: s04.06
kind: section-node
title: "Validation Approaches"
pdf_pages: [100, 106]
printed_pages: [75, 81]
toc: [s04.06]
fidelity: summary
---

# 4.6 Validation Approaches

Different threats need very different validation approaches; Figure 4.5 summarises the threat and methods at each level [p.100]. Methods are immediate (possible at that level) or downstream (needing results from the inner levels), and immediate methods alone never suffice to show a threat has been addressed [pp.101-102]. A common weakness is validating at a different level from the claimed benefit [p.106].

## Children

- [4.6.1 Domain Validation](s04-06-01-domain-validation.md) · ~757 words. **Use when** checking that the target users really have the problem claimed (interviews, field study, contextual inquiry, adoption rates); also holds the immediate versus downstream distinction and the Figure 4.5 table of every level's methods [pp.100-103]
- [4.6.2 Abstraction Validation](s04-06-02-abstraction-validation.md) · ~296 words. **Use when** checking that the chosen tasks and data actually help users with their own work: anecdotal evidence from a target user, insights found, or a field study of the deployed tool [p.103]
- [4.6.3 Idiom Validation](s04-06-03-idiom-validation.md) · ~620 words. **Use when** critiquing whether an encoding or interaction communicates the data: justify against perceptual principles, heuristic evaluation or expert review, lab studies of time and error, result-image discussion, quality metrics; also why usability studies are not validation [pp.103-105]
- [4.6.4 Algorithm Validation](s04-06-04-algorithm-validation.md) · ~291 words. **Use when** the question is whether the code is fast enough or correct: complexity analysis, wall-clock time and memory benchmarks, choice of test data, implementation bugs [pp.105-106]
- [4.6.5 Mismatches](s04-06-05-mismatches.md) · ~195 words. **Use when** a claimed benefit and its evidence sit at different levels, for example an encoding benefit argued from algorithm timings or a task characterisation tested in a lab study with designer-chosen tasks [p.106]

## Disambiguation

- **Domain Validation vs Abstraction Validation.** Both use field studies. At the domain level the field study documents users' existing work practices; at the abstraction level it observes how their behaviour changes after the tool is deployed [pp.102-103].
- **Abstraction Validation vs Idiom Validation.** Abstraction validation needs target users doing their own work; a lab study, where designers choose the abstract tasks, validates idioms only [pp.103-104].
- **Idiom Validation vs Algorithm Validation.** Both cite still images or video. For idioms, result images show the encoding's desirable properties; for algorithms they serve as implicit evidence of correctness [pp.104-106].
- **Mismatches vs Domain Validation vs Abstraction Validation vs Idiom Validation vs Algorithm Validation.** The level children say which methods fit each level; Mismatches is the check that a given claim and its evidence are at the same level [p.106].

## Related

- [4.5 Threats to Validity](../s04-05-threats-validity.md): the threat each method addresses [p.100]
- [4.7 Validation Examples](../s04-07-validation-examples/node.md): these methods applied to six real papers [p.106]
- [4.8 Further Reading](../s04-08-further-reading.md): fuller treatments of each method, which this section only outlines [p.101]
- [6.8 Responsiveness Is Required](../../ch06-rules-thumb/s06-08-responsiveness-required.md): matching system latency to user expectations [p.105]
- [6 Rules of Thumb](../../ch06-rules-thumb/node.md): the perceptual and cognitive principles idiom justification relies on [p.103]
