# Phase `pr-handbook` checks

Phase `pr-handbook` ships `packages/s-stack/.apm/skills/sam-mode/handbooks/pr-creator.md`, the PR creator's handbook, and `packages/s-stack/.apm/skills/sam-mode/references/pr-commands.md`, which holds the one script the PR creator runs. The script is the behaviour, so the checks extract it at run time and run it as the handbook says: copied into `pr.sh` outside the repository and called as `bash pr.sh refresh ...` and `bash pr.sh prove ...`. A change that breaks the script fails these checks. Run each block from anywhere inside the repository, with `/bin/bash` as written, because the agent shell is zsh.

## Rerun

### The script blocks parse

Every fenced `bash` block in `references/pr-commands.md` passes `bash -n` as extracted, and exactly one of them is the script, which answers `refresh` and `prove`. Expected: one `bash -n ok` line per block, `script block <n>`, and exit `0`.

```bash
/bin/bash <<'CHECK'
ref="$(git rev-parse --show-toplevel)/packages/s-stack/.apm/skills/sam-mode/references/pr-commands.md"
d=$(mktemp -d "${TMPDIR:-/tmp}/pr-commands.XXXXXX"); trap 'rm -rf "$d"' EXIT
awk -v dir="$d" '/^```bash$/ { n++; f = sprintf("%s/%02d.sh", dir, n); inb = 1; next } /^```$/ { inb = 0; next } inb { print > f }' "$ref"
status=0; scripts=0
for f in "$d"/*.sh; do
  [ -e "$f" ] || { echo "no bash block in $ref"; exit 1; }
  if bash -n "$f"; then echo "bash -n ok $(basename "$f")"; else echo "bash -n FAILED $(basename "$f")"; status=1; fi
  grep -q -E '^ *refresh \| prove\)' "$f" && { echo "script block $(basename "$f" .sh)"; scripts=$((scripts + 1)); }
done
[ "$scripts" = 1 ] || { echo "expected one script block, found $scripts"; status=1; }
exit $status
CHECK
```

### Scratch repositories

The check builds throwaway repositories under `$TMPDIR`, with git's global and system configuration switched off, and deletes them on exit. Each has a bare `origin` that refuses every non-fast-forward push, so a force-push by the script or by the round would fail the case. A forge rewrite, as GitHub makes when a stack parent merges, is written straight into the bare repository instead.

Each repository's `main` holds a package `pkg/` with `apm.yml`, whose second line is `version:`, and `apm.lock.yaml`, plus `shared.txt` of twelve lines. A stand-in regenerate command sets `pkg`'s `version:` to the patch after `origin/main`'s and rewrites the lockfile from the tree. The parameter lines stay as the reference file ships them, so `REGEN` is `^chore(s-stack): regenerate generated files$`, `GEN` excludes `*apm.lock.yaml` and `LINES` covers `*apm.yml`.

The harness follows the handbook's round for one branch. It runs `git fetch origin`, then `git worktree add --no-track -B <branch> <path> origin/<branch>`, or `-b <branch> <path> origin/<base>` for a new branch. In that worktree it runs `bash pr.sh refresh origin/main <spec> <commits>` and the stand-in regenerate command, committing with the regenerate subject when it changed anything. It then runs `git push -u origin <branch>` when `origin/<branch>` is missing or differs from `HEAD`, and removes the worktree. Branches below a stacked branch have their round first. The proof runs as `bash pr.sh prove orch phase origin/main <spec> ...` from the clone, where `orch` is the orchestrator branch and `phase` the phase branch, both local and never pushed. Another phase's pull request is cut from `main`, ends with a regenerate commit and exists only on `origin`. A squash merge commits the merged tree onto `main` with one parent, as GitHub does, and keeps the merged branch's ref. Commits a round adds are counted along the first-parent chain from the previous `origin/<branch>`, as merges, regenerate commits and all commits.

Each case prints `PASS <case>` or `FAIL <case>: <output>`. The block ends with `<n> failed` and exits `0` only when no case fails. Expected results:

| Repository | Case | Expected |
| --- | --- | --- |
| `split` | First build of `pr1:main` with the first content commit and of `pr2:other-pr` with the other three | both exit `0`; `pr2` holds two own commits, because the commit that changes only the lockfile and `.foundry/` drops out; `img.bin` byte for byte; `origin/main` an ancestor of `pr1` |
| `split` | Correct split with regenerate commits, `pr1:main` and `pr2:other-pr` | `EQUAL`, exit `0` |
| `split` | `pr2` left out | `b.txt` listed, `FAIL the pull requests differ from the phase`, `NOT EQUAL`, exit `1` |
| `split` | `pr1` plus a commit adding `extra.txt` | `extra.txt` listed, `NOT EQUAL`, exit `1` |
| `split` | `pr1` plus a commit adding `.foundry/leak.md` | `FAIL pr1f: contains .foundry/leak.md`, exit `1` |
| `split` | `pr1` plus a regenerate commit that changes `a.txt` | `FAIL pr1r: regenerate commit <sha> changes a.txt`, exit `1` |
| `split` | `pr1` plus a regenerate commit that changes `deps:` in `apm.yml` | that commit named with `-deps: []` and `+deps: [x]`, exit `1` |
| `split` | An immediate second round on `pr1`, and on `pr2` | each prints `up to date with`, adds no commit and pushes nothing |
| `split` | `main` moves, then a round on `pr1` | one merge commit and one regenerate commit, pushed as a fast-forward, `origin/main` an ancestor, proof `EQUAL` |
| `split` | `main` moves and raises `version:` to the branch's own `"0.1.1"`, then a round on `pr1` | one merge and one regenerate commit, `version: "0.1.2"`, proof `EQUAL` |
| `split` | `main` moves, and a round on `pr1` stops after refreshing and regenerating, before its push | `origin/pr1` unchanged |
| `split` | The next round on `pr1`, started from `origin/pr1` | one merge and one regenerate commit over the old `origin/pr1`, pushed, proof `EQUAL` |
| `split` | The round after that | `up to date with`, no commit, no push |
| `split` | No regenerate commit on `pr1` reverts an earlier one | no regenerate commit sets a file back to its content before an earlier regenerate commit changed it |
| `split` | `main` moves, and `pr1h` merges it by hand with an extra edit to `a.txt` inside the merge commit | `a.txt` listed, `FAIL pr1h: its head differs from its own commits on its base`, exit `1` |
| `split` | `other-pr` squash-merged into `main`, then a round on `pr2` as `pr2:main::other-pr` | one merge and one regenerate commit, `shared.txt` line 2 is `line 2 child`, hand-written diff against `main` is `b.txt`, `img.bin` and `shared.txt`, proof `pr1:main pr2:main::other-pr` `EQUAL` with `other-pr` excluded through its kept ref |
| `undeclared` | A branch cut from another phase's open pull request `other-pr`, so its own commits carry `other-pr`'s change, which the orchestrator branch already holds, given as `pr2:main` with no dependency | its hand-written diff against `main` holds `o.txt`, which is not in the phase, so `NOT EQUAL`, exit `1` |
| `review1` | Another pull request's fix to a squash-merged parent's line, which the child never touched, after the child's round as `child:main::parent` | line 2 is `main`'s fix, the hand-written diff against `main` is `c.txt` only, proof `EQUAL` |
| `review2a` | A fix round whose fix edits `apm.yml`'s `description:`, next to a `version:` line that the branch's regenerate commit changed | exit `0`, the new description carried, `version: "0.1.1"` kept, proof `EQUAL` |
| `review2b` | A first build whose commit edits `description:`, while the orchestrator branch holds another phase's `version:` raise | exit `0`, the new description carried, proof `EQUAL` |
| `review3` | The phase merged a newer orchestrator branch, with another phase's change two lines from the phase's own, then a fix round | exit `0`, proof `EQUAL` |
| `review4` | A pull request targeting `main` with two open dependencies, both then squash-merged, then a round as `pr3:main::depA,depB` | exit `0`, the child's lines kept in `a.txt` and `b.txt`, `origin/main` an ancestor, proof `EQUAL` |
| `review5` | `main` moves under a stack, the parent's round and then the child's as `child:parent` | the child's hand-written diff against its parent is `c.txt` only, one merge base, `origin/main` an ancestor of both, proof `EQUAL` |
| `review6` | Paths with spaces: a squash-merged parent and the child both changed `docs dir/read me.md`, and `main` raised `my pkg/apm.yml`'s `version:` next to the child's `description:` edit | exit `0`, `line 2 child` kept, `my pkg/apm.yml` has `main`'s `version:` and the child's description, proof `EQUAL` |
| `rewrite` | A stack parent squash-merged, the child's head rewritten on the forge onto `main` with the same tree, `main` moves, then a round as `child:main::parent` | the rewritten head is an ancestor of the new head, the push is a fast-forward, the hand-written diff against `main` is `c.txt` only, proof `EQUAL` |

```bash
/bin/bash <<'CHECK'
set -u
root=$(git rev-parse --show-toplevel)
ref="$root/packages/s-stack/.apm/skills/sam-mode/references/pr-commands.md"
S=$(mktemp -d "${TMPDIR:-/tmp}/pr-handbook-check.XXXXXX")
trap 'rm -rf "$S"' EXIT
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
export GIT_AUTHOR_NAME=check GIT_AUTHOR_EMAIL=check@example.com GIT_COMMITTER_NAME=check GIT_COMMITTER_EMAIL=check@example.com
REGEN_SUBJECT='chore(s-stack): regenerate generated files' REGEN_RE='^chore(s-stack): regenerate generated files$'
fails=0
pass() { echo "PASS $1"; }
fail() { echo "FAIL $1"; fails=$((fails + 1)); }

awk -v dir="$S" '/^```bash$/ { n++; f = sprintf("%s/block%02d.sh", dir, n); inb = 1; next } /^```$/ { inb = 0; next } inb { print > f }' "$ref"
script=$(grep -l -E '^ *refresh \| prove\)' "$S"/block*.sh | head -1)
[ -n "$script" ] || { echo "FAIL no script block in $ref"; exit 1; }
cp "$script" "$S/pr.sh"

commit() { git add -A && git commit -q -m "$1"; }
line() { sed "$1s/.*/$2/" "$3" > "$S/l" && cat "$S/l" > "$3"; }
set_version() { sed "s/^version: .*/version: \"$1\"/" "$2" > "$S/y" && cat "$S/y" > "$2"; }
relock() { git ls-files -s -- . ':(exclude)*apm.lock.yaml' > pkg/apm.lock.yaml && git add pkg/apm.lock.yaml; }
regen_commit() {
  local v; v=$(git show origin/main:pkg/apm.yml | sed -n 's/^version: "\(.*\)"$/\1/p')
  set_version "${v%.*}.$(( ${v##*.} + 1 ))" pkg/apm.yml && git add pkg/apm.yml && relock
  git diff --cached --quiet || git commit -q -m "$REGEN_SUBJECT"
}
push() { local b; b=$(git symbolic-ref --short HEAD); [ "$(git rev-parse -q --verify "origin/$b")" = "$(git rev-parse HEAD)" ] || git push -q -u origin "$b"; }
init() {
  O="$S/$1.git" R="$S/$1"
  git init -q --bare -b main "$O" && git -C "$O" config receive.denyNonFastForwards true
  git init -q -b main "$R" && cd "$R" && git remote add origin "$O" || exit 1
  mkdir pkg; printf 'name: pkg\nversion: "0.1.0"\ndescription: "A package."\nlicense: MIT\ndeps: []\n' > pkg/apm.yml
  for i in 1 2 3 4 5 6 7 8 9 10 11 12; do echo "line $i"; done > shared.txt
  echo readme > README; : > pkg/apm.lock.yaml; git add -A; relock; commit initial; git push -q -u origin main
}
in_tree() { local wt="$S/wt.tmp" c; git worktree add -q --detach "$wt" "$1" && (cd "$wt" && shift && "$@"); c=$?; git worktree remove --force "$wt"; return $c; }
on_main() { local m=$1; shift; git fetch -q origin; in_tree origin/main sh_commit "$m" "$@"; git fetch -q origin; }
sh_commit() { local m=$1; shift; "$@" && relock && commit "$m" && git push -q origin HEAD:main; }
other() {
  local b=$1 m=$2; shift 2; git fetch -q origin
  in_tree origin/main other_pr "$b" "$m" "$@"; git fetch -q origin
}
other_pr() { local b=$1 m=$2; shift 2; "$@" && commit "$m" && regen_commit && git push -q origin "HEAD:refs/heads/$b"; }
squash() { git fetch -q origin; in_tree origin/main squash_in "$1"; git fetch -q origin; }
squash_in() {
  git merge -q --squash "origin/$1" >/dev/null 2>&1 || [ -z "$(git diff --name-only --diff-filter=U -- . ':(exclude)*apm.lock.yaml')" ] || return 1
  relock && commit "feat: $1 (#1)" && git push -q origin HEAD:main
}
variant() { local b=$1 from=$2 wt="$S/wt.$1" c; shift 2; git worktree add -q -b "$b" "$wt" "$from" && (cd "$wt" && "$@"); c=$?; git worktree remove --force "$wt"; return $c; }
round() {
  local b=$1 spec=$2 base wt="$S/wt.$1"; shift 2; base=$(echo "$spec" | cut -d: -f2)
  git fetch -q origin
  if git rev-parse -q --verify "refs/remotes/origin/$b" >/dev/null; then git worktree add -q --no-track -B "$b" "$wt" "origin/$b"
  else git worktree add -q --no-track -b "$b" "$wt" "origin/$base"; fi || { out="worktree add failed"; code=1; return 1; }
  out=$(cd "$wt" && bash "$S/pr.sh" refresh origin/main "$spec" "$@" 2>&1 && regen_commit 2>&1 && push 2>&1); code=$?
  git worktree remove --force "$wt"; git fetch -q origin; return $code
}
stopped_round() {
  local b=$1 spec=$2 wt="$S/wt.$1"; shift 2; git fetch -q origin
  git worktree add -q --no-track -B "$b" "$wt" "origin/$b" || return 1
  out=$(cd "$wt" && bash "$S/pr.sh" refresh origin/main "$spec" "$@" 2>&1 && regen_commit 2>&1); code=$?
  git worktree remove --force "$wt"; return $code
}
prove() { out=$(bash "$S/pr.sh" prove orch phase origin/main "$@" 2>&1); code=$?; }
equal() { prove "$@"; [ $code = 0 ] && [ "$(echo "$out" | tail -1)" = EQUAL ]; }
not_equal() { prove "$@"; [ $code = 1 ] && [ "$(echo "$out" | tail -1)" = 'NOT EQUAL' ]; }
added() { echo "$(git rev-list --first-parent --merges --count "$1..$2") $(git rev-list --first-parent --count --grep="$REGEN_RE" "$1..$2") $(git rev-list --first-parent --count "$1..$2")"; }
own_count() { local b=$1; shift; git rev-list --no-merges --count --invert-grep --grep="$REGEN_RE" "$b" --not "$@"; }
hand() { git diff --name-only "$1...$2" -- . ':(exclude)*apm.lock.yaml' ':(exclude)*apm.yml' | tr '\n' ' '; }
ancestor() { git merge-base --is-ancestor "$1" "$2"; }
no_reverts() {
  local r e f seen="" bad=""
  for r in $(git rev-list --reverse --first-parent --grep="$REGEN_RE" "$@"); do
    for f in $(git diff-tree --no-commit-id --name-only -r "$r"); do
      for e in $seen; do
        git diff-tree --no-commit-id --name-only -r "$e" | grep -q -x -F "$f" && [ "$(git rev-parse "$r:$f")" = "$(git rev-parse "$e^:$f")" ] && bad="$bad $r restores $f to before $e;"
      done
    done
    seen="$seen $r"
  done
  out="regenerate commits:$seen;$bad"; [ -z "$bad" ] && [ -n "$seen" ]
}
start_orch() { git checkout -q -b orch origin/main && mkdir .foundry && echo plan > .foundry/plan.md && commit 'chore: plan'; }
merge_dep() { git merge -q --no-ff --no-edit "$1" >/dev/null 2>&1 || { relock && git commit -q --no-edit; }; }

feat_other_pr() { line 2 'line 2 parent' shared.txt && echo o > o.txt; }
init split
other other-pr 'feat: other phase' feat_other_pr
start_orch; merge_dep origin/other-pr
git checkout -q -b phase orch
echo a > a.txt; echo 'keywords: [a]' >> pkg/apm.yml; echo stale1 >> pkg/apm.lock.yaml; commit 'feat: a'; c1=$(git rev-parse HEAD)
echo s1 > .foundry/status.md; commit 'chore: status'
line 2 'line 2 child' shared.txt; echo b > b.txt; echo stale2 >> pkg/apm.lock.yaml; commit 'feat: b'; c2=$(git rev-parse HEAD)
printf 'bin\000\001\377' > img.bin; commit 'feat: binary'; c3=$(git rev-parse HEAD)
echo stale3 >> pkg/apm.lock.yaml; echo s2 > .foundry/status.md; commit 'chore: lockfile and status only'; c4=$(git rev-parse HEAD)

round pr1 pr1:main "$c1"; o1="$code: $out"
round pr2 pr2:other-pr "$c2" "$c3" "$c4"; o2="$code: $out"
[ "${o1%%:*}" = 0 ] && [ "${o2%%:*}" = 0 ] && [ "$(own_count origin/pr1 origin/main)" = 1 ] && [ "$(own_count origin/pr2 origin/other-pr)" = 2 ] \
  && git diff --quiet phase origin/pr2 -- img.bin && [ "$(git cat-file -s origin/pr2:img.bin)" = 6 ] && ancestor origin/main origin/pr1 \
  && pass "first build of pr1 and of pr2 stacked on another phase's pull request" || fail "first build: pr1 $o1; pr2 $o2"
equal pr1:main pr2:other-pr && pass "correct split with regenerate commits: EQUAL" || fail "correct split: $out"
not_equal pr1:main && echo "$out" | grep -q 'b.txt' && echo "$out" | grep -q '^FAIL the pull requests differ from the phase$' && pass "split that drops a change: NOT EQUAL" || fail "dropped change: $out"
add_extra() { echo extra > extra.txt && commit extra; }
variant pr1x pr1 add_extra; not_equal pr1x:main pr2:other-pr && echo "$out" | grep -q 'extra.txt' && pass "split that adds a change: NOT EQUAL" || fail "added change: $out"
add_leak() { mkdir -p .foundry && echo leak > .foundry/leak.md && commit leak; }
variant pr1f pr1 add_leak; not_equal pr1f:main pr2:other-pr && echo "$out" | grep -q '^FAIL pr1f: contains .foundry/leak.md$' && pass "branch with a file under .foundry: NOT EQUAL" || fail ".foundry leak: $out"
regen_hand() { echo changed >> a.txt && git commit -q -am "$REGEN_SUBJECT"; }
variant pr1r pr1 regen_hand; not_equal pr1r:main pr2:other-pr && echo "$out" | grep -q -E '^FAIL pr1r: regenerate commit [0-9a-f]+ changes a.txt$' && pass "regenerate commit changing a hand-written file: NOT EQUAL" || fail "regenerate commit changing a.txt: $out"
regen_deps() { sed 's/^deps: .*/deps: [x]/' pkg/apm.yml > "$S/y" && cat "$S/y" > pkg/apm.yml && git commit -q -am "$REGEN_SUBJECT"; }
variant pr1y pr1 regen_deps; not_equal pr1y:main pr2:other-pr && echo "$out" | grep -q -E '^FAIL pr1y: regenerate commit [0-9a-f]+ changes -deps: \[\]$' && echo "$out" | grep -q -x -F '+deps: [x]' && pass "regenerate commit changing an apm.yml line other than version: NOT EQUAL" || fail "regenerate commit changing deps: $out"

h1=$(git rev-parse origin/pr1) h2=$(git rev-parse origin/pr2)
round pr1 pr1:main; o1="$code: $out"; round pr2 pr2:other-pr; o2="$code: $out"
echo "$o1" | grep -q '^0: up to date with' && echo "$o2" | grep -q '^0: up to date with' && [ "$(git rev-parse origin/pr1) $(git rev-parse pr1) $(git rev-parse origin/pr2)" = "$h1 $h1 $h2" ] \
  && pass "an up-to-date round changes nothing" || fail "up-to-date round: pr1 $o1, adds $(added "$h1" origin/pr1); pr2 $o2"

readme() { echo "readme $1" > README; }
on_main 'docs: main moves' readme 2
h=$(git rev-parse origin/pr1); round pr1 pr1:main; o="$code: $out"
[ "${o%%:*}" = 0 ] && [ "$(added "$h" origin/pr1)" = '1 1 2' ] && ancestor "$h" origin/pr1 && ancestor origin/main origin/pr1 && equal pr1:main pr2:other-pr \
  && pass "a round after main moves: one merge and one regenerate commit, fast-forward, EQUAL" || fail "round after a move: $o; adds $(added "$h" origin/pr1); proof $out"
raise() { readme 3 && set_version "$1" pkg/apm.yml; }
on_main 'feat: another pull request raises the version' raise 0.1.1
h=$(git rev-parse origin/pr1); round pr1 pr1:main; o="$code: $out"
[ "${o%%:*}" = 0 ] && [ "$(added "$h" origin/pr1)" = '1 1 2' ] && git show origin/pr1:pkg/apm.yml | grep -q -x 'version: "0.1.2"' && equal pr1:main pr2:other-pr \
  && pass "a round after main takes the branch's version: one merge, one regenerate commit, EQUAL" || fail "round after main takes the version: $o; adds $(added "$h" origin/pr1); proof $out"
on_main 'docs: main moves again' readme 4
h=$(git rev-parse origin/pr1); stopped_round pr1 pr1:main; o="$code: $out"
[ "${o%%:*}" = 0 ] && [ "$(git rev-parse origin/pr1)" = "$h" ] && [ "$(git rev-parse pr1)" != "$h" ] || fail "the stopped round did not leave an unpushed local head: $o"
round pr1 pr1:main; o="$code: $out"
[ "${o%%:*}" = 0 ] && [ "$(added "$h" origin/pr1)" = '1 1 2' ] && ancestor "$h" origin/pr1 && ancestor origin/main origin/pr1 && equal pr1:main pr2:other-pr \
  && pass "a round that stopped part-way finishes on the next round from origin/pr1" || fail "round after a stopped round: $o; adds $(added "$h" origin/pr1); proof $out"
h=$(git rev-parse origin/pr1); round pr1 pr1:main; o="$code: $out"
echo "$o" | grep -q '^0: up to date with' && [ "$(git rev-parse origin/pr1)" = "$h" ] && pass "the round after a finished one changes nothing" || fail "round after a finished one: $o; adds $(added "$h" origin/pr1)"
no_reverts origin/pr1 ^origin/main && pass "no regenerate commit reverts an earlier one" || fail "regenerate commits revert: $out"

on_main 'docs: main moves for a hand edit' readme 5
hand_merge() { git merge -q --no-ff --no-commit origin/main >/dev/null 2>&1; relock && echo 'by hand' >> a.txt && git add -A && git commit -q --no-edit; }
variant pr1h origin/pr1 hand_merge
not_equal pr1h:main pr2:other-pr && echo "$out" | grep -q 'a.txt' && echo "$out" | grep -q -x 'FAIL pr1h: its head differs from its own commits on its base' && pass "a merge commit carrying a hand edit: NOT EQUAL" || fail "hand edit in a merge commit: $out"

squash other-pr
h=$(git rev-parse origin/pr2); round pr2 pr2:main::other-pr; o="$code: $out"
[ "${o%%:*}" = 0 ] && [ "$(added "$h" origin/pr2)" = '1 1 2' ] && ancestor origin/main origin/pr2 && [ "$(git show origin/pr2:shared.txt | sed -n 2p)" = 'line 2 child' ] \
  && [ "$(hand origin/main origin/pr2)" = 'b.txt img.bin shared.txt ' ] && equal pr1:main pr2:main::other-pr \
  && pass "parent squash-merged, the child's round and regenerate commit, parent excluded through its kept ref: EQUAL" || fail "squash-merged parent: $o; adds $(added "$h" origin/pr2); diff $(hand origin/main origin/pr2); proof $out"

cd "$S"; init undeclared
other other-pr 'feat: other phase' feat_other_pr
start_orch; merge_dep origin/other-pr; git checkout -q -b phase orch
echo b > b.txt; commit 'feat: b'; c1=$(git rev-parse HEAD)
git worktree add -q --no-track -b pr2 "$S/wt.pr2" origin/other-pr && (cd "$S/wt.pr2" && bash "$S/pr.sh" refresh origin/main pr2:main "$c1" >/dev/null && regen_commit && push)
git worktree remove --force "$S/wt.pr2"; git fetch -q origin
not_equal pr2:main && pass "a split whose own commits carry another phase's change from the orchestrator branch: NOT EQUAL" || fail "undeclared dependency: diff against main $(hand origin/main origin/pr2); proof exit $code: $out"

feat_parent() { line 2 'line 2 parent' shared.txt; }
fix_line2() { line 2 'line 2 fixed by a later pull request' shared.txt; }
cd "$S"; init review1
other parent 'feat: parent' feat_parent
start_orch; merge_dep origin/parent; git checkout -q -b phase orch
echo c > c.txt; commit 'feat: child'; c1=$(git rev-parse HEAD)
round child child:parent "$c1" || fail "review1 first build: $out"
squash parent; on_main 'fix: a later pull request fixes line 2' fix_line2
round child child:main::parent; o="$code: $out"
[ "${o%%:*}" = 0 ] && [ "$(git show origin/child:shared.txt | sed -n 2p)" = 'line 2 fixed by a later pull request' ] && [ "$(hand origin/main origin/child)" = 'c.txt ' ] && equal child:main::parent \
  && pass "review 1: a squash-merged parent's line fixed on main stays fixed, and the proof agrees" || fail "review 1: $o; line 2 '$(git show origin/child:shared.txt | sed -n 2p)'; diff $(hand origin/main origin/child); proof $out"

describe() { line 3 "description: \"$1\"" pkg/apm.yml; }
cd "$S"; init review2a
start_orch; git checkout -q -b phase orch
echo a > a.txt; commit 'feat: a'; c1=$(git rev-parse HEAD)
round pr1 pr1:main "$c1" || fail "review2a first build: $out"
describe 'A better description.'; commit 'fix: describe the package'; f1=$(git rev-parse HEAD)
round pr1 pr1:main "$f1"; o="$code: $out"
[ "${o%%:*}" = 0 ] && git show origin/pr1:pkg/apm.yml | grep -q -x 'description: "A better description."' && git show origin/pr1:pkg/apm.yml | grep -q -x 'version: "0.1.1"' && equal pr1:main \
  && pass "review 2a: a fix next to a version: line the branch changed is carried" || fail "review 2a: $o; proof $out"

cd "$S"; init review2b
other other-pr 'feat: other phase' feat_other_pr
start_orch; merge_dep origin/other-pr; git checkout -q -b phase orch
echo a > a.txt; describe 'A better description.'; commit 'feat: a'; c1=$(git rev-parse HEAD)
round pr1 pr1:main "$c1"; o="$code: $out"
[ "${o%%:*}" = 0 ] && git show origin/pr1:pkg/apm.yml | grep -q -x 'description: "A better description."' && equal pr1:main \
  && pass "review 2b: a commit next to another phase's version: raise is carried" || fail "review 2b: $o; proof $out"

cd "$S"; init review3
start_orch; git checkout -q -b phase orch
line 3 'line 3 phase' shared.txt; echo a > a.txt; commit 'feat: a'; c1=$(git rev-parse HEAD)
round pr1 pr1:main "$c1" || fail "review3 first build: $out"
git checkout -q -b other-phase orch; line 5 'line 5 other phase' shared.txt; commit 'feat: other phase'
git checkout -q orch; git merge -q --no-ff --no-edit other-phase
git checkout -q phase; git merge -q --no-edit orch >/dev/null; echo b > b.txt; commit 'feat: b'; c2=$(git rev-parse HEAD)
round pr1 pr1:main "$c2"; o="$code: $out"
[ "${o%%:*}" = 0 ] && equal pr1:main && pass "review 3: the proof after the phase merged a newer orchestrator branch: EQUAL" || fail "review 3: $o; proof $out"

dep_line() { echo "$2" > "$1"; }
base_files() { echo 'a 1' > a.txt && echo 'b 1' > b.txt; }
cd "$S"; init review4
on_main 'feat: base files' base_files
other depA 'feat: depA' dep_line a.txt 'a 1 depA'
other depB 'feat: depB' dep_line b.txt 'b 1 depB'
start_orch; merge_dep origin/depA; merge_dep origin/depB; git checkout -q -b phase orch
echo 'a 1 depA child' > a.txt; echo 'b 1 depB child' > b.txt; commit 'feat: child builds on both'; c1=$(git rev-parse HEAD)
round pr3 pr3:main:depA,depB "$c1" || fail "review4 first build: $out"
squash depA; squash depB
round pr3 pr3:main::depA,depB; o="$code: $out"
[ "${o%%:*}" = 0 ] && [ "$(git show origin/pr3:a.txt) $(git show origin/pr3:b.txt)" = 'a 1 depA child b 1 depB child' ] && ancestor origin/main origin/pr3 && equal pr3:main::depA,depB \
  && pass "review 4: two squash-merged dependencies: EQUAL" || fail "review 4: $o; proof $out"

unrelated() { echo m > m.txt && line 9 'line 9 main' shared.txt; }
feat_p() { echo p > p.txt; }
cd "$S"; init review5
other parent 'feat: parent' feat_p
start_orch; merge_dep origin/parent; git checkout -q -b phase orch
echo c > c.txt; commit 'feat: child'; c1=$(git rev-parse HEAD)
round child child:parent "$c1" || fail "review5 first build: $out"
on_main 'feat: an unrelated pull request lands' unrelated
round parent parent:main || fail "review5 parent round: $out"
round child child:parent; o="$code: $out"
[ "${o%%:*}" = 0 ] && [ "$(hand origin/parent origin/child)" = 'c.txt ' ] && [ "$(git merge-base --all origin/parent origin/child | wc -l | tr -d ' ')" = 1 ] \
  && ancestor origin/main origin/parent && ancestor origin/main origin/child && equal child:parent \
  && pass "review 5: a stacked child's diff shows only its own change" || fail "review 5: $o; diff $(hand origin/parent origin/child); merge bases $(git merge-base --all origin/parent origin/child | wc -l | tr -d ' '); proof $out"

spaced() { mkdir -p 'docs dir' 'my pkg' && for i in 1 2 3 4 5 6; do echo "line $i"; done > 'docs dir/read me.md' && printf 'name: my\nversion: "0.1.0"\ndescription: "Mine."\n' > 'my pkg/apm.yml'; }
spaced_parent() { line 2 'line 2 parent' 'docs dir/read me.md'; }
bump_my() { set_version 0.2.0 'my pkg/apm.yml'; }
cd "$S"; init review6
on_main 'feat: spaced paths' spaced
other parent 'feat: parent' spaced_parent
start_orch; merge_dep origin/parent; git checkout -q -b phase orch
line 2 'line 2 child' 'docs dir/read me.md'; line 3 'description: "Spaced."' 'my pkg/apm.yml'; commit 'feat: child'; c1=$(git rev-parse HEAD)
round child child:parent "$c1" || fail "review6 first build: $out"
squash parent; on_main 'feat: another pull request raises my pkg' bump_my
round child child:main::parent; o="$code: $out"
[ "${o%%:*}" = 0 ] && [ "$(git show 'origin/child:docs dir/read me.md' | sed -n 2p)" = 'line 2 child' ] \
  && [ "$(git show 'origin/child:my pkg/apm.yml' | sed -n '2,3p' | tr '\n' '|')" = 'version: "0.2.0"|description: "Spaced."|' ] && equal child:main::parent \
  && pass "review 6: paths with spaces" || fail "review 6: $o; proof $out"

forge_rebase() {
  local old new wt="$S/wt.forge"
  old=$(git rev-parse "origin/$1")
  git worktree add -q --detach "$wt" "origin/$1" && (cd "$wt" && git rebase -q --onto origin/main "origin/$2" >/dev/null 2>&1); new=$(git -C "$wt" rev-parse HEAD); git worktree remove --force "$wt"
  git push -q origin "$new:refs/forge/rewrite" && git -C "$O" update-ref "refs/heads/$1" "$new" && git -C "$O" update-ref -d refs/forge/rewrite && git fetch -q origin || return 1
  [ "$(git rev-parse "origin/$1")" = "$new" ] && [ "$(git rev-parse "$old^{tree}")" = "$(git rev-parse "$new^{tree}")" ] && ! ancestor "$old" "$new"
}
cd "$S"; init rewrite
other parent 'feat: parent' feat_p
start_orch; merge_dep origin/parent; git checkout -q -b phase orch
echo c > c.txt; commit 'feat: child'; c1=$(git rev-parse HEAD)
round child child:parent "$c1" || fail "rewrite first build: $out"
squash parent
if forge_rebase child parent; then
  rewritten=$(git rev-parse origin/child)
  on_main 'docs: main moves' readme 2
  round child child:main::parent; o="$code: $out"
  [ "${o%%:*}" = 0 ] && ancestor "$rewritten" origin/child && ancestor origin/main origin/child && [ "$(hand origin/main origin/child)" = 'c.txt ' ] && equal child:main::parent \
    && pass "a head the forge rewrote is the next round's starting point: commits only on top, EQUAL" || fail "forge rewrite: $o; adds $(added "$rewritten" origin/child); proof $out"
else
  fail "forge rewrite: the simulated rebase did not keep the tree"
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

### Cold read. Restacking after a parent merged

Restacking is prose the PR creator acts on, so this check is a cold read. Start a fresh subagent, give it only the two files below, tell it to read nothing else, and ask the question. Its answer passes when it agrees in substance with every point of the expected answer. Wait for the subagent to finish before reporting.

Files, relative to the repository root:

- `packages/s-stack/.apm/skills/sam-mode/handbooks/pr-creator.md`
- `packages/s-stack/.apm/skills/sam-mode/references/pr-commands.md`

Prompt: "Read only the two files at the paths below and nothing else, not even files they link to. Answer from them alone. You are the PR creator for phase `widgets`, in a fix round, and both gates passed for the current code head. The default branch is `main`. Your phase's one pull request is #12, on branch `widgets-pr`. It was stacked on another phase's pull request #10, branch `gadgets-pr`. Since your last round, #10 was squash-merged into `main`, and GitHub then rewrote `widgets-pr`'s head with a force-push from the developer's account, keeping its tree. Your fix commit needs the change in another phase's open pull request #11, branch `doohickey-pr`, which has no pull request stacked on it. (1) Which commit does your round on `widgets-pr` start from, and what do you do with your old local head? (2) Which base do you choose, and what spec do you pass to the script? (3) Which commands change the base and the stacking on GitHub, and in what order relative to the push? (4) May you push or refresh `doohickey-pr` or `gadgets-pr`? (5) How do you push `widgets-pr`?"

Expected answer:

1. From `origin/widgets-pr`'s current head, the one GitHub rewrote, through `git worktree add --no-track -B widgets-pr <path> origin/widgets-pr`. The rewrite is not an error, and the old local head is never merged back in.
2. One open dependency, #11, with nothing stacked on it, so `widgets-pr` joins #11's stack with `doohickey-pr` as its base. #10 has merged, so it goes in the fourth field: `widgets-pr:doohickey-pr::gadgets-pr`, with the fix commit as the commit argument.
3. After the branch is pushed, `gh pr edit 12 --base doohickey-pr`, then `gh stack link 11 12`, naming only the direct parent and itself. Never #10, a merged pull request, and never `gh stack sync`, `rebase`, `push`, `submit` or `unstack`, or `gh stack link` with branch names.
4. No. Another phase's branch or pull request is never written, even when this one depends on it.
5. With a plain `git push -u origin widgets-pr`, only when `origin/widgets-pr` is missing or differs from `HEAD`. It is a fast-forward, and never a force-push.

## Evidence

### A forge rewrite keeps the tree

What it checks: the handbook's rule that GitHub may rewrite a stacked pull request's head when its parent merges, keeping the tree and changing the commits, so the PR creator takes that head as its starting point. The scratch case `rewrite` assumes this shape, and this check ties it to the forge.

How: pick a pull request of this run whose stack parent has merged, from the run's decisions. Read its force-push events with `gh api graphql`, asking for `pullRequest(number: <n>) { timelineItems(itemTypes: [HEAD_REF_FORCE_PUSHED_EVENT]) { nodes { ... on HeadRefForcePushedEvent { createdAt beforeCommit { oid tree { oid } } afterCommit { oid tree { oid } } } } } }`. The rule holds when an event at the parent's merge time has equal tree object ids for the two commits and different commit ids. The check only reads.
</content>
</invoke>
