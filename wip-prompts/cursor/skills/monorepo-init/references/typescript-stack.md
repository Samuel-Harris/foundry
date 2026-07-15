# TypeScript/JavaScript stack: pnpm + Turborepo + Nx or dependency-cruiser

## Workspaces and Turborepo

pnpm workspaces own installation, linking, and module resolution. Turborepo orchestrates tasks.

```yaml
packages:
  - "apps/*"
  - "packages/*"
```

Use the current `tasks` key in `turbo.json`:

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

`^build` builds dependencies first; a bare task runs in the same package first; `pkg#task` targets one package. For affected CI, use a filter such as `turbo run test --filter='...[origin/main]'`.

Choose one internal-package strategy:

- **Just-in-time:** export raw TypeScript and let the consumer compile it. Default for lockstep internal packages.
- **Compiled:** build with `tsc` into `dist` for cacheable output.
- **Publishable:** build and version for npm.

Use `exports` maps as legal entry points. Avoid broad barrel files. Config-only packages need no build task.

## Nx module boundaries

Use Nx when already in an Nx workspace, when the TypeScript side has roughly ten or more projects, or when affected execution and remote caching justify it.

Tag every project with dimensions such as `scope:admin` and `type:app`, then configure `@nx/enforce-module-boundaries`:

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

Untagged projects can depend on nothing unless explicitly allowed. Use `allSourceTags` when a source constraint requires multiple tags.

## dependency-cruiser

Use dependency-cruiser as the framework-agnostic default outside Nx. Initialise its version-compatible config, then encode boundaries with `forbidden`, `allowed`, or `required` rules. Paths are regular expressions, not globs.

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

Run `pnpm exec depcruise apps packages --config .dependency-cruiser.js`. Preserve named, error-severity rules so output identifies the violated contract.

## TypeScript project references

Use project `references` plus `"composite": true` so `tsc --build` checks packages in dependency order and incrementally. Pair references with package `exports` subpaths instead of `compilerOptions.paths` for just-in-time packages.
