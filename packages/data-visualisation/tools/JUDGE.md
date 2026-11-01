# Judge recipe

You judge and fix the rubric gates no script can decide, for an assigned set of
files. Read `tools/CONVENTIONS.md` first. The mechanical gates
already pass (`tools/check.py`: 0 FAIL). Keep them passing.

## What you judge

- **C6, fidelity.** For every leaf and idiom card in your set, read each cited
  page in `build/pages/NNNN.txt` and check every summary claim against it. A
  claim fails when the pages do not support it, when it overstates the book
  (a hedge dropped, "can" turned into "should", description turned into
  advice), when it contradicts the book, or when it resolves an ambiguity the
  book leaves open. Fix it by rewording to what the page says, or delete it.
  Do not add new claims.
- **B1, use-when lines.** In every node in your set, each child's use-when
  must be a decision criterion: the data type, task or situation that makes
  this child the next hop. A line that restates or paraphrases the title fails.
  Rewrite it from the child's content, cited.
- **B4, disambiguation.** Every pair or group of children that one query could
  plausibly hit needs a note saying what separates them. A note that says how
  the children chain together, rather than how to choose between them, fails.
- **B6, self-sufficiency.** Read each node alone and pick a child for three
  realistic queries that should land under it. If you cannot pick without
  opening a child, fix the node.
- **Hints.** Read each card's hints. Flag and fix code that is wrong for the
  idiom (for example a diverging map on sequential data), not idiomatic for
  the library, or misleading. Hints stay `[NOT FROM BOOK]` and uncited.

## Rules

- Edit only the files in your set. If a fix belongs elsewhere, record it as a
  finding with action `handoff`.
- Keep every citation within the file's `pdf_pages`, and keep `~N words` sizes
  as they are. The size tool rewrites them after you.
- After your edits, from `packages/data-visualisation/tools`, run
  `../../../.venv-viz/bin/python scope_report.py NN` for each of your chapters
  and `../../../.venv-viz/bin/python run_hints.py <your cards>`. The only
  allowed scope_report lines are B2 size mismatches.

## Record

Write one TSV per judge at `provenance/reports/judge/<your-set>.tsv` with the
tab-separated header columns `gate`, `file:line`, `finding` and `action`, one row per finding. Action is
`fixed`, `deleted`, `handoff` or `kept: <reason>`. A finding you decided not to
act on still gets a row. Keep cells single-line.

## Report

Counts per gate (checked, failed, fixed), the handoff rows, the scope_report
and run_hints summary lines, and the three findings a reviewer should most
want to see.
