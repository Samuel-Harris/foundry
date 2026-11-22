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
required for every session except the first spec writer of a feature, or a
restart of it in its own pane.

Features and phases are kebab-case. A feature name may not contain -phase- or
end with -phase, -planner, -orchestrator, -spec or -spec-<n>, because another
feature's session could have that name.

Standard output is one line, except one closed line per pane for --close:
  started <name> pane=<pane id> worktree=<path>   started the session
  alive <name> pane=<pane id>                     the session already runs; nothing changed
  closed <name> pane=<pane id>                    --close closed a pane running the session,
                                                  or tagged with its name and idle at a shell
  absent <name>                                   --close found neither
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

# Without -u a client outside a UTF-8 locale prints tabs and non-ASCII characters
# in formats, paths among them, as underscores.
tmux() {
  command tmux -u "$@"
}

require() {
  local tool
  for tool in "$@"; do
    type -P "$tool" >/dev/null 2>&1 || { printf 'launch.sh: %s not found on PATH\n' "$tool" >&2; exit 3; }
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

# A pane is idle when every process in its terminal's foreground group is an
# interactive shell given no script and no -c command: -zsh, zsh -l, bash. A
# helper the shell keeps in the background, as zsh prompt plugins do, is not in
# that group; a build started as bash build.sh, or a command run with exec, is.
pane_is_idle() {
  LC_ALL=C ps -ww -t "${1#/dev/}" -o stat=,args= 2>/dev/null | awk '
    $1 !~ /[+]/ { next }
    {
      seen = 1
      program = $2; sub(/^-/, "", program); sub(/.*\//, "", program)
      if (program !~ /^(sh|bash|zsh|dash|fish|ksh|tcsh|csh)$/) busy = 1
      for (i = 3; i <= NF; i++) if ($i !~ /^-/ || $i ~ /^-[^-]*c/ || $i == "--command") busy = 1
    }
    END { exit !(seen && !busy) }'
}

# Prints "pane_id window_id tag kind in_worktree idle" for every pane, in tmux's
# order. tag is the pane's @s-stack-session option, or - when unset. kind
# describes the claude processes among the pane's descendants: strict when a
# claude's first argument is --name <session>, as the launcher writes it, so a
# --name inside a prompt never matches; continued when no argument is --name
# and one is --continue or -c, which is how workmux resurrect restarts a session
# and resumes its conversation; nameless for any other claude without --name;
# other for any other claude; none without one. A pane running several claudes reports the closest
# match. in_worktree is 1 when the pane's directory is <worktree> or under it.
# idle is 1 when the pane sits at an interactive shell, as pane_is_idle decides.
pane_inventory() {
  local session=$1 worktree_path=$2 panes pane_id pane_pid window_id tag tty idle current_path in_worktree resolved_worktree='' status
  # Spaces, not tabs, separate the fields: a tmux client without a UTF-8 locale
  # prints a tab in a format as "_". The path goes last so read keeps its spaces.
  if ! panes=$(tmux list-panes -a -F "#{pane_id} #{pane_pid} #{window_id} #{?@s-stack-session,#{@s-stack-session},-} #{pane_tty} #{pane_current_path}"); then
    # With no server no session runs, which --close and --remove may rely on; start mode needs a window.
    # Before tmux has ever run there is no socket directory, and tmux says it cannot connect.
    status=$(tmux list-sessions 2>&1) || true
    [ "$mode" != start ] && [[ $status == 'no server running'* || $status == 'error connecting to'* ]] || die 'tmux list-panes failed'
    panes=''
  fi
  [ -z "$worktree_path" ] || resolved_worktree=$(resolve "$worktree_path")
  {
    printf '%s\n' "$panes" | while read -r pane_id pane_pid window_id tag tty current_path; do
      [ -n "$pane_id" ] || continue
      idle=0
      if pane_is_idle "$tty"; then idle=1; fi
      in_worktree=0
      if [ -n "$resolved_worktree" ] && [[ "$(resolve "$current_path")/" == "$resolved_worktree"/* ]]; then in_worktree=1; fi
      printf 'pane %s %s %s %s %s %s\n' "$pane_id" "$pane_pid" "$window_id" "$tag" "$in_worktree" "$idle"
    done
    # procps cuts each line to $COLUMNS even into a pipe, which would hide --name.
    ps -A -ww -o pid=,ppid=,args=
  } | awk -v name="$session" '
    $1 == "pane" { order[++n] = $3; pane_pid[$3] = $2; info[$2] = $2 " " $4 " " $5; in_worktree[$2] = $6; idle[$2] = $7; next }
    {
      parent[$1] = $2
      program = $3; sub(/.*\//, "", program)
      if (program != "claude") next
      strict = ($4 == "--name" && $5 == name) || $4 == "--name=" name
      named = 0
      for (i = 4; i <= NF; i++) if ($i == "--name" || index($i, "--name=") == 1) named = 1
      continued = 0
      for (i = 4; i <= NF; i++) if ($i == "--continue" || $i == "-c") continued = 1
      claude[$1] = strict ? "strict" : (named ? "other" : (continued ? "continued" : "nameless"))
    }
    END {
      rank["none"] = 0; rank["other"] = 1; rank["nameless"] = 2; rank["continued"] = 3; rank["strict"] = 4
      for (i = 1; i <= n; i++) kind[pane_pid[order[i]]] = "none"
      for (pid in claude) {
        for (p = pid; p != "" && p > 1; p = parent[p]) {
          if (!(p in pane_pid)) continue
          pane = pane_pid[p]
          if (rank[claude[pid]] > rank[kind[pane]]) kind[pane] = claude[pid]
          break
        }
      }
      for (i = 1; i <= n; i++) { pane = pane_pid[order[i]]; print info[pane], kind[pane], in_worktree[pane], idle[pane] }
    }'
}

# Reads pane_inventory for <session> and prints the one pane that runs it, or
# nothing. A claude named for the session counts, and so does a nameless claude
# in the inventory's worktree in the session's own tagged pane, as a developer
# resuming it by hand leaves it. Only when neither exists does a continued one in
# an untagged pane count, as workmux resurrect makes, and only when <marker>
# shows the launcher started the session there. A plain claude the developer
# opens is never taken for it.
live_pane_of() {
  local session=$1 marker=$2 inventory matches
  inventory=$(cat)
  matches=$(printf '%s\n' "$inventory" | awk -v session="$session" '$4 == "strict" || (($4 == "nameless" || $4 == "continued") && $5 == 1 && $3 == session) { print $1 }')
  if [ -z "$matches" ] && [ -n "$marker" ] && [ -s "$marker" ]; then
    matches=$(printf '%s\n' "$inventory" | awk '$4 == "continued" && $5 == 1 && $3 == "-" { print $1 }')
  fi
  at_most_one "pane runs $session" "$matches"
  [ -z "$matches" ] || printf '%s\n' "$matches"
}

marker_of() {
  local worktree_path=$1 session=$2 markers
  markers=$(git -C "$worktree_path" rev-parse --git-path s-stack-sessions) || die "git -C $worktree_path rev-parse failed"
  case "$markers" in /*) ;; *) markers=$worktree_path/$markers ;; esac
  printf '%s/%s\n' "$markers" "$session"
}

find_live_pane() {
  local marker=''
  # workmux resurrect restores only the orchestrator, and the spec writer has
  # ended by then, so a nameless claude in an untagged pane of the feature
  # worktree is the orchestrator.
  if [ -z "$first_spec" ] && [ -n "$worktree" ]; then marker=$(marker_of "$worktree" "$name"); fi
  printf '%s\n' "$inventory" | live_pane_of "$name" "$marker"
}

# Reads pane_inventory and prints the first pane of $window tagged with the
# session's name that is idle: the session's pane, left at its shell after
# claude exited, and not running a command of the developer's. Restarting there
# keeps restarts from shrinking the columns.
find_own_pane() {
  awk -v window="$window" -v name="$name" '$2 == window && $3 == name && $4 == "none" && $6 == 1 { print $1; exit }'
}

# A launch killed with SIGKILL leaves its lock behind, and a crash is when every
# session is relaunched. The holder's PID and start time tell such a lock from a
# live one; the start time catches a PID that another process has since reused.
# ps prints the start time in the caller's locale and time zone, and launches
# compare each other's records, so every launch prints it in the same ones.
process_start() {
  LC_ALL=C TZ=UTC ps -o lstart= -p "$1" 2>/dev/null | awk '{ $1 = $1; print }'
}

# A record is "<pid> <start time>".
is_stale() {
  [ "$(process_start "${1%% *}")" != "${1#* }" ]
}

# A lock is a symlink whose target is its holder's record, so a launch takes the
# lock and records itself in one step. Two waiters can both see the same stale
# record, and the slower one must not remove the lock the faster one has taken
# since, so a stale lock is removed only under the breaker lock, and only while
# it still holds the record seen. Succeeds when it removed a stale lock or a
# stale breaker, so the caller retries at once.
break_stale_lock() {
  local lock=$1 stale=$2 breaker=$1.break record
  if ln -s "$lock_record" "$breaker" 2>/dev/null; then
    if [ "$(readlink "$lock" 2>/dev/null)" = "$stale" ]; then rm -f "$lock"; fi
    rm -f "$breaker"
    return 0
  fi
  record=$(readlink "$breaker" 2>/dev/null) && is_stale "$record" || return 1
  rm -f "$breaker"
}

take_lock() {
  local lock=$1 holder=$2 seconds=$3 tries=0 record
  until ln -s "$lock_record" "$lock" 2>/dev/null; do
    if record=$(readlink "$lock" 2>/dev/null) && is_stale "$record" && break_stale_lock "$lock" "$record"; then
      continue
    fi
    tries=$((tries + 1))
    [ "$tries" -lt $((seconds * 10)) ] || die "launch $(readlink "$lock" | awk '{ print $1 }') of $holder has held $lock for $seconds seconds"
    sleep 0.1
  done
}

# A lock whose holder was judged stale may since belong to another launch.
release_lock() {
  if [ -n "$1" ] && [ "$(readlink "$1" 2>/dev/null)" = "$lock_record" ]; then rm -f "$1"; fi
}

release_window() {
  if [ -n "$zoomed_pane" ]; then
    tmux resize-pane -Z -t "$zoomed_pane" || true
    zoomed_pane=''
  fi
  release_lock "$window_lock"
  window_lock=''
}

# git worktree add reads every sibling worktree's commondir file, and a
# concurrent add can catch one half written and fail. A workmux add can take
# minutes, so a concurrent launch waits five.
lock_worktrees() {
  take_lock "$locks/worktrees" "a session adding a worktree" 300
  worktrees_lock=$locks/worktrees
}

release_worktrees() {
  release_lock "$worktrees_lock"
  worktrees_lock=''
}

# Held until the launcher exits, so a concurrent launch of the same session
# checks liveness only after ps shows this one's claude. The holder may be
# waiting for the worktree lock, so the wait is as long.
lock_session() {
  local common
  common=$(git rev-parse --git-common-dir 2>/dev/null) && common=$(resolve "$common") && [ -n "$common" ] || die 'cannot resolve the git common directory'
  locks=$common/s-stack-locks
  mkdir -p "$locks" || die "cannot create $locks"
  lock_record="$$ $(process_start "$$")"
  take_lock "$locks/$name" "$name" 300
  session_lock=$locks/$name
  window_lock='' zoomed_pane='' worktrees_lock=''
  trap 'release_worktrees; release_window; release_lock "$session_lock"' EXIT
}

# Held from reading the window's layout until the new pane is tagged, so a
# concurrent launch of another session into the same window measures the
# layout after this split, not before it. tmux reports a zoomed pane as the
# whole window, so the window is unzoomed while it is measured and split, and
# release_window zooms the same pane again.
lock_window() {
  local zoomed
  take_lock "$locks/window-${window#@}" "a session into $window" 10
  window_lock=$locks/window-${window#@}
  zoomed=$(tmux list-panes -t "$window" -F '#{window_zoomed_flag} #{pane_active} #{pane_id}' | awk '$1 == 1 && $2 == 1 { print $3 }') || die "tmux list-panes -t $window failed"
  if [ -n "$zoomed" ]; then
    tmux resize-pane -Z -t "$zoomed" || die "tmux resize-pane -Z -t $zoomed failed"
    zoomed_pane=$zoomed
  fi
}

# A claude shows in ps a moment after its pane opens.
wait_for_started_claude() {
  local tries=0
  until pane_inventory "$name" '' | awk -v pane="$target_pane" '$1 == pane && $4 == "strict" { found = 1 } END { exit !found }'; do
    tries=$((tries + 1))
    [ "$tries" -lt 100 ] || die "claude did not start in $target_pane"
    sleep 0.1
  done
}

# Sets orchestrator_pane to the pane that runs the feature's orchestrator when
# that pane is in $window, else to nothing.
find_orchestrator_pane() {
  local feature_worktree marker=''
  feature_worktree=$(workmux path "$feature" 2>/dev/null) || feature_worktree=''
  [ -z "$feature_worktree" ] || marker=$(marker_of "$feature_worktree" "$feature-orchestrator")
  orchestrator_pane=$(pane_inventory "$feature-orchestrator" "$feature_worktree" | live_pane_of "$feature-orchestrator" "$marker")
  if [ -n "$orchestrator_pane" ] && [ "$(tmux display-message -p -t "$orchestrator_pane" '#{window_id}')" != "$window" ]; then
    orchestrator_pane=''
  fi
}

# Two panes of at least 80 columns each, and the divider between them.
side_by_side_width=161

# Each placement policy reads the window's pane table from choose_split.
top_of_first_column() {
  awk '!(NF == 8 && $8 == "workmux") && (best == "" || $2 < left || ($2 == left && $4 < top)) { best = $1; left = $2; top = $4 }
    END { if (best != "") print best }'
}

bottom_of_column() {
  awk -v anchor="$1" -v feature="$feature" '
    { n++; id[n] = $1; left[n] = $2; right[n] = $3; top[n] = $4; tag[n] = $7; if ($1 == anchor) a = n }
    END {
      if (!a) exit
      for (i = 1; i <= n; i++) {
        if (left[i] < left[a] || right[i] > right[a]) continue
        if (i != a && tag[i] != feature "-spec" && tag[i] !~ ("^" feature "-spec-[0-9]+$")) continue
        if (!best || top[i] > top[best]) best = i
      }
      print id[best]
    }'
}

right_of_column() {
  awk -v anchor="$1" -v wide="$side_by_side_width" '
    { n++; id[n] = $1; right[n] = $3; left[n] = $2; width[n] = $5; height[n] = $6; tag[n] = $7; if ($1 == anchor) a = n }
    END {
      if (!a) exit
      for (i = 1; i <= n; i++) {
        if (tag[i] == "-" || left[i] <= right[a]) continue
        if (!best || width[i] * height[i] > width[best] * height[best]) best = i
      }
      # Each -l keeps the orchestrator at least as wide as the new pane: the
      # divider takes one column of the orchestrator pane.
      if (!best) print id[a] " -h " int((width[a] - 1) / 2) " -f"
      else print id[best] " " (width[best] >= wide ? "-h" : "-v")
    }'
}

# Prints "pane_id width" for every pane wholly left or right of the column of
# <anchor>, and for <anchor> the width it keeps after giving up a <size> column
# and its divider, from left to right. A pane spanning across that column, such
# as a full-width pane above or below it, narrows with it. resize-pane -x moves a pane's right border, so setting
# each width in that order returns every other column to its width, takes the
# new column's width from the anchor's column alone, and leaves the new column,
# the rightmost, at <size>.
widths_after_full_span() {
  awk -v anchor="$1" -v size="$2" '
    { n++; id[n] = $1; left[n] = $2; right[n] = $3; width[n] = $5; if ($1 == anchor) a = n }
    END {
      for (i = 1; i <= n; i++) {
        if (i == a) print left[i], id[i], width[i] - size - 1
        else if (right[i] < left[a] || left[i] > right[a]) print left[i], id[i], width[i]
      }
    }' | sort -n | awk '{ print $2, $3 }'
}

# Sets target_pane, direction, split_size, full_span and widths for a session
# started by splitting a pane of $window. The orchestrator holds the first
# column after the workmux sidebar, spec writers stack in its column and every
# other session goes to its right. A pane without the @s-stack-session tag
# belongs to the developer or to workmux and is never split, except the
# orchestrator's pane, which a resurrect leaves untagged, and the first
# column's top pane when the orchestrator starts with no spec writer.
choose_split() {
  local panes anchor
  # Spaces separate the fields, as in pane_inventory, and the command goes last.
  panes=$(tmux list-panes -t "$window" -F '#{pane_id} #{pane_left} #{pane_right} #{pane_top} #{pane_width} #{pane_height} #{?@s-stack-session,#{@s-stack-session},-} #{pane_current_command}') || die "tmux list-panes -t $window failed"
  direction=-v split_size='' full_span='' widths=''
  case "$role" in
    orchestrator)
      anchor=$(pane_inventory "$feature-spec" '' | live_pane_of "$feature-spec" '')
      target_pane=$(printf '%s\n' "$panes" | awk -v anchor="$anchor" '$1 == anchor { print $1 }')
      [ -n "$target_pane" ] || target_pane=$(printf '%s\n' "$panes" | top_of_first_column)
      [ -n "$target_pane" ] || die "no pane to split in $window"
      ;;
    spec)
      target_pane=$(printf '%s\n' "$panes" | bottom_of_column "$orchestrator_pane")
      if [ -z "$target_pane" ] && [ -n "$first_spec" ]; then
        target_pane=$(printf '%s\n' "$panes" | top_of_first_column)
        [ -n "$target_pane" ] || die "no pane to split in $window"
      fi
      [ -n "$target_pane" ] || die "no $feature-orchestrator pane in $window"
      ;;
    planner|phase)
      read -r target_pane direction split_size full_span <<EOF
$(printf '%s\n' "$panes" | right_of_column "$orchestrator_pane")
EOF
      [ -n "$target_pane" ] || die "no $feature-orchestrator pane in $window"
      [ -z "$full_span" ] || widths=$(printf '%s\n' "$panes" | widths_after_full_span "$target_pane" "$split_size")
      ;;
  esac
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
  local inventory panes pane zoomed
  inventory=$(pane_inventory "$name" '')
  panes=$(printf '%s\n' "$inventory" | live_pane_of "$name" '')
  # A tagged pane where another claude or a command now runs belongs to whoever started it there.
  panes="$panes $(printf '%s\n' "$inventory" | awk -v name="$name" '$3 == name && $4 == "none" && $6 == 1 { print $1 }')"
  [ -n "${panes// /}" ] || { printf 'absent %s\n' "$name"; return; }
  for pane in $panes; do
    # Closing a pane unzooms its window.
    zoomed=$(tmux list-panes -t "$pane" -F '#{window_zoomed_flag} #{pane_active} #{pane_id}' | awk -v pane="$pane" '$1 == 1 && $2 == 1 && $3 != pane { print $3 }') || die "tmux list-panes -t $pane failed"
    tmux kill-pane -t "$pane" || die "tmux kill-pane -t $pane failed"
    if [ -n "$zoomed" ] && [ "$(tmux display-message -p -t "$zoomed" '#{window_zoomed_flag}')" = 0 ]; then
      tmux resize-pane -Z -t "$zoomed" || die "tmux resize-pane -Z -t $zoomed failed"
    fi
    printf 'closed %s pane=%s\n' "$name" "$pane"
  done
}

cmd_remove() {
  require workmux tmux
  local claudes dirty
  worktree=$(workmux path "$worktree_name" 2>/dev/null) || refuse 'no such worktree'
  claudes=$(pane_inventory "$name" "$worktree" | awk '$4 == "strict" || ($4 != "none" && $5 == 1)')
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
    [ -n "$first_spec" ] || usage
  fi

  lock_session
  inventory=$(pane_inventory "$name" "$worktree")
  live_pane=$(find_live_pane)
  if [ -n "$live_pane" ]; then
    printf 'alive %s pane=%s\n' "$name" "$live_pane"
    return
  fi

  target_pane=''
  if [ -n "$first_spec" ] && [ -z "$window" ] && [ -n "$worktree" ]; then
    # /sam-mode start runs again after a crash with no window to name, so the
    # spec writer is restarted in its own pane, wherever that pane is.
    read -r target_pane window <<EOF
$(printf '%s\n' "$inventory" | awk -v name="$name" '$3 == name && $4 == "none" && $6 == 1 { print $1, $2; exit }')
EOF
    [ -n "$target_pane" ] || { printf 'launch.sh: the feature worktree %s exists and no pane of %s is left; pass --window <the feature window>\n' "$feature" "$name" >&2; exit 2; }
  elif [ -n "$window" ]; then
    target_pane=$(printf '%s\n' "$inventory" | find_own_pane)
  fi
  orchestrator_pane=''
  if [ -z "$target_pane" ] && [ -n "$window" ] && [ "$role" != orchestrator ]; then
    find_orchestrator_pane
    [ -n "$orchestrator_pane" ] || [ -n "$first_spec" ] || die "no $feature-orchestrator pane in $window"
  fi
  split=''
  if [ -z "$worktree" ]; then
    if [ "$role" = orchestrator ]; then
      die "the feature worktree $feature does not exist; start the spec writer first"
    elif [ -n "$first_spec" ]; then
      branch=$(default_branch)
      git fetch -q origin "$branch" || die "git fetch origin $branch failed"
      windows_before=" $(tmux list-windows -a -F '#{window_id}' | tr '\n' ' ') "
      # workmux resurrect restores only sessions that ran in their worktree's own workmux window.
      lock_worktrees
      workmux add "$feature" --base "origin/$branch" -C >&2 || die "workmux add $feature failed"
    else
      lock_worktrees
      workmux add "$worktree_name" --headless --base "$feature" >&2 || die "workmux add $worktree_name failed"
    fi
    release_worktrees
    worktree=$(workmux path "$worktree_name") || die "workmux path $worktree_name failed after workmux add"
    if [ -n "$first_spec" ]; then
      resolved_worktree=$(resolve "$worktree")
      new_windows=$(tmux list-panes -a -F '#{window_id} #{pane_current_path}' | while read -r window_id path; do
        [[ $windows_before != *" $window_id "* ]] || continue
        if [[ "$(resolve "$path")/" == "$resolved_worktree"/* ]]; then printf '%s\n' "$window_id"; fi
      done | sort -u)
      [ -n "$new_windows" ] || die "no new window for $worktree after workmux add"
      at_most_one "new window for $worktree after workmux add" "$new_windows"
      target_pane=$(tmux list-panes -t "$new_windows" -F '#{pane_id} #{pane_current_command}' | awk '$2 != "workmux" { print $1; exit }')
      [ -n "$target_pane" ] || die "no pane but the sidebar in the new window $new_windows"
    fi
  fi

  if [ -z "$target_pane" ]; then
    split=1
    lock_window
    choose_split
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

  marker=$(marker_of "$worktree" "$name")
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
    target_pane=$(tmux split-window -d -P -F '#{pane_id}' -t "$target_pane" -c "$worktree" "$direction" ${full_span:+-f} ${split_size:+-l "$split_size"} /bin/sh -c "$pane_command") || cannot_split
    # A full-span split narrows every column in proportion.
    printf '%s\n' "$widths" | while read -r pane width; do
      [ -z "$pane" ] || tmux resize-pane -t "$pane" -x "$width" || die "tmux resize-pane -t $pane -x $width failed"
    done
  else
    tmux respawn-pane -k -t "$target_pane" -c "$worktree" /bin/sh -c "$pane_command" || die "tmux respawn-pane -t $target_pane failed"
  fi
  tmux set-option -p -t "$target_pane" @s-stack-session "$name" || die "tmux set-option -p -t $target_pane @s-stack-session failed"
  release_window
  wait_for_started_claude

  if [ "$conversation_flag" = --session-id ]; then
    mkdir -p "${marker%/*}" && printf '%s\n' "$conversation_id" > "$marker" || die "cannot write the session marker $marker"
  fi

  printf 'started %s pane=%s worktree=%s\n' "$name" "$target_pane" "$worktree"
}

case "$mode" in
  start) cmd_start ;;
  close) cmd_close ;;
  remove) cmd_remove ;;
  print-window) cmd_print_window ;;
esac
