---
name: verify-s-stack
description: "Verifies the s-stack package in Foundry: structural validation, markdown lint, line budgets, handbook routes, package isolation, launcher tests, the Tier 1 suite and each phase's check file. Run by s-stack phase verifiers and by the orchestrator's merge check."
---

# Verify s-stack

This skill proves the `s-stack` package on the checked-out branch. It lives under `tests/` because Foundry ignores `.claude/` and `.agents/`, so it is not a deployed primitive and agents read it by path.

Run every command from the repository root, in the order below. Run check 7 outside the agent sandbox; `AGENTS.md`, "Run it outside the agent sandbox", says why.

## Before you start

When `.venv-apm` is missing, create it first, which also installs the PyYAML that `validate_primitives.py` needs:

```bash
uv venv .venv-apm && uv pip install --python .venv-apm/bin/python apm-cli==0.32.0
```

```bash
git rev-parse --show-toplevel && git rev-parse HEAD && git branch --show-current
.venv-apm/bin/apm --version
```

`git rev-parse --show-toplevel` must print the current directory. Record the HEAD SHA in the report. The `apm` line must print version `0.32.0`.

## Checks

Report each check with its command, its output and one of PASS, FAIL or PENDING. Unless a check says otherwise, PASS means every command in it exits `0`.

### 1. Primitives and root manifest

A fast pre-flight. Tier 1 in check 7 runs the same two scripts again. The venv's `python3` goes first on `PATH` because it has the PyYAML that `validate_primitives.py` needs and the system `python3` lacks.

```bash
PATH="$PWD/.venv-apm/bin:$PATH" python3 tests/structural/validate_primitives.py
python3 tests/structural/check_root_manifest.py
```

### 2. Markdown lint

`.githooks/pre-commit` owns the linter pin, and `MARKDOWNLINT_CLI2_VERSION` overrides it.

```bash
npx --yes "markdownlint-cli2@${MARKDOWNLINT_CLI2_VERSION:-0.14.0}" "packages/s-stack/**/*.md" "tests/s-stack/**/*.md"
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

Every `handbooks/<role>.md` code span in `SKILL.md` names a handbook. Judge this check on its printed output, not its exit code: PASS when every line is `present`, PENDING when any line is `PENDING`, FAIL when it prints nothing. A missing route never fails here. The strict form, in which a missing route fails, belongs to the `default-stack` phase.

```bash
bash <<'EOF'
d=packages/s-stack/.apm/skills/sam-mode
grep -oE '`handbooks/[a-z0-9-]+\.md`' "$d/SKILL.md" | tr -d '`' | sort -u | while read -r route; do
  if [ -f "$d/$route" ]; then echo "present $route"; else echo "PENDING $route"; fi
done
EOF
```

### 5. Package isolation

No relative link inside `sam-mode` resolves outside `packages/s-stack/`, and no file under `packages/p-stack` changed on this branch. The first command parses each file as CommonMark with `markdown-it-py`, so code spans and fenced blocks never yield a link. It reads link and image targets, every reference definition, used or not, and `href` and `src` attributes in inline and block HTML. It declares and pins `markdown-it-py` in inline PEP 723 metadata and runs with `uv run`, as `scripts/pstack_upstream.py` does, so it needs neither `.venv-apm` nor the APM CLI's own dependencies. Never assume the default branch is `main`. PASS when both commands exit `0` and the diff prints nothing.

```bash
uv run --no-project - <<'EOF'
# /// script
# requires-python = ">=3.12"
# dependencies = ["markdown-it-py==4.0.0"]
# ///
import pathlib, re, sys, urllib.parse
from markdown_it import MarkdownIt
package = pathlib.Path("packages/s-stack").resolve()
html_attr = re.compile(r"""\b(?:href|src)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'=<>`]+))""", re.I)

def targets(tokens):
    for t in tokens:
        if t.type == "link_open":
            yield t.attrs["href"]
        elif t.type == "image":
            yield t.attrs["src"]
        elif t.type in ("html_inline", "html_block"):
            yield from ("".join(groups) for groups in html_attr.findall(t.content))
        yield from targets(t.children or [])

leaks = []
for md in sorted(pathlib.Path("packages/s-stack/.apm/skills/sam-mode").rglob("*.md")):
    env = {}
    tokens = MarkdownIt("commonmark").parse(md.read_text(), env)
    for target in dict.fromkeys([*targets(tokens), *(ref["href"] for ref in env.get("references", {}).values())]):
        if not target or target.startswith("#") or re.match(r"[a-z][a-z0-9+.-]*:", target, re.I):
            continue
        if not (md.parent / urllib.parse.unquote(target.split("#")[0])).resolve().is_relative_to(package):
            leaks.append(f"{md}: {target}")
print("\n".join(leaks) or "no relative link leaves packages/s-stack")
sys.exit(1 if leaks else 0)
EOF
```

```bash
bash <<'EOF'
set -euo pipefail
base="$(gh repo view --json defaultBranchRef --jq .defaultBranchRef.name 2>/dev/null || true)"
[ -n "$base" ] || base="$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's#^origin/##' || true)"
if [ -z "$base" ]; then echo "FAIL: cannot resolve the default branch" >&2; exit 1; fi
echo "default branch: $base"
git fetch -q origin "$base"
merge_base="$(git merge-base "origin/$base" HEAD)" || { echo "FAIL: no merge-base between origin/$base and HEAD" >&2; exit 1; }
git diff --name-only "$merge_base" -- packages/p-stack
EOF
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
- `## Evidence` describes one-off checks, such as a published test page or a real `claude` session, and never their results. `handbooks/verifier.md` defines the section. This skill does not run it.

List the files in name order, then run every check in each file's `## Rerun` section exactly as written and compare its result with the expected one. Report each check by file and name. A Rerun check may report PENDING when what it needs is absent on the checked-out branch, and that PENDING never fails the verdict. With no files, report "no check files" and PASS.

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

Tier 1 leaves gitignored deploy output in each package. Remove only that, with this command, which deletes ignored files under those paths and never a tracked file:

```bash
git clean -fdX -- 'packages/*/apm_modules' 'packages/*/.agents' 'packages/*/.claude' 'packages/*/.claude-plugin' 'packages/*/.cursor' 'packages/*/.github' 'packages/*/dist'
```

`git clean` leaves each package's `.cursor/` and `.github/` behind once empty, and an empty `.cursor/` makes `apm targets` report cursor as active. No package tracks a file there, so remove the empty directories:

```bash
bash <<'EOF'
for d in packages/*/.cursor packages/*/.github; do
  if [ -d "$d" ]; then find "$d" -depth -type d -empty -delete; fi
done
EOF
```

Then `find packages -mindepth 2 -maxdepth 2 -type d -empty` must print nothing the run left, and `git status --short` must show no change the run made. Kill only processes you started.
