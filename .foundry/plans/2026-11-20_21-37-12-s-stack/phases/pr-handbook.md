# Phase `pr-handbook` plan

This is the phase plan for `pr-handbook`, written by the phase session `s-stack-phase-pr-handbook` on 21 November 2026 against `s-stack-package` at `42c54ee`. The feature plan's entry for `pr-handbook` (`../README.md`, "Phase `pr-handbook`") sets the scope, the owned paths and the **Done when** list. This file adds the implementation detail. Where the two disagree, the feature plan wins and the session tells the orchestrator.

## The problem

The PR creator is the subagent that turns a verified and reviewed phase into draft pull requests. It is the last safeguard of roadmap decision D3. The developer reviews pull requests, not the phase branch, so the pull requests must hold exactly what the agents verified. `SKILL.md` already routes the PR creator to `handbooks/pr-creator.md`, and that file does not exist yet. Without it, every phase session improvises the split, the base, the `gh stack` commands, the generated-file handling and the equality proof. That is what happened in the November run and in this run's `foundation` phase, whose PR creator was briefed by hand.

## The intended outcome

After this phase, `packages/s-stack/.apm/skills/sam-mode/handbooks/pr-creator.md` exists, is at most 200 lines, and lets a fresh PR creator subagent do these things without other instructions:

- Refuse to start unless the status file's newest `verify` verdict is `VERIFIED` and newest `review` verdict is `CLEAR`, both for the current code head.
- Split the phase diff into pull requests along the phase plan, within the repository's scope and size rules.
- Work out each pull request's open dependencies and choose its base and form from the three-row rule in roadmap `workflow.md`, "Pull requests".
- Build each branch by carrying its own commits without generated hunks or `.foundry/`, and end it with one regenerate commit.
- Open every pull request as a draft, stack it with `gh stack link` when it has exactly one open dependency with nothing else stacked on it, and write the description by following p-stack's `summarise-pr` itself.
- Run the three checks before it reports: the equality proof, the repository's checks on each branch in stack order, and the missing-dependency rule.
- Update an open pull request as its one writer. That covers fix rounds, a moved default branch (including a squash-merged parent), regenerate-only rounds, and restacks on request, all without a force-push.
- Report a fixed set of facts to the phase session, after every subagent it started has finished.

## Non-goals and boundaries

- No change outside the two owned paths and the generated `packages/s-stack/apm.lock.yaml`. In particular, no edit to `SKILL.md`, the reference file, `tests/s-stack/verify-s-stack/SKILL.md` or anything under `packages/p-stack/`.
- No script file. The equality proof and the carry loop are commands in the handbook (roadmap `package.md`, maintenance rule 6).
- No `versioning.py bump` on the phase branch (feature plan C7).
- The handbook does not restate the status header or message kinds. It points to `references/status-and-messages.md`.
- The handbook does not state this run's code-head exemption for generated files as a general rule (feature plan C7, last paragraph). It takes the generated paths, the regenerate command and the regenerate subject from the feature plan.
- The handbook names no private repository, feature or page.
- `tests/s-stack/verify-s-stack/checks/pr-handbook.md` is written by the verifier in the Verify gate, not by the implementer.

## Design

### Where the facts come from

| Fact | Source the handbook distils |
| --- | --- |
| Inputs, when the PR creator runs, what it does | Roadmap `roles.md`, "PR creator" |
| Size, split, dependencies, base rule, the three checks, drafts, descriptions, one writer, restacks, fix rounds | Roadmap `workflow.md`, "Pull requests" |
| Carry loop, regenerate commit, merging the default branch, squash-merged parent, regenerate-only rounds | Feature plan C7, "On a pull request branch" and "Merging a branch that can change packages" |
| The equality proof | Feature plan Experiment 7, extended below |
| Running `summarise-pr` itself, waiting for its own subagents | Feature plan Experiment 2 |
| The `gh stack` commands | `gh stack --help` for `github/gh-stack` v0.3.0, read this session, and `foundation`'s PR evidence |

### Decisions taken in this plan

Each is a two-way door. The status file records them as `pr-handbook-d1` to `pr-handbook-d4`.

1. **`summarise-pr` is read, not invoked.** Its frontmatter sets `disable-model-invocation: true` (read in `packages/pr/.apm/skills/summarise-pr/SKILL.md`), so the Skill tool cannot load it. The handbook tells the PR creator to read `../summarise-pr/SKILL.md` relative to the `sam-mode` skill's directory and follow it, in the same way `SKILL.md` reads `poteto-mode`. Both are deployed as sibling skill directories.
2. **Only `gh pr create --draft`, `gh pr edit --base` and `gh stack link` with pull request numbers.** `gh stack sync`, `rebase` and `push` push with `--force-with-lease` after a rebase (their `--help`), which breaks the never-force-push rule. `gh stack submit` opens new pull requests as ready for review in its interactive editor, and the automatic permission check refused `gh stack submit --auto` in `foundation`. `gh stack link` with branch names pushes those branches. Given pull request numbers it only links. So the handbook pushes with a plain `git push -u origin <branch>`, opens each draft with `gh pr create --draft`, and links with `gh stack link <parent number> <child number>`, or `gh stack link <stack number> <child number>` when the parent is already in a stack. That exact sequence produced stack 83 for `foundation`.
3. **The equality proof prints one verdict.** Experiment 7's form relies on the reader noticing that a "must print nothing" line printed something. The handbook's form collects every failure, prints `FAIL <reason>` lines, then prints `EQUAL` and exits 0, or `NOT EQUAL` and exits 1. The verifier and the status evidence can then quote one line.
4. **Every multi-line command runs under `bash`.** The agent shell in this environment is zsh, which does not split an unquoted `$(...)` into words. A `for c in $(git rev-list ...)` loop then runs once over the whole list. This was observed while prototyping the proof, when a zsh harness passed `pr1: pr2:other-pr` as one argument. The handbook wraps each loop in `bash -s -- <args> <<'EOF'`.

### The generated-file parameters

The handbook defines four values once, from the feature plan. The example values are Foundry's, and the handbook says so.

```bash
REGEN='^chore(s-stack): regenerate generated files$'  # the regenerate commit's subject, as a git --grep pattern
GEN=(':(exclude)*apm.lock.yaml')                        # files that are wholly generated
LINES=(':(exclude)*apm.yml') LINES_IN='*apm.yml'         # files in which some lines are generated
LINE_OK='^[-+]version: '                                # the generated lines, as diff lines
```

A repository with no generated files sets `GEN=()` and `LINES=()`, and leaves `REGEN` set to a subject that no commit uses.

### The equality proof

This is the form the handbook carries. It was run on 21 November 2026 in a scratch repository with a package holding `apm.lock.yaml` and `apm.yml` with a `version:` line. That repository had an orchestrator branch carrying `.foundry/` and one merged phase, a phase branch with lockfile hunks inside its content commits and interleaved status commits, `pr1` cut from `main`, and `pr2` stacked on another phase's open pull request branch `other-pr`, each ending with a regenerate commit. The prototype is in the session scratchpad at `proto/prove.sh`, `proto/build.sh` and `proto/cases.sh`. The parameter block above is inlined into the proof below.

```bash
bash -s -- <orchestrator branch> <phase branch> <default branch> <pr branch>:<dep branch>,<dep branch> ... <<'EOF'
<the parameter block>
orch=$1 phase=$2 default=$3; shift 3; fail=0
only_lines() { git diff -U0 "$1" "$2" -- "$LINES_IN" | grep -E '^[-+]' | grep -v -E '^(\+\+\+|---) ' | grep -v -E "$LINE_OK"; }
idx=$(mktemp); GIT_INDEX_FILE=$idx git read-tree "$(git merge-base "$orch" "$phase")"
for spec in "$@"; do
  pr=${spec%%:*} deps=${spec#*:}; excl=("^$default")
  for d in ${deps//,/ }; do excl+=("^$d"); done
  for c in $(git rev-list --reverse --no-merges "$pr" "${excl[@]}" --invert-grep --grep="$REGEN"); do
    p=$(git diff-tree -p --binary "$c^" "$c" -- . "${GEN[@]}")
    [ -z "$p" ] || printf '%s\n' "$p" | GIT_INDEX_FILE=$idx git apply --cached || { echo "FAIL $pr: $c does not apply"; fail=1; }
  done
  for c in $(git rev-list --no-merges "$pr" "${excl[@]}" --grep="$REGEN"); do
    for f in $(git diff-tree --no-commit-id --name-only -r "$c" -- . "${GEN[@]}" "${LINES[@]}"); do echo "FAIL $pr: regenerate commit $c changes $f"; fail=1; done
    l=$(only_lines "$c^" "$c"); [ -z "$l" ] || { echo "FAIL $pr: regenerate commit $c changes $l"; fail=1; }
  done
  for f in $(git diff --name-only "$default...$pr" -- .foundry); do echo "FAIL $pr: contains $f"; fail=1; done
done
r=$(GIT_INDEX_FILE=$idx git write-tree); rm -f "$idx"
git diff --stat --exit-code "$r" "$phase" -- . ':(exclude).foundry' "${GEN[@]}" "${LINES[@]}" || { echo "FAIL the pull requests differ from the phase"; fail=1; }
l=$(only_lines "$r" "$phase"); [ -z "$l" ] || { echo "FAIL generated-line files differ outside generated lines: $l"; fail=1; }
[ "$fail" = 0 ] && echo EQUAL || { echo "NOT EQUAL"; exit 1; }
EOF
```

`<dep branch>` names a dependency's branch ref, local or `origin/...`. That covers a dependency in another phase, a dependency in the same phase, and a dependency that was squash-merged into the default branch with its branch ref kept. A pull request with no dependency is written `<pr branch>:`. Every pull request of the phase is listed.

| Case, prototype | Result |
| --- | --- |
| Correct split, `pr1:` and `pr2:other-pr` | `EQUAL`, exit 0 |
| `pr1` left out | `a.txt` listed, `NOT EQUAL`, exit 1 |
| An extra commit on `pr1` | `extra.txt` listed, exit 1 |
| `pr1` adds `.foundry/leak.md` | `FAIL pr1: contains .foundry/leak.md`, exit 1 |
| A regenerate commit that also changes `b.txt` | That commit and `b.txt` named, exit 1 |
| A regenerate commit that changes `deps:` in `apm.yml` | That commit and both lines named, exit 1 |
| `other-pr` squash-merged into `main`, `pr2` merged `main` and added a new regenerate commit, `other-pr`'s ref kept | `EQUAL`, exit 0 |

### The carry loop

From C7 step 1, generalised with the parameters. It runs on the pull request branch, once for each pull request, with the commits that the phase plan assigns to it.

```bash
bash -s -- <commits, oldest first> <<'EOF'
<the parameter block>
for c in $(git rev-list --no-merges --no-walk=unsorted "$@" -- . ':(exclude).foundry'); do
  d=$(git diff-tree -p --binary "$c^" "$c" -- . "${GEN[@]}" ':(exclude).foundry')
  [ -n "$d" ] || continue
  printf '%s\n' "$d" | git apply --index && git commit -q -C "$c" || exit 1
done
EOF
```

A repository hook that refuses a commit with stale generated files must be skipped for carried commits only, as the feature plan says. In Foundry that is `FOUNDRY_SKIP_LOCKFILE_HOOK=1`. The hook stays on for the regenerate commit and every merge commit.

### Handbook outline

The handbook is in British English and passes the repository's markdownlint configuration. It names other packages' skills in words, uses code spans and not links for paths, and states each rule once. Section order and the budget for each section are below. The total must stay at or under 200 lines.

| Section | Holds | About |
| --- | --- | --- |
| Title and opening | Who the PR creator is, when it runs, that it moves commits and never changes what the code does, and that it reads `poteto-mode`'s Opening a PR playbook only for what this handbook does not cover | 6 lines |
| Before you start | Inputs (roadmap, feature plan, phase plan, status file). The precondition on the two newest verdicts, with stop-and-report when it fails. Resolve the default branch and `git fetch origin`. Read the parameters from the feature plan. Hard rules: push only pull request branches; every pull request a draft; never mark ready, never merge, never force-push unless the developer says so; the `gh` commands of decision 2 only; wait for every subagent you start before you report | 18 lines |
| Split the phase | The phase diff, `git diff <orchestrator branch>...<phase branch> -- . ':(exclude).foundry'`. Start from the phase plan's split and change it when the diff demands. One atomic change per pull request within the repository's own size rules, which coding-style's software engineering rules give in section 11 for Foundry. The hand-written line count, `git diff --shortstat <base>...HEAD -- . "${GEN[@]}"` | 12 lines |
| Dependencies and base | Work out exactly which open pull requests each one needs, including other phases' open pull requests. The three-row base table from roadmap `workflow.md`, each row with how its branch is cut: from the default branch; from the parent's branch; from the default branch, then each dependency's branch merged in with the merge procedure | 16 lines |
| The parameters | The four-variable block and the no-generated-files form | 10 lines |
| Build each branch | The carry loop, the hook note, then the regenerate commit: the feature plan's regenerate command against `origin/<default>`, then the regenerate subject, committed with hooks on, touching only generated files and lines | 24 lines |
| Open the drafts | `git push -u origin <branch>`. `gh pr create --draft --base <base> --head <branch> --title <title> --body-file <file>`. For a stacked pull request, `gh stack link <parent> <child>` or `gh stack link <stack number> <child>`. Then `gh pr view <n> --json isDraft,baseRefName` | 12 lines |
| Descriptions | Read `../summarise-pr/SKILL.md` relative to the `sam-mode` skill's directory and follow it with the pull request's own diff, commits and the phase plan as context. Add "Depends on #n" lines. For the third base row, list each dependency and say the diff includes their changes until they merge. Add measured detail the phase produced, the hand-written line count, and the repository's attribution lines | 10 lines |
| The three checks | The equality proof. Each branch passes the repository's checks on its own, bottom of the stack first, as the repository's agent guide names them (for Foundry, the pre-commit hook with `FOUNDRY_DIFF_RANGE=origin/<default>...HEAD`, `scripts/versioning.py check origin/<default>` and Tier 1). A branch that fails because it needs undeclared code gets the dependency added, never a code change | 40 lines |
| Update an open pull request | One writer: fetch `gh pr view <n> --json headRefOid,body` first, merge in any remote commit you did not make, keep every description change you did not make, follow the repository's own stacking skill where one exists. A fix round: carry the fix commits to the owning branch, add a new regenerate commit, repeat the three checks. A moved default branch: the merge procedure (C7's, compact: `--no-ff --no-commit`, the squash-merged-parent `--ours` loop, `--theirs` for generated files after the `apm.yml`-differs-only-in-version check, abort on any other conflict, regenerate, commit with hooks on), then a new regenerate commit when it changes anything. A regenerate-only round does those two steps and the proof only. A restack only on request: `gh pr edit <n> --base <new base>`, then `gh stack link` when it joins a stack, or the merge procedure when it moves to the default branch | 34 lines |
| Report | For each pull request, its number, URL, branch, base, `depends_on`, `stacked` and hand-written line count. The proof's full output. Each check's result per branch. Any split change and why. The phase session writes these into its status file, because the PR creator writes no file under `.foundry/` | 10 lines |

## Blast radius

| Path | Change |
| --- | --- |
| `packages/s-stack/.apm/skills/sam-mode/handbooks/pr-creator.md` | New |
| `packages/s-stack/apm.lock.yaml` | Generated, gains the deployed paths and hashes of the new file for three targets |
| `tests/s-stack/verify-s-stack/checks/pr-handbook.md` | New, written by the verifier |

Check 4 of `verify-s-stack` stops reporting `handbooks/pr-creator.md` as pending. Nothing else reads the handbook until a phase session points a PR creator at it. No consumer installs s-stack before the `default-stack` phase.

## Execution order

Commits follow the one planned pull request. A commit never mixes `.foundry/` with other files.

1. Create the pinned CLI in this worktree: `uv venv .venv-apm && uv pip install --python .venv-apm/bin/python apm-cli==0.32.0`, then check that `.venv-apm/bin/apm --version` starts with `0.32.0`.
2. Write the handbook to the outline above.
3. Run the handbook's proof and carry loop, copied from the handbook file and not from this plan, against a scratch repository like the prototype. Every row of the case table must give its result.
4. Regenerate the lockfile: `cd packages/s-stack && perl -e 'alarm shift; exec @ARGV' 300 ../../.venv-apm/bin/apm install --target cursor,claude,copilot`, then `python3 scripts/relativise_lockfiles.py packages/s-stack/apm.lock.yaml` from the root.
5. Commit the handbook and the lockfile together with the hook on and `APM=$PWD/.venv-apm/bin/apm`. The subject is `feat(s-stack): add the PR creator handbook`.
6. Run `quick-review` on the whole diff `git diff s-stack-package...HEAD -- . ':(exclude).foundry'`, fix the findings, and commit the fixes the same way.
7. Commit the status file at Verify and tell the orchestrator, after merging `s-stack-package` into the phase branch with the C7 procedure.
8. **Verify.** A fresh verifier, briefed with roadmap `roles.md`, "Verifier", or `handbooks/verifier.md` if it is on the orchestrator branch by then, writes `checks/pr-handbook.md`, commits it, and runs `verify-s-stack` and the **Done when** list. The verifier copies the proof from the handbook into its check file's scratch-repository build, so the check fails when the handbook's commands break.
9. **Review.** Fresh reviewers run p-stack's `interrogate` on the phase diff, with the brief in roadmap `roles.md`, "Reviewer", and no access to `.foundry/`.
10. **PR.** A fresh PR creator reads the new handbook and opens one draft. With pull requests 81 and 82 both open, it has two dependencies, so it targets `main`, its branch contains both pull requests' commits, and its description lists both (feature plan, "Pull request rules for this run").

## Verification

- `wc -l` on the handbook is 200 or fewer.
- The **Done when** cases of the feature plan, run by the verifier from commands copied out of the handbook.
- `verify-s-stack` in full, including Tier 1 outside the sandbox.
- The PR creator of this phase follows the new handbook to open its own pull request. That is a first live use, recorded as evidence and not as a gate.
