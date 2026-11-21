# Phase `foundation` checks

Phase `foundation` ships the `sam-mode` router `SKILL.md` and `references/status-and-messages.md`. Both are prose, so the behavioural checks are cold reads. A cold read starts a fresh subagent, gives it only the files the check names, tells it to read nothing else, and asks the questions. Its answer passes when it agrees in substance with every point of the expected answer. Wording may differ, but a missing or contradicting point fails the check. Wait for every cold-read subagent to finish before reporting.

The two files, relative to the repository root:

- `packages/s-stack/.apm/skills/sam-mode/SKILL.md`
- `packages/s-stack/.apm/skills/sam-mode/references/status-and-messages.md`

## Rerun

### Cold read 1. Roles, handbooks and the phase session's first prompt

Files: both files above.

Prompt: "Read only these two files and nothing else, not even files they link to. Answer from them alone. (1) For each of these roles say which handbook path you would read, relative to the repository root: spec writer, orchestrator, planner, phase session, verifier, reviewer, PR creator. (2) Write the exact first prompt that a phase session of feature `<feature>` and phase `<phase>` receives, with placeholders for values you cannot know."

Expected answer:

1. Each handbook is under `packages/s-stack/.apm/skills/sam-mode/handbooks/`. Spec writer `spec-writer.md`, orchestrator `orchestrator.md`, planner `planner.md`, phase session `phase-session.md`, verifier `verifier.md`, reviewer `reviewer.md`, PR creator `pr-creator.md`. The verifier, reviewer and PR creator have no first-prompt role and are pointed at their handbook by the phase session.
2. `/sam-mode phase feature=<feature> phase=<phase> update=- roadmap=<path> plan=<path> orchestrator=<feature>-orchestrator`, where `update` is `-` because only a spec writer for a roadmap update has one.

### Cold read 2. Starting a feature, branches and doors

Files: `SKILL.md` only.

Prompt: "Read only this file and nothing else. Answer from it alone. (1) The developer types `/sam-mode start billing-export` into a Claude Code session at the root of a repository. What exactly does that session do, and what does it not do? (2) Which branches does s-stack name, and which of them may a session push to a public remote without the developer saying so? (3) A phase session meets a one-way door. What does it do?"

Expected answer:

1. It runs `scripts/launch.sh --feature billing-export --role spec`, the script in the `sam-mode` skill's own directory, with the repository root as the working directory, reports the script's output, and does nothing else. It does not interview the developer, write a roadmap or read a handbook itself.
2. The default branch (resolved, never assumed to be `main`), the orchestrator branch `<feature>`, phase branches `<feature>-phase-<phase>`, and pull request branches. Only pull request branches, which never contain `.foundry/`, are pushed. The orchestrator branch and phase branches carry `.foundry/` and are not pushed to a public remote unless the developer says so.
3. The developer decides it. The session sends a decision request to the orchestrator and continues with the work the decision does not affect.

### Cold read 3. Code head, messages and merging

Files: `references/status-and-messages.md` only.

Prompt: "Read only this file and nothing else. Answer from it alone. (1) How does a phase session compute its code head, and which commits leave it unchanged? (2) Phase `launcher` of feature `billing-export` has just moved to Verify. Write the message its session sends to the orchestrator, and say what it does before sending it. (3) When may the orchestrator merge a phase? (4) What is the commit subject of that phase's status commit?"

Expected answer:

1. `git log -1 --format=%H <phase branch> -- . ':(exclude).foundry'`, run from the worktree root: the latest commit on the phase branch that changes a file outside `.foundry/`. A commit that only records status leaves it unchanged. When the feature plan names generated paths such as lockfiles, the session adds an exclude clause for each, and commits touching only those also leave it unchanged.
2. It first commits its status file (state `Verify`, the code head) on its own branch. Then it sends a message whose first line is `billing-export-phase-launcher: state: <one sentence>`, carrying the new state `Verify` and the code head, with any detail lines below being facts already committed.
3. Only when the newest `verify` verdict is `VERIFIED` and the newest `review` verdict is `CLEAR`, and both name the current code head.
4. `chore(billing-export): launcher Verify`.

### Status header matches C2

The reference ships the feature plan's C2 with two kinds of change, both decided by the orchestrator (request `foundation-r1`, option A). This run's example values become placeholders: `<id>`, `<feature>` and `<phase>`, plus `<pull request branch>` and `<default branch>` for this run's pull request branch and `main`. The code-head rule states the general command with only `.foundry/` excluded, a sentence to run it from the worktree root, and a sentence that a feature plan may name generated paths to exclude too. The check compares that code-head rule, whole, with the wording the orchestrator approved. Any other difference, such as a new or reworded rule, is a contract change and fails. The check reads the feature plan under `.foundry/`, which exists only on the orchestrator branch and the phase branches. On a pull request branch or the default branch it prints `PENDING: .foundry/ is absent, so the feature plan's C2 cannot be read here` and exits `0`.

```bash
python3 - <<'EOF'
import difflib, pathlib, re, sys
plan_path = pathlib.Path(".foundry/plans/2026-11-20_21-37-12-s-stack/README.md")
if not plan_path.is_file():
    print("PENDING: .foundry/ is absent, so the feature plan's C2 cannot be read here")
    sys.exit(0)
plan = plan_path.read_text()
ref = pathlib.Path("packages/s-stack/.apm/skills/sam-mode/references/status-and-messages.md").read_text()

def header_section(text):
    start = text.index("The header is")
    end = text.index("\n", text.index("keeps its own form", start))
    return [re.sub(r"\s+", " ", l).strip() for l in text[start:end].splitlines() if l.strip()]

placeholders = [
    ('"s-stack-phase-launcher"', '"<feature>-phase-<phase>"'),
    ('phase: "launcher"', 'phase: "<phase>"'),
    ("2026-11-20_21-37-12-s-stack", "<id>"),
    ("launcher-evidence", "<phase>-evidence"),
    ('"launcher-r1"', '"<phase>-r1"'),
    ('"launcher-d1"', '"<phase>-d1"'),
    ('branch: "s-stack-launcher"', 'branch: "<pull request branch>"'),
    ('base: "main"', 'base: "<default branch>"'),
    ("chore(s-stack)", "chore(<feature>)"),
    ("tracker at `status/orchestrator.md`", "tracker at `.foundry/plans/<id>/status/orchestrator.md`"),
]
expected = []
for line in header_section(plan.split("### C2.", 1)[1].split("### C3.", 1)[0]):
    for old, new in placeholders:
        line = line.replace(old, new)
    expected.append(line)
shipped = header_section(ref)

code_head = "- **Code head.** It is `git log -1 --format=%H <phase branch> -- . ':(exclude).foundry'`, the latest commit on the phase branch that changes a file outside `.foundry/`. Run it from the worktree root. A commit that only records status leaves it unchanged and cancels no verdict. A feature plan may name generated paths, such as lockfiles, whose commits also move no code head. Its sessions then add an exclude clause for each such path to the command."

def without_code_head(lines):
    hits = [k for k, l in enumerate(lines) if l.startswith("- **Code head.**")]
    if len(hits) != 1:
        sys.exit("FAIL: expected exactly one Code head rule")
    return lines[hits[0]], lines[:hits[0]] + lines[hits[0] + 1:]

rule, shipped_rest = without_code_head(shipped)
_, expected_rest = without_code_head(expected)
problems = [] if rule == code_head else [f"code-head rule differs from the approved wording:\n-{code_head}\n+{rule}"]
problems += difflib.unified_diff(expected_rest, shipped_rest, "C2 with placeholders", "reference", lineterm="", n=0)
print("\n".join(problems) or "reference matches C2 apart from the allowed differences")
sys.exit(1 if problems else 0)
EOF
```

Expected: exit `0` and `reference matches C2 apart from the allowed differences`. On the reference at `13f835b` it exits `1` and prints the append-only sentences of the **Evidence** rule.

## Evidence

### C2 conformance of the reference at `512edd797f497f955ca5a0175faead7c18a8c2d8`

Compared the reference's header section with feature plan C2 by `diff` of the text from "The header is" to the tracker sentence. Differences: the `<id>`, `<feature>` and `<phase>` placeholders and the general code-head rule, both as the orchestrator decided (`foundation-r1`, option A), plus two additions that C2 does not contain: "Run it from the worktree root." in the code-head rule, and three sentences in the **Evidence** rule making the evidence file append-only with one section per verdict. Option A says every other part of C2 is copied unchanged, so the append-only rule is a contract change made without a decision request. Result: FAIL, reported to the phase session.

### Private names at `512edd797f497f955ca5a0175faead7c18a8c2d8`

A case-insensitive `grep` over every file in `git diff --name-only s-stack-package...HEAD -- . ':(exclude).foundry'` and over the phase's commit messages, for the private repository's name, its feature's name and both prototype page ids (taken from the developer's private notes and not reproduced here), found no hit.
