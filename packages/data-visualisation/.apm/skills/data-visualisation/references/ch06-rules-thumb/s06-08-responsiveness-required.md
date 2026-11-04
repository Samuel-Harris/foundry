---
id: s06.08
kind: section-leaf
title: "Responsiveness Is Required"
pdf_pages: [162, 165]
printed_pages: [137, 140]
toc: [s06.08, s06.08.01, s06.08.02, s06.08.03]
fidelity: mixed
---

# 6.8 Responsiveness Is Required

## The rule

<!-- verbatim p.162 -->
> The latency of interaction, namely, how much time it takes for the system to respond to the user action, matters immensely for interaction design.
<!-- /verbatim -->

Reaction to latency is not a continuum of rising irritation; it is best modelled as discrete categories, each with its own time constant [p.162].

<!-- verbatim p.162 -->
> A system will feel responsive if these latency classes are taken into account by providing feedback to the user within the relevant time scale.
<!-- /verbatim -->

## Latency classes (Table 6.1)

| Time constant | Value (seconds) | Relevant for |
| --- | --- | --- |
| perceptual processing | 0.1 | screen updates [p.162] |
| immediate response | 1 | visual feedback such as showing a clicked selection, and the length of an animated transition between layouts [p.162] |
| brief tasks | 10 | breaking complex tasks into simpler pieces; a good granularity for the smallest piece is this brief task time [pp.162-163] |

Table 6.1's caption, which credits Card et al. [p.162]:

<!-- verbatim p.162 -->
> Human response to interaction latency changes dramatically at these time thresholds.
<!-- /verbatim -->

## Subsections

<a id="s06.08.01"></a>

### 6.8.1 Visual Feedback

- **What latency is.** From the user's view, the time between their action and feedback that the operation has completed; in vis this feedback would most naturally be a visual indication of state change in the system itself, rather than cumbersome console status messages or popup confirmation dialogs that would interfere with the flow of exploration [p.163].
- **Always confirm.** The user should get confirmation that an action completed rather than wondering whether it is still running or never started, for example because they clicked the background instead of the target. Highlighting a selected item is a good confirmation; in navigation, the newly drawn frame is the feedback [p.163].
- **Timing.** Visual feedback should typically fall within the immediate response class, around one second [p.163].
- **Progress indicators.** If an action could take significantly longer than the user would expect, show a progress indicator [p.163].

<!-- verbatim p.163 -->
> A good rule of thumb for significantly longer is crossing from one latency class into another, as shown in Table 6.1.
<!-- /verbatim -->

<a id="s06.08.02"></a>

### 6.8.2 Latency and Interaction Design

<!-- verbatim p.163 -->
> Successful interaction design for a vis system depends on having a good match between the latencies of the low-level interaction mechanism, the visual feedback mechanism, the system update time, and the cognitive load of operation itself.
<!-- /verbatim -->

Worked through for seeing more detail about an item [pp.163-164]:

- **Interaction mechanism.** Clicking is slowest (move, stop on target, press). Mouseover hover with a dwell time may or may not be faster, depending on the dwell. Mouseover with no dwell, triggered by the cursor crossing the object, is fastest [pp.163-164].
- **Feedback: fixed detail pane.** The eyes must move to the side of the screen, so latency for using the feedback is relatively high; but much detail can be shown without occluding the main display [p.164].
- **Feedback: popup at the cursor.** Faster, since the eyes stay on the cursor, but it can occlude other objects, a visual encoding cost [p.164].
- **Feedback: highlight in the view.** A visual highlight change directly in the view, such as recolouring all graph neighbours one hop from the node under the cursor [p.164].
- **System update time.** Negligible for tiny local datasets. For larger ones, redrawing the whole view can take considerable time unless rendering guarantees a frame rate; partial updates without full redraws are possible but most graphics systems do not offer them by default, so guaranteeing immediate response can need significant algorithmic attention. Distributed data may need a client-server round trip of several seconds on a congested network [p.164].

When all these latencies match, users interact fluidly and stay focused on high-level goals such as building a mental model of the data; a mismatch jars them out of a state of flow by forcing them to wait [p.164].

<a id="s06.08.03"></a>

### 6.8.3 Interactivity Costs

<!-- verbatim p.165 -->
> Interactivity has both power and cost. The benefit of interaction is that people can explore a larger information space than can be understood in a single static image. However, a cost to interaction is that it requires human time and attention.
<!-- /verbatim -->

If the user must exhaustively check every possibility, the vis may degenerate into human-powered search [p.165]. Automatically detecting features of interest and bringing them to the user's attention through the encoding is a useful goal, yet a task fully solvable automatically would need no vis at all; there is always a trade-off between automating and relying on the human in the loop to detect patterns [p.165].

## Figures

## Related

- [11.4.2 Highlighting](../ch11-manipulate-view/s11-04-select-elements/s11-04-02-highlighting.md): highlighting as selection feedback [p.163]
- [6.5 Eyes Beat Memory](s06-05-eyes-beat-memory.md): when animated transitions help, the operations timed by the one-second class [p.162]
- [1.7 Why Use Interactivity?](../ch01-whats-vis-why/s01-07-why-use-interactivity.md): the power of interaction that this section weighs against its cost [p.165]
- [1.3 Why Have a Computer in the Loop?](../ch01-whats-vis-why/s01-03-why-have-computer-loop.md): the automation trade-off behind the human in the loop [p.165]
