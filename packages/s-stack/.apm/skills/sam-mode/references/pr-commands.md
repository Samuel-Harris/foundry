# PR creator commands

This file holds the script the PR creator runs. `handbooks/pr-creator.md` says when to run each command. Copy the block at the end of this file, exactly as it stands, into a file outside the repository, such as `pr.sh` in your scratch directory. Set its parameter lines once, then run it with `bash` from a worktree of the repository. It needs bash and git 2.43 or later.

```text
OWN=<own branches> PUSHED=<pushed heads> bash pr.sh refresh <phase branch> <default branch> <spec> [<commit> ...]
OWN=<own branches> MERGED=<merged branches> PUSHED=<pushed heads> bash pr.sh prove <orchestrator branch> <phase branch> <default branch> <spec> ...
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

A branch may be written `main` or `origin/main`. The default branch always resolves to `origin/<default>`. Any other branch resolves to the local branch only when it is named in the environment variable `OWN`, exists, and holds `origin/<branch>`, so a child reads its own phase's parent's unpushed head. `OWN` is a comma-separated list of every pull request branch of this phase, including those opened in earlier rounds and those already merged. Set it on every call. `MERGED` is a comma-separated list of the phase's pull request branches that have merged into the default branch. Set it on every `prove` call. `PUSHED` is a comma-separated list of `<branch>=<sha>` for the pull request branches of this phase that the PR creator has pushed. Set it on every call to the `RECORD` line of the last `prove` that printed `EQUAL`, once that round's pushes have succeeded. A branch may appear more than once: its last entry is the head after that round, and the earlier ones are heads it no longer descends from, as after GitHub rebases a stack child. Every entry's commits count for matching, so a commit the phase took with `git cherry-pick -x` still matches after the commit it names is rewritten. Another phase's branch always resolves to `origin/<branch>`, the state that phase proved and pushed, whatever its local copy holds, and a branch outside `OWN` with no `origin/<branch>` is missing. A pull request's own commits are the commits reachable from its branch and from none of the default branch, its base and its dependencies, leaving out merges and regenerate commits.

## How the script sees the phase

- **Phase commits** are the commits on the phase branch's first-parent line that the default branch lacks, leaving out merges. Work that reached the phase through a merge, such as another phase's commits from the orchestrator branch, is not a phase commit.
- **A commit's paths** are the files it changes outside `.foundry/`. A wholly generated file counts only when the commit deletes it. A file with generated lines counts only when its hand-written lines change.
- **A carried commit** ends its message with `(cherry picked from commit <sha>)`, naming its phase commit, as `git cherry-pick -x` writes it. The script matches a pull request's commit to a phase commit by that line or by its own hash, never by author, date, subject or content. A phase commit taken from a pull request's commit with `git cherry-pick -x` also matches that commit. A forge rebase keeps the message, so a head GitHub rewrote still matches.
- **A phase commit is accounted for** a pull request when the pull request's branch, a merged dependency's branch or the default branch holds it, or holds a commit that matches it. In a refresh, the base's and open dependencies' tips count as the branch, because the merge brings them in. Every head that `PUSHED` names for it counts too, so a commit the phase took with `git cherry-pick -x` still matches after GitHub rebases the pull request.
- **A shared path** is one that commits other than phase commits changed on the phase branch, or one with a phase commit that is not accounted for, because another pull request of the phase carries it. Every other path of a pull request's own commits is **owned** by it.

## Refresh a branch

`refresh` brings a pull request branch onto its base, carries new commits to it, and sets each of its paths to the phase's content. Run it in the branch's worktree, with the branch checked out. The first build, a fix round, a moved default branch, a merged dependency, a new base and a regenerate-only round all use it.

1. **Check the spec.** `<pr>` must be in `OWN`. Every branch the spec names must exist. A base other than the default branch must hold `origin/<default>`.
2. **Check for stale paths.** For each owned path of the pull request, it reads the version on the default branch, on each open dependency, and on the base when the base is another phase's pull request. That version must equal the phase tip's, the one at the phase's merge base with that branch, or one the phase branch has held since. So a default branch that holds an earlier version of the phase's file, such as one a merged pull request landed, is not stale.
3. **Carry.** It carries each `<commit>` given, oldest first. An owned path takes the commit's version of the file, or the phase tip's when no later phase commit changes the path, with the current generated lines. A shared path takes only the commit's own change, through `git apply --3way`. When the pull request and its base hold none of the earlier phase commits on a shared path that no other commit changed, the commit spans two pull requests, and the refresh stops. Each carried commit keeps the original author, date and message, and adds the `(cherry picked from commit <sha>)` line. A commit with nothing left to carry is skipped when it has no paths or the branch, its base or a dependency already holds it or a commit that matches it. Otherwise it is carried as an empty commit, so the pull request accounts for it, as for a phase commit that copies a developer merge's hand edit.
4. **Overlay.** In a temporary worktree at the base's tip, it merges each open dependency's tip. Then, for each path of the pull request's own commits, an owned path takes the phase tip's version with the base's generated lines, or is deleted when the phase deleted it. A shared path replays, with `git apply --3way`, each phase commit on that path that the pull request carries, oldest first. A conflict in a wholly generated file keeps the base's side. A file with generated lines is merged after both sides take the base's generated lines. Any other conflict stops the refresh.
5. **Record.** When a base tip is not yet an ancestor of `HEAD`, or the overlaid tree differs from `HEAD` outside generated files and generated lines, it records the tree as one merge commit, `git commit-tree <tree> -p HEAD -p <each new tip>`, with the base's tip as the second parent when no tip is new and `(s-stack refresh)` as the message's last line, and prints `merged <commit>`. Otherwise it prints `up to date with <tips>`. The merge takes the base's generated content, so a regenerate commit usually follows.

The merge commit and the carried commits run no hook. A stop prints `STOP` lines, leaves the branch where it started and exits 1.

| `STOP` line | Cause |
| --- | --- |
| `<pr> is not in OWN, so it is not one of this phase's pull request branches` | `OWN` leaves out the branch being refreshed |
| `<branch> is not a branch here` | A branch in the spec is missing, or is outside `OWN` and has no `origin/<branch>` |
| `<base> does not hold origin/<default>, so <pr> must target it with <base> merged in` | A stacked spec on a parent that has not taken the default branch |
| `<path> changed on <branch> after the phase last took it, so the phase must merge it first` | An owned path is stale |
| `<path> conflicts outside generated content`, `<commit> does not apply`, then `<path> is a shared path, so the stop is permanent: no merge or commit on the phase clears it, and it needs a decision` | A shared path's replay or carry conflicts |
| `<commit> also changes <path>, which <pr> and its base do not hold, so it spans two pull requests and the split must change` | A carried commit changes another pull request's path, and that pull request is not below this one |
| `<path> conflicts outside generated content` alone | An open dependency conflicts with the base or with another dependency |
| `<pr> would carry <path>, which the phase does not change` | The pull request's own commits touch a path off the phase's first-parent line: a delegate's branch merged into the phase, or a third-row dependency whose old head GitHub rewrote. The check runs before anything is recorded. When the branch holds a developer commit or merge, by the rule in [Prove the split](#prove-the-split), the refresh prints `DEVELOPER-COMMITS <pr> <sha>...` instead and exits 1, so a file the developer added is not taken for a delegate's |
| `<pr> was recorded at <sha>, which is not here, so its developer commits cannot be told apart` | `PUSHED` names a head that this repository lacks. Fetch it, or report |
| `<pr> is on origin but has no PUSHED entry, so its developer commits cannot be told apart` | The branch was pushed before, but the brief gave no recorded head for it. Report, and do not guess one |
| `<path> cannot be written into the tree, as when a file and a directory share its name` | The phase replaced a file with a directory of the same name, or the reverse |
| `the branch is back at <commit>` | Follows a stopped carry |

A shared path's stop is permanent because the refresh replays only the phase's original commits on it. A merge of the default branch into the phase, or a resolution commit, never changes those commits' context on the pull request's base.

## Prove the split

`prove` checks that the pull requests hold exactly the phase. List every pull request of the phase, merged ones included, bottom of the stack first. Write a merged one with the default branch as its base, and name each merged dependency in the fourth field of every spec that depends on it. Write each pull request as its local branch, `<pr>`, because the proof runs before the push: `prove` reads a pull request's head as written, and `origin/<pr>` names the pushed head. The default branch may be given as `<default>` or `origin/<default>`.

- **Each pull request's head** equals its target tree outside generated files and generated lines. The target tree is the overlay of its own commits, built at the merge base of its base and its head, with each open dependency's merge base merged in. This catches a hand edit inside a merge commit and a path taken from the wrong version.
- **No own commit is already on the orchestrator branch.** Such a commit belongs to another pull request, so the spec is missing a dependency.
- **No developer commit or merge.** Each is reported as `DEVELOPER-COMMITS <pr> <sha>...`, which makes the proof `NOT EQUAL`, because the refresh would revert it. The boundary is the last head that `PUSHED` names for the pull request. A branch with no entry and no `origin/<pr>` has not been pushed, so nothing on it is the developer's. A branch on `origin` with no entry stops, because a missing record cannot be told from a first push. The check reads `origin/<pr>` when that ref exists, because a round starts from it. When `PUSHED` names a head that is not here, the proof prints the refresh's `STOP` line for it.
  - A developer commit is an own commit on the pull request's first-parent line after the pushed head that matches no phase commit, such as GitHub's "Apply suggestions from code review".
  - When the pull request's head does not descend from the pushed head, as after GitHub rebases a stack child, the check compares the owned paths of the pull request's own commits instead. A path whose version differs from both the pushed head's and the phase tip's reports the head as `DEVELOPER-COMMITS`. A rebase that brings in the default branch's changes to other files reports nothing. The remedy is the one for a developer merge, with the head's content.
  - A developer merge is a merge after the pushed head, reachable from the pull request and from none of the default branch, its base and its dependencies, whose message does not end with the refresh's `(s-stack refresh)` line. It is reported when its second parent is in none of the default branch, the base and the dependencies, or when it has a hand edit whose version differs from the phase tip's. Its hand edits are the paths where its tree differs from `git merge-tree --write-tree` of its two parents, outside `.foundry/` and wholly generated files, ignoring generated lines. A merge that only brings in the default branch, as GitHub's "Update branch" button makes, is not reported; the refresh starts from it.
  - The remedy for a developer merge is an ordinary phase commit that gives those paths the merge's content. The phase tip then holds the edit, and the next round proves `EQUAL`.
- **A landed pull request is history.** A pull request is landed when it is in `MERGED`, a listed spec names it as a merged dependency, or the default branch holds its head. It takes neither the developer check, the head check, the check below for paths the phase does not change, nor the ownership check's rule for a version that is neither the phase's nor its base's. Its head is read as `origin/<pr>` whenever that ref exists, not as a local branch, which nobody updates after the merge. Its paths still count in the ownership check, except a path where both the phase tip's version differs from the default branch's and the landed head's version differs from the phase tip's, such as after a developer commit that merged with it.
- **No pull request changes a path that the phase commits do not.**
- **Regenerate commits** change only generated files and generated lines.
- **No pull request contains `.foundry/`.**
- **Every path is owned.** Each path of the phase commits whose version on the phase tip differs from the default branch's is in a listed pull request. Every pull request that holds a phase path, whether or not the path differs, lies in one dependency chain, and the topmost of them accounts for every phase commit on the path. When the phase tip's version equals the default branch's, the topmost one's version must also equal the phase tip's or its base's.
- **No delegate merge.** No merge on the phase's first-parent line brings in a branch that the orchestrator branch, the default branch and the specs' bases and dependencies all lack.
- **No edit hides in a phase merge.** Each merge on the phase's first-parent line that is not on the orchestrator branch's is merged again with `git merge-tree --write-tree`. A path outside `.foundry/` and generated content that the merge commit holds differently fails with `<merge> edits <path> inside the merge, so no pull request carries the edit`, unless it is a phase path that no other commit changed. Such a path is owned, so it takes the phase tip's content, a conflict resolution included.

It prints each pull request's hand-written diff against its base as `git diff --shortstat` does, then `EQUAL`, then `RECORD <branch>=<sha>,...`, the next value of `PUSHED`, and exits 0, or a `FAIL` line for each fault, then `NOT EQUAL`, and exits 1. Before a head's `FAIL` line, a `git diff --stat` list names each file that differs.

The ownership check prints one of these:

- `<path> has not landed and is in no open pull request, so it needs a new pull request`, when the default branch and the listed landed pull requests lack a phase commit on it;
- `<path> differs between the phase and <default> and no open pull request holds it: if the phase changed it, open a pull request for its commits; if <default> changed it, for example a developer commit on a merged pull request, merge <default> into the phase`, when they hold every phase commit on it;
- `<path> is in <pr> and <pr>, which are not in one stack`;
- `<path>: <pr> lacks phase commits <hash> <subject>;, so they need a pull request`, when the pull request's version of the path also differs from the phase tip's, which catches a pull request that still holds a change the phase later reverted. A path whose version already equals the phase tip's passes, even when older phase commits on it cannot be matched;
- `<path>: <pr> holds a version that is neither the phase's nor <base>'s`, for such a path with no uncarried commit to name.

## What the proof assumes

The proof relies on three rules from the other handbooks. When one is broken, it prints `NOT EQUAL`, and the round pushes nothing.

- **The phase merges the orchestrator branch with `git merge --no-ff`.** A fast-forward puts the orchestrator's merges on the phase's first-parent line, and the phase's own commits then drop out of the phase commits. The proof prints `<pr>: it changes <path>, which the phase does not`.
- **The orchestrator commits nothing outside `.foundry/`.** An orchestrator commit outside `.foundry/`, or another phase's branch squash-merged into the phase, becomes a phase commit that no pull request carries. The proof prints `<path> has not landed and is in no open pull request`.
- **The phase's own commits sit on its first-parent line.** A delegate's branch merged into the phase leaves its commits off that line. The refresh stops with `<pr> would carry <path>, which the phase does not change` when it is given a delegate commit, and the proof prints `<merge> merges <commit>, whose commits are not phase commits: a delegate's branch merged into the phase` in every case. Commits taken with `git cherry-pick -x` are phase commits, and the proof handles them.

Two other histories stop the refresh in every round, so nothing is pushed, and the handbook sends both for a decision. When GitHub rewrites a third-row dependency's head after its parent merges, or a stack parent's head while leaving its child's alone, the refresh prints `<pr> would carry <file>, which the phase does not change` for the parent's or dependency's files. When the phase replaces a file with a directory of the same name, or the reverse, the refresh prints git's own error and then `<path> cannot be written into the tree, as when a file and a directory share its name`.

A commit or a merge with a hand edit made on a pull request branch, and an edit inside one of the phase's merges, fail the proof as the checks above say. One history goes undetected: a merged pull request that the developer reverts on the default branch. The proof counts the merged pull request as holding its paths, so it still prints `EQUAL`.

## The script

```bash
set -f                                                  # a path such as app/[id]/page.tsx is never a glob
cd "$(git rev-parse --show-toplevel)" || exit 1
IFS=$'\n'                                               # paths with spaces survive every loop
export GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.quotePath GIT_CONFIG_VALUE_0=false
REGEN='^chore(s-stack): regenerate generated files$'
GEN=(':(exclude)*apm.lock.yaml')
LINES=(':(exclude)*apm.yml') LINES_IN='*apm.yml'
GEN_LINE='^version: '
MARK='^(s-stack refresh)$'
mine_b() { [[ ",${OWN:-}," == *",${1#origin/},"* ]]; }
ref() {
  local b=${1#origin/}; git rev-parse -q --verify "refs/remotes/origin/$b" >/dev/null || { mine_b "$b" && echo "$b" || echo "origin/$b"; return; }
  [ "origin/$b" != "${D:-}" ] && git rev-parse -q --verify "refs/heads/$b" >/dev/null && git merge-base --is-ancestor "origin/$b" "refs/heads/$b" && mine_b "$b" && echo "$b" || echo "origin/$b"
}
not() { local d r; for d; do r=$(ref "$d"); git rev-parse -q --verify "$r^{commit}" >/dev/null && echo "^$r"; done; }
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
    { echo "STOP $(git log -1 --format='%h %s' "$c") does not apply"; echo "STOP ${1#':(literal)'} is a shared path, so the stop is permanent: no merge or commit on the phase clears it, and it needs a decision"; return 1; }
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
pairs() {
  git log -z --no-merges --format='%H%n%B' "$@" | tr '\0' '\036' | awk 'BEGIN { RS = "\036" } NF { p = ""
    n = split($0, l, "\n"); for (i = n; i > 1; i--) if (l[i] ~ /^\(cherry picked from commit [0-9a-f]+\)$/) { p = " " substr(l[i], 28, length(l[i]) - 28); break }; print $1 p }'
}
ids() { pairs "$@" | tr ' ' '\n'; }
matched() { awk 'NR == FNR { a[$1]; next } $2 in a { print $1 }' "$1" "$W/named" > "$W/m"; cat "$W/m" >> "$1"; }
setup() {
  local first; PH=$1 D=origin/${2#origin/}; D=$(ref "$2") W=$(mktemp -d); trap 'rm -rf "$W"' EXIT; first=$(git rev-list --first-parent "$PH" "^$D" | tail -1)
  S0=$(git rev-parse "${first:-$D}^" 2>/dev/null || git rev-parse "$D")
  git rev-list --first-parent --no-merges "$PH" "^$D" > "$W/fp"; : > "$W/named"
  [ ! -s "$W/fp" ] || pairs --no-walk=unsorted --stdin < "$W/fp" | awk 'NF == 2' > "$W/named"
}
refs() { local b; for b in $(list "$1"); do ref "$b"; done; }
accounted() {
  ids "$@" "$D" "^$S0" | sort -u > "$W/acc"; matched "$W/acc"
}
unacc() {
  local t; t=$(git rev-list --first-parent --no-merges "${2:-$PH}" "^$D" -- ":(literal)$1"); [ -n "$t" ] || return 1
  [ -n "$(echo "$t" | grep -v -x -F -f "$W/acc")" ]
}
foreign() { [ -n "$(git rev-list --no-merges "$PH" "^$D" -- ":(literal)$1" | grep -v -x -F -f "$W/fp")" ]; }
held() { [ -n "$(git rev-list --first-parent --no-merges "$2^" "^$D" -- ":(literal)$1" | grep -x -F -f "$W/acc")" ]; }
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
  local x c; : > "$W/mine"; [ $# = 0 ] || ids --no-walk=unsorted "$@" > "$W/mine"; matched "$W/mine"
  for x in $(paths "$@"); do
    if shared "$x"; then
      for c in $(git rev-list --reverse --first-parent --no-merges "$PH" "^$D" -- ":(literal)$x"); do
        grep -q -x -F "$c" "$W/mine" || continue; apply_c "$c" ":(literal)$x" || return 1
      done
    else put "$x" "$PH" || { echo "STOP $x cannot be written into the tree, as when a file and a directory share its name"; return 1; }; fi
  done
}
trailer() {
  git log -1 --format=%B "$1" | git stripspace > "$W/msg"
  git interpret-trailers --parse < "$W/msg" | grep -q . || echo >> "$W/msg"; echo "(cherry picked from commit $1)" >> "$W/msg"
}
carry() {
  local c x s ext; for c; do
    ext=; for x in $(paths "$c"); do held "$x" "$c" && ext=1; done
    for x in $(paths "$c"); do
      if unacc "$x" "$c"; then
        [ -n "$ext" ] && ! foreign "$x" && ! held "$x" "$c" && { echo "STOP $(git log -1 --format='%h %s' "$c") also changes $x, which $pr and its base do not hold, so it spans two pull requests and the split must change"; return 1; }
        apply_c "$c" ":(literal)$x" || return 1
      else
        s=$c; [ -n "$(git rev-list -1 --first-parent --no-merges "$PH" "^$c" -- ":(literal)$x")" ] || s=$PH
        put "$x" "$s" || { echo "STOP $x cannot be written into the tree, as when a file and a directory share its name"; return 1; }
      fi
    done
    { git diff --cached --quiet && { grep -q -x -F "$c" "$W/held" || [ -z "$(paths "$c")" ]; }; } || { trailer "$c" && git commit -q --allow-empty --no-verify -F "$W/msg" --author="$(git log -1 --format='%an <%ae>' "$c")" --date="$(git log -1 --format=%ad --date=raw "$c")"; } || return 1
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
matches() { ids --no-walk "$1" | grep -q -x -F -f "$W/fp" || cut -d ' ' -f 2 "$W/named" | grep -q -x -F "$1"; }
entries() { list "${PUSHED:-}" | awk -v b="${1#origin/}=" 'index($0, b) == 1 { print substr($0, length(b) + 1) }'; }
pushed() { entries "$1" | tail -1; }
pin() { local p; p=$(pushed "$1"); [ -n "$p" ] && git cat-file -e "$p^{commit}" 2>/dev/null && echo "$p"; }
pins() { local p; for p in $(entries "$1"); do git cat-file -e "$p^{commit}" 2>/dev/null && echo "$p"; done; }
pushed_here() {
  local p; p=$(pushed "$1")
  [ -n "$p" ] || ! git rev-parse -q --verify "refs/remotes/origin/${1#origin/}" >/dev/null ||
    { echo "STOP ${1#origin/} is on origin but has no PUSHED entry, so its developer commits cannot be told apart"; return 1; }
  for p in $(entries "$1"); do git cat-file -e "$p^{commit}" 2>/dev/null ||
    { echo "STOP ${1#origin/} was recorded at $p, which is not here, so its developer commits cannot be told apart"; return 1; }; done
}
devs() {
  local p h=$2 c b x v; p=$(pin "$1") || return 0; shift 2
  if ! git merge-base --is-ancestor "$p" "$h"; then
    for x in $(paths "${mine[@]}"); do shared "$x" && continue; v=$(ver "$h" "$x")
      [ "$v" = "$(ver "$p" "$x")" ] || [ "$v" = "$(ver "$PH" "$x")" ] || { git rev-parse --short "$h"; return; }
    done; return
  fi
  for c in $(git rev-list --reverse --first-parent --no-merges "$h" "^$p" $(not "$@") --invert-grep --grep="$REGEN"); do matches "$c" || git rev-parse --short "$c"; done
  for c in $(git rev-list --merges "$h" "^$p" $(not "$@") --invert-grep --grep="$MARK"); do
    for b in $(not "$@"); do git merge-base --is-ancestor "$c^2" "${b#^}" && { hand_edited "$c" && git rev-parse --short "$c"; continue 2; }; done; git rev-parse --short "$c"
  done
}
edits() {
  local x; git diff --name-only "$1" "$2" -- . "${GEN[@]}" "${LINES[@]}" ':(exclude).foundry'
  for x in $(git diff --name-only "$1" "$2" -- "$LINES_IN"); do [ -z "$(only_lines "$1" "$2" ":(literal)$x" | grep -v -E '^-(<{7}|={7}|>{7})')" ] || echo "$x"; done
}
hand_edited() {
  local t x; t=$(git merge-tree --write-tree "$1^1" "$1^2" 2>/dev/null | head -1); [ -n "$t" ] || return 0
  for x in $(edits "$t" "$1"); do [ "$(ver "$1" "$x")" = "$(ver "$PH" "$x")" ] || return 0; done; return 1
}
outside() { [ "$(ref "$1")" = "$D" ] || mine_b "$1" || ref "$1"; }
refresh() {
  local pr base extra merged wt head tips t new m new_c; IFS=: read -r pr base extra merged <<< "$3"; setup "$1" "$2"; shift 3; new_c=("$@")
  mine_b "$pr" || { echo "STOP $pr is not in OWN, so it is not one of this phase's pull request branches"; exit 1; }
  pushed_here "$pr" || exit 1
  for t in "$base" $(list "$extra") $(list "$merged"); do git rev-parse -q --verify "$(ref "$t")^{commit}" >/dev/null || { echo "STOP $t is not a branch here"; exit 1; }; done
  [ "$(ref "$base")" = "$D" ] || git merge-base --is-ancestor "$D" "$(ref "$base")" || { echo "STOP $base does not hold $D, so $pr must target it with $base merged in"; exit 1; }
  wt=$(pwd) head=$(git rev-parse HEAD) tips=$(for b in "$base" $(list "$extra"); do ref "$b"; done)
  [ ${#new_c[@]} = 0 ] || new_c=($(git rev-list --no-merges --no-walk=unsorted "${new_c[@]}"))
  mine=($(own "$head" "$D" "$base" $(list "$extra") $(list "$merged")) "${new_c[@]}")
  accounted HEAD $tips $(refs "$merged") $(pins "$pr"); cp "$W/acc" "$W/held"; [ ${#new_c[@]} = 0 ] || printf '%s\n' "${new_c[@]}" >> "$W/acc"
  stale "$D" $(refs "$extra") $(outside "$base") || exit 1
  paths $(git rev-list --first-parent --no-merges "$PH" "^$D") > "$W/pp"
  for x in $(paths "${mine[@]}" | grep -v -x -F -f "$W/pp"); do
    dev=($(devs "$pr" "$head" "$D" "$base" $(list "$extra") $(list "$merged"))); [ ${#dev[@]} = 0 ] || { echo "DEVELOPER-COMMITS $pr $(printf '%s ' "${dev[@]}")"; exit 1; }
    echo "STOP $pr would carry $x, which the phase does not change"; exit 1; done
  [ ${#new_c[@]} = 0 ] || carry "${new_c[@]}" || { git reset -q --hard "$head"; echo "STOP the branch is back at $head"; exit 1; }
  mine=($(own HEAD "$D" "$base" $(list "$extra") $(list "$merged"))); accounted HEAD $tips $(refs "$merged") $(pins "$pr")
  at "$(ref "$base")" && merge_in $(echo "$tips" | sed 1d) && overlay "${mine[@]}" || { done_at "$wt"; git reset -q --hard "$head"; exit 1; }
  t=$(git write-tree); done_at "$wt"
  new=$(for x in $tips; do git merge-base --is-ancestor "$x" HEAD || echo "$x"; done)
  if [ -n "$new" ] || ! same "$t" HEAD; then
    m=$(git commit-tree "$t" -p HEAD $(for x in ${new:-$(echo "$tips" | head -1)}; do printf -- '-p\n%s\n' "$x"; done) -m "Merge $(echo $tips) into $pr" -m "(s-stack refresh)") && git merge -q --ff-only "$m" || exit 1
    echo "merged $m"
  else echo "up to date with $(echo $tips)"; fi
}
deps_of() { local s b e x m; for s in "${specs[@]}"; do IFS=: read -r b e x m <<< "$s"; [ "${b#origin/}" = "${1#origin/}" ] && { echo "${e#origin/}"; list "$x,$m" | sed 's,^origin/,,'; }; done; }
hd() { grep -q -x -F -- "${1#origin/}" "$W/landed" && git rev-parse -q --verify "refs/remotes/origin/${1#origin/}" >/dev/null && echo "origin/${1#origin/}" || echo "$1"; }
above() { local d; for d in $(deps_of "$1"); do { [ "$d" = "${2#origin/}" ] || above "$d" "$2"; } && return 0; done; return 1; }
prove() {
  local orch=$1 fail=0 top s c f l t x o i b v m p n h deps landed lp dev; setup "$2" "$3"; shift 3; specs=("$@") top=$(pwd)
  spec() {
    IFS=: read -r pr base extra merged <<< "$1"; n=${pr#origin/} lp=
    { echo "$landed" | grep -q -x -F -- "$n" || git merge-base --is-ancestor "$pr" "$D"; } && lp=1 && echo "$n" >> "$W/landed" && pr=$(hd "$pr")
    mine=($(own "$pr" "$D" "$base" $(list "$extra") $(list "$merged")))
  }
  deps=$(for s; do IFS=: read -r _ b x m <<< "$s"; ref "$b"; refs "$x"; refs "$m"; done)
  landed=$( { for s; do IFS=: read -r _ _ _ m <<< "$s"; list "$m"; done; list "${MERGED:-}"; } | sed 's,^origin/,,'); : > "$W/landed"
  git rev-list --first-parent "$orch" > "$W/ofp"
  paths $(git rev-list --first-parent --no-merges "$PH" "^$D") > "$W/pp"
  for m in $(git rev-list --first-parent --merges "$PH" "^$D" | grep -v -x -F -f "$W/ofp"); do
    for p in $(git rev-parse "$m^@" | sed 1d); do
      grep -q -x -F "$p" "$W/ofp" && continue
      for b in "$D" $deps; do git merge-base --is-ancestor "$p" "$b" && continue 2; done
      echo "FAIL $(git log -1 --format='%h %s' "$m") merges $(git rev-parse --short "$p"), whose commits are not phase commits: a delegate's branch merged into the phase"; fail=1
    done
    t=$(git merge-tree --write-tree "$m^1" "$m^2" 2>/dev/null | head -1)
    [ -n "$t" ] || { echo "FAIL $(git log -1 --format='%h %s' "$m") cannot be merged again to check it for edits"; fail=1; continue; }
    for x in $(edits "$t" "$m"); do
      grep -q -x -F -- "$x" "$W/pp" && ! foreign "$x" && continue
      echo "FAIL $(git log -1 --format='%h %s' "$m") edits $x inside the merge, so no pull request carries the edit"; fail=1
    done
  done
  for s; do
    spec "$s"; paths "${mine[@]}" > "$W/own.${n//\//_}"
    echo "$n:$(git diff --shortstat "$(ref "$base")...$pr" -- . "${GEN[@]}")"
    for c in ${mine[@]}; do ! git merge-base --is-ancestor "$c" "$orch" || { echo "FAIL $pr: $c is already on $orch, so its pull request is an undeclared dependency"; fail=1; }; done
    [ -n "$lp" ] || for x in $(grep -v -x -F -f "$W/pp" "$W/own.${n//\//_}"); do echo "FAIL $pr: it changes $x, which the phase does not"; fail=1; done
    for c in $(git rev-list --no-merges "$pr" $(not "$D" "$base" $(list "$extra") $(list "$merged")) --grep="$REGEN"); do
      for f in $(git diff-tree --no-commit-id --name-only -r "$c" -- . "${GEN[@]}" "${LINES[@]}"); do echo "FAIL $pr: regenerate commit $c changes $f"; fail=1; done
      l=$(only_lines "$c^" "$c"); [ -z "$l" ] || { echo "FAIL $pr: regenerate commit $c changes $l"; fail=1; }
    done
    for f in $(git diff --name-only "$D...$pr" -- .foundry); do echo "FAIL $pr: contains $f"; fail=1; done
    [ -n "$lp" ] && continue
    accounted "$pr" $(refs "$merged") $(pins "$n")
    h=$pr; git rev-parse -q --verify "refs/remotes/origin/$n" >/dev/null && h=origin/$n
    pushed_here "$n" || fail=1
    dev=($(devs "$n" "$h" "$D" "$base" $(list "$extra") $(list "$merged"))); [ ${#dev[@]} = 0 ] || { echo "DEVELOPER-COMMITS $pr $(printf '%s ' "${dev[@]}")"; fail=1; }
    at "$(git merge-base "$(ref "$base")" "$pr")"
    merge_in $(for e in $(list "$extra"); do git merge-base "$(ref "$e")" "$pr"; done) && overlay "${mine[@]}" && t=$(git write-tree) || t=
    done_at "$top"
    [ -n "$t" ] && same "$t" "$pr" || { [ -z "$t" ] || git diff --stat "$t" "$pr" -- . "${GEN[@]}" "${LINES[@]}"; echo "FAIL $pr: its head differs from its target tree"; fail=1; }
  done
  for x in $(cat "$W/pp"); do
    l=; [ "$(ver "$PH" "$x")" = "$(ver "$D" "$x")" ] && l=1
    o=(); for s; do IFS=: read -r pr _ <<< "$s"; n=${pr#origin/}; grep -q -x -F -- "$x" "$W/own.${n//\//_}" || continue
      [ -n "$l" ] || ! grep -q -x -F -- "$n" "$W/landed" || [ "$(ver "$(hd "$pr")" "$x")" = "$(ver "$PH" "$x")" ] && o+=("$pr"); done
    [ ${#o[@]} -gt 0 ] || [ -z "$l" ] || continue
    [ ${#o[@]} -gt 0 ] || { accounted $(for n in $(cat "$W/landed"); do hd "$n"; done)
      if unacc "$x"; then echo "FAIL $x has not landed and is in no open pull request, so it needs a new pull request"
      else echo "FAIL $x differs between the phase and $D and no open pull request holds it: if the phase changed it, open a pull request for its commits; if $D changed it, for example a developer commit on a merged pull request, merge $D into the phase"; fi; fail=1; continue; }
    t=${o[0]}; for i in "${o[@]}"; do above "$i" "$t" && t=$i; done
    for i in "${o[@]}"; do [ "$i" = "$t" ] || above "$t" "$i" || { echo "FAIL $x is in $i and $t, which are not in one stack"; fail=1; continue 2; }; done
    for s; do IFS=: read -r pr base _ merged <<< "$s"; [ "$pr" = "$t" ] && accounted "$(hd "$pr")" $(refs "$merged") $(pins "$pr") && b=$base; done
    if unacc "$x" && [ "$(ver "$(hd "$t")" "$x")" != "$(ver "$PH" "$x")" ]; then echo "FAIL $x: $t lacks phase commits $(git rev-list --first-parent --no-merges "$PH" "^$D" -- ":(literal)$x" | grep -v -x -F -f "$W/acc" | git log --stdin --no-walk=unsorted --format='%h %s' | tr '\n' ';'), so they need a pull request"; fail=1
    elif [ -n "$l" ] && ! grep -q -x -F -- "${t#origin/}" "$W/landed" && v=$(ver "$t" "$x") && [ "$v" != "$(ver "$PH" "$x")" ] && [ "$v" != "$(ver "$(ref "$b")" "$x")" ]; then echo "FAIL $x: $t holds a version that is neither the phase's nor $b's"; fail=1; fi
  done
  [ "$fail" = 0 ] || { echo "NOT EQUAL"; exit 1; }
  echo EQUAL
  for s; do IFS=: read -r pr _ <<< "$s"; n=${pr#origin/}
    if grep -s -q -x -F -- "$n" "$W/landed"; then entries "$n"
    else h=$(git rev-parse "$pr"); for p in $(entries "$n"); do git merge-base --is-ancestor "$p" "$h" || echo "$p"; done; echo "$h"; fi | sed "s|^|$n=|"
  done | paste -s -d , - | sed 's/^/RECORD /'
}
case ${1:-} in
  refresh | prove) "$@" ;;
  *) echo "usage: bash pr.sh refresh|prove ..."; exit 2 ;;
esac
```
