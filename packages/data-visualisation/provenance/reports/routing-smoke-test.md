# Routing smoke test: data-visualisation skill

Agent started at `SKILL.md` and followed markdown links only. Word counts are approximate: SKILL.md measured at 2,047 (`wc -w`); other files use the `~N words` figure on the linking line, or an estimate where none was shown (Treemaps 812 measured, Why Reduce 455 measured). "Hops" is the number of files opened, including SKILL.md. Each query is counted as if started fresh, so SKILL.md (2,047) is included every time.

Protocol deviation: after the run the agent ran `wc -w` on three files already read and an `ls` on the `reports/` directory (to confirm it existed). No file outside the link graph was read.

## Per-query results

| # | Query | Path | Hops | Words | Answered | Unsure at |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 8 product lines, monthly, which are growing | SKILL, J1, 12.5 Superimpose Layers, Superimposed Line Charts | 4 | 4,580 | yes | J1: no Line Charts child. Chose 12.5 over 7.5 by guess |
| 2 | 2,000 people x 12 numeric answers, relationships | SKILL, J1, 7.5 node, SPLOM | 4 | 5,190 | yes (caveat: 2,000 items exceeds the card's "hundreds") | J1: SPLOM is not a child but Scatterplots is; 7.6 (parallel coordinates) also fits |
| 3 | Org chart, 400 people, hierarchy and team sizes | SKILL, J1, 9.5 Containment, Treemaps | 4 | 5,030 | yes | J1: 9.4 vs 9.5 (an org chart is a tree, but 9.4 is titled "network") |
| 4 | Average temperature per US county | SKILL, J1, ch8 node, Choropleth Map | 4 | 4,490 | yes | none |
| 5 | matplotlib clustered gene x sample heatmap | SKILL, J2, Heatmaps, Cluster Heatmaps | 4 | 4,620 | yes | J2: Cluster Heatmaps is not listed. Reached only through the Heatmaps card's Related line |
| 6 | D3 zoomable scatterplot | SKILL, J2, Scatterplots (dead end), back to SKILL, ch11 node, Geometric Zooming | 5 (+1 backtrack) | 5,590 | partly (zoom snippet is generic, no scatterplot-specific example) | J2: no link to any interaction card. J2 and Scatterplots do not mention zoom |
| 7 | Colormap for correlation matrix -1 to 1 | SKILL, J2, Ordered Colormaps | 3 | 4,140 | yes | none |
| 8 | 6 categories as lines, how many colours | SKILL, J2, Categorical Colormaps | 3 | 4,120 | yes | J2: Line Charts card vs Categorical Colormaps. The card with the line-specific hint (Superimposed Line Charts) is not in J2 |
| 9 | 3D pie charts dashboard critique | SKILL, J3, 6.3 No Unjustified 3D (node), 7.6.3 Radial Layouts | 4 | 5,080 | partly | J3: 6.1 vs 6.3 vs 6.3.4 vs 7.6.3. No 3D-pie entry. 6.3 never mentions pies. 6.3.4 (3D bar) left unread |
| 10 | Rainbow colormap for elevation | SKILL, J3, 10.3.2 Ordered Colormaps (leaf) | 3 | 4,070 | yes (elevation, sea-level example is in the leaf) | J3: 10.2.3 vs 10.3.2 is minor |
| 11 | "Users liked it in a survey", enough validation? | SKILL, J3, 4.6.5 Mismatches, 4.6.3 Idiom Validation | 4 | 4,000 | partly (usability and preference are not validation, but no explicit survey/adoption guidance) | J3: 4.5, 4.6.5, 4.6.3, 4.3. 4.6.1 and 4.6.2 are not J3 children |
| 12 | 50,000 overlapping points | SKILL, J3, 13.2 Why Reduce (Related), 13.4 Aggregate, Continuous Scatterplots | 5 | 4,950 | yes | J3: nothing matches overplotting. Took 13.2 from a Related line as a stretch |
| 13 | Linked views: map region selection highlights table rows | SKILL, J4, 12.3.1 Share Encoding | 3 | 3,880 | yes (generic linked highlighting; no map or table specifics) | J4: 12.3.1 vs Improvise (geographic) vs 11.4. J4 disambiguation resolved it |
| 14 | 10 years of server logs, drill-down to a day | SKILL, J4, 12.3.2 Share Data, 6.7 Overview First | 4 | 5,030 | yes (design pattern; no time-series idiom named) | J4: 12.3.2 vs 6.7 vs 13.4 vs 11.5 |
| 15 | Small multiples vs overlaid lines | SKILL, J4, 12.2 Why Facet, 12.5 node, Superimposed Line Charts | 5 | 5,170 | yes | J4: 12.2 states "two layers feasible, three with care", the opposite of the card's "nearly a dozen". The card is not a J4 child |
| 16 | Focus on part of huge network without losing context | SKILL, J4, 14.2 Why Embed, 14.5 Distort | 4 | 4,810 | partly (lenses and hyperbolic geometry named; no network-specific or elision/degree-of-interest guidance) | J4: only 14.2 and 14.5 listed from ch14. Elision (14.3 / 14.4) only via Related |

## Routing problems

1. `references/jobs/j3-critique.md`, Children: no entry for overplotting or too many points. First child that could apply was none; the agent used `13.2 Why Reduce?` from Related: "the cost of filtering versus aggregating when a design hides data". Q12 needed Continuous Scatterplots, which J3 never links.
2. `references/jobs/j2-write-plotting-code.md`, Children: no interaction or zoom card for a coding job. Scatterplots entry: "**Use when** coding two quantitative attributes as horizontal and vertical position of point marks". Q6 dead-ended here and had to backtrack to SKILL.md to reach ch11 / Geometric Zooming.
3. `references/jobs/j2-write-plotting-code.md`: does not list Superimposed Line Charts, the card with the `tab10` hint and the ~dozen-series limit. Line Charts entry: "**Use when** coding a quantitative value against an ordered key such as time to show trend". Q8 (colours for 6 lines) is answered by Categorical Colormaps but the line-specific card is hidden.
4. `references/jobs/j2-write-plotting-code.md`: Cluster Heatmaps is not listed. Heatmaps entry: "**Use when** coding a matrix of two categorical keys with a quantitative value in each cell's colour". Q5 (clustered) got there only through the Heatmaps card's Related line. The 7.5 entry does mention "cluster heatmaps", but it is a 1,253-word node.
5. `references/jobs/j3-critique.md`, Children: 4.6.1 Domain Validation and 4.6.2 Abstraction Validation are missing. "Users liked it" is a domain or abstraction-level claim; the agent found 4.6.5 and 4.6.3 and had to guess. The 4.6.5 entry reads "**Use when** a design's claimed benefit is backed by evidence from a different level".
6. `references/jobs/j3-critique.md`: no "3D pie" entry. 6.3.4 reads "**Use when** the specific complaint is that perspective makes bar heights or sizes impossible to compare, as in a 3D bar chart". 7.6.3 reads "**Use when** critiquing a pie, polar area or other radial chart against a bar chart". The agent has to join two leaves itself, and the 6.3 node never mentions pies.
7. `references/jobs/j4-dashboards.md`, Disambiguation: "Juxtaposed views cost screen space but several are straightforward and up to a few dozen viable with care; layers cost none but two are feasible, three with care". The 12.2 leaf says the same. For Q15 this suggests overlaying at most three lines, while Superimposed Line Charts says "nearly a dozen" (thin line marks). Neither J4 nor 12.2 flags the exception. J4 also does not list the Superimposed Line Charts card.
8. `references/jobs/j4-dashboards.md`, Children: ch14 is represented only by 14.2 and 14.5. Elision / degree-of-interest, the likeliest answer for a huge network, is reachable only via Related: "[14 Embed: Focus+Context]: the elision and lens idioms beyond distortion". 14.2 reads "**Use when** users lose their place after zooming and need context kept in the same view rather than in a second view".
9. `references/jobs/j1-choose-idiom.md`, Children: no Line Charts card, and SPLOM / Parallel Coordinates are absent while Scatterplots is present. Scatterplots entry reads "**Use when** a table has two quantitative values and no key, and the question concerns correlation, trends, outliers or clusters among up to hundreds of items". For Q1 and Q2 the agent chose between 12.5, 7.5 and 7.6 on guesswork. Also the intro "Work down the children in order; stop at the first that settles the idiom" implies reading eight classification nodes (about 5,500 words) before reaching any chart child. The agent jumped by use-when line instead.
10. SKILL.md routing table, row "Table, many quantitative value attributes": the cell for Compare some lists "rankings: LineUp", not correlation. The correlation query (Q2) is in the Explore column. Q2 was resolved by the J1 route, not the table.
11. SKILL.md Children, ch11 entry: "**Use when** a single view must respond to the user: changing encoding or order, selecting and highlighting, zooming and panning, or slicing away dimensions". That line is the only reason Q6 was recoverable. J2 never points at ch11.
12. Cost of entry: SKILL.md is 2,047 words, with a roughly 1,100-word routing table. Every query pays it plus a 1,100-1,250-word job node, so about 3,200 words are spent before any content file. The router table was used for none of the 16 queries (all went through job nodes), so its cost was pure overhead on this test.
13. Card/leaf pairs that duplicate: Ordered Colormaps (card) and 10.3.2 (leaf) both exist. J2 sends coders to the card and J3 sends critics to the leaf, which works, but nothing tells a J1 reader that the card exists.

## Summary

- Median hops: 4 files (range 3 to 5), counting SKILL.md. Backtracks: 1 (Q6).
- Median words read: about 4,700 (range about 3,900 to 5,600). Of that, about 2,050 is SKILL.md and about 1,100-1,250 the job node.
- Answered: yes 12 (Q1, 2, 3, 4, 5, 7, 8, 10, 12, 13, 14, 15), partly 4 (Q6, 9, 11, 16), no 0. One dead end (Q6 at the Scatterplots card). One query (Q12) reached its answer only through a Related line, not a Children entry.
- Where the job node had a direct child (Q4, Q7, Q8, Q10, Q13), routing was clean: 3-4 files and no hesitation.

Three worst routing problems:

1. J3 omits overplotting entirely (Q12). Nothing in J3's Children matches 50,000 overlapping points. The route works only by following a stretch Related link (13.2 to 13.4 to Continuous Scatterplots). Same shape of gap: J3 lacks 4.6.1 and 4.6.2 for "users liked it" claims (Q11) and has no 3D-pie route (Q9).
2. J2 has no interaction or zoom route and hides cards that answer its own queries (Q6, Q5, Q8). Q6 dead-ended at Scatterplots and needed a backtrack to SKILL.md. Cluster Heatmaps and Superimposed Line Charts are absent from J2's list.
3. Contradictory capacity guidance with no pointer to the exception (Q15). J4's disambiguation and 12.2 say two or three layers; the unlisted Superimposed Line Charts card says nearly a dozen lines. An agent that stops at 12.2 gives the wrong answer to "overlaid lines or small multiples?". Runner-up: J4 lists only 14.2 and 14.5 and hides the elision idioms (Q16).
