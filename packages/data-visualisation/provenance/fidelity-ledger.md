# Fidelity ledger

Which fidelity each level of the resource uses, and why (rubric C5). Unmarked
text is from the book and is either a cited summary (C2) or a checked verbatim
block (C1). Non-book text sits only in `[NOT FROM BOOK]` sections or items.

| Level | Choice | Reason |
| --- | --- | --- |
| Router | Summary, cited, navigation only, no verbatim | Read first on every query, so it must stay small; it routes and holds no content |
| Job nodes and lookup | Summary, cited, navigation only, no verbatim | Same reason as the router; they choose the next hop and point at content |
| Chapter node | Summary, cited, navigation only, no verbatim | Read in full at every hop; content lives in leaves |
| Section node | Summary, cited, navigation only, no verbatim | Same as chapter nodes; a section's opening text lives at the top of its first subsection leaf |
| Leaf (section and subsection) | Mixed: cited summary plus verbatim blocks for definitions, named guidelines and wording that carries the point | Summaries keep each leaf to a few book pages' worth of reading; verbatim keeps the book's exact rules where paraphrase could shift them |
| Idiom card | Mixed: verbatim idiom-box (or System-box) fields, cited summary for the rest, implementation hints marked `[NOT FROM BOOK]` | The box is the book's own compact schema; hints are required by E2 and are the implementer's own knowledge |

<!-- measured-counts:start (written by tools/check.py) -->

## Measured counts

| Kind | Files | Verbatim words | Summary words | Non-book words |
| --- | --- | --- | --- | --- |
| chapter-node | 15 | 0 | 11,996 | 20 |
| idiom-card | 76 | 2,849 | 26,797 | 10,257 |
| index-node | 1 | 0 | 2,765 | 0 |
| job-node | 5 | 0 | 6,185 | 15 |
| router | 1 | 0 | 1,863 | 0 |
| section-leaf | 95 | 6,122 | 32,313 | 0 |
| section-node | 21 | 0 | 11,457 | 0 |
| subsection-leaf | 85 | 5,330 | 30,330 | 30 |

<!-- measured-counts:end -->
