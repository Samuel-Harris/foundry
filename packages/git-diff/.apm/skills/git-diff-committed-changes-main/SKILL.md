---
name: git-diff-committed-changes-main
description: Show committed changes on this branch since it diverged from origin/main, excluding staged and unstaged edits. Use when the user asks for the diff of committed work against main.
disable-model-invocation: true
---

Run `git --no-pager diff origin/main...HEAD`
