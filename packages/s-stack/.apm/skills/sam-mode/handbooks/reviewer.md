# Reviewer

The Review gate examines a phase's diff after the phase is VERIFIED. Fresh reviewers on different model families try to break the change through p-stack's `interrogate` skill. They get the diff and the repository, and nothing that explains the change in other words, because the code must explain itself.

This handbook has two parts. The phase session reads [Running the gate](#running-the-gate). Each reviewer reads [The brief](#the-brief).

## Running the gate

`interrogate` sets `disable-model-invocation: true`, so the Skill tool cannot load it. Read `../interrogate/SKILL.md` relative to the `sam-mode` directory, and follow it with the changes below.

1. **The scope.** The first review of a phase covers the phase diff, `git diff <orchestrator branch>...<phase branch> -- . ':(exclude).foundry'`. After a fix, the review covers the commits added since the last reviewed code head, `git diff <last reviewed code head>..<code head> -- . ':(exclude).foundry'`. Name the scope to every reviewer as that command.
2. **The intent.** `interrogate` states the intent from the user's message, the commits and the pull request description. For a phase session, the user's message is the plan, and the reviewers may see no plan. State the intent from the commit messages in the scope and the code alone. Never quote or paraphrase the roadmap, a plan or the status file.
3. **The brief.** Give each reviewer `interrogate`'s own brief, then tell it to read [The brief](#the-brief) in this file. Give it nothing from `.foundry/`.
4. **The worktrees.** `interrogate` gives each reviewer a worktree of the phase branch, and that worktree contains `.foundry/`. Only the brief keeps the reviewers out of it.
5. **Classify.** `interrogate` returns only findings that a rerun proved. Classify each one as significant or not, by the rule in [The brief](#the-brief).
6. **The verdict.** SIGNIFICANT when at least one verified finding is significant. CLEAR when none is. The verdict names the code head that the scope ends at.

Record the verdict in the status file. Put every verified finding in the evidence file, the ones that are not significant included, with the command, its output and your classification. A SIGNIFICANT verdict sends the phase back to Implement. A finding that is not significant changes nothing, and the phase session may still fix it in a later commit.

## The brief

You are a reviewer for one change. Your job is to break it, as `interrogate`'s brief says, and to report what you proved.

**What you may read.** The diff named by your scope, and the repository it changes. Read any file outside `.foundry/` that helps you understand or run the code.

**What you must not read.** Anything under `.foundry/`, a roadmap, a plan, a status file or the implementer's notes, wherever you find them. Do not ask for them. If the change cannot be understood without them, that is itself a finding: say which part a reader of the diff cannot follow.

**What counts as significant.** A finding is significant when a run shows that the change does one of these things:

- It crashes, hangs or gives a wrong result on input it is meant to accept.
- It loses or corrupts data, or leaves state that the next run cannot recover from.
- It opens a security hole, such as an injection, a leaked secret or a widened permission.
- It breaks a documented contract, such as a command-line interface, a file format, an API or a rule written in the repository's own instructions.
- It breaks the repository's build, tests or checks.
- For an instruction that an agent follows, such as a skill or a handbook, it leads a reader to the wrong action, or two of its statements contradict each other. A cold read by a fresh subagent is the run that proves it.

**What is not significant.** Naming, style, formatting, the shape of the code, a preference between two working designs, and a risk that needs some future change before it matters. Do not report these. `interrogate` drops any finding you did not prove with a run.

**Your report.** For each finding, the title, the exact command or cold-read prompt, the output it printed, the output the intent requires, and whether you judge it significant and why. No findings is a valid result.
