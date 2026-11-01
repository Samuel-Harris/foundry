# Build conventions for the data-visualisation resource

The contract every build tool and every writing agent follows. Source rubric:
`viz-resource-build-rubric.md` at the repository root. Writing agents must not
edit this file, `tools/`, or `build/`.

Source PDF: passed as `--pdf` or `$VIZ_PDF`. Never copy it into the repository.
"Page" always means **PDF page** (1-based) unless it says printed page.

## Layout

```text
packages/data-visualisation/
  .apm/skills/data-visualisation/        deployed skill (the resource)
    SKILL.md                              router
    references/
      lookup.md                           idiom and concept lookup (index node)
      jobs/j1-choose-idiom.md ... j4-dashboards.md     job nodes
      chNN-<slug>/node.md                 chapter node
      chNN-<slug>/sNN-MM-<slug>.md        section leaf
      chNN-<slug>/sNN-MM-<slug>/node.md   section node (large sections only)
      chNN-<slug>/sNN-MM-<slug>/sNN-MM-KK-<slug>.md   subsection leaf
      idioms/<idiom-slug>.md              idiom cards
    assets/figures/fig-NN-MM.png          figure store
  provenance/                             not deployed
    book.json  plan.json  figures.json  coverage.json
    fidelity-ledger.md
    reports/{links,orphans,provenance,self-check}.md
  tools/                                  build tools and their tests (not deployed)
  build/                                  gitignored scratch: page text, packets, renders
```

`plan.json` (written by `tools/plan.py`) is the single source of truth for which
file every TOC entry, idiom card and figure lands in. Writers create exactly the
files the plan assigns them and link to other chapters by their planned paths,
whether or not those files exist yet.

## Identifiers

- TOC entries: `ch07`, `s07.05`, `s07.05.01`, `s07.05.01.02`. Named idioms in the
  TOC: `idiom:<slug>`.
- Idiom slugs: lowercase kebab case of the idiom name, e.g. `idiom:scatterplots`.
- Figures: `fig-NN-MM` (`Figure 7.3` is `fig-07-03`). Sub-panels (a), (b) share
  one file.
- In-file anchors: `<a id="s07.05.01"></a>` on the line before the heading of
  every TOC entry a file covers that is not the file's own top entry. Coverage
  maps those entries to `path#s07.05.01`.

## Granularity rule (applied by `plan.py`, not by writers)

- Every chapter gets a chapter node.
- A section spanning more than 5 PDF pages **and** having subsections becomes a
  section node, with one leaf per subsection. Consecutive subsections of 1 page or
  less may share a leaf; each covered subsection gets an anchor.
- Every other section is one leaf; its subsections are `###` headings with
  anchors.
- Every idiom box and every TOC-named idiom gets an idiom card. A4: chapters 10 and
  11 also get unboxed cards (`boxed: false`) for their core idioms (colormap
  types, interaction idioms); the plan lists them.
- Idiom cards are children of the node that owns their section (the section node
  when one exists, otherwise the chapter node). Leaves may link to them under
  `## Related`.

## Frontmatter (every file under the skill)

```yaml
---
id: s07.05                 # router: "router"; lookup: "lookup"; jobs: "j1".."j4"; cards: "idiom:<slug>"
kind: section-leaf         # router | job-node | index-node | chapter-node | section-node | section-leaf | subsection-leaf | idiom-card
title: "Separate, Order, and Align: Categorical Regions"
pdf_pages: [176, 186]      # inclusive range the file draws on; navigation-only files use the span they route over
printed_pages: [151, 161]
toc: [s07.05, s07.05.01, s07.05.02]   # every TOC id this file covers (cards: their idiom id)
fidelity: summary          # summary | mixed (summary plus verbatim blocks)
---
```

`SKILL.md` additionally carries `name: data-visualisation` and `description:`.
Idiom cards additionally carry `boxed: true|false` and `figures: [fig-07-03]`.

## Citations (C2)

- Cite PDF pages as `[p.172]` or `[pp.172-174]`.
- Every paragraph, list item and table row of book-derived prose carries at least
  one citation. That includes use-when lines, disambiguation notes and related
  links. Headings, frontmatter, figure lines and verbatim blocks are exempt.
- A citation must fall inside the book's page range for the cited claim; never
  cite a page you have not read.
- Where the source is ambiguous, say so and cite it. Never resolve or extend it.

## Verbatim blocks (C1)

```markdown
<!-- verbatim pp.171-172 -->
> Exact text from the book.
<!-- /verbatim -->
```

After stripping the leading `>` and its space, normalising whitespace, joining end-of-line hyphenation,
unifying quotes and ligatures, the block text must be a substring of the cited
pages' extracted text. One block per contiguous quote. Never put hints inside.

## Hints (E2 to E5)

- Non-book content lives only in a section whose heading ends with
  `[NOT FROM BOOK]`, e.g. `## Implementation hints [NOT FROM BOOK]`, and runs
  until the next `##` heading.
- Outside such sections, a non-book sentence must sit in its own paragraph or
  list item that begins with `[NOT FROM BOOK]`.
- Hint text never carries a page citation.
- Deleting every hint section and `[NOT FROM BOOK]` item must leave a complete
  file.

## Node structure (B1 to B6)

Every node (router, job node, index node, chapter node, section node) has, in
order:

1. `# <title>` and a one-paragraph scope, cited.
2. `## Children`. One list item per child, exactly this shape:

   ```markdown
   - [7.5 Separate, Order, and Align](s07-05-separate-order-align.md) · ~1,240 words. **Use when** <decision criterion: the data type, task or situation that makes this the next hop, not a restatement of the title> [pp.176-186]
   ```

   The `~N words` value is written by `tools/check.py --write-sizes`; writers put
   `~? words` and the tool fills it.
3. `## Disambiguation`. One bullet per group of overlapping siblings:
   `- **Bar charts vs dot charts vs line charts.** <what separates them> [p.N]`.
   Every sibling title named in the bold lead must be a child of this node. If no
   siblings overlap, write the single item `- No overlapping children.`
4. `## Related`. One bullet per link: `- [9.2 Connection](../ch09-.../s09-02-....md): <why it is related> [p.N]`.
   Seed from the book's "Section x.y" references; add cross-chapter links where
   the book leaves a gap. At least one per node.

A node must let an agent choose its next hop without opening any child (B6).

## Leaf structure

`# <number> <title>`, then content under `##`/`###` headings mirroring the
book's TOC order, summaries cited per paragraph, verbatim blocks for definitions
and the book's named guidelines, `## Figures` and `## Related` (same bullet shape
as nodes).

## Idiom card structure

```markdown
# <Idiom name>
## Idiom box
(boxed) one verbatim block per field, e.g. What: Data / Why: Tasks / How: Encode / Scale.
(unboxed) "No idiom box in the book." then a cited summary of the same fields.
## What it is            cited summary
## Use when / avoid when cited, book claims only
## Figures
## Alternatives and disambiguation   sibling idioms and what separates them, cited
## Related
## Implementation hints [NOT FROM BOOK]
### matplotlib
### D3
```

## Figures (D1, D5, D6)

A figure reference is one list item under `## Figures`:

```markdown
- ![Figure 7.3](../../assets/figures/fig-07-03.png) **Figure 7.3** [p.172]. <caption exactly as in figures.json>
```

The caption must equal the `caption` field in `provenance/figures.json`.

## Size limits (section 6 of the rubric, gated)

Measured in words, frontmatter excluded: router 2,500; job, index, chapter and
section nodes 1,500 (lookup 4,000); leaves 2,000; idiom cards 1,500. A leaf over
budget is a plan problem: report it, do not truncate content.

## Fidelity ledger (C5)

| Level | Choice | Reason |
| --- | --- | --- |
| Router, job nodes, lookup | Summary, cited, navigation only | Must stay small enough to read at every hop |
| Chapter and section nodes | Summary, cited, navigation only | Same; content lives in leaves |
| Section and subsection leaves | Mixed: cited summary plus verbatim blocks for definitions and named guidelines | Summaries keep leaves to a few pages' size; verbatim keeps the book's exact rules where wording matters |
| Idiom cards | Mixed: verbatim idiom-box fields, cited summary for the rest, marked hints | The box is the book's own compact schema; hints are required by E2 |

`provenance/fidelity-ledger.md` carries this table plus the measured counts.

## Data files (shared by every tool)

All JSON is UTF-8, keys sorted, two-space indent, so reruns diff cleanly.

`provenance/book.json` (written by `tools/extract.py`):

```json
{
  "pdf": {"pages": 422, "sha256": "..."},
  "page_map": [{"from_pdf": 1, "to_pdf": 25, "offset": 1, "style": "roman"}, {"from_pdf": 26, "to_pdf": 422, "offset": 25, "style": "arabic"}],
  "toc": [{"id": "s07.05", "level": "section", "number": "7.5", "title": "...", "parent": "ch07",
           "printed_page": 151, "pdf_start": 176, "pdf_end": 186}],
  "idiom_boxes": [{"slug": "scatterplots", "name": "Scatterplots", "chapter": 7, "section": "s07.04",
                   "pdf_page": 175, "fields": {"What: Data": "...", "How: Encode": "..."}}],
  "figures": [{"id": "fig-07-03", "number": "7.3", "chapter": 7, "pdf_page": 172, "caption": "..."}],
  "crossrefs": [{"from": "s07.05", "pdf_page": 180, "target_number": "9.2", "target": "s09.02"}]
}
```

`level` is one of `chapter | section | subsection | subsubsection | idiom`.
TOC-named idioms are `level: idiom` with `id: idiom:<slug>`.

`provenance/plan.json` (written by `tools/plan.py`):

```json
{
  "files": [{"path": "references/ch07-arrange-tables/node.md", "kind": "chapter-node", "id": "ch07",
             "chapter": 7, "toc": ["ch07"], "pdf_pages": [170, 203],
             "children": ["references/ch07-arrange-tables/s07-01-why-arrange.md"]}],
  "entries": {"s07.05.01": "references/ch07-arrange-tables/s07-05-....md#s07.05.01"},
  "idiom_cards": [{"id": "idiom:scatterplots", "path": "references/idioms/scatterplots.md", "boxed": true,
                   "chapter": 7, "section": "s07.04", "parent": "references/ch07-.../node.md",
                   "pdf_pages": [175, 176], "figures": ["fig-07-03"]}],
  "figure_homes": {"fig-07-03": ["references/ch07-.../s07-04-....md", "references/idioms/scatterplots.md"]}
}
```

Paths are relative to the skill directory. The router, job nodes and lookup are
not in `files`; the integration step owns them.

`provenance/figures.json` (written by `tools/figures.py`): one entry per
`book.json` figure, `{"id", "number", "pdf_page", "caption", "file": "assets/figures/fig-07-03.png" | null,
"method": "embedded" | "crop" | null, "dpi": 150, "reason": null | "why it could not be extracted",
"referenced_by": [...]}`. `referenced_by` is filled by `tools/check.py`.

`build/packets/chNN.json` (written by `tools/plan.py`): everything one chapter
writer needs: its `files` and `idiom_cards` from the plan, the TOC subtree, the
page-text file paths for its range, its figures with captions and homes, and its
outgoing crossrefs resolved to planned paths.

## Clarifications (settled after the checker baseline)

- **Page text.** `build/pages/NNNN.txt` holds the body column only, with running
  heads and page numbers removed. Margin notes follow the body, separated by a
  blank line. A verbatim quote never spans a margin note.
- **figures.json container.** It is `{"figures": [ ... ]}`, keys sorted.
- **Card ids.** A boxed card's `id` is `idiom:<box slug>`. Its frontmatter `toc`
  lists every TOC idiom id it covers. `plan.json` records that mapping on the
  card (`"toc": [...]`), so every TOC-named idiom lands on exactly one card.
- **Reachability.** A2 and F3 ignore links from `lookup.md`. The `## Children`
  tree must reach every file on its own.
- **Citations in tables.** C2 applies to every table data row. Header rows are
  exempt.
- **Empty figure sections.** A card or leaf with no figures keeps an empty
  `## Figures` section.
- **Job reach (E1).** j1 reaches chapters 2 and 3 and idiom cards. j2 reaches
  idiom cards. j3 reaches chapters 4 and 6. j4 reaches chapters 11 and 12.
- **Duplicate figure labels.** The book prints "Figure 8.6" twice (pp.211 and
  213). The second is `fig-08-06b` with number "8.6". Figure ids may carry one
  trailing letter only for such duplicates. Figure lines still show the printed
  number. The image path and caption tell the two apart.
- **One page or range per citation bracket.** Write `[pp.47-48] [p.59]`, never
  `[pp.47-48, 59]`. A comma list does not count as a citation.
- **Section introductions.** A section node is navigation only. The text between
  a section heading and its first subsection is summarised (and may be quoted) at
  the top of the first subsection leaf, and the node's scope says so.
- **Card figures** come from the explicit `CARD_FIGURES` table in `plan.py`,
  decided by reading each figure against the text, not by page proximity.
