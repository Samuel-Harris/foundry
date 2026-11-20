---
name: summarise-pr
description: Summarise provided PR change context into concise PR-description bullets. Use when the user asks for a PR description summary, major changes, or design decisions, or invokes this skill after another skill or command has supplied the change context.
disable-model-invocation: true
---

# Summarise PR

Turn change context that is already in the conversation into a concise pull-request description. This skill is manual-invocation only: it never gathers context itself, it summarises what the caller provides.

## Input

The caller supplies the change context — a diff, changed-file summary, commit list, or an implementation plan. If no change context is present, ask the user to provide it (or to run a diff first); do not go looking for it.

## Output

Produce a PR description in this shape:

```markdown
## Summary

- <1–3 bullets: what changed and why it matters, and what will behave differently for users or in production once this merges, including any infrastructure resources created, replaced or destroyed>

## Changes

- <grouped, concise bullets of the major changes>

## Design decisions

- <notable decisions and rejected alternatives, only where they matter>

## Test plan

- [ ] <how the change was verified>
```

Rules:

- Lead with the outcome, not the mechanics. Say why the change exists before listing what moved.
- One bullet per idea. Prefer a few high-signal bullets over an exhaustive list.
- Name every user-facing feature and every production or infrastructure effect in the supplied context; these may not be compressed away by 'a few high-signal bullets'.
- Summarise by logical change, not by file.
- Keep the description consistent with the repository's existing PR style when one is available.
- Omit a section entirely when it has nothing meaningful to say; never emit empty placeholder bullets.
- Do not invent tests, evidence, or design rationale that the supplied context does not support.
- Check every factual sentence against the supplied diff before returning; drop or correct any that the diff contradicts or that describe an earlier state of the branch.
- If the supplied context is partial (truncated diff, file list only), say which parts the description was written from; never claim it was written from the full diff.
