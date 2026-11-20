---
name: git-diff-staged-changes-main
description: Show staged and committed changes compared to the merge base with origin/main, excluding unstaged edits. Use when the user asks for the diff of everything staged or committed against main.
disable-model-invocation: true
---

Run `git --no-pager diff --cached --merge-base origin/main`
