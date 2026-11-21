# PR creator commands

This file holds the script the PR creator runs. `handbooks/pr-creator.md` says when to run each command. Copy the block at the end of this file, exactly as it stands, into a file outside the repository, such as `pr.sh` in your scratch directory. Set its parameter lines once, then run it with `bash` from a worktree of the repository. It needs bash and git 2.43 or later.

```text
bash pr.sh refresh <phase branch> <default branch> <spec> [<commit> ...]
bash pr.sh prove <orchestrator branch> <phase branch> <default branch> <spec> ...
```

## The parameters

The feature plan names the generated files, the command that regenerates them and the regenerate commit's subject. The script's first lines hold them. The values shown are Foundry's.

| Parameter | Holds |
| --- | --- |
| `REGEN` | The regenerate commit's subject, as a `git --grep` pattern |
| `GEN` | An exclude pathspec for each wholly generated file |
| `LINES` | An exclude pathspec for each file in which some lines are generated |
| `LINES_IN` | The pathspec those files match |
| `GEN_LINE` | A generated line, as an extended regular expression |

A repository with no generated files sets `GEN=()` and `LINES=()`, sets `LINES_IN` to a path that does not exist, and sets `REGEN` and `GEN_LINE` to patterns that nothing matches. The script also matches each path against `LINES_IN`, and against each `GEN` pattern without its `:(exclude)`, as a bash pattern, in which `*` matches `/` too.

## Specs

Both commands describe a pull request as `<pr>:<base>[:<open deps>[:<merged deps>]]`.

- `<pr>` is the pull request's branch.
- `<base>` is the branch the pull request targets on GitHub: the parent's branch when it is stacked, otherwise the default branch. A parent's branch must hold `origin/<default>`.
- `<open deps>` lists, with commas, the branches of the open dependencies merged into a pull request that targets the default branch.
- `<merged deps>` lists the branches of dependencies that have merged into the default branch, squash-merged or not. Their branch refs must stay, because they keep those commits out of the pull request's own commits.

| Spec | Pull request |
| --- | --- |
| `pr1:main` | No open dependency |
| `pr2:pr1` | Stacked on `pr1` |
| `pr3:main:pr1,pr2` | Targets `main` and carries `pr1` and `pr2` |
| `pr2:main::pr1` | `pr1` was squash-merged into `main` |

A branch may be written `main` or `origin/main`. The script uses `origin/<branch>` whenever that ref exists, so push a parent before its child reads it. A pull request's own commits are the commits reachable from its branch and from none of the default branch, its base and its dependencies, leaving out merges and regenerate commits.

## How the script sees the phase

- **Phase commits** are the commits on the phase branch's first-parent line that the default branch lacks, leaving out merges. Work that reached the phase through a merge, such as another phase's commits from the orchestrator branch, is not a phase commit.
- **A commit's paths** are the files it changes outside `.foundry/`. A wholly generated file counts only when the commit deletes it. A file with generated lines counts only when its hand-written lines change.
- **A carried commit** ends its message with `(cherry picked from commit <sha>)`, naming its phase commit, as `git cherry-pick -x` writes it. The script matches a pull request's commit to a phase commit by that line or by its own hash, never by author, date or subject. A forge rebase keeps the message, so a head GitHub rewrote still matches.
- **A phase commit is accounted for** a pull request when the pull request's branch, a merged dependency's branch or the default branch holds it, or holds a commit carried from it.
- **A shared path** is one that commits other than phase commits changed on the phase branch, or one with a phase commit that is not accounted for, because another pull request of the phase carries it. Every other path of a pull request's own commits is **owned** by it.

## Refresh a branch

`refresh` brings a pull request branch onto its base, carries new commits to it, and sets each of its paths to the phase's content. Run it in the branch's worktree, with the branch checked out. The first build, a fix round, a moved default branch, a merged dependency, a new base and a regenerate-only round all use it.

1. **Check the spec.** Every branch the spec names must exist. A base other than the default branch must hold `origin/<default>`.
2. **Check for stale paths.** For each owned path of the pull request, it reads the version on the default branch, on each open dependency, and on the base when the base is another phase's pull request. That version must equal the phase tip's, the one at the phase's merge base with that branch, or one the phase branch has held since. So a default branch that holds an earlier version of the phase's file, such as one a merged pull request landed, is not stale.
3. **Carry.** It carries each `<commit>` given, oldest first. An owned path takes the commit's version of the file, with the current generated lines. A shared path takes only the commit's own change, through `git apply --3way`. Each carried commit keeps the original author, date and message, and adds the `(cherry picked from commit <sha>)` line. A commit with nothing left to carry is skipped.
4. **Overlay.** In a temporary worktree at the base's tip, it merges each open dependency's tip. Then, for each path of the pull request's own commits, an owned path takes the phase tip's version with the base's generated lines, or is deleted when the phase deleted it. A shared path replays, with `git apply --3way`, each phase commit on that path that the pull request carries, oldest first. A conflict in a wholly generated file keeps the base's side. A file with generated lines is merged after both sides take the base's generated lines. Any other conflict stops the refresh.
5. **Record.** When a base tip is not yet an ancestor of `HEAD`, or the overlaid tree differs from `HEAD` outside generated files and generated lines, it records the tree as one merge commit, `git commit-tree <tree> -p HEAD -p <each new tip>`, and prints `merged <commit>`. Otherwise it prints `up to date with <tips>`. The merge takes the base's generated content, so a regenerate commit usually follows.

The merge commit and the carried commits run no hook. A stop prints `STOP` lines, leaves the branch where it started and exits 1.

| `STOP` line | Cause |
| --- | --- |
| `<branch> is not a branch here` | A branch in the spec is missing |
| `<base> does not hold origin/<default>, so <pr> must target it with <base> merged in` | A stacked spec on a parent that has not taken the default branch |
| `<path> changed on <branch> after the phase last took it, so the phase must merge it first` | An owned path is stale |
| `<path> conflicts outside generated content`, then `<commit> does not apply` | A shared path's replay conflicts |
| `the branch is back at <commit>` | Follows a failed carry |

## Prove the split

`prove` checks that the pull requests hold exactly the phase. List every open pull request of the phase, bottom of the stack first. A merged pull request may be left out, but keep its branch in the specs that name it. The default branch may be given as `<default>` or `origin/<default>`.

- **Each pull request's head** equals its target tree outside generated files and generated lines. The target tree is the overlay of its own commits, built at the merge base of its base and its head, with each open dependency's merge base merged in. This catches a hand edit inside a merge commit and a path taken from the wrong version.
- **No own commit is already on the orchestrator branch.** Such a commit belongs to another pull request, so the spec is missing a dependency.
- **No pull request changes a path that the phase commits do not.**
- **Regenerate commits** change only generated files and generated lines.
- **No pull request contains `.foundry/`.**
- **Every path is owned.** Each path of the phase commits whose version on the phase tip differs from the default branch's is in an open pull request. Every open pull request that holds it lies in one dependency chain, and the topmost of them accounts for every phase commit on the path.

It prints each pull request's hand-written diff against its base as `git diff --shortstat` does, then `EQUAL` and exits 0, or a `FAIL` line for each fault, then `NOT EQUAL`, and exits 1. Before a head's `FAIL` line, a `git diff --stat` list names each file that differs.

The ownership check prints one of these:

- `<path> has not landed and is in no open pull request, so it needs a new pull request`;
- `<path> is in <pr> and <pr>, which are not in one stack`;
- `<path>: <pr> lacks phase commits <hash> <subject>;, so they need a pull request`.

## What the proof assumes

The proof relies on two rules from the other handbooks. When either is broken, it prints `NOT EQUAL`.

- **The phase merges the orchestrator branch with `git merge --no-ff`.** A fast-forward puts the orchestrator's merges on the phase's first-parent line, and the phase's own commits then drop out of the phase commits. The proof prints `<pr>: it changes <path>, which the phase does not`.
- **The orchestrator commits nothing outside `.foundry/`.** An orchestrator commit outside `.foundry/`, or another phase's branch squash-merged into the phase, becomes a phase commit that no pull request carries. The proof prints `<path> has not landed and is in no open pull request`.

## The script

```bash
cd "$(git rev-parse --show-toplevel)" || exit 1
IFS=$'\n'                                               # paths with spaces survive every loop
export GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.quotePath GIT_CONFIG_VALUE_0=false
REGEN='^chore(s-stack): regenerate generated files$'
GEN=(':(exclude)*apm.lock.yaml')
LINES=(':(exclude)*apm.yml') LINES_IN='*apm.yml'
GEN_LINE='^version: '
ref() { local b=${1#origin/}; git rev-parse -q --verify "refs/remotes/origin/$b" >/dev/null && echo "origin/$b" || echo "$1"; }
not() { local d r; for d; do for r in "$d" "$(ref "$d")"; do git rev-parse -q --verify "$r^{commit}" >/dev/null && echo "^$r"; done; done; }
own() { local pr=$1; shift; git rev-list --reverse --no-merges "$pr" $(not "$@") --invert-grep --grep="$REGEN"; }
only_lines() { git diff -U0 "$1" "$2" -- "${3:-$LINES_IN}" | grep -E '^[-+]' | grep -v -E '^(\+\+\+|---) ' | grep -v -E "^[-+]${GEN_LINE#^}"; }
same() { git diff --quiet "$1" "$2" -- . "${GEN[@]}" "${LINES[@]}" ':(exclude).foundry' && [ -z "$(only_lines "$1" "$2")" ]; }
gen_as() { awk -v re="$GEN_LINE" 'NR == FNR { if ($0 ~ re) g[++n] = $0; next } $0 ~ re && i < n { print g[++i]; next } { print }' "$1" "$2"; }
is_gen() { local p; for p in "${GEN[@]}"; do [[ $1 == ${p#':(exclude)'} ]] && return 0; done; return 1; }
resolve() {
  local f d; d=$(mktemp -d)
  for f in $(git diff --name-only --diff-filter=U); do
    if is_gen "$f"; then git checkout --ours -- "$f" && git add -- "$f" && continue
    elif [[ $f == $LINES_IN ]] && git show ":2:$f" > "$d/o" 2>/dev/null && git show ":3:$f" > "$d/t" 2>/dev/null; then
      git show ":1:$f" > "$d/b" 2>/dev/null || : > "$d/b"
      gen_as "$d/o" "$d/b" > "$d/b2" && gen_as "$d/o" "$d/t" > "$d/t2" && git merge-file -q "$d/o" "$d/b2" "$d/t2" && cat "$d/o" > "$f" && git add -- "$f" && continue
    fi
    echo "STOP $f conflicts outside generated content"; rm -rf "$d"; return 1
  done; rm -rf "$d"
}
apply_c() {
  local c=$1; shift
  git diff-tree -r --quiet "$c^" "$c" -- "$@" && return 0
  git diff-tree -p --binary "$c^" "$c" -- "$@" | git apply --index --3way --whitespace=nowarn 2>/dev/null ||
    { [ -n "$(git ls-files -u)" ] && resolve; } ||
    { echo "STOP $(git log -1 --format='%h %s' "$c") does not apply"; return 1; }
}
merge_in() {
  local t; for t; do
    git merge -q --no-ff --no-commit "$t" >/dev/null 2>&1; git rev-parse -q --verify MERGE_HEAD >/dev/null || continue
    { [ -z "$(git ls-files -u)" ] || resolve; } && git commit -q --no-verify -m base || return 1
  done
}
at() { tmp=$W/tree; git worktree add -q --detach "$tmp" "$1" && cd "$tmp"; }
done_at() { cd "$1" && git worktree remove --force "$tmp"; }
list() { echo "$1" | tr , '\n' | grep .; }
paths() {
  local c e x; for c; do for e in $(git diff-tree --no-commit-id --no-renames --name-status -r "$c" -- . ':(exclude).foundry'); do
    x=${e#*$'\t'}
    if is_gen "$x"; then [ "${e%%$'\t'*}" = D ] || continue
    elif [[ $x == $LINES_IN ]]; then [ -n "$(only_lines "$c^" "$c" ":(literal)$x")" ] || continue; fi
    echo "$x"
  done; done | sort -u
}
ver() {
  local e; e=$(git ls-tree "$1" -- ":(literal)$2"); [ -n "$e" ] || { echo none; return; }
  e=${e%%$'\t'*}; [[ $2 == $LINES_IN ]] || { echo "$e"; return; }
  echo "${e%% *} $(git cat-file blob "${e##* }" | grep -v -E "$GEN_LINE" | git hash-object --stdin)"
}
ids() {
  git log -z --no-merges --format='%H%n%B' "$@" | tr '\0' '\036' | awk 'BEGIN { RS = "\036" } NF { print $1
    n = split($0, l, "\n"); for (i = n; i > 1; i--) if (l[i] ~ /^\(cherry picked from commit [0-9a-f]+\)$/) { print substr(l[i], 28, length(l[i]) - 28); break } }'
}
setup() {
  local first; PH=$1 D=$(ref "$2") W=$(mktemp -d); trap 'rm -rf "$W"' EXIT; first=$(git rev-list --first-parent "$PH" "^$D" | tail -1)
  S0=$(git rev-parse "${first:-$D}^" 2>/dev/null || git rev-parse "$D")
  git rev-list --first-parent --no-merges "$PH" "^$D" > "$W/fp"
}
refs() { local b; for b in $(list "$1"); do ref "$b"; done; }
accounted() { ids "$@" "$D" "^$S0" | sort -u > "$W/acc"; }
unacc() {
  local t; t=$(git rev-list --first-parent --no-merges "${2:-$PH}" "^$D" -- ":(literal)$1"); [ -n "$t" ] || return 1
  [ -n "$(echo "$t" | grep -v -x -F -f "$W/acc")" ]
}
foreign() { [ -n "$(git rev-list --no-merges "$PH" "^$D" -- ":(literal)$1" | grep -v -x -F -f "$W/fp")" ]; }
shared() { foreign "$1" || unacc "$1"; }
put() {
  local x=$1 e m s; e=$(git ls-tree "$2" -- ":(literal)$x")
  [ -n "$e" ] || { git update-index -q --force-remove -- "$x"; rm -f -- "$x"; return 0; }
  e=${e%%$'\t'*}; m=${e%% *}; s=${e##* }
  if [[ $x == $LINES_IN ]] && git show ":0:$x" > "$W/cur" 2>/dev/null; then
    git cat-file blob "$s" > "$W/new"; s=$(gen_as "$W/cur" "$W/new" | git hash-object -w --stdin)
  fi
  git update-index --add --cacheinfo "$m,$s,$x" && git checkout-index -f -- "$x"
}
overlay() {
  local x c; [ $# = 0 ] || ids --no-walk=unsorted "$@" > "$W/mine"
  for x in $(paths "$@"); do
    if shared "$x"; then
      for c in $(git rev-list --reverse --first-parent --no-merges "$PH" "^$D" -- ":(literal)$x"); do
        grep -q -x -F "$c" "$W/mine" || continue; apply_c "$c" ":(literal)$x" || return 1
      done
    else put "$x" "$PH"; fi
  done
}
trailer() {
  git log -1 --format=%B "$1" | git stripspace > "$W/msg"
  git interpret-trailers --parse < "$W/msg" | grep -q . || echo >> "$W/msg"; echo "(cherry picked from commit $1)" >> "$W/msg"
}
carry() {
  local c x; for c; do
    for x in $(paths "$c"); do if unacc "$x" "$c"; then apply_c "$c" ":(literal)$x" || return 1; else put "$x" "$c"; fi; done
    git diff --cached --quiet || { trailer "$c" && git commit -q --no-verify -F "$W/msg" --author="$(git log -1 --format='%an <%ae>' "$c")" --date="$(git log -1 --format=%ad --date=raw "$c")"; } || return 1
  done
}
stale() {
  local t x b v c; for t; do b=$(git merge-base "$PH" "$t")
    for x in $(paths "${mine[@]}"); do shared "$x" && continue; v=$(ver "$t" "$x")
      { [ "$v" = "$(ver "$PH" "$x")" ] || [ "$v" = "$(ver "$b" "$x")" ]; } && continue
      for c in $(git rev-list --full-history "$PH" "^$b" -- ":(literal)$x"); do [ "$v" = "$(ver "$c" "$x")" ] && continue 2; done
      echo "STOP $x changed on $t after the phase last took it, so the phase must merge it first"; return 1
    done
  done
}
outside() { [ "$(ref "$1")" = "$D" ] || ids "$(ref "$1")" "^$D" | grep -q -x -F -f "$W/fp" || ref "$1"; }
refresh() {
  local pr base extra merged wt head tips t new m new_c; IFS=: read -r pr base extra merged <<< "$3"; setup "$1" "$2"; shift 3; new_c=("$@")
  for t in "$base" $(list "$extra") $(list "$merged"); do git rev-parse -q --verify "$(ref "$t")^{commit}" >/dev/null || { echo "STOP $t is not a branch here"; exit 1; }; done
  [ "$(ref "$base")" = "$D" ] || git merge-base --is-ancestor "$D" "$(ref "$base")" || { echo "STOP $base does not hold $D, so $pr must target it with $base merged in"; exit 1; }
  wt=$(pwd) head=$(git rev-parse HEAD) tips=$(for b in "$base" $(list "$extra"); do ref "$b"; done)
  [ ${#new_c[@]} = 0 ] || new_c=($(git rev-list --no-merges --no-walk=unsorted "${new_c[@]}"))
  mine=($(own "$head" "$D" "$base" $(list "$extra") $(list "$merged")) "${new_c[@]}")
  accounted HEAD $(refs "$merged"); [ ${#new_c[@]} = 0 ] || printf '%s\n' "${new_c[@]}" >> "$W/acc"
  stale "$D" $(refs "$extra") $(outside "$base") || exit 1
  [ ${#new_c[@]} = 0 ] || carry "${new_c[@]}" || { git reset -q --hard "$head"; echo "STOP the branch is back at $head"; exit 1; }
  mine=($(own HEAD "$D" "$base" $(list "$extra") $(list "$merged"))); accounted HEAD $(refs "$merged")
  at "$(ref "$base")" && merge_in $(echo "$tips" | sed 1d) && overlay "${mine[@]}" || { done_at "$wt"; git reset -q --hard "$head"; exit 1; }
  t=$(git write-tree); done_at "$wt"
  new=$(for x in $tips; do git merge-base --is-ancestor "$x" HEAD || echo "$x"; done)
  if [ -n "$new" ] || ! same "$t" HEAD; then
    m=$(git commit-tree "$t" -p HEAD $(for x in $new; do printf -- '-p\n%s\n' "$x"; done) -m "Merge $(echo $tips) into $pr") && git merge -q --ff-only "$m" || exit 1
    echo "merged $m"
  else echo "up to date with $(echo $tips)"; fi
}
deps_of() { local s b e x m; for s in "${specs[@]}"; do IFS=: read -r b e x m <<< "$s"; [ "$b" = "$1" ] && { echo "${e#origin/}"; list "$x,$m" | sed 's,^origin/,,'; }; done; }
above() { local d; for d in $(deps_of "$1"); do { [ "$d" = "$2" ] || above "$d" "$2"; } && return 0; done; return 1; }
prove() {
  local orch=$1 fail=0 top s c f l t x o i; setup "$2" "$3"; shift 3; specs=("$@") top=$(pwd)
  spec() { IFS=: read -r pr base extra merged <<< "$1"; mine=($(own "$pr" "$D" "$base" $(list "$extra") $(list "$merged"))); }
  paths $(git rev-list --first-parent --no-merges "$PH" "^$D") > "$W/pp"
  for s; do
    spec "$s"; paths "${mine[@]}" > "$W/own.${pr//\//_}"
    echo "$pr:$(git diff --shortstat "$(ref "$base")...$pr" -- . "${GEN[@]}")"
    for c in ${mine[@]}; do ! git merge-base --is-ancestor "$c" "$orch" || { echo "FAIL $pr: $c is already on $orch, so its pull request is an undeclared dependency"; fail=1; }; done
    for x in $(grep -v -x -F -f "$W/pp" "$W/own.${pr//\//_}"); do echo "FAIL $pr: it changes $x, which the phase does not"; fail=1; done
    for c in $(git rev-list --no-merges "$pr" $(not "$D" "$base" $(list "$extra") $(list "$merged")) --grep="$REGEN"); do
      for f in $(git diff-tree --no-commit-id --name-only -r "$c" -- . "${GEN[@]}" "${LINES[@]}"); do echo "FAIL $pr: regenerate commit $c changes $f"; fail=1; done
      l=$(only_lines "$c^" "$c"); [ -z "$l" ] || { echo "FAIL $pr: regenerate commit $c changes $l"; fail=1; }
    done
    for f in $(git diff --name-only "$D...$pr" -- .foundry); do echo "FAIL $pr: contains $f"; fail=1; done
    accounted "$pr" $(refs "$merged")
    at "$(git merge-base "$(ref "$base")" "$pr")"
    merge_in $(for e in $(list "$extra"); do git merge-base "$(ref "$e")" "$pr"; done) && overlay "${mine[@]}" && t=$(git write-tree) || t=
    done_at "$top"
    [ -n "$t" ] && same "$t" "$pr" || { [ -z "$t" ] || git diff --stat "$t" "$pr" -- . "${GEN[@]}" "${LINES[@]}"; echo "FAIL $pr: its head differs from its target tree"; fail=1; }
  done
  for x in $(cat "$W/pp"); do
    [ "$(ver "$PH" "$x")" = "$(ver "$D" "$x")" ] && continue
    o=(); for s; do IFS=: read -r pr _ <<< "$s"; grep -q -x -F -- "$x" "$W/own.${pr//\//_}" && o+=("$pr"); done
    [ ${#o[@]} -gt 0 ] || { echo "FAIL $x has not landed and is in no open pull request, so it needs a new pull request"; fail=1; continue; }
    t=${o[0]}; for i in "${o[@]}"; do above "$i" "$t" && t=$i; done
    for i in "${o[@]}"; do [ "$i" = "$t" ] || above "$t" "$i" || { echo "FAIL $x is in $i and $t, which are not in one stack"; fail=1; continue 2; }; done
    for s; do IFS=: read -r pr _ _ merged <<< "$s"; [ "$pr" = "$t" ] && accounted "$pr" $(refs "$merged"); done
    ! unacc "$x" || { echo "FAIL $x: $t lacks phase commits $(git rev-list --first-parent --no-merges "$PH" "^$D" -- ":(literal)$x" | grep -v -x -F -f "$W/acc" | git log --stdin --no-walk=unsorted --format='%h %s' | tr '\n' ';'), so they need a pull request"; fail=1; }
  done
  [ "$fail" = 0 ] && echo EQUAL || { echo "NOT EQUAL"; exit 1; }
}
case ${1:-} in
  refresh | prove) "$@" ;;
  *) echo "usage: bash pr.sh refresh|prove ..."; exit 2 ;;
esac
```
