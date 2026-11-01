---
id: s10.03.04
kind: subsection-leaf
title: "Colorblind-Safe Colormap Design"
pdf_pages: [260, 260]
printed_pages: [235, 235]
toc: [s10.03.04]
fidelity: mixed
---

# 10.3.4 Colorblind-Safe Colormap Design

## The problem

<!-- verbatim p.260 -->
> Designers using color should take the common problem of red–green color blindness into account.
<!-- /verbatim -->

- Red–green colour blindness is a sex-linked inherited trait affecting 8% of males and a much smaller proportion of females, 0.5% [p.260].
- In the common forms, sensing along the red–green opponent axis is limited or absent [p.260].
- Many more pairs than red and green are confused: red from black, blue from purple, light green from white, and brown from green [p.260].

## Theory: what to design

<!-- verbatim p.260 -->
> On the theoretical side, the safest strategy is to avoid using only the hue channel to encode information: design categorical colormaps that vary in luminance or saturation, in addition to hue.
<!-- /verbatim -->

- Avoid colormaps that emphasise red–green, especially divergent red–green ramps [p.260].
- Where a domain has strong red and green conventions, accommodate them by ensuring luminance differences between the reds and greens [p.260].

## Practice: how to check

Check the design with a colour blindness simulator. Many desktop tools include one, such as Adobe Illustrator and Photoshop, and websites offer them: <http://www.rehue.net>, <http://www.color-blindness.com> and <http://www.etre.com/tools/colourblindsimulator> [p.260].

## Figures

## Related

- [Colorblind-Safe Colormaps](../../idioms/colorblind-safe-colormaps.md): the card with decision rules and code [p.260]
- [10.2 Color Theory](../s10-02-color-theory/node.md): opponent colour channels, which explain colour deficiency [p.260]
- [7.5.2 Matrix Alignment: Two Keys](../../ch07-arrange-tables/s07-05-separate-order-align-categorical/s07-05-02-matrix-alignment-two-keys.md): the historical and technical reasons for red–green use in bioinformatics [p.260]
