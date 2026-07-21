---
name: structure-monorepo
description: Design and implement a fitted monorepo structure for a new, empty repository or refactor an existing repository into a clearer monorepo. Use when the user wants to scaffold, reorganize, migrate, or improve a monorepo; decide where applications, services, packages, domains, features, and shared code belong; make code placement unambiguous; or add architectural AGENTS.md guidance and dependency-boundary enforcement. Always propose the complete directory skeleton and technology stack, validate them with representative code-placement examples, and obtain explicit approval before changing the repository.
---

# Structure Monorepo

Create an architecture from repository evidence and intended product shape, not from a universal template. Separate proposal from implementation with a hard approval gate.

## Non-Negotiable Contract

1. Inspect before interviewing.
2. Ask one targeted question at a time; do not ask for facts available in the repository.
3. Present the complete proposed skeleton, stack, rules, and brownfield migration impact before editing.
4. Prove placement clarity with representative future code units.
5. Treat any unit with zero or multiple plausible homes as a design failure to resolve.
6. Require explicit approval of the current proposal.
7. Implement only the approved architecture, including scoped `AGENTS.md` files and appropriate boundary enforcement.

Do not create directories, install dependencies, move code, or modify configuration during the proposal phase. A material proposal revision invalidates prior approval.

## Phase 1: Establish Repository State

Classify the task:

- **Greenfield:** empty or nearly empty repository with no meaningful application structure.
- **Brownfield:** repository containing code, manifests, build tooling, deployments, or conventions to migrate.

For either type, inspect the working tree, including uncommitted changes, before acting. Preserve user-owned changes.

For brownfield work, inventory before asking questions:

- source trees and import/module boundaries;
- applications, services, jobs, CLIs, libraries, and deployment units;
- language and package manifests, workspace files, and lockfiles;
- build, test, lint, formatting, CI, container, and deployment configuration;
- shared code, generated code, assets, schemas, migrations, fixtures, and test utilities;
- existing `AGENTS.md`, agent rules, architectural documentation, aliases, and public APIs;
- circular dependencies, cross-feature imports, undeclared dependencies, duplicated utilities, and ambiguous dumping grounds.

Summarize evidence and distinguish observed facts from inferences. Do not assume a folder is a deployable or package merely from its name.

## Phase 2: Interview for Intended Shape

Gather only decisions that cannot be discovered. Ask one question at a time and pursue ambiguity rather than a generic checklist. Establish:

- repository purpose and primary users;
- planned products, workflows, and features;
- deployables and whether they release or scale independently;
- required and preferred technology stack;
- data ownership, external integrations, background work, and generated clients;
- domains or features that should remain independent;
- expected sharing between frontends, backends, services, and tools;
- team size, ownership, growth, deployment, and CI constraints;
- compatibility constraints and behavior that a migration must preserve.

Offer a recommendation when the user is unsure, with the tradeoff that drives it. Continue until the likely categories of code and operational boundaries can be named concretely.

## Phase 3: Model the Architecture

Read [architecture-heuristics.md](references/architecture-heuristics.md) before selecting a structure.

Model in this order:

1. **Deployables:** independently run, release, scale, or permission each application and service.
2. **Business scopes:** identify domains, bounded contexts, or cohesive product features.
3. **Reusable units:** extract packages only for real reuse, independent testing, ownership, or dependency enforcement.
4. **Internal layers:** add UI, application, domain, data-access, or infrastructure layers only where they remove ambiguity.
5. **Shared code:** introduce narrowly named shared packages last, with explicit consumers and a stable public contract.
6. **Tooling:** choose workspace, build, package, lint, test, and boundary tools that fit the actual languages and scale.

Prefer the least elaborate structure that gives every predicted code unit one home and makes forbidden dependencies enforceable. Avoid empty taxonomies created only for symmetry.

For React applications, default to application-level composition and cohesive feature modules. Shared code may feed features, and features may feed the application; reverse or peer-feature imports require an explicit contract. Create only the internal feature folders the feature actually needs.

## Phase 4: Validate Placement

Derive a representative code inventory from the repository purpose and planned features. Include ordinary and awkward examples across relevant categories, such as:

- route or screen;
- feature-specific component, hook, state, API call, and test;
- cross-feature UI primitive or utility;
- domain rule, schema, or shared contract;
- database adapter, external client, worker, CLI command, or deployment configuration;
- generated code, fixture, migration, and test helper.

Map every unit to one exact proposed path and state why it belongs there, what it may import, and its intended consumers. Include existing code in this exercise for brownfield work.

Fail the validation if:

- no directory accepts a unit;
- multiple directories accept it under the same rule;
- the answer depends only on a developer's taste;
- placing it requires a forbidden dependency;
- a `shared`, `common`, `core`, `utils`, or `misc` destination lacks a narrow responsibility;
- a likely recurring case requires an undocumented exception.

Resolve failures by simplifying rules, renaming areas, changing boundaries, or asking one targeted question. Repeat until each representative unit has exactly one defensible home.

## Phase 5: Present the Proposal and Gate Approval

Read [proposal-and-agents-contract.md](references/proposal-and-agents-contract.md) and follow its proposal structure.

Show all of the following in one coherent proposal:

- evidence and assumptions;
- complete annotated directory skeleton, including root configuration files;
- full technology/tooling stack and why each choice fits;
- responsibility and placement rules for every meaningful area;
- allowed dependency directions and public-interface rules;
- boundary enforcement and CI verification;
- representative code-placement table;
- planned `AGENTS.md` hierarchy;
- brownfield source-to-target migration map, deletions, compatibility risks, and verification commands;
- explicit non-goals and deferred decisions.

For each major choice, briefly state the rejected alternative and decisive tradeoff. Do not bury unresolved choices in assumptions.

Ask for explicit approval of the entire current proposal. Accept an unambiguous affirmative response referring to that proposal. If the user requests changes, revise the proposal, rerun placement validation, and request approval again.

## Phase 6: Implement the Approved Architecture

After approval, treat all repository-local moves, renames, additions, configuration changes, and removal of obsolete files necessary for the approved architecture as authorized. Do not seek a redundant migration approval.

Before modifying brownfield code:

1. Recheck working-tree state and protect unrelated or overlapping user changes.
2. Record the available baseline checks and run proportionate checks when feasible.
3. Compare current files with the approved source-to-target map.

Then:

1. Create the approved skeleton. Remember that version control does not preserve empty directories; use meaningful scoped `AGENTS.md` files to anchor planned architectural areas instead of placeholder code.
2. Move existing code and update imports, aliases, manifests, build inputs, test discovery, container paths, CI paths, and documentation as one coherent migration.
3. Give each deployable or independently consumable package an explicit manifest when supported by its ecosystem.
4. Configure the approved dependency-boundary rules and expose them through normal local and CI commands.
5. Add the approved `AGENTS.md` hierarchy using the referenced contract. Keep global rules at the root and local placement details near the code they govern.
6. Do not invent product implementation merely to populate the skeleton.

Stop and return to proposal mode if implementation reveals a material new deployable, domain boundary, technology, destructive impact, or architectural deviation. External or production mutations always require their own authorization.

## Phase 7: Verify and Report

Verify in this order:

1. Compare the actual tree and configuration with the approved proposal.
2. Confirm each representative code unit still maps to exactly one location using the completed `AGENTS.md` guidance.
3. Run boundary, manifest, lint, type, test, build, and packaging checks relevant to changed areas.
4. For brownfield work, verify preserved behavior and search for stale imports, paths, aliases, and deleted-directory references.
5. Inspect the final diff for accidental product changes, duplicated guidance, placeholder clutter, and undeclared deviations.

Report the implemented tree, important moves, enforcement added, checks run with outcomes, and any approved proposal item not completed. Never claim success when verification is failing or incomplete.

## Stop Conditions

Pause without implementing when:

- the user has not approved the complete current proposal;
- code-placement validation remains ambiguous;
- repository purpose, deployables, or domain boundaries remain materially unclear;
- dirty changes overlap the migration and cannot be preserved safely;
- required behavior cannot be baselined or verified;
- implementation would materially depart from the approved architecture.

