---
name: verify-s-stack
description: "Verifies the s-stack package in Foundry: structural validation, markdown lint, line budgets, handbook routes, package isolation, launcher tests, the Tier 1 suite and each phase's check file. Run by s-stack phase verifiers and by the orchestrator's merge check."
---

# Verify s-stack

This skill proves the `s-stack` package on the checked-out branch. It lives under `tests/` because Foundry ignores `.claude/` and `.agents/`, so it is not a deployed primitive and agents read it by path.

Run every command from the repository root, in the order below. Run check 7 outside the agent sandbox. APM creates `.cursor/` directories in its staging areas whatever the targets, and the sandbox denies writes beneath `.cursor` and to `$HOME/.apm/`, so Tier 1 fails there for reasons unrelated to the package.

## Before you start

When `.venv-apm` is missing, create it first, which also installs the PyYAML that `validate_primitives.py` needs:

```bash
uv venv .venv-apm && uv pip install --python .venv-apm/bin/python apm-cli==0.32.0
```

```bash
git rev-parse --show-toplevel && git rev-parse HEAD && git branch --show-current
.venv-apm/bin/apm --version
git status --short --ignored > "${TMPDIR:-/tmp}/verify-s-stack-$(basename "$PWD").txt"
```

The first line must be the working directory. Record the HEAD SHA in the report. The `apm` line must print version `0.32.0`. The last command snapshots the worktree for cleanup, so it runs after the venv exists.

## Checks

Report each check with its command, its output and one of PASS, FAIL or PENDING. Unless a check says otherwise, PASS means every command in it exits `0`.

### 1. Primitives and root manifest

```bash
PATH="$PWD/.venv-apm/bin:$PATH" python3 tests/structural/validate_primitives.py
python3 tests/structural/check_root_manifest.py
```

### 2. Markdown lint

```bash
npx --yes markdownlint-cli2@0.14.0 "packages/s-stack/**/*.md" "tests/s-stack/**/*.md"
```

### 3. Line budgets

`SKILL.md` has at most 150 lines and each handbook at most 200. No handbooks yet is a PASS.

```bash
bash <<'EOF'
d=packages/s-stack/.apm/skills/sam-mode
status=0
for f in "$d/SKILL.md" "$d"/handbooks/*.md; do
  [ -e "$f" ] || continue
  limit=200
  [ "$f" = "$d/SKILL.md" ] && limit=150
  n=$(wc -l < "$f" | tr -d ' ')
  echo "$n/$limit $f"
  [ "$n" -le "$limit" ] || status=1
done
exit $status
EOF
```

### 4. Handbook routes

Every `handbooks/<role>.md` code span in `SKILL.md` names a handbook. PASS when every one exists, PENDING when any is missing, FAIL when the command prints nothing. A missing route never fails here. The strict form, in which a missing route fails, belongs to the `default-stack` phase.

```bash
bash <<'EOF'
d=packages/s-stack/.apm/skills/sam-mode
grep -o '`handbooks/[a-z0-9-]*\.md`' "$d/SKILL.md" | tr -d '`' | sort -u | while read -r route; do
  if [ -f "$d/$route" ]; then echo "present $route"; else echo "PENDING $route"; fi
done
EOF
```

### 5. Package isolation

No relative Markdown link inside `sam-mode` resolves outside `packages/s-stack/`, and no file under `packages/p-stack` differs from the default branch. Never assume the default branch is `main`. PASS when the first command exits `0` and the `git diff` prints nothing.

```bash
python3 - <<'EOF'
import pathlib, re, sys
package = pathlib.Path("packages/s-stack").resolve()
leaks = []
for md in sorted(pathlib.Path("packages/s-stack/.apm/skills/sam-mode").rglob("*.md")):
    text = re.sub(r"```.*?```", "", md.read_text(), flags=re.S)
    text = re.sub(r"`[^`\n]*`", "", text)
    targets = re.findall(r"\]\(([^)\s]+)", text) + re.findall(r"^\[[^\]]+\]:\s*(\S+)", text, flags=re.M)
    for target in targets:
        if re.match(r"[a-z][a-z0-9+.-]*:|#", target):
            continue
        if not (md.parent / target.split("#")[0]).resolve().is_relative_to(package):
            leaks.append(f"{md}: {target}")
print("\n".join(leaks) or "no relative link leaves packages/s-stack")
sys.exit(1 if leaks else 0)
EOF
```

```bash
base="$(gh repo view --json defaultBranchRef --jq .defaultBranchRef.name 2>/dev/null)"
[ -n "$base" ] || base="$(git symbolic-ref --short refs/remotes/origin/HEAD | sed 's#^origin/##')"
echo "default branch: $base"
git diff --name-only "$(git merge-base "origin/$base" HEAD)" -- packages/p-stack
```

### 6. Launcher tests

PENDING while `packages/s-stack/tests` is missing.

```bash
bash <<'EOF'
if [ -d packages/s-stack/tests ]; then
  python3 -m unittest discover -s packages/s-stack/tests
else
  echo "PENDING: packages/s-stack/tests is missing"
fi
EOF
```

### 7. Tier 1

Run outside the sandbox. The suite takes about three minutes and bounds each `apm` call itself, so give the command at least ten minutes. PASS needs exit `0` and a final line of the form `all Tier 1 structural checks passed across <n> packages`.

```bash
PATH="$PWD/.venv-apm/bin:$PATH" APM="$PWD/.venv-apm/bin/apm" bash tests/structural/run-tier1.sh
```

### 8. Phase check files

Each phase's verifier records that phase's behavioural checks in `tests/s-stack/verify-s-stack/checks/<phase>.md`, and only phase `<phase>` writes that file. It has two sections.

- `## Rerun` holds cheap, repeatable checks that touch nothing outside the machine, such as cold reads, scratch repositories and unit tests. Each states its command or scenario and its expected result.
- `## Evidence` records one-off checks with their results, such as a published test page or a real `claude` session. Never rerun it.

List the files in name order, then run every check in each file's `## Rerun` section exactly as written and compare its result with the expected one. Report each check by file and name. With no files, report "no check files" and PASS.

```bash
bash <<'EOF'
shopt -s nullglob
files=(tests/s-stack/verify-s-stack/checks/*.md)
if [ ${#files[@]} -eq 0 ]; then echo "no check files"; else printf '%s\n' "${files[@]}" | LC_ALL=C sort; fi
EOF
```

## Report

List the HEAD SHA, then each check with its command, output and result. End with the verdict: VERIFIED when no check is FAIL, NOT VERIFIED otherwise. PENDING never fails the verdict. Name every PENDING item beneath the verdict. Give the report in your reply or in a file outside the repository, never inside it.

## Cleanup

Tier 1 removes its scratch directory on exit but leaves gitignored deploy output, such as `.agents/`, `.claude/` and `dist/`, in each package. Remove every ignored path that is new since the snapshot, unless it holds a tracked file, then confirm the worktree matches the snapshot. Kill only processes you started.

```bash
bash <<'EOF'
before="${TMPDIR:-/tmp}/verify-s-stack-$(basename "$PWD").txt"
new=$(git status --short --ignored | diff "$before" - | sed -n 's/^> !! //p')
if [ -n "$new" ] && [ -z "$(git ls-files -- $new)" ]; then rm -rf -- $new; fi
git status --short --ignored | diff "$before" - && echo "worktree matches the snapshot"
EOF
```
