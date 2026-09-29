---
description: Keep project documentation (AGENTS.md, agent rules, skills, commands and hooks) up to date when code changes make them stale.
applyTo: "**/AGENTS.md"
---

# Keep Documentation Current

If your change adds, removes, renames, or relocates something that appears in project documentation, update that documentation in the same change.

Documentation includes: `AGENTS.md` files, agent rules under `.cursor/rules/`, `.claude/rules/` or `.github/instructions/`, agent skills, agent commands, agent hooks configuration, and `CONTRIBUTING.md`.

## When to update

- Adding, removing, renaming, or moving files/directories referenced in an `AGENTS.md`
- Changing CLI commands, environment variables, or setup steps
- Adding or removing API endpoints, models, schemas, or CRUD modules listed in an `AGENTS.md`
- Altering patterns or conventions described in rules or skills
- Changing the project structure in a way that affects directory tables

## When NOT to update

- Bug fixes to internal implementation not referenced in any documentation
- Changes to test files
- Modifications within a file that don't alter its public interface or documented behaviour

## How to update

- Use the `agents-md` skill for guidance on how to update the `AGENTS.md` file.
- Update only the nearest relevant `AGENTS.md` — don't walk up the hierarchy unless the parent explicitly references what changed.
