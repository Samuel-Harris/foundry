# TypeScript/JavaScript stack: pnpm + Turborepo + Nx or dependency-cruiser

## Workspaces and Turborepo

pnpm (or npm/yarn) workspaces own installation, linking, and module resolution; Turborepo is a task orchestrator on top, not a package manager.

```yaml
packages:
  - "apps/*"
  - "packages/*"
```

Use the current `tasks` key in `turbo.json` (the older `pipeline` key is deprecated):

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

`^build` builds dependencies first; a bare task runs in the same package first; `pkg#task` targets one package. Caching hashes inputs (sources, dependencies, config, and environment) and restores outputs on a hit. For affected CI, use a filter such as `turbo run test --filter='...[origin/main]'`, which runs only affected packages (reported 60–80% CI cuts on single-package PRs in ~15-package repositories).

Choose one internal-package strategy:

- **Just-in-time:** export raw TypeScript (`.ts` via `exports`) and let the consumer's bundler compile it. No build step, not cacheable, and cannot use `compilerOptions.paths`. The default for lockstep internal packages.
- **Compiled:** build with `tsc` into `dist` for cacheable output; needs build configuration.
- **Publishable:** build and version for npm.

Use `exports` maps as the only legal entry points. Avoid broad barrel files (bad for bundlers and compilers). Config-only packages (eslint-config, tsconfig) need no build task.

## Nx module boundaries

Use Nx when already in an Nx workspace, when the TypeScript side has roughly ten or more projects, or when affected execution and remote caching justify it.

Tag every project (`project.json` → `"tags": ["scope:admin", "type:app"]`) with dimensions such as `scope:admin` and `type:app`, then configure `@nx/enforce-module-boundaries`:

```js
import nx from "@nx/eslint-plugin";

export default [
  ...nx.configs["flat/base"],
  ...nx.configs["flat/typescript"],
  {
    files: ["**/*.ts", "**/*.tsx", "**/*.js", "**/*.jsx"],
    rules: {
      "@nx/enforce-module-boundaries": [
        "error",
        {
          allow: [],
          depConstraints: [
            {
              sourceTag: "scope:shared",
              onlyDependOnLibsWithTags: ["scope:shared"],
            },
            {
              sourceTag: "scope:admin",
              onlyDependOnLibsWithTags: ["scope:shared", "scope:admin"],
            },
            {
              sourceTag: "scope:store",
              onlyDependOnLibsWithTags: ["scope:shared", "scope:store"],
            },
            {
              sourceTag: "type:app",
              onlyDependOnLibsWithTags: [
                "type:feature",
                "type:ui",
                "type:util",
              ],
            },
            {
              sourceTag: "type:feature",
              onlyDependOnLibsWithTags: ["type:ui", "type:util"],
            },
            {
              sourceTag: "type:ui",
              onlyDependOnLibsWithTags: ["type:ui", "type:util"],
            },
            { sourceTag: "type:util", onlyDependOnLibsWithTags: ["type:util"] },
          ],
        },
      ],
    },
  },
];
```

Two-dimensional tags are the standard: `scope:*` (domain) plus `type:*` (app/feature/ui/util). Untagged projects can depend on nothing unless explicitly allowed. Errors are agent-legible: "A project tagged with 'scope:admin' can only depend on libs tagged with 'scope:shared' or 'scope:admin'." Use `allSourceTags` when a source constraint requires multiple tags.

## dependency-cruiser

Use dependency-cruiser as the framework-agnostic default outside Nx. `npx depcruise --init` scaffolds sensible defaults (no-circular, no-orphans, missing-deps, prod-not-to-dev); then encode boundaries with `forbidden`, `allowed`, or `required` rules. Paths are regular expressions, not globs, and support `$1` back-references.

```js
module.exports = {
  forbidden: [
    {
      name: "no-circular",
      severity: "error",
      from: {},
      to: { circular: true },
    },
    {
      name: "apps-not-to-apps",
      comment: "One app must not depend on another app",
      severity: "error",
      from: { path: "^apps/([^/]+)/" },
      to: { path: "^apps/", pathNot: "^apps/$1/" },
    },
    {
      name: "packages-not-to-apps",
      severity: "error",
      from: { path: "^packages/" },
      to: { path: "^apps/" },
    },
  ],
};
```

Run `pnpm exec depcruise apps packages --config .dependency-cruiser.js`. Output is ESLint-style (file → file, rule name), so it is agent-legible; preserve named, error-severity rules so output identifies the violated contract.

Choosing: dependency-cruiser when you want boundary rules plus dead-code and circular detection and are not on Nx; Nx's rule when already in an Nx workspace or the TypeScript side is large; Sheriff is a third option for folder-level rules without tags.

## TypeScript project references

Use project `references` plus `"composite": true` per package so `tsc --build` checks packages in dependency order and incrementally. Pair references with package `exports` subpaths (TS 5.4+) instead of `compilerOptions.paths` for just-in-time packages.
