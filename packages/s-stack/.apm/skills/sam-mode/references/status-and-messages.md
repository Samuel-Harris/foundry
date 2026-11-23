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
    result: "VERIFIED"              # verify: VERIFIED | NOT VERIFIED | INCONCLUSIVE | WAIVED
                                    # review: CLEAR | SIGNIFICANT | WAIVED
    code_head: "3f2c1e0a9b..."      # the code head the verdict covers
    at: "2026-11-21T15:40:00Z"
    evidence: ".foundry/plans/<id>/status/<phase>-evidence.md"
pull_requests:
  - number: 81
    branch: "<pull request branch>"
    base: "<default branch>"        # the branch the pull request targets
    depends_on: [79]                # open pull requests this one needs, as numbers
    stacked: true                   # true when it joined its parent's gh stack
pushed: "<branch>=<sha>,<branch>=<sha>"  # the PR creator's last RECORD line, else null
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
    afk: false                      # true for an answer the orchestrator gave in AFK mode, until the developer reviews it
    at: "2026-11-21T14:30:00Z"
---
```

The rules:

- **Code head.** It is the newest commit on the phase branch's first-parent line whose diff against its own first parent changes a file outside `.foundry/`, with one exception. A clean merge of the orchestrator branch moves no code head, because code merged in from it counts as verified and reviewed. A merge of the orchestrator branch is one whose second parent is on the orchestrator branch's first-parent line. It is clean when its tree equals git's automatic merge of its two parents outside `.foundry/`. Any other merge that brings in code moves the code head, a merge of the default branch and a conflict resolution included. Run this under bash from the worktree root:

  ```bash
  ob=$(git rev-list --first-parent <orchestrator branch>)
  for c in $(git rev-list --first-parent <phase branch>); do
    if p2=$(git rev-parse -q --verify "$c^2") && grep -qx "$p2" <<<"$ob"; then
      t=$(git merge-tree --write-tree "$c^1" "$p2" | head -n 1)
      git diff --quiet "$t" "$c" -- . ':(exclude).foundry' && continue
    fi
    git diff --quiet "$c^" "$c" -- . ':(exclude).foundry' || { echo "$c"; break; }
  done
  ```

  A commit that only records status leaves it unchanged and cancels no verdict. A feature plan may name generated paths, such as lockfiles, and generated lines, such as a `version:` line, whose changes also move no code head. Its sessions then add `':(exclude,glob)**/<name>'` to both `git diff` pathspecs for each such path, and `-I '<regex>'` before each `--` for each such line. Without `glob`, `**/<name>` misses a file at the repository root. A generated-line regex must match only generated lines, because `-I` applies to every file. A correct run prints one 40-character SHA and nothing on standard error, so any error output means the result cannot be trusted.
- **Verdicts.** The list keeps every verdict, newest last. The merge rule is that the newest `verify` verdict is `VERIFIED` or `WAIVED`, the newest `review` verdict is `CLEAR` or `WAIVED`, and both name the current code head. A `WAIVED` verdict counts only when the newest earlier verdict of the same gate that is not `WAIVED` is `VERIFIED` or `CLEAR`. A phase moves to PR once the rule holds, and `handbooks/orchestrator.md` owns the further checks the orchestrator makes before it merges.
- **Waivers.** A fresh gate agent, the verifier or the first reviewer, may return `WAIVED` instead of running its gate, with its reason. It may do so only when its brief says it may, which the phase session says only when the gate's newest verdict that is not `WAIVED` is `VERIFIED` or `CLEAR`, so that every waiver counts under the merge rule, and only when the diff in its scope changes nothing that a user, a program or an agent reading the file would act on differently. Waivable: generated files only; formatting, import order or a linter's auto-fix; a complete rename of a local variable or private function; comments, docstrings, log wording, or a typo in a user-facing string that no test asserts; a small, isolated change whose whole effect the agent can state from the diff, that no check or probe exercises and that nothing acts on differently, such as tightening a type annotation, deleting code the diff shows unreachable, or raising a log level. Never waivable: any change to logic or control flow, however small, such as a condition, a default, an error path or a retry; a change to a public interface or contract; a dependency added or bumped by hand; anything touching authentication, permissions, secrets, input handling or the commands the code runs; a test or check change that alters an expected result; a change to instructions an agent follows, such as a prompt, skill or handbook. An empty scope is waivable. A waiver never moves a gate's baseline: the next scoped Verify covers everything since the last `VERIFIED` code head, and the next Review everything since the last `CLEAR` or `SIGNIFICANT` one.
- **Ids.** A request or decision id is `<phase>-r<n>` or `<phase>-d<n>`, numbered by the phase itself. A decision that records an AFK answer takes the answer's `AFK-<n>` id instead. The planner numbers its requests `planner-r<n>`, and `handbooks/planner.md` says where it keeps them. No list is shared between writers.
- **Evidence.** Evidence that is not a URL lives in a file the phase owns under `.foundry/plans/<id>/status/`, named `<phase>-evidence.md`.
- **Pushed heads.** `pushed` holds the `RECORD` line of the PR creator's last proof that printed `EQUAL` and whose pushes all succeeded, without the word `RECORD`, exactly as printed. It is `null` before the first push. The phase passes it unchanged as the PR creator's `PUSHED`. `pull_requests` keeps every pull request once opened, merged ones included, because the PR creator's `OWN` lists them all.
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
| `blocked` | The session is blocked | What it waits for, which a phase first commits as `waits_for` |
| `prs-open` | A phase's pull requests are open | Each number with its `depends_on` list, the code head the pull requests hold, and the `pushed` line from the status file |
| `instruction` | The developer gave it an instruction that changes the phase's scope or a recorded decision | The instruction |
| `done-planning` | The planner has finished | The branch and commit to merge, and the phases whose plan entry changed |
| `roadmap-update` | A spec writer has an approved update | The branch and commit to merge, what changed, the behaviour that the change affects, and the `run-decisions.md` rows it folded in |

The orchestrator sends these. [handbooks/phase-session.md](../handbooks/phase-session.md) says what the phase does. The planner takes an `instruction` to revise the plan, as [handbooks/planner.md](../handbooks/planner.md#when-the-orchestrator-starts-you-again) says.

| Kind | When | The message carries |
| --- | --- | --- |
| `answer` | The developer has decided, or in AFK mode the orchestrator answered a two-way request | The answer and the id of the request that it answers, and for an AFK answer its `AFK-<n>` id |
| `instruction` | The developer gave an instruction | The instruction, in the developer's words |
| `instruction` | A pull request's head differs from the head in the phase's last `prs-open` | The pull request, the recorded head and its current head |
| `instruction` | A pull request lacks the current head of a pull request it depends on | The pull request and the dependency's head |
| `instruction` | A phase in PR has sent no `prs-open` at its current code head, or the orchestrator restarted | A request to send `prs-open` once a pull request holds that code head |
| `instruction` | A Done phase's status-only merge was refused for its own status files | The files, and a request to fix them in a `.foundry/`-only commit and stay Done |
| `merge-orchestrator-branch` | The orchestrator branch changed under a live phase | A request to merge it |
| `fix-round` | The developer reviewed a pull request, or one of its checks failed | The pull request and its comments, or the failed check |
| `fix-round` | A pull request merged: a pull request lacks the default branch's tip, because a dependency merged or the default branch moved | The pull request and the default branch tip |
| `fix-round` | A hand-written file the phase owns conflicts with the default branch | The conflicting paths and the default branch commit |
| `move-back` | A roadmap or plan change touches a phase, or a check on the orchestrator branch failed after the phase merged | The state to move back to, and what changed or the failed check |
| `instruction` | Every pull request of the phase merged into the default branch | The merged pull request numbers |
| `stop` | A phase's pane is about to close, or a stalled session is being replaced | A request to commit and stop |
| `park` | In AFK mode, a phase must stop starting work: a round cap, a session cap, a usage threshold, a start time not yet reached, or an open one-way door with nothing else to do | The reason, and the time to wait until or "the developer's return" |
| `unpark` | The reason for a `park` has passed | Nothing more |

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

The session commits the request to its status file, then sends a `decision-request` message. It removes the request from `requests` once the answer arrives. In AFK mode the orchestrator answers a two-way request itself, as [afk-mode.md](afk-mode.md) says, and a one-way request waits for the developer.
