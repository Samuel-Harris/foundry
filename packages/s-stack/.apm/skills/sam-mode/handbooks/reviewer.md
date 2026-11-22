# Reviewer

The Review gate examines a phase's change after the phase is VERIFIED. Fresh reviewers on different model families try to break the change through p-stack's `interrogate` skill. They get the change and the repository, and nothing that explains the change in other words, because the code must explain itself.

The phase session reads [Running the gate](#running-the-gate). Each reviewer reads [The brief](#the-brief).

## Running the gate

Read `../interrogate/SKILL.md` relative to the `sam-mode` directory, and follow it with these changes.

1. **The scope.** The first review covers the phase diff, `git diff <orchestrator branch>...<phase branch> -- . ':(exclude).foundry'`. Every later review covers what changed since the code head of the most recent `CLEAR` or `SIGNIFICANT` review, never a `WAIVED` one, and only the phase's own work. That is each commit in `git log --first-parent --no-merges <last reviewed code head, not waived>..<phase branch> -- . ':(exclude).foundry'`, and the conflict resolution of each merge commit in `git log --first-parent --merges <last reviewed code head, not waived>..<phase branch>`, from `git show --remerge-diff <merge commit>`. End the range at the phase branch, not at the code head. After the orchestrator has merged the phase, the code head command can name a commit on the orchestrator branch, and a range ending there walks the orchestrator's history. A clean merge shows nothing there. Another phase's code arrives only through merges, and its own gate reviewed it.
2. **Earlier findings.** After a SIGNIFICANT verdict, give every reviewer the command of each significant finding from the earlier reviews, as a probe to run again at the new code head. A probe that still shows the failure is a significant finding of this review.
3. **The intent.** `interrogate` states the intent from the user's message. For a phase session that message is the plan, which the reviewers may not see. State the intent from the commit messages in the scope and the code alone. Never quote or paraphrase the roadmap, a plan or the status file.
4. **One reviewer first.** Start one reviewer on one model family, and say in its brief that it is the first reviewer. It reads the scope and either returns `WAIVED` with its reason, or reviews. When it reviews, start the second adversary on the other model family, as `interrogate` says.
5. **The brief.** Give each reviewer `interrogate`'s own brief, then the absolute path of this file and the instruction to read [The brief](#the-brief). Give it nothing from `.foundry/`. Each reviewer's worktree of the phase branch contains `.foundry/`, and only the brief keeps the reviewer out of it.
6. **Classify** each finding that `interrogate` returns as significant or not, by the rule in [The brief](#the-brief).
7. **The verdict.** SIGNIFICANT when at least one finding is significant. CLEAR when none is. WAIVED when the first reviewer waived. The verdict names the code head that the scope ends at.

Record the verdict in the status file. Put every finding in the evidence file, with its command, its output and your classification. A finding that is not significant changes no state, and you may still fix it in a later commit.

## The brief

You are a reviewer for one change. Break it, as `interrogate`'s brief says.

**What you may read.** The change your scope names, and the repository it changes, outside `.foundry/`.

**What you must not read.** Anything under `.foundry/`, a roadmap, a plan, a status file or the implementer's notes, wherever you find them. Do not ask for them. If the change cannot be understood without them, that is itself a finding: say which part a reader of the change cannot follow.

**Probes.** Run every probe your brief gives you at the current code head, and report each one's output.

**Waiving.** If your brief says you are the first reviewer, you may return `WAIVED` instead of reviewing, under the waiver rule in `references/status-and-messages.md`, with your reason. You may not waive while a probe from an earlier significant finding still shows the failure.

**What counts as significant.** A finding is significant when a run shows that the change does one of these things:

- It crashes, hangs or gives a wrong result on input it is meant to accept.
- It loses or corrupts data, or leaves state that the next run cannot recover from.
- It opens a security hole, such as an injection, a leaked secret or a widened permission.
- It breaks a documented contract, such as a command-line interface, a file format, an API or a rule in the repository's own instructions.
- It breaks the repository's build, tests or checks.
- For an instruction that an agent follows, such as a skill or a handbook, it leads a reader to the wrong action, or two of its statements contradict each other. A cold read by a fresh subagent is the run that proves it.

A preference between two working designs is not significant, and neither is anything `interrogate`'s brief tells you to leave out.

**Your report.** Report as `interrogate`'s brief says, and add whether you judge each finding significant and why.
