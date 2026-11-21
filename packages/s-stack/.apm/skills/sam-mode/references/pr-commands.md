# PR creator commands

This file holds the script the PR creator runs. `handbooks/pr-creator.md` says when to run each command. Copy the block at the end of this file, exactly as it stands, into a file outside the repository, such as `pr.sh` in your scratch directory. Set its parameter lines once, then run it with `bash` from a worktree of the repository. It needs bash and git 2.43 or later.

```text
bash pr.sh refresh <default branch> <spec> [<commit> ...]
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

A repository with no generated files sets `GEN=()` and `LINES=()`, sets `LINES_IN` to a path that does not exist, and sets `REGEN` and `GEN_LINE` to patterns that nothing matches.

## Specs

Both commands describe a pull request as `<pr>:<base>[:<open deps>[:<merged deps>]]`.

- `<pr>` is the pull request's branch.
- `<base>` is the branch the pull request targets on GitHub: the parent's branch when it is stacked, otherwise the default branch.
- `<open deps>` lists, with commas, the branches of the open dependencies merged into a pull request that targets the default branch.
- `<merged deps>` lists the branches of dependencies that have merged into the default branch, squash-merged or not. Their branch refs must stay, because they keep those commits out of the pull request's own commits.

| Spec | Pull request |
| --- | --- |
| `pr1:main` | No open dependency |
| `pr2:pr1` | Stacked on `pr1` |
| `pr3:main:pr1,pr2` | Targets `main` and carries `pr1` and `pr2` |
| `pr2:main::pr1` | `pr1` was squash-merged into `main` |

A branch may be written `main` or `origin/main`. The script uses `origin/<branch>` whenever that ref exists, so push a parent before its child reads it. A pull request's own commits are the commits reachable from its branch and from none of the default branch, its base and its dependencies, leaving out merges and regenerate commits.

## Refresh a branch

`refresh` brings a pull request branch onto its base and carries new commits to it. Run it in the branch's worktree, with the branch checked out. The first build, a fix round, a moved default branch, a merged dependency, a new base and a regenerate-only round all use it.

1. In a temporary worktree at the base's tip, it merges each open dependency's tip, then replays the branch's own commits with `git apply --3way`. Before the 3-way merge of a file with generated lines, it sets the base's and the commit's generated lines to the current tree's, so a hunk next to a `version:` line still applies. A conflict in a wholly generated file keeps the base's side. Any other conflict stops the refresh.
2. When a base tip is not yet an ancestor of `HEAD`, or the rebuilt tree differs from `HEAD` outside generated files and generated lines, it records the tree on the branch as one merge commit, `git commit-tree <tree> -p HEAD -p <each new tip>`, and prints `merged <commit>`. Otherwise it prints `up to date with <tips>` and changes nothing. The merge takes the base's generated content, so a regenerate commit usually follows.
3. It carries each `<commit>` given, oldest first, as an ordinary commit with the original message and author. It leaves out merges, `.foundry/` and generated files, and skips a commit with nothing else in it.

The merge commit and the carried commits run no hook. When the refresh stops, it prints a `STOP` line naming the file or the commit, puts the branch back where it started and exits 1.

## Prove the split

`prove` runs the checks that the pull requests equal the phase. List every pull request of the phase, merged ones included, bottom of the stack first. The default branch may be given as `<default>` or `origin/<default>`.

- **The phase.** Every pull request's own commits, replayed in order onto the phase's merge base with the orchestrator branch, equal the phase head outside `.foundry/`, generated files and generated lines.
- **Each pull request.** Its head equals its own commits replayed onto its base, outside generated files and generated lines. This catches a hand edit inside a merge commit.
- **No own commit is already on the orchestrator branch.** Such a commit belongs to another pull request, so the spec is missing a dependency.
- **Regenerate commits** change only generated files and generated lines.
- **No pull request contains `.foundry/`.**

It prints each pull request's hand-written diff against its base as `git diff --shortstat` does, then `EQUAL` and exits 0, or a `FAIL` line for each fault, then `NOT EQUAL`, and exits 1. Before a `FAIL` line, a `git diff --stat` list names each file that the split dropped or added, or that a merge changed by hand.

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
only_lines() { git diff -U0 "$1" "$2" -- "$LINES_IN" | grep -E '^[-+]' | grep -v -E '^(\+\+\+|---) ' | grep -v -E "^[-+]${GEN_LINE#^}"; }
same() { git diff --quiet "$1" "$2" -- . "${GEN[@]}" "${LINES[@]}" ':(exclude).foundry' && [ -z "$(only_lines "$1" "$2")" ]; }
gen_as() { awk -v re="$GEN_LINE" 'NR == FNR { if ($0 ~ re) g[++n] = $0; next } $0 ~ re && i < n { print g[++i]; next } { print }' "$1" "$2"; }
resolve() {
  local f d; d=$(mktemp -d)
  for f in $(git diff --name-only --diff-filter=U); do
    if [ -z "$(git ls-files -- "$f" "${GEN[@]}")" ]; then git checkout --ours -- "$f" && git add -- "$f" && continue
    elif [ -z "$(git ls-files -- "$f" "${LINES[@]}")" ] && git show ":2:$f" > "$d/o" 2>/dev/null && git show ":3:$f" > "$d/t" 2>/dev/null; then
      git show ":1:$f" > "$d/b" 2>/dev/null || : > "$d/b"
      gen_as "$d/o" "$d/b" > "$d/b2" && gen_as "$d/o" "$d/t" > "$d/t2" && git merge-file -q "$d/o" "$d/b2" "$d/t2" && cat "$d/o" > "$f" && git add -- "$f" && continue
    fi
    echo "STOP $f conflicts outside generated content"; rm -rf "$d"; return 1
  done; rm -rf "$d"
}
replay() {
  local c p=(. "${GEN[@]}" ':(exclude).foundry')
  for c; do
    git diff-tree -r --quiet "$c^" "$c" -- "${p[@]}" && continue
    git diff-tree -p --binary "$c^" "$c" -- "${p[@]}" | git apply --index --3way --whitespace=nowarn 2>/dev/null ||
      { [ -n "$(git ls-files -u)" ] && resolve; } || { echo "STOP $(git log -1 --format='%h %s' "$c") does not apply"; return 1; }
    [ -z "${COMMIT:-}" ] || git diff --cached --quiet || git commit -q --no-verify -C "$c" || return 1
  done
}
merge_in() {
  local t; for t; do
    git merge -q --no-ff --no-commit "$t" >/dev/null 2>&1; git rev-parse -q --verify MERGE_HEAD >/dev/null || continue
    { [ -z "$(git ls-files -u)" ] || resolve; } && git commit -q --no-verify -m base || return 1
  done
}
at() { tmp=$(mktemp -d); git worktree add -q --detach "$tmp" "$1" && cd "$tmp"; }
done_at() { cd "$1" && git worktree remove --force "$tmp"; }
list() { echo "$1" | tr , '\n' | grep .; }
refresh() {
  local default=$1 pr base extra merged wt head tips t new m; IFS=: read -r pr base extra merged <<< "$2"; shift 2
  for t in "$base" $(list "$extra") $(list "$merged"); do git rev-parse -q --verify "$(ref "$t")^{commit}" >/dev/null || { echo "STOP $t is not a branch here"; exit 1; }; done
  wt=$(pwd) head=$(git rev-parse HEAD) tips=$(for b in "$base" $(list "$extra"); do ref "$b"; done)
  at "$(ref "$base")" && merge_in $(echo "$tips" | sed 1d) && replay $(own "$head" "$default" "$base" $(list "$extra") $(list "$merged")) || { done_at "$wt"; exit 1; }
  t=$(git write-tree); done_at "$wt"
  new=$(for x in $tips; do git merge-base --is-ancestor "$x" HEAD || echo "$x"; done)
  if [ -n "$new" ] || ! same "$t" HEAD; then
    m=$(git commit-tree "$t" -p HEAD $(for x in $new; do printf -- '-p\n%s\n' "$x"; done) -m "Merge $(echo $tips) into $pr") && git merge -q --ff-only "$m" || exit 1
    echo "merged $m"
  else echo "up to date with $(echo $tips)"; fi
  [ $# = 0 ] || COMMIT=1 replay $(git rev-list --no-merges --no-walk=unsorted "$@") || { git reset -q --hard "$head"; echo "STOP the branch is back at $head"; exit 1; }
}
prove() {
  local orch=$1 phase=$2 default=$3 fail=0 top s c f l t r; shift 3; top=$(pwd)
  spec() { IFS=: read -r pr base extra merged <<< "$1"; mine=$(own "$pr" "$default" "$base" $(list "$extra") $(list "$merged")); }
  at "$(git merge-base "$orch" "$phase")"
  for s; do
    spec "$s"
    for c in $mine; do ! git merge-base --is-ancestor "$c" "$orch" || { echo "FAIL $pr: $c is already on $orch, so its pull request is an undeclared dependency"; fail=1; }; done
    replay $mine || { echo "FAIL $pr: its own commits do not replay onto the phase"; fail=1; }
  done
  r=$(git write-tree); done_at "$top"
  same "$r" "$phase" || { git diff --stat "$r" "$phase" -- . ':(exclude).foundry' "${GEN[@]}" "${LINES[@]}"; only_lines "$r" "$phase"; echo "FAIL the pull requests differ from the phase"; fail=1; }
  for s; do
    spec "$s"
    echo "$pr:$(git diff --shortstat "$(ref "$base")...$pr" -- . "${GEN[@]}")"
    for c in $(git rev-list --no-merges "$pr" $(not "$default" "$base" $(list "$extra") $(list "$merged")) --grep="$REGEN"); do
      for f in $(git diff-tree --no-commit-id --name-only -r "$c" -- . "${GEN[@]}" "${LINES[@]}"); do echo "FAIL $pr: regenerate commit $c changes $f"; fail=1; done
      l=$(only_lines "$c^" "$c"); [ -z "$l" ] || { echo "FAIL $pr: regenerate commit $c changes $l"; fail=1; }
    done
    for f in $(git diff --name-only "$(ref "$default")...$pr" -- .foundry); do echo "FAIL $pr: contains $f"; fail=1; done
    at "$(git merge-base "$(ref "$base")" "$pr")"
    merge_in $(for e in $(list "$extra"); do git merge-base "$(ref "$e")" "$pr"; done) && replay $mine && t=$(git write-tree) || t=
    done_at "$top"
    [ -n "$t" ] && same "$t" "$pr" || { [ -z "$t" ] || git diff --stat "$t" "$pr" -- . "${GEN[@]}" "${LINES[@]}"; echo "FAIL $pr: its head differs from its own commits on its base"; fail=1; }
  done
  [ "$fail" = 0 ] && echo EQUAL || { echo "NOT EQUAL"; exit 1; }
}
case ${1:-} in
  refresh | prove) "$@" ;;
  *) echo "usage: bash pr.sh refresh|prove ..."; exit 2 ;;
esac
