#!/usr/bin/env bash
# Kept to Bash 3.2 features, because that is what macOS ships at /bin/bash.
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage:
  afk-watchdog.sh install
  afk-watchdog.sh remove
  afk-watchdog.sh status
  afk-watchdog.sh run <git common dir>
  afk-watchdog.sh keep-awake
  afk-watchdog.sh stop-keep-awake

install, remove and status run from inside the repository. install writes a
per-user launchd job, ~/Library/LaunchAgents/<label>.plist, that runs
"afk-watchdog.sh run <git common dir>" every 20 minutes and logs to
~/Library/Logs/s-stack-afk-watchdog.log, and loads it, replacing an older copy.
The label is com.s-stack.afk-watchdog.<first 8 hex digits of the sha1 of the
git common dir>. run reads the s-stack-afk marker, "<feature> <window id>", in
each worktree's git directory and runs the launch.sh beside this script from
that worktree with --feature <feature> --role orchestrator --window <window id>.
keep-awake keeps the Mac from idle-sleeping while the nearest claude process
above this script lives.

Standard output:
  installed <label> plist=<path>        install loaded the job
  removed <label>                       remove unloaded the job and deleted its plist
  absent <label>                        remove found no plist; status found no loaded job
  installed <label>                     status found the plist and the loaded job
  unsupported                           status on anything but macOS
  <UTC time> <feature> <outcome>        run, one line per marker: the launcher's
                                        output line, or failed <exit code>
  <UTC time> malformed marker=<path>    run, a marker that is not one line of two words
  awake claude=<pid> caffeinate=<pid>   keep-awake, whether it started caffeinate or found it
  stopped caffeinate=<pid>              stop-keep-awake ended that caffeinate
  none                                  stop-keep-awake found no caffeinate to end

Exit codes:
  1  any other failure, named on standard error; for run, a marker that failed
     or was malformed, after every marker has been tried
  2  bad arguments
  6  not macOS, for every subcommand but status and run
EOF
  exit 2
}

die() {
  printf 'afk-watchdog.sh: %s\n' "$*" >&2
  exit 1
}

on_macos() {
  [ "$(uname)" = Darwin ]
}

require_macos() {
  on_macos || { printf 'afk-watchdog.sh: %s needs macOS\n' "$1" >&2; exit 6; }
}

script_dir=$(cd "$(dirname "$0")" && pwd -P)
script=$script_dir/$(basename "$0")

resolve_job() {
  local common
  common=$(git rev-parse --git-common-dir 2>/dev/null) || die 'run this from inside a git repository'
  common=$(cd "$common" && pwd -P) || die "cannot resolve $common"
  common_dir=$common
  label=com.s-stack.afk-watchdog.$(printf '%s' "$common" | shasum -a 1 | cut -c1-8)
  plist=$HOME/Library/LaunchAgents/$label.plist
  domain=gui/$(id -u)
}

xml() {
  printf '%s' "$1" | sed -e 's/&/\&amp;/g' -e 's/</\&lt;/g' -e 's/>/\&gt;/g' -e 's/"/\&quot;/g'
}

string() {
  printf '      <string>%s</string>\n' "$(xml "$1")"
}

variable() {
  printf '      <key>%s</key>\n' "$(xml "$1")"
  string "$2"
}

write_plist() {
  local log=$HOME/Library/Logs/s-stack-afk-watchdog.log
  cat <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key>
    <string>$(xml "$label")</string>
    <key>ProgramArguments</key>
    <array>
$(string /bin/bash)
$(string "$script")
$(string run)
$(string "$common_dir")
    </array>
    <key>StartInterval</key>
    <integer>1200</integer>
    <key>RunAtLoad</key>
    <false/>
    <key>StandardOutPath</key>
    <string>$(xml "$log")</string>
    <key>StandardErrorPath</key>
    <string>$(xml "$log")</string>
    <key>EnvironmentVariables</key>
    <dict>
$(variable PATH "$PATH")
$(variable HOME "$HOME")
$([ -z "${TMUX_TMPDIR:-}" ] || variable TMUX_TMPDIR "$TMUX_TMPDIR")
$([ -z "${LANG:-}" ] || variable LANG "$LANG")
    </dict>
  </dict>
</plist>
EOF
}

cmd_install() {
  require_macos install
  resolve_job
  mkdir -p "$HOME/Library/LaunchAgents" "$HOME/Library/Logs" || die "cannot create the directories under $HOME/Library"
  write_plist > "$plist.tmp" || die "cannot write $plist.tmp"
  mv -f "$plist.tmp" "$plist" || die "cannot write $plist"
  launchctl bootout "$domain/$label" >/dev/null 2>&1 || true
  # bootout returns before the old job is gone, and bootstrap fails while it is still loaded.
  local tries=0
  while launchctl print "$domain/$label" >/dev/null 2>&1 && [ "$tries" -lt 50 ]; do
    sleep 0.1
    tries=$((tries + 1))
  done
  launchctl bootstrap "$domain" "$plist" || die "launchctl bootstrap $domain $plist failed"
  printf 'installed %s plist=%s\n' "$label" "$plist"
}

cmd_remove() {
  require_macos remove
  resolve_job
  launchctl bootout "$domain/$label" >/dev/null 2>&1 || true
  if [ -e "$plist" ]; then
    rm -f "$plist" || die "cannot delete $plist"
    printf 'removed %s\n' "$label"
  else
    printf 'absent %s\n' "$label"
  fi
}

cmd_status() {
  on_macos || { echo unsupported; return; }
  resolve_job
  if [ -e "$plist" ] && launchctl print "$domain/$label" >/dev/null 2>&1; then
    printf 'installed %s\n' "$label"
  else
    printf 'absent %s\n' "$label"
  fi
}

cmd_run() {
  local common=$1 failed='' listing worktree git_dir marker content feature window extra out
  [ -d "$common" ] || usage
  listing=$(git --git-dir "$common" worktree list --porcelain) || die "git --git-dir $common worktree list failed"
  while IFS= read -r line; do
    case "$line" in worktree\ *) ;; *) continue ;; esac
    worktree=${line#worktree }
    git_dir=$(git -C "$worktree" rev-parse --absolute-git-dir 2>/dev/null) || continue
    marker=$git_dir/s-stack-afk
    [ -f "$marker" ] || continue
    content=$(cat "$marker") || content=''
    feature='' window='' extra=''
    case "$content" in *$'\n'*) ;; *) read -r feature window extra <<<"$content" || true ;; esac
    if [ -z "$feature" ] || [ -z "$window" ] || [ -n "$extra" ]; then
      printf '%s malformed marker=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$marker"
      failed=1
      continue
    fi
    out=$(cd "$worktree" && "$script_dir/launch.sh" --feature "$feature" --role orchestrator --window "$window" </dev/null) || {
      out="failed $?"
      failed=1
    }
    printf '%s %s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$feature" "$out"
  done <<EOF
$listing
EOF
  [ -z "$failed" ] || exit 1
}

nearest_claude() {
  local pid=$$ comm
  while [ "$pid" -gt 1 ]; do
    comm=$(ps -o comm= -p "$pid" 2>/dev/null) || break
    comm=${comm##*/}
    if [ "$comm" = claude ]; then
      echo "$pid"
      return
    fi
    pid=$(ps -o ppid= -p "$pid" 2>/dev/null | tr -d ' ') || break
    [ -n "$pid" ] || break
  done
  die 'no claude process above this script'
}

caffeinates_for() {
  ps -A -ww -o pid= -o args= | awk -v want="$1" '{
    program = $2
    sub(/.*\//, "", program)
    if (program == "caffeinate" && NF == 6 && $3 == "-i" && $4 == "-s" && $5 == "-w" && $6 == want) print $1
  }'
}

cmd_keep_awake() {
  require_macos keep-awake
  local claude caffeinate
  claude=$(nearest_claude)
  caffeinate=$(caffeinates_for "$claude" | head -n 1)
  if [ -z "$caffeinate" ]; then
    type -P caffeinate >/dev/null 2>&1 || die 'caffeinate not found on PATH'
    nohup caffeinate -i -s -w "$claude" >/dev/null 2>&1 &
    caffeinate=$!
  fi
  printf 'awake claude=%s caffeinate=%s\n' "$claude" "$caffeinate"
}

cmd_stop_keep_awake() {
  require_macos stop-keep-awake
  local claude pids pid
  claude=$(nearest_claude)
  pids=$(caffeinates_for "$claude")
  if [ -z "$pids" ]; then
    echo none
    return
  fi
  for pid in $pids; do
    kill "$pid" 2>/dev/null || die "cannot end caffeinate $pid"
    printf 'stopped caffeinate=%s\n' "$pid"
  done
}

[ $# -ge 1 ] || usage
case "$1" in
  install|remove|status|keep-awake|stop-keep-awake) [ $# -eq 1 ] || usage ;;
  run) [ $# -eq 2 ] || usage ;;
  *) usage ;;
esac
case "$1" in
  install) cmd_install ;;
  remove) cmd_remove ;;
  status) cmd_status ;;
  run) cmd_run "$2" ;;
  keep-awake) cmd_keep_awake ;;
  stop-keep-awake) cmd_stop_keep_awake ;;
esac
