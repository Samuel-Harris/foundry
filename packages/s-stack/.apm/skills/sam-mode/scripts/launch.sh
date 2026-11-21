#!/usr/bin/env bash
# Kept to Bash 3.2 features, because that is what macOS ships at /bin/bash.
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage:
  launch.sh --feature <f> --role <r> [--phase <p>] [--update <n>] [--window <window id>] [--fresh]
  launch.sh --feature <f> --role <r> [--phase <p>] [--update <n>] --close
  launch.sh --feature <f> --role <r> [--phase <p>] [--update <n>] --remove
  launch.sh --print-window

Roles: spec, orchestrator, planner, phase. --phase is required with --role phase
and refused otherwise. --update is allowed only with --role spec. --window is
required for every session except the first spec writer of a feature.
EOF
  exit 2
}

die() {
  printf 'launch.sh: %s\n' "$*" >&2
  exit 1
}

refuse() {
  printf 'refused %s: %s\n' "$name" "$1" >&2
  exit 5
}

require() {
  local command
  for command in "$@"; do
    command -v "$command" >/dev/null 2>&1 || { printf 'launch.sh: %s not found on PATH\n' "$command" >&2; exit 3; }
  done
}

kebab='^[a-z0-9]+(-[a-z0-9]+)*$'
feature='' role='' phase='' update='' window='' fresh='' close='' remove='' print_window=''
while [ $# -gt 0 ]; do
  case "$1" in
    --feature|--role|--phase|--update|--window)
      [ $# -ge 2 ] || usage
      case "$1" in
        --feature) feature=$2 ;;
        --role) role=$2 ;;
        --phase) phase=$2 ;;
        --update) update=$2 ;;
        --window) window=$2 ;;
      esac
      shift 2
      ;;
    --fresh) fresh=1; shift ;;
    --close) close=1; shift ;;
    --remove) remove=1; shift ;;
    --print-window) print_window=1; shift ;;
    *) usage ;;
  esac
done

if [ -n "$print_window" ]; then
  [ -z "$feature$role$phase$update$window$fresh$close$remove" ] || usage
  require tmux
  [ -n "${TMUX_PANE:-}" ] || die 'not inside tmux'
  printf 'window=%s\n' "$(tmux display-message -p -t "$TMUX_PANE" '#{window_id}')"
  exit 0
fi

[[ $feature =~ $kebab ]] || usage
case "$role" in spec|orchestrator|planner|phase) ;; *) usage ;; esac
if [ "$role" = phase ]; then
  [[ $phase =~ $kebab ]] || usage
else
  [ -z "$phase" ] || usage
fi
if [ -n "$update" ]; then
  [ "$role" = spec ] || usage
  [[ $update =~ ^[1-9][0-9]*$ ]] || usage
fi
if [ -n "$close" ] || [ -n "$remove" ]; then
  [ -z "$fresh$window" ] || usage
  [ -z "$close" ] || [ -z "$remove" ] || usage
fi

case "$role" in
  spec)
    if [ -n "$update" ]; then name=$feature-spec-$update; worktree_name=$name; else name=$feature-spec; worktree_name=$feature; fi ;;
  orchestrator) name=$feature-orchestrator; worktree_name=$feature ;;
  planner) name=$feature-planner; worktree_name=$name ;;
  phase) name=$feature-phase-$phase; worktree_name=$name ;;
esac
feature_worktree=''
[ "$worktree_name" != "$feature" ] || feature_worktree=1
if [ -n "$remove" ] && [ -n "$feature_worktree" ]; then usage; fi

resolve() {
  (cd "$1" 2>/dev/null && pwd -P) || true
}

# Prints "pane_id width height window_id" for each pane with a claude process
# among its descendants that matches $1. strict: started with --name $name.
# both: strict, or a claude with no --name whose pane is in $worktree, which is
# how workmux resurrect restarts a session. any: every claude.
session_panes() {
  local mode=$1 tab panes pane_id pane_pid width height path window_id resolved_worktree=''
  tab=$(printf '\t')
  panes=$(tmux list-panes -a -F "#{pane_id}${tab}#{pane_pid}${tab}#{pane_width}${tab}#{pane_height}${tab}#{pane_current_path}${tab}#{window_id}") || die 'tmux list-panes failed'
  [ "$mode" = strict ] || [ -z "$worktree" ] || resolved_worktree=$(resolve "$worktree")
  {
    printf '%s\n' "$panes" | while IFS="$tab" read -r pane_id pane_pid width height path window_id; do
      [ -n "$pane_id" ] || continue
      if [ -n "$resolved_worktree" ] && [ "$(resolve "$path")" = "$resolved_worktree" ]; then path=1; else path=0; fi
      printf 'pane %s %s %s %s %s %s\n' "$pane_id" "$pane_pid" "$width" "$height" "$window_id" "$path"
    done
    ps -A -o pid=,ppid=,args=
  } | awk -v name="$name" -v mode="$mode" '
    $1 == "pane" { pane_pid[$3] = $2; info[$2] = $2 " " $4 " " $5 " " $6; in_worktree[$2] = $7; next }
    {
      parent[$1] = $2
      program = $3; sub(/.*\//, "", program)
      if (program != "claude") next
      named = 0; strict = 0
      for (i = 4; i <= NF; i++) {
        if ($i == "--name") { named = 1; if ($(i + 1) == name) strict = 1 }
        else if (index($i, "--name=") == 1) { named = 1; if ($i == "--name=" name) strict = 1 }
      }
      claude[$1] = strict ? "strict" : (named ? "other" : "nameless")
    }
    END {
      for (pid in claude) {
        for (p = pid; p != "" && p > 1; p = parent[p]) {
          if (!(p in pane_pid)) continue
          pane = pane_pid[p]
          kind = claude[pid]
          if (mode == "any" || kind == "strict" || (mode == "both" && kind == "nameless" && in_worktree[pane] == 1)) found[pane] = 1
          break
        }
      }
      for (pane in found) print info[pane]
    }'
}

worktree=''
if [ -n "$close" ]; then
  require tmux
  matches=$(session_panes strict)
  [ -n "$matches" ] || { printf 'absent %s\n' "$name"; exit 0; }
  [ "$(printf '%s\n' "$matches" | wc -l)" -eq 1 ] || die "more than one pane runs $name: $(printf '%s\n' "$matches" | awk '{print $1}' | tr '\n' ' ')"
  pane=${matches%% *}
  tmux kill-pane -t "$pane" || die "tmux kill-pane -t $pane failed"
  printf 'closed %s pane=%s\n' "$name" "$pane"
  exit 0
fi

if [ -n "$remove" ]; then
  require workmux tmux
else
  require tmux workmux claude
fi

worktree=$(workmux path "$worktree_name" 2>/dev/null) || worktree=''

if [ -z "$remove" ] && [ -z "$window" ]; then
  [ "$role" = spec ] && [ -n "$feature_worktree" ] && [ -z "$worktree" ] || usage
fi

matches=$(session_panes both)
if [ -n "$matches" ] && [ "$(printf '%s\n' "$matches" | wc -l)" -gt 1 ]; then
  die "more than one pane runs $name: $(printf '%s\n' "$matches" | awk '{print $1}' | tr '\n' ' ')"
fi
live_pane=${matches%% *}

if [ -n "$remove" ]; then
  [ -n "$worktree" ] || refuse 'no such worktree'
  [ -z "$live_pane" ] || refuse "a live session in pane $live_pane"
  dirty=$(git -C "$worktree" status --porcelain) || die "git -C $worktree status failed"
  [ -z "$dirty" ] || refuse "dirty worktree $worktree"
  git merge-base --is-ancestor "$worktree_name" "$feature" || refuse "branch $worktree_name not merged into $feature"
  workmux remove "$worktree_name" --keep-branch --force >&2 || die "workmux remove $worktree_name failed"
  printf 'removed %s worktree=%s\n' "$name" "$worktree"
  exit 0
fi

if [ -n "$live_pane" ]; then
  printf 'alive %s pane=%s\n' "$name" "$live_pane"
  exit 0
fi

default_branch() {
  local ref
  if ref=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null); then
    printf '%s\n' "${ref#origin/}"
  elif ref=$(gh repo view --json defaultBranchRef --jq .defaultBranchRef.name 2>/dev/null) && [ -n "$ref" ]; then
    printf '%s\n' "$ref"
  else
    die 'cannot resolve the default branch: both "git symbolic-ref --short refs/remotes/origin/HEAD" and "gh repo view --json defaultBranchRef" failed'
  fi
}

target_pane=''
split=''
if [ -z "$worktree" ]; then
  if [ "$role" = orchestrator ]; then
    die "the feature worktree $feature does not exist; start the spec writer first"
  elif [ -n "$feature_worktree" ]; then
    branch=$(default_branch)
    git fetch -q origin "$branch" || die "git fetch origin $branch failed"
    windows_before=" $(tmux list-windows -a -F '#{window_id}' | tr '\n' ' ') "
    workmux add "$feature" --base "origin/$branch" -C >&2 || die "workmux add $feature failed"
  else
    workmux add "$worktree_name" --headless --base "$feature" >&2 || die "workmux add $worktree_name failed"
  fi
  worktree=$(workmux path "$worktree_name") || die "workmux path $worktree_name failed after workmux add"
  if [ -n "$feature_worktree" ]; then
    resolved_worktree=$(resolve "$worktree")
    new_windows=$(tmux list-panes -a -F '#{window_id} #{pane_current_path}' | while read -r window_id path; do
      [[ $windows_before != *" $window_id "* ]] || continue
      [ "$(resolve "$path")" != "$resolved_worktree" ] || printf '%s\n' "$window_id"
    done | sort -u)
    [ -n "$new_windows" ] && [ "$(printf '%s\n' "$new_windows" | wc -l)" -eq 1 ] || die "expected one new window for $worktree after workmux add, found: ${new_windows:-none}"
    target_pane=$(tmux list-panes -t "$new_windows" -F '#{pane_id}' | head -n 1)
  fi
fi

if [ -z "$target_pane" ]; then
  split=1
  window_panes=$(tmux list-panes -t "$window" -F '#{pane_id} #{pane_width} #{pane_height} #{window_id}') || die "tmux list-panes -t $window failed"
  candidates=$(session_panes any | awk -v window="$window" '$4 == window')
  [ -n "$candidates" ] || candidates=$window_panes
  read -r target_pane width height _ <<EOF
$(printf '%s\n' "$candidates" | awk '{ area = $2 * $3; if (area > best) { best = area; line = $0 } } END { print line }')
EOF
  if [ "$width" -gt $((2 * height)) ]; then direction=-h; else direction=-v; fi
fi

roadmap_pattern='^[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{2}-[0-9]{2}-[0-9]{2}-(.*)$'
roadmap=- plan=-
if [ -d "$worktree/.foundry/feature-roadmaps" ]; then
  found=$(cd "$worktree/.foundry/feature-roadmaps" && for entry in *; do
    [ -d "$entry" ] && [[ $entry =~ $roadmap_pattern ]] && [ "${BASH_REMATCH[1]}" = "$feature" ] && printf '%s\n' "$entry"
  done || true)
  if [ -n "$found" ]; then
    [ "$(printf '%s\n' "$found" | wc -l)" -eq 1 ] || die "more than one roadmap for $feature in $worktree/.foundry/feature-roadmaps: $(printf '%s\n' "$found" | tr '\n' ' ')"
    roadmap=.foundry/feature-roadmaps/$found
    plan=.foundry/plans/$found/README.md
  fi
fi

new_conversation_id() {
  if command -v uuidgen >/dev/null 2>&1; then
    uuidgen | tr 'A-Z' 'a-z'
  else
    cat /proc/sys/kernel/random/uuid
  fi
}

markers=$(git -C "$worktree" rev-parse --git-path s-stack-sessions) || die "git -C $worktree rev-parse failed"
case "$markers" in /*) ;; *) markers=$worktree/$markers ;; esac
marker=$markers/$name
if [ -z "$fresh" ] && [ -s "$marker" ]; then
  conversation_flag=--resume
  conversation_id=$(head -n 1 "$marker")
else
  conversation_flag=--session-id
  conversation_id=$(new_conversation_id) || die 'cannot make a conversation id: neither uuidgen nor /proc/sys/kernel/random/uuid works'
  mkdir -p "$markers" && printf '%s\n' "$conversation_id" > "$marker" || die "cannot write the session marker $marker"
fi

prompt="/sam-mode $role feature=$feature phase=${phase:--} update=${update:--} roadmap=$roadmap plan=$plan orchestrator=$feature-orchestrator"
# The trailing shell keeps the pane open after claude exits, so its last output stays visible.
command="claude --name $(printf %q "$name") $conversation_flag $(printf %q "$conversation_id") $(printf %q "$prompt"); exec \"\${SHELL:-/bin/sh}\" -l"

if [ -n "$split" ]; then
  target_pane=$(tmux split-window -d -P -F '#{pane_id}' -t "$target_pane" -c "$worktree" "$direction" "$command") || exit 4
else
  tmux respawn-pane -k -t "$target_pane" -c "$worktree" "$command" || die "tmux respawn-pane -t $target_pane failed"
fi

printf 'started %s pane=%s worktree=%s\n' "$name" "$target_pane" "$worktree"
