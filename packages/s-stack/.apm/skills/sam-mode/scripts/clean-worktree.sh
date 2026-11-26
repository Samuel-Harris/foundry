#!/usr/bin/env bash
# Kept to Bash 3.2 features, because that is what macOS ships at /bin/bash.
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage:
  clean-worktree.sh <worktree> <merged-into>

Run it in the repository that owns <worktree>. It removes a worktree whose work
is finished, with the Docker Compose projects started from it, the linked
worktrees of any repository nested inside it, and its branch. <merged-into> is
the ref that must contain the worktree's HEAD and branch, such as the feature
branch.

It refuses, and changes nothing, when any of these holds:
  - <worktree> is not a linked worktree of this repository
  - a process has its working directory in or under it
  - it or a nested worktree has uncommitted or untracked changes
  - its HEAD or branch is not merged into <merged-into>
  - a nested worktree's HEAD is on no remote branch, nor, for a worktree of
    this repository, in <merged-into>
  - it holds a git repository or a submodule, whose work would go with it

Standard output is one line per removal:
  stopped <compose project>   removed its containers, volumes, networks and built images
  removed <worktree path>     removed a worktree, and its branch when it had one

Exit codes:
  1  any other failure, named on standard error
  2  bad arguments
  3  git or lsof is not on PATH
  5  refused, with the reason on standard error
EOF
  exit 2
}

[ $# -eq 2 ] || usage
for tool in git lsof; do
  type -P "$tool" >/dev/null 2>&1 || { printf 'clean-worktree.sh: %s not found on PATH\n' "$tool" >&2; exit 3; }
done

worktree=$(cd "$1" 2>/dev/null && pwd -P) || worktree=''
merged_into=$2
label=$(basename "${worktree:-$1}")

refuse() {
  printf 'refused %s: %s\n' "$label" "$1" >&2
  exit 5
}

die() {
  printf 'clean-worktree.sh: %s\n' "$*" >&2
  exit 1
}

under() {
  [ "$1" = "$worktree" ] || [ "${1#"$worktree"/}" != "$1" ]
}

# Paths in porcelain output are physical only when git was given physical
# paths, so resolve each one before comparing.
registered_worktrees() {
  git worktree list --porcelain | awk '/^worktree / { print substr($0, 10) }' | while IFS= read -r path; do
    (cd "$path" 2>/dev/null && pwd -P) || true
  done
}

[ -n "$worktree" ] || refuse 'no such directory'
git rev-parse --verify --quiet "$merged_into^{commit}" >/dev/null || die "$merged_into is not a commit"
registered=$(registered_worktrees)
main_worktree=$(printf '%s\n' "$registered" | head -n 1)
printf '%s\n' "$registered" | grep -qxF "$worktree" || refuse 'not a worktree of this repository'
[ "$worktree" != "$main_worktree" ] || refuse 'the main worktree'

busy=$(lsof -a -d cwd -F pn 2>/dev/null | awk -v root="$worktree" '
  /^p/ { pid = substr($0, 2) }
  /^n/ { path = substr($0, 2); if (path == root || index(path, root "/") == 1) print pid }
' | sort -un | tr '\n' ' ') || true
[ -z "$busy" ] || refuse "processes ${busy% } have their working directory in it"

check_clean() {
  local dirty
  dirty=$(git -C "$1" status --porcelain) || die "git -C $1 status failed"
  [ -z "$dirty" ] || refuse "uncommitted changes in $1"
}

branch_of() {
  git -C "$1" symbolic-ref --quiet --short HEAD || true
}

git_path() {
  local path
  path=$(git -C "$1" rev-parse --path-format=absolute "$2") || die "git -C $1 rev-parse $2 failed"
  (cd "$path" && pwd -P)
}

check_clean "$worktree"
git -C "$worktree" merge-base --is-ancestor HEAD "$merged_into" || refuse "HEAD of $worktree not merged into $merged_into"
branch=$(branch_of "$worktree")
if [ -n "$branch" ]; then
  git merge-base --is-ancestor "$branch" "$merged_into" || refuse "branch $branch not merged into $merged_into"
fi
own_common=$(git_path . --git-common-dir)

# A clean worktree can hide another checkout only where git ignores files.
# Listing ignored files names each checkout there as one "<dir>/" entry, and
# git does not descend into it, so each nested worktree is listed in turn.
nested_checkouts() {
  git -C "$1" ls-files -z --others --ignored --exclude-standard | tr '\0' '\n' | { grep '/$' || true; } | while IFS= read -r entry; do
    (cd "$1/$entry" && pwd -P)
  done
}

# Each line is <depth> <tab> <path> <tab> <common dir>, for removal deepest first.
nested=''
queue=$(nested_checkouts "$worktree") || die "cannot list the checkouts nested in $worktree"
while [ -n "$queue" ]; do
  holder=${queue%%
*}
  if [ "$holder" = "$queue" ]; then queue=''; else queue=${queue#*
}; fi
  [ -f "$holder/.git" ] || refuse "it holds a git repository at $holder"
  common=$(git_path "$holder" --git-common-dir)
  [ "$(dirname "$(git_path "$holder" --git-dir)")" = "$common/worktrees" ] || refuse "it holds a submodule at $holder"
  check_clean "$holder"
  if [ "$common" = "$own_common" ]; then
    [ -z "$(git -C "$holder" rev-list -n 1 HEAD --not "$merged_into" --remotes)" ] \
      || refuse "nested worktree $holder has commits in neither $merged_into nor a remote branch"
  else
    [ -z "$(git -C "$holder" rev-list -n 1 HEAD --not --remotes)" ] \
      || refuse "nested worktree $holder has commits on no remote branch"
  fi
  nested="$nested$(printf '%s' "$holder" | tr -cd / | wc -c | tr -d ' ')	$holder	$common
"
  deeper=$(nested_checkouts "$holder") || die "cannot list the checkouts nested in $holder"
  [ -z "$deeper" ] || queue=$(printf '%s\n%s' "$deeper" "$queue" | sed '/^$/d')
done

# Compose labels each container with the directory its project was started
# from, and a file-less down finds the rest of the project by its label.
if type -P docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
  projects=$(docker ps -a --format '{{.Label "com.docker.compose.project"}}	{{.Label "com.docker.compose.project.working_dir"}}' \
    | while IFS='	' read -r project dir; do
      [ -n "$project" ] && [ -n "$dir" ] || continue
      dir=$( (cd "$dir" 2>/dev/null && pwd -P) || true)
      [ -n "$dir" ] && under "$dir" && printf '%s\n' "$project"
    done | sort -u) || true
  while IFS= read -r project; do
    [ -n "$project" ] || continue
    docker compose -p "$project" down --volumes --rmi local --remove-orphans >&2 || die "docker compose -p $project down failed"
    printf 'stopped %s\n' "$project"
  done <<EOF
$projects
EOF
else
  printf 'clean-worktree.sh: Docker is not running, so no compose project was stopped\n' >&2
fi

# A branch goes only when its work survives elsewhere: merged into
# <merged-into>, for this repository, or pushed.
remove_worktree() {
  local path=$1 common=$2 path_branch
  path_branch=$(branch_of "$path")
  git --git-dir="$common" worktree remove "$path" >&2 || die "git worktree remove $path failed"
  [ -n "$path_branch" ] || { printf 'removed %s\n' "$path"; return; }
  if { [ "$common" = "$own_common" ] && git merge-base --is-ancestor "$path_branch" "$merged_into"; } \
     || [ -z "$(git --git-dir="$common" rev-list -n 1 "$path_branch" --not --remotes)" ]; then
    git --git-dir="$common" branch -D "$path_branch" >&2 || die "git branch -D $path_branch failed"
  fi
  printf 'removed %s\n' "$path"
}

printf '%s' "$nested" | sort -t '	' -k1,1rn | while IFS='	' read -r _ path common; do
  remove_worktree "$path" "$common"
done
remove_worktree "$worktree" "$own_common"
