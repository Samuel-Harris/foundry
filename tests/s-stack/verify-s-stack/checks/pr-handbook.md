# Phase `pr-handbook` checks

Phase `pr-handbook` ships `packages/s-stack/.apm/skills/sam-mode/handbooks/pr-creator.md`, the PR creator's handbook, and `packages/s-stack/.apm/skills/sam-mode/references/pr-commands.md`, which holds the one script the PR creator runs. The script is the behaviour, so the checks extract it at run time and run it the way the handbook does: copied into `pr.sh` outside the repository and called as `OWN=<own branches> PUSHED=<pushed heads> bash pr.sh refresh <phase branch> <default branch> <spec> [<commit> ...]` and `OWN=<own branches> MERGED=<merged branches> PUSHED=<pushed heads> bash pr.sh prove ...`. Run each block from anywhere inside the repository with `/bin/bash`, as written, because the agent shell is zsh. The script then runs under the same bash.

## Rerun

### The script block parses

Every fenced `bash` block in `references/pr-commands.md` passes `bash -n` as extracted, and exactly one of them is the script, which answers `refresh` and `prove`. Expected: a `bash -n ok` line for each block, one `script block` line, and exit `0`.

```bash
/bin/bash <<'CHECK'
md="$(git rev-parse --show-toplevel)/packages/s-stack/.apm/skills/sam-mode/references/pr-commands.md"
d=$(mktemp -d "${TMPDIR:-/tmp}/pr-commands.XXXXXX"); trap 'rm -rf "$d"' EXIT
awk '/^```bash$/ { b = 1; n++; next } /^```$/ { b = 0; next } b { print > (dir "/block" n ".sh") }' dir="$d" "$md"
status=0 scripts=0
for f in "$d"/block*.sh; do
  [ -e "$f" ] || { echo "no bash block in $md"; exit 1; }
  if bash -n "$f"; then echo "bash -n ok $(basename "$f")"; else echo "bash -n FAILED $(basename "$f")"; status=1; fi
  grep -q -E '^ *refresh \| prove\)' "$f" && { echo "script block $(basename "$f")"; scripts=$((scripts + 1)); }
done
[ "$scripts" = 1 ] || { echo "expected one script block, found $scripts"; status=1; }
exit $status
CHECK
```

### Scratch repositories

The block builds throwaway repositories under `$TMPDIR` with git's global and system configuration switched off, and deletes them on exit. Each repository has a bare `origin` that refuses every non-fast-forward push and every branch deletion, so a force-push by the script or by a round fails its case. A forge rewrite, as GitHub makes when a stack parent merges, is written straight into the bare repository instead. A forge rebase onto a `main` that moved since the parent merged changes the tree as well.

`main` holds a package `pkg/` whose `apm.yml` has `version:` on its second line and `description:` on its third, an `apm.lock.yaml` beside each `apm.yml` that lists the package's other files, a twelve-line `shared.txt` and a `README`. The stand-in regenerate command sets `pkg`'s `version:` to the patch after `origin/main`'s and rewrites every lockfile from the tree, and commits with the regenerate subject when that changed anything. The script's parameter lines stay as the reference file ships them.

Each case follows the handbook's round order. A round starts with `git fetch origin` and records every branch on `origin`. Then, for each branch it builds, bottom of the stack first, it removes any worktree a stopped round left at the branch's path and runs `git worktree add --no-track -B <branch> <path> origin/<branch>`. A new branch starts instead from its base as the refresh reads it: the local branch of a parent named in `OWN`, `origin/<parent>` for any other parent, or `origin/main` when the base is `main`. In that worktree it runs `bash pr.sh refresh phase origin/main <spec> <commits>` with `OWN` set and the regenerate command, and removes the worktree. When every branch has had that, the round proves the local branches with `bash pr.sh prove orch phase origin/main <spec> ...`, with every open pull request, and with a merged one only where a case lists it. Only when the proof prints `EQUAL` does it run `git push -u origin <branch>`, bottom first, for each branch whose `origin/<branch>` is missing or differs. On any `STOP` or on `NOT EQUAL` it pushes nothing, resets each branch it built to `origin/<branch>` or deletes a new one, and fails the case if any branch on `origin` moved. A crashed round stops after the refresh and regenerate of a branch, with no proof and no reset. `OWN` names the case's own pull request branches: every branch the case builds is added to it before its first refresh, and every refresh and proof is given it. A case that tests the list itself sets it before a build. `MERGED` names the case's own pull request branches that have merged: a squash or true merge of a branch in `OWN` adds it, and every proof is given it. `PUSHED` records, after every round that proves `EQUAL`, the head `origin/<branch>` then holds for each branch the round built, pushed in that round or not, as `<branch>=<sha>`. It starts empty in each new repository, and every refresh and proof is given it; a branch that GitHub or the developer moved keeps the head recorded after its last `EQUAL` round. A case that tests the list itself sets it before a round. `orch` and `phase` are local, never pushed. The orchestrator branch carries `.foundry/`, and the phase merges it with `git merge --no-ff`. Another phase's pull request is cut from `main`, ends with a regenerate commit and exists only on `origin`. A squash merge commits the merged tree onto `main` with one parent and keeps the merged branch. A round's added commits are counted along the first parent from the old `origin/<branch>`.

A round keeps the guarantees when the old `origin/<branch>` is an ancestor of the new one, `origin/main` is an ancestor of it, and it adds at most one merge commit and one regenerate commit. Each case prints `PASS <case>` or `FAIL <case>: <output>`, and the block ends with `<n> failed` and exits `0` only when no case failed.

| Case | Scenario | Expected |
| --- | --- | --- |
| `done-when build` | Phase commits `a` (with lockfile and `apm.yml` hunks), a `.foundry/` status commit, `b` (on `shared.txt` line 2, which another phase's open pull request `other-pr` also changed), a binary, and a lockfile-and-status commit. `pr1:main` takes `a`; `pr2:other-pr` takes the other three. | Both exit `0`. Hand-written diffs are `a.txt` and `b.txt img.bin shared.txt`. The binary is byte-identical. `pr1`'s carried commit ends with `(cherry picked from commit <a>)`. |
| `done-when correct split` | `pr1:main pr2:other-pr` | `EQUAL`, exit `0` |
| `done-when drops a change` | `pr1:main` alone | `FAIL b.txt has not landed and is in no open pull request, so it needs a new pull request`, `NOT EQUAL`, exit `1` |
| `done-when adds a change` | `pr1` plus a commit adding `extra.txt` | `FAIL pr1x: it changes extra.txt, which the phase does not`, `NOT EQUAL` |
| `done-when .foundry` | `pr1` plus `.foundry/leak.md` | `FAIL pr1f: contains .foundry/leak.md`, `NOT EQUAL` |
| `done-when regenerate a.txt` | `pr1` plus a regenerate commit that changes `a.txt` | `FAIL pr1r: regenerate commit <sha> changes a.txt`, `NOT EQUAL` |
| `done-when regenerate deps` | `pr1` plus a regenerate commit that changes `deps:` in `apm.yml` | that commit named with `-deps: []` and `+deps: [x]`, `NOT EQUAL` |
| `done-when squash-merged parent` | `other-pr` squash-merged, then `pr2`'s round as `pr2:main::other-pr` | guarantees kept, exactly one merge and one regenerate commit, `shared.txt` line 2 `line 2 child`, diff `b.txt img.bin shared.txt`, proof `pr1:main pr2:main::other-pr` `EQUAL` |
| `guarantee up to date` | A round straight after the build | `up to date with`, `origin/pr1` unchanged |
| `guarantee main moves` | `main` changes `README`, then a round | guarantees kept, one merge and one regenerate commit, `EQUAL` |
| `guarantee version taken` | `main` raises `version:` to the branch's `"0.1.1"`, then a round | guarantees kept, `version: "0.1.2"`, `EQUAL` |
| `guarantee interrupted` | `main` moves, a round crashes after refresh and regenerate and before its proof, then a full round | `origin/pr1` unchanged by the first. The second keeps the guarantees over the old `origin/pr1`, with one merge and one regenerate commit, and `EQUAL`. |
| `guarantee repeated` | Two more rounds | `origin/pr1` unchanged |
| `guarantee fix rerun` | A fix round, then the same round again with the same fix commit | the second leaves `origin/pr1` unchanged |
| `hand edit in a merge` | `pr1h` merges `main` by hand and edits `a.txt` inside the merge commit | `FAIL pr1h: its head differs from its target tree`, `a.txt` listed, `NOT EQUAL` |
| `forge rewrite` | A same-phase stack `parent:main`, `child:parent`. `parent` is squash-merged, the forge rebases `child` onto `main` with the same tree, `main` moves, then `child:main::parent` | guarantees kept over the rewritten head, diff `c.txt`, `EQUAL` |
| `round 1 squash step` | Child stacked on another phase's `parent`, which is squash-merged; then `main` fixes `parent`'s line 2; child's round as `child:main::parent` | line 2 is `main`'s fix, diff `c.txt`, `EQUAL` |
| `round 1 version fix` | A fix round editing `description:`, next to the `version:` line the branch's regenerate commit changed | exit `0`, `version: "0.1.1"` and the new description, `EQUAL` |
| `round 1 version build` | A first build editing `description:`, while the orchestrator branch holds another phase's `version:` raise | exit `0`, the new description, diff `a.txt`, `EQUAL` |
| `round 1 newer orchestrator` | Another phase changes `shared.txt` line 5 two lines from the phase's line 3, the phase merges the newer orchestrator branch, then a fix round | exit `0`, lines 3 to 5 are `line 3 phase`, `line 4`, `line 5`, diff `a.txt b.txt shared.txt`, `EQUAL` |
| `round 1 two squashed` | `pr3:main:depA,depB`, both squash-merged, then `pr3:main::depA,depB` | guarantees kept, the child's `a.txt` and `b.txt`, `EQUAL` |
| `round 1 stack moves` | A same-phase stack after `main` moves: parent's round, then child's as `child:parent` | both keep the guarantees, child's diff against parent is `c.txt`, one merge base, `EQUAL` |
| `round 1 spaces` | Child and a squash-merged parent both changed `docs dir/read me.md`, and `main` raised `my pkg/apm.yml`'s `version:` beside the child's `description:` edit | line 2 `line 2 child`, `my pkg/apm.yml` with `main`'s version and the child's description, `EQUAL` |
| `round 2 conflict, commit` | `main` changes the line 5 that `pr1` owns. A round stops; the phase merges `main` taking `main`'s side, then commits its resolution; a round with that commit | first: exit `1`, `STOP shared.txt changed on origin/main after the phase last took it, so the phase must merge it first`, `origin/pr1` unchanged. Then: guarantees kept, line 5 is the resolution, `EQUAL`. |
| `round 1 and 2 conflict, merge` | The same, but the phase resolves inside its merge of `main`, and the next round passes no commit | the same stop, then guarantees kept, line 5 is the resolution, `EQUAL` |
| `round 2 clean merge` | The phase merges `main` cleanly, then a round | `EQUAL` |
| `round 2 orchestrator merged, one line` | The orchestrator merges the phase, a fix changes the same line, the orchestrator merges again, then a round | up to date, line 5 fixed, `EQUAL` |
| `round 2 orchestrator merged, delete` | The phase deletes `README`, the orchestrator merges the phase | `EQUAL`, no `README` on `pr1` |
| `round 2 merge commit` | Parent `pr1` merged into `main` with a merge commit, then `pr2:main::pr1` | guarantees kept, diff `b.txt`, `EQUAL` |
| `round 2 row 3 to row 2` | `pr3:main:depA,depB`, `depA` squash-merged; `depB` lacks the new `main`. First `pr3:depB::depA`, then `pr3:main:depB:depA` | first: exit `1`, `STOP depB does not hold origin/main, so pr3 must target it with depB merged in`, `origin/pr3` unchanged. Then guarantees kept, both child lines, `EQUAL`. |
| `round 2 grandchild` | Stack `pr1`, `pr2`, `pr3`, where `pr2` rewrites `pr1`'s line. `pr1` squash-merged, the forge rewrites `pr2` only, then `pr2:main::pr1` and `pr3:pr2` | both exit `0`, `pr2` an ancestor of `pr3`, `pr3`'s diff against `pr2` is `three.txt`, line 2 `line 2 Y`, `EQUAL` |
| `round 2 delete package` | `main` holds package `old/` with its lockfile; the phase deletes `old/` | nothing under `old/` on `pr1`, `EQUAL` |
| `round 2 undeclared` | `pr2` cut from `pr1`'s unpushed head in the same round, given as `pr2:main` | `NOT EQUAL`, a `FAIL` line naming `a.txt`, neither branch pushed |
| `adjacent-line STOP` | Stack `pr1` (line 5) and `pr2` (line 6) of `shared.txt`; a fix to `pr1`'s line 5 | `pr1`'s round exits `1` with `STOP shared.txt conflicts outside generated content`, `STOP <sha> fix: pr1 does not apply` and `STOP the branch is back at <old head>`, `origin/pr1` unchanged |
| `uncarried, open` | A fix to `b.txt` that `pr2` does not carry | `FAIL b.txt: pr2 lacks phase commits <sha> fix: b;, so they need a pull request` |
| `uncarried, merged` | After `pr2` carries it and `pr1` is squash-merged, a fix to `a.txt`; then a round of `pr2` alone | `FAIL a.txt has not landed and is in no open pull request, so it needs a new pull request`. The round prints a `FAIL` for `a.txt` and `NOT EQUAL`, and `pr2` and `origin/pr2` are unchanged. |
| `uncarried, new pull request` | A new pull request `pr1b:main::pr1` carrying that fix | diff `a.txt`, `a fixed`, proof `pr2:main pr1b:main::pr1` `EQUAL` |
| `leak` | Another phase changes `shared.txt` line 9, the phase takes it through the orchestrator branch, then a fix on line 4 | line 9 is `line 9`, lines 3 and 4 the phase's, diff `a.txt shared.txt`, `EQUAL` |
| `identity` | Two phase commits with the same author, date and subject; a round of `pr1` carrying only the first | `FAIL shared.txt: pr1 lacks phase commits <second> fix: review;, so they need a pull request`, nothing pushed. Then a round of `pr1` with the first and `pr2:pr1` with the second: `EQUAL`, `pr1` with line 3 changed and line 9 not, `pr2` with line 9. |
| `assumption, fast-forward` | The phase fast-forwards to the orchestrator branch after the orchestrator merged it | `FAIL pr1: it changes a.txt, which the phase does not` |
| `assumption, orchestrator commit` | The orchestrator commits `orch-fix.txt` before the phase branches, then the first build | `FAIL orch-fix.txt has not landed and is in no open pull request, so it needs a new pull request`, `NOT EQUAL`, nothing pushed |
| `missing branch` | Specs naming a merged dependency `gone` and an open dependency `gone2`, neither a branch | each exits `1` with `STOP <branch> is not a branch here`, `origin/pr1` unchanged |
| `wrong result, revert` | Phase commit `a` adds `debug.txt` and edits `README`, and `pr1` is built from it; a later phase commit reverts both. Then a round with no commit, then a fix round carrying the revert | the proof prints `FAIL debug.txt: pr1 lacks phase commits <sha> fix: revert debug;, so they need a pull request`, the same for `README`, `NOT EQUAL`. The round without the revert prints the same `FAIL` and leaves `pr1` and `origin/pr1` unchanged. The fix round gives `EQUAL` and no `debug.txt` on `pr1`. |
| `wrong result, origin/ names` | A same-phase stack `pr1:main`, `pr2:pr1` sharing `shared.txt` | the proof prints `EQUAL` with plain names, with `origin/` on the pull requests, and with `origin/` everywhere |
| `stop, shared path` | Stack `pr1` (line 5) and `pr2` (line 9) of `shared.txt`; `main` changes line 5. A round; the phase merges `main` and resolves line 5 in the merge; a round; the phase commits a further resolution; a round with that commit | each round exits `1` with exactly `STOP shared.txt conflicts outside generated content`, `STOP <sha> <subject> does not apply` and `STOP shared.txt is a shared path, so the stop is permanent: no merge or commit on the phase clears it, and it needs a decision`, the last followed by `STOP the branch is back at <old head>`. `pr1` and `origin/pr1` unchanged throughout. |
| `stop, owned path changed cleanly` | Another phase's pull request changes `shared.txt` line 10 and is squash-merged; `pr1` owns `shared.txt` (line 3). A round; then the phase merges `main` and a round | first: exit `1` with exactly `STOP shared.txt changed on origin/main after the phase last took it, so the phase must merge it first`, `pr1` and `origin/pr1` unchanged. Then: guarantees kept, lines 3 and 10 both present, `EQUAL`. |
| `stop, forge-rewritten row 3` | `ours:main:x2`, where another phase's `x2` is stacked on `x1` and has `x3` stacked on it. `x1` is squash-merged and the forge rewrites `x2`. Rounds as `ours:main:x2:x1`, then `x2` is squash-merged and a round as `ours:main::x2,x1` | each round exits `1` with exactly `STOP ours would carry x2.txt, which the phase does not change`, also after `x2` merged, and leaves `ours` and `origin/ours` where they started. The proof still prints `FAIL ours: it changes x2.txt, which the phase does not` and `NOT EQUAL` after each round. |
| `stop, delegate merge` | The phase merges a delegate branch adding `d.txt` with `git merge --no-ff`; `pr1:main` built from the session's commit and the delegate's | the refresh exits `1` with exactly `STOP pr1 would carry d.txt, which the phase does not change`, and nothing is pushed to `origin/pr1` |
| `stop, file to directory` | `main` has a file `notes`; the phase replaces it with `notes/one.md`; `pr1:main` | the refresh exits `1`, printing git's own error, then `STOP notes cannot be written into the tree, as when a file and a directory share its name`, then `STOP the branch is back at <old head>`, and nothing is pushed to `origin/pr1` |
| `stop, directory to file` | The reverse: `main` has `notes/one.md`; the phase replaces the directory with a file `notes` | the same output as `stop, file to directory`, which the handbook documents in the same row |
| `chained rule` | `pr1` (line 2 and `a.txt`) and `pr2` (line 11 and `b.txt`) both change `shared.txt`; a first build as `pr1:main` and `pr2:main`, then one as `pr1:main` and `pr2:pr1` | unchained: `FAIL shared.txt is in pr1 and pr2, which are not in one stack`, in either order, `NOT EQUAL`, and neither branch pushed or left locally. Chained: `pr2` holds `pr1`, `pr2`'s diff against `pr1` is `b.txt shared.txt`, `EQUAL`. |
| `merged listed, parent` | Stack `parent` (line 2), `child` (`c.txt`); `parent` squash-merged, then `main` changes line 2; `child`'s round as `child:main::parent` | proof `child:main::parent` prints `FAIL shared.txt has not landed and is in no open pull request, so it needs a new pull request`; proof `parent:main child:main::parent` prints `EQUAL` |
| `merged listed, new pull request` | `pr1` squash-merged, then a fix to `a.txt`; a new pull request `pr1b:main::pr1` carrying the fix | its round exits `0` with `a fixed`, and proof `pr1:main pr1b:main::pr1` prints `EQUAL` |
| `delegate, first-parent commits only` | The phase merges a delegate branch adding `d.txt` with `git merge --no-ff`; the first build of `pr1:main` is given only the session's commit `z.txt` | the round prints `FAIL <merge> merges <delegate commit>, whose commits are not phase commits: a delegate's branch merged into the phase` and `NOT EQUAL`, and nothing is pushed or left locally |
| `delegate, rebuild` | The phase session resets the phase to before the merge and takes the delegate's commit with `git cherry-pick -x`; a round with both commits | exit `0`, diff `d.txt z.txt`, `EQUAL` |
| `delegate after a push` | `pr1` is built and pushed, then the phase merges a delegate branch and adds `y.txt`; a fix round with that commit; then the rebuild with `git cherry-pick -x` and a round with the delegate's commit and the re-picked one | the fix round prints the delegate `FAIL` and leaves `pr1` and `origin/pr1` unchanged. After the rebuild, guarantees kept over the old `origin/pr1`, diff `d.txt y.txt z.txt`, `EQUAL`. |
| `own-phase stack, unpushed parent` | A first build of `parent:main` and `child:parent` in one round, where `child`'s round reads the unpushed `parent`; then a fix to `parent`'s line 2 in a round of both | neither branch is on `origin` before the proof. After it, `child` holds `parent`, diff `c.txt`. In the fix round `origin/parent` is unchanged until the proof; then both keep the guarantees, `child` has the fix on line 2 and diff `c.txt`. |
| `another phase's local parent` | Another phase's `other-pr` is on `origin`, and a local `other-pr` is ahead of it with an unproved commit adding `u.txt`; `child:other-pr` | exit `0`; `child` holds `origin/other-pr` and not the local `other-pr`, has `o.txt` as `origin` has it and no `u.txt`, diff `c.txt`, `EQUAL` |
| `retry after a stopped build` | A first build as `pr1:main::gone` stops; a build crashes after its refresh, leaving the local `pr1` and a worktree checked out on it; then a full build | the stop prints exactly `STOP gone is not a branch here`, nothing pushed and no local `pr1`. The full build starts again, diff `a.txt`, exactly one commit with `(cherry picked from commit <a>)`, `EQUAL`. |
| `own-phase child extends its parent's file` | Parent adds a two-line `f.txt`; the child extends it to five lines; a first build of `parent:main` and `child:parent` in one round | all three exit `0`, `EQUAL`, `child` holds `parent`, `child`'s diff against `parent` is `f.txt`, `parent` has two lines and `child` five |
| `another phase stacked on ours, local ahead` | Own `pr1` is pushed. Another phase's `x` is stacked on `pr1` and carries its own commit with `git cherry-pick -x`, and a local `x` is ahead of `origin/x` with another carried commit adding `u.txt`. Then `pr2:x` | exit `0`; `origin/pr2` holds `origin/x` and not the local `x`, has no `u.txt`, diff against `origin/x` is `b.txt`, proof `pr1:main pr2:x` `EQUAL` |
| `delegate after the orchestrator merged` | `pr1` is built and pushed; the phase merges a delegate branch adding `d.txt` and adds `y.txt`; the orchestrator merges the phase; a fix round with the `y.txt` commit | exit `1`, the delegate `FAIL` line naming the merge and the delegate commit, `NOT EQUAL`, `pr1` and `origin/pr1` unchanged, no `d.txt` on `origin/pr1` |
| `mixed stack, parent only merges` | Another phase's `x` ← own `pr1` ← own `pr2`. `x` takes a fix and merges a moved `main`; then a round of both in which `pr1` carries no commit and only merges `x` | all three exit `0` with no `STOP`, both keep the guarantees, `pr2` holds the new `pr1` and `origin/main`, `pr2` has `x`'s fix, diff against `pr1` `c.txt`, `EQUAL` |
| `mixed stack, crashed foreign branch` | Own `pr1` ← another phase's `x`, which carries its own commit with `git cherry-pick -x` ← own `pr2`. A fix round of `pr1`; then `x`'s crashed round leaves a local `x` ahead of `origin/x` that merges `origin/pr1` and adds `u.txt`; then a round of `pr2` | exit `0`; `origin/pr2` holds `origin/x`, not the local `x`, has no `u.txt`, diff against `origin/x` `b.txt`, proof `pr1:main pr2:x` `EQUAL` |
| `branch missing from OWN` | A pushed own stack `parent:main`, `child:parent`; a fix round refreshes `parent` locally; then `child`'s refresh with `OWN` naming only `child` | the refresh exits `0`, and `child` holds `origin/parent` and not the local `parent` with the fix; nothing is pushed |
| `stale owned path, another phase's branch` | `pr1` owns `shared.txt` line 3 and depends on another phase's `other-pr`, first stacked as `child:other-pr`, then as `child:main:other-pr`. `other-pr` then changes line 10; a round; the phase merges `origin/other-pr`; a round | the first round exits `1` with exactly `STOP shared.txt changed on <other-pr> after the phase last took it, so the phase must merge it first` and leaves `child` and `origin/child` unchanged. The second prints no delegate `FAIL`, keeps the guarantees, holds lines 3 and 10, and proves `EQUAL`. |
| `refresh order, child's fix on parent's fix` | Stack `pr1:main`, `pr2:pr1` in one file `m.py`. A fix to `pr1` and a child fix that changes the parent fix's line, in one round | all three exit `0` with no `STOP`, both keep the guarantees, `pr2`'s `m.py` is the phase's, `EQUAL` |
| `refresh order, row-3 build` | A first build of `pr1:main`, `pr2:pr1`, then `pr3:main:pr1`, whose commit extends `pr1`'s `a.txt` and adds `c.txt` | all exit `0` with no `STOP`, `pr3` holds the phase's `a.txt` and `c.txt`, diff `a.txt c.txt`, `EQUAL` |
| `refresh order, chained spanning fix` | `pr1:main` and `pr2:main` built; a fix changes both `a.txt` and `b.txt`; a round of `pr1:main` and `pr2:pr1` with the fix | all exit `0` with no `STOP`, `pr2` keeps the guarantees and holds `pr1`, diff against `pr1` `a.txt b.txt`, both fixed, `EQUAL` |
| `split fault` | The same fix given to `pr1` while `pr1:main` and `pr2:main` stay unchained | exit `1` with `STOP <sha> fix: a and b also changes b.txt, which pr1 and its base do not hold, so it spans two pull requests and the split must change` and `STOP the branch is back at <old head>`, no shared-path `STOP`, `pr1` and `origin/pr1` unchanged |
| `another phase stacked on ours, changed later` | Own `pr1` ← another phase's `x` ← own `pr2:x`, where `pr2` owns `shared.txt` line 3. `x` then changes line 10; a round; the phase merges `origin/x`; a round | first: exit `1` with exactly `STOP shared.txt changed on origin/x after the phase last took it, so the phase must merge it first`, `pr2` and `origin/pr2` unchanged. Then: guarantees kept, lines 3 and 10 both present, `EQUAL`. |
| `stale local copy of a rewritten parent` | `ours:x2` on another phase's `x2`, stacked on `x1`, with a local `x2` left at its old head. `x1` is squash-merged and the forge rewrites `x2`; a round as `ours:x2:x1` | exit `1` with `STOP ours would carry x2.txt, which the phase does not change`, `ours` and `origin/ours` unchanged |
| `glob path` | `main` has `app/i/page.tsx`; the phase adds `app/[id]/page.tsx` | exit `0`, `origin/pr1` has `app/[id]/page.tsx` as the phase wrote it and `app/i/page.tsx` as `main` has it, diff `app/[id]/page.tsx`, `EQUAL` |
| `local branch outside OWN` | A local `other-pr`, never pushed and not in `OWN`, with an unproved commit; `child:other-pr` | exit `1` with `STOP other-pr is not a branch here`, nothing pushed, no local `child` left |
| `OWN refusal` | A refresh of `pr1:main` with `OWN=other` | exit `1` with exactly `STOP pr1 is not in OWN, so it is not one of this phase's pull request branches`, `pr1` not moved |
| `merged one skipped` | `pr1:main` and `pr2:main`; `pr1` squash-merged and `main` moves; a round of `pr2` alone, proved with `pr1:main pr2:main` | exit `0`, `pr1` and `origin/pr1` unchanged, `pr2` keeps the guarantees, diff `b.txt`, `EQUAL` |
| `edit inside a merge, shared path` | Another phase changes `shared.txt` line 9; the phase merges the orchestrator branch and, inside that merge, edits its own line 2 of `shared.txt` and its owned `a.txt`; a round | exit `1`, `FAIL <merge> edits shared.txt inside the merge, so no pull request carries the edit`, no such line for `a.txt`, `NOT EQUAL`, `pr1` and `origin/pr1` unchanged |
| `edit inside a merge, other path` | The same merge edits `README`, which no phase commit changes | exit `1`, `FAIL <merge> edits README inside the merge, so no pull request carries the edit`, `NOT EQUAL`, `pr1` and `origin/pr1` unchanged |
| `developer commit` | The developer commits a suggestion to `a.txt` on `origin/pr1`; a round; then the phase takes it with `git cherry-pick -x` and a round carries that commit | first: exit `1`, `DEVELOPER-COMMITS pr1 <sha>`, `NOT EQUAL`, `pr1` and `origin/pr1` still at the developer's commit. Then: exit `0`, no `DEVELOPER-COMMITS`, guarantees kept over the developer's commit, the suggestion kept, `EQUAL`. |
| `Update branch` | `main` moves and `origin/pr1` merges it, as GitHub's "Update branch" does; a round | exit `0`, no `DEVELOPER-COMMITS`, guarantees kept over that merge, diff `a.txt`, `EQUAL` |
| `Update branch with an edit` | The same merge also edits `a.txt`; a round; then the phase commits the merge's `a.txt` and a round carries that commit | first: exit `1`, `DEVELOPER-COMMITS pr1 <merge>`, `NOT EQUAL`, `pr1` and `origin/pr1` unchanged, the developer's `a.txt` kept. Then: exit `0`, no `DEVELOPER-COMMITS`, guarantees kept over the merge, the edit kept, one commit with `(cherry picked from commit <fix>)`, `EQUAL`. |
| `landed content` | `pr1`, built with no trailer, is squash-merged; a fix to `a.txt` in a new `pr1b:main::pr1` | exit `0`, `a fixed`, diff `a.txt`. The proof `pr1:main pr1b:main::pr1`, which lists the merged one as the handbook says, prints `EQUAL`. |
| `developer's new file` | The developer commits a new `a_test.txt` on `origin/pr1`; a round; then the phase takes it with `git cherry-pick -x` and a round carries that commit | first: the refresh exits `1` and prints exactly `DEVELOPER-COMMITS pr1 <sha>`, `pr1` and `origin/pr1` still at the developer's commit. Then: exit `0`, no `DEVELOPER-COMMITS`, guarantees kept over it, diff `a.txt a_test.txt`, `EQUAL`. |
| `Update branch on a stacked child` | A same-phase stack `parent:main`, `child:parent`; a fix round of `parent`; `origin/child` merges `origin/parent`, as GitHub's "Update branch" does; a round of both | all three exit `0`, no `DEVELOPER-COMMITS`, `child` holds the merge and `origin/parent`, line 2 is the fix, diff against `parent` `c.txt`, `EQUAL` |
| `developer commit, then squash-merged` | Stack `pr1:main` (`a.txt`), `pr2:pr1` (`b.txt`). The developer commits a suggestion to `a.txt` on `origin/pr1`, the phase has not taken it, and `pr1` is squash-merged. A round of `pr2:main::pr1`, proved with `pr1:main pr2:main::pr1`; then the phase merges `origin/main`, keeping its `a.txt`, and a round | first: exit `1`, exactly `FAIL a.txt differs between the phase and origin/main and no open pull request holds it: if the phase changed it, open a pull request for its commits; if origin/main changed it, for example a developer commit on a merged pull request, merge origin/main into the phase`, no `DEVELOPER-COMMITS`, `NOT EQUAL`, `pr2` and `origin/pr2` unchanged. Then: exit `0`, guarantees kept, `pr2` has the suggestion and diff `b.txt`, `EQUAL`. |
| `developer commit, then true-merged` | The same with `pr1` and `pr2:main` independent, and `pr1` merged with a merge commit; rounds of `pr2:main` proved with `pr1:main pr2:main` | the same two-remedy `FAIL` and `NOT EQUAL`, no "needs a new pull request" line; then `EQUAL` with the suggestion on `pr2` |
| `merged one listed after main edits its file` | Independent `pr1:main` (eight-line `a.txt`) and `pr2:main`; `pr1` squash-merged; the phase merges `origin/main` and a round of `pr2`; another pull request on `main` edits `a.txt` line 8, the phase merges `origin/main` again, and a round, each proved with `pr1:main pr2:main` | both rounds exit `0` with `EQUAL` and no `neither the phase's` or head `FAIL`, `pr2` has `main`'s line 8 and diff `b.txt` |
| `merged one with a developer commit, local branch stale` | Independent `pr1:main` and `pr2:main`; a suggestion on `origin/pr1` that the local `pr1` lacks; `pr1` squash-merged. A round of `pr2`, then the same proof with the local `pr1` moved to `origin/pr1`; then the phase merges `origin/main` and a round | the round and the second proof print the same lines: the two-remedy `FAIL`, no `DEVELOPER-COMMITS`, `NOT EQUAL`, `pr2` unchanged. After the merge: exit `0`, `EQUAL`. |
| `taken developer commit, child rebased` | Stack `parent:main`, `child:parent`. The developer commits a suggestion to `c.txt` on `origin/child`; the phase takes it with `git cherry-pick -x` and a round of both carries it, pushing nothing because `child` already holds it, and proves `EQUAL`, so `PUSHED` records `child` at the developer's commit. `parent` is squash-merged, and the forge rebases `child` onto `main` with the same tree; a round of `child:main::parent`, then another | the carry round pushes nothing and records `child=<developer's commit>`. Then: exit `0`, no `DEVELOPER-COMMITS`, guarantees kept over the rewritten head, `c.txt` is the suggestion, diff `c.txt`, `EQUAL`; the second round leaves `origin/child` unchanged and proves `EQUAL` |
| `twin developer commit` | `pr1` carries phase commits `a`, `a2` (`a.txt` from `a` to `a2`) and a revert to `a`. The developer commits `a.txt` from `a` to `a2` on `origin/pr1`, with the same patch-id as the phase's `a2`; a round | exit `1`, `DEVELOPER-COMMITS pr1 <sha>`, `NOT EQUAL`, `pr1` and `origin/pr1` still at the developer's commit, `a.txt` is `a2` |
| `rebased child, main moved` | Stack `parent:main`, `child:parent`, pushed. `parent` is squash-merged, `main` changes `README`, and the forge rebases `child` onto that `main`, so the tree changes; a round of `child:main::parent` | exit `0`, no `DEVELOPER-COMMITS`, guarantees kept over the rewritten head, `README` is `main`'s, diff `c.txt`, `EQUAL` |
| `rebased child with a developer edit` | The same, but the developer commits a suggestion to `c.txt` on `origin/child` before the rebase; a round; then the phase commits the head's `c.txt` and a round carries that commit | first: exit `1`, `DEVELOPER-COMMITS child <rewritten head>`, `NOT EQUAL`, `child` and `origin/child` unchanged, the suggestion kept. Then: exit `0`, no `DEVELOPER-COMMITS`, guarantees kept, the suggestion kept, `EQUAL`. |
| `taken before the round, child rebased` | Stack `parent:main`, `child:parent`, pushed. The developer commits a suggestion to `c.txt` on `origin/child` and the phase takes it with `git cherry-pick -x`; before any round, `parent` is squash-merged and the forge rebases `child` onto `main` with the same tree; a round of `child:main::parent` carrying the taken commit | exit `0`, no `DEVELOPER-COMMITS`, guarantees kept over the rewritten head, `c.txt` is the suggestion, diff `c.txt`, `EQUAL` |
| `never pushed, no entry` | A first build of `pr1:main` with `PUSHED` naming only `xpr1` | exit `0`, no `STOP`, diff `a.txt`, `EQUAL` |
| `pushed, no entry` | `pr1` is pushed. A proof with an empty `PUSHED`; then the developer commits a suggestion to `a.txt` and a proof with the recorded entry; then a round and a proof with an empty `PUSHED`, and again with `PUSHED` naming only `xpr1` | each proof without the entry prints `STOP pr1 is on origin but has no PUSHED entry, so its developer commits cannot be told apart` and `NOT EQUAL`, and never `EQUAL`. The proof with the entry prints `DEVELOPER-COMMITS pr1 <sha>`. Each round exits `1` and prints exactly that `STOP`, and `pr1` and `origin/pr1` stay at the developer's commit with the suggestion. |
| `pushed head missing` | `pr1` is pushed, then `PUSHED` names a head that the repository lacks; a round, then a proof | the refresh exits `1` and prints exactly `STOP pr1 was last pushed at <sha>, which is not here, so its developer commits cannot be told apart`, `pr1` and `origin/pr1` unchanged; the proof prints the same line and `NOT EQUAL` |

```bash
/bin/bash <<'CHECK'
set -u
root=$(git rev-parse --show-toplevel)
md="$root/packages/s-stack/.apm/skills/sam-mode/references/pr-commands.md"
S=$(mktemp -d "${TMPDIR:-/tmp}/pr-handbook-check.XXXXXX")
trap 'cd /; rm -rf "$S"' EXIT
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
export GIT_AUTHOR_NAME=check GIT_AUTHOR_EMAIL=check@example.com GIT_COMMITTER_NAME=check GIT_COMMITTER_EMAIL=check@example.com
REGEN_SUBJECT='chore(s-stack): regenerate generated files' REGEN_RE='^chore(s-stack): regenerate generated files$'
awk '/^```bash$/ { b = 1; n++; next } /^```$/ { b = 0; next } b { print > (dir "/block" n ".sh") }' dir="$S" "$md"
script=$(grep -l -E '^ *refresh \| prove\)' "$S"/block*.sh | head -1)
[ -n "$script" ] && cp "$script" "$S/pr.sh" || { echo "FAIL no script block in $md"; exit 1; }
: > "$S/failed"
pass() { echo "PASS $1"; }
fail() { echo "FAIL $1"; echo x >> "$S/failed"; }
export OWN= MERGED= PUSHED=
own_add() { [[ ",$OWN," == *",$1,"* ]] || OWN=${OWN:+$OWN,}$1; }
pushed_set() { local e r=; for e in ${PUSHED//,/ }; do [ "${e%%=*}" = "$1" ] || r=${r:+$r,}$e; done; PUSHED=${r:+$r,}$1=$2; }
merged_add() { [[ ",$OWN," != *",$1,"* || ",$MERGED," == *",$1,"* ]] || MERGED=${MERGED:+$MERGED,}$1; }

commit() { git add -A && git commit -q -m "$1"; }
line() { sed "$1s/.*/$2/" "$3" > "$S/l" && cat "$S/l" > "$3"; }
set_version() { sed "s/^version: .*/version: \"$1\"/" "$2" > "$S/y" && cat "$S/y" > "$2"; }
relock() { local p; for p in $(git ls-files -c -o --exclude-standard -- '*apm.yml'); do git ls-files -s -- "$(dirname "$p")" ':(exclude)*apm.lock.yaml' > "$(dirname "$p")/apm.lock.yaml"; git add -- "$(dirname "$p")/apm.lock.yaml"; done; }
regen() {
  local v; v=$(git show origin/main:pkg/apm.yml | sed -n 's/^version: "\(.*\)"$/\1/p')
  set_version "${v%.*}.$(( ${v##*.} + 1 ))" pkg/apm.yml && git add pkg/apm.yml && relock
  git diff --cached --quiet || git commit -q -m "$REGEN_SUBJECT"
}
init() {
  O="$S/$1.git" R="$S/$1" PUSHED=
  git init -q --bare -b main "$O" && git -C "$O" config receive.denyNonFastForwards true && git -C "$O" config receive.denyDeletes true
  git init -q -b main "$R" && cd "$R" && git remote add origin "$O" || exit 1
  mkdir pkg; printf 'name: pkg\nversion: "0.1.0"\ndescription: "A package."\nlicense: MIT\ndeps: []\n' > pkg/apm.yml
  for i in 1 2 3 4 5 6 7 8 9 10 11 12; do echo "line $i"; done > shared.txt
  echo readme > README; git add -A; relock; commit initial; git push -q -u origin main
}
in_wt() { local at=$1 wt="$S/wt.tmp" c; shift; git worktree add -q --detach "$wt" "$at" && (cd "$wt" && "$@"); c=$?; git worktree remove --force "$wt"; git fetch -q origin; return $c; }
main_commit() { local m=$1; shift; "$@" && relock && commit "$m" && git push -q origin HEAD:main; }
on_main() { git fetch -q origin; in_wt origin/main main_commit "$@"; }
other_commit() { local b=$1 m=$2; shift 2; "$@" && relock && commit "$m" && regen && git push -q origin "HEAD:refs/heads/$b"; }
other() { git fetch -q origin; in_wt origin/main other_commit "$@"; }
squash_in() { git merge -q --squash "origin/$1" >/dev/null 2>&1; relock; commit "feat: $1 (#1)" && git push -q origin HEAD:main; }
squash() { git fetch -q origin; in_wt origin/main squash_in "$1"; local c=$?; merged_add "$1"; return $c; }
true_merge_in() { git merge -q --no-ff --no-edit "origin/$1" >/dev/null 2>&1 || { git checkout -q origin/main -- pkg; relock; git commit -q --no-edit; }; git push -q origin HEAD:main; }
true_merge() { git fetch -q origin; in_wt origin/main true_merge_in "$1"; local c=$?; merged_add "$1"; return $c; }
forge_in() { git rebase -q --onto origin/main "$1" >/dev/null 2>&1 && git rev-parse HEAD > "$S/forged"; }
forge_moved() {
  local old=$(git rev-parse "origin/$1") new
  in_wt "origin/$1" forge_in "$2" || return 1; new=$(cat "$S/forged")
  git push -q origin "$new:refs/forge/tmp" && git -C "$O" update-ref "refs/heads/$1" "$new" && git -C "$O" update-ref -d refs/forge/tmp && git fetch -q origin
  ! git merge-base --is-ancestor "$old" "$new" && git merge-base --is-ancestor origin/main "$new"
}
forge() { local old=$(git rev-parse "origin/$1"); forge_moved "$@" && [ "$(git rev-parse "$old^{tree}")" = "$(git rev-parse "origin/$1^{tree}")" ]; }
orch() { git checkout -q -b orch origin/main && mkdir -p .foundry && echo plan > .foundry/plan.md && commit 'chore: plan'; }
take() { git merge -q --no-ff --no-edit "$1" >/dev/null 2>&1 || { relock; git commit -q --no-edit; }; }
phase() { git checkout -q -b phase orch; }
sha() { git rev-parse HEAD; }
snap() { git -C "$O" for-each-ref --format='%(objectname) %(refname)' refs/heads; }
has_local() { git rev-parse -q --verify "refs/heads/$1" >/dev/null; }
IN_ROUND= RB=() R_OUT= SNAP=
start_of() {
  local p r; p=$(echo "$1" | cut -d: -f2); p=${p#origin/}
  [ "$p" = main ] && { echo origin/main; return; }
  [[ ",$OWN," == *",$p,"* ]] && has_local "$p" && { echo "$p"; return; }
  echo "origin/$p"
}
step() {
  local b=$1 spec=$2 wt="$S/wt.$1"; shift 2
  [ "$IN_ROUND" = x ] && return 1
  [ -n "$IN_ROUND" ] || { IN_ROUND=1 RB=() R_OUT=; git fetch -q origin; SNAP=$(snap); }
  RB+=("$b"); own_add "$b"; [ ! -d "$wt" ] || git worktree remove --force "$wt"
  if git rev-parse -q --verify "refs/remotes/origin/$b" >/dev/null; then git worktree add -q --no-track -B "$b" "$wt" "origin/$b"
  else git worktree add -q --no-track -B "$b" "$wt" "${START_AT:-$(start_of "$spec")}"; fi || { out="worktree add failed"; code=1; abort; return 1; }
  out=$(cd "$wt" && "$BASH" "$S/pr.sh" refresh phase origin/main "$spec" "$@" 2>&1 && regen 2>&1); code=$?
  git worktree remove --force "$wt"; R_OUT="$R_OUT${R_OUT:+$'\n'}$out"
  [ $code = 0 ] || { abort; return 1; }
}
abort() {
  local b; for b in "${RB[@]}"; do
    if git rev-parse -q --verify "refs/remotes/origin/$b" >/dev/null; then git branch -q -f "$b" "origin/$b"; elif has_local "$b"; then git branch -q -D "$b"; fi
  done
  IN_ROUND=x; [ "$(snap)" = "$SNAP" ] || fail "a round that did not prove EQUAL pushed: $(git -C "$O" for-each-ref --format='%(refname:short)' refs/heads | tr '\n' ' ')"
  git fetch -q origin
}
finish() {
  local b; [ "$IN_ROUND" = 1 ] || { IN_ROUND=; code=1; return 1; }
  prove "$@"; R_OUT="$R_OUT${R_OUT:+$'\n'}$out"
  if [ $code = 0 ] && [ "$(echo "$out" | tail -1)" = EQUAL ]; then
    for b in "${RB[@]}"; do [ "$(git rev-parse -q --verify "refs/remotes/origin/$b")" = "$(git rev-parse "$b")" ] && continue
      git push -q -u origin "$b" 2>&1 || { out="$R_OUT"$'\n'"push of $b refused"; code=1; IN_ROUND=; return 1; }; done
    IN_ROUND=; git fetch -q origin; for b in "${RB[@]}"; do pushed_set "$b" "$(git rev-parse "origin/$b")"; done; out=$R_OUT; code=0; return 0
  fi
  abort; IN_ROUND=; out=$R_OUT; code=1; return 1
}
round() { step "$@" && finish ${PROOF:-$2}; local c=$?; IN_ROUND=; return $c; }
crashed_round() { step "$@"; local c=$?; IN_ROUND=; return $c; }
variant() { local b=$1 from=$2 wt="$S/wt.v" c; shift 2; git worktree add -q -b "$b" "$wt" "$from" && (cd "$wt" && "$@"); c=$?; git worktree remove --force "$wt"; return $c; }
prove() { out=$("$BASH" "$S/pr.sh" prove orch phase origin/main "$@" 2>&1); code=$?; }
equal() { prove "$@"; [ $code = 0 ] && [ "$(echo "$out" | tail -1)" = EQUAL ]; }
not_equal() { prove "$@"; [ $code = 1 ] && [ "$(echo "$out" | tail -1)" = 'NOT EQUAL' ]; }
has() { echo "$out" | grep -q -x -E -- "$1"; }
added() { echo "$(git rev-list --first-parent --merges --count "$1..$2") $(git rev-list --first-parent --count --grep="$REGEN_RE" "$1..$2") $(git rev-list --first-parent --count "$1..$2")"; }
hand() { git diff --name-only "$1...$2" -- . ':(exclude)*apm.lock.yaml' ':(exclude)*apm.yml' | tr '\n' ' '; }
at() { git show "$1:$2" | sed -n "$3p"; }
anc() { git merge-base --is-ancestor "$1" "$2"; }
guarded() {
  local old=$1 new=$2 a; a=$(added "$old" "$new")
  anc "$old" "$new" && anc origin/main "$new" && [ "${a%% *}" -le 1 ] && a=${a#* } && [ "${a%% *}" -le 1 ]
}
readme() { echo "readme $1" > README; }
put_line() { line "$1" "$2" "$3"; }
desc() { line 3 "description: \"$1\"" pkg/apm.yml; }
write() { printf '%s\n' "$2" > "$1"; }

c_split() {
  init split
  other other-pr 'feat: other phase' sh -c 'sed "2s/.*/line 2 parent/" shared.txt > t && mv t shared.txt && echo o > o.txt'
  orch; take origin/other-pr; phase
  echo a > a.txt; echo 'keywords: [a]' >> pkg/apm.yml; echo stale >> pkg/apm.lock.yaml; commit 'feat: a'; c1=$(sha)
  echo s1 > .foundry/status.md; commit 'chore: status'
  line 2 'line 2 child' shared.txt; echo b > b.txt; commit 'feat: b'; c2=$(sha)
  printf 'bin\000\001\377' > img.bin; commit 'feat: binary'; c3=$(sha)
  echo stale2 >> pkg/apm.lock.yaml; echo s2 > .foundry/status.md; commit 'chore: lockfile and status only'; c4=$(sha)
  step pr1 pr1:main "$c1"; o1="$code $out"; step pr2 pr2:other-pr "$c2" "$c3" "$c4"; o2="$code $out"; finish pr1:main pr2:other-pr; o3="$code $out"
  [ "${o1%% *} ${o2%% *} ${o3%% *}" = '0 0 0' ] && [ "$(hand origin/main origin/pr1)" = 'a.txt ' ] && [ "$(hand origin/other-pr origin/pr2)" = 'b.txt img.bin shared.txt ' ] \
    && git diff --quiet phase origin/pr2 -- img.bin && anc origin/main origin/pr1 && anc origin/other-pr origin/pr2 \
    && [ "$(git log --format=%B origin/main..origin/pr1 | grep -c -x -F "(cherry picked from commit $c1)")" = 1 ] \
    && git show origin/pr1:pkg/apm.yml | grep -q -x 'keywords: \[a\]' \
    && pass "done-when build: pr1 on main and pr2 stacked on another phase's pull request, own paths only, trailer, binary intact" || fail "done-when build: pr1 $o1; pr2 $o2"
  equal pr1:main pr2:other-pr && pass "done-when correct split with regenerate commits: EQUAL" || fail "done-when correct split: $out"
  not_equal pr1:main && has 'FAIL b.txt has not landed and is in no open pull request, so it needs a new pull request' && pass "done-when split that drops a change: NOT EQUAL" || fail "done-when dropped change: $out"
  variant pr1x origin/pr1 sh -c 'echo extra > extra.txt && git add -A && git commit -q -m extra'
  not_equal pr1x:main pr2:other-pr && has 'FAIL pr1x: it changes extra.txt, which the phase does not' && pass "done-when split that adds a change: NOT EQUAL" || fail "done-when added change: $out"
  variant pr1f origin/pr1 sh -c 'mkdir -p .foundry && echo leak > .foundry/leak.md && git add -A && git commit -q -m leak'
  not_equal pr1f:main pr2:other-pr && has 'FAIL pr1f: contains .foundry/leak.md' && pass "done-when branch with a file under .foundry: NOT EQUAL" || fail "done-when .foundry: $out"
  variant pr1r origin/pr1 sh -c "echo more >> a.txt && git commit -q -am '$REGEN_SUBJECT'"
  not_equal pr1r:main pr2:other-pr && has 'FAIL pr1r: regenerate commit [0-9a-f]+ changes a.txt' && pass "done-when regenerate commit that changes a hand-written file: NOT EQUAL" || fail "done-when regenerate a.txt: $out"
  variant pr1y origin/pr1 sh -c "sed 's/^deps: .*/deps: [x]/' pkg/apm.yml > t && mv t pkg/apm.yml && git commit -q -am '$REGEN_SUBJECT'"
  not_equal pr1y:main pr2:other-pr && has 'FAIL pr1y: regenerate commit [0-9a-f]+ changes -deps: \[\]' && has '\+deps: \[x\]' && pass "done-when regenerate commit that changes an apm.yml line other than version: NOT EQUAL" || fail "done-when regenerate deps: $out"
  squash other-pr; h=$(git rev-parse origin/pr2)
  PROOF="pr1:main pr2:main::other-pr" round pr2 pr2:main::other-pr; o="$code $out"
  [ "${o%% *}" = 0 ] && guarded "$h" origin/pr2 && [ "$(added "$h" origin/pr2)" = '1 1 2' ] && [ "$(hand origin/main origin/pr2)" = 'b.txt img.bin shared.txt ' ] \
    && [ "$(at origin/pr2 shared.txt 2)" = 'line 2 child' ] && equal pr1:main pr2:main::other-pr \
    && pass "done-when squash-merged parent: the child's round and regenerate commit, parent excluded through its kept ref, EQUAL" || fail "done-when squash-merged parent: $o; adds $(added "$h" origin/pr2); diff $(hand origin/main origin/pr2); proof $out"
}

c_rounds() {
  init rounds; orch; phase
  echo a > a.txt; commit 'feat: a'; c1=$(sha)
  round pr1 pr1:main "$c1" || fail "rounds build: $out"
  h=$(git rev-parse origin/pr1); round pr1 pr1:main; o="$code $out"
  [ "${o%% *}" = 0 ] && echo "$out" | grep -q '^up to date with' && [ "$(git rev-parse origin/pr1)" = "$h" ] && pass "guarantee: a round on an up-to-date branch changes nothing" || fail "up-to-date round: $o"
  on_main 'docs: main moves' readme 2; h=$(git rev-parse origin/pr1); round pr1 pr1:main; o="$code $out"
  [ "${o%% *}" = 0 ] && guarded "$h" origin/pr1 && [ "$(added "$h" origin/pr1)" = '1 1 2' ] && equal pr1:main \
    && pass "guarantee: main moves, one merge and one regenerate commit, a fast-forward push, main an ancestor, EQUAL" || fail "round after a move: $o; adds $(added "$h" origin/pr1); proof $out"
  on_main 'feat: another pull request raises the version' sh -c 'echo "readme 3" > README && sed "s/^version: .*/version: \"0.1.1\"/" pkg/apm.yml > t && mv t pkg/apm.yml'
  h=$(git rev-parse origin/pr1); round pr1 pr1:main; o="$code $out"
  [ "${o%% *}" = 0 ] && guarded "$h" origin/pr1 && [ "$(at origin/pr1 pkg/apm.yml 2)" = 'version: "0.1.2"' ] && equal pr1:main \
    && pass "guarantee: main takes the branch's own version, the round raises it again" || fail "version taken: $o; proof $out"
  on_main 'docs: main moves again' readme 4; h=$(git rev-parse origin/pr1)
  crashed_round pr1 pr1:main; o="$code $out"
  [ "${o%% *}" = 0 ] && [ "$(git rev-parse origin/pr1)" = "$h" ] && [ "$(git rev-parse pr1)" != "$h" ] || fail "interrupted round did not leave an unpushed head: $o"
  round pr1 pr1:main; o="$code $out"
  [ "${o%% *}" = 0 ] && guarded "$h" origin/pr1 && [ "$(added "$h" origin/pr1)" = '1 1 2' ] && equal pr1:main \
    && pass "guarantee: an interrupted round finishes on the next one, from origin/pr1" || fail "after an interrupted round: $o; adds $(added "$h" origin/pr1); proof $out"
  h=$(git rev-parse origin/pr1); round pr1 pr1:main; round pr1 pr1:main; o="$code $out"
  [ "${o%% *}" = 0 ] && [ "$(git rev-parse origin/pr1)" = "$h" ] && pass "guarantee: repeated rounds after that change nothing" || fail "repeated rounds: $o"
  echo 'a fixed' > a.txt; commit 'fix: a'; f1=$(sha); round pr1 pr1:main "$f1" || fail "fix round: $out"
  h=$(git rev-parse origin/pr1); round pr1 pr1:main "$f1"; o="$code $out"
  [ "${o%% *}" = 0 ] && [ "$(git rev-parse origin/pr1)" = "$h" ] && [ "$(git show origin/pr1:a.txt)" = 'a fixed' ] && pass "guarantee: a fix round rerun after its push, with the same commit, changes nothing" || fail "rerun fix round: $o; adds $(added "$h" origin/pr1)"
  on_main 'docs: main moves for a hand edit' readme 5
  variant pr1h origin/pr1 sh -c 'git merge -q --no-ff --no-commit origin/main >/dev/null 2>&1; git checkout -q origin/main -- pkg; echo "by hand" >> a.txt; git add -A; git commit -q --no-edit'
  not_equal pr1h:main && has 'FAIL pr1h: its head differs from its target tree' && echo "$out" | grep -q 'a.txt' && pass "a hand edit inside a merge commit: NOT EQUAL" || fail "hand edit in a merge: $out"
}

c_rewrite() {
  init rewrite; orch; phase
  echo p > p.txt; commit 'feat: parent'; c1=$(sha)
  echo c > c.txt; commit 'feat: child'; c2=$(sha)
  step parent parent:main "$c1"; step child child:parent "$c2"; finish parent:main child:parent || fail "rewrite build: $out"
  squash parent
  if forge child origin/parent; then
    rw=$(git rev-parse origin/child); on_main 'docs: main moves' readme 2
    PROOF="parent:main child:main::parent" round child child:main::parent; o="$code $out"
    [ "${o%% *}" = 0 ] && guarded "$rw" origin/child && [ "$(hand origin/main origin/child)" = 'c.txt ' ] && equal child:main::parent \
      && pass "forge rewrite: the rewritten head is the start, commits only on top, EQUAL" || fail "forge rewrite: $o; adds $(added "$rw" origin/child); proof $out"
  else fail "forge rewrite: the simulated rebase changed the tree"; fi
}

c_r1_squash_fix() {
  init r1-squash-fix
  other parent 'feat: parent' put_line 2 'line 2 parent' shared.txt
  orch; take origin/parent; phase
  echo c > c.txt; commit 'feat: child'; c1=$(sha)
  round child child:parent "$c1" || fail "r1-squash-fix build: $out"
  squash parent; on_main 'fix: another pull request fixes line 2' put_line 2 'line 2 fixed' shared.txt
  round child child:main::parent; o="$code $out"
  [ "${o%% *}" = 0 ] && [ "$(at origin/child shared.txt 2)" = 'line 2 fixed' ] && [ "$(hand origin/main origin/child)" = 'c.txt ' ] && equal child:main::parent \
    && pass "round 1, squash step: a later fix on main to a squash-merged parent's line stays, EQUAL" || fail "r1-squash-fix: $o; line 2 '$(at origin/child shared.txt 2)'; diff $(hand origin/main origin/child); proof $out"
}

c_r1_version_fix() {
  init r1-version-fix; orch; phase
  echo a > a.txt; commit 'feat: a'; c1=$(sha)
  round pr1 pr1:main "$c1" || fail "r1-version-fix build: $out"
  desc 'Better.'; commit 'fix: describe'; f1=$(sha)
  round pr1 pr1:main "$f1"; o="$code $out"
  [ "${o%% *}" = 0 ] && [ "$(at origin/pr1 pkg/apm.yml 2,3 | tr '\n' '|')" = 'version: "0.1.1"|description: "Better."|' ] && equal pr1:main \
    && pass "round 1, version context: a fix next to a version: line the regenerate commit changed is carried" || fail "r1-version-fix: $o; proof $out"
}

c_r1_version_build() {
  init r1-version-build
  other other-pr 'feat: other phase' sh -c 'echo o > o.txt'
  orch; take origin/other-pr; phase
  echo a > a.txt; desc 'Better.'; commit 'feat: a'; c1=$(sha)
  round pr1 pr1:main "$c1"; o="$code $out"
  [ "${o%% *}" = 0 ] && [ "$(at origin/pr1 pkg/apm.yml 3)" = 'description: "Better."' ] && [ "$(hand origin/main origin/pr1)" = 'a.txt ' ] && equal pr1:main \
    && pass "round 1, version context: a first build next to another phase's version: raise" || fail "r1-version-build: $o; proof $out"
}

c_r1_orch_merged() {
  init r1-orch-merged; orch; phase
  line 3 'line 3 phase' shared.txt; echo a > a.txt; commit 'feat: a'; c1=$(sha)
  round pr1 pr1:main "$c1" || fail "r1-orch-merged build: $out"
  git checkout -q -b other-phase orch; line 5 'line 5 other phase' shared.txt; commit 'feat: other phase'
  git checkout -q orch; take other-phase; git checkout -q phase; take orch
  echo b > b.txt; commit 'feat: b'; c2=$(sha)
  round pr1 pr1:main "$c2"; o="$code $out"
  [ "${o%% *}" = 0 ] && [ "$(at origin/pr1 shared.txt 3,5 | tr '\n' '|')" = 'line 3 phase|line 4|line 5|' ] && [ "$(hand origin/main origin/pr1)" = 'a.txt b.txt shared.txt ' ] && equal pr1:main \
    && pass "round 1, newer orchestrator branch: the fix round leaves the other phase's line out, EQUAL" || fail "r1-orch-merged: $o; lines $(at origin/pr1 shared.txt 3,5 | tr '\n' '|'); proof $out"
}

c_r1_two_squashed() {
  init r1-two-squashed
  on_main 'feat: base files' sh -c 'echo "a 1" > a.txt && echo "b 1" > b.txt'
  other depA 'feat: depA' write a.txt 'a 1 depA'; other depB 'feat: depB' write b.txt 'b 1 depB'
  orch; take origin/depA; take origin/depB; phase
  echo 'a 1 depA child' > a.txt; echo 'b 1 depB child' > b.txt; commit 'feat: child'; c1=$(sha)
  round pr3 pr3:main:depA,depB "$c1" || fail "r1-two-squashed build: $out"
  squash depA; squash depB; h=$(git rev-parse origin/pr3)
  round pr3 pr3:main::depA,depB; o="$code $out"
  [ "${o%% *}" = 0 ] && guarded "$h" origin/pr3 && [ "$(git show origin/pr3:a.txt) $(git show origin/pr3:b.txt)" = 'a 1 depA child b 1 depB child' ] && [ "$(hand origin/main origin/pr3)" = 'a.txt b.txt ' ] && equal pr3:main::depA,depB \
    && pass "round 1, two squash-merged dependencies in one round: EQUAL" || fail "r1-two-squashed: $o; proof $out"
}

c_r1_stack_moves() {
  init r1-stack-moves; orch; phase
  echo p > p.txt; commit 'feat: parent'; c1=$(sha)
  echo c > c.txt; commit 'feat: child'; c2=$(sha)
  step parent parent:main "$c1"; step child child:parent "$c2"; finish parent:main child:parent || fail "r1-stack-moves build: $out"
  on_main 'feat: an unrelated pull request' sh -c 'echo m > m.txt'
  hp=$(git rev-parse origin/parent) hc=$(git rev-parse origin/child)
  step parent parent:main; o1="$code $out"; step child child:parent; o2="$code $out"; finish parent:main child:parent; o3="$code $out"
  [ "${o1%% *} ${o2%% *} ${o3%% *}" = '0 0 0' ] && guarded "$hp" origin/parent && guarded "$hc" origin/child && [ "$(hand origin/parent origin/child)" = 'c.txt ' ] \
    && [ "$(git merge-base --all origin/parent origin/child | wc -l | tr -d ' ')" = 1 ] && anc origin/parent origin/child && equal parent:main child:parent \
    && pass "round 1, a stack after main moves: the child takes its parent, its diff is its own change" || fail "r1-stack-moves: parent $o1; child $o2; diff $(hand origin/parent origin/child); proof $out"
}

c_r1_spaces() {
  init r1-spaces
  on_main 'feat: spaced paths' sh -c 'mkdir -p "docs dir" "my pkg" && for i in 1 2 3 4 5 6; do echo "line $i"; done > "docs dir/read me.md" && printf "name: my\nversion: \"0.1.0\"\ndescription: \"Mine.\"\n" > "my pkg/apm.yml"'
  other parent 'feat: parent' put_line 2 'line 2 parent' 'docs dir/read me.md'
  orch; take origin/parent; phase
  line 2 'line 2 child' 'docs dir/read me.md'; line 3 'description: "Spaced."' 'my pkg/apm.yml'; commit 'feat: child'; c1=$(sha)
  round child child:parent "$c1" || fail "r1-spaces build: $out"
  squash parent; on_main 'feat: raise my pkg' set_version 0.2.0 'my pkg/apm.yml'
  round child child:main::parent; o="$code $out"
  [ "${o%% *}" = 0 ] && [ "$(at origin/child 'docs dir/read me.md' 2)" = 'line 2 child' ] && [ "$(at origin/child 'my pkg/apm.yml' 2,3 | tr '\n' '|')" = 'version: "0.2.0"|description: "Spaced."|' ] && equal child:main::parent \
    && pass "round 1, paths with spaces" || fail "r1-spaces: $o; proof $out"
}

conflict_setup() {
  init "$1"; orch; phase
  line 5 'line 5 phase' shared.txt; echo a > a.txt; commit 'feat: a'; c1=$(sha)
  round pr1 pr1:main "$c1" || fail "$1 build: $out"
  on_main 'feat: another pull request edits line 5' sh -c 'sed "5s/.*/line 5 main/" shared.txt > t && mv t shared.txt && echo m > m.txt'
  h=$(git rev-parse origin/pr1); round pr1 pr1:main; o="$code $out"
  [ "${o%% *}" = 1 ] && has 'STOP shared.txt changed on origin/main after the phase last took it, so the phase must merge it first' && [ "$(git rev-parse origin/pr1)" = "$h" ] \
    && pass "$1: a stale owned path stops the round and leaves the branch" || fail "$1 stale stop: $o"
  git checkout -q phase; git merge -q --no-ff --no-commit origin/main >/dev/null 2>&1
}
c_r2_conflict_commit() {
  conflict_setup r2-conflict-commit
  git checkout -q origin/main -- shared.txt pkg; relock; git commit -q --no-edit
  line 5 'line 5 phase and main' shared.txt; commit 'fix: resolve line 5'; f1=$(sha)
  round pr1 pr1:main "$f1"; o="$code $out"
  [ "${o%% *}" = 0 ] && guarded "$h" origin/pr1 && [ "$(at origin/pr1 shared.txt 5)" = 'line 5 phase and main' ] && equal pr1:main \
    && pass "round 2, old conflicting commit: an ordinary resolution commit on the phase carries, EQUAL" || fail "r2-conflict-commit: $o; line 5 '$(at origin/pr1 shared.txt 5)'; proof $out"
}
c_r2_conflict_merge() {
  conflict_setup r2-conflict-merge
  line 5 'line 5 phase and main' shared.txt; git checkout -q origin/main -- pkg; relock; git add -A; git commit -q --no-edit
  round pr1 pr1:main; o="$code $out"
  [ "${o%% *}" = 0 ] && guarded "$h" origin/pr1 && [ "$(at origin/pr1 shared.txt 5)" = 'line 5 phase and main' ] && equal pr1:main \
    && pass "round 1 and 2, resolution inside the phase's merge: the next round takes it, EQUAL" || fail "r2-conflict-merge: $o; line 5 '$(at origin/pr1 shared.txt 5)'; proof $out"
}

c_r2_clean_merge() {
  init r2-clean-merge; orch; phase
  echo a > a.txt; commit 'feat: a'; c1=$(sha)
  round pr1 pr1:main "$c1" || fail "r2-clean-merge build: $out"
  on_main 'feat: another pull request lands' write m.txt m
  git checkout -q phase; take origin/main
  round pr1 pr1:main; o="$code $out"
  [ "${o%% *}" = 0 ] && equal pr1:main && pass "round 2, clean merge of main into the phase: EQUAL" || fail "r2-clean-merge: $o; proof $out"
}

c_r2_orch_line() {
  init r2-orch-line; orch; phase
  line 5 'line 5 first' shared.txt; commit 'feat: a'; c1=$(sha)
  round pr1 pr1:main "$c1" || fail "r2-orch-line build: $out"
  git checkout -q orch; take phase; git checkout -q phase
  line 5 'line 5 fixed' shared.txt; commit 'fix: line 5'; f1=$(sha)
  round pr1 pr1:main "$f1" || fail "r2-orch-line fix round: $out"
  git checkout -q orch; take phase; git checkout -q phase
  h=$(git rev-parse origin/pr1); round pr1 pr1:main; o="$code $out"
  [ "${o%% *}" = 0 ] && [ "$(git rev-parse origin/pr1)" = "$h" ] && [ "$(at origin/pr1 shared.txt 5)" = 'line 5 fixed' ] && equal pr1:main \
    && pass "round 2, orchestrator merged the phase and two own commits share a line: EQUAL" || fail "r2-orch-line: $o; proof $out"
}

c_r2_orch_delete() {
  init r2-orch-delete; orch; phase
  git rm -q README; echo a > a.txt; commit 'feat: drop README'; c1=$(sha)
  round pr1 pr1:main "$c1" || fail "r2-orch-delete build: $out"
  git checkout -q orch; take phase; git checkout -q phase
  equal pr1:main && ! git cat-file -e origin/pr1:README 2>/dev/null && pass "round 2, orchestrator merged a phase that deletes a file: EQUAL" || fail "r2-orch-delete: $out"
}

c_r2_merge_commit() {
  init r2-merge-commit; orch; phase
  echo a > a.txt; commit 'feat: a'; c1=$(sha)
  echo b > b.txt; commit 'feat: b'; c2=$(sha)
  step pr1 pr1:main "$c1"; step pr2 pr2:pr1 "$c2"; finish pr1:main pr2:pr1 || fail "r2-merge-commit build: $out"
  true_merge pr1; h=$(git rev-parse origin/pr2)
  round pr2 pr2:main::pr1; o="$code $out"
  [ "${o%% *}" = 0 ] && guarded "$h" origin/pr2 && [ "$(hand origin/main origin/pr2)" = 'b.txt ' ] && equal pr2:main::pr1 \
    && pass "round 2, a parent merged with a merge commit: the child's round and the proof, EQUAL" || fail "r2-merge-commit: $o; proof $out"
}

c_r2_row3_to_row2() {
  init r2-row3-to-row2
  on_main 'feat: base files' sh -c 'echo "a 1" > a.txt && echo "b 1" > b.txt'
  other depA 'feat: depA' write a.txt 'a 1 depA'; other depB 'feat: depB' write b.txt 'b 1 depB'
  orch; take origin/depA; take origin/depB; phase
  echo 'a 1 depA child' > a.txt; echo 'b 1 depB child' > b.txt; commit 'feat: child'; c1=$(sha)
  round pr3 pr3:main:depA,depB "$c1" || fail "r2-row3-to-row2 build: $out"
  squash depA; h=$(git rev-parse origin/pr3)
  round pr3 pr3:depB::depA; o="$code $out"
  [ "${o%% *}" = 1 ] && has 'STOP depB does not hold origin/main, so pr3 must target it with depB merged in' && [ "$(git rev-parse origin/pr3)" = "$h" ] \
    && pass "round 2, row 3 to row 2 under a parent without main: STOP, branch unchanged" || fail "r2-row3-to-row2 stop: $o"
  round pr3 pr3:main:depB:depA; o="$code $out"
  [ "${o%% *}" = 0 ] && guarded "$h" origin/pr3 && [ "$(git show origin/pr3:a.txt) $(git show origin/pr3:b.txt)" = 'a 1 depA child b 1 depB child' ] && equal pr3:main:depB:depA \
    && pass "round 2, staying in row 3 with depB merged in: merged dependency kept, EQUAL" || fail "r2-row3-to-row2 row 3: $o; proof $out"
}

c_r2_grandchild() {
  init r2-grandchild; orch; phase
  line 2 'line 2 X' shared.txt; commit 'feat: one'; c1=$(sha)
  line 2 'line 2 Y' shared.txt; echo two > two.txt; commit 'feat: two'; c2=$(sha)
  echo three > three.txt; commit 'feat: three'; c3=$(sha)
  step pr1 pr1:main "$c1"; step pr2 pr2:pr1 "$c2"; step pr3 pr3:pr2 "$c3"; finish pr1:main pr2:pr1 pr3:pr2 || fail "r2-grandchild build: $out"
  squash pr1; forge pr2 origin/pr1 || fail "r2-grandchild: the simulated rewrite changed the tree"
  step pr2 pr2:main::pr1; o1="$code $out"; step pr3 pr3:pr2; o2="$code $out"; finish pr2:main::pr1 pr3:pr2; o3="$code $out"
  [ "${o1%% *} ${o2%% *} ${o3%% *}" = '0 0 0' ] && anc origin/pr2 origin/pr3 && [ "$(hand origin/pr2 origin/pr3)" = 'three.txt ' ] && [ "$(at origin/pr3 shared.txt 2)" = 'line 2 Y' ] && equal pr2:main::pr1 pr3:pr2 \
    && pass "round 2, a grandchild whose parent the forge rewrote, spec without the merged grandparent" || fail "r2-grandchild: pr2 $o1; pr3 $o2; diff $(hand origin/pr2 origin/pr3); proof $out"
}

c_r2_delete_package() {
  init r2-delete-package
  on_main 'feat: a second package' sh -c 'mkdir old && printf "name: old\nversion: \"0.1.0\"\n" > old/apm.yml && echo skill > old/skill.md'
  orch; phase
  git rm -rq old; commit 'feat: remove the old package'; c1=$(sha)
  round pr1 pr1:main "$c1"; o="$code $out"
  [ "${o%% *}" = 0 ] && git cat-file -e origin/main:old/apm.lock.yaml && [ -z "$(git ls-tree -r --name-only origin/pr1 -- old)" ] && equal pr1:main \
    && pass "round 2, a phase that deletes a package: the lockfile goes too, EQUAL" || fail "r2-delete-package: $o; left $(git ls-tree -r --name-only origin/pr1 -- old | tr '\n' ' '); proof $out"
}

c_r2_undeclared() {
  init r2-undeclared; orch; phase
  echo a > a.txt; commit 'feat: a'; c1=$(sha)
  echo b > b.txt; commit 'feat: b'; c2=$(sha)
  step pr1 pr1:main "$c1"; START_AT=pr1 step pr2 pr2:main "$c2"; finish pr1:main pr2:main; o="$code $out"
  [ "${o%% *}" = 1 ] && [ "$(echo "$out" | tail -1)" = 'NOT EQUAL' ] && echo "$out" | grep -q '^FAIL.*a\.txt' && unpushed pr1 && unpushed pr2 && ! has_local pr2 \
    && pass "round 2, a same-phase branch with an undeclared dependency: NOT EQUAL, nothing pushed" || fail "r2-undeclared: $o"
}

c_r2_adjacent() {
  init r2-adjacent; orch; phase
  line 5 'line 5 pr1' shared.txt; commit 'feat: pr1'; c1=$(sha)
  line 6 'line 6 pr2' shared.txt; commit 'feat: pr2'; c2=$(sha)
  step pr1 pr1:main "$c1"; step pr2 pr2:pr1 "$c2"; finish pr1:main pr2:pr1 || fail "r2-adjacent build: $out"
  equal pr1:main pr2:pr1 || fail "r2-adjacent proof before the fix: $out"
  line 5 'line 5 pr1 fixed' shared.txt; commit 'fix: pr1'; f1=$(sha)
  h=$(git rev-parse origin/pr1); PROOF="pr1:main pr2:pr1" round pr1 pr1:main "$f1"; o="$code $out"
  [ "${o%% *}" = 1 ] && has 'STOP shared.txt conflicts outside generated content' && has 'STOP [0-9a-f]+ fix: pr1 does not apply' && has "STOP the branch is back at $h" && [ "$(git rev-parse origin/pr1)" = "$h" ] \
    && pass "adjacent-line edits split across a stack: STOP, branch unchanged" || fail "r2-adjacent: $o"
}

c_uncarried() {
  init uncarried; orch; phase
  echo a > a.txt; commit 'feat: a'; c1=$(sha)
  echo b > b.txt; commit 'feat: b'; c2=$(sha)
  step pr1 pr1:main "$c1"; step pr2 pr2:main "$c2"; finish pr1:main pr2:main || fail "uncarried build: $out"
  echo 'b fixed' > b.txt; commit 'fix: b'; f1=$(sha)
  not_equal pr1:main pr2:main && has "FAIL b.txt: pr2 lacks phase commits $(git rev-parse --short "$f1") fix: b;, so they need a pull request" \
    && pass "a phase commit an open pull request does not carry: NOT EQUAL, named" || fail "uncarried open: $out"
  PROOF="pr1:main pr2:main" round pr2 pr2:main "$f1" || fail "uncarried fix round: $out"
  squash pr1; echo 'a fixed' > a.txt; commit 'fix: a after its pull request merged'; f2=$(sha)
  not_equal pr2:main && has 'FAIL a.txt has not landed and is in no open pull request, so it needs a new pull request' \
    && pass "a fix after its pull request merged: NOT EQUAL, needs a new pull request" || fail "uncarried merged: $out"
  h=$(git rev-parse origin/pr2); PROOF="pr1:main pr2:main" round pr2 pr2:main; o="$code $out"
  [ "${o%% *}" = 1 ] && has 'FAIL a\.txt.*' && [ "$(echo "$out" | tail -1)" = 'NOT EQUAL' ] && unchanged pr2 "$h" \
    && pass "a round whose proof fails: NOT EQUAL, nothing pushed, the branch back at its remote head" || fail "uncarried, failed round: $o"
  PROOF="pr1:main pr2:main pr1b:main::pr1" round pr1b pr1b:main::pr1 "$f2"; o="$code $out"
  [ "${o%% *}" = 0 ] && [ "$(hand origin/main origin/pr1b)" = 'a.txt ' ] && [ "$(git show origin/pr1b:a.txt)" = 'a fixed' ] && equal pr2:main pr1b:main::pr1 && pass "the new pull request for it: EQUAL" || fail "uncarried new pull request: $o; proof $out"
}

c_leak() {
  init leak; orch; phase
  line 3 'line 3 phase' shared.txt; echo a > a.txt; commit 'feat: a'; c1=$(sha)
  round pr1 pr1:main "$c1" || fail "leak build: $out"
  git checkout -q -b other-phase orch; line 9 'line 9 other phase' shared.txt; echo o > o.txt; commit 'feat: other phase'
  git checkout -q orch; take other-phase; git checkout -q phase; take orch
  line 4 'line 4 phase' shared.txt; commit 'fix: line 4'; f1=$(sha)
  round pr1 pr1:main "$f1"; o="$code $out"
  [ "${o%% *}" = 0 ] && [ "$(at origin/pr1 shared.txt 9)" = 'line 9' ] && [ "$(at origin/pr1 shared.txt 3,4 | tr '\n' '|')" = 'line 3 phase|line 4 phase|' ] && [ "$(hand origin/main origin/pr1)" = 'a.txt shared.txt ' ] && equal pr1:main \
    && pass "leak: another phase's line in a shared file stays out of the pull request" || fail "leak: $o; line 9 '$(at origin/pr1 shared.txt 9)'; diff $(hand origin/main origin/pr1); proof $out"
}

c_identity() {
  init identity; orch; phase
  export GIT_AUTHOR_DATE='1795000000 +0000'
  line 3 'line 3 first' shared.txt; commit 'fix: review'; c1=$(sha)
  line 9 'line 9 second' shared.txt; commit 'fix: review'; c2=$(sha)
  unset GIT_AUTHOR_DATE
  round pr1 pr1:main "$c1"; o="$code $out"
  [ "${o%% *}" = 1 ] && has "FAIL shared.txt: pr1 lacks phase commits $(git rev-parse --short "$c2") fix: review;, so they need a pull request" && unpushed pr1 && ! has_local pr1 \
    && pass "identity: twin commits with one author, date and subject stay distinct, and the round pushes nothing" || fail "identity: $o"
  step pr1 pr1:main "$c1"; step pr2 pr2:pr1 "$c2"; finish pr1:main pr2:pr1; o="$code $out"
  [ "${o%% *}" = 0 ] && [ "$(at origin/pr1 shared.txt 3) $(at origin/pr1 shared.txt 9)" = 'line 3 first line 9' ] && [ "$(at origin/pr2 shared.txt 9)" = 'line 9 second' ] && equal pr1:main pr2:pr1 \
    && pass "identity: the twin carried by its own pull request: EQUAL" || fail "identity second: $o; proof $out"
}

c_assumptions() {
  init ff; orch; phase
  echo a > a.txt; commit 'feat: a'; c1=$(sha)
  round pr1 pr1:main "$c1" || fail "ff build: $out"
  git checkout -q orch; take phase; git checkout -q phase; git merge -q --ff-only orch
  not_equal pr1:main && has 'FAIL pr1: it changes a.txt, which the phase does not' && pass "assumption: a fast-forward of the orchestrator branch is reported" || fail "ff: $out"
  cd "$S"; init orch-commit; orch; echo fix > orch-fix.txt; commit 'chore: orchestrator edits a file'; phase
  echo a > a.txt; commit 'feat: a'; c1=$(sha)
  round pr1 pr1:main "$c1"; o="$code $out"
  [ "${o%% *}" = 1 ] && has 'FAIL orch-fix.txt has not landed and is in no open pull request, so it needs a new pull request' && [ "$(echo "$out" | tail -1)" = 'NOT EQUAL' ] && unpushed pr1 \
    && pass "assumption: an orchestrator commit outside .foundry is reported, and nothing is pushed" || fail "orch-commit: $o"
}

c_missing() {
  init missing; orch; phase
  echo a > a.txt; commit 'feat: a'; c1=$(sha)
  round pr1 pr1:main "$c1" || fail "missing build: $out"
  h=$(git rev-parse origin/pr1); round pr1 pr1:main::gone; o1="$code $out"; round pr1 pr1:main:gone2; o2="$code $out"
  [ "${o1%% *} ${o2%% *}" = '1 1' ] && echo "$o1" | grep -q -x -F '1 STOP gone is not a branch here' && echo "$o2" | grep -q -x -F '1 STOP gone2 is not a branch here' && [ "$(git rev-parse origin/pr1)" = "$h" ] \
    && pass "a spec naming a missing branch: STOP, branch unchanged" || fail "missing branch: $o1; $o2"
}

unchanged() { [ "$(git rev-parse "origin/$1")" = "$2" ] && [ "$(git rev-parse "$1")" = "$2" ]; }
unpushed() { ! git rev-parse -q --verify "refs/remotes/origin/$1" >/dev/null; }
SHARED_STOP='STOP shared.txt is a shared path, so the stop is permanent: no merge or commit on the phase clears it, and it needs a decision'
other_on() { local at=$1; shift; git fetch -q origin; in_wt "$at" other_commit "$@"; }

c_revert() {
  init revert; orch; phase
  echo a > a.txt; echo debug > debug.txt; readme phase; commit 'feat: a'; c1=$(sha)
  round pr1 pr1:main "$c1" || fail "revert build: $out"
  rm debug.txt; echo readme > README; commit 'fix: revert debug'; f1=$(sha)
  f=$(git rev-parse --short "$f1")
  not_equal pr1:main && has "FAIL debug.txt: pr1 lacks phase commits $f fix: revert debug;, so they need a pull request" && has "FAIL README: pr1 lacks phase commits $f fix: revert debug;, so they need a pull request" \
    && pass "wrong result, revert: a pull request that still holds a change the phase reverted is NOT EQUAL" || fail "wrong result, revert: $out"
  h=$(git rev-parse origin/pr1); round pr1 pr1:main; o="$code $out"
  [ "${o%% *}" = 1 ] && has "FAIL debug.txt: pr1 lacks phase commits $f fix: revert debug;, so they need a pull request" && unchanged pr1 "$h" \
    && pass "wrong result, revert: a round without the revert pushes nothing" || fail "wrong result, revert, round without it: $o"
  round pr1 pr1:main "$f1"; o="$code $out"
  [ "${o%% *}" = 0 ] && ! git cat-file -e origin/pr1:debug.txt 2>/dev/null && [ "$(git show origin/pr1:README)" = readme ] && equal pr1:main \
    && pass "wrong result, revert: carrying the revert gives EQUAL" || fail "wrong result, revert carried: $o; proof $out"
}

c_origin_names() {
  init origin-names; orch; phase
  line 2 'line 2 pr1' shared.txt; commit 'feat: pr1'; c1=$(sha)
  line 11 'line 11 pr2' shared.txt; commit 'feat: pr2'; c2=$(sha)
  step pr1 pr1:main "$c1"; step pr2 pr2:pr1 "$c2"; finish pr1:main pr2:pr1 || fail "origin-names build: $out"
  equal pr1:main pr2:pr1 && equal origin/pr1:main origin/pr2:pr1 && equal origin/pr1:origin/main origin/pr2:origin/pr1 \
    && pass "wrong result, origin/ names: origin/<pr> proves the same as <pr>" || fail "wrong result, origin/ names: $out"
}

c_stop_shared() {
  init stop-shared; orch; phase
  line 5 'line 5 pr1' shared.txt; commit 'feat: pr1'; c1=$(sha)
  line 9 'line 9 pr2' shared.txt; commit 'feat: pr2'; c2=$(sha)
  step pr1 pr1:main "$c1"; step pr2 pr2:pr1 "$c2"; finish pr1:main pr2:pr1 || fail "stop-shared build: $out"; PROOF="pr1:main pr2:pr1"
  on_main 'feat: another pull request edits line 5' put_line 5 'line 5 main' shared.txt
  h=$(git rev-parse origin/pr1) want=$(printf '%s\n' 'STOP shared.txt conflicts outside generated content' "STOP $(git rev-parse --short "$c1") feat: pr1 does not apply" "$SHARED_STOP")
  round pr1 pr1:main; o1="$code $out"
  [ "$o1" = "1 $want" ] && unchanged pr1 "$h" || { fail "stop, shared path, after main moved: $o1"; return; }
  git checkout -q phase; git merge -q --no-ff --no-commit origin/main >/dev/null 2>&1
  { for i in 1 2 3 4; do echo "line $i"; done; echo 'line 5 pr1 and main'; for i in 6 7 8; do echo "line $i"; done; echo 'line 9 pr2'; for i in 10 11 12; do echo "line $i"; done; } > shared.txt
  git checkout -q origin/main -- pkg; relock; git add -A; git commit -q --no-edit
  round pr1 pr1:main; o2="$code $out"
  [ "$o2" = "1 $want" ] && unchanged pr1 "$h" || { fail "stop, shared path, after the phase merged main: $o2"; return; }
  line 5 'line 5 resolved' shared.txt; commit 'fix: resolve line 5'; f1=$(sha)
  round pr1 pr1:main "$f1"; o3="$code $out"
  [ "$o3" = "1 $(printf '%s\n' 'STOP shared.txt conflicts outside generated content' "STOP $(git rev-parse --short "$f1") fix: resolve line 5 does not apply" "$SHARED_STOP" "STOP the branch is back at $h")" ] && unchanged pr1 "$h" \
    && pass "stop, shared path: permanent through a phase merge and a resolution commit, branch unchanged" || fail "stop, shared path, resolution commit: $o3"
}

c_stop_owned() {
  init stop-owned; orch; phase
  line 3 'line 3 phase' shared.txt; echo a > a.txt; commit 'feat: a'; c1=$(sha)
  round pr1 pr1:main "$c1" || fail "stop-owned build: $out"
  other other-pr 'feat: other phase edits line 10' put_line 10 'line 10 other' shared.txt
  squash other-pr; h=$(git rev-parse origin/pr1)
  round pr1 pr1:main; o="$code $out"
  [ "$o" = '1 STOP shared.txt changed on origin/main after the phase last took it, so the phase must merge it first' ] && unchanged pr1 "$h" \
    && pass "stop, owned path changed cleanly: STOP, branch unchanged" || fail "stop, owned path changed cleanly: $o"
  git checkout -q phase; take origin/main
  round pr1 pr1:main; o="$code $out"
  [ "${o%% *}" = 0 ] && guarded "$h" origin/pr1 && [ "$(at origin/pr1 shared.txt 3) $(at origin/pr1 shared.txt 10)" = 'line 3 phase line 10 other' ] && equal pr1:main \
    && pass "stop, owned path changed cleanly: cleared once the phase merges main, EQUAL" || fail "stop, owned path cleared: $o; proof $out"
}

xphase_in() { echo x1 > x1.txt && commit 'feat: x1' && echo x2 > x2.txt && commit 'feat: x2' && echo x3 > x3.txt && commit 'feat: x3' && git push -q origin HEAD:refs/heads/xphase; }
c_stop_forge() {
  init stop-forge
  other x1 'feat: x1' write x1.txt x1
  other_on origin/x1 x2 'feat: x2' write x2.txt x2
  other_on origin/x2 x3 'feat: x3' write x3.txt x3
  git fetch -q origin; in_wt origin/main xphase_in
  orch; take origin/xphase; phase
  echo a > a.txt; commit 'feat: a, needs x2'; c1=$(sha)
  round ours ours:main:x2 "$c1" && equal ours:main:x2 || fail "stop-forge build: $out"
  squash x1; forge x2 origin/x1 || { fail "stop-forge: the simulated rewrite changed the tree"; return; }
  h=$(git rev-parse origin/ours) st='1 STOP ours would carry x2.txt, which the phase does not change' fl='FAIL ours: it changes x2.txt, which the phase does not'
  round ours ours:main:x2:x1; o1="$code $out"; unchanged ours "$h"; u1=$?; not_equal ours:main:x2:x1; p1=$out
  round ours ours:main:x2:x1; o2="$code $out"; unchanged ours "$h"; u2=$?; not_equal ours:main:x2:x1; p2=$out
  squash x2; round ours ours:main::x2,x1; o3="$code $out"; unchanged ours "$h"; u3=$?; not_equal ours:main::x2,x1; p3=$out
  [ "$o1|$o2|$o3" = "$st|$st|$st" ] && [ "$u1$u2$u3" = 000 ] \
    && pass "stop, forge-rewritten row 3: the documented STOP in every round, also after the dependency merged, branch unchanged, nothing pushed" \
    || fail "stop, forge-rewritten row 3: rounds '$o1' '$o2' '$o3', unchanged $u1$u2$u3 (0 is unchanged)"
  for p in "$p1" "$p2" "$p3"; do out=$p; has "$fl" && [ "$(echo "$p" | tail -1)" = 'NOT EQUAL' ] || { fail "stop, forge-rewritten row 3, proof: $p"; return; }; done
  pass "stop, forge-rewritten row 3: the proof stays NOT EQUAL in every round"
}

c_stop_delegate() {
  init stop-delegate; orch; phase
  git checkout -q -b delegate; echo d > d.txt; commit 'feat: delegate work'; cd_=$(sha)
  git checkout -q phase; echo z > z.txt; commit 'feat: session work'; c0=$(sha)
  git merge -q --no-ff --no-edit delegate
  round pr1 pr1:main "$c0" "$cd_"; o="$code $out"
  [ "$o" = '1 STOP pr1 would carry d.txt, which the phase does not change' ] && pass "stop, delegate merge: the documented STOP" || fail "stop, delegate merge, documented output: $o"
  unpushed pr1 && pass "stop, delegate merge: nothing is pushed" || fail "stop, delegate merge: the round pushed origin/pr1 with $(hand origin/main origin/pr1)and without d.txt: $o"
}

c_stop_dir() {
  init "stop-$1"
  if [ "$1" = dir ]; then on_main 'docs: notes' write notes 'some notes'; else on_main 'docs: notes' sh -c 'mkdir notes && echo one > notes/one.md'; fi
  orch; phase
  if [ "$1" = dir ]; then git rm -q notes; mkdir notes; echo one > notes/one.md; else git rm -rq notes; echo 'a file' > notes; fi
  commit "docs: notes becomes a $1"; c1=$(sha)
  h=$(git rev-parse origin/main); round pr1 pr1:main "$c1"; o="$code $(echo "$out" | grep -v -E '^hint:|^warning: index entry')"
  stops=$(echo "$out" | grep '^STOP') first=$(echo "$out" | grep -v -E '^hint:' | head -1)
  [ "$code" = 1 ] && [ "$stops" = "$(printf '%s\n' 'STOP notes cannot be written into the tree, as when a file and a directory share its name' "STOP the branch is back at $h")" ] \
    && echo "$first" | grep -q -E '^(error|fatal|warning|git [a-z-]+):' \
    && pass "stop, $2: git's own error, then the documented STOP" || fail "stop, $2, documented output: $o"
  unpushed pr1 && pass "stop, $2: nothing is pushed" || fail "stop, $2: the round pushed origin/pr1"
}
c_stop_file_to_dir() { c_stop_dir dir "file to directory"; }
c_stop_dir_to_file() { c_stop_dir file "directory to file"; }

c_chain() {
  init chain; orch; phase
  line 2 'line 2 pr1' shared.txt; echo a > a.txt; commit 'feat: pr1'; k1=$(sha)
  line 11 'line 11 pr2' shared.txt; echo b > b.txt; commit 'feat: pr2'; k2=$(sha)
  step pr1 pr1:main "$k1"; step pr2 pr2:main "$k2"; finish pr1:main pr2:main; o="$code $out"
  [ "${o%% *}" = 1 ] && has 'FAIL shared.txt is in (pr1 and pr2|pr2 and pr1), which are not in one stack' && unpushed pr1 && unpushed pr2 && ! has_local pr1 && ! has_local pr2 \
    && pass "chained rule: two unchained pull requests on one hand-written path are NOT EQUAL, and nothing is pushed" || fail "chained rule, unchained: $o"
  step pr1 pr1:main "$k1"; step pr2 pr2:pr1 "$k2"; finish pr1:main pr2:pr1; o="$code $out"
  [ "${o%% *}" = 0 ] && anc origin/pr1 origin/pr2 && [ "$(hand origin/pr1 origin/pr2)" = 'b.txt shared.txt ' ] && equal pr1:main pr2:pr1 \
    && pass "chained rule: the later one restacked on the earlier one, EQUAL" || fail "chained rule, chained: $o; diff $(hand origin/pr1 origin/pr2); proof $out"
}

c_merged_listed() {
  init merged-parent; orch; phase
  line 2 'line 2 parent' shared.txt; commit 'feat: parent'; c1=$(sha)
  echo c > c.txt; commit 'feat: child'; c2=$(sha)
  step parent parent:main "$c1"; step child child:parent "$c2"; finish parent:main child:parent || fail "merged-parent build: $out"
  squash parent; on_main 'fix: another pull request fixes line 2' put_line 2 'line 2 fixed' shared.txt
  PROOF="parent:main child:main::parent" round child child:main::parent || fail "merged-parent child round: $out"
  not_equal child:main::parent && has 'FAIL shared.txt has not landed and is in no open pull request, so it needs a new pull request' && equal parent:main child:main::parent \
    && pass "merged listed: a merged parent listed as the handbook says gives EQUAL" || fail "merged listed, parent: $out"
  cd "$S"; init merged-new; orch; phase
  echo a > a.txt; commit 'feat: a'; c1=$(sha)
  round pr1 pr1:main "$c1" || fail "merged-new build: $out"
  squash pr1; echo 'a fixed' > a.txt; commit 'fix: a'; f2=$(sha)
  PROOF="pr1:main pr1b:main::pr1" round pr1b pr1b:main::pr1 "$f2"; o="$code $out"
  [ "${o%% *}" = 0 ] && [ "$(git show origin/pr1b:a.txt)" = 'a fixed' ] && equal pr1:main pr1b:main::pr1 \
    && pass "merged listed: a new pull request for a fix after its merge, with the merged one listed, EQUAL" || fail "merged listed, new pull request: $o; proof $out"
}

DELEGATE_FAIL_RE="FAIL [0-9a-f]+ .* merges [0-9a-f]+, whose commits are not phase commits: a delegate's branch merged into the phase"
delegate_fail() { echo "FAIL $(git log -1 --format='%h %s' "$1") merges $(git rev-parse --short "$2"), whose commits are not phase commits: a delegate's branch merged into the phase"; }

c_delegate_first_parent() {
  init delegate-first-parent; orch; phase
  git checkout -q -b delegate; echo d > d.txt; commit 'feat: delegate work'; cd_=$(sha)
  git checkout -q phase; echo z > z.txt; commit 'feat: session work'; c0=$(sha)
  git merge -q --no-ff --no-edit delegate; mg=$(sha)
  round pr1 pr1:main "$c0"; o="$code $out"
  [ "${o%% *}" = 1 ] && has "$(delegate_fail "$mg" "$cd_")" && [ "$(echo "$out" | tail -1)" = 'NOT EQUAL' ] && unpushed pr1 && ! has_local pr1 \
    && pass "delegate merge, first-parent commits only: the proof prints the delegate FAIL and nothing is pushed" || fail "delegate merge, first-parent commits only: $o"
  git reset -q --hard "$mg^1"; git cherry-pick -x "$cd_" >/dev/null; cp=$(sha)
  round pr1 pr1:main "$c0" "$cp"; o="$code $out"
  [ "${o%% *}" = 0 ] && [ "$(hand origin/main origin/pr1)" = 'd.txt z.txt ' ] && equal pr1:main \
    && pass "delegate merge, rebuilt with cherry-pick -x: EQUAL, the delegate's file carried" || fail "delegate rebuild: $o; diff $(hand origin/main origin/pr1); proof $out"
}

c_delegate_after_push() {
  init delegate-after-push; orch; phase
  echo z > z.txt; commit 'feat: session work'; c0=$(sha)
  round pr1 pr1:main "$c0" || fail "delegate-after-push build: $out"
  h=$(git rev-parse origin/pr1)
  git checkout -q -b delegate; echo d > d.txt; commit 'feat: delegate work'; cd_=$(sha)
  git checkout -q phase; git merge -q --no-ff --no-edit delegate; mg=$(sha)
  echo y > y.txt; commit 'feat: later session work'; c3=$(sha)
  round pr1 pr1:main "$c3"; o="$code $out"
  [ "${o%% *}" = 1 ] && has "$(delegate_fail "$mg" "$cd_")" && unchanged pr1 "$h" \
    && pass "delegate merge after a pushed round: the delegate FAIL, origin/pr1 and pr1 unchanged" || fail "delegate merge after a pushed round: $o"
  git reset -q --hard "$mg^1"; git cherry-pick -x "$cd_" >/dev/null; cp=$(sha); git cherry-pick "$c3" >/dev/null; c3b=$(sha)
  round pr1 pr1:main "$cp" "$c3b"; o="$code $out"
  [ "${o%% *}" = 0 ] && guarded "$h" origin/pr1 && [ "$(hand origin/main origin/pr1)" = 'd.txt y.txt z.txt ' ] && equal pr1:main \
    && pass "delegate merge after a pushed round, rebuilt: EQUAL, a fast-forward over the old origin/pr1" || fail "delegate rebuild after a push: $o; diff $(hand origin/main origin/pr1); proof $out"
}

c_stack_local() {
  init stack-local; orch; phase
  line 2 'line 2 parent' shared.txt; echo p > p.txt; commit 'feat: parent'; c1=$(sha)
  echo c > c.txt; commit 'feat: child'; c2=$(sha)
  step parent parent:main "$c1"; o1="$code $out"; step child child:parent "$c2"; o2="$code $out"
  unpushed parent && unpushed child; u=$?
  finish parent:main child:parent; o3="$code $out"
  [ "${o1%% *} ${o2%% *} ${o3%% *} $u" = '0 0 0 0' ] && anc origin/parent origin/child && [ "$(hand origin/parent origin/child)" = 'c.txt ' ] && [ "$(at origin/child shared.txt 2)" = 'line 2 parent' ] \
    && pass "own-phase stack, first build: the child refreshes on the unpushed parent, both proved before either is pushed" || fail "own-phase stack, first build: $o1; $o2; $o3; unpushed before proof $u"
  hp=$(git rev-parse origin/parent) hc=$(git rev-parse origin/child)
  line 2 'line 2 parent fixed' shared.txt; commit 'fix: parent'; f1=$(sha)
  step parent parent:main "$f1"; o1="$code $out"; git fetch -q origin; [ "$(git rev-parse origin/parent)" = "$hp" ]; u=$?
  step child child:parent; o2="$code $out"; finish parent:main child:parent; o3="$code $out"
  [ "${o1%% *} ${o2%% *} ${o3%% *} $u" = '0 0 0 0' ] && guarded "$hp" origin/parent && guarded "$hc" origin/child && anc origin/parent origin/child \
    && [ "$(at origin/child shared.txt 2)" = 'line 2 parent fixed' ] && [ "$(hand origin/parent origin/child)" = 'c.txt ' ] \
    && pass "own-phase stack, fix round: the child takes the parent's unpushed fix, then both push as fast-forwards" || fail "own-phase stack, fix round: $o1; $o2; $o3; parent unpushed before proof $u"
}

c_foreign_local() {
  init foreign-local
  other other-pr 'feat: other phase' write o.txt o
  orch; take origin/other-pr; phase
  echo c > c.txt; commit 'feat: child'; c1=$(sha)
  git fetch -q origin; git worktree add -q -b other-pr "$S/wt.o" origin/other-pr
  (cd "$S/wt.o" && echo unproved > o.txt && echo u > u.txt && git add -A && git commit -q -m 'feat: other phase, unproved'); git worktree remove --force "$S/wt.o"
  anc origin/other-pr other-pr && [ "$(git rev-parse other-pr)" != "$(git rev-parse origin/other-pr)" ] || fail "foreign-local: the other phase's local branch is not ahead of origin"
  round child child:other-pr "$c1"; o="$code $out"
  [ "${o%% *}" = 0 ] && anc origin/other-pr origin/child && ! anc other-pr origin/child && [ "$(git show origin/child:o.txt)" = o ] && ! git cat-file -e origin/child:u.txt 2>/dev/null \
    && [ "$(hand origin/other-pr origin/child)" = 'c.txt ' ] && equal child:other-pr \
    && pass "another phase's local parent ahead of origin is ignored: the child is built on origin/other-pr" || fail "foreign-local: $o; diff $(hand origin/other-pr origin/child); proof $out"
}

c_retry() {
  init retry; orch; phase
  echo a > a.txt; commit 'feat: a'; c1=$(sha)
  round pr1 pr1:main::gone "$c1"; o="$code $out"
  [ "$o" = '1 STOP gone is not a branch here' ] && unpushed pr1 && ! has_local pr1 && pass "retry: a stopped first build pushes nothing and leaves no local branch" || fail "retry, stopped build: $o"
  crashed_round pr1 pr1:main "$c1"; git worktree add -q "$S/wt.pr1" pr1
  has_local pr1 && unpushed pr1 || fail "retry: the crashed build did not leave an unpushed local branch"
  round pr1 pr1:main "$c1"; o="$code $out"
  [ "${o%% *}" = 0 ] && [ "$(hand origin/main origin/pr1)" = 'a.txt ' ] && [ "$(git log --format=%B origin/main..origin/pr1 | grep -c -x -F "(cherry picked from commit $c1)")" = 1 ] && equal pr1:main \
    && pass "retry: a build after a crashed one starts again from origin/main, one carried commit, EQUAL" || fail "retry: $o; proof $out"
}

c_stale_other() {
  init "stale-other-$1"
  other other-pr 'feat: other phase' write o.txt o
  orch; take origin/other-pr; phase
  line 3 'line 3 phase' shared.txt; echo c > c.txt; commit 'feat: child'; c1=$(sha)
  round child "$2" "$c1" || fail "stale-other $1 build: $out"
  git fetch -q origin; in_wt origin/other-pr sh -c 'sed "10s/.*/line 10 other/" shared.txt > t && mv t shared.txt && git commit -q -am "fix: other phase edits line 10" && git push -q origin HEAD:refs/heads/other-pr'
  h=$(git rev-parse origin/child); round child "$2"; o="$code $out"
  echo "$o" | grep -q -x -E '1 STOP shared.txt changed on (origin/)?other-pr after the phase last took it, so the phase must merge it first' && unchanged child "$h" \
    && pass "stale owned path from another phase's pull request, $1: STOP, nothing pushed" || fail "stale-other $1 stop: $o"
  git checkout -q phase; take origin/other-pr
  round child "$2"; o="$code $out"
  [ "${o%% *}" = 0 ] && ! echo "$out" | grep -q -E "$DELEGATE_FAIL_RE" && guarded "$h" origin/child && [ "$(at origin/child shared.txt 3) $(at origin/child shared.txt 10)" = 'line 3 phase line 10 other' ] && equal "$2" \
    && pass "stale owned path, $1: cleared once the phase merges the other phase's branch, no delegate FAIL, EQUAL" || fail "stale-other $1 cleared: $o; proof $out"
}
c_stale_other_stacked() { c_stale_other stacked child:other-pr; }

c_extend() {
  init extend; orch; phase
  printf 'one\ntwo\n' > f.txt; commit 'feat: parent adds f'; c1=$(sha)
  printf 'one\ntwo\nthree\nfour\nfive\n' > f.txt; commit 'feat: child extends f'; c2=$(sha)
  step parent parent:main "$c1"; o1="$code $out"; step child child:parent "$c2"; o2="$code $out"; finish parent:main child:parent; o3="$code $out"
  [ "${o1%% *} ${o2%% *} ${o3%% *}" = '0 0 0' ] && [ "$(echo "$o3" | tail -1)" = EQUAL ] && anc origin/parent origin/child && [ "$(hand origin/parent origin/child)" = 'f.txt ' ] \
    && [ "$(git show origin/parent:f.txt | wc -l | tr -d ' ') $(git show origin/child:f.txt | wc -l | tr -d ' ')" = '2 5' ] && equal parent:main child:parent \
    && pass "own-phase child extends its parent's file: built on the parent's unpushed head, EQUAL" || fail "own-phase child extends its parent's file: parent $o1; child $o2; proof $o3"
}

c_foreign_above() {
  init foreign-above; orch; phase
  echo a > a.txt; commit 'feat: a'; c1=$(sha)
  round pr1 pr1:main "$c1" || fail "foreign-above build: $out"
  git checkout -q -b xphase orch; echo x > x.txt; commit 'feat: x phase'; xc=$(sha); echo u > u.txt; commit 'feat: x phase, later'; xu=$(sha)
  git checkout -q orch; git merge -q --no-ff --no-edit "$xc"; git checkout -q phase; take orch
  echo b > b.txt; commit 'feat: b, needs x'; c2=$(sha)
  git fetch -q origin; git worktree add -q -b x "$S/wt.x" origin/pr1
  (cd "$S/wt.x" && git cherry-pick -x "$xc" >/dev/null && git push -q origin x && git cherry-pick -x "$xu" >/dev/null); git worktree remove --force "$S/wt.x"; git fetch -q origin
  anc origin/x x && [ "$(git rev-parse x)" != "$(git rev-parse origin/x)" ] || fail "foreign-above: the other phase's local branch is not ahead of origin"
  PROOF="pr1:main pr2:x" round pr2 pr2:x "$c2"; o="$code $out"
  [ "${o%% *}" = 0 ] && anc origin/x origin/pr2 && ! anc x origin/pr2 && ! git cat-file -e origin/pr2:u.txt 2>/dev/null && [ "$(hand origin/x origin/pr2)" = 'b.txt ' ] && equal pr1:main pr2:x \
    && pass "another phase's branch stacked on ours, local ahead of origin: not read, its file stays out of our pull request" || fail "foreign-above: $o; diff $(hand origin/x origin/pr2); proof $out"
}

c_delegate_after_orch() {
  init delegate-after-orch; orch; phase
  echo z > z.txt; commit 'feat: session work'; c0=$(sha)
  round pr1 pr1:main "$c0" || fail "delegate-after-orch build: $out"
  h=$(git rev-parse origin/pr1)
  git checkout -q -b delegate; echo d > d.txt; commit 'feat: delegate fix'; cd_=$(sha)
  git checkout -q phase; git merge -q --no-ff --no-edit delegate; mg=$(sha)
  echo y > y.txt; commit 'fix: session fix'; c3=$(sha)
  git checkout -q orch; take phase; git checkout -q phase
  round pr1 pr1:main "$c3"; o="$code $out"
  [ "${o%% *}" = 1 ] && has "$(delegate_fail "$mg" "$cd_")" && [ "$(echo "$out" | tail -1)" = 'NOT EQUAL' ] && unchanged pr1 "$h" && ! git cat-file -e origin/pr1:d.txt 2>/dev/null \
    && pass "delegate merge after the orchestrator merged the phase: the delegate FAIL, nothing pushed" || fail "delegate after the orchestrator merged: $o"
}
c_stale_other_row3() { c_stale_other row3 child:main:other-pr; }

c_mixed_below() {
  init mixed-below
  other x 'feat: x' write x.txt x
  orch; take origin/x; phase
  echo a > a.txt; commit 'feat: a, needs x'; c1=$(sha)
  echo c > c.txt; commit 'feat: child'; c2=$(sha)
  step pr1 pr1:x "$c1"; step pr2 pr2:pr1 "$c2"; finish pr1:x pr2:pr1 || fail "mixed-below build: $out"
  sleep 1; git fetch -q origin; in_wt origin/x sh -c 'echo x2 > x.txt && git commit -q -am "fix: x" && git push -q origin HEAD:refs/heads/x'
  on_main 'docs: main moves' readme 2; in_wt origin/x sh -c 'git merge -q --no-edit origin/main && git push -q origin HEAD:refs/heads/x'
  git checkout -q orch; take origin/x; git checkout -q phase; take orch
  hp=$(git rev-parse origin/pr1) hc=$(git rev-parse origin/pr2)
  step pr1 pr1:x; o1="$code $out"; step pr2 pr2:pr1; o2="$code $out"; finish pr1:x pr2:pr1; o3="$code $out"
  [ "${o1%% *} ${o2%% *} ${o3%% *}" = '0 0 0' ] && ! echo "$o1$o2$o3" | grep -q STOP && guarded "$hp" origin/pr1 && guarded "$hc" origin/pr2 \
    && anc origin/pr1 origin/pr2 && anc origin/main origin/pr2 && [ "$(git show origin/pr2:x.txt)" = x2 ] && [ "$(hand origin/pr1 origin/pr2)" = 'c.txt ' ] && equal pr1:x pr2:pr1 \
    && pass "mixed stack, own parent that only merges another phase's branch: no false STOP, the child holds the parent" || fail "mixed-below: pr1 $o1; pr2 $o2; proof $o3"
}

c_mixed_above() {
  init mixed-above; orch; phase
  line 2 'line 2 a' shared.txt; echo a > a.txt; commit 'feat: a'; c1=$(sha)
  round pr1 pr1:main "$c1" || fail "mixed-above build: $out"
  git checkout -q -b xphase orch; echo x > x.txt; commit 'feat: x phase'; xc=$(sha)
  git checkout -q orch; git merge -q --no-ff --no-edit "$xc"; git checkout -q phase; take orch
  echo b > b.txt; commit 'feat: b, needs x'; c2=$(sha)
  git fetch -q origin; git worktree add -q -b x "$S/wt.x" origin/pr1
  (cd "$S/wt.x" && git cherry-pick -x "$xc" >/dev/null && git push -q origin x); git worktree remove --force "$S/wt.x"; git fetch -q origin
  PROOF="pr1:main pr2:x" round pr2 pr2:x "$c2" || fail "mixed-above pr2 build: $out"
  sleep 1; line 2 'line 2 a fixed' shared.txt; commit 'fix: a'; f1=$(sha)
  PROOF="pr1:main pr2:x" round pr1 pr1:main "$f1" || fail "mixed-above pr1 fix round: $out"
  git worktree add -q "$S/wt.x" x; (cd "$S/wt.x" && git merge -q --no-ff --no-commit origin/pr1 >/dev/null 2>&1; echo unproved > u.txt; git add -A; git commit -q --no-edit); git worktree remove --force "$S/wt.x"
  anc origin/x x && [ "$(git rev-parse x)" != "$(git rev-parse origin/x)" ] || fail "mixed-above: the other phase's local branch is not ahead of origin"
  PROOF="pr1:main pr2:x" round pr2 pr2:x; o="$code $out"
  [ "${o%% *}" = 0 ] && anc origin/x origin/pr2 && ! anc x origin/pr2 && ! git cat-file -e origin/pr2:u.txt 2>/dev/null && [ "$(hand origin/x origin/pr2)" = 'b.txt ' ] && equal pr1:main pr2:x \
    && pass "mixed stack, another phase's crashed branch between ours: not read, its unproved file stays out of our pull request" || fail "mixed-above: $o; diff $(hand origin/x origin/pr2); proof $out"
}

c_own_missing() {
  init own-missing; orch; phase
  line 2 'line 2 parent' shared.txt; commit 'feat: parent'; c1=$(sha)
  echo c > c.txt; commit 'feat: child'; c2=$(sha)
  step parent parent:main "$c1"; step child child:parent "$c2"; finish parent:main child:parent || fail "own-missing build: $out"
  line 2 'line 2 parent fixed' shared.txt; commit 'fix: parent'; f1=$(sha)
  step parent parent:main "$f1" || fail "own-missing parent fix: $out"
  OWN=; step child child:parent; o="$code $out"
  [ "${o%% *}" = 0 ] && anc origin/parent child && ! anc parent child && [ "$(at child shared.txt 2)" = 'line 2 parent' ] \
    && pass "a branch missing from OWN is read from origin, even when its local copy is ahead" || fail "own-missing: $o; child line 2 '$(at child shared.txt 2)'"
  abort; IN_ROUND=
}

no_stop() { ! echo "$1" | grep -q STOP; }

c_order_stack_fix() {
  init order-stack-fix; orch; phase
  printf 'def parent():\n    pass\n\n\n\n\n\n' > m.py; commit 'feat: parent'; c1=$(sha)
  printf 'def child():\n    parent()\n' >> m.py; commit 'feat: child'; c2=$(sha)
  step pr1 pr1:main "$c1"; step pr2 pr2:pr1 "$c2"; finish pr1:main pr2:pr1 || fail "order-stack-fix build: $out"
  sed -e '2s/.*/    return helper()/' -e '3s/.*/def helper():/' -e '4s/.*/    return 1/' m.py > t && mv t m.py; commit 'fix: parent gets a helper'; f1=$(sha)
  sed '4s/.*/    return 2/' m.py > t && mv t m.py; commit 'fix: child changes the helper'; f2=$(sha)
  hp=$(git rev-parse origin/pr1) hc=$(git rev-parse origin/pr2)
  step pr1 pr1:main "$f1"; o1="$code $out"; step pr2 pr2:pr1 "$f2"; o2="$code $out"; finish pr1:main pr2:pr1; o3="$code $out"
  [ "${o1%% *} ${o2%% *} ${o3%% *}" = '0 0 0' ] && no_stop "$o1$o2" && guarded "$hp" origin/pr1 && guarded "$hc" origin/pr2 \
    && git diff --quiet phase origin/pr2 -- m.py && [ "$(at origin/pr1 m.py 4)" = '    return 1' ] && equal pr1:main pr2:pr1 \
    && pass "refresh order: a child's fix on its parent's fix in one round, no false STOP, EQUAL" || fail "order-stack-fix: pr1 $o1; pr2 $o2; proof $o3"
}

c_order_row3_edit() {
  init order-row3-edit; orch; phase
  echo a > a.txt; commit 'feat: a'; c1=$(sha)
  echo b > b.txt; commit 'feat: b'; c2=$(sha)
  echo a2 >> a.txt; echo c > c.txt; commit 'feat: c, extends a'; c3=$(sha)
  step pr1 pr1:main "$c1"; o1="$code $out"; step pr2 pr2:pr1 "$c2"; o2="$code $out"; step pr3 pr3:main:pr1 "$c3"; o3="$code $out"
  finish pr1:main pr2:pr1 pr3:main:pr1; o4="$code $out"
  [ "${o1%% *} ${o2%% *} ${o3%% *} ${o4%% *}" = '0 0 0 0' ] && no_stop "$o3" && git diff --quiet phase origin/pr3 -- a.txt c.txt \
    && [ "$(hand origin/main origin/pr3)" = 'a.txt c.txt ' ] && equal pr1:main pr2:pr1 pr3:main:pr1 \
    && pass "refresh order: a first build of a third-row pull request that edits its dependency's file, EQUAL" || fail "order-row3-edit: pr3 $o3; proof $o4"
}

c_order_span_chained() {
  init order-span-chained; orch; phase
  echo a > a.txt; commit 'feat: a'; c1=$(sha)
  echo b > b.txt; commit 'feat: b'; c2=$(sha)
  step pr1 pr1:main "$c1"; step pr2 pr2:main "$c2"; finish pr1:main pr2:main || fail "order-span-chained build: $out"
  echo 'a fixed' > a.txt; echo 'b fixed' > b.txt; commit 'fix: a and b'; f=$(sha)
  h=$(git rev-parse origin/pr2)
  step pr1 pr1:main; o1="$code $out"; step pr2 pr2:pr1 "$f"; o2="$code $out"; finish pr1:main pr2:pr1; o3="$code $out"
  [ "${o1%% *} ${o2%% *} ${o3%% *}" = '0 0 0' ] && no_stop "$o2" && guarded "$h" origin/pr2 && anc origin/pr1 origin/pr2 \
    && [ "$(hand origin/pr1 origin/pr2)" = 'a.txt b.txt ' ] && [ "$(git show origin/pr2:a.txt) $(git show origin/pr2:b.txt)" = 'a fixed b fixed' ] && equal pr1:main pr2:pr1 \
    && pass "refresh order: a fix that spans two pull requests goes to the later one once they are chained, EQUAL" || fail "order-span-chained: pr2 $o2; proof $o3"
}

c_span_unchained() {
  init span-unchained; orch; phase
  echo a > a.txt; commit 'feat: a'; c1=$(sha)
  echo b > b.txt; commit 'feat: b'; c2=$(sha)
  step pr1 pr1:main "$c1"; step pr2 pr2:main "$c2"; finish pr1:main pr2:main || fail "span-unchained build: $out"
  echo 'a fixed' > a.txt; echo 'b fixed' > b.txt; commit 'fix: a and b'; f=$(sha)
  h=$(git rev-parse origin/pr1)
  round pr1 pr1:main "$f"; o="$code $out"
  [ "${o%% *}" = 1 ] && has "STOP $(git log -1 --format='%h %s' "$f") also changes b.txt, which pr1 and its base do not hold, so it spans two pull requests and the split must change" \
    && has "STOP the branch is back at $h" && ! has "$SHARED_STOP" && ! has 'STOP b.txt is a shared path.*' && unchanged pr1 "$h" \
    && pass "split fault: a fix that spans two unchained pull requests stops with the split-fault STOP, nothing pushed" || fail "span-unchained: $o"
}

c_outside_own() {
  init outside-own; orch; phase
  echo a > a.txt; commit 'feat: a'; c1=$(sha)
  round pr1 pr1:main "$c1" || fail "outside-own build: $out"
  git checkout -q -b xphase orch; echo x > x.txt; commit 'feat: x phase'; xc=$(sha)
  git checkout -q orch; git merge -q --no-ff --no-edit "$xc"; git checkout -q phase; take orch
  line 3 'line 3 phase' shared.txt; echo b > b.txt; commit 'feat: b, needs x'; c2=$(sha)
  git fetch -q origin; git worktree add -q -b x "$S/wt.x" origin/pr1
  (cd "$S/wt.x" && git cherry-pick -x "$xc" >/dev/null && git push -q origin x); git worktree remove --force "$S/wt.x"; git fetch -q origin
  PROOF="pr1:main pr2:x" round pr2 pr2:x "$c2" || fail "outside-own pr2 build: $out"
  git worktree add -q "$S/wt.x" x && (cd "$S/wt.x" && git reset -q --hard origin/x && sed '10s/.*/line 10 x/' shared.txt > t && mv t shared.txt && git commit -q -am 'fix: x line 10' && git push -q origin x); git worktree remove --force "$S/wt.x"; git fetch -q origin
  h=$(git rev-parse origin/pr2)
  PROOF="pr1:main pr2:x" round pr2 pr2:x; o1="$code $out"; unchanged pr2 "$h"; u=$?
  git checkout -q phase; take origin/x
  PROOF="pr1:main pr2:x" round pr2 pr2:x; o2="$code $out"
  [ "${o1%% *}" = 1 ] && echo "$o1" | grep -q -x -F '1 STOP shared.txt changed on origin/x after the phase last took it, so the phase must merge it first' && [ $u = 0 ] \
    && [ "${o2%% *}" = 0 ] && guarded "$h" origin/pr2 && [ "$(at origin/pr2 shared.txt 3) $(at origin/pr2 shared.txt 10)" = 'line 3 phase line 10 x' ] && equal pr1:main pr2:x \
    && pass "another phase's branch stacked on ours, changed later: the stale STOP, never a silent revert; EQUAL once the phase takes it" || fail "outside-own: first $o1; second $o2; line 10 '$(at origin/pr2 shared.txt 10)'"
}

c_not_own() {
  init not-own
  other x1 'feat: x1' write x1.txt x1
  other_on origin/x1 x2 'feat: x2' write x2.txt x2
  git branch -q --no-track x2 origin/x2
  orch; take origin/x2; phase
  echo a > a.txt; commit 'feat: a, needs x2'; c1=$(sha)
  round ours ours:x2 "$c1" && equal ours:x2 || fail "not-own build: $out"
  squash x1; forge x2 origin/x1 || { fail "not-own: the simulated rewrite changed the tree"; return; }
  h=$(git rev-parse origin/ours)
  round ours ours:x2:x1; o="$code $out"
  [ "${o%% *}" = 1 ] && has 'STOP ours would carry x2.txt, which the phase does not change' && unchanged ours "$h" \
    && pass "a stale local copy of another phase's rewritten parent is ignored: the documented forge STOP, nothing pushed" || fail "not-own: $o"
}

c_glob() {
  init glob
  on_main 'feat: route i' sh -c 'mkdir -p app/i && echo "main i" > app/i/page.tsx'
  orch; phase
  mkdir -p 'app/[id]'; echo 'dynamic route' > 'app/[id]/page.tsx'; commit 'feat: dynamic route'; c1=$(sha)
  round pr1 pr1:main "$c1"; o="$code $out"
  [ "${o%% *}" = 0 ] && [ "$(git show 'origin/pr1:app/[id]/page.tsx' 2>/dev/null)" = 'dynamic route' ] && [ "$(git show origin/pr1:app/i/page.tsx)" = 'main i' ] \
    && [ "$(hand origin/main origin/pr1)" = 'app/[id]/page.tsx ' ] && equal pr1:main \
    && pass "a path with glob characters is carried as written, not expanded" || fail "glob: $o; diff $(hand origin/main origin/pr1)"
}

c_local_only() {
  init local-only; orch; phase
  echo c > c.txt; commit 'feat: child'; c1=$(sha)
  git branch -q --no-track other-pr origin/main
  variant tmp-o other-pr sh -c 'echo unproved > unproved.txt && git add -A && git commit -q -m "feat: unproved, never pushed"'; git branch -q -f other-pr tmp-o
  OWN=child; START_AT=other-pr round child child:other-pr "$c1"; o="$code $out"
  [ "${o%% *}" = 1 ] && has 'STOP other-pr is not a branch here' && unpushed child && ! has_local child \
    && pass "a local branch outside OWN with no origin ref is missing, so the refresh stops and nothing is pushed" || fail "local-only: $o"
}

c_own_refusal() {
  init own-refusal; orch; phase
  echo a > a.txt; commit 'feat: a'; c1=$(sha)
  git worktree add -q --no-track -B pr1 "$S/wt.o" origin/main
  o=$(cd "$S/wt.o" && OWN=other "$BASH" "$S/pr.sh" refresh phase origin/main pr1:main "$c1" 2>&1); c=$?
  git worktree remove --force "$S/wt.o"
  [ $c = 1 ] && [ "$o" = 'STOP pr1 is not in OWN, so it is not one of this phase'"'"'s pull request branches' ] && [ "$(git rev-parse pr1)" = "$(git rev-parse origin/main)" ] \
    && pass "a refresh whose pull request is not in OWN is refused before it records anything" || fail "own-refusal: $c $o"
  git branch -q -D pr1
}

c_merged_skipped() {
  init merged-skipped; orch; phase
  echo a > a.txt; commit 'feat: a'; c1=$(sha)
  echo b > b.txt; commit 'feat: b'; c2=$(sha)
  step pr1 pr1:main "$c1"; step pr2 pr2:main "$c2"; finish pr1:main pr2:main || fail "merged-skipped build: $out"
  squash pr1; on_main 'docs: main moves' readme 2
  h1=$(git rev-parse origin/pr1) h2=$(git rev-parse origin/pr2)
  PROOF="pr1:main pr2:main" round pr2 pr2:main; o="$code $out"
  [ "${o%% *}" = 0 ] && unchanged pr1 "$h1" && guarded "$h2" origin/pr2 && [ "$(hand origin/main origin/pr2)" = 'b.txt ' ] && equal pr1:main pr2:main \
    && pass "a merged pull request takes no round and appears only in the proof: EQUAL, its branch untouched" || fail "merged-skipped: $o"
}

c_merge_edit_shared() {
  init merge-edit-shared; orch; phase
  line 2 'line 2 phase calls foo' shared.txt; echo a > a.txt; commit 'feat: a'; c1=$(sha)
  round pr1 pr1:main "$c1" || fail "merge-edit-shared build: $out"
  git checkout -q -b other-phase orch; line 9 'line 9 other renames foo to bar' shared.txt; commit 'feat: other phase'
  git checkout -q orch; take other-phase; git checkout -q phase
  git merge -q --no-ff --no-commit orch >/dev/null 2>&1; line 2 'line 2 phase calls bar' shared.txt; echo 'a calls bar' > a.txt; git add -A; git commit -q --no-edit; mg=$(sha)
  h=$(git rev-parse origin/pr1)
  round pr1 pr1:main; o="$code $out"
  [ "${o%% *}" = 1 ] && has "FAIL $(git log -1 --format='%h %s' "$mg") edits shared.txt inside the merge, so no pull request carries the edit" \
    && ! has 'FAIL .* edits a.txt inside the merge.*' && [ "$(echo "$out" | tail -1)" = 'NOT EQUAL' ] && unchanged pr1 "$h" \
    && pass "an edit inside the phase's merge, on a shared path: FAIL, nothing pushed; an owned path edited there is accepted" || fail "merge-edit-shared: $o"
}

c_merge_edit_other() {
  init merge-edit-other; orch; phase
  echo a > a.txt; commit 'feat: a'; c1=$(sha)
  round pr1 pr1:main "$c1" || fail "merge-edit-other build: $out"
  git checkout -q -b other-phase orch; echo 'other api v2' > o.txt; commit 'feat: other phase'
  git checkout -q orch; take other-phase; git checkout -q phase
  git merge -q --no-ff --no-commit orch >/dev/null 2>&1; echo 'readme adapted' > README; git add -A; git commit -q --no-edit; mg=$(sha)
  h=$(git rev-parse origin/pr1)
  round pr1 pr1:main; o="$code $out"
  [ "${o%% *}" = 1 ] && has "FAIL $(git log -1 --format='%h %s' "$mg") edits README inside the merge, so no pull request carries the edit" \
    && [ "$(echo "$out" | tail -1)" = 'NOT EQUAL' ] && unchanged pr1 "$h" \
    && pass "an edit inside the phase's merge, on a path no phase commit changes: FAIL, nothing pushed" || fail "merge-edit-other: $o"
}

c_developer() {
  init developer; orch; phase
  echo a > a.txt; commit 'feat: a'; c1=$(sha)
  round pr1 pr1:main "$c1" || fail "developer build: $out"
  in_wt origin/pr1 sh -c 'echo "a, as the reviewer suggested" > a.txt && git commit -q -am "Apply suggestions from code review" && git push -q origin HEAD:pr1'
  s=$(git rev-parse origin/pr1)
  round pr1 pr1:main; o="$code $out"
  [ "${o%% *}" = 1 ] && has "DEVELOPER-COMMITS pr1 $(git rev-parse --short "$s") ?" && [ "$(echo "$out" | tail -1)" = 'NOT EQUAL' ] && unchanged pr1 "$s" \
    && [ "$(git show origin/pr1:a.txt)" = 'a, as the reviewer suggested' ] \
    && pass "a developer's commit on a pull request branch: DEVELOPER-COMMITS, NOT EQUAL, nothing pushed or reverted" || fail "developer: $o"
  git checkout -q phase; git cherry-pick -x "$s" >/dev/null; p=$(sha)
  round pr1 pr1:main "$p"; o="$code $out"
  [ "${o%% *}" = 0 ] && ! has 'DEVELOPER-COMMITS.*' && guarded "$s" origin/pr1 && [ "$(git show origin/pr1:a.txt)" = 'a, as the reviewer suggested' ] && equal pr1:main \
    && pass "the developer's commit taken into the phase with cherry-pick -x: the next round proves EQUAL and keeps it" || fail "developer remedy: $o"
}

c_update_branch() {
  init update-branch; orch; phase
  echo a > a.txt; commit 'feat: a'; c1=$(sha)
  round pr1 pr1:main "$c1" || fail "update-branch build: $out"
  on_main 'docs: main moves' sh -c 'echo m > m.txt'
  in_wt origin/pr1 sh -c 'git merge -q --no-ff --no-edit origin/main && git push -q origin HEAD:pr1'
  u=$(git rev-parse origin/pr1)
  round pr1 pr1:main; o="$code $out"
  [ "${o%% *}" = 0 ] && ! has 'DEVELOPER-COMMITS.*' && guarded "$u" origin/pr1 && [ "$(hand origin/main origin/pr1)" = 'a.txt ' ] && equal pr1:main \
    && pass "GitHub's Update branch merge is a base move: not reported, the round starts from it, EQUAL" || fail "update-branch: $o"
}

c_landed() {
  init landed; orch; phase
  echo a > a.txt; commit 'feat: a, built before trailers'; c1=$(sha)
  in_wt origin/main sh -c "git cherry-pick $c1 >/dev/null 2>&1 && git commit -q --amend -m 'feat: a, no trailer' && git push -q origin HEAD:refs/heads/pr1"
  squash pr1; git branch -q --no-track pr1 origin/pr1
  echo 'a fixed' > a.txt; commit 'fix: a'; c2=$(sha)
  OWN=pr1 MERGED=pr1; PROOF="pr1b:main::pr1" round pr1b pr1b:main::pr1 "$c2"; o="$code $out"
  [ "${o%% *}" = 0 ] && [ "$(git show origin/pr1b:a.txt)" = 'a fixed' ] && [ "$(hand origin/main origin/pr1b)" = 'a.txt ' ] \
    && pass "landed content: a pull request merged without trailers, then a fix in a new one, EQUAL" || fail "landed: $o"
  equal pr1:main pr1b:main::pr1 && pass "landed content: the proof also lists the merged pull request, as the handbook says, EQUAL" || fail "landed, merged one listed: $out"
}

c_update_edit() {
  init update-edit; orch; phase
  echo a > a.txt; commit 'feat: a'; c1=$(sha)
  round pr1 pr1:main "$c1" || fail "update-edit build: $out"
  on_main 'docs: main moves' sh -c 'echo m > m.txt'
  in_wt origin/pr1 sh -c 'git merge -q --no-ff --no-commit origin/main >/dev/null 2>&1; echo "a, edited in the merge" > a.txt && git add -A && git commit -q --no-edit && git push -q origin HEAD:pr1'
  u=$(git rev-parse origin/pr1)
  round pr1 pr1:main; o="$code $out"
  [ "${o%% *}" = 1 ] && has "DEVELOPER-COMMITS pr1 $(git rev-parse --short "$u") ?" && [ "$(echo "$out" | tail -1)" = 'NOT EQUAL' ] && unchanged pr1 "$u" && [ "$(git show origin/pr1:a.txt)" = 'a, edited in the merge' ] \
    && pass "a developer's merge of main that also edits a file: DEVELOPER-COMMITS names the merge, NOT EQUAL, nothing pushed or reverted" || fail "update-edit: $o; a.txt on origin/pr1 '$(git show origin/pr1:a.txt)'"
  git checkout -q phase; git show "$u:a.txt" > a.txt; commit 'fix: a, as edited in review'; p=$(sha)
  round pr1 pr1:main "$p"; o="$code $out"
  [ "${o%% *}" = 0 ] && ! has 'DEVELOPER-COMMITS.*' && guarded "$u" origin/pr1 && [ "$(git show origin/pr1:a.txt)" = 'a, edited in the merge' ] \
    && [ "$(git log --format=%B "$u..origin/pr1" | grep -c -x -F "(cherry picked from commit $p)")" = 1 ] && equal pr1:main \
    && pass "the merge's edit taken into the phase as an ordinary commit: the round carries it, keeps the edit, EQUAL" || fail "update-edit remedy: $o"
}

c_developer_file() {
  init developer-file; orch; phase
  echo a > a.txt; commit 'feat: a'; c1=$(sha)
  round pr1 pr1:main "$c1" || fail "developer-file build: $out"
  in_wt origin/pr1 sh -c 'echo test > a_test.txt && git add -A && git commit -q -m "Add a test, from review" && git push -q origin HEAD:pr1'
  s=$(git rev-parse origin/pr1)
  round pr1 pr1:main; o="$code $out"
  [ "${o%% *}" = 1 ] && [ "$out" = "DEVELOPER-COMMITS pr1 $(git rev-parse --short "$s") " ] && unchanged pr1 "$s" && [ "$(git show origin/pr1:a_test.txt)" = test ] \
    && pass "a developer's commit adding a file: the refresh prints DEVELOPER-COMMITS, not the delegate STOP, nothing pushed or reverted" || fail "developer-file: $o"
  git checkout -q phase; git cherry-pick -x "$s" >/dev/null; p=$(sha)
  round pr1 pr1:main "$p"; o="$code $out"
  [ "${o%% *}" = 0 ] && ! has 'DEVELOPER-COMMITS.*' && guarded "$s" origin/pr1 && [ "$(git show origin/pr1:a_test.txt)" = test ] && [ "$(hand origin/main origin/pr1)" = 'a.txt a_test.txt ' ] && equal pr1:main \
    && pass "the developer's new file taken with cherry-pick -x: the next round keeps it, EQUAL" || fail "developer-file remedy: $o"
}

c_update_child() {
  init update-child; orch; phase
  line 2 'line 2 parent' shared.txt; commit 'feat: parent'; c1=$(sha)
  echo c > c.txt; commit 'feat: child'; c2=$(sha)
  step parent parent:main "$c1"; step child child:parent "$c2"; finish parent:main child:parent || fail "update-child build: $out"
  line 2 'line 2 parent, fixed' shared.txt; commit 'fix: parent'; c3=$(sha)
  PROOF="parent:main child:parent" round parent parent:main "$c3" || fail "update-child parent fix: $out"
  in_wt origin/child sh -c 'git merge -q --no-ff --no-edit origin/parent && git push -q origin HEAD:child'
  u=$(git rev-parse origin/child)
  step parent parent:main; o1="$code $out"; step child child:parent; o2="$code $out"; finish parent:main child:parent; o="$code $out"
  [ "${o1%% *} ${o2%% *} ${o%% *}" = '0 0 0' ] && ! has 'DEVELOPER-COMMITS.*' && anc "$u" origin/child && anc origin/parent origin/child \
    && [ "$(at origin/child shared.txt 2)" = 'line 2 parent, fixed' ] && [ "$(hand origin/parent origin/child)" = 'c.txt ' ] \
    && pass "GitHub's Update branch on a stacked child, merging its parent: not reported, EQUAL" || fail "update-child: $o1 / $o2 / $o"
}

SUGGESTED='a, as the reviewer suggested'
suggest() { in_wt "origin/$1" sh -c "echo '$3' > $2 && git commit -q -am 'Apply suggestions from code review' && git push -q origin HEAD:$1"; }
take_main() { git checkout -q phase; git merge -q --no-ff --no-edit origin/main >/dev/null 2>&1 || { git checkout -q origin/main -- pkg "$@"; relock; git commit -q --no-edit; }; }
two_remedy() { echo "FAIL $1 differs between the phase and origin/main and no open pull request holds it: if the phase changed it, open a pull request for its commits; if origin/main changed it, for example a developer commit on a merged pull request, merge origin/main into the phase"; }

c_dev_merged() {
  init "dev-merged-$1"; orch; phase
  echo a > a.txt; commit 'feat: a'; c1=$(sha)
  echo b > b.txt; commit 'feat: b'; c2=$(sha)
  step pr1 pr1:main "$c1"; step pr2 "$2" "$c2"; finish pr1:main "$2" || fail "dev-merged-$1 build: $out"
  suggest pr1 a.txt "$SUGGESTED"
  "$1" pr1; h=$(git rev-parse origin/pr2)
  PROOF="pr1:main $3" round pr2 "$3"; o="$code $out"
  [ "${o%% *}" = 1 ] && has "$(two_remedy a.txt)" && ! has 'FAIL .*needs a new pull request' && ! has 'DEVELOPER-COMMITS.*' && [ "$(echo "$out" | tail -1)" = 'NOT EQUAL' ] && unchanged pr2 "$h" \
    && pass "developer commit, then merged by $1: the two-remedy FAIL, nothing pushed" || fail "dev-merged-$1, before the phase takes main: $o"
  take_main a.txt
  PROOF="pr1:main $3" round pr2 "$3"; o="$code $out"
  [ "${o%% *}" = 0 ] && guarded "$h" origin/pr2 && [ "$(git show origin/pr2:a.txt)" = "$SUGGESTED" ] && [ "$(hand origin/main origin/pr2)" = 'b.txt ' ] && equal pr1:main "$3" \
    && pass "developer commit, then merged by $1: EQUAL once the phase merges main" || fail "dev-merged-$1, after the phase took main: $o; proof $out"
}
c_dev_merged_squash() { c_dev_merged squash pr2:pr1 pr2:main::pr1; }
c_dev_merged_true() { c_dev_merged true_merge pr2:main pr2:main; }

c_merged_main_edits() {
  init merged-main-edits; orch; phase
  for i in 1 2 3 4 5 6 7 8; do echo "a $i"; done > a.txt; commit 'feat: a'; c1=$(sha)
  echo b > b.txt; commit 'feat: b'; c2=$(sha)
  step pr1 pr1:main "$c1"; step pr2 pr2:main "$c2"; finish pr1:main pr2:main || fail "merged-main-edits build: $out"
  squash pr1; take_main
  PROOF="pr1:main pr2:main" round pr2 pr2:main; o1="$code $out"
  on_main 'fix: another pull request edits a.txt line 8' put_line 8 'a 8 by another pull request' a.txt; take_main
  h=$(git rev-parse origin/pr2); PROOF="pr1:main pr2:main" round pr2 pr2:main; o2="$code $out"
  [ "${o1%% *} ${o2%% *}" = '0 0' ] && ! echo "$o1$o2" | grep -q '^FAIL' && guarded "$h" origin/pr2 && [ "$(at origin/pr2 a.txt 8)" = 'a 8 by another pull request' ] \
    && [ "$(hand origin/main origin/pr2)" = 'b.txt ' ] && equal pr1:main pr2:main \
    && pass "a squash-merged pull request listed after main edits its file and the phase takes main: EQUAL" || fail "merged-main-edits: $o1 / $o2"
}

c_merged_stale_local() {
  init merged-stale-local; orch; phase
  echo a > a.txt; commit 'feat: a'; c1=$(sha)
  echo b > b.txt; commit 'feat: b'; c2=$(sha)
  step pr1 pr1:main "$c1"; step pr2 pr2:main "$c2"; finish pr1:main pr2:main || fail "merged-stale-local build: $out"
  suggest pr1 a.txt "$SUGGESTED"; squash pr1; h=$(git rev-parse origin/pr2)
  PROOF="pr1:main pr2:main" round pr2 pr2:main; o1="$code $out"
  p1=$(echo "$out" | sed -n '/^pr1:/,$p'); git branch -q -f pr1 origin/pr1; prove pr1:main pr2:main; o2="$code $out"
  out=${o1#* }; has "$(two_remedy a.txt)"; t=$?
  [ "${o1%% *}" = 1 ] && [ $t = 0 ] && ! echo "$o1$o2" | grep -q 'DEVELOPER-COMMITS' && [ "$p1" = "${o2#* }" ] && [ "${o2%% *}" = 1 ] && unchanged pr2 "$h" \
    && pass "a merged pull request with a developer commit: no DEVELOPER-COMMITS, the same proof whether or not the local branch is stale" || fail "merged-stale-local: round $o1; proof with local pr1 synced $o2"
  take_main a.txt
  PROOF="pr1:main pr2:main" round pr2 pr2:main; o="$code $out"
  [ "${o%% *}" = 0 ] && equal pr1:main pr2:main && pass "a merged pull request with a developer commit: EQUAL once the phase merges main" || fail "merged-stale-local, after the phase took main: $o"
}

c_taken_rebased() {
  init taken-rebased; orch; phase
  echo p > p.txt; commit 'feat: parent'; c1=$(sha)
  echo c > c.txt; commit 'feat: child'; c2=$(sha)
  step parent parent:main "$c1"; step child child:parent "$c2"; finish parent:main child:parent || fail "taken-rebased build: $out"
  suggest child c.txt 'c, as the reviewer suggested'; s=$(git rev-parse origin/child)
  git checkout -q phase; git cherry-pick -x "$s" >/dev/null; p=$(sha)
  step parent parent:main; step child child:parent "$p"; finish parent:main child:parent || fail "taken-rebased, the pick carried: $out"
  [ "$(git rev-parse origin/child)" = "$s" ] && [[ ",$PUSHED," == *",child=$s,"* ]] \
    && pass "a taken developer commit carried with nothing to push: the EQUAL round records origin/child at the developer's commit" || fail "taken-rebased, recorded head: origin/child $(git rev-parse origin/child), PUSHED $PUSHED"
  squash parent
  forge child origin/parent || { fail "taken-rebased: the simulated rebase changed the tree"; return; }
  rw=$(git rev-parse origin/child)
  PROOF="parent:main child:main::parent" round child child:main::parent; o="$code $out"
  [ "${o%% *}" = 0 ] && ! has 'DEVELOPER-COMMITS.*' && guarded "$rw" origin/child && [ "$(git show origin/child:c.txt)" = 'c, as the reviewer suggested' ] \
    && [ "$(hand origin/main origin/child)" = 'c.txt ' ] && equal parent:main child:main::parent \
    && pass "a taken developer commit after GitHub rebases the child: the pushed head accounts for it, EQUAL" || fail "taken-rebased: $o"
  h=$(git rev-parse origin/child); PROOF="parent:main child:main::parent" round child child:main::parent; o="$code $out"
  [ "${o%% *}" = 0 ] && [ "$(git rev-parse origin/child)" = "$h" ] && equal parent:main child:main::parent \
    && pass "a taken developer commit after GitHub rebases the child: a further round changes nothing, EQUAL" || fail "taken-rebased, a further round: $o"
}

c_twin() {
  init twin; orch; phase
  echo a > a.txt; commit 'feat: a'; c1=$(sha)
  echo a2 > a.txt; commit 'fix: a2'; f1=$(sha)
  echo a > a.txt; commit 'fix: back to a'; f2=$(sha)
  round pr1 pr1:main "$c1" "$f1" "$f2" || fail "twin build: $out"
  in_wt origin/pr1 sh -c 'echo a2 > a.txt && git commit -q -am "Apply suggestions from code review" && git push -q origin HEAD:pr1'
  s=$(git rev-parse origin/pr1)
  [ "$(git show "$s" | git patch-id --stable | cut -d ' ' -f 1)" = "$(git show "$f1" | git patch-id --stable | cut -d ' ' -f 1)" ] || { fail "twin: the developer's commit does not share a patch-id with $f1"; return; }
  round pr1 pr1:main; o="$code $out"
  [ "${o%% *}" = 1 ] && has "DEVELOPER-COMMITS pr1 $(git rev-parse --short "$s") ?" && [ "$(echo "$out" | tail -1)" = 'NOT EQUAL' ] && unchanged pr1 "$s" && [ "$(git show origin/pr1:a.txt)" = a2 ] \
    && pass "a developer commit with the same patch-id as a phase commit: DEVELOPER-COMMITS, nothing pushed or reverted" || fail "twin: $o"
}

rebased_setup() {
  init "$1"; orch; phase
  echo p > p.txt; commit 'feat: parent'; c1=$(sha)
  echo c > c.txt; commit 'feat: child'; c2=$(sha)
  step parent parent:main "$c1"; step child child:parent "$c2"; finish parent:main child:parent || fail "$1 build: $out"
}

c_rebased_equal() {
  rebased_setup rebased-equal
  squash parent; on_main 'docs: main moves' readme 2
  forge_moved child origin/parent || { fail "rebased-equal: the simulated rebase failed"; return; }
  rw=$(git rev-parse origin/child)
  PROOF="parent:main child:main::parent" round child child:main::parent; o="$code $out"
  [ "${o%% *}" = 0 ] && ! has 'DEVELOPER-COMMITS.*' && guarded "$rw" origin/child && [ "$(git show origin/child:README)" = 'readme 2' ] \
    && [ "$(hand origin/main origin/child)" = 'c.txt ' ] && equal parent:main child:main::parent \
    && pass "a child rebased onto a moved main, owned paths as last pushed: no DEVELOPER-COMMITS, EQUAL" || fail "rebased-equal: $o"
}

c_rebased_dev() {
  rebased_setup rebased-dev
  suggest child c.txt 'c, as the reviewer suggested'
  squash parent; on_main 'docs: main moves' readme 2
  forge_moved child origin/parent || { fail "rebased-dev: the simulated rebase failed"; return; }
  rw=$(git rev-parse origin/child)
  PROOF="parent:main child:main::parent" round child child:main::parent; o="$code $out"
  [ "${o%% *}" = 1 ] && has "DEVELOPER-COMMITS child $(git rev-parse --short "$rw") ?" && [ "$(echo "$out" | tail -1)" = 'NOT EQUAL' ] && unchanged child "$rw" \
    && [ "$(git show origin/child:c.txt)" = 'c, as the reviewer suggested' ] \
    && pass "a rebased child with a developer edit to an owned path: DEVELOPER-COMMITS, nothing pushed or reverted" || fail "rebased-dev: $o"
  git checkout -q phase; git show "$rw:c.txt" > c.txt; commit 'fix: c, as suggested in review'; p=$(sha)
  PROOF="parent:main child:main::parent" round child child:main::parent "$p"; o="$code $out"
  [ "${o%% *}" = 0 ] && ! has 'DEVELOPER-COMMITS.*' && guarded "$rw" origin/child && [ "$(git show origin/child:c.txt)" = 'c, as the reviewer suggested' ] && equal parent:main child:main::parent \
    && pass "the rebased child's edit taken into the phase as an ordinary commit: EQUAL" || fail "rebased-dev remedy: $o"
}

c_taken_before_round() {
  rebased_setup taken-before-round
  suggest child c.txt 'c, as the reviewer suggested'; s=$(git rev-parse origin/child)
  git checkout -q phase; git cherry-pick -x "$s" >/dev/null; p=$(sha)
  squash parent
  forge child origin/parent || { fail "taken-before-round: the simulated rebase changed the tree"; return; }
  rw=$(git rev-parse origin/child)
  PROOF="parent:main child:main::parent" round child child:main::parent "$p"; o="$code $out"
  [ "${o%% *}" = 0 ] && ! has 'DEVELOPER-COMMITS.*' && guarded "$rw" origin/child && [ "$(git show origin/child:c.txt)" = 'c, as the reviewer suggested' ] \
    && [ "$(hand origin/main origin/child)" = 'c.txt ' ] && equal parent:main child:main::parent \
    && pass "a developer commit taken before any round, then the parent squash-merged and the child rebased: the suggestion kept, EQUAL" || fail "taken-before-round: $o"
}

c_never_pushed() {
  init never-pushed; orch; phase
  echo a > a.txt; commit 'feat: a'; c1=$(sha)
  PUSHED="xpr1=$(git rev-parse origin/main)"; round pr1 pr1:main "$c1"; o="$code $out"
  [ "${o%% *}" = 0 ] && ! has 'STOP.*' && [ "$(git show origin/pr1:a.txt)" = a ] && [ "$(hand origin/main origin/pr1)" = 'a.txt ' ] && equal pr1:main \
    && pass "no PUSHED entry on a branch never pushed: the first build proceeds, EQUAL" || fail "never-pushed: $o"
}

c_no_entry() {
  init no-entry; orch; phase
  echo a > a.txt; commit 'feat: a'; c1=$(sha)
  round pr1 pr1:main "$c1" || fail "no-entry build: $out"
  stop="STOP pr1 is on origin but has no PUSHED entry, so its developer commits cannot be told apart"
  rec=$PUSHED; PUSHED=; prove pr1:main
  [ $code = 1 ] && has "$stop" && ! has EQUAL && [ "$(echo "$out" | tail -1)" = 'NOT EQUAL' ] \
    && pass "a pushed branch with an empty PUSHED and no developer commit: the proof STOPs, NOT EQUAL" || fail "no-entry, clean branch: $out"
  PUSHED=$rec; suggest pr1 a.txt "$SUGGESTED"; s=$(git rev-parse origin/pr1)
  prove pr1:main
  [ $code = 1 ] && has "DEVELOPER-COMMITS pr1 $(git rev-parse --short "$s") ?" && pass "with the recorded entry, the developer's commit is reported" || fail "no-entry, with the entry: $out"
  for e in '' "xpr1=$(git rev-parse origin/main)"; do
    PUSHED=$e; round pr1 pr1:main; o="$code $out"
    [ "${o%% *}" = 1 ] && [ "$out" = "$stop" ] && unchanged pr1 "$s" && [ "$(git show origin/pr1:a.txt)" = "$SUGGESTED" ] \
      && pass "a pushed branch with no PUSHED entry ('$e'): the refresh STOPs, the suggestion kept, nothing pushed" || fail "no-entry refresh ('$e'): $o"
    prove pr1:main
    [ $code = 1 ] && has "$stop" && ! has EQUAL && [ "$(echo "$out" | tail -1)" = 'NOT EQUAL' ] \
      && pass "a pushed branch with no PUSHED entry ('$e'): the proof prints the STOP and NOT EQUAL, never EQUAL" || fail "no-entry proof ('$e'): $out"
  done
}

c_pushed_missing() {
  init pushed-missing; orch; phase
  echo a > a.txt; commit 'feat: a'; c1=$(sha)
  round pr1 pr1:main "$c1" || fail "pushed-missing build: $out"
  h=$(git rev-parse origin/pr1); z=0123456789abcdef0123456789abcdef01234567
  stop="STOP pr1 was last pushed at $z, which is not here, so its developer commits cannot be told apart"
  PUSHED="pr1=$z"; round pr1 pr1:main; o="$code $out"
  [ "${o%% *}" = 1 ] && [ "$out" = "$stop" ] && unchanged pr1 "$h" && pass "a recorded pushed head missing here: the refresh STOPs, nothing pushed" || fail "pushed-missing refresh: $o"
  not_equal pr1:main && has "$stop" && pass "a recorded pushed head missing here: the proof prints the STOP and NOT EQUAL" || fail "pushed-missing proof: $out"
}

for c in c_split c_rounds c_rewrite c_r1_squash_fix c_r1_version_fix c_r1_version_build c_r1_orch_merged c_r1_two_squashed c_r1_stack_moves c_r1_spaces \
  c_r2_conflict_commit c_r2_conflict_merge c_r2_clean_merge c_r2_orch_line c_r2_orch_delete c_r2_merge_commit c_r2_row3_to_row2 c_r2_grandchild \
  c_r2_delete_package c_r2_undeclared c_r2_adjacent c_uncarried c_leak c_identity c_assumptions c_missing \
  c_revert c_origin_names c_stop_shared c_stop_owned c_stop_forge c_stop_delegate c_stop_file_to_dir c_stop_dir_to_file c_chain c_merged_listed \
  c_delegate_first_parent c_delegate_after_push c_stack_local c_foreign_local c_retry c_stale_other_stacked c_stale_other_row3 \
  c_extend c_foreign_above c_delegate_after_orch c_mixed_below c_mixed_above c_own_missing \
  c_order_stack_fix c_order_row3_edit c_order_span_chained c_span_unchained c_outside_own c_not_own c_glob c_local_only c_own_refusal \
  c_merged_skipped c_merge_edit_shared c_merge_edit_other c_developer c_update_branch c_update_edit c_landed c_developer_file c_update_child \
  c_dev_merged_squash c_dev_merged_true c_merged_main_edits c_merged_stale_local c_taken_rebased c_twin c_rebased_equal c_rebased_dev c_taken_before_round c_never_pushed c_no_entry c_pushed_missing; do
  (cd "$S" && "$c") || fail "$c ended early"
done
n=$(wc -l < "$S/failed" | tr -d ' ')
echo "$n failed"
[ "$n" = 0 ]
CHECK
```

### Line budget

The handbook has at most 200 lines. Expected: `<n>/200` with `n` at most 200, and exit `0`.

```bash
/bin/bash <<'CHECK'
f="$(git rev-parse --show-toplevel)/packages/s-stack/.apm/skills/sam-mode/handbooks/pr-creator.md"
n=$(wc -l < "$f" | tr -d ' ')
echo "$n/200 $f"
[ "$n" -le 200 ]
CHECK
```

### Cold read. What each `STOP` means and who acts

A `STOP` line hands work to someone, and the PR creator acts on the handbook's prose, so this check is a cold read. Start a fresh subagent, give it only `packages/s-stack/.apm/skills/sam-mode/handbooks/pr-creator.md`, tell it to read nothing else, and ask the question. Its answer passes when it agrees in substance with every point of the expected answer. Wait for it to finish before reporting.

Prompt: "Read only the file `packages/s-stack/.apm/skills/sam-mode/handbooks/pr-creator.md` and nothing else, not even files it links to or names. Answer from it alone. You are the PR creator for phase `widgets`. The default branch is `main`. Your pull request #12 is on branch `widgets-pr`. Each item below is output you see in a round. For each, say what it means, who acts next and what they do, what you do, and in what state the branch is left. (1) The refresh prints `STOP shared.txt changed on origin/main after the phase last took it, so the phase must merge it first` and exits 1. (2) The same line, but naming `gadgets-pr`, another phase's open pull request that #12 depends on, instead of `origin/main`. (3) The refresh prints `STOP shared.txt conflicts outside generated content`, then `STOP 1a2b3c4 feat: widgets does not apply`, then `STOP shared.txt is a shared path, so the stop is permanent: no merge or commit on the phase clears it, and it needs a decision`, while a parent pull request of your own phase had a fix round on the line next to your change. (4) The refresh prints `STOP gadgets-pr does not hold origin/main, so widgets-pr must target it with gadgets-pr merged in`. Answer twice: (a) `widgets-pr` is a new pull request; (b) `widgets-pr` is already stacked on an open parent and the base table now gives another base. (5) The refresh prints `STOP gone is not a branch here`, where `gone` is a dependency that merged last week. (6) A carry stops and also prints `the branch is back at 9f8e7d6`. What has happened to the branch and to `origin/widgets-pr`? (7) The proof prints `FAIL a.txt has not landed and is in no open pull request, so it needs a new pull request`. Answer twice: (a) `a.txt` changed in a fix the phase made after its pull request merged; (b) the named path is `orch-fix.txt`, which the orchestrator committed on the orchestrator branch outside `.foundry/`. (8) May you resolve any of these conflicts yourself by editing files? (9) `widgets-pr` targets `main` and carries `gadgets-pr`, which was stacked on `gizmos-pr`. After `gizmos-pr` merged, every round's refresh prints `STOP widgets-pr would carry gadgets.txt, which the phase does not change`, where `gadgets.txt` is one of `gadgets-pr`'s files, and it still does after `gadgets-pr` merges. (10) The phase session merged a delegate's branch into the phase with a merge commit, and the refresh prints `STOP widgets-pr would carry d.txt, which the phase does not change` for the delegate's file `d.txt`. (11) The refresh prints `git checkout-index: notes is not in the cache`, then `STOP notes cannot be written into the tree, as when a file and a directory share its name`, after the phase replaced the file `notes` with a directory `notes/` holding `one.md`. (12) Before your next round, the developer amended a commit on `widgets-pr` and force-pushed it, as GitHub's 'Update with rebase' does. What does the round detect, and what may it do to the developer's change? What should the developer do instead of rewriting the branch, what do you do, and what does each pull request description ask of reviewers about this? For (1), (2), (3), (9), (10) and (11), also say who decides, and what the options or the action are that would clear it."

Expected answer:

1. The default branch changed a path the pull request owns after the phase last took it, even without a conflict, such as another pull request landing an edit elsewhere in the file. The PR creator does not work around it. It reports the output to the phase session, which sends it to the orchestrator as a decision request. Clearing it needs the phase to merge `origin/main` and resolve any conflict there, which moves the phase's code head and so needs Verify and Review again; it is not a gate-free round. The decision is whether the phase merges now. The branch is left where it started, nothing is pushed.
2. The same stale path, changed by the phase that owns `gadgets-pr`. The same decision request goes through the phase session to the orchestrator. Clearing it needs this phase to merge `gadgets-pr` and resolve any conflict there, with both gates again. The PR creator never writes `gadgets-pr`'s branch.
3. A shared path's own commits do not apply on this base, and the stop is permanent: neither a merge resolution nor a resolution commit on the phase reaches the pull request. The PR creator reports the lines to the phase session and does not resolve the conflict, and the phase session sends the orchestrator a decision request. The options are a one-off rebuild of the branch from its base, which force-pushes and needs the developer's approval, or a replacement pull request on a new branch. The branch is back where it started, nothing is pushed.
4. (a) Use the third row of the base table: target `main` with `gadgets-pr` merged in, a spec such as `widgets-pr:main:gadgets-pr`, and no `gh stack link`. (b) This is leaving a stack. Do not refresh it onto the new base, and do not run `gh stack unstack`. Report it to the phase session.
5. A branch in the spec is missing. Fetch again, restore the merged dependency's ref with `git fetch origin pull/<number>/head:refs/remotes/origin/gone`, or correct the spec, then run the round again. Never prune remote-tracking refs.
6. The carry failed and the branch was reset to the head it started from. `origin/widgets-pr` is untouched, because pushing comes after a successful refresh.
7. (a) An uncarried phase change. Open a new draft pull request for it, with its base from the base table and a new branch, run its round and the three checks again. (b) A broken assumption of the proof, not the phase's own work. Open no pull request. Report it to the phase session with the `FAIL` lines, and the phase session raises it with the orchestrator.
8. No. The PR creator never resolves a hand-written conflict and never changes what the code does.
9. GitHub rewrote `gadgets-pr`'s head when its parent merged, so `widgets-pr` holds the old head, whose commits now count as its own, and the stop recurs in every round, even after `gadgets-pr` merges. The PR creator does not work around it and opens no pull request for it. It reports the output to the phase session, which sends the orchestrator a decision request with the same two options as (3): a one-off rebuild that force-pushes with the developer's approval, or a replacement pull request on a new branch. The branch is left where it started, nothing is pushed.
10. A delegate's branch merged into the phase leaves its commits off the phase's first-parent line, so they are not phase commits. The PR creator opens no pull request for it and reports the output to the phase session, which sends the orchestrator a decision request. Either the phase session rebuilds its phase branch locally without that merge, taking the delegate's commits with `git cherry-pick -x` so they become phase commits that the next round carries, a local rewrite that needs Verify and Review again, or the orchestrator decides otherwise. The branch is left where it started, nothing is pushed.
11. The phase replaced a file with a directory of the same name, which the design does not handle. The PR creator reports it to the phase session, which sends the orchestrator a decision request: whether to split that change by hand, or to undo it in the phase. The branch is left where it started, nothing is pushed.
12. A rewritten pull request branch is a history the design does not detect. The round may print `EQUAL`, or a stop whose remedy has nothing to commit, and it can put the phase's version back over the developer's change, because an amended commit keeps its `cherry-pick` line. It is out of scope: the handbook states as a precondition that nobody rewrites a pull request branch. The developer adds commits on top, uses "Update branch", or comments. The PR creator does not work around it. If it happens, the phase session reports it to the orchestrator before any round. Each description asks reviewers to add commits on top, use "Update branch" or comment, and never to rewrite the branch with an amend, a squash or "Update with rebase".

## Evidence

The phase's own verifier runs these at every code head it verifies. They are never rerun by the merged-branch check.

### `gh stack link` with pull request numbers only links

What it checks: the handbook's rule that `gh stack link <parent number> <own number>` adds a pull request on top of its parent's stack without pushing or rebasing any branch, and that linking a merged pull request is refused. The scratch cases cannot reach GitHub.

How: in a throwaway public repository owned by the developer, never Foundry, push two branches with plain `git push`, open both as drafts with `gh pr create --draft`, and run `gh stack link <first> <second>`. Record both branches' head SHAs before and after, and the stack GitHub shows. Then merge the first, open a third draft on the second, and run `gh stack link <first> <third>`. The rule holds when the heads do not move on the first link and the second link is refused. This changes state on GitHub, so the developer runs it or approves it first.

### A forge rewrite keeps the tree

What it checks: the handbook's rule that when a stack parent merges, GitHub may rewrite the child's head with the same tree and new commits, which the `forge rewrite` and `round 2 grandchild` cases simulate.

How: pick a pull request of this run whose stack parent has merged, from the run's decisions. Read its force-push events with `gh api graphql`, asking for `pullRequest(number: <n>) { timelineItems(itemTypes: [HEAD_REF_FORCE_PUSHED_EVENT]) { nodes { ... on HeadRefForcePushedEvent { createdAt beforeCommit { oid tree { oid } } afterCommit { oid tree { oid } } } } } }`. The rule holds when an event at the parent's merge time has equal tree ids and different commit ids. It only reads.
