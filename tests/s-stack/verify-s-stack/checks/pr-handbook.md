# Phase `pr-handbook` checks

Phase `pr-handbook` ships `packages/s-stack/.apm/skills/sam-mode/handbooks/pr-creator.md`, the PR creator's handbook. Its commands are the behaviour, so the checks run them. The scratch-repository check extracts the parameter block, the carry loop, the equality proof and the merge procedure from the handbook's fenced `bash` blocks at run time, substitutes the parameter block for each `<the parameter block>` line, and runs them as the handbook says, under `bash -s`. A change that breaks a handbook command therefore fails this check. Run each block from anywhere inside the repository, with `/bin/bash` as written, because the agent shell is zsh.

## Rerun

### Scratch repository

The check builds a throwaway repository under `$TMPDIR` with git's global and system configuration switched off, and deletes it on exit. The repository has a package `pkg/` holding `apm.yml`, with a `version:` line, and `apm.lock.yaml`. A stand-in regenerate command rewrites the lockfile from the tree and sets `version:` to the patch after `main`'s. The branches are these.

- `main`, the default branch.
- `other-pr`, another phase's open pull request, which edits line 2 of `shared.txt` and adds `o.txt`.
- `orch`, the orchestrator branch, which adds `.foundry/plan.md` and merges `other-pr`.
- `phase`, cut from `orch`. Its commits are `a.txt` plus a `description:` line in `apm.yml` plus a stale lockfile hunk; a `.foundry/` status commit; line 2 of `shared.txt` again plus `b.txt` plus a lockfile hunk; a binary `img.bin`; and a commit that changes only the lockfile and `.foundry/`.
- `pr1`, cut from `main` with no dependency, carries the first content commit. `pr2`, stacked on `other-pr`, carries the other three. Each ends with a regenerate commit whose subject is `chore(s-stack): regenerate generated files`.

Each case prints `PASS <case>` or `FAIL <case>: <output>`, and the block ends with `<n> failed` and exits `0` only when no case fails. Expected results:

| Case | Expected |
| --- | --- |
| The carry loop on `pr2`, given the lockfile-and-`.foundry`-only commit | exit `0`, the commit drops out, three commits on `pr2` |
| The binary `img.bin` | carried byte for byte |
| Correct split, `pr1:` and `pr2:other-pr` | `EQUAL`, exit `0` |
| `pr2` left out | `b.txt` listed, `FAIL the pull requests differ from the phase`, `NOT EQUAL`, exit `1` |
| An extra commit adding `extra.txt` | `extra.txt` listed, exit `1` |
| A commit adding `.foundry/leak.md` | `FAIL pr1f: contains .foundry/leak.md`, exit `1` |
| A regenerate commit that also changes `a.txt` | `FAIL pr1r: regenerate commit <sha> changes a.txt`, exit `1` |
| A regenerate commit that changes `deps:` in `apm.yml` | that commit named with `-deps: []` and `+deps: [x]`, exit `1` |
| An own commit, not a regenerate commit, that changes only the lockfile | the commit is skipped, `EQUAL`, exit `0` |
| `main` moves; a merge with the merge procedure that also carries a hand edit to `a.txt` | `FAIL pr1h: merge <sha> changes a.txt by hand`, exit `1` |
| The same clean automatic merge of `main` into `pr1`, regenerated and committed | `EQUAL`, exit `0` |
| `other-pr` squash-merged into `main`, then `main` changes line 11 of `shared.txt` and sets `version: "0.3.0"`; `pr1` merges `main`, so `apm.yml` conflicts only on `version:` while `pr1` has a hand edit elsewhere in it | merge completes, `description: pr1` kept, `version: "0.3.1"` after regenerating, `EQUAL`, exit `0` |
| `pr2` merges `main` passing `other-pr` as the squash-merged parent, then regenerates | `shared.txt` keeps `line 2 child` and `line 11 main` |
| The proof after that, with `other-pr` excluded through its kept branch ref | `EQUAL`, exit `0` |

```bash
/bin/bash <<'CHECK'
set -u
root=$(git rev-parse --show-toplevel)
hb="$root/packages/s-stack/.apm/skills/sam-mode/handbooks/pr-creator.md"
S=$(mktemp -d "${TMPDIR:-/tmp}/pr-handbook-check.XXXXXX")
trap 'rm -rf "$S"' EXIT
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
export GIT_AUTHOR_NAME=check GIT_AUTHOR_EMAIL=check@example.com GIT_COMMITTER_NAME=check GIT_COMMITTER_EMAIL=check@example.com
fails=0
pass() { echo "PASS $1"; }
fail() { echo "FAIL $1"; fails=$((fails + 1)); }

mkdir "$S/blocks"
awk -v dir="$S/blocks" '/^```bash$/ { n++; f = sprintf("%s/%02d.sh", dir, n); inb = 1; next } /^```$/ { inb = 0; next } inb { print > f }' "$hb"
pick() { grep -l -F -e "$1" "$S"/blocks/*.sh | head -1; }
params=$(grep -l -E '^REGEN=' "$S"/blocks/*.sh | head -1)
[ -n "$params" ] || { echo "FAIL no parameter block in $hb"; exit 1; }
body() {
  local f; f=$(pick "$1")
  [ -n "$f" ] && head -1 "$f" | grep -q "<<'EOF'\$" && [ "$(tail -1 "$f")" = EOF ] || { echo "handbook block with '$1' not found in the bash -s form" >&2; return 1; }
  sed '1d;$d' "$f" | awk -v p="$params" '$0 == "<the parameter block>" { while ((getline l < p) > 0) print l; close(p); next } { print }'
}
for x in carry:'git rev-list --no-merges --no-walk=unsorted' prove:'orch=$1 phase=$2 default=$3' merge:'git merge --no-ff --no-commit'; do
  body "${x#*:}" > "$S/${x%%:*}.sh" || { echo "FAIL cannot extract the ${x%%:*} block from $hb"; exit 1; }
done

R="$S/repo"; git init -q -b main "$R"; cd "$R" || exit 1
carry() { bash -s -- "$@" < "$S/carry.sh"; }
prove() { bash -s -- orch phase main "$@" < "$S/prove.sh"; }
merge() { bash -s -- "$@" < "$S/merge.sh"; }
regen() {
  local v; v=$(git show main:pkg/apm.yml | sed -n 's/^version: "\(.*\)"$/\1/p')
  sed "s/^version: .*/version: \"${v%.*}.$(( ${v##*.} + 1 ))\"/" pkg/apm.yml > "$S/y" && cat "$S/y" > pkg/apm.yml && git add pkg/apm.yml
  git ls-files -s -- . ':(exclude)*apm.lock.yaml' > pkg/apm.lock.yaml && git add pkg/apm.lock.yaml
}
regen_commit() { regen; git diff --cached --quiet || git commit -q -m 'chore(s-stack): regenerate generated files'; }
commit() { git add -A && git commit -q -m "$1"; }
line() { sed "$1s/.*/$2/" "$3" > "$S/l" && cat "$S/l" > "$3"; }
run() { out=$("$@" 2>&1); code=$?; }

mkdir pkg
printf 'name: pkg\nversion: "0.1.0"\na: 1\nb: 2\nc: 3\nd: 4\ne: 5\ndeps: []\n' > pkg/apm.yml
for i in 1 2 3 4 5 6 7 8 9 10 11 12; do echo "line $i"; done > shared.txt
echo readme > README
: > pkg/apm.lock.yaml; git add -A; git ls-files -s -- . ':(exclude)*apm.lock.yaml' > pkg/apm.lock.yaml; commit 'initial'

git checkout -q -b other-pr main
line 2 'line 2 parent' shared.txt; echo other > o.txt; commit 'feat: other phase'

git checkout -q -b orch main
mkdir .foundry; echo plan > .foundry/plan.md; commit 'chore: plan'
git merge -q --no-ff --no-edit other-pr

git checkout -q -b phase orch
echo a > a.txt; echo 'description: pr1' >> pkg/apm.yml; echo stale1 >> pkg/apm.lock.yaml; commit 'feat: a'; c1=$(git rev-parse HEAD)
echo s1 > .foundry/status.md; commit 'chore: status'
line 2 'line 2 child' shared.txt; echo b > b.txt; echo stale2 >> pkg/apm.lock.yaml; commit 'feat: b'; c2=$(git rev-parse HEAD)
printf 'bin\000\001\377' > img.bin; commit 'feat: binary'; c3=$(git rev-parse HEAD)
echo stale3 >> pkg/apm.lock.yaml; echo s2 > .foundry/status.md; commit 'chore: lockfile and status only'; c4=$(git rev-parse HEAD)
git checkout -q orch

git worktree add -q --no-track -b pr1 "$S/pr1" main
(cd "$S/pr1" && carry "$c1" && regen_commit)
git worktree add -q --no-track -b pr2 "$S/pr2" other-pr
run sh -c "cd '$S/pr2' && bash -s -- $c2 $c3 $c4 < '$S/carry.sh'"
(cd "$S/pr2" && regen_commit)
n=$(git rev-list --count other-pr..pr2)
[ $code = 0 ] && [ "$n" = 3 ] && pass "carry loop drops a commit that changes only a generated file and .foundry" || fail "carry loop on a commit that changes only a generated file and .foundry: exit $code, $n commits on pr2: $out"
git diff --quiet phase pr2 -- img.bin && [ "$(git cat-file -s pr2:img.bin)" = 6 ] && pass "binary file carried byte for byte" || fail "binary file not carried"

run prove pr1: pr2:other-pr
[ $code = 0 ] && [ "$(echo "$out" | tail -1)" = EQUAL ] && pass "correct split with regenerate commits: EQUAL" || fail "correct split: $out"

run prove pr1:
[ $code = 1 ] && echo "$out" | grep -q 'b.txt' && echo "$out" | grep -q '^FAIL the pull requests differ from the phase' && [ "$(echo "$out" | tail -1)" = 'NOT EQUAL' ] && pass "split that drops a change: NOT EQUAL" || fail "dropped change: $out"

bad() { git branch -q -f "$1" pr1; (cd "$S/pr1" && git checkout -q "$1" && shift && "$@"; git checkout -q pr1); }
bad pr1x sh -c 'echo extra > extra.txt && git add extra.txt && git commit -q -m extra'
run prove pr1x: pr2:other-pr
[ $code = 1 ] && echo "$out" | grep -q 'extra.txt' && pass "split that adds a change: NOT EQUAL" || fail "added change: $out"

bad pr1f sh -c 'mkdir -p .foundry && echo leak > .foundry/leak.md && git add .foundry && git commit -q -m leak'
run prove pr1f: pr2:other-pr
[ $code = 1 ] && echo "$out" | grep -q '^FAIL pr1f: contains .foundry/leak.md$' && pass "branch with a file under .foundry: NOT EQUAL" || fail ".foundry leak: $out"

bad pr1r sh -c "echo changed >> a.txt && git commit -q -am 'chore(s-stack): regenerate generated files'"
run prove pr1r: pr2:other-pr
[ $code = 1 ] && echo "$out" | grep -q -E '^FAIL pr1r: regenerate commit [0-9a-f]+ changes a.txt$' && pass "regenerate commit changing a hand-written file: NOT EQUAL" || fail "regenerate hand-written file: $out"

bad pr1y sh -c "sed 's/^deps: .*/deps: [x]/' pkg/apm.yml > ../y && cat ../y > pkg/apm.yml && git commit -q -am 'chore(s-stack): regenerate generated files'"
run prove pr1y: pr2:other-pr
[ $code = 1 ] && echo "$out" | grep -q -E '^FAIL pr1y: regenerate commit [0-9a-f]+ changes -deps: \[\]$' && echo "$out" | grep -q -F '+deps: [x]' && pass "regenerate commit changing a non-version apm.yml line: NOT EQUAL" || fail "regenerate apm.yml line: $out"

bad pr1g sh -c "echo hand-fixed >> pkg/apm.lock.yaml && git commit -q -am 'fix: lockfile'"
run prove pr1g: pr2:other-pr
[ $code = 0 ] && [ "$(echo "$out" | tail -1)" = EQUAL ] && pass "own commit that changes only a generated file is skipped by the proof: EQUAL" || fail "own commit that changes only a generated file: $out"

git checkout -q main; echo 'readme from main' > README; commit 'docs: main moves'; git checkout -q orch

git branch -q pr1h pr1
git worktree add -q "$S/pr1h" pr1h
(cd "$S/pr1h" && merge main && echo 'by hand' >> a.txt && git add a.txt && regen && git commit -q --no-edit)
run prove pr1h: pr2:other-pr
[ $code = 1 ] && echo "$out" | grep -q -E '^FAIL pr1h: merge [0-9a-f]+ changes a.txt by hand$' && pass "merge commit carrying a hand-made edit: NOT EQUAL" || fail "hand-made merge edit: $out"

(cd "$S/pr1" && merge main && regen && git commit -q --no-edit && regen_commit)
[ "$(git rev-list --merges --count main..pr1)" = 1 ] && git show pr1:README | grep -q 'from main' || fail "clean merge of main did not make one merge commit"
run prove pr1: pr2:other-pr
[ $code = 0 ] && [ "$(echo "$out" | tail -1)" = EQUAL ] && pass "clean automatic merge of main: EQUAL" || fail "clean merge: $out"

git checkout -q main
git diff main...other-pr | git apply --index && git commit -q -m 'feat: other phase (#1)'
line 11 'line 11 main' shared.txt; sed 's/^version: .*/version: "0.3.0"/' pkg/apm.yml > "$S/y" && cat "$S/y" > pkg/apm.yml; commit 'feat: main moves again'
git checkout -q orch

run sh -c "cd '$S/pr1' && bash -s -- main < '$S/merge.sh'"
if [ $code = 0 ] && (cd "$S/pr1" && regen && git commit -q --no-edit && regen_commit); then
  git show pr1:pkg/apm.yml | grep -q '^description: pr1$' && git show pr1:pkg/apm.yml | grep -q '^version: "0.3.1"$' || fail "version-only conflict lost a change"
  run prove pr1: pr2:other-pr
  [ $code = 0 ] && [ "$(echo "$out" | tail -1)" = EQUAL ] && pass "version-only conflict in apm.yml with a hand edit elsewhere: EQUAL" || fail "version-only conflict: $out"
else
  fail "version-only conflict in apm.yml aborted: $out"
fi

run sh -c "cd '$S/pr2' && bash -s -- main other-pr < '$S/merge.sh'"
if [ $code = 0 ] && (cd "$S/pr2" && regen && git commit -q --no-edit && regen_commit); then
  git show pr2:shared.txt | grep -q '^line 2 child$' && git show pr2:shared.txt | grep -q '^line 11 main$' && pass "squash-merged parent then a later main change in the same file: both changes kept" || fail "squash merge lost a change: $(git show pr2:shared.txt | tr '\n' ' ')"
  run prove pr1: pr2:other-pr
  [ $code = 0 ] && [ "$(echo "$out" | tail -1)" = EQUAL ] && pass "parent squash-merged, child merged main and regenerated, parent excluded by its kept ref: EQUAL" || fail "squash-merged parent: $out"
else
  fail "merge after squash-merged parent aborted: $out"
fi

cd "$root"
echo "$fails failed"
[ "$fails" = 0 ]
CHECK
```

### Line budget

The handbook has at most 200 lines. Expected: `<n>/200` with `n` at most 200, and exit `0`.

```bash
/bin/bash <<'CHECK'
f="$(git rev-parse --show-toplevel)/packages/s-stack/.apm/skills/sam-mode/handbooks/pr-creator.md"
n=$(wc -l < "$f" | tr -d ' ')
echo "$n/200 $f"
[ "$n" -le 200 ]
CHECK
```

## Evidence

### Scratch repository at handbook commit `391d9a86ba533c163608938dda6f2d881e5f8c41`

The scratch-repository check printed twelve `PASS` lines and two failures, and exited `1`.

- `FAIL carry loop on a commit that changes only a generated file and .foundry: exit 1 ... error: No valid patches in input`. The carry loop, handbook line 63, tests `git diff-tree --quiet "$c^" "$c" -- "${paths[@]}"`. Without `-r`, `git diff-tree` compares top-level entries, so a changed `pkg/` directory counts as a difference even when every changed file under it is excluded. The empty patch then reaches `git apply`, which exits non-zero, and the loop exits `1` before the regenerate commit.
- `FAIL pr1g: <sha> does not apply`, then `NOT EQUAL`. The proof, handbook line 112, has the same test.

With `git diff-tree -r --quiet` in both places, in a copy of the handbook outside the repository, the same check printed `0 failed`.
