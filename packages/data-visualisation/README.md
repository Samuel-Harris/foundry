# data-visualisation

Munzner's *Visualization Analysis and Design* as a page-cited reference for choosing, coding, critiquing and designing visualisations.

## What it installs

| Primitive | Name | Purpose |
| --- | --- | --- |
| Skill | `data-visualisation` | Route a visualisation task to the book's guidance on data, tasks, idioms, colour, interaction and validation. |

## Install

```bash
apm install Samuel-Harris/foundry/packages/data-visualisation#v0.1.0 --target cursor,claude,copilot
```

## What the skill is for

The router in `SKILL.md` sends each request to one of four job nodes:

- **J1** chooses a chart or idiom for a dataset and a question.
- **J2** writes plotting code for a chart that is already chosen.
- **J3** critiques or improves an existing chart, dashboard or tool.
- **J4** designs interactive and multiple-view dashboards.

Each job node reads across the chapters it needs and ends at the sections and idiom cards that answer the request.

## How the skill is organised

The skill discloses detail in layers, so an agent reads only the files its task needs. Every node lists its children with a word count and a **Use when** line.

- `SKILL.md` is the router. It routes by job, and by data type and task through a routing table.
- `references/jobs/` holds the four job nodes.
- `references/lookup.md` maps every idiom, chapter, section and key concept to its file.
- `references/chNN-<slug>/node.md` is a chapter node, one for each of the book's 15 chapters.
- Section leaves sit beside each chapter node. A large section becomes a section node with subsection leaves beneath it.
- `references/idioms/` holds 76 idiom cards. Each card summarises when the idiom fits, when to avoid it, its alternatives and its figures.
- `assets/figures/` holds 197 figures cropped from the book. Files link to them with the book's captions.

## Where the content comes from

The content is derived from the book. Summaries and verbatim quotations carry PDF page citations such as `[p.68]` or `[pp.126-128]`. Material that is not from the book carries the `[NOT FROM BOOK]` marker. The main case is the matplotlib and D3 implementation hints at the end of each idiom card.

## Copyright and licence

The skill's quotations, summaries and figures come from Tamara Munzner, *Visualization Analysis and Design*, A K Peters/CRC Press, 2014. The copyright in that material stays with its holders, and this package grants no licence to it. Keep the package in private repositories and do not redistribute it.

The build tools under `tools/` and the `[NOT FROM BOOK]` implementation hints are released under the MIT licence.

## Rebuild and check the skill

The source PDF is not in the repository. Pass it to the extraction tools with `--pdf` or the `VIZ_PDF` environment variable.

The tools under `tools/` extract the book model and figures, plan every file, build the lookup and check the result against the build rubric. `tools/requirements.txt` pins their Python dependencies. `tools/CONVENTIONS.md` is the contract for layout, identifiers, frontmatter, citations, hints and figures, and each tool's docstring gives its usage.

`tools/check.py` writes the gate results to `provenance/reports/`. Read `self-check.md` for the per-gate status, and `links.md`, `orphans.md` and `provenance.md` for the evidence behind them. `provenance/fidelity-ledger.md` records the measured fidelity counts.

`tools/`, `provenance/`, `build/` and `scratch/` sit outside `.apm/`, so an install does not deploy them. `build/` and `scratch/` are gitignored.

## Targets

Deployed to `cursor`, `claude` and `copilot`.
