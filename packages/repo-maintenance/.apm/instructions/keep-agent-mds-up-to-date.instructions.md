---
description: When a change renames, removes, moves or changes the behaviour of anything, find and fix every agent doc that still describes the old state.
applyTo: "**/*"
---

# Keep agent docs current

Before you finish a change that renames, removes, moves or changes the behaviour of a file, symbol, command, config key, setting, permission, workflow job or test check:

1. Search every doc for the old name and the old behaviour: `rg -n '<old name>' -g '*.md' -g '*.mdc'`, plus docstrings and tool descriptions in the files you touched.
2. Fix every hit in the same change, including sibling and parent `AGENTS.md` files, rules, skills and routing tables, not only the nearest `AGENTS.md`.
3. If you added a skill, contract rule or exception, add it wherever the repository says such things are listed.

Internal changes that no doc mentions need no doc edit.
