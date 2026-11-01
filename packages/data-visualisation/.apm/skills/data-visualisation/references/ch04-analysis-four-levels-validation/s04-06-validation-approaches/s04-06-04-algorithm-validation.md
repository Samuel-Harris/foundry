---
id: s04.06.04
kind: subsection-leaf
title: "Algorithm Validation"
pdf_pages: [105, 106]
printed_pages: [80, 81]
toc: [s04.06.04]
fidelity: mixed
---

# 4.6.4 Algorithm Validation

## Threat: slow or memory-hungry algorithm

The primary threat is that the algorithm is suboptimal in time or memory, either against a theoretical minimum or against previously proposed algorithms. Poor time performance is a problem if the user expects a response in milliseconds and the operation takes hours or days [p.105].

**Immediate.** Analyse the algorithm's computational complexity with the standard computer science approaches. Complexity is usually analysed in terms of the number of items in the dataset, but sometimes the number of pixels in the display is more appropriate [p.105].

**Downstream.** Measure the wall-clock time and memory of the implemented algorithm; this is so common it is nearly mandatory for papers claiming an algorithm contribution [p.105]. The primary consideration is typically scalability, how dataset size affects speed. Choosing test data is tricky: consider matching standard benchmarks used in previous papers and using a sufficiently broad set of data [p.105].

## Threat: incorrect algorithm

Another threat is that the implementation does not meet the specification from the idiom level, through poor algorithm design or ordinary bugs. Establishing a program's correctness is notoriously difficult, whether by careful testing or formal methods [p.105].

<!-- verbatim p.106 -->
> The threat of algorithm incorrectness is often addressed implicitly rather than explicitly within the vis literature.
<!-- /verbatim -->

Presenting still images or videos from the implemented algorithm is one implicit validation, letting readers see that correctness objectives are met; explicit qualitative discussion of why the images show correctness is less common [p.106].

## Figures

## Related

- [6.8 Responsiveness Is Required](../../ch06-rules-thumb/s06-08-responsiveness-required.md): matching system latency to user expectations [p.105]
- [4.3.4 Algorithm](../s04-03-four-levels-design/s04-03-04-algorithm.md): what the algorithm level designs [p.105]
- [4.7.3 Flow Maps](../s04-07-validation-examples/s04-07-03-flow-maps.md): complexity analysis, timings and result images used for correctness [p.105]
