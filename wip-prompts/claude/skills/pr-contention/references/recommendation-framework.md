# Recommendation Framework

The primary goal of recommendations is to **maximise merge parallelism** — decouple PRs so as many as possible can merge independently.

After completing the analysis and conflict investigation, generate recommendations using this priority schema. Each recommendation must include:

- **What**: A concrete, actionable description
- **Why**: The specific contention risk it addresses
- **PRs affected**: Which PR numbers AND titles are involved
- **Implementation**: Brief description of what executing this recommendation entails

Always refer to PRs by number AND title: `#14476 (Optimise vector db migration)`.

---

## P0 — Critical (high impact, low effort)

Assign P0 when the recommendation resolves an **active or imminent conflict** with minimal work.

Triggers:
- A PR has `mergeable: CONFLICTING` — recommend immediate rebase
- Two PRs have CONFLICTING files in the same function/class/config block AND one is a clear superset of the other — recommend stacking
- A PR is a strict subset of another PR's changes — recommend merging them or stacking
- Two PRs rename/restructure the same file differently — recommend consolidating

Example recommendations:
- "Rebase #14466 (OCR skip for public PDFs) onto dev to resolve existing merge conflict"
- "Stack #14476 (Optimise migration) onto #14463 (Verification): retarget base from dev to sam/eng-5535-..."

---

## P1 — Important (high impact, moderate effort)

Assign P1 when the recommendation **prevents future conflicts or increases parallelism** with moderate work.

Triggers:
- Conflict investigation shows two PRs could be independent but share CONFLICTING files that could be extracted — recommend extracting shared changes into a prep PR to decouple them
- Hot files (touched by 3+ PRs) that should be extracted into a prep PR
- A PR bundles infrastructure/config changes with application logic, and extracting one layer would make it independent of another PR — recommend splitting
- A cluster of 3+ PRs in the same area with no explicit dependency ordering — recommend defining a merge sequence
- PRs that are 50+ commits behind dev — recommend proactive rebase

Example recommendations:
- "Extract shared migration script changes from #14476 and #14463 into a prep PR to allow both to merge independently"
- "Split #14463 (Verification) into code/infra + data PRs — the 244k data files slow CI and block review"
- "Define merge order for the vector-db cluster: #14449 → #14463 → #14476 (rebase each after previous merges)"

---

## P2 — Recommended (moderate impact)

Assign P2 for improvements that **reduce future contention risk** but aren't urgent.

Triggers:
- DEPENDENT files (auto-mergeable but semantically coupled) that warrant a post-merge review
- PRs older than 14 days — recommend prioritising review or breaking into smaller pieces
- Documentation-only overlaps across PRs (AGENTS.md, README, skills) — recommend batching doc updates
- Directory-level overlaps (different files in the same directory) that signal potential logic conflicts

Example recommendations:
- "#14476 and #14463 both rewrite prepare-shared-db-snapshot/action.yml — auto-merges but review the combined result"
- "PR #X is 3 weeks old with 300+ changed files — consider breaking into smaller PRs"

---

## P3 — Nice to Have (lower impact)

Assign P3 for workflow improvements and low-risk observations.

Triggers:
- PRs with no overlaps but high staleness (>21 days) — recommend pinging reviewers
- IDENTICAL files across PRs (shared prerequisite work) — note that whichever merges first makes the duplicate a no-op
- Minor config file overlaps (.gitignore entries, package.json version bumps) that will auto-resolve
- Suggestions for labelling PRs with dependency info for reviewer awareness

Example recommendations:
- "Add `[depends: #14449]` to #14476's description to signal merge order to reviewers"
- "9 files are IDENTICAL between #14476 and #14449 — shared prerequisite work, auto-resolves"
