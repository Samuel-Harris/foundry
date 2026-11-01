# Chapter writer recipe

You write one chapter of the data-visualisation resource. Read
`tools/CONVENTIONS.md` in full first. It is binding.

## Inputs

- `build/packets/chNN.json`: your files, idiom cards, TOC subtree, page-text
  paths, figures with captions and homes, and outgoing crossrefs resolved to
  planned paths.
- `build/pages/NNNN.txt`: body-only page text. Read every page in your range
  before writing about it. Never cite a page you have not read.
- `provenance/book.json`: idiom-box fields (copy them verbatim from here) and
  the whole TOC, for linking into other chapters.
- `provenance/plan.json`: planned paths of every file in the book. Link to other
  chapters by these paths even though those files may not exist yet.
- `provenance/figures.json`: captions. Copy them exactly.
- Figure images under `.apm/skills/data-visualisation/assets/figures/`. Open the
  ones for your idioms when the caption alone does not tell you what they show.

## Write scope

Write only the files your packet lists, under
`.apm/skills/data-visualisation/`. Never edit `tools/`, `provenance/`, `build/`,
other chapters' files, `SKILL.md`, `references/lookup.md` or
`references/jobs/`. If you need something outside your scope, say so in your
report.

## What good looks like

- **Leaves** summarise the book faithfully, closely enough that an agent rarely
  needs the book itself, within the 2,000-word limit. Every paragraph and list
  item is cited. Quote the book verbatim, in verbatim blocks, for definitions,
  named guidelines and any sentence whose exact wording carries the point. Add
  nothing the book does not say. Where it is ambiguous, say so. Keep the book's
  own terms (marks, channels, expressiveness, effectiveness, and so on).
- **Nodes** let an agent choose the next hop without opening a child. A use-when
  line names the data type, the task or the situation that sends you there, in
  the book's terms, for example "a table with one categorical key and one
  quantitative value, to look up or compare values". It never restates the
  title. Disambiguation notes cover every pair of children a single query could
  plausibly hit, and say what separates them. Related links come from the
  book's "Section x.y" references (your packet lists them), plus cross-chapter
  links where they help, each with a one-line reason.
- **Idiom cards** carry the box fields verbatim from book.json, one block per
  field. Unboxed cards summarise the same What/Why/How facets from the text,
  cited. `Use when / avoid when` holds only what the book says.
  `Alternatives and disambiguation` names sibling idioms (any chapter) and what
  separates them. Implementation hints give real, idiomatic matplotlib and D3
  (v7) code sketches or API pointers for this idiom, under the hints heading,
  with no citations. Keep hints short: one compact snippet or a few API names
  per library.
- Put each figure line in every file the plan homes it in. Never type a
  figure line. Generate it with
  `uv run figure_lines.py --file <path-relative-to-skill>`
  and paste the output. Captions keep extraction quirks on purpose.
- Use `~? words` for child sizes. The size tool fills them later.
- **Page ranges.** Set each file's `pdf_pages` to the span of pages it actually
  cites, within your chapter. Start from the plan's range and widen it, for
  example when a card cites the chapter's costs-and-benefits pages.
- **Cross-chapter links.** A Related item may link any planned path. Cite the
  page in your own range where the book makes the reference, not the target's
  pages.
- **Aliased idioms.** When a card's frontmatter `toc` lists an id other than its
  own, put `<a id="<that id>"></a>` before its `# title`.
- **System boxes.** Some examples are printed in a "System" box rather than an
  "Idiom" box. Their cards keep the line `No idiom box in the book.`, then say
  the book gives a System box and quote its fields verbatim, one block each.
- **Hints must run.** Each `### matplotlib` hint is one self-contained python
  block with inline toy data, ending at the figure (no `plt.show()` needed).
  Each `### D3` hint is a D3 v7 JavaScript block, or a few API names when a
  snippet would mislead. Run `uv run run_hints.py
  <your card paths>` and fix every failure.

## Check your work

From `packages/data-visualisation/tools`:

```bash
uv run scope_report.py NN
```

It prints only the failing evidence about your files. It never writes shared
state, so it is safe to run while other writers work. Fix everything it reports
except:

- size mismatches on `~? words` (B2), which the size tool fixes later;
- dead links to other chapters' planned files that do not exist yet (F2, and
  B3 `related target ... does not exist`);
- orphans, until the integration step writes the router (A2, F3).

Then reread two of your leaves against their pages as a sceptical reviewer.
Look for any claim the pages do not support (C6). Fix what you find.

## Report

Keep it short: files written, the final `scope_report.py` summary line, the
remaining failing lines and why, any C6 doubts, and anything in the plan or
conventions that did not fit the chapter.
