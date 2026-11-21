# Phase `pr-handbook` checks

Phase `pr-handbook` ships `packages/s-stack/.apm/skills/sam-mode/handbooks/pr-creator.md`, the PR creator's handbook, and `packages/s-stack/.apm/skills/sam-mode/references/pr-commands.md`, which holds the one script the PR creator runs. The script is the behaviour, so the checks extract it at run time and run it the way the handbook does: copied into `pr.sh` outside the repository and called as `bash pr.sh refresh <phase branch> <default branch> <spec> [<commit> ...]` and `bash pr.sh prove ...`. Run each block from anywhere inside the repository with `/bin/bash`, as written, because the agent shell is zsh. The script then runs under the same bash.

## Rerun

### The script block parses

Every fenced `bash` block in `references/pr-commands.md` passes `bash -n` as extracted, and exactly one of them is the script, which answers `refresh` and `prove`. Expected: a `bash -n ok` line for each block, one `script block` line, and exit `0`.

```bash
/bin/bash <<'CHECK'
md="$(git rev-parse --show-toplevel)/packages/s-stack/.apm/skills/sam-mode/references/pr-commands.md"
d=$(mktemp -d "${TMPDIR:-/tmp}/pr-commands.XXXXXX"); trap 'rm -rf "$d"' EXIT
awk '/^```bash$/ { b = 1; n++; next } /^```$/ { b = 0; next } b { print > (dir "/block" n ".sh") }' dir="$d" "$md"
status=0 scripts=0
for f in "$d"/block*.sh; do
  [ -e "$f" ] || { echo "no bash block in $md"; exit 1; }
  if bash -n "$f"; then echo "bash -n ok $(basename "$f")"; else echo "bash -n FAILED $(basename "$f")"; status=1; fi
  grep -q -E '^ *refresh \| prove\)' "$f" && { echo "script block $(basename "$f")"; scripts=$((scripts + 1)); }
done
[ "$scripts" = 1 ] || { echo "expected one script block, found $scripts"; status=1; }
exit $status
CHECK
```

### Scratch repositories

The block builds throwaway repositories under `$TMPDIR` with git's global and system configuration switched off, and deletes them on exit. Each repository has a bare `origin` that refuses every non-fast-forward push and every branch deletion, so a force-push by the script or by a round fails its case. A forge rewrite, as GitHub makes when a stack parent merges, is written straight into the bare repository instead.

`main` holds a package `pkg/` whose `apm.yml` has `version:` on its second line and `description:` on its third, an `apm.lock.yaml` beside each `apm.yml` that lists the package's other files, a twelve-line `shared.txt` and a `README`. The stand-in regenerate command sets `pkg`'s `version:` to the patch after `origin/main`'s and rewrites every lockfile from the tree, and commits with the regenerate subject when that changed anything. The script's parameter lines stay as the reference file ships them.

Each case follows the handbook's round for each branch, bottom of the stack first. It runs `git fetch origin`, then `git worktree add --no-track -B <branch> <path> origin/<branch>`, or `-b <branch> <path> origin/<base>` for a new branch. In that worktree it runs `bash pr.sh refresh phase origin/main <spec> <commits>` and the regenerate command, then `git push -u origin <branch>` when `origin/<branch>` is missing or differs from `HEAD`, and removes the worktree. The proof runs from the clone as `bash pr.sh prove orch phase origin/main <spec> ...`, with every open pull request, and with a merged one only where a case lists it. `orch` and `phase` are local, never pushed. The orchestrator branch carries `.foundry/`, and the phase merges it with `git merge --no-ff`. Another phase's pull request is cut from `main`, ends with a regenerate commit and exists only on `origin`. A squash merge commits the merged tree onto `main` with one parent and keeps the merged branch. A round's added commits are counted along the first parent from the old `origin/<branch>`.

A round keeps the guarantees when the old `origin/<branch>` is an ancestor of the new one, `origin/main` is an ancestor of it, and it adds at most one merge commit and one regenerate commit. Each case prints `PASS <case>` or `FAIL <case>: <output>`, and the block ends with `<n> failed` and exits `0` only when no case failed.

| Case | Scenario | Expected |
| --- | --- | --- |
| `done-when build` | Phase commits `a` (with lockfile and `apm.yml` hunks), a `.foundry/` status commit, `b` (on `shared.txt` line 2, which another phase's open pull request `other-pr` also changed), a binary, and a lockfile-and-status commit. `pr1:main` takes `a`; `pr2:other-pr` takes the other three. | Both exit `0`. Hand-written diffs are `a.txt` and `b.txt img.bin shared.txt`. The binary is byte-identical. `pr1`'s carried commit ends with `(cherry picked from commit <a>)`. |
| `done-when correct split` | `pr1:main pr2:other-pr` | `EQUAL`, exit `0` |
| `done-when drops a change` | `pr1:main` alone | `FAIL b.txt has not landed and is in no open pull request, so it needs a new pull request`, `NOT EQUAL`, exit `1` |
| `done-when adds a change` | `pr1` plus a commit adding `extra.txt` | `FAIL pr1x: it changes extra.txt, which the phase does not`, `NOT EQUAL` |
| `done-when .foundry` | `pr1` plus `.foundry/leak.md` | `FAIL pr1f: contains .foundry/leak.md`, `NOT EQUAL` |
| `done-when regenerate a.txt` | `pr1` plus a regenerate commit that changes `a.txt` | `FAIL pr1r: regenerate commit <sha> changes a.txt`, `NOT EQUAL` |
| `done-when regenerate deps` | `pr1` plus a regenerate commit that changes `deps:` in `apm.yml` | that commit named with `-deps: []` and `+deps: [x]`, `NOT EQUAL` |
| `done-when squash-merged parent` | `other-pr` squash-merged, then `pr2`'s round as `pr2:main::other-pr` | guarantees kept, exactly one merge and one regenerate commit, `shared.txt` line 2 `line 2 child`, diff `b.txt img.bin shared.txt`, proof `pr1:main pr2:main::other-pr` `EQUAL` |
| `guarantee up to date` | A round straight after the build | `up to date with`, `origin/pr1` unchanged |
| `guarantee main moves` | `main` changes `README`, then a round | guarantees kept, one merge and one regenerate commit, `EQUAL` |
| `guarantee version taken` | `main` raises `version:` to the branch's `"0.1.1"`, then a round | guarantees kept, `version: "0.1.2"`, `EQUAL` |
| `guarantee interrupted` | `main` moves, a round stops after refresh and regenerate and before its push, then a full round | `origin/pr1` unchanged by the first. The second keeps the guarantees over the old `origin/pr1`, with one merge and one regenerate commit, and `EQUAL`. |
| `guarantee repeated` | Two more rounds | `origin/pr1` unchanged |
| `guarantee fix rerun` | A fix round, then the same round again with the same fix commit | the second leaves `origin/pr1` unchanged |
| `hand edit in a merge` | `pr1h` merges `main` by hand and edits `a.txt` inside the merge commit | `FAIL pr1h: its head differs from its target tree`, `a.txt` listed, `NOT EQUAL` |
| `forge rewrite` | A same-phase stack `parent:main`, `child:parent`. `parent` is squash-merged, the forge rebases `child` onto `main` with the same tree, `main` moves, then `child:main::parent` | guarantees kept over the rewritten head, diff `c.txt`, `EQUAL` |
| `round 1 squash step` | Child stacked on another phase's `parent`, which is squash-merged; then `main` fixes `parent`'s line 2; child's round as `child:main::parent` | line 2 is `main`'s fix, diff `c.txt`, `EQUAL` |
| `round 1 version fix` | A fix round editing `description:`, next to the `version:` line the branch's regenerate commit changed | exit `0`, `version: "0.1.1"` and the new description, `EQUAL` |
| `round 1 version build` | A first build editing `description:`, while the orchestrator branch holds another phase's `version:` raise | exit `0`, the new description, diff `a.txt`, `EQUAL` |
| `round 1 newer orchestrator` | Another phase changes `shared.txt` line 5 two lines from the phase's line 3, the phase merges the newer orchestrator branch, then a fix round | exit `0`, lines 3 to 5 are `line 3 phase`, `line 4`, `line 5`, diff `a.txt b.txt shared.txt`, `EQUAL` |
| `round 1 two squashed` | `pr3:main:depA,depB`, both squash-merged, then `pr3:main::depA,depB` | guarantees kept, the child's `a.txt` and `b.txt`, `EQUAL` |
| `round 1 stack moves` | A same-phase stack after `main` moves: parent's round, then child's as `child:parent` | both keep the guarantees, child's diff against parent is `c.txt`, one merge base, `EQUAL` |
| `round 1 spaces` | Child and a squash-merged parent both changed `docs dir/read me.md`, and `main` raised `my pkg/apm.yml`'s `version:` beside the child's `description:` edit | line 2 `line 2 child`, `my pkg/apm.yml` with `main`'s version and the child's description, `EQUAL` |
| `round 2 conflict, commit` | `main` changes the line 5 that `pr1` owns. A round stops; the phase merges `main` taking `main`'s side, then commits its resolution; a round with that commit | first: exit `1`, `STOP shared.txt changed on origin/main after the phase last took it, so the phase must merge it first`, `origin/pr1` unchanged. Then: guarantees kept, line 5 is the resolution, `EQUAL`. |
| `round 1 and 2 conflict, merge` | The same, but the phase resolves inside its merge of `main`, and the next round passes no commit | the same stop, then guarantees kept, line 5 is the resolution, `EQUAL` |
| `round 2 clean merge` | The phase merges `main` cleanly, then a round | `EQUAL` |
| `round 2 orchestrator merged, one line` | The orchestrator merges the phase, a fix changes the same line, the orchestrator merges again, then a round | up to date, line 5 fixed, `EQUAL` |
| `round 2 orchestrator merged, delete` | The phase deletes `README`, the orchestrator merges the phase | `EQUAL`, no `README` on `pr1` |
| `round 2 merge commit` | Parent `pr1` merged into `main` with a merge commit, then `pr2:main::pr1` | guarantees kept, diff `b.txt`, `EQUAL` |
| `round 2 row 3 to row 2` | `pr3:main:depA,depB`, `depA` squash-merged; `depB` lacks the new `main`. First `pr3:depB::depA`, then `pr3:main:depB:depA` | first: exit `1`, `STOP depB does not hold origin/main, so pr3 must target it with depB merged in`, `origin/pr3` unchanged. Then guarantees kept, both child lines, `EQUAL`. |
| `round 2 grandchild` | Stack `pr1`, `pr2`, `pr3`, where `pr2` rewrites `pr1`'s line. `pr1` squash-merged, the forge rewrites `pr2` only, then `pr2:main::pr1` and `pr3:pr2` | both exit `0`, `pr2` an ancestor of `pr3`, `pr3`'s diff against `pr2` is `three.txt`, line 2 `line 2 Y`, `EQUAL` |
| `round 2 delete package` | `main` holds package `old/` with its lockfile; the phase deletes `old/` | nothing under `old/` on `pr1`, `EQUAL` |
| `round 2 undeclared` | `pr2` cut from `pr1` of the same phase, given as `pr2:main` | `NOT EQUAL`, a `FAIL` line naming `a.txt` |
| `adjacent-line STOP` | Stack `pr1` (line 5) and `pr2` (line 6) of `shared.txt`; a fix to `pr1`'s line 5 | `pr1`'s round exits `1` with `STOP shared.txt conflicts outside generated content`, `STOP <sha> fix: pr1 does not apply` and `STOP the branch is back at <old head>`, `origin/pr1` unchanged |
| `uncarried, open` | A fix to `b.txt` that `pr2` does not carry | `FAIL b.txt: pr2 lacks phase commits <sha> fix: b;, so they need a pull request` |
| `uncarried, merged` | After `pr2` carries it and `pr1` is squash-merged, a fix to `a.txt` | `FAIL a.txt has not landed and is in no open pull request, so it needs a new pull request` |
| `uncarried, new pull request` | A new pull request `pr1b:main::pr1` carrying that fix | diff `a.txt`, `a fixed`, proof `pr2:main pr1b:main::pr1` `EQUAL` |
| `leak` | Another phase changes `shared.txt` line 9, the phase takes it through the orchestrator branch, then a fix on line 4 | line 9 is `line 9`, lines 3 and 4 the phase's, diff `a.txt shared.txt`, `EQUAL` |
| `identity` | Two phase commits with the same author, date and subject; `pr1` carries only the first | line 3 changed and line 9 not, `FAIL shared.txt: pr1 lacks phase commits <second> fix: review;, so they need a pull request`. Then `pr2:pr1` carries the second, `EQUAL`. |
| `assumption, fast-forward` | The phase fast-forwards to the orchestrator branch after the orchestrator merged it | `FAIL pr1: it changes a.txt, which the phase does not` |
| `assumption, orchestrator commit` | The orchestrator commits `orch-fix.txt` before the phase branches | `FAIL orch-fix.txt has not landed and is in no open pull request, so it needs a new pull request` |
| `missing branch` | Specs naming a merged dependency `gone` and an open dependency `gone2`, neither a branch | each exits `1` with `STOP <branch> is not a branch here`, `origin/pr1` unchanged |
| `wrong result, revert` | Phase commit `a` adds `debug.txt` and edits `README`; a later phase commit reverts both. `pr1` carries only `a` | `FAIL debug.txt: pr1 lacks phase commits <sha> fix: revert debug;, so they need a pull request`, the same for `README`, `NOT EQUAL`. After a fix round carrying the revert, `EQUAL` and no `debug.txt` on `pr1`. |
| `wrong result, origin/ names` | A same-phase stack `pr1:main`, `pr2:pr1` sharing `shared.txt` | the proof prints `EQUAL` with plain names, with `origin/` on the pull requests, and with `origin/` everywhere |
| `stop, shared path` | Stack `pr1` (line 5) and `pr2` (line 9) of `shared.txt`; `main` changes line 5. A round; the phase merges `main` and resolves line 5 in the merge; a round; the phase commits a further resolution; a round with that commit | each round exits `1` with exactly `STOP shared.txt conflicts outside generated content`, `STOP <sha> <subject> does not apply` and `STOP shared.txt is a shared path, so the stop is permanent: no merge or commit on the phase clears it, and it needs a decision`, the last followed by `STOP the branch is back at <old head>`. `pr1` and `origin/pr1` unchanged throughout. |
| `stop, owned path changed cleanly` | Another phase's pull request changes `shared.txt` line 10 and is squash-merged; `pr1` owns `shared.txt` (line 3). A round; then the phase merges `main` and a round | first: exit `1` with exactly `STOP shared.txt changed on origin/main after the phase last took it, so the phase must merge it first`, `pr1` and `origin/pr1` unchanged. Then: guarantees kept, lines 3 and 10 both present, `EQUAL`. |
| `stop, forge-rewritten row 3` | `ours:main:x2`, where another phase's `x2` is stacked on `x1` and has `x3` stacked on it. `x1` is squash-merged and the forge rewrites `x2`. Rounds as `ours:main:x2:x1`, then `x2` is squash-merged and a round as `ours:main::x2,x1` | the proof prints `FAIL ours: it changes x2.txt, which the phase does not` and `NOT EQUAL` after each round. The round in which it first fails leaves `origin/ours` where it started, as the handbook says. |
| `stop, delegate merge` | The phase merges a delegate branch adding `d.txt` with `git merge --no-ff`; `pr1:main` built from the session's commit and the delegate's | the proof prints `FAIL pr1: it changes d.txt, which the phase does not` and `NOT EQUAL`, and nothing was pushed to `origin/pr1` |
| `stop, file to directory` | `main` has a file `notes`; the phase replaces it with `notes/one.md`; `pr1:main` | the refresh prints `git checkout-index: notes is not in the cache`, the proof prints `FAIL pr1: it changes notesone.md, which the phase does not` and `NOT EQUAL`, and nothing was pushed to `origin/pr1` |
| `stop, directory to file` | The reverse: `main` has `notes/one.md`; the phase replaces the directory with a file `notes` | the outputs that the handbook documents for the same row: the refresh prints `git checkout-index: notes is not in the cache`, the proof a `FAIL pr1: it changes <path>, which the phase does not` line and `NOT EQUAL`, and nothing was pushed to `origin/pr1` |
| `chained rule` | `pr1` (line 2 and `a.txt`) and `pr2` (line 11 and `b.txt`) both change `shared.txt`; built as `pr1:main` and `pr2:main`, then `pr2`'s round as `pr2:pr1` | unchained: `FAIL shared.txt is in pr1 and pr2, which are not in one stack`, in either order, and `NOT EQUAL`. Chained: guarantees kept over the old `origin/pr2`, `pr2`'s diff against `pr1` is `b.txt shared.txt`, `EQUAL`. |
| `merged listed, parent` | Stack `parent` (line 2), `child` (`c.txt`); `parent` squash-merged, then `main` changes line 2; `child`'s round as `child:main::parent` | proof `child:main::parent` prints `FAIL shared.txt has not landed and is in no open pull request, so it needs a new pull request`; proof `parent:main child:main::parent` prints `EQUAL` |
| `merged listed, new pull request` | `pr1` squash-merged, then a fix to `a.txt`; a new pull request `pr1b:main::pr1` carrying the fix | its round exits `0` with `a fixed`, and proof `pr1:main pr1b:main::pr1` prints `EQUAL` |

```bash
/bin/bash <<'CHECK'
set -u
root=$(git rev-parse --show-toplevel)
md="$root/packages/s-stack/.apm/skills/sam-mode/references/pr-commands.md"
S=$(mktemp -d "${TMPDIR:-/tmp}/pr-handbook-check.XXXXXX")
trap 'cd /; rm -rf "$S"' EXIT
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
export GIT_AUTHOR_NAME=check GIT_AUTHOR_EMAIL=check@example.com GIT_COMMITTER_NAME=check GIT_COMMITTER_EMAIL=check@example.com
REGEN_SUBJECT='chore(s-stack): regenerate generated files' REGEN_RE='^chore(s-stack): regenerate generated files$'
awk '/^```bash$/ { b = 1; n++; next } /^```$/ { b = 0; next } b { print > (dir "/block" n ".sh") }' dir="$S" "$md"
script=$(grep -l -E '^ *refresh \| prove\)' "$S"/block*.sh | head -1)
[ -n "$script" ] && cp "$script" "$S/pr.sh" || { echo "FAIL no script block in $md"; exit 1; }
: > "$S/failed"
pass() { echo "PASS $1"; }
fail() { echo "FAIL $1"; echo x >> "$S/failed"; }

commit() { git add -A && git commit -q -m "$1"; }
line() { sed "$1s/.*/$2/" "$3" > "$S/l" && cat "$S/l" > "$3"; }
set_version() { sed "s/^version: .*/version: \"$1\"/" "$2" > "$S/y" && cat "$S/y" > "$2"; }
relock() { local p; for p in $(git ls-files -c -o --exclude-standard -- '*apm.yml'); do git ls-files -s -- "$(dirname "$p")" ':(exclude)*apm.lock.yaml' > "$(dirname "$p")/apm.lock.yaml"; git add -- "$(dirname "$p")/apm.lock.yaml"; done; }
regen() {
  local v; v=$(git show origin/main:pkg/apm.yml | sed -n 's/^version: "\(.*\)"$/\1/p')
  set_version "${v%.*}.$(( ${v##*.} + 1 ))" pkg/apm.yml && git add pkg/apm.yml && relock
  git diff --cached --quiet || git commit -q -m "$REGEN_SUBJECT"
}
init() {
  O="$S/$1.git" R="$S/$1"
  git init -q --bare -b main "$O" && git -C "$O" config receive.denyNonFastForwards true && git -C "$O" config receive.denyDeletes true
  git init -q -b main "$R" && cd "$R" && git remote add origin "$O" || exit 1
  mkdir pkg; printf 'name: pkg\nversion: "0.1.0"\ndescription: "A package."\nlicense: MIT\ndeps: []\n' > pkg/apm.yml
  for i in 1 2 3 4 5 6 7 8 9 10 11 12; do echo "line $i"; done > shared.txt
  echo readme > README; git add -A; relock; commit initial; git push -q -u origin main
}
in_wt() { local at=$1 wt="$S/wt.tmp" c; shift; git worktree add -q --detach "$wt" "$at" && (cd "$wt" && "$@"); c=$?; git worktree remove --force "$wt"; git fetch -q origin; return $c; }
main_commit() { local m=$1; shift; "$@" && relock && commit "$m" && git push -q origin HEAD:main; }
on_main() { git fetch -q origin; in_wt origin/main main_commit "$@"; }
other_commit() { local b=$1 m=$2; shift 2; "$@" && relock && commit "$m" && regen && git push -q origin "HEAD:refs/heads/$b"; }
other() { git fetch -q origin; in_wt origin/main other_commit "$@"; }
squash_in() { git merge -q --squash "origin/$1" >/dev/null 2>&1; relock; commit "feat: $1 (#1)" && git push -q origin HEAD:main; }
squash() { git fetch -q origin; in_wt origin/main squash_in "$1"; }
true_merge_in() { git merge -q --no-ff --no-edit "origin/$1" >/dev/null 2>&1 || { git checkout -q origin/main -- pkg; relock; git commit -q --no-edit; }; git push -q origin HEAD:main; }
true_merge() { git fetch -q origin; in_wt origin/main true_merge_in "$1"; }
forge_in() { git rebase -q --onto origin/main "$1" >/dev/null 2>&1 && git rev-parse HEAD > "$S/forged"; }
forge() {
  local old=$(git rev-parse "origin/$1") new
  in_wt "origin/$1" forge_in "$2" || return 1; new=$(cat "$S/forged")
  git push -q origin "$new:refs/forge/tmp" && git -C "$O" update-ref "refs/heads/$1" "$new" && git -C "$O" update-ref -d refs/forge/tmp && git fetch -q origin
  [ "$(git rev-parse "$old^{tree}")" = "$(git rev-parse "$new^{tree}")" ] && ! git merge-base --is-ancestor "$old" "$new"
}
orch() { git checkout -q -b orch origin/main && mkdir -p .foundry && echo plan > .foundry/plan.md && commit 'chore: plan'; }
take() { git merge -q --no-ff --no-edit "$1" >/dev/null 2>&1 || { relock; git commit -q --no-edit; }; }
phase() { git checkout -q -b phase orch; }
sha() { git rev-parse HEAD; }
push_if() { local b; b=$(git symbolic-ref --short HEAD); [ "$(git rev-parse -q --verify "refs/remotes/origin/$b")" = "$(git rev-parse HEAD)" ] || git push -q -u origin "$b"; }
start() {
  local b=$1 base=${2#*:}; base=${base%%:*}; wt="$S/wt.$b"; git fetch -q origin
  if git rev-parse -q --verify "refs/remotes/origin/$b" >/dev/null; then git worktree add -q --no-track -B "$b" "$wt" "origin/$b"
  else git worktree add -q --no-track -b "$b" "$wt" "origin/$base"; fi
}
round() {
  local b=$1 spec=$2; shift 2; start "$b" "$spec" || { out="worktree add failed"; code=1; return 1; }
  out=$(cd "$wt" && "$BASH" "$S/pr.sh" refresh phase origin/main "$spec" "$@" 2>&1 && regen 2>&1 && push_if 2>&1); code=$?
  git worktree remove --force "$wt"; git fetch -q origin; return $code
}
unpushed_round() {
  local b=$1 spec=$2; shift 2; start "$b" "$spec" || return 1
  out=$(cd "$wt" && "$BASH" "$S/pr.sh" refresh phase origin/main "$spec" "$@" 2>&1 && regen 2>&1); code=$?
  git worktree remove --force "$wt"; return $code
}
variant() { local b=$1 from=$2 wt="$S/wt.v" c; shift 2; git worktree add -q -b "$b" "$wt" "$from" && (cd "$wt" && "$@"); c=$?; git worktree remove --force "$wt"; return $c; }
prove() { out=$("$BASH" "$S/pr.sh" prove orch phase origin/main "$@" 2>&1); code=$?; }
equal() { prove "$@"; [ $code = 0 ] && [ "$(echo "$out" | tail -1)" = EQUAL ]; }
not_equal() { prove "$@"; [ $code = 1 ] && [ "$(echo "$out" | tail -1)" = 'NOT EQUAL' ]; }
has() { echo "$out" | grep -q -x -E -- "$1"; }
added() { echo "$(git rev-list --first-parent --merges --count "$1..$2") $(git rev-list --first-parent --count --grep="$REGEN_RE" "$1..$2") $(git rev-list --first-parent --count "$1..$2")"; }
hand() { git diff --name-only "$1...$2" -- . ':(exclude)*apm.lock.yaml' ':(exclude)*apm.yml' | tr '\n' ' '; }
at() { git show "$1:$2" | sed -n "$3p"; }
anc() { git merge-base --is-ancestor "$1" "$2"; }
guarded() {
  local old=$1 new=$2 a; a=$(added "$old" "$new")
  anc "$old" "$new" && anc origin/main "$new" && [ "${a%% *}" -le 1 ] && a=${a#* } && [ "${a%% *}" -le 1 ]
}
readme() { echo "readme $1" > README; }
put_line() { line "$1" "$2" "$3"; }
desc() { line 3 "description: \"$1\"" pkg/apm.yml; }
write() { printf '%s\n' "$2" > "$1"; }

c_split() {
  init split
  other other-pr 'feat: other phase' sh -c 'sed "2s/.*/line 2 parent/" shared.txt > t && mv t shared.txt && echo o > o.txt'
  orch; take origin/other-pr; phase
  echo a > a.txt; echo 'keywords: [a]' >> pkg/apm.yml; echo stale >> pkg/apm.lock.yaml; commit 'feat: a'; c1=$(sha)
  echo s1 > .foundry/status.md; commit 'chore: status'
  line 2 'line 2 child' shared.txt; echo b > b.txt; commit 'feat: b'; c2=$(sha)
  printf 'bin\000\001\377' > img.bin; commit 'feat: binary'; c3=$(sha)
  echo stale2 >> pkg/apm.lock.yaml; echo s2 > .foundry/status.md; commit 'chore: lockfile and status only'; c4=$(sha)
  round pr1 pr1:main "$c1"; o1="$code $out"; round pr2 pr2:other-pr "$c2" "$c3" "$c4"; o2="$code $out"
  [ "${o1%% *} ${o2%% *}" = '0 0' ] && [ "$(hand origin/main origin/pr1)" = 'a.txt ' ] && [ "$(hand origin/other-pr origin/pr2)" = 'b.txt img.bin shared.txt ' ] \
    && git diff --quiet phase origin/pr2 -- img.bin && anc origin/main origin/pr1 && anc origin/other-pr origin/pr2 \
    && [ "$(git log --format=%B origin/main..origin/pr1 | grep -c -x -F "(cherry picked from commit $c1)")" = 1 ] \
    && git show origin/pr1:pkg/apm.yml | grep -q -x 'keywords: \[a\]' \
    && pass "done-when build: pr1 on main and pr2 stacked on another phase's pull request, own paths only, trailer, binary intact" || fail "done-when build: pr1 $o1; pr2 $o2"
  equal pr1:main pr2:other-pr && pass "done-when correct split with regenerate commits: EQUAL" || fail "done-when correct split: $out"
  not_equal pr1:main && has 'FAIL b.txt has not landed and is in no open pull request, so it needs a new pull request' && pass "done-when split that drops a change: NOT EQUAL" || fail "done-when dropped change: $out"
  variant pr1x origin/pr1 sh -c 'echo extra > extra.txt && git add -A && git commit -q -m extra'
  not_equal pr1x:main pr2:other-pr && has 'FAIL pr1x: it changes extra.txt, which the phase does not' && pass "done-when split that adds a change: NOT EQUAL" || fail "done-when added change: $out"
  variant pr1f origin/pr1 sh -c 'mkdir -p .foundry && echo leak > .foundry/leak.md && git add -A && git commit -q -m leak'
  not_equal pr1f:main pr2:other-pr && has 'FAIL pr1f: contains .foundry/leak.md' && pass "done-when branch with a file under .foundry: NOT EQUAL" || fail "done-when .foundry: $out"
  variant pr1r origin/pr1 sh -c "echo more >> a.txt && git commit -q -am '$REGEN_SUBJECT'"
  not_equal pr1r:main pr2:other-pr && has 'FAIL pr1r: regenerate commit [0-9a-f]+ changes a.txt' && pass "done-when regenerate commit that changes a hand-written file: NOT EQUAL" || fail "done-when regenerate a.txt: $out"
  variant pr1y origin/pr1 sh -c "sed 's/^deps: .*/deps: [x]/' pkg/apm.yml > t && mv t pkg/apm.yml && git commit -q -am '$REGEN_SUBJECT'"
  not_equal pr1y:main pr2:other-pr && has 'FAIL pr1y: regenerate commit [0-9a-f]+ changes -deps: \[\]' && has '\+deps: \[x\]' && pass "done-when regenerate commit that changes an apm.yml line other than version: NOT EQUAL" || fail "done-when regenerate deps: $out"
  squash other-pr; h=$(git rev-parse origin/pr2)
  round pr2 pr2:main::other-pr; o="$code $out"
  [ "${o%% *}" = 0 ] && guarded "$h" origin/pr2 && [ "$(added "$h" origin/pr2)" = '1 1 2' ] && [ "$(hand origin/main origin/pr2)" = 'b.txt img.bin shared.txt ' ] \
    && [ "$(at origin/pr2 shared.txt 2)" = 'line 2 child' ] && equal pr1:main pr2:main::other-pr \
    && pass "done-when squash-merged parent: the child's round and regenerate commit, parent excluded through its kept ref, EQUAL" || fail "done-when squash-merged parent: $o; adds $(added "$h" origin/pr2); diff $(hand origin/main origin/pr2); proof $out"
}

c_rounds() {
  init rounds; orch; phase
  echo a > a.txt; commit 'feat: a'; c1=$(sha)
  round pr1 pr1:main "$c1" || fail "rounds build: $out"
  h=$(git rev-parse origin/pr1); round pr1 pr1:main; o="$code $out"
  [ "${o%% *}" = 0 ] && echo "$out" | grep -q '^up to date with' && [ "$(git rev-parse origin/pr1)" = "$h" ] && pass "guarantee: a round on an up-to-date branch changes nothing" || fail "up-to-date round: $o"
  on_main 'docs: main moves' readme 2; h=$(git rev-parse origin/pr1); round pr1 pr1:main; o="$code $out"
  [ "${o%% *}" = 0 ] && guarded "$h" origin/pr1 && [ "$(added "$h" origin/pr1)" = '1 1 2' ] && equal pr1:main \
    && pass "guarantee: main moves, one merge and one regenerate commit, a fast-forward push, main an ancestor, EQUAL" || fail "round after a move: $o; adds $(added "$h" origin/pr1); proof $out"
  on_main 'feat: another pull request raises the version' sh -c 'echo "readme 3" > README && sed "s/^version: .*/version: \"0.1.1\"/" pkg/apm.yml > t && mv t pkg/apm.yml'
  h=$(git rev-parse origin/pr1); round pr1 pr1:main; o="$code $out"
  [ "${o%% *}" = 0 ] && guarded "$h" origin/pr1 && [ "$(at origin/pr1 pkg/apm.yml 2)" = 'version: "0.1.2"' ] && equal pr1:main \
    && pass "guarantee: main takes the branch's own version, the round raises it again" || fail "version taken: $o; proof $out"
  on_main 'docs: main moves again' readme 4; h=$(git rev-parse origin/pr1)
  unpushed_round pr1 pr1:main; o="$code $out"
  [ "${o%% *}" = 0 ] && [ "$(git rev-parse origin/pr1)" = "$h" ] && [ "$(git rev-parse pr1)" != "$h" ] || fail "interrupted round did not leave an unpushed head: $o"
  round pr1 pr1:main; o="$code $out"
  [ "${o%% *}" = 0 ] && guarded "$h" origin/pr1 && [ "$(added "$h" origin/pr1)" = '1 1 2' ] && equal pr1:main \
    && pass "guarantee: an interrupted round finishes on the next one, from origin/pr1" || fail "after an interrupted round: $o; adds $(added "$h" origin/pr1); proof $out"
  h=$(git rev-parse origin/pr1); round pr1 pr1:main; round pr1 pr1:main; o="$code $out"
  [ "${o%% *}" = 0 ] && [ "$(git rev-parse origin/pr1)" = "$h" ] && pass "guarantee: repeated rounds after that change nothing" || fail "repeated rounds: $o"
  echo 'a fixed' > a.txt; commit 'fix: a'; f1=$(sha); round pr1 pr1:main "$f1" || fail "fix round: $out"
  h=$(git rev-parse origin/pr1); round pr1 pr1:main "$f1"; o="$code $out"
  [ "${o%% *}" = 0 ] && [ "$(git rev-parse origin/pr1)" = "$h" ] && [ "$(git show origin/pr1:a.txt)" = 'a fixed' ] && pass "guarantee: a fix round rerun after its push, with the same commit, changes nothing" || fail "rerun fix round: $o; adds $(added "$h" origin/pr1)"
  on_main 'docs: main moves for a hand edit' readme 5
  variant pr1h origin/pr1 sh -c 'git merge -q --no-ff --no-commit origin/main >/dev/null 2>&1; git checkout -q origin/main -- pkg; echo "by hand" >> a.txt; git add -A; git commit -q --no-edit'
  not_equal pr1h:main && has 'FAIL pr1h: its head differs from its target tree' && echo "$out" | grep -q 'a.txt' && pass "a hand edit inside a merge commit: NOT EQUAL" || fail "hand edit in a merge: $out"
}

c_rewrite() {
  init rewrite; orch; phase
  echo p > p.txt; commit 'feat: parent'; c1=$(sha)
  echo c > c.txt; commit 'feat: child'; c2=$(sha)
  round parent parent:main "$c1" && round child child:parent "$c2" || fail "rewrite build: $out"
  squash parent
  if forge child origin/parent; then
    rw=$(git rev-parse origin/child); on_main 'docs: main moves' readme 2
    round child child:main::parent; o="$code $out"
    [ "${o%% *}" = 0 ] && guarded "$rw" origin/child && [ "$(hand origin/main origin/child)" = 'c.txt ' ] && equal child:main::parent \
      && pass "forge rewrite: the rewritten head is the start, commits only on top, EQUAL" || fail "forge rewrite: $o; adds $(added "$rw" origin/child); proof $out"
  else fail "forge rewrite: the simulated rebase changed the tree"; fi
}

c_r1_squash_fix() {
  init r1-squash-fix
  other parent 'feat: parent' put_line 2 'line 2 parent' shared.txt
  orch; take origin/parent; phase
  echo c > c.txt; commit 'feat: child'; c1=$(sha)
  round child child:parent "$c1" || fail "r1-squash-fix build: $out"
  squash parent; on_main 'fix: another pull request fixes line 2' put_line 2 'line 2 fixed' shared.txt
  round child child:main::parent; o="$code $out"
  [ "${o%% *}" = 0 ] && [ "$(at origin/child shared.txt 2)" = 'line 2 fixed' ] && [ "$(hand origin/main origin/child)" = 'c.txt ' ] && equal child:main::parent \
    && pass "round 1, squash step: a later fix on main to a squash-merged parent's line stays, EQUAL" || fail "r1-squash-fix: $o; line 2 '$(at origin/child shared.txt 2)'; diff $(hand origin/main origin/child); proof $out"
}

c_r1_version_fix() {
  init r1-version-fix; orch; phase
  echo a > a.txt; commit 'feat: a'; c1=$(sha)
  round pr1 pr1:main "$c1" || fail "r1-version-fix build: $out"
  desc 'Better.'; commit 'fix: describe'; f1=$(sha)
  round pr1 pr1:main "$f1"; o="$code $out"
  [ "${o%% *}" = 0 ] && [ "$(at origin/pr1 pkg/apm.yml 2,3 | tr '\n' '|')" = 'version: "0.1.1"|description: "Better."|' ] && equal pr1:main \
    && pass "round 1, version context: a fix next to a version: line the regenerate commit changed is carried" || fail "r1-version-fix: $o; proof $out"
}

c_r1_version_build() {
  init r1-version-build
  other other-pr 'feat: other phase' sh -c 'echo o > o.txt'
  orch; take origin/other-pr; phase
  echo a > a.txt; desc 'Better.'; commit 'feat: a'; c1=$(sha)
  round pr1 pr1:main "$c1"; o="$code $out"
  [ "${o%% *}" = 0 ] && [ "$(at origin/pr1 pkg/apm.yml 3)" = 'description: "Better."' ] && [ "$(hand origin/main origin/pr1)" = 'a.txt ' ] && equal pr1:main \
    && pass "round 1, version context: a first build next to another phase's version: raise" || fail "r1-version-build: $o; proof $out"
}

c_r1_orch_merged() {
  init r1-orch-merged; orch; phase
  line 3 'line 3 phase' shared.txt; echo a > a.txt; commit 'feat: a'; c1=$(sha)
  round pr1 pr1:main "$c1" || fail "r1-orch-merged build: $out"
  git checkout -q -b other-phase orch; line 5 'line 5 other phase' shared.txt; commit 'feat: other phase'
  git checkout -q orch; take other-phase; git checkout -q phase; take orch
  echo b > b.txt; commit 'feat: b'; c2=$(sha)
  round pr1 pr1:main "$c2"; o="$code $out"
  [ "${o%% *}" = 0 ] && [ "$(at origin/pr1 shared.txt 3,5 | tr '\n' '|')" = 'line 3 phase|line 4|line 5|' ] && [ "$(hand origin/main origin/pr1)" = 'a.txt b.txt shared.txt ' ] && equal pr1:main \
    && pass "round 1, newer orchestrator branch: the fix round leaves the other phase's line out, EQUAL" || fail "r1-orch-merged: $o; lines $(at origin/pr1 shared.txt 3,5 | tr '\n' '|'); proof $out"
}

c_r1_two_squashed() {
  init r1-two-squashed
  on_main 'feat: base files' sh -c 'echo "a 1" > a.txt && echo "b 1" > b.txt'
  other depA 'feat: depA' write a.txt 'a 1 depA'; other depB 'feat: depB' write b.txt 'b 1 depB'
  orch; take origin/depA; take origin/depB; phase
  echo 'a 1 depA child' > a.txt; echo 'b 1 depB child' > b.txt; commit 'feat: child'; c1=$(sha)
  round pr3 pr3:main:depA,depB "$c1" || fail "r1-two-squashed build: $out"
  squash depA; squash depB; h=$(git rev-parse origin/pr3)
  round pr3 pr3:main::depA,depB; o="$code $out"
  [ "${o%% *}" = 0 ] && guarded "$h" origin/pr3 && [ "$(git show origin/pr3:a.txt) $(git show origin/pr3:b.txt)" = 'a 1 depA child b 1 depB child' ] && [ "$(hand origin/main origin/pr3)" = 'a.txt b.txt ' ] && equal pr3:main::depA,depB \
    && pass "round 1, two squash-merged dependencies in one round: EQUAL" || fail "r1-two-squashed: $o; proof $out"
}

c_r1_stack_moves() {
  init r1-stack-moves; orch; phase
  echo p > p.txt; commit 'feat: parent'; c1=$(sha)
  echo c > c.txt; commit 'feat: child'; c2=$(sha)
  round parent parent:main "$c1" && round child child:parent "$c2" || fail "r1-stack-moves build: $out"
  on_main 'feat: an unrelated pull request' sh -c 'echo m > m.txt'
  hp=$(git rev-parse origin/parent) hc=$(git rev-parse origin/child)
  round parent parent:main; o1="$code $out"; round child child:parent; o2="$code $out"
  [ "${o1%% *} ${o2%% *}" = '0 0' ] && guarded "$hp" origin/parent && guarded "$hc" origin/child && [ "$(hand origin/parent origin/child)" = 'c.txt ' ] \
    && [ "$(git merge-base --all origin/parent origin/child | wc -l | tr -d ' ')" = 1 ] && anc origin/parent origin/child && equal parent:main child:parent \
    && pass "round 1, a stack after main moves: the child takes its parent, its diff is its own change" || fail "r1-stack-moves: parent $o1; child $o2; diff $(hand origin/parent origin/child); proof $out"
}

c_r1_spaces() {
  init r1-spaces
  on_main 'feat: spaced paths' sh -c 'mkdir -p "docs dir" "my pkg" && for i in 1 2 3 4 5 6; do echo "line $i"; done > "docs dir/read me.md" && printf "name: my\nversion: \"0.1.0\"\ndescription: \"Mine.\"\n" > "my pkg/apm.yml"'
  other parent 'feat: parent' put_line 2 'line 2 parent' 'docs dir/read me.md'
  orch; take origin/parent; phase
  line 2 'line 2 child' 'docs dir/read me.md'; line 3 'description: "Spaced."' 'my pkg/apm.yml'; commit 'feat: child'; c1=$(sha)
  round child child:parent "$c1" || fail "r1-spaces build: $out"
  squash parent; on_main 'feat: raise my pkg' set_version 0.2.0 'my pkg/apm.yml'
  round child child:main::parent; o="$code $out"
  [ "${o%% *}" = 0 ] && [ "$(at origin/child 'docs dir/read me.md' 2)" = 'line 2 child' ] && [ "$(at origin/child 'my pkg/apm.yml' 2,3 | tr '\n' '|')" = 'version: "0.2.0"|description: "Spaced."|' ] && equal child:main::parent \
    && pass "round 1, paths with spaces" || fail "r1-spaces: $o; proof $out"
}

conflict_setup() {
  init "$1"; orch; phase
  line 5 'line 5 phase' shared.txt; echo a > a.txt; commit 'feat: a'; c1=$(sha)
  round pr1 pr1:main "$c1" || fail "$1 build: $out"
  on_main 'feat: another pull request edits line 5' sh -c 'sed "5s/.*/line 5 main/" shared.txt > t && mv t shared.txt && echo m > m.txt'
  h=$(git rev-parse origin/pr1); round pr1 pr1:main; o="$code $out"
  [ "${o%% *}" = 1 ] && has 'STOP shared.txt changed on origin/main after the phase last took it, so the phase must merge it first' && [ "$(git rev-parse origin/pr1)" = "$h" ] \
    && pass "$1: a stale owned path stops the round and leaves the branch" || fail "$1 stale stop: $o"
  git checkout -q phase; git merge -q --no-ff --no-commit origin/main >/dev/null 2>&1
}
c_r2_conflict_commit() {
  conflict_setup r2-conflict-commit
  git checkout -q origin/main -- shared.txt pkg; relock; git commit -q --no-edit
  line 5 'line 5 phase and main' shared.txt; commit 'fix: resolve line 5'; f1=$(sha)
  round pr1 pr1:main "$f1"; o="$code $out"
  [ "${o%% *}" = 0 ] && guarded "$h" origin/pr1 && [ "$(at origin/pr1 shared.txt 5)" = 'line 5 phase and main' ] && equal pr1:main \
    && pass "round 2, old conflicting commit: an ordinary resolution commit on the phase carries, EQUAL" || fail "r2-conflict-commit: $o; line 5 '$(at origin/pr1 shared.txt 5)'; proof $out"
}
c_r2_conflict_merge() {
  conflict_setup r2-conflict-merge
  line 5 'line 5 phase and main' shared.txt; git checkout -q origin/main -- pkg; relock; git add -A; git commit -q --no-edit
  round pr1 pr1:main; o="$code $out"
  [ "${o%% *}" = 0 ] && guarded "$h" origin/pr1 && [ "$(at origin/pr1 shared.txt 5)" = 'line 5 phase and main' ] && equal pr1:main \
    && pass "round 1 and 2, resolution inside the phase's merge: the next round takes it, EQUAL" || fail "r2-conflict-merge: $o; line 5 '$(at origin/pr1 shared.txt 5)'; proof $out"
}

c_r2_clean_merge() {
  init r2-clean-merge; orch; phase
  echo a > a.txt; commit 'feat: a'; c1=$(sha)
  round pr1 pr1:main "$c1" || fail "r2-clean-merge build: $out"
  on_main 'feat: another pull request lands' write m.txt m
  git checkout -q phase; take origin/main
  round pr1 pr1:main; o="$code $out"
  [ "${o%% *}" = 0 ] && equal pr1:main && pass "round 2, clean merge of main into the phase: EQUAL" || fail "r2-clean-merge: $o; proof $out"
}

c_r2_orch_line() {
  init r2-orch-line; orch; phase
  line 5 'line 5 first' shared.txt; commit 'feat: a'; c1=$(sha)
  round pr1 pr1:main "$c1" || fail "r2-orch-line build: $out"
  git checkout -q orch; take phase; git checkout -q phase
  line 5 'line 5 fixed' shared.txt; commit 'fix: line 5'; f1=$(sha)
  round pr1 pr1:main "$f1" || fail "r2-orch-line fix round: $out"
  git checkout -q orch; take phase; git checkout -q phase
  h=$(git rev-parse origin/pr1); round pr1 pr1:main; o="$code $out"
  [ "${o%% *}" = 0 ] && [ "$(git rev-parse origin/pr1)" = "$h" ] && [ "$(at origin/pr1 shared.txt 5)" = 'line 5 fixed' ] && equal pr1:main \
    && pass "round 2, orchestrator merged the phase and two own commits share a line: EQUAL" || fail "r2-orch-line: $o; proof $out"
}

c_r2_orch_delete() {
  init r2-orch-delete; orch; phase
  git rm -q README; echo a > a.txt; commit 'feat: drop README'; c1=$(sha)
  round pr1 pr1:main "$c1" || fail "r2-orch-delete build: $out"
  git checkout -q orch; take phase; git checkout -q phase
  equal pr1:main && ! git cat-file -e origin/pr1:README 2>/dev/null && pass "round 2, orchestrator merged a phase that deletes a file: EQUAL" || fail "r2-orch-delete: $out"
}

c_r2_merge_commit() {
  init r2-merge-commit; orch; phase
  echo a > a.txt; commit 'feat: a'; c1=$(sha)
  echo b > b.txt; commit 'feat: b'; c2=$(sha)
  round pr1 pr1:main "$c1" && round pr2 pr2:pr1 "$c2" || fail "r2-merge-commit build: $out"
  true_merge pr1; h=$(git rev-parse origin/pr2)
  round pr2 pr2:main::pr1; o="$code $out"
  [ "${o%% *}" = 0 ] && guarded "$h" origin/pr2 && [ "$(hand origin/main origin/pr2)" = 'b.txt ' ] && equal pr2:main::pr1 \
    && pass "round 2, a parent merged with a merge commit: the child's round and the proof, EQUAL" || fail "r2-merge-commit: $o; proof $out"
}

c_r2_row3_to_row2() {
  init r2-row3-to-row2
  on_main 'feat: base files' sh -c 'echo "a 1" > a.txt && echo "b 1" > b.txt'
  other depA 'feat: depA' write a.txt 'a 1 depA'; other depB 'feat: depB' write b.txt 'b 1 depB'
  orch; take origin/depA; take origin/depB; phase
  echo 'a 1 depA child' > a.txt; echo 'b 1 depB child' > b.txt; commit 'feat: child'; c1=$(sha)
  round pr3 pr3:main:depA,depB "$c1" || fail "r2-row3-to-row2 build: $out"
  squash depA; h=$(git rev-parse origin/pr3)
  round pr3 pr3:depB::depA; o="$code $out"
  [ "${o%% *}" = 1 ] && has 'STOP depB does not hold origin/main, so pr3 must target it with depB merged in' && [ "$(git rev-parse origin/pr3)" = "$h" ] \
    && pass "round 2, row 3 to row 2 under a parent without main: STOP, branch unchanged" || fail "r2-row3-to-row2 stop: $o"
  round pr3 pr3:main:depB:depA; o="$code $out"
  [ "${o%% *}" = 0 ] && guarded "$h" origin/pr3 && [ "$(git show origin/pr3:a.txt) $(git show origin/pr3:b.txt)" = 'a 1 depA child b 1 depB child' ] && equal pr3:main:depB:depA \
    && pass "round 2, staying in row 3 with depB merged in: merged dependency kept, EQUAL" || fail "r2-row3-to-row2 row 3: $o; proof $out"
}

c_r2_grandchild() {
  init r2-grandchild; orch; phase
  line 2 'line 2 X' shared.txt; commit 'feat: one'; c1=$(sha)
  line 2 'line 2 Y' shared.txt; echo two > two.txt; commit 'feat: two'; c2=$(sha)
  echo three > three.txt; commit 'feat: three'; c3=$(sha)
  round pr1 pr1:main "$c1" && round pr2 pr2:pr1 "$c2" && round pr3 pr3:pr2 "$c3" || fail "r2-grandchild build: $out"
  squash pr1; forge pr2 origin/pr1 || fail "r2-grandchild: the simulated rewrite changed the tree"
  round pr2 pr2:main::pr1; o1="$code $out"; round pr3 pr3:pr2; o2="$code $out"
  [ "${o1%% *} ${o2%% *}" = '0 0' ] && anc origin/pr2 origin/pr3 && [ "$(hand origin/pr2 origin/pr3)" = 'three.txt ' ] && [ "$(at origin/pr3 shared.txt 2)" = 'line 2 Y' ] && equal pr2:main::pr1 pr3:pr2 \
    && pass "round 2, a grandchild whose parent the forge rewrote, spec without the merged grandparent" || fail "r2-grandchild: pr2 $o1; pr3 $o2; diff $(hand origin/pr2 origin/pr3); proof $out"
}

c_r2_delete_package() {
  init r2-delete-package
  on_main 'feat: a second package' sh -c 'mkdir old && printf "name: old\nversion: \"0.1.0\"\n" > old/apm.yml && echo skill > old/skill.md'
  orch; phase
  git rm -rq old; commit 'feat: remove the old package'; c1=$(sha)
  round pr1 pr1:main "$c1"; o="$code $out"
  [ "${o%% *}" = 0 ] && git cat-file -e origin/main:old/apm.lock.yaml && [ -z "$(git ls-tree -r --name-only origin/pr1 -- old)" ] && equal pr1:main \
    && pass "round 2, a phase that deletes a package: the lockfile goes too, EQUAL" || fail "r2-delete-package: $o; left $(git ls-tree -r --name-only origin/pr1 -- old | tr '\n' ' '); proof $out"
}

c_r2_undeclared() {
  init r2-undeclared; orch; phase
  echo a > a.txt; commit 'feat: a'; c1=$(sha)
  echo b > b.txt; commit 'feat: b'; c2=$(sha)
  round pr1 pr1:main "$c1" || fail "r2-undeclared build: $out"
  git fetch -q origin; git worktree add -q --no-track -b pr2 "$S/wt.u" origin/pr1
  (cd "$S/wt.u" && "$BASH" "$S/pr.sh" refresh phase origin/main pr2:main "$c2" >/dev/null 2>&1 && regen && push_if); git worktree remove --force "$S/wt.u"; git fetch -q origin
  not_equal pr1:main pr2:main && echo "$out" | grep -q '^FAIL.*a\.txt' && pass "round 2, a same-phase branch with an undeclared dependency: NOT EQUAL" || fail "r2-undeclared: $out"
}

c_r2_adjacent() {
  init r2-adjacent; orch; phase
  line 5 'line 5 pr1' shared.txt; commit 'feat: pr1'; c1=$(sha)
  line 6 'line 6 pr2' shared.txt; commit 'feat: pr2'; c2=$(sha)
  round pr1 pr1:main "$c1" && round pr2 pr2:pr1 "$c2" || fail "r2-adjacent build: $out"
  equal pr1:main pr2:pr1 || fail "r2-adjacent proof before the fix: $out"
  line 5 'line 5 pr1 fixed' shared.txt; commit 'fix: pr1'; f1=$(sha)
  h=$(git rev-parse origin/pr1); round pr1 pr1:main "$f1"; o="$code $out"
  [ "${o%% *}" = 1 ] && has 'STOP shared.txt conflicts outside generated content' && has 'STOP [0-9a-f]+ fix: pr1 does not apply' && has "STOP the branch is back at $h" && [ "$(git rev-parse origin/pr1)" = "$h" ] \
    && pass "adjacent-line edits split across a stack: STOP, branch unchanged" || fail "r2-adjacent: $o"
}

c_uncarried() {
  init uncarried; orch; phase
  echo a > a.txt; commit 'feat: a'; c1=$(sha)
  echo b > b.txt; commit 'feat: b'; c2=$(sha)
  round pr1 pr1:main "$c1" && round pr2 pr2:main "$c2" || fail "uncarried build: $out"
  echo 'b fixed' > b.txt; commit 'fix: b'; f1=$(sha)
  not_equal pr1:main pr2:main && has "FAIL b.txt: pr2 lacks phase commits $(git rev-parse --short "$f1") fix: b;, so they need a pull request" \
    && pass "a phase commit an open pull request does not carry: NOT EQUAL, named" || fail "uncarried open: $out"
  round pr2 pr2:main "$f1" || fail "uncarried fix round: $out"
  squash pr1; echo 'a fixed' > a.txt; commit 'fix: a after its pull request merged'; f2=$(sha)
  not_equal pr2:main && has 'FAIL a.txt has not landed and is in no open pull request, so it needs a new pull request' \
    && pass "a fix after its pull request merged: NOT EQUAL, needs a new pull request" || fail "uncarried merged: $out"
  round pr1b pr1b:main::pr1 "$f2"; o="$code $out"
  [ "${o%% *}" = 0 ] && [ "$(hand origin/main origin/pr1b)" = 'a.txt ' ] && [ "$(git show origin/pr1b:a.txt)" = 'a fixed' ] && equal pr2:main pr1b:main::pr1 && pass "the new pull request for it: EQUAL" || fail "uncarried new pull request: $o; proof $out"
}

c_leak() {
  init leak; orch; phase
  line 3 'line 3 phase' shared.txt; echo a > a.txt; commit 'feat: a'; c1=$(sha)
  round pr1 pr1:main "$c1" || fail "leak build: $out"
  git checkout -q -b other-phase orch; line 9 'line 9 other phase' shared.txt; echo o > o.txt; commit 'feat: other phase'
  git checkout -q orch; take other-phase; git checkout -q phase; take orch
  line 4 'line 4 phase' shared.txt; commit 'fix: line 4'; f1=$(sha)
  round pr1 pr1:main "$f1"; o="$code $out"
  [ "${o%% *}" = 0 ] && [ "$(at origin/pr1 shared.txt 9)" = 'line 9' ] && [ "$(at origin/pr1 shared.txt 3,4 | tr '\n' '|')" = 'line 3 phase|line 4 phase|' ] && [ "$(hand origin/main origin/pr1)" = 'a.txt shared.txt ' ] && equal pr1:main \
    && pass "leak: another phase's line in a shared file stays out of the pull request" || fail "leak: $o; line 9 '$(at origin/pr1 shared.txt 9)'; diff $(hand origin/main origin/pr1); proof $out"
}

c_identity() {
  init identity; orch; phase
  export GIT_AUTHOR_DATE='1795000000 +0000'
  line 3 'line 3 first' shared.txt; commit 'fix: review'; c1=$(sha)
  line 9 'line 9 second' shared.txt; commit 'fix: review'; c2=$(sha)
  unset GIT_AUTHOR_DATE
  round pr1 pr1:main "$c1"; o="$code $out"
  [ "${o%% *}" = 0 ] && [ "$(at origin/pr1 shared.txt 3) $(at origin/pr1 shared.txt 9)" = 'line 3 first line 9' ] && not_equal pr1:main && has "FAIL shared.txt: pr1 lacks phase commits $(git rev-parse --short "$c2") fix: review;, so they need a pull request" \
    && pass "identity: twin commits with one author, date and subject stay distinct" || fail "identity: $o; proof $out"
  round pr2 pr2:pr1 "$c2"; o="$code $out"
  [ "${o%% *}" = 0 ] && [ "$(at origin/pr2 shared.txt 9)" = 'line 9 second' ] && equal pr1:main pr2:pr1 && pass "identity: the twin carried by its own pull request: EQUAL" || fail "identity second: $o; proof $out"
}

c_assumptions() {
  init ff; orch; phase
  echo a > a.txt; commit 'feat: a'; c1=$(sha)
  round pr1 pr1:main "$c1" || fail "ff build: $out"
  git checkout -q orch; take phase; git checkout -q phase; git merge -q --ff-only orch
  not_equal pr1:main && has 'FAIL pr1: it changes a.txt, which the phase does not' && pass "assumption: a fast-forward of the orchestrator branch is reported" || fail "ff: $out"
  cd "$S"; init orch-commit; orch; echo fix > orch-fix.txt; commit 'chore: orchestrator edits a file'; phase
  echo a > a.txt; commit 'feat: a'; c1=$(sha)
  round pr1 pr1:main "$c1" || fail "orch-commit build: $out"
  not_equal pr1:main && has 'FAIL orch-fix.txt has not landed and is in no open pull request, so it needs a new pull request' && pass "assumption: an orchestrator commit outside .foundry is reported" || fail "orch-commit: $out"
}

c_missing() {
  init missing; orch; phase
  echo a > a.txt; commit 'feat: a'; c1=$(sha)
  round pr1 pr1:main "$c1" || fail "missing build: $out"
  h=$(git rev-parse origin/pr1); round pr1 pr1:main::gone; o1="$code $out"; round pr1 pr1:main:gone2; o2="$code $out"
  [ "${o1%% *} ${o2%% *}" = '1 1' ] && echo "$o1" | grep -q -x -F '1 STOP gone is not a branch here' && echo "$o2" | grep -q -x -F '1 STOP gone2 is not a branch here' && [ "$(git rev-parse origin/pr1)" = "$h" ] \
    && pass "a spec naming a missing branch: STOP, branch unchanged" || fail "missing branch: $o1; $o2"
}

unchanged() { [ "$(git rev-parse "origin/$1")" = "$2" ] && [ "$(git rev-parse "$1")" = "$2" ]; }
unpushed() { ! git rev-parse -q --verify "refs/remotes/origin/$1" >/dev/null; }
SHARED_STOP='STOP shared.txt is a shared path, so the stop is permanent: no merge or commit on the phase clears it, and it needs a decision'
other_on() { local at=$1; shift; git fetch -q origin; in_wt "$at" other_commit "$@"; }

c_revert() {
  init revert; orch; phase
  echo a > a.txt; echo debug > debug.txt; readme phase; commit 'feat: a'; c1=$(sha)
  rm debug.txt; echo readme > README; commit 'fix: revert debug'; f1=$(sha)
  round pr1 pr1:main "$c1" || fail "revert build: $out"
  f=$(git rev-parse --short "$f1")
  not_equal pr1:main && has "FAIL debug.txt: pr1 lacks phase commits $f fix: revert debug;, so they need a pull request" && has "FAIL README: pr1 lacks phase commits $f fix: revert debug;, so they need a pull request" \
    && pass "wrong result, revert: a pull request that still holds a change the phase reverted is NOT EQUAL" || fail "wrong result, revert: $out"
  round pr1 pr1:main "$f1"; o="$code $out"
  [ "${o%% *}" = 0 ] && ! git cat-file -e origin/pr1:debug.txt 2>/dev/null && [ "$(git show origin/pr1:README)" = readme ] && equal pr1:main \
    && pass "wrong result, revert: carrying the revert gives EQUAL" || fail "wrong result, revert carried: $o; proof $out"
}

c_origin_names() {
  init origin-names; orch; phase
  line 2 'line 2 pr1' shared.txt; commit 'feat: pr1'; c1=$(sha)
  line 11 'line 11 pr2' shared.txt; commit 'feat: pr2'; c2=$(sha)
  round pr1 pr1:main "$c1" && round pr2 pr2:pr1 "$c2" || fail "origin-names build: $out"
  equal pr1:main pr2:pr1 && equal origin/pr1:main origin/pr2:pr1 && equal origin/pr1:origin/main origin/pr2:origin/pr1 \
    && pass "wrong result, origin/ names: origin/<pr> proves the same as <pr>" || fail "wrong result, origin/ names: $out"
}

c_stop_shared() {
  init stop-shared; orch; phase
  line 5 'line 5 pr1' shared.txt; commit 'feat: pr1'; c1=$(sha)
  line 9 'line 9 pr2' shared.txt; commit 'feat: pr2'; c2=$(sha)
  round pr1 pr1:main "$c1" && round pr2 pr2:pr1 "$c2" || fail "stop-shared build: $out"
  on_main 'feat: another pull request edits line 5' put_line 5 'line 5 main' shared.txt
  h=$(git rev-parse origin/pr1) want=$(printf '%s\n' 'STOP shared.txt conflicts outside generated content' "STOP $(git rev-parse --short "$c1") feat: pr1 does not apply" "$SHARED_STOP")
  round pr1 pr1:main; o1="$code $out"
  [ "$o1" = "1 $want" ] && unchanged pr1 "$h" || { fail "stop, shared path, after main moved: $o1"; return; }
  git checkout -q phase; git merge -q --no-ff --no-commit origin/main >/dev/null 2>&1
  { for i in 1 2 3 4; do echo "line $i"; done; echo 'line 5 pr1 and main'; for i in 6 7 8; do echo "line $i"; done; echo 'line 9 pr2'; for i in 10 11 12; do echo "line $i"; done; } > shared.txt
  git checkout -q origin/main -- pkg; relock; git add -A; git commit -q --no-edit
  round pr1 pr1:main; o2="$code $out"
  [ "$o2" = "1 $want" ] && unchanged pr1 "$h" || { fail "stop, shared path, after the phase merged main: $o2"; return; }
  line 5 'line 5 resolved' shared.txt; commit 'fix: resolve line 5'; f1=$(sha)
  round pr1 pr1:main "$f1"; o3="$code $out"
  [ "$o3" = "1 $(printf '%s\n' 'STOP shared.txt conflicts outside generated content' "STOP $(git rev-parse --short "$f1") fix: resolve line 5 does not apply" "$SHARED_STOP" "STOP the branch is back at $h")" ] && unchanged pr1 "$h" \
    && pass "stop, shared path: permanent through a phase merge and a resolution commit, branch unchanged" || fail "stop, shared path, resolution commit: $o3"
}

c_stop_owned() {
  init stop-owned; orch; phase
  line 3 'line 3 phase' shared.txt; echo a > a.txt; commit 'feat: a'; c1=$(sha)
  round pr1 pr1:main "$c1" || fail "stop-owned build: $out"
  other other-pr 'feat: other phase edits line 10' put_line 10 'line 10 other' shared.txt
  squash other-pr; h=$(git rev-parse origin/pr1)
  round pr1 pr1:main; o="$code $out"
  [ "$o" = '1 STOP shared.txt changed on origin/main after the phase last took it, so the phase must merge it first' ] && unchanged pr1 "$h" \
    && pass "stop, owned path changed cleanly: STOP, branch unchanged" || fail "stop, owned path changed cleanly: $o"
  git checkout -q phase; take origin/main
  round pr1 pr1:main; o="$code $out"
  [ "${o%% *}" = 0 ] && guarded "$h" origin/pr1 && [ "$(at origin/pr1 shared.txt 3) $(at origin/pr1 shared.txt 10)" = 'line 3 phase line 10 other' ] && equal pr1:main \
    && pass "stop, owned path changed cleanly: cleared once the phase merges main, EQUAL" || fail "stop, owned path cleared: $o; proof $out"
}

xphase_in() { echo x1 > x1.txt && commit 'feat: x1' && echo x2 > x2.txt && commit 'feat: x2' && echo x3 > x3.txt && commit 'feat: x3' && git push -q origin HEAD:refs/heads/xphase; }
c_stop_forge() {
  init stop-forge
  other x1 'feat: x1' write x1.txt x1
  other_on origin/x1 x2 'feat: x2' write x2.txt x2
  other_on origin/x2 x3 'feat: x3' write x3.txt x3
  git fetch -q origin; in_wt origin/main xphase_in
  orch; take origin/xphase; phase
  echo a > a.txt; commit 'feat: a, needs x2'; c1=$(sha)
  round ours ours:main:x2 "$c1" && equal ours:main:x2 || fail "stop-forge build: $out"
  squash x1; forge x2 origin/x1 || { fail "stop-forge: the simulated rewrite changed the tree"; return; }
  h=$(git rev-parse origin/ours); round ours ours:main:x2:x1; o1="$code $out"; not_equal ours:main:x2:x1; p1=$out; h1=$(git rev-parse origin/ours)
  round ours ours:main:x2:x1; not_equal ours:main:x2:x1; p2=$out
  squash x2; round ours ours:main::x2,x1; not_equal ours:main::x2,x1; p3=$out
  fl='FAIL ours: it changes x2.txt, which the phase does not'
  for p in "$p1" "$p2" "$p3"; do out=$p; has "$fl" && [ "$(echo "$p" | tail -1)" = 'NOT EQUAL' ] || { fail "stop, forge-rewritten row 3, documented output: $p"; return; }; done
  pass "stop, forge-rewritten row 3: the documented FAIL in every round, also after the dependency merged"
  [ "$h1" = "$h" ] && pass "stop, forge-rewritten row 3: the branch is left where it started, and nothing is pushed" || fail "stop, forge-rewritten row 3: the round pushed $(git log --oneline -1 "$h1") over $(git rev-parse --short "$h"): $o1"
}

c_stop_delegate() {
  init stop-delegate; orch; phase
  git checkout -q -b delegate; echo d > d.txt; commit 'feat: delegate work'; cd_=$(sha)
  git checkout -q phase; echo z > z.txt; commit 'feat: session work'; c0=$(sha)
  git merge -q --no-ff --no-edit delegate
  round pr1 pr1:main "$c0" "$cd_"; o="$code $out"
  not_equal pr1:main && has 'FAIL pr1: it changes d.txt, which the phase does not' \
    && pass "stop, delegate merge: the documented FAIL" || fail "stop, delegate merge, documented output: $out"
  unpushed pr1 && pass "stop, delegate merge: nothing is pushed" || fail "stop, delegate merge: the round pushed origin/pr1 with $(hand origin/main origin/pr1)and without d.txt: $o"
}

c_stop_dir() {
  init "stop-$1"
  if [ "$1" = dir ]; then on_main 'docs: notes' write notes 'some notes'; else on_main 'docs: notes' sh -c 'mkdir notes && echo one > notes/one.md'; fi
  orch; phase
  if [ "$1" = dir ]; then git rm -q notes; mkdir notes; echo one > notes/one.md; else git rm -rq notes; echo 'a file' > notes; fi
  commit "docs: notes becomes a $1"; c1=$(sha)
  round pr1 pr1:main "$c1"; r=$out o="$code $(echo "$out" | grep -v -E '^hint:|^warning: index entry')"
  prove pr1:main; p=$out
  out=$r; has 'git checkout-index: notes is not in the cache' && out=$p && [ "$(echo "$p" | tail -1)" = 'NOT EQUAL' ] \
    && if [ "$1" = dir ]; then has 'FAIL pr1: it changes notesone.md, which the phase does not'; else has 'FAIL pr1: it changes .*, which the phase does not'; fi \
    && pass "stop, $2: the documented refresh line and FAIL" || fail "stop, $2, documented output: refresh $o; proof $p"
  unpushed pr1 && pass "stop, $2: nothing is pushed" || fail "stop, $2: the round pushed origin/pr1"
}
c_stop_file_to_dir() { c_stop_dir dir "file to directory"; }
c_stop_dir_to_file() { c_stop_dir file "directory to file"; }

c_chain() {
  init chain; orch; phase
  line 2 'line 2 pr1' shared.txt; echo a > a.txt; commit 'feat: pr1'; k1=$(sha)
  line 11 'line 11 pr2' shared.txt; echo b > b.txt; commit 'feat: pr2'; k2=$(sha)
  round pr1 pr1:main "$k1" && round pr2 pr2:main "$k2" || fail "chain build: $out"
  not_equal pr1:main pr2:main && has 'FAIL shared.txt is in (pr1 and pr2|pr2 and pr1), which are not in one stack' \
    && pass "chained rule: two unchained pull requests on one hand-written path are NOT EQUAL" || fail "chained rule, unchained: $out"
  h=$(git rev-parse origin/pr2); round pr2 pr2:pr1; o="$code $out"
  [ "${o%% *}" = 0 ] && guarded "$h" origin/pr2 && anc origin/pr1 origin/pr2 && [ "$(hand origin/pr1 origin/pr2)" = 'b.txt shared.txt ' ] && equal pr1:main pr2:pr1 \
    && pass "chained rule: the later one restacked on the earlier one, EQUAL" || fail "chained rule, chained: $o; diff $(hand origin/pr1 origin/pr2); proof $out"
}

c_merged_listed() {
  init merged-parent; orch; phase
  line 2 'line 2 parent' shared.txt; commit 'feat: parent'; c1=$(sha)
  echo c > c.txt; commit 'feat: child'; c2=$(sha)
  round parent parent:main "$c1" && round child child:parent "$c2" || fail "merged-parent build: $out"
  squash parent; on_main 'fix: another pull request fixes line 2' put_line 2 'line 2 fixed' shared.txt
  round child child:main::parent || fail "merged-parent child round: $out"
  not_equal child:main::parent && has 'FAIL shared.txt has not landed and is in no open pull request, so it needs a new pull request' && equal parent:main child:main::parent \
    && pass "merged listed: a merged parent listed as the handbook says gives EQUAL" || fail "merged listed, parent: $out"
  cd "$S"; init merged-new; orch; phase
  echo a > a.txt; commit 'feat: a'; c1=$(sha)
  round pr1 pr1:main "$c1" || fail "merged-new build: $out"
  squash pr1; echo 'a fixed' > a.txt; commit 'fix: a'; f2=$(sha)
  round pr1b pr1b:main::pr1 "$f2"; o="$code $out"
  [ "${o%% *}" = 0 ] && [ "$(git show origin/pr1b:a.txt)" = 'a fixed' ] && equal pr1:main pr1b:main::pr1 \
    && pass "merged listed: a new pull request for a fix after its merge, with the merged one listed, EQUAL" || fail "merged listed, new pull request: $o; proof $out"
}

for c in c_split c_rounds c_rewrite c_r1_squash_fix c_r1_version_fix c_r1_version_build c_r1_orch_merged c_r1_two_squashed c_r1_stack_moves c_r1_spaces \
  c_r2_conflict_commit c_r2_conflict_merge c_r2_clean_merge c_r2_orch_line c_r2_orch_delete c_r2_merge_commit c_r2_row3_to_row2 c_r2_grandchild \
  c_r2_delete_package c_r2_undeclared c_r2_adjacent c_uncarried c_leak c_identity c_assumptions c_missing \
  c_revert c_origin_names c_stop_shared c_stop_owned c_stop_forge c_stop_delegate c_stop_file_to_dir c_stop_dir_to_file c_chain c_merged_listed; do
  (cd "$S" && "$c") || fail "$c ended early"
done
n=$(wc -l < "$S/failed" | tr -d ' ')
echo "$n failed"
[ "$n" = 0 ]
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

### Cold read. What each `STOP` means and who acts

A `STOP` line hands work to someone, and the PR creator acts on the handbook's prose, so this check is a cold read. Start a fresh subagent, give it only `packages/s-stack/.apm/skills/sam-mode/handbooks/pr-creator.md`, tell it to read nothing else, and ask the question. Its answer passes when it agrees in substance with every point of the expected answer. Wait for it to finish before reporting.

Prompt: "Read only the file `packages/s-stack/.apm/skills/sam-mode/handbooks/pr-creator.md` and nothing else, not even files it links to or names. Answer from it alone. You are the PR creator for phase `widgets`. The default branch is `main`. Your pull request #12 is on branch `widgets-pr`. Each item below is output you see in a round. For each, say what it means, who acts next and what they do, what you do, and in what state the branch is left. (1) The refresh prints `STOP shared.txt changed on origin/main after the phase last took it, so the phase must merge it first` and exits 1. (2) The same line, but naming `gadgets-pr`, another phase's open pull request that #12 depends on, instead of `origin/main`. (3) The refresh prints `STOP shared.txt conflicts outside generated content`, then `STOP 1a2b3c4 feat: widgets does not apply`, then `STOP shared.txt is a shared path, so the stop is permanent: no merge or commit on the phase clears it, and it needs a decision`, while a parent pull request of your own phase had a fix round on the line next to your change. (4) The refresh prints `STOP gadgets-pr does not hold origin/main, so widgets-pr must target it with gadgets-pr merged in`. Answer twice: (a) `widgets-pr` is a new pull request; (b) `widgets-pr` is already stacked on an open parent and the base table now gives another base. (5) The refresh prints `STOP gone is not a branch here`, where `gone` is a dependency that merged last week. (6) A carry stops and also prints `the branch is back at 9f8e7d6`. What has happened to the branch and to `origin/widgets-pr`? (7) The proof prints `FAIL a.txt has not landed and is in no open pull request, so it needs a new pull request`. Answer twice: (a) `a.txt` changed in a fix the phase made after its pull request merged; (b) the named path is `orch-fix.txt`, which the orchestrator committed on the orchestrator branch outside `.foundry/`. (8) May you resolve any of these conflicts yourself by editing files? (9) `widgets-pr` targets `main` and carries `gadgets-pr`, which was stacked on `gizmos-pr`. After `gizmos-pr` merged, every round's proof prints `FAIL widgets-pr: it changes gadgets.txt, which the phase does not`, where `gadgets.txt` is one of `gadgets-pr`'s files, and it still does after `gadgets-pr` merges. (10) The phase session merged a delegate's branch into the phase with a merge commit, and the proof prints `FAIL widgets-pr: it changes d.txt, which the phase does not` for the delegate's file `d.txt`. (11) The refresh prints `git checkout-index: notes is not in the cache`, and the proof prints `FAIL widgets-pr: it changes notesone.md, which the phase does not`, after the phase replaced the file `notes` with a directory `notes/` holding `one.md`. For (1), (2), (3), (9), (10) and (11), also say who decides, and what the options or the action are that would clear it."

Expected answer:

1. The default branch changed a path the pull request owns after the phase last took it, even without a conflict, such as another pull request landing an edit elsewhere in the file. The PR creator does not work around it. It reports the output to the phase session, which sends it to the orchestrator as a decision request. Clearing it needs the phase to merge `origin/main` and resolve any conflict there, which moves the phase's code head and so needs Verify and Review again; it is not a gate-free round. The decision is whether the phase merges now. The branch is left where it started, nothing is pushed.
2. The same stale path, changed by the phase that owns `gadgets-pr`. The same decision request goes through the phase session to the orchestrator. Clearing it needs this phase to merge `gadgets-pr` and resolve any conflict there, with both gates again. The PR creator never writes `gadgets-pr`'s branch.
3. A shared path's own commits do not apply on this base, and the stop is permanent: neither a merge resolution nor a resolution commit on the phase reaches the pull request. The PR creator reports the lines to the phase session and does not resolve the conflict, and the phase session sends the orchestrator a decision request. The options are a one-off rebuild of the branch from its base, which force-pushes and needs the developer's approval, or a replacement pull request on a new branch. The branch is back where it started, nothing is pushed.
4. (a) Use the third row of the base table: target `main` with `gadgets-pr` merged in, a spec such as `widgets-pr:main:gadgets-pr`, and no `gh stack link`. (b) This is leaving a stack. Do not refresh it onto the new base, and do not run `gh stack unstack`. Report it to the phase session.
5. A branch in the spec is missing. Fetch again, restore the merged dependency's ref with `git fetch origin pull/<number>/head:gone`, or correct the spec, then run the round again. Never prune remote-tracking refs.
6. The carry failed and the branch was reset to the head it started from. `origin/widgets-pr` is untouched, because pushing comes after a successful refresh.
7. (a) An uncarried phase change. Open a new draft pull request for it, with its base from the base table and a new branch, run its round and the three checks again. (b) A broken assumption of the proof, not the phase's own work. Open no pull request. Report it to the phase session with the `FAIL` lines, and the phase session raises it with the orchestrator.
8. No. The PR creator never resolves a hand-written conflict and never changes what the code does.
9. GitHub rewrote `gadgets-pr`'s head when its parent merged, so `widgets-pr` holds the old head and the proof stays `NOT EQUAL` in every round, even after `gadgets-pr` merges. The PR creator does not work around it and opens no pull request for it. It reports the output to the phase session, which sends the orchestrator a decision request with the same two options as (3): a one-off rebuild that force-pushes with the developer's approval, or a replacement pull request on a new branch.
10. A delegate's branch merged into the phase breaks the proof's assumption that the phase's own commits sit on its first-parent line, so the delegate's commits are not phase commits. The PR creator opens no pull request for it and reports it with the `FAIL` lines to the phase session, which sends the orchestrator a decision request. Taking the delegate's commits with `git cherry-pick -x` instead of a merge works.
11. The phase replaced a file with a directory of the same name, which the design does not handle. The PR creator reports it to the phase session, which sends the orchestrator a decision request: whether to split that change by hand, or to undo it in the phase.

## Evidence

The phase's own verifier runs these at every code head it verifies. They are never rerun by the merged-branch check.

### `gh stack link` with pull request numbers only links

What it checks: the handbook's rule that `gh stack link <parent number> <own number>` adds a pull request on top of its parent's stack without pushing or rebasing any branch, and that linking a merged pull request is refused. The scratch cases cannot reach GitHub.

How: in a throwaway public repository owned by the developer, never Foundry, push two branches with plain `git push`, open both as drafts with `gh pr create --draft`, and run `gh stack link <first> <second>`. Record both branches' head SHAs before and after, and the stack GitHub shows. Then merge the first, open a third draft on the second, and run `gh stack link <first> <third>`. The rule holds when the heads do not move on the first link and the second link is refused. This changes state on GitHub, so the developer runs it or approves it first.

### A forge rewrite keeps the tree

What it checks: the handbook's rule that when a stack parent merges, GitHub may rewrite the child's head with the same tree and new commits, which the `forge rewrite` and `round 2 grandchild` cases simulate.

How: pick a pull request of this run whose stack parent has merged, from the run's decisions. Read its force-push events with `gh api graphql`, asking for `pullRequest(number: <n>) { timelineItems(itemTypes: [HEAD_REF_FORCE_PUSHED_EVENT]) { nodes { ... on HeadRefForcePushedEvent { createdAt beforeCommit { oid tree { oid } } afterCommit { oid tree { oid } } } } } }`. The rule holds when an event at the parent's merge time has equal tree ids and different commit ids. It only reads.
