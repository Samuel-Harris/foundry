---
id: s06.05
kind: section-leaf
title: "Eyes Beat Memory"
pdf_pages: [156, 159]
printed_pages: [131, 134]
toc: [s06.05, s06.05.01, s06.05.02, s06.05.03]
fidelity: mixed
---

# 6.5 Eyes Beat Memory

## The rule

<!-- verbatim p.156 -->
> Using our eyes to switch between different views that are visible simultaneously has much lower cognitive load than consulting our memory to compare a current view with what was seen before.
<!-- /verbatim -->

Many interaction idioms implicitly rely on memory and so impose cognitive load [p.156]. Navigating within a single view is the example: staying oriented means remembering past navigation choices or past views. A small overview window with a rectangle showing the position and size of the main view's viewport turns that into an external representation the perceptual system reads off instead of remembering [p.156].

## Subsections

<a id="s06.05.01"></a>

### 6.5.1 Memory and Attention

- **Two kinds of memory.** Long-term memory can last a lifetime and has no strict capacity limit; short-term or working memory lasts several seconds and is very limited. When its limits are reached, people experience cognitive load and fail to absorb all the information presented [p.157].
- **Attention is limited too.** Conscious search grows harder with the number of items to check [p.157].
- **Vigilance.** The ability to perform visual search degrades quickly, with far worse results after several hours than in the first few minutes [p.157].

<a id="s06.05.02"></a>

### 6.5.2 Animation versus Side-by-Side Views

Some animation idioms impose significant cognitive load through implicit memory demands [p.157]. The book distinguishes three meanings of animation [p.157]:

<!-- verbatim p.157 -->
> • narrative storytelling, as in popular movies; • transitions from just one state to another; • video-style playback of a multiframe sequence: play, pause, stop, rewind, and step forward/back.
<!-- /verbatim -->

#### Narrative storytelling

Films succeed through deliberate choreography, keeping action in one place at a time and guiding the viewer's eyes; a dataset animation may change in many places at once, so the film intuition does not carry over [p.157].

#### Transitions

<!-- verbatim p.157 -->
> Animation is extremely powerful when used for transitions between two dataset configurations because it helps the user maintain context.
<!-- /verbatim -->

- **Evidence.** Animated transitions can be more effective than jump cuts because they help people track changes in object positions or camera viewpoints [p.157].
- **Limit.** They work best when only a few things change; when many objects change between frames, people will have a hard time tracking everything; we are blind to changes in regions outside the focus of attention [p.158].
- **Blink comparator.** Jump cuts are hard to follow when seen once, but letting the user jump back and forth between just two frames can reveal a localised change between scenes; the astronomer who found Pluto used this idiom [p.158].

#### Multiframe playback

- **Not interaction.** With video-style playback the user controls only the speed, not what occurs, unlike true interactive control such as flying through a scene [p.158].
- **Memory demand.** Comparing frames that do not adjoin relies on memory of earlier frames. If changes occur in only one place at a time, the demands on attention and memory are small; when many things change all over the frame across many frames, tracking what happens is very difficult [p.158].
- **Pause and replay help, partly.** They are much better than one straight-through viewing but do not fully solve the problem [p.158].

#### Side by side instead

<!-- verbatim p.158 -->
> For tasks requiring detailed comparison across many frames, seeing all the frames at once side by side can be more effective than animation.
<!-- /verbatim -->

Frames must stay few enough that each one's detail can be discerned, typically dozens but not hundreds at current display resolutions, and the action should be segmented into meaningful chunks rather than randomly chosen keyframes [p.158]. Many multiple-view idioms exploit this, especially small multiples [p.158].

<a id="s06.05.03"></a>

### 6.5.3 Change Blindness

We feel we hold a detailed internal memory of the visual field, but we do not; our eyes dart around gathering information just in time, so quickly that we do not typically notice it consciously [pp.158-159].

<!-- verbatim p.159 -->
> The phenomenon of change blindness is that we fail to notice even quite drastic changes if our attention is directed elsewhere.
<!-- /verbatim -->

In one experiment, a stranger asking directions was swapped for another person while a door carried between them blocked the view; most people did not notice, even when the new person was dressed completely differently or was of a different gender [p.159]. We are very sensitive to changes at the focus of attention and surprisingly blind elsewhere; the difficulty of tracking complex, widespread changes in multiframe animations is one implication for vis [p.159].

## Figures

## Related

- [12.3.2 Share Data: All, Subset, None](../ch12-facet-into-multiple-views/s12-03-juxtapose-coordinate-views/s12-03-02-share-data-all-subset.md): small multiples, the side-by-side alternative to animation [p.158]
- [11.3 Change View over Time](../ch11-manipulate-view/s11-03-change-view-over-time.md): animated transitions as a way to change a view [p.157]
- [6.7 Overview First, Zoom and Filter, Details on Demand](s06-07-overview-first-zoom-filter.md): overviews, of which the viewport-rectangle window is one use [p.156]
- [6.8 Responsiveness Is Required](s06-08-responsiveness-required.md): the one-second time constant for an animated transition [p.157]
- [1.4 Why Use an External Representation?](../ch01-whats-vis-why/s01-04-why-use-external-representation.md): external representations that replace internal memory [p.156]
- [6.3.3 Occlusion Hides Information](s06-03-no-unjustified-3d/s06-03-03-occlusion-hides-information.md): 3D navigation that forces remembering shape across viewpoints [p.156]
