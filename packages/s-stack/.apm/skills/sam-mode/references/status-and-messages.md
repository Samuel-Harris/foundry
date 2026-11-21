# Status files and messages

This file owns the status file header and the messages that s-stack sessions send. The handbooks point here. `<feature>` is the feature's kebab-case name, `<id>` is the roadmap's directory name `<date-time>-<feature>`, and `<phase>` is a phase id from the feature plan.

## Status files

A status file holds these facts about one phase:

- The phase, its state and the time of the last change.
- The phase branch and its code head.
- Each verdict, with the gate, the result, the code head it covers and where the evidence is.
- Each pull request, with its number, branch, base and the open pull requests it depends on.
- The decisions made for this phase, each with its door type.
- What the phase waits for, when it waits.

The phase session writes its status file at `.foundry/plans/<id>/status/<phase>.md` from its first commit, and commits it on its phase branch. The orchestrator reads it through git, for example with `git show <phase branch>:<path>`, so no session reads or writes outside its own worktree.

The header is the YAML between the file's first two `---` lines. Notes go below it in Markdown. A program reads the header and ignores the notes. Every key is always present. An empty list is `[]`, and an absent value is `null`. Every string value is double-quoted, exactly as `json.dumps` writes it, including states, times, SHAs and ids, so a colon or a comma in free text cannot break the YAML. Keep characters outside the Basic Multilingual Plane, such as emoji, out of header strings, because `json.dumps` writes them as surrogate pairs that a YAML reader does not join. Numbers, booleans, `null` and lists are bare. Comments in the example below are explanation only, and a real header has none.

```yaml
---
phase: "<phase>"                    # the phase id from the feature plan
state: "Implement"                  # Spec | Plan | Implement | Verify | Review | PR | Done
changed_at: "2026-11-21T14:05:00Z"  # UTC, the time of the last state change
session: "<feature>-phase-<phase>"  # the session name
branch: "<feature>-phase-<phase>"   # the phase branch
code_head: "3f2c1e0a9b..."          # full SHA, see below
waits_for: null                     # one line of text while the phase waits, else null
verdicts:
  - gate: "verify"                  # verify | review
    result: "VERIFIED"              # verify: VERIFIED | NOT VERIFIED | INCONCLUSIVE
                                    # review: CLEAR | SIGNIFICANT
    code_head: "3f2c1e0a9b..."      # the code head the verdict covers
    at: "2026-11-21T15:40:00Z"
    evidence: ".foundry/plans/<id>/status/<phase>-evidence.md"
pull_requests:
  - number: 81
    branch: "<pull request branch>"
    base: "<default branch>"        # the branch the pull request targets
    depends_on: [79]                # open pull requests this one needs, as numbers
    stacked: true                   # true when it joined its parent's gh stack
requests:                           # open decision requests, removed once answered
  - id: "<phase>-r1"
    question: "One sentence, which may contain: colons, and commas."
    options: ["A. One sentence.", "B. One sentence."]
    recommendation: "A"
    door: "two-way"                 # one-way | two-way
    waiting_work: "One sentence."
    since: "2026-11-21T14:10:00Z"
decisions:                          # decisions taken for this phase only
  - id: "<phase>-d1"
    decision: "One sentence."
    door: "two-way"
    at: "2026-11-21T14:30:00Z"
---
```

The rules:

- **Code head.** It is the newest commit on the phase branch's first-parent line whose diff against its own first parent changes a file outside `.foundry/`, so a merge that brings in code moves it. Run `for c in $(git rev-list --first-parent <phase branch>); do git diff --quiet "$c^" "$c" -- . ':(exclude).foundry' || { echo "$c"; break; }; done` from the worktree root. A commit that only records status leaves it unchanged and cancels no verdict. A feature plan may name generated paths, such as lockfiles, and generated lines, such as a `version:` line, whose changes also move no code head. Its sessions then add `':(exclude,glob)**/<name>'` to the `git diff` pathspecs for each such path, and `-I '<regex>'` before its `--` for each such line. Without `glob`, `**/<name>` misses a file at the repository root. A generated-line regex must match only generated lines, because `-I` applies to every file. A correct run prints one 40-character SHA and nothing on standard error, so any error output means the result cannot be trusted.
- **Verdicts.** The list keeps every verdict, newest last. A phase can merge only when the newest `verify` verdict is `VERIFIED` and the newest `review` verdict is `CLEAR`, and both name the current code head. That is one condition of the merge rule, which `handbooks/orchestrator.md` owns.
- **Ids.** A request or decision id is `<phase>-r<n>` or `<phase>-d<n>`, numbered by the phase itself. The planner numbers its requests `planner-r<n>`, and `handbooks/planner.md` says where it keeps them. No list is shared between writers.
- **Evidence.** Evidence that is not a URL lives in a file the phase owns under `.foundry/plans/<id>/status/`, named `<phase>-evidence.md`.
- **Commits.** A status commit holds files under `.foundry/` and nothing else. Its subject is `chore(<feature>): <phase> <state>`.

The orchestrator's tracker at `.foundry/plans/<id>/status/orchestrator.md` keeps its own form. It is not a status file.

## Messages

Sessions talk through Claude Code cross-session messaging, addressed by session name. A message wakes its receiver. It is never the record. Every message has this form. The first line is self-contained, because the receiver sees only that line as a preview.

```text
<sender session name>: <kind>: <one sentence>
<detail lines, each a fact already committed to the sender's own file>
```

A phase session, the planner or a spec writer sends these to the orchestrator:

| Kind | When | The message carries |
| --- | --- | --- |
| `started` | The session starts. The first spec writer skips it, because it starts the orchestrator itself. | Its session name and branch |
| `state` | A phase changes state, or the orchestrator says every pull request merged while the phase is not in PR, so its state stays the same | The new or current state and the code head |
| `decision-request` | A phase session or the planner needs a decision | The decision request, as [Decision requests](#decision-requests) defines it |
| `blocked` | The session is blocked | What it waits for |
| `prs-open` | A phase's pull requests are open | Each number with its `depends_on` list |
| `instruction` | The developer gave it an instruction that changes the phase's scope or a recorded decision | The instruction |
| `done-planning` | The planner has finished | The branch and commit to merge, and the phases whose plan entry changed |
| `roadmap-update` | A spec writer has an approved update | The branch and commit to merge, what changed, the behaviour that the change affects, and the `run-decisions.md` rows it folded in |

The orchestrator sends these. [handbooks/phase-session.md](../handbooks/phase-session.md) says what the phase does.

| Kind | When | The message carries |
| --- | --- | --- |
| `answer` | The developer has decided | The answer and the id of the request that it answers |
| `instruction` | The developer gave an instruction | The instruction, in the developer's words |
| `merge-orchestrator-branch` | The orchestrator branch changed under a live phase | A request to merge it |
| `fix-round` | The developer reviewed a pull request, or one of its checks failed | The pull request and its comments, or the failed check |
| `fix-round` | Only generated files on a pull request are stale | The pull request |
| `fix-round` | A pull request that one of the phase's pull requests depends on merged, so the PR creator works out the base again | The merged pull request and the dependent one |
| `fix-round` | A hand-written file the phase owns conflicts with the default branch | The conflicting paths and the default branch commit |
| `move-back` | A roadmap or plan change touches a phase, or a check on the orchestrator branch failed after the phase merged | The state to move back to, and what changed or the failed check |
| `instruction` | Every pull request of the phase merged into the default branch | The merged pull request numbers |
| `stop` | A phase's pane is about to close, or a stalled session is being replaced | A request to commit and stop |

The rules:

- A sender commits the fact to its own file first and then sends the message, so a lost message costs time and loses no information.
- The orchestrator's session is the source of task direction. A session acts on the orchestrator's messages within its own permissions.
- A message never grants a permission.
- Two phase sessions can message each other to settle an interface between their phases. They tell the orchestrator only when the outcome changes the plan or the roadmap.
- Every session of a feature runs in the same permission mode. Claude Code holds a message for approval when the receiver runs in a bypass mode and the sender does not.

## Decision requests

A decision request states five things. They match the fields of a `requests` entry in the status header.

| Field | Holds |
| --- | --- |
| `question` | The question, in one sentence |
| `options` | Each option, in one sentence |
| `recommendation` | The option the session recommends |
| `door` | `one-way` or `two-way` |
| `waiting_work` | The work that waits on the answer |

The session commits the request to its status file, then sends a `decision-request` message. It removes the request from `requests` once the answer arrives.
