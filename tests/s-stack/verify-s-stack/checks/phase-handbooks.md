# Phase `phase-handbooks` checks

Phase `phase-handbooks` ships the three handbooks of one phase's gate chain. They are prose that agents act on, so the behavioural checks are cold reads. A cold read starts a fresh subagent, gives it only the files the check names and the sample text the check quotes, tells it to read nothing else, and asks the questions. Its answer passes when it agrees in substance with every point of the expected answer. Wording may differ, but a missing or contradicting point fails the check. Wait for every cold-read subagent to finish before reporting.

The three files, relative to the repository root:

- `packages/s-stack/.apm/skills/sam-mode/handbooks/phase-session.md`
- `packages/s-stack/.apm/skills/sam-mode/handbooks/verifier.md`
- `packages/s-stack/.apm/skills/sam-mode/handbooks/reviewer.md`

The line budget of 200 per handbook is the verification skill's check 3, so it is not repeated here.

## Rerun

### Cold read 1. An old verdict at Verify

Files: `phase-session.md` only, plus this sample status file, pasted into the prompt.

```yaml
---
phase: "widgets"
state: "Verify"
changed_at: "2026-11-21T16:00:00Z"
session: "demo-phase-widgets"
branch: "demo-phase-widgets"
code_head: "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
waits_for: null
verdicts:
  - gate: "verify"
    result: "VERIFIED"
    code_head: "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    at: "2026-11-21T12:00:00Z"
    evidence: ".foundry/plans/<id>/status/widgets-evidence.md"
pull_requests: []
requests: []
decisions: []
---
```

Prompt: "Read only the handbook file at the path below and nothing else, not even files it links to. Answer from it and the sample status file below alone. You are the phase session for phase `widgets`. Since the verdict below was recorded you merged the orchestrator branch into the phase branch, and the code head command now prints `bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb`. The only change your merge brought into your own paths is a one-line typo fix. (1) Does the `VERIFIED` verdict in the status file cover the current code head? (2) May the phase move on to Review on the strength of it? (3) What must happen for verification, and how much of it runs?"

Expected answer:

1. No. The verdict names code head `aaaa…`, and a verdict covers only the code head it names. The current code head is `bbbb…`, which the merge moved.
2. No. The phase moves to Review only on a `VERIFIED` verdict for the current code head. The size of the change does not matter, and an old verdict is never carried forward.
3. A fresh verifier subagent runs, and verification runs again in full for the new code head. Its verdict is recorded in the status file before the phase can move on.

### Cold read 2. The verifier's check file and a check that could not run

Files: `verifier.md` only, plus this placeholder diff, pasted into the prompt.

```diff
diff --git a/packages/demo/.apm/skills/widgets/SKILL.md b/packages/demo/.apm/skills/widgets/SKILL.md
new file mode 100644
--- /dev/null
+++ b/packages/demo/.apm/skills/widgets/SKILL.md
@@ -0,0 +1,6 @@
+---
+name: widgets
+description: "Builds a widget report and publishes it as a page."
+---
+
+Run `scripts/report.sh`, then publish its output as a page.
```

Prompt: "Read only the handbook file at the path below and nothing else, not even files it links to. Answer from it and the placeholder diff below alone. You are the verifier for phase `widgets` of feature `demo`. The phase session's brief says the verification skill is `tests/demo/verify-demo/SKILL.md`, and the feature plan does not give your phase that skill's files. One check you need publishes a test page, and the publishing tool is not available in your environment. Every other check ran and passed. (1) Which file do you write, as a path from the repository root, and which sections does it have? (2) When do you commit it, relative to running the checks? (3) What verdict do you return, and is it a pass? (4) May you return while a subagent you started is still running?"

Expected answer:

1. `tests/demo/verify-demo/checks/widgets.md`, beside the verification skill's `SKILL.md`, with a `## Rerun` section for cheap, repeatable, local checks and an `## Evidence` section that describes one-off checks without their results. It does not edit the skill's `SKILL.md`, which its phase does not own.
2. Before running anything. The commit moves the code head, and the verdict must come from a run at that head. Any later change outside `.foundry/`, this file included, means a new commit and a full rerun.
3. INCONCLUSIVE, because no check failed but one could not run. INCONCLUSIVE is not a pass.
4. No. It waits until every subagent it started has reported.

### Cold read 3. What a reviewer reads, and two findings

Files: `reviewer.md` only, plus this placeholder diff, pasted into the prompt.

```diff
diff --git a/tools/demo_cli.py b/tools/demo_cli.py
--- a/tools/demo_cli.py
+++ b/tools/demo_cli.py
@@ -10,3 +10,7 @@ def main(argv):
     command, *rest = argv
+    if command == "parse":
+        return parse_row(rest[0])
+
+def parse_row(text):
+    return [int(cell) for cell in text.split(",")]
```

Prompt: "Read only the handbook file at the path below and nothing else, not even files it links to. Answer from it and the placeholder diff below alone. You are one reviewer in a phase's Review gate, and your worktree of the phase branch contains a `.foundry/` directory holding the roadmap and the plans. (1) Will you read anything under `.foundry/`, the roadmap or a plan to understand the change? (2) Classify each finding as significant or not, and say why. Finding A: running `python3 tools/demo_cli.py parse 'a,b'`, which the change's own help text says accepts any comma-separated row, exits with a `ValueError` traceback. Finding B: `parse_row` would read better as `parse_line`."

Expected answer:

1. No. It does not read `.foundry/`, the roadmap, a plan, a status file or the implementer's notes, and does not ask for them. The code must explain itself, and a change it cannot follow without them is itself a finding.
2. Finding A is significant: a run shows a crash on input the change is meant to accept. Finding B is not significant: it is a naming preference between two working designs.

### Cold read 4. A restart and a direct instruction

Files: `phase-session.md` only.

Prompt: "Read only the handbook file at the path below and nothing else, not even files it links to. Answer from it alone. You are a phase session. (1) Your pane was killed and the launcher has just started you again. What do you read again before you continue, and how do you decide what to do next? (2) The developer types into your pane: 'Also add a CSV export command to this phase.' That changes the phase's scope. What do you do with the instruction, and whom do you tell?"

Expected answer:

1. It reads again the phase plan, the status file and the phase branch, including uncommitted work (`git status`) and the current code head. It continues from the state recorded in the status file. A gate with no verdict in the status file runs again, and a verdict for a different code head no longer covers the phase.
2. It follows the instruction. Because it changes the phase's scope, it records it in the status file's `decisions`, commits, and sends the orchestrator an `instruction` message that carries it. If the change conflicts with the feature plan, it also sends a decision request, because only the planner changes the plan.

## Evidence

### Private names

A case-insensitive search for the private repository's name, its feature's name and the prototype page ids, over every file in `git diff --name-only s-stack-package...s-stack-phase-phase-handbooks -- . ':(exclude).foundry'`, over that diff's text and over the messages of the commits in `s-stack-package..s-stack-phase-phase-handbooks`. The patterns live outside this repository and are never written here. It passes when nothing matches. The verifier reports the result.
