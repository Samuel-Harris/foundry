---
name: git-diff-staged-changes-main
description: Show staged changes compared to origin/main. Use when the user asks for the diff of staged changes against main.
disable-model-invocation: true
---

Run `git --no-pager diff --cached --merge-base origin/main`
