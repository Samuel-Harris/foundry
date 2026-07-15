# TypeScript/JS stack: pnpm + Turborepo + Nx boundaries or dependency-cruiser

## Workspaces + Turborepo

- pnpm (or npm/yarn) workspaces own dependency install, linking, and module resolution. **Turborepo is a task orchestrator on top, not a package manager.** `pnpm-workspace.yaml`:
  ```yaml
  packages:
    - "apps/*"
    - "packages/*"
  ```
- `turbo.json` uses `tasks` (the older `pipeline` key is deprecated):
  ```json
  {
    "$schema": "https://turbo.build/schema.json",
    "tasks": {
      "build": { "dependsOn": ["^build"], "outputs": ["dist/**"] },
      "test": { "dependsOn": ["^build"] },
      "lint": {},
      "typecheck": { "dependsOn": ["^build"] },
      "dev": { "cache": false, "persistent": true }
    }
  }
  ```
  `^build` = build dependencies first; bare `"task"` = same-package task first; `pkg#task` targets one package. Caching hashes inputs (sources + deps + config + env) and restores outputs on hit. `turbo run test --filter='...[origin/main]'` runs only affected packages (reported 60–80% CI cuts on single-package PRs in ~15-package repos).
- **Internal package strategies**:
  - *Just-in-Time*: export raw `.ts` via `exports`; consumer's bundler compiles. No build step, not cacheable, can't use `compilerOptions.paths`. Best default for lockstep internal packages.
  - *Compiled*: `tsc` → `dist`, cacheable, needs build config.
  - *Publishable*: full build + versioning for npm.
  Use `exports` maps as the only legal entry points; avoid barrel files (bad for bundlers and compilers). Config-only packages (eslint-config, tsconfig) have no build task.

## Nx module boundaries (when in an Nx workspace, or TS side >~10 projects)

Tag every project (`project.json` → `"tags": ["scope:admin", "type:app"]`), then enforce with the `@nx/enforce-module-boundaries` ESLint rule. Two-dimensional tags are the standard: `scope:*` (domain) + `type:*` (app/feature/ui/util). Untagged projects can depend on nothing unless allow-listed. Errors are agent-legible: "A project tagged with 'scope:admin' can only depend on libs tagged with 'scope:shared' or 'scope:admin'."

```js
// eslint.config.mjs (flat config)
import nx from '@nx/eslint-plugin';
export default [
  ...nx.configs['flat/base'], ...nx.configs['flat/typescript'],
  { files: ['**/*.ts', '**/*.tsx', '**/*.js', '**/*.jsx'],
    rules: { '@nx/enforce-module-boundaries': ['error', {
      allow: [],
      depConstraints: [
        { sourceTag: 'scope:shared', onlyDependOnLibsWithTags: ['scope:shared'] },
        { sourceTag: 'scope:admin',  onlyDependOnLibsWithTags: ['scope:shared', 'scope:admin'] },
        { sourceTag: 'scope:store',  onlyDependOnLibsWithTags: ['scope:shared', 'scope:store'] },
        { sourceTag: 'type:app',     onlyDependOnLibsWithTags: ['type:feature', 'type:ui', 'type:util'] },
        { sourceTag: 'type:feature', onlyDependOnLibsWithTags: ['type:ui', 'type:util'] },
        { sourceTag: 'type:ui',      onlyDependOnLibsWithTags: ['type:ui', 'type:util'] },
        { sourceTag: 'type:util',    onlyDependOnLibsWithTags: ['type:util'] },
      ] }] } },
];
```

`allSourceTags` requires multiple tags on the source side for multi-dimensional constraints.

## dependency-cruiser (framework-agnostic default outside Nx)

`npx depcruise --init` scaffolds sensible defaults (no-circular, no-orphans, missing-deps, prod-not-to-dev). Rules are `forbidden`/`allowed`/`required` with `from`/`to` **regex** conditions (not globs), including `$1` back-references. The canonical "features must not import each other" rule:

```js
// .dependency-cruiser.js
module.exports = {
  forbidden: [
    { name: 'no-circular', severity: 'error', from: {}, to: { circular: true } },
    { name: 'apps-not-to-apps',
      comment: 'One app must not depend on another app',
      severity: 'error',
      from: { path: '^apps/([^/]+)/' },
      to:   { path: '^apps/', pathNot: '^apps/$1/' } },
    { name: 'packages-not-to-apps',
      severity: 'error',
      from: { path: '^packages/' },
      to:   { path: '^apps/' } },
  ],
};
```

Run: `npx depcruise apps packages --config .dependency-cruiser.js`. Output is ESLint-style (file → file, rule name) — agent-legible.

Choosing: **dependency-cruiser** when you want boundary rules plus dead-code/circular detection and aren't on Nx; **Nx's rule** when already in an Nx workspace or the TS side is large; Sheriff is a third option for folder-level rules without tags.

## tsconfig project references

Use `references` + `"composite": true` per package so `tsc --build` type-checks in dependency order with incremental builds. Pair with `exports` subpath imports (TS 5.4+) rather than `compilerOptions.paths` for JIT packages.
