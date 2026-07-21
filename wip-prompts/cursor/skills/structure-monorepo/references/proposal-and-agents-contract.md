# Proposal and AGENTS.md Contract

Use this contract to make approval informed and future code placement deterministic.

## Contents

- Proposal format
- AGENTS.md hierarchy
- Placement decision procedure
- AGENTS.md quality test

## Proposal Format

Present these sections before requesting approval.

### 1. Repository Model

State:

- observed repository facts;
- user-confirmed purpose and planned features;
- deployables and release boundaries;
- domains or cohesive features;
- important constraints;
- remaining assumptions.

Label inferences. Resolve material uncertainty before continuing.

### 2. Proposed Technology Stack

Use a table:

| Concern | Choice | Existing or new | Why it fits | Rejected alternative |
| --- | --- | --- | --- | --- |
| Workspace | ... | ... | ... | ... |
| Build/tasks | ... | ... | ... | ... |
| Package management | ... | ... | ... | ... |
| Tests/lint/types | ... | ... | ... | ... |
| Boundary enforcement | ... | ... | ... | ... |
| CI/deployment | ... | ... | ... | ... |

Include application frameworks, languages, persistence, generated clients, and container tooling when they influence structure. Do not replace user-selected product technology without explaining the incompatibility or decisive benefit.

### 3. Complete Annotated Skeleton

Show one tree from the repository root. Include:

- meaningful planned directories;
- root and project manifests;
- workspace and task configuration;
- test, lint, type, boundary, CI, container, and deployment configuration;
- `AGENTS.md` locations;
- existing files that remain relevant.

Annotate each meaningful entry with its single responsibility. Mark planned skeleton areas distinctly from existing populated areas. Do not use `...` to hide an unresolved architectural branch.

### 4. Placement and Dependency Rules

For every architectural area, state:

| Area | Put here | Do not put here | May depend on | Intended consumers |
| --- | --- | --- | --- | --- |
| `path/` | ... | ... | ... | ... |

Then show the allowed dependency direction. Name any explicit public interfaces and cross-domain contracts.

### 5. Code-Placement Simulation

Derive examples from the actual planned product rather than generic `foo` modules:

| Likely code unit | Exact destination | Why only this location fits | Allowed dependencies | Consumers |
| --- | --- | --- | --- | --- |
| ... | ... | ... | ... | ... |

Include boundary cases and likely pressure toward shared code. The proposal fails if any row admits two equally valid destinations or requires an undocumented exception.

### 6. AGENTS.md Plan

List every planned `AGENTS.md`, its scope, and the decisions it will add beyond its parent. Include enough files to anchor the meaningful skeleton in version control, but avoid one file per trivial leaf directory.

### 7. Brownfield Migration

For existing repositories, include:

| Current source | Target | Operation | Import/config impact | Risk |
| --- | --- | --- | --- | --- |
| ... | ... | move/split/merge/delete | ... | ... |

List obsolete files to remove, compatibility shims to add temporarily, baseline behavior to preserve, and verification commands. Architecture approval authorizes this repository-local migration; do not add a redundant approval gate.

### 8. Verification and Non-Goals

List exact commands or checks for:

- dependency boundaries;
- direct dependency declarations;
- lint, types, and tests;
- builds and per-deployable packaging;
- stale imports and paths;
- code-placement clarity.

State what will not be implemented, especially product features represented only by skeleton directories.

### 9. Approval Request

Ask the user to approve the entire proposal. Make clear that approval authorizes implementation and, for brownfield repositories, all listed moves, renames, configuration changes, and deletions needed to reach the target.

If any preceding section changes materially, present the revised proposal and request approval again.

## AGENTS.md Hierarchy

Use hierarchical guidance. The closest applicable file adds local rules; it should not repeat its ancestors.

### Root AGENTS.md

Cover:

- repository purpose and architecture summary;
- complete top-level responsibility map;
- canonical dependency direction;
- workspace-wide naming and placement decision process;
- standard install, lint, type, test, build, boundary, and packaging commands;
- rule that deployables compose and packages do not import from deployables;
- shared-code promotion criteria;
- generated-code and migration policies;
- pointers to deeper `AGENTS.md` files.

### Deployable AGENTS.md

Cover:

- runtime purpose and entry points;
- what is composed locally versus imported from packages;
- internal structure and feature rules;
- local test, build, and run commands;
- allowed dependencies and forbidden package internals;
- deployment-specific configuration placement.

### Domain or Package-Group AGENTS.md

Cover:

- domain responsibility and vocabulary;
- owned concepts and excluded concerns;
- allowed internal layer direction;
- public contracts and consumers;
- peer-domain isolation rules;
- exact criteria for creating another package or module.

### Shared-Area AGENTS.md

Cover:

- narrow shared responsibility;
- eligible and ineligible code;
- supported consumers;
- stability and public API expectations;
- promotion review questions;
- prohibition on application or feature-specific convenience code.

## Placement Decision Procedure

Include this procedure, adapted to the approved paths, in root guidance:

1. Identify the deployable, domain, or feature that owns the behavior.
2. Keep the code with that owner unless there is a demonstrated cross-owner consumer or independent boundary need.
3. Select the responsibility layer from what the code does, not what framework type it uses.
4. Place integrations at the edge and business rules inward.
5. Promote code to a narrowly named shared package only when its consumers and public contract are explicit.
6. If two destinations still qualify, stop and clarify or revise the architecture; do not choose by preference.

## AGENTS.md Quality Test

After writing the hierarchy, answer these questions using only the applicable `AGENTS.md` files:

- Where does a new route or entry point go?
- Where does feature-specific UI, state, and data access go?
- Where does a business rule independent of delivery technology go?
- Where does an external-service adapter go?
- Where do cross-domain schemas or contracts go?
- When may local code become shared?
- Which imports are forbidden?
- Which command proves the dependency graph is legal?

Revise the guidance if an answer is missing, conflicting, or admits multiple destinations.
