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

1. It runs `scripts/launch.sh --feature billing-export --role spec`, the script in the `sam-mode` skill's own directory, with the repository root as the working directory, reports the script's output, and does nothing else. It does not read `poteto-mode` first, interview the developer, write a roadmap or read a handbook itself.
2. The default branch (resolved, never assumed to be `main`), the orchestrator branch `<feature>`, the planner branch `<feature>-planner`, update spec writer branches `<feature>-spec-<n>`, phase branches `<feature>-phase-<phase>`, and pull request branches. Only pull request branches, which never contain `.foundry/`, are pushed. The orchestrator branch and every branch cut from it carry `.foundry/` and are not pushed to a public remote unless the developer says so.
3. The developer decides it. The session sends a decision request to the orchestrator and continues with the work the decision does not affect.

### Cold read 3. Code head, messages and merging

Files: `references/status-and-messages.md` only.

Prompt: "Read only this file and nothing else. Answer from it alone. (1) How does a phase session compute its code head, and which commits leave it unchanged? (2) Phase `launcher` of feature `billing-export` has just moved to Verify. Write the message its session sends to the orchestrator, and say what it does before sending it. (3) When may the orchestrator merge a phase? (4) What is the commit subject of that phase's status commit? (5) Which message does the orchestrator send when (a) every pull request of a phase in PR has merged into the default branch, (b) a pull request of the phase lacks the default branch's tip, because the default branch moved, and (c) a check on the orchestrator branch fails after the phase merged?"

Expected answer:

1. Walk the phase branch's first-parent line, newest first, diff each commit against its own first parent, and take the newest that changes something outside `.foundry/`, leaving out the generated paths and lines the feature plan names. A clean merge of the orchestrator branch leaves it unchanged. A merge is clean when its tree equals git's automatic merge of its two parents outside `.foundry/`. Any other merge that brings in code moves it, including a merge of the default branch and a conflict resolution. A merge that brings only `.foundry/` changes leaves it unchanged. A commit that only records status, or changes only those generated paths and lines, leaves it unchanged.
2. It first commits its status file (state `Verify`, the code head) on its own branch. Then it sends a message whose first line is `billing-export-phase-launcher: state: <one sentence>`, carrying the new state `Verify` and the code head, with any detail lines below being facts already committed.
3. The newest `verify` verdict is `VERIFIED` or `WAIVED`, and the newest `review` verdict is `CLEAR` or `WAIVED`. Both name the current code head. A `WAIVED` verdict counts only when the newest earlier verdict of the same gate that is not `WAIVED` is `VERIFIED` or `CLEAR`. That is the merge rule, and the phase moves to PR once it holds. `handbooks/orchestrator.md` owns the further checks the orchestrator makes before it merges.
4. `chore(billing-export): launcher Verify`.
5. (a) An `instruction` carrying the merged pull request numbers. (b) `fix-round`, naming the pull request and the default branch tip. (c) `move-back`, naming the state to move back to and the failed check.

### Status header matches C2

The reference ships the feature plan's C2 with these changes, each set by a run decision in `run-decisions.md` or by an item the orchestrator queued in its tracker. Request `foundation-r1`, option A, turns this run's example values into placeholders: `<id>`, `<feature>` and `<phase>`, plus `<pull request branch>` and `<default branch>` for this run's pull request branch and `main`. Request `foundation-r2`, option A, adds one sentence to the quoting rule that keeps characters outside the Basic Multilingual Plane out of header strings. The code-head rule follows `foundation-r1`, which keeps it general with only `.foundry/` excluded, and the run decision that the code head is the newest first-parent commit whose diff against its first parent changes a line outside the excluded paths and lines. It gives that rule as a bash loop over `git rev-list --first-parent`, run under bash from the worktree root, and says how a feature plan's generated paths and lines are excluded. The check compares that code-head rule, whole, with the approved wording. Queued item 1, raised by `spec-planner-handbooks`, adds the planner's `planner-r<n>` exception to the **Ids** rule. The run decision on `prs-open` re-merges and the follow-up round's review make the **Verdicts** rule state the merge rule, which a phase checks before it moves to PR, and point to `handbooks/orchestrator.md` for the orchestrator's further checks before it merges. The integration fix round replaces the code-head rule with one that skips clean merges of the orchestrator branch, adds `WAIVED` to both verdict lists and to the merge rule, adds the `pushed` key, and adds the **Waivers** and **Pushed heads** rules. Any other difference, such as a new or reworded rule, is a contract change and fails. The check runs from the repository root wherever it is started, and always compares the code-head rule, which needs only the reference. The rest of the comparison reads the feature plan under `.foundry/`, which exists only on the orchestrator branch and the phase branches. Without the plan, as on a pull request branch or the default branch, it prints `PENDING: .foundry/plans/2026-11-20_21-37-12-s-stack/README.md not found, so the reference cannot be compared with C2 here` and skips that part. It exits `1` whenever the code-head rule differs, and otherwise `0`, with the PENDING line when only the plan is missing.

```bash
python3 - <<'EOF'
import difflib, os, pathlib, re, subprocess, sys
os.chdir(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True).stdout.strip())
plan_path = pathlib.Path(".foundry/plans/2026-11-20_21-37-12-s-stack/README.md")
ref = pathlib.Path("packages/s-stack/.apm/skills/sam-mode/references/status-and-messages.md").read_text()

def header_section(text):
    start = text.index("The header is")
    end = text.index("\n", text.index("keeps its own form", start))
    return [re.sub(r"\s+", " ", l).strip() for l in text[start:end].splitlines() if l.strip()]

code_head = [re.sub(r"\s+", " ", l).strip() for l in """- **Code head.** It is the newest commit on the phase branch's first-parent line whose diff against its own first parent changes a file outside `.foundry/`, with one exception. A clean merge of the orchestrator branch moves no code head, because code merged in from it counts as verified and reviewed. A merge of the orchestrator branch is one whose second parent is on the orchestrator branch's first-parent line. It is clean when its tree equals git's automatic merge of its two parents outside `.foundry/`. Any other merge that brings in code moves the code head, a merge of the default branch and a conflict resolution included. Run this under bash from the worktree root:

  \x60\x60\x60bash
  ob=$(git rev-list --first-parent <orchestrator branch>)
  for c in $(git rev-list --first-parent <phase branch>); do
    if p2=$(git rev-parse -q --verify "$c^2") && grep -qx "$p2" <<<"$ob"; then
      t=$(git merge-tree --write-tree "$c^1" "$p2" | head -n 1)
      git diff --quiet "$t" "$c" -- . ':(exclude).foundry' && continue
    fi
    git diff --quiet "$c^" "$c" -- . ':(exclude).foundry' || { echo "$c"; break; }
  done
  \x60\x60\x60

  A commit that only records status leaves it unchanged and cancels no verdict. A feature plan may name generated paths, such as lockfiles, and generated lines, such as a `version:` line, whose changes also move no code head. Its sessions then add `':(exclude,glob)**/<name>'` to both `git diff` pathspecs for each such path, and `-I '<regex>'` before each `--` for each such line. Without `glob`, `**/<name>` misses a file at the repository root. A generated-line regex must match only generated lines, because `-I` applies to every file. A correct run prints one 40-character SHA and nothing on standard error, so any error output means the result cannot be trusted.""".splitlines() if l.strip()]

def without_code_head(lines):
    hits = [k for k, l in enumerate(lines) if l.startswith("- **Code head.**")]
    if len(hits) != 1:
        sys.exit("FAIL: expected exactly one Code head rule")
    end = next((k for k in range(hits[0] + 1, len(lines)) if lines[k].startswith("- **")), len(lines))
    return lines[hits[0]:end], lines[:hits[0]] + lines[end:]

rule, shipped_rest = without_code_head(header_section(ref))
problems = [] if rule == code_head else ["code-head rule differs from the approved wording:"] + list(difflib.unified_diff(code_head, rule, "approved", "reference", lineterm="", n=0))
if plan_path.is_file():
    plan = plan_path.read_text()
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
        ("cannot break the YAML.", "cannot break the YAML. Keep characters outside the Basic Multilingual Plane, such as emoji, out of header strings, because `json.dumps` writes them as surrogate pairs that a YAML reader does not join."),
        ('The orchestrator merges only when the newest `verify` verdict is `VERIFIED` and the newest `review` verdict is `CLEAR`, and both name the current code head.', 'The merge rule is that the newest `verify` verdict is `VERIFIED` or `WAIVED`, the newest `review` verdict is `CLEAR` or `WAIVED`, and both name the current code head. A `WAIVED` verdict counts only when the newest earlier verdict of the same gate that is not `WAIVED` is `VERIFIED` or `CLEAR`. A phase moves to PR once the rule holds, and `handbooks/orchestrator.md` owns the further checks the orchestrator makes before it merges.'),
        ('# verify: VERIFIED | NOT VERIFIED | INCONCLUSIVE', '# verify: VERIFIED | NOT VERIFIED | INCONCLUSIVE | WAIVED'),
        ('# review: CLEAR | SIGNIFICANT', '# review: CLEAR | SIGNIFICANT | WAIVED'),
        ("numbered by the phase itself.", "numbered by the phase itself. The planner numbers its requests `planner-r<n>`, and `handbooks/planner.md` says where it keeps them."),
    ]
    insertions = [
        ("stacked: true", 'pushed: "<branch>=<sha>,<branch>=<sha>" # the PR creator\'s last RECORD line, else null'),
        ("- **Verdicts.**", "- **Waivers.** A fresh gate agent, the verifier or the first reviewer, may return `WAIVED` instead of running its gate, with its reason. It may do so only when the diff in its scope changes nothing that a user, a program or an agent reading the file would act on differently. Waivable: generated files only; formatting, import order or a linter's auto-fix; a complete rename of a local variable or private function; comments, docstrings, log wording, or a typo in a user-facing string that no test asserts; a small, isolated change whose whole effect the agent can state from the diff and that no check or probe exercises. Never waivable: any change to logic or control flow; a change to a public interface or contract; a dependency added or bumped by hand; anything touching authentication, permissions, secrets, input handling or the commands the code runs; a test or check change that alters an expected result; a change to instructions an agent follows, such as a prompt, skill or handbook. An empty scope is waivable. A waiver never moves a gate's baseline: the next scoped Verify covers everything since the last `VERIFIED` code head, and the next Review everything since the last `CLEAR` or `SIGNIFICANT` one."),
        ("- **Evidence.**", "- **Pushed heads.** `pushed` holds the `RECORD` line of the PR creator's last proof that printed `EQUAL` and whose pushes all succeeded, without the word `RECORD`, exactly as printed. It is `null` before the first push. The phase passes it unchanged as the PR creator's `PUSHED`. `pull_requests` keeps every pull request once opened, merged ones included, because the PR creator's `OWN` lists them all."),
    ]
    expected = []
    for line in header_section(plan.split("### C2.", 1)[1].split("### C3.", 1)[0]):
        for old, new in placeholders:
            line = line.replace(old, new)
        expected.append(line)
        for anchor, added in insertions:
            if line.startswith(anchor):
                expected.append(added)
    _, expected_rest = without_code_head(expected)
    problems += difflib.unified_diff(expected_rest, shipped_rest, "C2 with placeholders", "reference", lineterm="", n=0)
else:
    print(f"PENDING: {plan_path} not found, so the reference cannot be compared with C2 here")
if problems:
    print("\n".join(problems))
    sys.exit(1)
if plan_path.is_file():
    print("reference matches C2 apart from the allowed differences")
EOF
```

Expected: exit `0` and `reference matches C2 apart from the allowed differences`. On the reference at `13f835b` it exits `1`, and among the differences it prints the append-only sentences of the **Evidence** rule.

## Evidence

### Private names

A case-insensitive `grep` over every file in `git diff --name-only s-stack-package...HEAD -- . ':(exclude).foundry'`, and over the phase's commit messages, for the private repository's name, its feature's name and both prototype page ids. The verifier takes the names from the developer's private notes and never writes them into a file. Passes when nothing matches.
