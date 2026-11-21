# Phase `foundation` plan

This is the phase plan for `foundation`, written by the phase session `s-stack-phase-foundation` on 21 November 2026 against `s-stack-package` at `12d98d9`. The feature plan's entry for `foundation` (`../README.md`, "Phase `foundation`") sets the scope, the owned paths and the **Done when** list. This file adds the implementation detail. Where the two disagree, the feature plan wins and the session tells the orchestrator.

## The problem

Every other phase of s-stack writes into `packages/s-stack/.apm/skills/sam-mode/`, reads the status header and message kinds from a shipped reference file, and adds its checks to one verification skill. None of that exists yet. Until `foundation` lands on `s-stack-package`, the six middle phases cannot start.

## The intended outcome

After this phase, on the phase branch:

- `packages/s-stack` is a valid Foundry package. It installs for `cursor`, `claude` and `copilot`, passes `apm audit --ci`, and is pack-blocked like every package with sibling `path:` dependencies.
- A session whose first prompt is `/sam-mode <role> ...` loads `SKILL.md`, reads `poteto-mode`'s `SKILL.md`, learns the rules every session follows, and finds its handbook path. A session given `/sam-mode start <feature>` runs `scripts/launch.sh --feature <feature> --role spec` and nothing else.
- `references/status-and-messages.md` defines the status file header and the messages. From this phase on it owns them.
- The root manifest reaches s-stack, and every count and pack-blocked list in the docs says twenty packages and six pack-blocked packages.
- `tests/s-stack/verify-s-stack/SKILL.md` runs the eight checks of feature plan C6 and reports each handbook route as pending.

## Non-goals and boundaries

- No launcher, board template or handbook. Those belong to later phases. `SKILL.md` names their paths in code spans so the validator passes while they are missing.
- No change under `packages/default-stack/` or `packages/p-stack/`, and no change to any other package's manifest or lockfile.
- No `versioning.py bump` on the phase branch (feature plan C7). s-stack's version stays `"0.1.0"`. The PR creator's regenerate commit raises versions on pull request branches.
- No script file in the verification skill. The phase owns only `tests/s-stack/verify-s-stack/SKILL.md` and `checks/foundation.md`, so every check is a command written in `SKILL.md`.
- `run-tier1.sh` line 40's "nine" stays, because it counts `default-stack`'s packages.
- No ignore entry for `.foundry`.

## Design

### Package files

```text
packages/s-stack/
├── apm.yml                 # copy of packages/pr/apm.yml with the C1 dependencies
├── README.md               # in the form of packages/pr/README.md
├── .gitignore              # byte-identical to packages/pr/.gitignore (33 bytes)
├── apm.lock.yaml           # generated
└── .apm/skills/sam-mode/
    ├── SKILL.md
    └── references/status-and-messages.md
```

`apm.yml`:

```yaml
name: s-stack
version: "0.1.0"
description: "Run one large feature as cooperating Claude Code sessions, each in its own worktree and tmux pane."
author: sam
license: MIT
repository: https://github.com/Samuel-Harris/foundry
targets:
  - cursor
  - claude
  - copilot
includes: auto
dependencies:
  apm:
    - path: ../p-stack
    - path: ../deep-interview
    - path: ../review
    - path: ../pr
    - path: ../planning
    - path: ../coding-style
scripts:
  check: apm audit --ci
```

`README.md` follows `packages/pr/README.md`: title, the manifest description, a "What it installs" table with one `sam-mode` row, an "Install" block with `apm install Samuel-Harris/foundry/packages/s-stack#^0.1.0 --target cursor,claude,copilot` (the newer packages use the range form), a "Requirements" section that names Claude Code 2.1.224 or later with cross-session messaging, tmux and workmux, and the "Targets" section. It says that the package declares all three targets like every Foundry package, and that only Claude Code can run the workflow.

### `SKILL.md`

Frontmatter: `name: sam-mode`, and a quoted `description` of at most 1024 characters with no colon. It says the skill runs one large feature as cooperating Claude Code sessions (spec writer, orchestrator, planner, one session per phase), is used through `/sam-mode start <feature>` or `/sam-mode <role>`, needs Claude Code with cross-session messaging, tmux and workmux, and is not for small patches, which one `poteto-mode` session handles. No `disable-model-invocation`; the plan does not ask for it.

Body, in this order, at most 150 lines:

1. **What s-stack is**, in two or three sentences, and that it adds to `poteto-mode` and replaces none of it.
2. **When to use it and when not.** A large feature with several phases that can run in parallel. Not a small patch or minor bug fix.
3. **First, read `poteto-mode`.** Read `../poteto-mode/SKILL.md` from this skill's directory (a code span, not a link), because `poteto-mode` sets `disable-model-invocation: true` and cannot be invoked as a skill. Follow it for how to work. The handbook adds only what is specific to s-stack.
4. **The invocation.** Two forms. `/sam-mode start <feature>`: run `scripts/launch.sh --feature <feature> --role spec` from the repository root and report its output, nothing else. `/sam-mode <role> feature=<feature> phase=<phase> update=<n> roadmap=<path> plan=<path> orchestrator=<name>`: the C4 first prompt, where `-` means empty. Take the role, read its handbook, then the roadmap and plan it names.
5. **Role-to-handbook table**, exactly the C1 table, paths in code spans. Subagent roles have no launcher role; the phase session points each subagent at its handbook.
6. **Rules for every main session**, from roadmap `roles.md` "Rules for every main session", in s-stack's own words.
7. **Shared rules** every role needs and no single handbook owns. The artefact table (path, writer), the seven states with the forward-one-at-a-time rule and the code-head rule for verdicts, the branch table, one writer per file under `.foundry/`, a commit never mixes `.foundry/` with other files, a pull request branch never contains `.foundry/`, every pull request is a draft and s-stack never marks one ready or merges one, never assume the default branch is `main`, one-way doors go to the orchestrator. Each rule is one or two lines.
8. **Where to read next.** `references/status-and-messages.md` for the status header and messages. The handbooks for everything role-specific.

`SKILL.md` names other packages' skills in words ("p-stack's `interrogate` skill"), never a relative link into another package.

### `references/status-and-messages.md`

1. **Status files.** The facts a status file holds (roadmap `coordination.md`, "Status files"), then C2's header example and its five rules. The path, the example evidence path and the commit subject use the placeholders `<id>` and `<feature>` instead of this run's names, because the file ships to every repository. See request `foundation-r1` for the code-head rule.
2. **Messages.** The C3 line form, then the two message tables from roadmap `coordination.md`, each with a `Kind` column holding the C3 kind for that row (`started`, `state`, `decision-request`, `blocked`, `prs-open`, `instruction`, `done-planning`, `roadmap-update`; and `answer`, `instruction`, `merge-orchestrator-branch`, `fix-round`, `restack`, `move-back`, `stop`), then the four rules. The rule that a sender commits the fact before it sends the message goes first.
3. **Decision requests.** The fields of a request (question, options, recommendation, door, waiting work), which match the header's `requests` entries.

### Root wiring and docs

| File | Change |
| --- | --- |
| Root `apm.yml` | Add `- path: ./packages/s-stack` between `./packages/skill-creation` and `./packages/ui`. The list sorts ignoring hyphens, as `skill-creation` after `search` shows. Remove `./packages/coding-style`, `./packages/planning` and `./packages/p-stack`. |
| `tests/structural/run-tier1.sh` | `PACK_BLOCKED=" default-stack execution planning repo-init s-stack skill-creation "`. Line 4 "nineteen" to "twenty". |
| `AGENTS.md` | Line 3 "nineteen" to "twenty", line 4 "eighteen" to "nineteen". Lines 131 to 133, "The five packages" to "The six packages", with `s-stack` in the list in name order. Line 380 "Nineteen byte-identical" to "Twenty byte-identical". |
| Root `README.md` | `s-stack` row in the package table after `skill-creation`, contents `skills: \`sam-mode\``, purpose matching the manifest description. `sam-mode` row in the skills table after `design-skill`, with the `description` truncated to 160 characters as the table's note requires. |
| `docs/COMPATIBILITY.md` | `s-stack` row after `skill-creation`, `1 skill`, `verified`, `untested`, `untested`. Line 77 "nineteen" to "twenty". Line 98 "five packages" to "six packages", and `s-stack` joins the list after `repo-init`. The "fourteen packages with an empty `dependencies:` mapping" stays fourteen. |
| `docs/DEPENDENCY-CONTRACTS.md` | Line 221 list gains `s-stack`. Line 74's list of dependency-bearing packages gains `s-stack`. The cross-package reference table gains six rows declared in "`s-stack`, the `sam-mode` skill and its handbooks": `poteto-mode` and `interrogate` (p-stack), `deep-interview`, `quick-review` (review), `summarise-pr` (pr), `plan-handoff-standard` (planning), and the pull request scope and size rules in `software-engineering-rules` (coding-style), each with its edge. The acyclic graph block gains the six `s-stack --> <dep>` lines. The default-stack tree is unchanged. |
| `tests/acceptance.md` | Lines 21, 23 and 51 "nineteen" to "twenty". Line 39 "The five packages" to "The six packages", `s-stack` in the list. |

Line 74 of `docs/DEPENDENCY-CONTRACTS.md` already says "nine" while listing eight names, some of which have no dependencies. That is pre-existing. Adding `s-stack` makes nine names. The phase does not correct the other names; it is reported to the orchestrator as a note.

### Verification skill

`tests/s-stack/verify-s-stack/SKILL.md`, written by following p-stack's `create-verification-skill` with its output directed to this path. Frontmatter `name: verify-s-stack` and a description. It runs the C6 checks in order and reports each with its output and PASS, FAIL or PENDING:

1. `python3 tests/structural/validate_primitives.py` and `python3 tests/structural/check_root_manifest.py`, with `.venv-apm/bin` on `PATH`.
2. `npx --yes markdownlint-cli2@0.14.0` on `packages/s-stack/**/*.md` and `tests/s-stack/**/*.md`.
3. `wc -l` budgets. `SKILL.md` at most 150 lines, each `handbooks/*.md` at most 200.
4. Routes. Extract every `handbooks/<role>.md` code span from `SKILL.md`. Each missing file is PENDING, not FAIL.
5. No relative Markdown link from `packages/s-stack/.apm/skills/sam-mode/` that leaves the package, and `git diff --name-only <default branch>... -- packages/p-stack` prints nothing.
6. `python3 -m unittest discover -s packages/s-stack/tests`, PENDING while the directory is missing.
7. Tier 1, as feature plan rule 7, outside the sandbox.
8. The `## Rerun` section of each `checks/*.md`, in name order.

The skill resolves the default branch with `gh repo view --json defaultBranchRef --jq .defaultBranchRef.name`, falling back to `origin/HEAD`.

## Blast radius

Exactly the owned paths in the feature plan entry, plus the generated `packages/s-stack/apm.lock.yaml`. The root `apm.lock.yaml` is gitignored and changes locally only. No consumer installs s-stack until the `default-stack` phase. After pulling, a Foundry developer reinstalls at the root (`AGENTS.md`, "Root development manifest").

## Execution order

Commits follow the pull request split, so the PR creator moves whole commits.

**Pull request 1. The package and its wiring.**

1. Create the package files, the root `apm.yml` change, and the lockfile in one commit. The pre-commit hook runs `check_root_manifest.py`, which fails if the package exists without the root change or the reverse, so they go together. Generate the lockfile with `cd packages/s-stack && perl -e 'alarm shift; exec @ARGV' 300 ../../.venv-apm/bin/apm install --target cursor,claude,copilot`, then `python3 scripts/relativise_lockfiles.py packages/s-stack/apm.lock.yaml`. Subject `feat(s-stack): add the s-stack package with the sam-mode router`.
2. Fix the counts, the pack-blocked lists and the new rows in one commit. Subject `docs: count s-stack among Foundry's packages`.
3. Run `quick-review` on commits 1 and 2 against `s-stack-package`, fix findings, commit the fixes.

**Pull request 2. The verification skill.**

4. Write `tests/s-stack/verify-s-stack/SKILL.md`. Subject `test(s-stack): add the verify-s-stack verification skill`.
5. Run it once end to end on the head and record the output in `../status/foundation-evidence.md`.
6. Run `quick-review` on commit 4 alone, fix findings, commit.

**Gates.**

7. Merge `s-stack-package` into the phase branch (C7 procedure on a generated-only conflict).
8. Verify. A fresh verifier writes `checks/foundation.md`, commits it, and runs the skill and the **Done when** list, including the cold read of `SKILL.md` and the reference file.
9. Review. Fresh reviewers run p-stack's `interrogate` on `git diff s-stack-package...HEAD -- . ':(exclude).foundry'`, told not to read `.foundry/`.
10. PR. A fresh PR creator opens the two drafts, the second stacked on the first with `gh stack`, with a regenerate commit on each branch that changes a package, and runs the equality proof.

The status file is committed, and the orchestrator told, at every state change.

## Verification

The **Done when** list in the feature plan entry, with this evidence:

| Item | Evidence |
| --- | --- |
| Validator and root manifest | `primitives valid`; `12 listed, 19 reached`, exit 0 |
| Tier 1 | `all Tier 1 structural checks passed across 20 packages` |
| Audit | `apm audit --ci` in `packages/s-stack` passes on the committed lockfile with no reinstall first |
| Budget | `wc -l packages/s-stack/.apm/skills/sam-mode/SKILL.md` at most 150 |
| Verification skill | One end-to-end run on this head, handbooks PENDING |
| Counts | The `git grep` from the feature plan's counts step finds no stale count or list |
| Cold read | A fresh subagent given only `SKILL.md` and the reference names each role's handbook path and writes the first prompt of a phase session |

## Rejected alternatives

- **A script for the verification checks.** It would be easier to rerun, but the phase owns only `SKILL.md` and `checks/foundation.md` under `tests/s-stack/verify-s-stack/`, and the C6 contract names commands, not a script.
- **Placing the states and branches in the reference file.** The reference owns the header and messages (C1). The states and branches are rules every session follows, which C1 assigns to `SKILL.md`.
- **Copying C2 with this run's paths.** The reference ships to every repository that installs s-stack, so a path naming this run would be wrong everywhere else. See `foundation-r1`.

## Open decision

`foundation-r1` in the status file. C2 says to copy the header definition into the reference unchanged, but its code-head command excludes `**/apm.lock.yaml`, which is option B, a decision for this run only (C7 says no handbook states it as a general rule). Recommendation A: the shipped reference gives the general rule, `git log -1 --format=%H <phase branch> -- . ':(exclude).foundry'`, says that a feature plan may name generated paths that also move no code head, and uses `<id>` and `<feature>` placeholders. This run's sessions keep using C2 from the feature plan, which names the lockfile exclusion. Option B: copy C2 word for word. The work waiting on it is the code-head paragraph of the reference file only.
