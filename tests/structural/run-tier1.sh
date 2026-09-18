#!/usr/bin/env bash
# Tier 1 structural acceptance suite.
#
# Proves structural packaging and deployment for all sixteen packages: manifests
# resolve, installs succeed, deployed inventory matches the promised primitives,
# and the pinned CLI's documented limitations are asserted rather than hidden.
#
# Runtime recognition, workflow behaviour and agent identity dispatch are out of
# scope: no client application is launched.
#
# Every `apm` invocation is bounded by a hard timeout. APM 0.30.0 serialises
# state mutations behind one OS-user lock at `$HOME/.apm/.apm-lifecycle.lock`
# with a 120-second bounded wait, so a concurrent or orphaned APM operation can
# stall a call for two minutes before it fails. That lock path is derived from
# `Path.home()`, so `HOME` must be writable; redirect it to a scratch directory
# if it is not. `apm pack` does not take that lock and fails fast on the
# local-path guardrail, but it is bounded for uniformity.
set -uo pipefail
shopt -s nullglob

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if [[ -z "${APM:-}" ]]; then
  if [[ -x "$REPO_ROOT/.venv-apm/bin/apm" ]]; then
    APM="$REPO_ROOT/.venv-apm/bin/apm"
  else
    APM="$(command -v apm || true)"
  fi
fi
TARGETS="${APM_TARGETS:-cursor,claude,copilot}"
IFS=',' read -r -a target_list <<< "$TARGETS"
APM_TIMEOUT="${APM_TIMEOUT:-180}"

# Manifests that declare a sibling `path:` dependency. APM 0.30.0 refuses to
# pack such a manifest in every bundle format. See docs/DEPENDENCY-CONTRACTS.md;
# this suite asserts that refusal rather than skipping these packages silently.
PACK_BLOCKED=" foundry-default-stack foundry-execution foundry-planning foundry-pr foundry-repo-maintenance foundry-skill-creation foundry-swarm "

# `apm audit --ci` cannot replay `foundry-default-stack`'s own lockfile: the
# meta-package reaches `foundry-planning` both directly and transitively, so
# `apm install` writes two `_local/foundry-planning` entries with different
# `resolved_by` values, and the drift replay then cannot tell which one parents
# `foundry-architect` and `foundry-swarm`. That is an APM 0.30.0 lockfile-writer
# defect, reproduced without Foundry in docs/DEPENDENCY-CONTRACTS.md. The
# consumer-side audit of the same manifest passes, and that is asserted below by
# the scratch-consumer checks, so this package's own audit is asserted as a
# known failure rather than treated as a pass.
AUDIT_KNOWN_BROKEN=" foundry-default-stack "
AUDIT_KNOWN_BROKEN_SIGNATURE="ambiguous resolved_by parent"

# Direct dependencies of the meta-package, plus the two packages they pull in
# transitively (`foundry-swarm` via several packages, `foundry-architect` via
# `foundry-swarm`). A default-stack install therefore deploys ten of the sixteen
# packages, which is what the scratch-consumer inventory check covers.
DEFAULT_STACK_DEPLOYED="foundry-architect foundry-coding-style foundry-execution foundry-git-diff foundry-planning foundry-pr foundry-repo-maintenance foundry-review foundry-skill-creation foundry-swarm"

# Primitives that no longer ship. `design-skill` is deliberately absent: it moved
# to `foundry-skill-creation` and is still deployed.
RETIRED="pr-contention port-claude-code-artefact sequential-ralplan explain-pr generate-pr-story optimise-cursor-repo"

failures=0
scratch=""
cleanup() { [[ -n "$scratch" ]] && rm -rf "$scratch"; }
trap cleanup EXIT

if [[ ! -x "$APM" ]]; then
  echo "error: apm not found at '${APM:-<unset>}' (set APM=, create .venv-apm, or put apm on PATH)" >&2
  exit 2
fi

bounded() {
  if command -v timeout >/dev/null 2>&1; then
    timeout "$APM_TIMEOUT" "$@"
  elif command -v gtimeout >/dev/null 2>&1; then
    gtimeout "$APM_TIMEOUT" "$@"
  elif command -v perl >/dev/null 2>&1; then
    perl -e 'alarm shift; exec @ARGV' "$APM_TIMEOUT" "$@"
  else
    echo "error: no timeout mechanism available (need timeout, gtimeout or perl)" >&2
    return 127
  fi
}

run_apm() { bounded "$APM" "$@"; }

# True when the given target is part of the target list being exercised.
has_target() {
  local needle="$1" candidate
  for candidate in "${target_list[@]}"; do
    [[ "$candidate" == "$needle" ]] && return 0
  done
  return 1
}

report() {
  if [[ "$1" == "0" ]]; then
    printf '  [+] %s\n' "$2"
  else
    printf '  [x] %s (exit %s)\n' "$2" "$1"
    failures=$((failures + 1))
  fi
}

# Expected deployed path for one source file, relative to the consumer root.
# Mirrors the per-target layout asserted in docs/COMPATIBILITY.md.
deployed_path() {
  local target="$1" source="$2" base
  case "$source" in
    skills/*)
      if [[ "$target" == "claude" ]]; then
        printf '.claude/skills/%s' "${source#skills/}"
      else
        printf '.agents/skills/%s' "${source#skills/}"
      fi
      ;;
    agents/*.agent.md)
      base="${source#agents/}"
      base="${base%.agent.md}"
      case "$target" in
        cursor) printf '.cursor/agents/%s.md' "$base" ;;
        claude) printf '.claude/agents/%s.md' "$base" ;;
        copilot) printf '.github/agents/%s.agent.md' "$base" ;;
      esac
      ;;
    instructions/*.instructions.md)
      base="${source#instructions/}"
      base="${base%.instructions.md}"
      case "$target" in
        cursor) printf '.cursor/rules/%s.mdc' "$base" ;;
        claude) printf '.claude/rules/%s.md' "$base" ;;
        copilot) printf '.github/instructions/%s.instructions.md' "$base" ;;
      esac
      ;;
    *)
      printf '%s' "$source"
      ;;
  esac
}

packages=()
for dir in "$REPO_ROOT"/packages/*/; do
  packages+=("$(basename "$dir")")
done

echo "APM: $(bounded "$APM" --version)"
echo "Targets: $TARGETS (override with APM_TARGETS)"
echo
echo "Primitive contract"
bounded python3 "$REPO_ROOT/tests/structural/validate_primitives.py"
report $? "validate_primitives.py"

initial_state="$( cd "$REPO_ROOT" && { git status --porcelain | sort; git diff; } | git hash-object --stdin )"

echo
echo "Per-package matrix"
# `install --frozen` precedes `compile --validate`: on a package whose .apm/
# holds only skills, `compile --validate` exits 1 until an install has
# materialised the deploy targets. See docs/COMPATIBILITY.md.
printf '  %-26s %-8s %-8s %-6s %-9s %-10s\n' PACKAGE dry-run frozen audit validate pack
for package in "${packages[@]}"; do
  work_dir="$REPO_ROOT/packages/$package"

  ( cd "$work_dir" && run_apm install --dry-run --target "$TARGETS" ) >/dev/null 2>&1
  dry_status=$?
  ( cd "$work_dir" && run_apm install --frozen --target "$TARGETS" ) >/dev/null 2>&1
  frozen_status=$?
  audit_output="$( cd "$work_dir" && run_apm audit --ci 2>&1 )"
  audit_status=$?
  audit_display="$audit_status"
  if [[ "$AUDIT_KNOWN_BROKEN" == *" $package "* && "$audit_status" != "0" && "$audit_output" == *"$AUDIT_KNOWN_BROKEN_SIGNATURE"* ]]; then
    audit_display="known"
  fi
  ( cd "$work_dir" && run_apm compile --validate ) >/dev/null 2>&1
  validate_status=$?

  pack_output="$( cd "$work_dir" && run_apm pack --dry-run --verbose 2>&1 )"
  pack_status=$?
  if [[ "$PACK_BLOCKED" == *" $package "* && "$pack_status" != "0" && "$pack_output" == *"contains local path dependency"* ]]; then
    pack_status="blocked"
  fi

  printf '  %-26s %-8s %-8s %-6s %-9s %-10s\n' \
    "$package" "$dry_status" "$frozen_status" "$audit_display" "$validate_status" "$pack_status"

  report "$dry_status" "$package install --dry-run"
  report "$frozen_status" "$package install --frozen"
  if [[ "$audit_display" == "known" ]]; then
    echo "  [+] $package audit --ci blocked by the duplicated-resolved_by bug (documented)"
  else
    report "$audit_status" "$package audit --ci"
  fi
  report "$validate_status" "$package compile --validate"
  if [[ "$pack_status" == "0" ]]; then
    echo "  [+] $package pack --dry-run"
  elif [[ "$pack_status" == "blocked" ]]; then
    echo "  [+] $package pack --dry-run blocked by the local-path guardrail (documented)"
  else
    echo "  [x] $package pack --dry-run (exit $pack_status)"
    failures=$((failures + 1))
  fi
done

echo
echo "Scratch-consumer installs (source, per target)"
scratch="$(mktemp -d "${TMPDIR:-/tmp}/foundry-tier1.XXXXXX")"
for target in "${target_list[@]}"; do
  consumer="$scratch/consumer-$target"
  mkdir -p "$consumer"
  (
    cd "$consumer" || exit 1
    run_apm init -y --target "$target" >/dev/null 2>&1 || exit 1
    run_apm install "$REPO_ROOT/packages/foundry-default-stack" --target "$target" >/dev/null 2>&1 || exit 1
    run_apm view foundry-default-stack >/dev/null 2>&1 || exit 1
    run_apm audit --ci >/dev/null 2>&1 || exit 1
  )
  report $? "$target scratch consumer (init, install, view, audit)"

  inventory_missing=0
  for package in $DEFAULT_STACK_DEPLOYED; do
    package_dir="$REPO_ROOT/packages/$package"
    apm_dir="$package_dir/.apm"
    while IFS= read -r file; do
      source_relative="${file#"$apm_dir"/}"
      expected="$(deployed_path "$target" "$source_relative")"
      if [[ ! -f "$consumer/$expected" ]]; then
        echo "  [x] $target $package: missing $expected (from .apm/$source_relative)"
        inventory_missing=$((inventory_missing + 1))
      fi
    done < <(find "$apm_dir" -type f)
  done
  failures=$((failures + inventory_missing))
  if (( inventory_missing == 0 )); then
    echo "  [+] $target deployed every skill, agent and instruction file for the ten default-stack packages"
  fi

  retired_hits=0
  for retired in $RETIRED; do
    if grep -rqs "$retired" "$consumer" 2>/dev/null; then
      echo "  [x] $target deployed retired primitive \"$retired\""
      failures=$((failures + 1))
      retired_hits=$((retired_hits + 1))
    fi
  done
  if (( retired_hits == 0 )); then
    echo "  [+] $target deployed no retired primitive"
  fi
done

echo
echo "Target detection"
run_apm targets --json --all
report $? "apm targets --json --all (recorded above; targets are always passed explicitly)"

echo
echo "Instruction scoping translation"
scope_rows=(
  "software-engineering-rules|**/*"
  "compatibility-surface-gate|**/*"
  "zen-of-python|**/*.py"
  "plan-handoff-standard|.foundry/plans/**/*.md"
  "keep-agent-mds-up-to-date|**/AGENTS.md"
)
scope_failures=0
for row in "${scope_rows[@]}"; do
  name="${row%%|*}"
  pattern="${row#*|}"
  if has_target cursor; then
    cursor_rule="$scratch/consumer-cursor/.cursor/rules/$name.mdc"
    grep -qF "globs: \"$pattern\"" "$cursor_rule" 2>/dev/null || { echo "  [x] cursor $name globs"; failures=$((failures + 1)); scope_failures=$((scope_failures + 1)); }
  fi
  if has_target claude; then
    claude_rule="$scratch/consumer-claude/.claude/rules/$name.md"
    grep -qF "\"$pattern\"" "$claude_rule" 2>/dev/null || { echo "  [x] claude $name paths"; failures=$((failures + 1)); scope_failures=$((scope_failures + 1)); }
  fi
  if has_target copilot; then
    copilot_rule="$scratch/consumer-copilot/.github/instructions/$name.instructions.md"
    grep -qF "applyTo: \"$pattern\"" "$copilot_rule" 2>/dev/null || { echo "  [x] copilot $name applyTo"; failures=$((failures + 1)); scope_failures=$((scope_failures + 1)); }
  fi
done
if (( scope_failures == 0 )); then
  echo "  [+] scoping keys translated for all five instructions on $TARGETS"
fi

echo
echo "Archive consumer (packed bundles)"
archive_failures=0
for package in "${packages[@]}"; do
  [[ "$PACK_BLOCKED" == *" $package "* ]] && continue
  work_dir="$REPO_ROOT/packages/$package"
  # `--target` is passed explicitly: without it `apm pack` detects the target
  # from the filesystem, which on a clean checkout yields the `minimal`
  # pseudo-target and produces a bundle `apm install` rejects.
  ( cd "$work_dir" && run_apm pack --archive -o ./dist --target "$TARGETS" ) >/dev/null 2>&1
  status=$?
  archive="$(find "$work_dir/dist" -maxdepth 1 -name '*.zip' 2>/dev/null | sort | head -1)"
  if (( status != 0 )) || [[ -z "$archive" ]]; then
    echo "  [x] $package pack --archive failed (exit $status)"
    archive_failures=$((archive_failures + 1))
    continue
  fi
  if unzip -l "$archive" | grep -qE "pr-contention|port-claude-code-artefact|sequential-ralplan|explain-pr|generate-pr-story|optimise-cursor-repo"; then
    echo "  [x] $package archive contains a retired primitive"
    archive_failures=$((archive_failures + 1))
    continue
  fi
  echo "  [+] $package archive $(basename "$archive")"
done
report "$archive_failures" "pack --archive for every packable package"

# `foundry-review` carries both skills and agents, so the archive consumer
# asserts the two primitive types that a plugin bundle can deploy.
archive="$(find "$REPO_ROOT/packages/foundry-review/dist" -maxdepth 1 -name '*.zip' 2>/dev/null | sort | head -1)"
if [[ -n "$archive" ]]; then
  mkdir -p "$scratch/archive-consumer"
  (
    cd "$scratch/archive-consumer" || exit 1
    run_apm init -y --target "$TARGETS" >/dev/null 2>&1 || exit 1
    run_apm install "$archive" --target "$TARGETS" >/dev/null 2>&1 || exit 1
    run_apm audit --ci >/dev/null 2>&1 || exit 1
  )
  report $? "archive install + audit in a clean consumer"

  archive_inventory_missing=0
  archive_expected=(".agents/skills/thermos/SKILL.md")
  has_target cursor && archive_expected+=(".cursor/agents/thermo-nuclear-review-subagent.md")
  has_target claude && archive_expected+=(".claude/agents/thermo-nuclear-review-subagent.md")
  has_target copilot && archive_expected+=(".github/agents/thermo-nuclear-review-subagent.agent.md")
  for expected in "${archive_expected[@]}"; do
    if [[ ! -f "$scratch/archive-consumer/$expected" ]]; then
      echo "  [x] archive consumer: missing $expected"
      archive_inventory_missing=$((archive_inventory_missing + 1))
    fi
  done
  failures=$((failures + archive_inventory_missing))
  if (( archive_inventory_missing == 0 )); then
    echo "  [+] archive consumer deployed the bundle's skills and agents for $TARGETS"
  fi

  tampered="$scratch/tampered.zip"
  cp "$archive" "$tampered"
  bounded python3 - "$tampered" <<'PY'
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
data = bytearray(path.read_bytes())
data[len(data) // 2] ^= 0x01
path.write_bytes(bytes(data))
PY
  ( cd "$scratch/archive-consumer" && run_apm install "$tampered" --target "$TARGETS" ) >/dev/null 2>&1
  if [[ $? -ne 0 ]]; then
    report 0 "tampered archive rejected after flipping one byte"
  else
    report 1 "tampered archive rejected after flipping one byte"
  fi
else
  report 1 "found an archive to consume"
fi

echo
echo "Secret scan (working tree, deploy candidates and dist archives)"
bounded python3 "$REPO_ROOT/tests/structural/scan_secrets.py"
report $? "scan_secrets.py"

echo
echo "Missing sibling dependency fails actionably"
missing="$scratch/missing"
mkdir -p "$missing/packages"
for package in foundry-execution foundry-pr; do
  mkdir -p "$missing/packages/$package"
  cp "$REPO_ROOT/packages/$package/apm.yml" "$REPO_ROOT/packages/$package/apm.lock.yaml" "$missing/packages/$package/"
  cp -R "$REPO_ROOT/packages/$package/.apm" "$missing/packages/$package/"
done
rm -rf "$missing/packages/foundry-pr"
missing_output="$( cd "$missing/packages/foundry-execution" && run_apm install --frozen --target cursor 2>&1 )"
missing_status=$?
if [[ $missing_status -ne 0 && "$missing_output" == *"does not exist"* ]]; then
  report 0 "missing sibling dependency reports an actionable error"
else
  report 1 "missing sibling dependency reports an actionable error"
fi

echo
echo "Stability"
final_state="$( cd "$REPO_ROOT" && { git status --porcelain | sort; git diff; } | git hash-object --stdin )"
if [[ "$initial_state" == "$final_state" ]]; then
  report 0 "install and pack leave no tracked-file change"
else
  report 1 "install and pack leave no tracked-file change"
fi

echo
if (( failures > 0 )); then
  echo "[x] $failures failing check(s)"
  exit 1
fi
echo "[+] all Tier 1 structural checks passed across ${#packages[@]} packages"
