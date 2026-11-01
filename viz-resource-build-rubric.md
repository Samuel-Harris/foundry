# Build Rubric: Progressive-Disclosure Resource from *Visualization Analysis and Design*

Audience: the orchestrator and subagents building the resource.
Keywords: MUST / MUST NOT items are gating (pass/fail). SHOULD items are non-gating guidance.
Source: `Visualization_Analysis_and_Design.pdf` (T. Munzner).

---

## 1. Goal

Convert the book into a resource that a **visualisation agent** can navigate by progressive disclosure: load a small top level first, then descend only into the parts it needs, with each step telling it precisely where to go next.

The consuming agent will use the resource for four jobs:

- **J1** Choose a chart or idiom for a given dataset and question.
- **J2** Write plotting code (e.g. matplotlib, D3) for a user's data.
- **J3** Critique or improve an existing visualisation.
- **J4** Design interactive or multi-view dashboards.

**Format is the implementer's decision.** Do not use vendor-specific constructs. This rubric uses abstract terms:

- **Router**: the single top-level entry point.
- **Node**: any navigation file that lists children.
- **Leaf**: a file holding actual book content.
- **Idiom card**: a structured leaf for one visualisation idiom.
- **Hint**: content added by the implementer that is not from the book.
- **Manifest**: a machine-checkable index.

---

## 2. Source facts (from preliminary analysis; re-verify before relying on them)

- PDF: 422 pages, clean text layer (`pdftotext` works; no OCR needed), about 200 figure captions.
- **Page mapping:** front matter PDF page = printed page + 1; body = printed page + 25; back matter (bibliography) = printed + 25. Chapter 1 starts at PDF p.26.
- **Bookmarks are chapter-level only.** The detailed table of contents is on roughly PDF pp. 6-15 and includes section, subsection and named-idiom entries.
- **Both book indexes (idiom index, concept index) are absent from this PDF.** The file ends with the bibliography. Nothing in the book maps idiom or concept names to pages.
- **Chapters** (PDF page ranges taken from bookmarks, so verify): 1 What's Vis (26-45); 2 What: Data (46-67); 3 Why: Task (68-91); 4 Validation (92-119); 5 Marks and Channels (120-141); 6 Rules of Thumb (142-169); 7 Arrange Tables (170-203); 8 Arrange Spatial Data (204-225); 9 Arrange Networks and Trees (226-243); 10 Map Color and Other Channels (244-267); 11 Manipulate View (268-289); 12 Facet into Multiple Views (290-323); 13 Reduce Items and Attributes (324-347); 14 Embed: Focus+Context (348-365); 15 Case Studies (366-393); bibliography from 400.
- Chapters generally open with a "Big Picture" section and an overview figure placed on the preceding page, and generally end with "Further Reading" (verify per chapter).
- **Idiom boxes** use a fixed schema (What: Data / Why: Task / How: ...). About 43 detected: ch7 15, ch8 6, ch9 4, ch10 0, ch11 2, ch12 4, ch13 7, ch14 4, ch15 1. Treat these counts as approximate and recount.
- About 100 in-text "Section x.y" cross-references exist and are usable as graph edges.

---

## 3. Required components

1. **Router** that supports all four jobs (J1-J4) as entry points.
2. **Chapter nodes** (15), one per chapter.
3. **Section nodes and leaves** following the book's table-of-contents hierarchy.
4. **Idiom cards**, one per idiom (every idiom box, plus every idiom named in the table of contents that lacks a box).
5. **Figure store and figure manifest**.
6. **Hints layer** (non-book content, clearly separated or marked).
7. **Coverage manifest** and **fidelity ledger** (see sections 4C and 4F).

---

## 4. Gating rubric

### A. Coverage

- **A1** Every table-of-contents entry (chapter, section, subsection, named idiom) maps to at least one node or leaf in the coverage manifest. No unmapped entries.
- **A2** Every chapter, section and idiom is reachable from the router by following navigation links only (no orphans). Verify by graph traversal from the router.
- **A3** Every idiom box in the book has an idiom card. The implementer recounts idiom boxes from the source rather than trusting the count in section 2.
- **A4** Chapters with few or no idiom boxes (notably ch10 colour and ch11 manipulate) MUST still have structured, card-like leaves for their core idioms and guidance (e.g. colormap types, interaction idioms), so that routing is not coarser there than elsewhere.
- **A5** All nodes and leaves are reachable without relying on the book's absent indexes. The implementer builds an idiom and concept lookup (name to node) as part of the router or a linked index node.

### B. Navigation precision

Every node MUST contain, for each child:

- **B1** a **use-when condition**: the data type, task, or situation in which this child is the right next step. It must be a decision criterion, not a restatement of the child's title.
- **B2** a **link to the child** with its approximate size (so the agent can budget reads). *(Size is a SHOULD unless a limit is set in section 6.)*

Every node MUST also contain:

- **B3** **related links**: pointers to relevant sections elsewhere in the book (cross-chapter included), each with one line saying why it is related. Seed these from the book's in-text "Section x.y" references and add missing ones where the book's own cross-references leave a gap.
- **B4** a **disambiguation note** for every group of sibling children that overlap. Siblings overlap when a single query could plausibly satisfy the use-when conditions of two or more of them (e.g. bar chart vs. dot chart vs. line chart). The note states what separates them. Where siblings do not overlap, no note is required.
- **B5** The router lists the entry points for J1-J4 and a data-type by task routing table (built from the book's data and task chapters) pointing to specific section or idiom nodes, not only chapters.
- **B6** Every node is self-sufficient for deciding the next hop: an agent reading only the node can pick a child without opening any child.

### C. Fidelity and provenance

- **C1** **Verbatim text matches the source exactly.** Any text marked as verbatim, after whitespace and hyphenation normalisation, is a substring of the corresponding source pages' extracted text. Verify programmatically.
- **C2** **Every summary claim traces to a cited page.** Each summary leaf or paragraph cites the PDF page(s) it is based on, at claim or paragraph granularity at least. No uncited summary statements.
- **C3** **Every leaf cites its PDF page range** in its metadata (and SHOULD also give the printed page range for human use).
- **C4** **Every non-book addition carries a provenance marker** (see section 4E). Unmarked content is assumed to be from the book and MUST be traceable under C1 or C2.
- **C5** **Fidelity ledger:** the implementer chooses verbatim vs. summary per level and documents, for each level (router, chapter node, section node, leaf, idiom card), the choice and the reason. Mixed fidelity is permitted; undocumented mixing is a FAIL.
- **C6** Summaries MUST NOT contradict or add claims to the source. When the source is ambiguous, say so rather than resolve it.

### D. Figures

- **D1** Figure images are extracted as files (about 200 figures), stored in a figure store, and **referenced from the leaves** that discuss them. Each reference includes figure number and caption.
- **D2** A **figure manifest** lists, per figure: figure number, PDF page, file path, caption, and the leaves that reference it.
- **D3** If a figure is vector or composite and cannot be pulled with a plain image-extraction tool, fall back to cropping a rasterised page region (at least 150 DPI). Do not silently omit it.
- **D4** Any figure that could not be extracted is listed in the manifest with the reason. A figure missing without a manifest entry is a FAIL.
- **D5** Each idiom card references the figure(s) that illustrate that idiom, where the book has one.
- **D6** Figure file names follow a deterministic scheme (e.g. `fig-<chapter>-<n>`), and the references in leaves resolve to existing files (link check).

### E. Job support and non-book hints

- **E1** For each of J1-J4, the router gives a named entry point that leads, via nodes only, to the sections that serve it. Examples: J1 to data/task abstraction and idiom selection; J3 to rules of thumb and validation; J4 to multi-view and manipulate chapters.
- **E2** Each idiom card includes an **implementation hints** field: how to realise the idiom in common plotting libraries (e.g. matplotlib and D3 at least). This is the implementer's own knowledge, not the book's.
- **E3** Every hint carries an explicit marker such as `[NOT FROM BOOK]`, visually distinct from book content. Hints MUST NOT carry page citations that imply book support.
- **E4** Hints MUST NOT appear inside verbatim blocks or be mixed into summary text; they live in their own field or section.
- **E5** The book's content is always usable without the hints: removing every marked hint leaves a complete, book-faithful resource.

### F. Verification deliverables

- **F1** **Coverage manifest** (machine-readable): table-of-contents entry, level, node or leaf path, PDF page range.
- **F2** **Link report:** every navigation link and figure reference resolves; zero dead links.
- **F3** **Orphan report:** zero unreachable nodes or leaves.
- **F4** **Provenance report:** counts of verbatim, summary and non-book content per level, and results of the C1 verbatim check.
- **F5** **Self-check report** that runs each gating item above (A1-F4) and records PASS/FAIL with evidence. Any FAIL is either fixed or listed with the reason it could not be.

---

## 5. Suggested orchestration (non-gating)

1. **Shared conventions first (single agent):** ID scheme, metadata fields, marker syntax, node and leaf templates, page-mapping helper, verbatim-check script.
2. **Parallel by chapter:** one subagent per chapter (or per group), each producing its chapter node, section leaves, idiom cards and figure extractions against the shared conventions.
3. **Integration pass (single agent):** build the router, the data-type by task table, the idiom and concept lookup, cross-chapter related links, and disambiguation notes. Disambiguation spans chapters, so it cannot be done per chapter in isolation.
4. **Verification pass:** run the F1-F5 checks and fix failures.
5. **Optional, non-gating:** smoke-test routing with a handful of realistic queries per job. This was not made a pass/fail requirement, but it is the most direct check that "precise next step" actually holds.

---

## 6. Open parameters (not decided in the interview; implementer proposes, owner confirms)

- **Size limits** for nodes and leaves. Suggested starting point (unconfirmed): nodes small enough to read in full at every hop, leaves sized to roughly a few book pages each.
- **Directory and file layout and naming**, including how nodes and leaves are distinguished.
- **Whether idiom cards also appear inside their chapter's section tree** or only in a separate catalogue, provided A2 and B6 still hold.

---

## 7. Non-goals

- No requirement to match any particular agent platform's skill format.
- No algorithms, implementation techniques or code reproduced from the book (the book largely excludes them); code appears only as marked hints.
- No rewriting or "improving" the book's claims.
