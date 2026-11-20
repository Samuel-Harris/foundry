---
name: principle-never-block-on-the-human
description: "Apply when tempted to ask 'should I do X?' on reversible work."
disable-model-invocation: true
---

# Never Block on the Human

The human supervises asynchronously. Agents must stay unblocked. Make reasonable decisions, proceed, and let the human course-correct after the fact. Since code changes are reversible and reviewable, a wrong decision usually costs less than blocking.

- Proceed, then present. Do the work, show the result. Don't ask "should I do X?" Do X, explain why.
- Make the system self-healing. When you notice a problem, log it and fix it in the next round.
- Irreversible actions (force-push, delete production data, send external messages) still require confirmation.
- A refused credential, role or sign-in is a blocker, not a reversible choice. Do not switch to a broader profile (such as an admin role), bypass a login, or print or measure a secret value to debug it. Report what was refused and ask the user to re-authenticate or grant access.
- Reversible actions (write code, edit notes, split tasks) should proceed without blocking.
- Once you have recommended an option, take it. Do not ask the user to choose between options you already ranked.
- Check that a command is reversible by reading what it does. A command that moves, deletes or rewrites untracked files (repo `sync`, `clean`, `reset --hard`) is not reversible.
- Product direction comes from the human. Execution should not block.
