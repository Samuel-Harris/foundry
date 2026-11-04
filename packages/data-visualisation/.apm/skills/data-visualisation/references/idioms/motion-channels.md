---
id: "idiom:motion-channels"
kind: idiom-card
title: "Motion Channels"
pdf_pages: [263, 266]
printed_pages: [238, 241]
toc: []
fidelity: mixed
boxed: false
figures: []
---

# Motion Channels

## Idiom box

No idiom box in the book.

- **What: Data.** A binary category: items that move versus items that do not [p.264].
- **Why: Tasks.** Highlighting: drawing attention to selected items, especially transitorily [p.264].
- **How: Encode.** One combined motion channel (direction, velocity or flicker frequency), typically a cyclic oscillation around each item's location so it stays in view [pp.263-264].

## What it is

Direction of motion, velocity of motion and flicker frequency are visual channels. With a fixed spatial layout, items typically oscillate around their location rather than moving off in one direction [pp.263-264].

<!-- verbatim p.264 -->
> The strength and weakness of motion is that it strongly draws attention; it is nearly impossible to ignore.
<!-- /verbatim -->

The book classifies motion as an identity channel, like shape, though a subchannel such as velocity could in theory be a magnitude channel [p.264].

## Use when / avoid when

- **Use** for highlighting, where pulling attention from the rest of the scene is the goal, particularly transitory highlighting on lightweight actions such as mouseover or clicking rather than heavyweight ones such as typed search [p.264].
- **Use** for binary distinctions, selected versus not selected [p.264].
- **Use** when colour and position already carry groups and categories: motion is very separable from all static channels, notably those [p.264]. An empirical study confirmed motion highlighting is effective where colour coding already conveys other information [p.266].
- **Use** blinking only where very strong emphasis is wanted, for example new items appearing at several places in one timestep of a dynamic layout [p.264].
- **Avoid** more than two levels: whether motion channels are separable from each other, and how many bins each has, is not known [p.264].
- **Avoid** casual flicker and blinking: they are so hard to ignore they can be very annoying [p.264].
- **Use with care** when viewers must attend to the static channels: directing attention to nonmoving channels may be difficult when motion is used [p.264].

## Figures

## Alternatives and disambiguation

- **Shape Channel**: the other identity channel, with dozens of bins for large points, where motion is safe only for two levels [pp.263-264].
- **Categorical Colormaps**: colour can also mark a selection, but motion stays separable when colour is already in use [pp.264-266].

## Related

- [10.4 Other Channels](../ch10-map-color-other-channels/s10-04-other-channels.md#s10.04.05): the full subsection [p.263]
- [11.4.2 Highlighting](../ch11-manipulate-view/s11-04-select-elements/s11-04-02-highlighting.md): highlighting design choices [p.264]
- [Highlighting](highlighting.md): the highlighting idiom card [p.264]
- [10.5 Further Reading](../ch10-map-color-other-channels/s10-05-further-reading.md): the Ware and Bobrow study of motion highlighting [p.266]

## Implementation hints [NOT FROM BOOK]

### matplotlib

```python
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
rng = np.random.default_rng(3)
xy = rng.random((40, 2))
selected = rng.random(40) < 0.15
fig, ax = plt.subplots()
ax.scatter(*xy[~selected].T, color="gray")
moving = ax.scatter(*xy[selected].T, color="gray")
def update(t):
    moving.set_offsets(xy[selected] + 0.01 * np.array([np.sin(t / 2), 0]))  # oscillate in place
    return (moving,)
anim = FuncAnimation(fig, update, frames=20, interval=50, blit=True)
```

### D3

```js
import * as d3 from "d3";
function oscillate(sel) {
  sel.transition().duration(300).attr("transform", "translate(3,0)")
    .transition().duration(300).attr("transform", "translate(-3,0)")
    .on("end", function () { d3.select(this).call(oscillate); });
}
export { oscillate }; // svg.selectAll("circle").filter((d) => d.selected).call(oscillate)
```
