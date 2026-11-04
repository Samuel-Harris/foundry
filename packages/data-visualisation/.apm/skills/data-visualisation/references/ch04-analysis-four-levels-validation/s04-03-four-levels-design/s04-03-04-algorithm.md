---
id: s04.03.04
kind: subsection-leaf
title: "Algorithm"
pdf_pages: [97, 98]
printed_pages: [72, 73]
toc: [s04.03.04]
fidelity: mixed
---

# 4.3.4 Algorithm

The innermost level covers the design of an algorithm, a detailed procedure that lets a computer carry out a goal automatically; here the goal is to handle the chosen encoding and interaction idioms efficiently. Algorithm blocks are designed, not just identified [p.97].

Many algorithms can instantiate the same idiom. Direct volume rendering, an idiom for making images from a three-dimensional field such as medical MRI scans, has been achieved by ray casting, splatting and texture mapping [pp.97-98]. They can be compared on speed of computation, memory required, and whether the image exactly matches the specified idiom or only approximates it [p.98].

<!-- verbatim p.98 -->
> The nested model emphasizes separating algorithm design, where your primary concerns are about computational issues, from idiom design, where your primary concerns are about human perceptual issues.
<!-- /verbatim -->

The levels still interact. A design that must change dynamically as the user moves the mouse may be infeasible if computing it takes minutes or hours instead of a fraction of a second; clever algorithm design, such as precomputing data that supports a fast enough response, can save it [p.98].

## Figures

## Related

- [4.3.3 Visual Encoding and Interaction Idiom](s04-03-03-visual-encoding-interaction-idiom.md): the idioms an algorithm instantiates, judged on perception rather than computation [p.98]
- [4.6.4 Algorithm Validation](../s04-06-validation-approaches/s04-06-04-algorithm-validation.md): complexity analysis, timings and correctness [p.98]
- [6.8 Responsiveness Is Required](../../ch06-rules-thumb/s06-08-responsiveness-required.md): matching system latency to user expectations, the concern in the mouse-movement example [p.98]
