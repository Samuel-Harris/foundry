# Phase `default-stack` checks

Phase `default-stack` makes the meta-package install `s-stack` in place of `planning`, which it now reaches through `s-stack`. It adds `s-stack` and `p-stack` to the Tier 1 scratch-consumer inventory, documents the new dependency graph and the drift that `apm audit --ci` reports on `default-stack`'s relativised lockfile, and makes `scripts/relativise_lockfiles.py` write the same lockfile from every checkout path.

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

### `default-stack`'s lockfile is the same from another checkout path

Check out `HEAD` in a second worktree at a fresh `mktemp -d` path, install `packages/default-stack` there with `--frozen`, relativise its lockfile and diff it against the committed one. APM writes the checkout's absolute path into the lockfile and into the name of the directory that p-stack's deployed links point at, so any part of the committed lockfile that still depends on the path it was generated at shows up as a diff. The second worktree holds only `HEAD`, so commit the work first.

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
git worktree add -q --detach "$t/x" HEAD || exit 1
cd "$t/x/packages/default-stack" || exit 1
bounded 300 "$APM" install --frozen --target cursor,claude,copilot >/dev/null 2>&1; i=$?
python3 ../../scripts/relativise_lockfiles.py apm.lock.yaml; r=$?
git diff --exit-code --stat apm.lock.yaml; d=$?
cd "$repo" && git worktree remove --force "$t/x" && rm -rf "$t"
echo "install=$i relativise=$r diff=$d"
[ "$i" -eq 0 ] && [ "$r" -eq 0 ] && [ "$d" -eq 0 ]
EOF
```

Expected: no `--stat` output, the last line `install=0 relativise=0 diff=0`, and exit `0`. Any changed line in `apm.lock.yaml` fails the check.

### The documented drift on `default-stack`'s relativised lockfile

`docs/DEPENDENCY-CONTRACTS.md`, section "`apm audit --ci` reports drift on `default-stack`'s relativised lockfile", gives commands that a reader can rerun, with the line each `apm audit --ci` ends on in a comment. This runs them as written, bounded, in the same order. On the same tree as the first audit, it also runs `apm audit --ci --format json` to read which checks failed and which files drifted. It fails when the relativised lockfile is not the committed one, when the first audit does not print the summary line the section states, when the failed checks are not the ones the section names in brackets after that line, when the number of drifted files differs from the number of p-stack files the section says carry the hashed directory, when the audit after a fresh install does not print the second line the section states, or when the lockfile does not return to its committed form.

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
doc=docs/DEPENDENCY-CONTRACTS.md
stated1=$(sed -nE 's/^apm audit --ci +# (\[x\] [0-9]+ of [0-9]+ check\(s\) failed) \(.*$/\1/p' "$doc" | head -n 1)
stated_failed=$(sed -nE 's/^apm audit --ci +# \[x\] .* failed \(([^)]*)\)$/\1/p' "$doc" | head -n 1 | tr -d ' ' | tr ',' '\n' | LC_ALL=C sort | paste -sd, -)
stated_files=$(grep -oE 'so [0-9]+ deployed p-stack skill files' "$doc" | head -n 1 | grep -oE '[0-9]+')
stated2=$(sed -nE 's/^apm audit --ci +# (\[\*\] .*)$/\1/p' "$doc" | head -n 1)
cd packages/default-stack || exit 1
bounded 300 "$APM" install --frozen --target cursor,claude,copilot >/dev/null 2>&1; i1=$?
python3 ../../scripts/relativise_lockfiles.py apm.lock.yaml; r1=$?
git diff --exit-code --stat apm.lock.yaml; d1=$?
bounded 300 "$APM" audit --ci > "$t/audit1.log" 2>&1; a1=$?
grep -qF "$stated1" "$t/audit1.log"; s1=$?
bounded 300 "$APM" audit --ci --format json --output "$t/audit1.json" >/dev/null 2>&1
failed=$(python3 -c 'import json, sys; print(",".join(sorted(c["name"] for c in json.load(open(sys.argv[1]))["checks"] if not c["passed"])))' "$t/audit1.json")
files=$(python3 -c 'import json, sys; print(len(json.load(open(sys.argv[1]))["drift"]["drift"]))' "$t/audit1.json")
bounded 300 "$APM" install --frozen --target cursor,claude,copilot >/dev/null 2>&1; i2=$?
bounded 300 "$APM" audit --ci > "$t/audit2.log" 2>&1; a2=$?
grep -qF "$stated2" "$t/audit2.log"; s2=$?
python3 ../../scripts/relativise_lockfiles.py apm.lock.yaml; r2=$?
git diff --exit-code --stat apm.lock.yaml; d2=$?
rm -rf "$t"
echo "stated [$stated1] ($stated_failed) files=$stated_files, then [$stated2]"
echo "install=$i1 relativise=$r1 diff=$d1 audit=$a1 summary=$s1 failed=$failed files=$files"
echo "reinstall=$i2 audit=$a2 summary=$s2 relativise=$r2 restored=$d2"
[ -n "$stated1" ] && [ -n "$stated_failed" ] && [ -n "$stated_files" ] && [ -n "$stated2" ] \
  && [ "$i1" -eq 0 ] && [ "$r1" -eq 0 ] && [ "$d1" -eq 0 ] && [ "$a1" -ne 0 ] && [ "$s1" -eq 0 ] \
  && [ "$failed" = "$stated_failed" ] && [ "$files" = "$stated_files" ] \
  && [ "$i2" -eq 0 ] && [ "$a2" -eq 0 ] && [ "$s2" -eq 0 ] && [ "$r2" -eq 0 ] && [ "$d2" -eq 0 ]
EOF
```

Expected with apm-cli 0.32.0: `stated [[x] 2 of 9 check(s) failed] (content-integrity,drift) files=32, then [[*] All 10 check(s) passed]`, then `install=0 relativise=0 diff=0`, a non-zero first `audit`, `summary=0 failed=content-integrity,drift files=32`, then `reinstall=0 audit=0 summary=0 relativise=0 restored=0`, and exit `0`. Run the verification skill's Cleanup afterwards, because the installs deploy into `packages/default-stack`.

## Evidence

### Every changed package is bumped

`git fetch origin`, then `python3 scripts/versioning.py check origin/main` on the phase branch. It must exit `0` and name no package without a version bump. It needs the network and the moving tip of `origin/main`, so it is not rerun.

### A consumer of `default-stack` loses no file

Export `main` at the commit before this phase into a `mktemp -d` directory, install its `packages/default-stack` by path into an empty consumer on `--target cursor,claude,copilot`, and record `find . -type f ! -path './apm_modules/*' | LC_ALL=C sort` as `before.txt`. Do the same with a consumer installed from the phase branch, as in the consumer check above, giving `after.txt`. `comm -23 before.txt after.txt` must print nothing. Report the added files grouped by package. Then compare each path present in both after replacing every `_local/<12 hex digits>/` with `_local/<slot>/` in each copy. APM names p-stack's materialised directory after a hash of the source tree's absolute path, and p-stack's deployed links name that directory, so those files differ between any two consumers installed from trees at different paths while nothing is lost. After the replacement, only the consumer's `apm.yml`, `apm.lock.yaml` and `.gitignore` may differ, because they record the source path and the resolved packages. Report how many files differ only by that directory name. The baseline needs a tree from before the phase, so it is not rerun.
