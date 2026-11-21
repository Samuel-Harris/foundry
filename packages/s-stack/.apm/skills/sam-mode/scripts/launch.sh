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

Features and phases are kebab-case. A feature name may not contain -phase- or
end with -phase, -planner, -orchestrator, -spec or -spec-<n>, because another
feature's session could have that name.

Standard output is one line:
  started <name> pane=<pane id> worktree=<path>   started the session
  alive <name> pane=<pane id>                     the session already runs; nothing changed
  closed <name> pane=<pane id>                    --close closed the session's pane
  absent <name>                                   --close found no pane running the session
  removed <name> worktree=<path>                  --remove removed the session's worktree
  window=<window id>                              --print-window

Exit codes:
  1  any other failure, named on standard error
  2  bad arguments
  3  tmux, workmux or claude is not on PATH
  4  tmux could not split a pane; tmux's error is on standard error
  5  --remove refused: no such worktree, a claude running in or under it or
     under the session's name, a dirty worktree, or a branch or HEAD not merged
     into the feature
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

cannot_split() {
  exit 4
}

require() {
  local tool
  for tool in "$@"; do
    command -v "$tool" >/dev/null 2>&1 || { printf 'launch.sh: %s not found on PATH\n' "$tool" >&2; exit 3; }
  done
}

at_most_one() {
  [ "$(printf '%s\n' "$2" | wc -l)" -le 1 ] || die "more than one $1: $(printf '%s\n' "$2" | awk '{print $1}' | tr '\n' ' ')"
}

kebab='^[a-z0-9]+(-[a-z0-9]+)*$'
feature='' role='' phase='' update='' window='' fresh='' mode=start
set_mode() {
  [ "$mode" = start ] || usage
  mode=$1
}
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
    --close) set_mode close; shift ;;
    --remove) set_mode remove; shift ;;
    --print-window) set_mode print-window; shift ;;
    *) usage ;;
  esac
done

if [ "$mode" = print-window ]; then
  [ -z "$feature$role$phase$update$window$fresh" ] || usage
else
  [[ $feature =~ $kebab ]] || usage
  case "$feature" in *-phase-*|*-phase|*-planner|*-orchestrator|*-spec) usage ;; esac
  [[ ! $feature =~ -spec-[0-9]+$ ]] || usage
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
  if [ "$mode" != start ]; then
    [ -z "$fresh$window" ] || usage
  fi

  case "$role" in
    spec)
      if [ -n "$update" ]; then name=$feature-spec-$update; worktree_name=$name; else name=$feature-spec; worktree_name=$feature; fi ;;
    orchestrator) name=$feature-orchestrator; worktree_name=$feature ;;
    planner) name=$feature-planner; worktree_name=$name ;;
    phase) name=$feature-phase-$phase; worktree_name=$name ;;
  esac
  first_spec=''
  if [ "$role" = spec ] && [ -z "$update" ]; then first_spec=1; fi
  if [ "$mode" = remove ] && [ "$worktree_name" = "$feature" ]; then usage; fi
fi

resolve() {
  (cd "$1" 2>/dev/null && pwd -P) || true
}

# Prints "pane_id width height window_id kind in_worktree" for each pane with a
# claude process among its descendants. kind is strict when that claude's first
# argument is --name <name>, as the launcher writes it, so a --name inside a
# prompt never matches. It is nameless when no argument is --name, which is how
# workmux resurrect restarts a session, and other otherwise. A pane running
# several claudes reports the closest match. in_worktree is 1 when the pane's
# directory is <worktree> or under it.
session_panes() {
  local session=$1 worktree_path=$2 panes pane_id pane_pid width height current_path window_id in_worktree resolved_worktree=''
  # Spaces, not tabs, separate the fields: a tmux client without a UTF-8 locale
  # prints a tab in a format as "_". The path goes last so read keeps its spaces.
  if ! panes=$(tmux list-panes -a -F '#{pane_id} #{pane_pid} #{pane_width} #{pane_height} #{window_id} #{pane_current_path}'); then
    # With no server no session runs, which --close and --remove may rely on; start mode needs a window.
    [ "$mode" != start ] && [[ $(tmux list-sessions 2>&1) == 'no server running'* ]] || die 'tmux list-panes failed'
    panes=''
  fi
  [ -z "$worktree_path" ] || resolved_worktree=$(resolve "$worktree_path")
  {
    printf '%s\n' "$panes" | while read -r pane_id pane_pid width height window_id current_path; do
      [ -n "$pane_id" ] || continue
      in_worktree=0
      if [ -n "$resolved_worktree" ] && [[ "$(resolve "$current_path")/" == "$resolved_worktree"/* ]]; then in_worktree=1; fi
      printf 'pane %s %s %s %s %s %s\n' "$pane_id" "$pane_pid" "$width" "$height" "$window_id" "$in_worktree"
    done
    ps -A -o pid=,ppid=,args=
  } | awk -v name="$session" '
    $1 == "pane" { pane_pid[$3] = $2; info[$2] = $2 " " $4 " " $5 " " $6; in_worktree[$2] = $7; next }
    {
      parent[$1] = $2
      program = $3; sub(/.*\//, "", program)
      if (program != "claude") next
      strict = ($4 == "--name" && $5 == name) || $4 == "--name=" name
      named = 0
      for (i = 4; i <= NF; i++) if ($i == "--name" || index($i, "--name=") == 1) named = 1
      claude[$1] = strict ? "strict" : (named ? "other" : "nameless")
    }
    END {
      rank["other"] = 1; rank["nameless"] = 2; rank["strict"] = 3
      for (pid in claude) {
        for (p = pid; p != "" && p > 1; p = parent[p]) {
          if (!(p in pane_pid)) continue
          pane = pane_pid[p]
          if (rank[claude[pid]] > rank[kind[pane]]) kind[pane] = claude[pid]
          break
        }
      }
      for (pane in kind) print info[pane], kind[pane], in_worktree[pane]
    }'
}

find_live_pane() {
  local matches resumed=1
  # workmux resurrect restores only the orchestrator, and the spec writer has
  # ended by then, so a nameless claude in the feature worktree is the orchestrator.
  [ -z "$first_spec" ] || resumed=0
  matches=$(session_panes "$name" "$worktree" | awk -v resumed="$resumed" '$5 == "strict" || (resumed && $5 == "nameless" && $6 == 1)')
  at_most_one "pane runs $name" "$matches"
  live_pane=${matches%% *}
}

# Held until the launcher exits, so a concurrent launch of the same session
# checks liveness only after ps shows this one's claude.
lock_session() {
  local common tries=0
  common=$(resolve "$(git rev-parse --git-common-dir)")
  [ -n "$common" ] || die 'cannot resolve the git common directory'
  lock=$common/s-stack-locks/$name
  mkdir -p "$common/s-stack-locks" || die "cannot create $common/s-stack-locks"
  until mkdir "$lock" 2>/dev/null; do
    tries=$((tries + 1))
    [ "$tries" -lt 100 ] || die "another launch of $name has held $lock for 10 seconds; if none is running, remove that directory"
    sleep 0.1
  done
  trap 'rmdir "$lock"' EXIT
}

# A claude shows in ps a moment after its pane opens.
wait_for_started_claude() {
  local tries=0
  until session_panes "$name" '' | awk -v pane="$target_pane" '$1 == pane && $5 == "strict" { found = 1 } END { exit !found }'; do
    tries=$((tries + 1))
    [ "$tries" -lt 100 ] || return 0
    sleep 0.1
  done
}

# Sets target_pane, direction and split_size for a session started by splitting
# a pane of $window. The orchestrator holds the first column after the workmux
# sidebar, spec writers stack in its column and every other session goes to its
# right. A pane without the @s-stack-session tag belongs to the developer or to
# workmux and is never split, except the orchestrator's pane, which a resurrect
# leaves untagged, and the first column's top pane when the orchestrator starts
# with no spec writer.
choose_split() {
  local panes feature_worktree orchestrator_pane='' spec_pane='' choice
  # Spaces separate the fields, as in session_panes, and the command goes last.
  panes=$(tmux list-panes -t "$window" -F '#{pane_id} #{pane_left} #{pane_right} #{pane_top} #{pane_width} #{pane_height} #{?@s-stack-session,#{@s-stack-session},-} #{pane_current_command}') || die "tmux list-panes -t $window failed"
  if [ "$role" = orchestrator ]; then
    spec_pane=$(session_panes "$feature-spec" '' | awk '$5 == "strict"')
    at_most_one "pane runs $feature-spec" "$spec_pane"
    spec_pane=${spec_pane%% *}
  else
    feature_worktree=$(workmux path "$feature" 2>/dev/null) || feature_worktree=''
    orchestrator_pane=$(session_panes "$feature-orchestrator" "$feature_worktree" | awk '$5 == "strict" || ($5 == "nameless" && $6 == 1)')
    at_most_one "pane runs $feature-orchestrator" "$orchestrator_pane"
    orchestrator_pane=${orchestrator_pane%% *}
  fi
  choice=$(printf '%s\n' "$panes" | awk -v role="$role" -v feature="$feature" -v orchestrator="$orchestrator_pane" -v spec="$spec_pane" -v first_spec="$first_spec" '
    {
      n++
      id[n] = $1; left[n] = $2; right[n] = $3; top[n] = $4; width[n] = $5; height[n] = $6; tag[n] = $7
      sidebar[n] = NF == 8 && $8 == "workmux"
      if ($1 == orchestrator) o = n
      if ($1 == spec) s = n
    }
    function first_column_top(   i, best) {
      for (i = 1; i <= n; i++) {
        if (sidebar[i]) continue
        if (!best || left[i] < left[best] || (left[i] == left[best] && top[i] < top[best])) best = i
      }
      return best ? id[best] " -v" : "none"
    }
    END {
      if (role == "orchestrator") { print s ? id[s] " -v" : first_column_top(); exit }
      if (!o) { print (role == "spec" && first_spec) ? first_column_top() : "no-orchestrator"; exit }
      if (role == "spec") {
        best = 0
        for (i = 1; i <= n; i++) {
          if (left[i] < left[o] || right[i] > right[o]) continue
          if (i != o && tag[i] != feature "-spec" && tag[i] !~ ("^" feature "-spec-[0-9]+$")) continue
          if (!best || top[i] > top[best]) best = i
        }
        print id[best] " -v"
        exit
      }
      best = 0
      for (i = 1; i <= n; i++) {
        if (tag[i] == "-" || left[i] <= right[o]) continue
        if (!best || width[i] * height[i] > width[best] * height[best]) best = i
      }
      # Each -l keeps the orchestrator at least as wide as the new pane: the
      # divider takes one column of the orchestrator pane.
      if (!best) print id[o] " -h " int((width[o] - 1) / 2)
      else print id[best] " " (width[best] >= 161 ? "-h" : "-v")
    }')
  case "$choice" in
    none) die "no pane to split in $window" ;;
    no-orchestrator) die "no $feature-orchestrator pane in $window" ;;
  esac
  read -r target_pane direction split_size <<EOF
$choice
EOF
}

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

new_conversation_id() {
  if command -v uuidgen >/dev/null 2>&1; then
    uuidgen | tr 'A-Z' 'a-z'
  else
    cat /proc/sys/kernel/random/uuid
  fi
}

cmd_print_window() {
  require tmux
  local window_id
  [ -n "${TMUX_PANE:-}" ] || die 'not inside tmux'
  window_id=$(tmux display-message -p -t "$TMUX_PANE" '#{window_id}') && [ -n "$window_id" ] || die "no window for pane $TMUX_PANE"
  printf 'window=%s\n' "$window_id"
}

cmd_close() {
  require tmux
  local matches pane
  matches=$(session_panes "$name" '' | awk '$5 == "strict"')
  [ -n "$matches" ] || { printf 'absent %s\n' "$name"; return; }
  at_most_one "pane runs $name" "$matches"
  pane=${matches%% *}
  tmux kill-pane -t "$pane" || die "tmux kill-pane -t $pane failed"
  printf 'closed %s pane=%s\n' "$name" "$pane"
}

cmd_remove() {
  require workmux tmux
  local claudes dirty
  worktree=$(workmux path "$worktree_name" 2>/dev/null) || refuse 'no such worktree'
  claudes=$(session_panes "$name" "$worktree" | awk '$5 == "strict" || $6 == 1')
  [ -z "$claudes" ] || refuse "a live session in pane ${claudes%% *}"
  dirty=$(git -C "$worktree" status --porcelain) || die "git -C $worktree status failed"
  [ -z "$dirty" ] || refuse "dirty worktree $worktree"
  git merge-base --is-ancestor "$worktree_name" "$feature" || refuse "branch $worktree_name not merged into $feature"
  git -C "$worktree" merge-base --is-ancestor HEAD "$feature" || refuse "HEAD of $worktree not merged into $feature"
  workmux remove "$worktree_name" --keep-branch --force >&2 || die "workmux remove $worktree_name failed"
  printf 'removed %s worktree=%s\n' "$name" "$worktree"
}

cmd_start() {
  require tmux workmux claude
  worktree=$(workmux path "$worktree_name" 2>/dev/null) || worktree=''
  if [ -z "$window" ]; then
    [ -n "$first_spec" ] && [ -z "$worktree" ] || usage
  fi

  lock_session
  find_live_pane
  if [ -n "$live_pane" ]; then
    printf 'alive %s pane=%s\n' "$name" "$live_pane"
    return
  fi

  target_pane=''
  split=''
  if [ -z "$worktree" ]; then
    if [ "$role" = orchestrator ]; then
      die "the feature worktree $feature does not exist; start the spec writer first"
    elif [ -n "$first_spec" ]; then
      branch=$(default_branch)
      git fetch -q origin "$branch" || die "git fetch origin $branch failed"
      windows_before=" $(tmux list-windows -a -F '#{window_id}' | tr '\n' ' ') "
      # workmux resurrect restores only sessions that ran in their worktree's own workmux window.
      workmux add "$feature" --base "origin/$branch" -C >&2 || die "workmux add $feature failed"
    else
      workmux add "$worktree_name" --headless --base "$feature" >&2 || die "workmux add $worktree_name failed"
    fi
    worktree=$(workmux path "$worktree_name") || die "workmux path $worktree_name failed after workmux add"
    if [ -n "$first_spec" ]; then
      resolved_worktree=$(resolve "$worktree")
      new_windows=$(tmux list-panes -a -F '#{window_id} #{pane_current_path}' | while read -r window_id path; do
        [[ $windows_before != *" $window_id "* ]] || continue
        if [[ "$(resolve "$path")/" == "$resolved_worktree"/* ]]; then printf '%s\n' "$window_id"; fi
      done | sort -u)
      [ -n "$new_windows" ] || die "no new window for $worktree after workmux add"
      at_most_one "new window for $worktree after workmux add" "$new_windows"
      target_pane=$(tmux list-panes -t "$new_windows" -F '#{pane_id}' | head -n 1)
    fi
  fi

  if [ -z "$target_pane" ]; then
    split=1
    choose_split
    # split-window unzooms a zoomed window unless given -Z, which zooms an unzoomed one.
    zoom=''
    if [ "$(tmux display-message -p -t "$target_pane" '#{window_zoomed_flag}')" = 1 ]; then zoom=-Z; fi
  fi

  roadmap_pattern='^[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{2}-[0-9]{2}-[0-9]{2}-(.*)$'
  roadmap=- plan=-
  if [ -d "$worktree/.foundry/feature-roadmaps" ]; then
    found=$(cd "$worktree/.foundry/feature-roadmaps" && for entry in *; do
      [ -d "$entry" ] && [[ $entry =~ $roadmap_pattern ]] && [ "${BASH_REMATCH[1]}" = "$feature" ] && printf '%s\n' "$entry"
    done || true)
    if [ -n "$found" ]; then
      at_most_one "roadmap for $feature in $worktree/.foundry/feature-roadmaps" "$found"
      roadmap=.foundry/feature-roadmaps/$found
      plan=.foundry/plans/$found/README.md
    fi
  fi

  markers=$(git -C "$worktree" rev-parse --git-path s-stack-sessions) || die "git -C $worktree rev-parse failed"
  case "$markers" in /*) ;; *) markers=$worktree/$markers ;; esac
  marker=$markers/$name
  if [ -z "$fresh" ] && [ -s "$marker" ]; then
    conversation_flag=--resume
    conversation_id=$(head -n 1 "$marker")
  else
    conversation_flag=--session-id
    conversation_id=$(new_conversation_id) || die 'cannot make a conversation id: neither uuidgen nor /proc/sys/kernel/random/uuid works'
  fi

  prompt="/sam-mode $role feature=$feature phase=${phase:--} update=${update:--} roadmap=$roadmap plan=$plan orchestrator=$feature-orchestrator"
  # The trailing shell keeps the pane open after claude exits, so its last output stays visible.
  pane_command="claude --name $(printf %q "$name") $conversation_flag $(printf %q "$conversation_id") $(printf %q "$prompt"); exec \"\${SHELL:-/bin/sh}\" -l"

  if [ -n "$split" ]; then
    target_pane=$(tmux split-window -d $zoom -P -F '#{pane_id}' -t "$target_pane" -c "$worktree" "$direction" ${split_size:+-l "$split_size"} /bin/sh -c "$pane_command") || cannot_split
  else
    tmux respawn-pane -k -t "$target_pane" -c "$worktree" /bin/sh -c "$pane_command" || die "tmux respawn-pane -t $target_pane failed"
  fi
  tmux set-option -p -t "$target_pane" @s-stack-session "$name" || die "tmux set-option -p -t $target_pane @s-stack-session failed"

  if [ "$conversation_flag" = --session-id ]; then
    mkdir -p "$markers" && printf '%s\n' "$conversation_id" > "$marker" || die "cannot write the session marker $marker"
  fi
  wait_for_started_claude

  printf 'started %s pane=%s worktree=%s\n' "$name" "$target_pane" "$worktree"
}

case "$mode" in
  start) cmd_start ;;
  close) cmd_close ;;
  remove) cmd_remove ;;
  print-window) cmd_print_window ;;
esac
