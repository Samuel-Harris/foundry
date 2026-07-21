# Architecture Selection Heuristics

Use these heuristics to fit the structure to the repository. They are decision aids, not a mandatory template.

## Contents

- Selection order
- Top-level patterns
- Internal organization
- Dependency direction
- Shared-code rules
- Tooling and enforcement
- Complexity checks

## Selection Order

Make structural decisions from the outside inward:

1. Identify independently run or shipped deployables.
2. Identify business or ownership boundaries.
3. Identify code that genuinely needs reuse or independent enforcement.
4. Add internal layers only to clarify dependency direction.
5. Add shared areas only after naming their exact responsibility and consumers.

Folders should communicate at least one of these facts:

- how the code is operated;
- who or what owns the code;
- what responsibility the code has;
- who may depend on it.

If a folder communicates none of them, remove or rename it.

## Top-Level Patterns

### Deployables plus reusable packages

Use when operational units are clearer than business-domain colocation:

```text
apps/ or services/
  <deployable>/
packages/ or libs/
  <scope>/
    <responsibility>/
```

This is usually the easiest model when frontends, APIs, workers, and CLIs release independently. Keep Python services under `services/` when that distinction makes language-specific tooling or deployment clearer; otherwise one `apps/` collection may be enough.

### Domain-first colocation

Use when a bounded context owns several tightly related deployables and libraries:

```text
domains/ or packages/
  <domain>/
    apps/
    services/
    packages/
shared/
```

Choose this only when domain ownership is more stable and informative than runtime type. Do not use it when developers routinely need to scan all deployables together.

### Single application with internal features

Do not manufacture a large package graph for a repository with one cohesive deployable and little real reuse. A workspace may contain one application whose internal `features/`, `app/`, and narrowly shared areas provide sufficient boundaries.

### Mixed pattern

Combining deployables at the top with domain-scoped reusable packages is often appropriate:

```text
apps/
services/
packages/
  <domain>/
    <type>/
  shared/
    <narrow-purpose>/
```

Use path names consistently. Scope should answer who may use the code; type or responsibility should answer what the code contains.

## Internal Organization

### Feature-oriented frontend

Keep application assembly, routing, and global providers in the application layer. Keep a business feature cohesive:

```text
src/
  app/
  features/
    <feature>/
      api/          # only when needed
      components/   # only when needed
      hooks/        # only when needed
      state/        # only when needed
      types/        # only when needed
      utils/        # only when feature-specific
  components/       # genuinely cross-feature UI
  lib/              # configured third-party or technical adapters
  testing/           # cross-feature test infrastructure
```

Do not pre-create every optional subfolder. Avoid broad barrel exports when direct imports are clearer or the toolchain handles them poorly. Compose peer features in `app/`; do not let one feature reach into another feature's internals.

### Domain and layered code

Use layers when the distinction changes allowed dependencies:

- **domain:** business rules with minimal framework dependencies;
- **application:** use cases and orchestration;
- **infrastructure/data-access:** databases, queues, external services, and framework adapters;
- **interface/UI/API:** inbound delivery mechanisms and presentation.

Do not create layers merely to mirror a diagram. Small scopes may remain one cohesive package until separation creates a real benefit.

### Package extraction test

Extract a directory as its own package/project only when at least one is true:

- multiple consumers need it;
- it has a meaningful public API;
- it benefits from independent dependency declarations or boundary checks;
- it has distinct ownership, release, or testing needs;
- isolating it prevents a known coupling problem.

Otherwise prefer a module inside its owning application or domain.

## Dependency Direction

Define a directed graph, not just folders. A common default is:

```text
narrow shared primitives -> domain logic -> feature/application logic -> deployable composition
```

Adapters may depend inward on interfaces or domain abstractions; domain logic must not depend outward on adapters. Peer domains or features remain independent unless they communicate through an approved contract, event, or composition layer.

For every area, specify:

- allowed upstream dependencies;
- allowed consumers;
- public import surface;
- forbidden peer, inward, or outward dependencies.

Use explicit API or contract packages for deliberate cross-domain sharing. Never make a domain depend on another domain's internal files.

## Shared-Code Rules

Treat `shared`, `common`, `core`, and `utils` as warning labels. Permit a shared area only when all are explicit:

- narrow responsibility;
- intended consumers;
- ownership and change expectations;
- dependency restrictions;
- promotion rule explaining when local code may move there.

Prefer names such as `testing-react`, `ui-primitives`, `auth-contracts`, or `observability-client` over `common` or `helpers`. Keep feature-specific convenience code with the feature even when it could theoretically be reused.

## Tooling and Enforcement

Select tooling only after the graph is known. Verify current ecosystem support before choosing unfamiliar or version-sensitive tools.

### TypeScript and JavaScript

- Use the existing workspace manager when sound; pnpm workspaces are a common lightweight choice.
- Use Nx when its project graph, generators, tags, and affected commands justify the additional framework.
- Use Turborepo when task orchestration and caching are needed without Nx's project model.
- Use `eslint-plugin-boundaries` for path-pattern rules inside or across projects.
- Use Nx module-boundary rules when projects and tags already express the intended graph.
- Use Dependency Cruiser or Sheriff when graph analysis must go beyond ordinary lint rules.
- Give each deployable or real package its own direct dependencies rather than relying on root hoisting.

### Python

- Give each independently deployable service or reusable package its own `pyproject.toml` membership and direct dependencies.
- Use an existing workspace manager when present; uv workspaces are suitable when the repository has chosen uv.
- Use Import Linter for layered and independence contracts.
- Use Tach when explicit module dependencies, public interfaces, or external-dependency checking fit the repository.
- Start with coarse enforceable contracts and tighten them rather than introducing dozens of exceptions.

### Other ecosystems

Use the native workspace, module, dependency, and lint facilities of the chosen ecosystem. Preserve the same architectural contract: explicit projects, explicit direct dependencies, declared public surfaces, and automated illegal-edge detection.

Integrate the selected checks into the repository's normal verification command and CI. Do not add two overlapping tools without a concrete coverage gap.

## Complexity Checks

Reject or simplify a proposal when:

- most packages have one consumer and no independent boundary value;
- domain names duplicate deployable names without adding meaning;
- a new unit requires choosing between `shared`, `common`, `core`, and `utils`;
- generated code or migrations have no explicit owner;
- test utilities could plausibly live in three places;
- boundary rules are documented but cannot be automatically checked despite suitable tooling;
- the directory tree is much larger than the predicted code inventory;
- a developer must understand exceptions before understanding the default.

Prefer a small number of strong rules over a large taxonomy of weak categories.

