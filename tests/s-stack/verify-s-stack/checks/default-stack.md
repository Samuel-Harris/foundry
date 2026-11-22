# Phase `default-stack` checks

Phase `default-stack` makes the meta-package install `s-stack` in place of `planning`, which it now reaches through `s-stack`. It adds `s-stack` and `p-stack` to the Tier 1 scratch-consumer inventory, and documents the new dependency graph and the drift that `apm audit --ci` reports on `default-stack`'s relativised lockfile.

Run every check from the repository root, outside the agent sandbox, with the pinned CLI. `APM` names it, and defaults to `.venv-apm/bin/apm`. Each check bounds every `apm` call as `AGENTS.md` requires. Scratch consumers go under `mktemp -d`. Afterwards, run the verification skill's Cleanup, and `git status --short` must show nothing the checks left.

## Rerun

### Strict handbook routes

Every `handbooks/<role>.md` code span in `SKILL.md` names a file that exists, and a missing one fails. This is the strict form of the verification skill's check 4. The same function then runs on a copy of `SKILL.md` outside the repository with an extra route to a handbook that does not exist, and must fail there, which proves the check can fail.

```bash
bash <<'EOF'
d=packages/s-stack/.apm/skills/sam-mode
check_routes() {
  local routes route status=0
  routes=$(grep -oE '`handbooks/[a-z0-9-]+\.md`' "$1" | tr -d '`' | sort -u)
  [ -n "$routes" ] || { echo "FAIL no route in $1"; return 1; }
  for route in $routes; do
    if [ -f "$d/$route" ]; then echo "present $route"; else echo "MISSING $route"; status=1; fi
  done
  return $status
}
check_routes "$d/SKILL.md"; real=$?
tmp=$(mktemp -d)
{ cat "$d/SKILL.md"; printf '\nRead `handbooks/no-such-role.md`.\n'; } > "$tmp/SKILL.md"
check_routes "$tmp/SKILL.md" >/dev/null; bogus=$?
rm -rf "$tmp"
echo "real=$real bogus=$bogus"
[ "$real" -eq 0 ] && [ "$bogus" -eq 1 ]
EOF
```

Expected: one `present` line per route, no `MISSING` line, the last line `real=0 bogus=1`, and exit `0`. Any `MISSING` line fails the check, and so does `bogus=0`.

### Tier 1 inventory covers every package `default-stack` resolves

The packages that `DEFAULT_STACK_DEPLOYED` in `tests/structural/run-tier1.sh` lists, which the scratch-consumer inventory checks, must be the packages that `default-stack`'s committed lockfile resolves, its distinct `repo_url` values. A package the lockfile resolves but the list lacks is deployed without any inventory check.

```bash
bash <<'EOF'
set -euo pipefail
eval "$(grep '^DEFAULT_STACK_DEPLOYED=' tests/structural/run-tier1.sh)"
list=$(tr ' ' '\n' <<<"$DEFAULT_STACK_DEPLOYED" | sort -u)
lock=$(grep -E '^- repo_url: _local/' packages/default-stack/apm.lock.yaml | sed 's#.*_local/##' | sort -u)
echo "lockfile resolves $(wc -l <<<"$lock" | tr -d ' ') packages"
diff <(echo "$lock") <(echo "$list") && echo "inventory list matches the lockfile"
EOF
```

Expected: `lockfile resolves 11 packages`, then `inventory list matches the lockfile`, and exit `0`. Any `diff` output fails the check.

### A consumer of `default-stack` gains `sam-mode` and passes its audit

Install `packages/default-stack` by path into an empty scratch directory on all three targets, then run `apm audit --ci` there. The consumer must deploy `sam-mode` with an executable launcher under both skill roots, and the audit must pass every check.

```bash
bash <<'EOF'
set -u
repo=$PWD
APM="${APM:-$repo/.venv-apm/bin/apm}"
bounded() {
  if command -v timeout >/dev/null; then timeout "$@"
  elif command -v gtimeout >/dev/null; then gtimeout "$@"
  else perl -e 'alarm shift; exec @ARGV' "$@"; fi
}
c=$(mktemp -d)/consumer && mkdir -p "$c" && cd "$c" || exit 1
bounded 300 "$APM" install "$repo/packages/default-stack" --target cursor,claude,copilot > install.log 2>&1
echo "install exit $?"
status=0
for f in .claude/skills/sam-mode/SKILL.md .agents/skills/sam-mode/SKILL.md; do
  if [ -f "$f" ]; then echo "present $f"; else echo "MISSING $f"; status=1; fi
done
for f in .claude/skills/sam-mode/scripts/launch.sh .agents/skills/sam-mode/scripts/launch.sh; do
  if [ -x "$f" ]; then echo "executable $f"; else echo "NOT EXECUTABLE $f"; status=1; fi
done
bounded 300 "$APM" audit --ci > audit.log 2>&1; audit=$?
tail -n 1 audit.log
echo "audit exit $audit, consumer $c"
[ "$status" -eq 0 ] && [ "$audit" -eq 0 ]
EOF
```

Expected: `install exit 0`, two `present` lines, two `executable` lines, an audit line `[*] All 10 check(s) passed`, `audit exit 0`, and exit `0`.

### The documented drift on `default-stack`'s relativised lockfile

`docs/DEPENDENCY-CONTRACTS.md`, section "`apm audit --ci` reports drift on `default-stack`'s relativised lockfile", gives commands that a reader can rerun. This runs them as written, bounded, in the same order. It fails when the relativised lockfile audits clean, when the audit after a fresh install does not, when the drifted file count differs from the number the section states, or when the lockfile does not return to its committed form.

```bash
bash <<'EOF'
set -u
repo=$PWD
APM="${APM:-$repo/.venv-apm/bin/apm}"
bounded() {
  if command -v timeout >/dev/null; then timeout "$@"
  elif command -v gtimeout >/dev/null; then gtimeout "$@"
  else perl -e 'alarm shift; exec @ARGV' "$@"; fi
}
t=$(mktemp -d)
stated=$(grep -oE 'Drift detected: [0-9]+ file' docs/DEPENDENCY-CONTRACTS.md | head -n 1 | grep -oE '[0-9]+')
cd packages/default-stack || exit 1
bounded 300 "$APM" install --frozen --target cursor,claude,copilot >/dev/null 2>&1; i1=$?
python3 ../../scripts/relativise_lockfiles.py apm.lock.yaml
git diff --exit-code --stat apm.lock.yaml; d1=$?
bounded 300 "$APM" audit --ci > "$t/audit1.log" 2>&1; a1=$?
drift=$(grep -oE 'Drift detected: [0-9]+ file' "$t/audit1.log" | head -n 1 | grep -oE '[0-9]+')
bounded 300 "$APM" install --frozen --target cursor,claude,copilot >/dev/null 2>&1; i2=$?
bounded 300 "$APM" audit --ci > "$t/audit2.log" 2>&1; a2=$?
last=$(grep -E 'check\(s\) passed' "$t/audit2.log" | tail -n 1)
python3 ../../scripts/relativise_lockfiles.py apm.lock.yaml
git diff --exit-code --stat apm.lock.yaml; d2=$?
rm -rf "$t"
echo "install=$i1 diff=$d1 audit=$a1 drift=$drift stated=$stated reinstall=$i2 audit=$a2 [$last] restored=$d2"
[ "$i1" -eq 0 ] && [ "$d1" -eq 0 ] && [ "$a1" -ne 0 ] && [ -n "$drift" ] && [ "$drift" = "$stated" ] \
  && [ "$i2" -eq 0 ] && [ "$a2" -eq 0 ] && [ "$d2" -eq 0 ]
EOF
```

Expected: `install=0 diff=0`, a non-zero first `audit`, `drift` equal to `stated` (32 with apm-cli 0.32.0), `reinstall=0 audit=0` with `[*] All 10 check(s) passed`, `restored=0`, and exit `0`. Run the verification skill's Cleanup afterwards, because the installs deploy into `packages/default-stack`.

## Evidence

### Every changed package is bumped

`git fetch origin`, then `python3 scripts/versioning.py check origin/main` on the phase branch. It must exit `0` and name no package without a version bump. It needs the network and the moving tip of `origin/main`, so it is not rerun.

### A consumer of `default-stack` loses no file

Export `main` at the commit before this phase into a `mktemp -d` directory, install its `packages/default-stack` by path into an empty consumer on `--target cursor,claude,copilot`, and record `find . -type f ! -path './apm_modules/*' | LC_ALL=C sort` as `before.txt`. Do the same with a consumer installed from the phase branch, as in the consumer check above, giving `after.txt`. `comm -23 before.txt after.txt` must print nothing. Report the added files grouped by package, and separately each path present in both whose content differs. Only the consumer's `apm.yml`, `apm.lock.yaml` and `.gitignore` may differ, because they record the source path and the resolved packages. The baseline needs a tree from before the phase, so it is not rerun.
