# Cross-handbook integration fixes

Read on branch `s-stack-package` at `dfbad07`. All paths under `packages/s-stack/.apm/skills/sam-mode/` are written from that directory. Roadmap paths are under `.foundry/feature-roadmaps/2026-11-20_21-37-12-s-stack/`. "Row n" of `run-decisions.md` means file line n.

Severity: **common path** breaks or blocks a normal run. **Minor** is a rare history or a wrong but harmless reading. **Cosmetic** is wording only.

The goal: every handbook a session follows at the same time agrees with the others and with the reference file, and the gate-cost rules (run-decisions row 65) are in the handbook text.

## Summary

| Owner | Common path | Minor | Cosmetic |
| --- | --- | --- | --- |
| foundation | 7 | 2 | 3 |
| phase-handbooks | 11 | 5 | 2 |
| spec-planner-handbooks | 0 | 1 | 1 |
| orchestrator-handbook | 2 | 7 | 1 |
| pr-handbook | 1 | 2 | 0 |
| board | 0 | 0 | 0 |

## One design choice to settle first (foundation)

Gate-cost rule 7 (`proposals/gate-cost.md` line 120) says a clean merge "needs no gate of its own". Rule 6 (line 116) keeps "both naming the current code head". The current code head (`references/status-and-messages.md` line 60) moves on every merge that brings code. So after a clean merge no verdict names the current code head, and the phase cannot reach PR without a gate. The rules cannot both hold as written.

Recommended: a clean merge of the orchestrator branch moves no code head (item F1). This is how `launcher-r3` worked (row 51: "leaves the phase's code head and verdicts in place"), and rule 7 generalises it (row 66). It keeps `SKILL.md` line 85 and `phase-session.md` line 98 correct unchanged. A merge of the default branch still moves the code head, because `orchestrator.md` line 104 waits for "a code head that contains that tip" and line 88 refuses to re-merge a code head it has merged. Its gates are scoped to the phase's own work, so a clean one is waived cheaply.

The alternative is a rule that lets a verdict cover later clean merges. It needs a second test at every place that reads verdicts (`orchestrator.md` line 88, `pr-creator.md` line 11, `phase-session.md` line 84). Not recommended.

I ran the command in F1 in a scratch repository under bash. A clean merge of the orchestrator branch left the code head on the phase's commit. A conflicted merge of it moved the code head to the merge. A clean merge of `main` moved it to the merge.

## foundation: `SKILL.md`, `references/status-and-messages.md`, `tests/s-stack/verify-s-stack/SKILL.md`

### F1. The code head does not implement gate-cost rule 7. Common path.

- **Where.** `references/status-and-messages.md` line 60.
- **Wrong.** "a merge that brings in code moves it". Every clean merge of the orchestrator branch cancels both verdicts.
- **Conflicts with.** `proposals/gate-cost.md` line 120: "A clean merge needs no gate of its own, even when it touches the phase's owned paths." Row 66 retires `launcher-r3` in favour of it.
- **Fix.** Replace the first three sentences of the bullet, up to "from the worktree root.", with:

  > **Code head.** It is the newest commit on the phase branch's first-parent line whose diff against its own first parent changes a file outside `.foundry/`, with one exception. A clean merge of the orchestrator branch moves no code head, because code merged in from it counts as verified and reviewed. A merge of the orchestrator branch is one whose second parent is on the orchestrator branch's first-parent line. It is clean when its tree equals git's automatic merge of its two parents outside `.foundry/`. Any other merge that brings in code moves the code head, a merge of the default branch and a conflict resolution included. Run this under bash from the worktree root:
  >
  > ```bash
  > ob=$(git rev-list --first-parent <orchestrator branch>)
  > for c in $(git rev-list --first-parent <phase branch>); do
  >   if p2=$(git rev-parse -q --verify "$c^2") && grep -qx "$p2" <<<"$ob"; then
  >     t=$(git merge-tree --write-tree "$c^1" "$p2" | head -n 1)
  >     git diff --quiet "$t" "$c" -- . ':(exclude).foundry' && continue
  >   fi
  >   git diff --quiet "$c^" "$c" -- . ':(exclude).foundry' || { echo "$c"; break; }
  > done
  > ```

  Then, in the same bullet, change "Its sessions then add `':(exclude,glob)**/<name>'` to the `git diff` pathspecs" to "Its sessions then add `':(exclude,glob)**/<name>'` to both `git diff` pathspecs". Keep the rest of the bullet.

### F2. The verdict values and the merge rule lack `WAIVED`. Common path.

- **Where.** `references/status-and-messages.md` lines 31 to 32 and line 61.
- **Wrong.** Line 31 allows `VERIFIED | NOT VERIFIED | INCONCLUSIVE`, line 32 `CLEAR | SIGNIFICANT`. Line 61 needs `VERIFIED` and `CLEAR`.
- **Conflicts with.** Gate-cost rules 3 and 6 (`proposals/gate-cost.md` lines 82 and 116), and row 65.
- **Fix.** Line 31: `# verify: VERIFIED | NOT VERIFIED | INCONCLUSIVE | WAIVED`. Line 32: `# review: CLEAR | SIGNIFICANT | WAIVED`. Line 61, replace the second and third sentences with:

  > The merge rule is that the newest `verify` verdict is `VERIFIED` or `WAIVED`, the newest `review` verdict is `CLEAR` or `WAIVED`, and both name the current code head. A `WAIVED` verdict counts only when the newest earlier verdict of the same gate that is not `WAIVED` is `VERIFIED` or `CLEAR`. A phase moves to PR once the rule holds, and `handbooks/orchestrator.md` owns the further checks the orchestrator makes before it merges.

  The second sentence is item F3.

### F3. A waiver can pass a gate that last failed. Minor.

- **Where.** Gate-cost rule 6 (`proposals/gate-cost.md` line 116), which F2 puts at reference line 61.
- **Wrong.** As written, review `SIGNIFICANT` at one head, then a comment-only commit that both gates waive, satisfies "the newest `review` verdict is `CLEAR` or `WAIVED`". The significant finding was never fixed, and the phase reaches PR.
- **Conflicts with.** Gate-cost rule 4 (line 108): "A waiver never moves the baseline", and `README.md` line 71, "No skipped gate".
- **Fix.** The second sentence of F2's line 61 wording. It is a reading of rule 4, not a new rule. Record it in `run-decisions.md` as a clarification of gate-cost.

### F4. No single home for the waiver test. Common path.

- **Where.** `references/status-and-messages.md`, after the **Verdicts** bullet (line 61).
- **Wrong.** Both `verifier.md` and `reviewer.md` need the same waivable and never-waivable lists (gate-cost rule 3, lines 84 to 104). Two copies would drift.
- **Fix.** Add a bullet:

  > **Waivers.** A fresh gate agent, the verifier or the first reviewer, may return `WAIVED` instead of running its gate, with its reason. It may do so only when the diff in its scope changes nothing that a user, a program or an agent reading the file would act on differently. Waivable: generated files only; formatting, import order or a linter's auto-fix; a complete rename of a local variable or private function; comments, docstrings, log wording, or a typo in a user-facing string that no test asserts; a small, isolated change whose whole effect the agent can state from the diff and that no check or probe exercises. Never waivable: any change to logic or control flow; a change to a public interface or contract; a dependency added or bumped by hand; anything touching authentication, permissions, secrets, input handling or the commands the code runs; a test or check change that alters an expected result; a change to instructions an agent follows, such as a prompt, skill or handbook. An empty scope is waivable. A waiver never moves a gate's baseline: the next scoped Verify covers everything since the last `VERIFIED` code head, and the next Review everything since the last `CLEAR` or `SIGNIFICANT` one.

### F5. The status header has no slot for the pushed heads. Common path.

- **Where.** `references/status-and-messages.md` lines 36 to 41, and the rules at lines 58 to 64.
- **Wrong.** `pr-creator.md` line 55 says `<pushed heads>` comes from "the phase session's brief ... from its status file", and line 163 says the phase "records [the `RECORD` line] in its status file". The header has no such key. Without it, `PUSHED` is empty. `references/pr-commands.md` line 86 then stops any branch already on `origin`: "A branch on `origin` with no entry stops". So every round after the first push stops. Known items 14 and 15 (`integration-items.md` lines 14 and 15).
- **Conflicts with.** `pr-creator.md` lines 55, 74 and 163; `pr-commands.md` lines 40 and 86; run-decision row 16 ("The boundary is the head the PR creator last pushed, recorded in the phase's status").
- **Fix.** After line 41 add:

  ```yaml
  pushed: "<branch>=<sha>,<branch>=<sha>"  # the PR creator's last RECORD line, else null
  ```

  Add a rule after **Evidence**:

  > **Pushed heads.** `pushed` holds the `RECORD` line of the PR creator's last proof that printed `EQUAL` and whose pushes all succeeded, without the word `RECORD`, exactly as printed. It is `null` before the first push. The phase passes it unchanged as the PR creator's `PUSHED`. `pull_requests` keeps every pull request once opened, merged ones included, because the PR creator's `OWN` lists them all.

### F6. `prs-open` does not carry the heads or the code head. Common path.

- **Where.** `references/status-and-messages.md` line 85.
- **Wrong.** It carries "Each number with its `depends_on` list". `orchestrator.md` line 148 records each head when the message arrives, so a developer commit made between the push and the arrival is never compared. Line 88 needs "the code head each `prs-open` arrived at", which the message does not state. Known item 15.
- **Conflicts with.** `orchestrator.md` lines 56, 88 and 148; run-decision row 15 ("comparing its head with the head in the phase's last `prs-open`").
- **Fix.** Line 85's third column:

  > Each number with its `depends_on` list, the code head the pull requests hold, and the `pushed` line from the status file

### F7. The orchestrator's message table does not match the kinds it sends. Common path.

- **Where.** `references/status-and-messages.md` lines 95 to 102.
- **Wrong.**
  - Line 95's `instruction` is "in the developer's words". The orchestrator also sends its own instructions: ask for `prs-open` (`orchestrator.md` lines 72 and 181), refresh onto a dependency's head (line 117), refresh after a head moved (line 148), fix a Done phase's status files (line 129), and restart the planner (line 177).
  - Lines 98 and 99 split one kind in two. `orchestrator.md` line 117 and `phase-session.md` line 111 use one kind, "A pull request merged", and line 117's payload is the default branch's tip, not "the pull request" or "the merged pull request and the dependent one". Known item 6.
  - Known item 8 asks for the developer's commits on the line 97 row. That is superseded: under run-decision row 15 they reach the phase through the refresh `instruction`, not a `fix-round`. The row below covers it.
- **Fix.** Replace lines 98 and 99 with one row:

  > | `fix-round` | A pull request merged: a pull request lacks the default branch's tip, because a dependency merged or the default branch moved | The pull request and the default branch tip |

  After line 95 add:

  > | `instruction` | A pull request's head differs from the head in the phase's last `prs-open` | The pull request, the recorded head and its current head |
  > | `instruction` | A pull request lacks the current head of a pull request it depends on | The pull request and the dependency's head |
  > | `instruction` | A phase in PR has sent no `prs-open` at its current code head, or the orchestrator restarted | A request to send `prs-open` once a pull request holds that code head |
  > | `instruction` | A Done phase's status-only merge was refused for its own status files | The files, and a request to fix them in a `.foundry/`-only commit and stay Done |

  The planner restart is not a phase message. Add to line 90: "The planner takes an `instruction` to revise the plan, as [handbooks/planner.md](../handbooks/planner.md) says."

### F8. `blocked` does not say to record `waits_for`. Minor.

- **Where.** `references/status-and-messages.md` line 84.
- **Wrong.** The row carries "What it waits for". Rule 107 needs the fact committed first, but no file says where a phase commits it.
- **Conflicts with.** `orchestrator.md` line 13, which judges a quiet phase without `waits_for` as stalled.
- **Fix.** Third column: "What it waits for, which a phase first commits as `waits_for`".

### F9. "A fact already committed to the sender's own file" does not fit two messages. Cosmetic.

- **Where.** `references/status-and-messages.md` lines 74 and 107.
- **Wrong.** `started` is sent before the planner or spec writer has committed anything (`planner.md` line 23, `spec-writer.md` line 43). Known item 7.
- **Fix.** Line 74: `<detail lines, each a fact the sender has already committed, except a started message's name and branch>`. Rule 107: "A sender commits the fact first and then sends the message, so a lost message costs time and loses no information. `started` is the exception: it carries only the session name and branch, which the launcher made."

### F10. "The repository root" is ambiguous in a worktree. Cosmetic.

- **Where.** `SKILL.md` line 31.
- **Wrong.** A session in a worktree has to work out which root is meant. Known item 9.
- **Conflicts with.** `orchestrator.md` line 22, "from the feature worktree's root".
- **Fix.** "Run these two commands with your own worktree's root as the working directory:". Leave line 24, which runs from the main checkout.

### F11. Nothing records the Spec state. Cosmetic.

- **Where.** `SKILL.md` lines 83 to 84.
- **Wrong.** "Only the phase session changes its phase's state, by committing its status file", and a phase "skips none". But the phase session's first commit is in Plan (`phase-session.md` line 37), so Spec is never committed.
- **Fix.** Add to line 84: "A phase is in Spec until its session first commits its status file, in Plan."

### F12. The verification skill runs every check on every Verify. Common path.

- **Where.** `tests/s-stack/verify-s-stack/SKILL.md` check 8 (lines 155 to 162).
- **Wrong.** "run every check in each file's `## Rerun` section". Gate-cost rule 1 scopes Verify to the blast radius.
- **Conflicts with.** `proposals/gate-cost.md` lines 70 to 73 and line 164.
- **Fix.** Add after line 162: "A scoped run, which the verifier and the post-merge check make, runs only the checks its brief names as in the blast radius, and reports each other check file with the brief's reason. The full run, every Rerun check, is for the end of the feature and for when the developer asks."

## phase-handbooks: `phase-session.md`, `verifier.md`, `reviewer.md`

### P1. The phase session never sets `waits_for`. Common path.

- **Where.** `handbooks/phase-session.md` lines 56, 69, 86, 125 and 129.
- **Wrong.** No line sets `waits_for`. A phase waiting on a decision, a blocked conflict or a `move-back` to Plan is quiet with no `waits_for`. After two ticks the orchestrator replaces it, and the fresh session waits again.
- **Conflicts with.** `orchestrator.md` line 13: "A session has stalled when it still has work, is quiet, its status has no `waits_for`, and it has made no pull request change for two ticks." Reference line 28 defines the key.
- **Fix.** Add to "Changing state", after line 33:

  > Whenever you wait, for an answer, a blocked merge or a `move-back`, set `waits_for` to one line saying what for, in the commit that records the request or the state, before you send the message. Set it back to `null` in the commit that ends the wait.

### P2. The PR creator's brief lacks what `pr-creator.md` needs, and `pushed` is never recorded. Common path.

- **Where.** `handbooks/phase-session.md` line 85 (step 2) and line 89 (step 3).
- **Wrong.** The brief gives "the absolute path of `handbooks/pr-creator.md`, the roadmap, the feature plan and your phase plan". `pr-creator.md` line 9 also needs "the phase's status file, the phase branch and the orchestrator branch". Line 55 needs the `PUSHED` line and the list of own branches. Step 3 records `pull_requests` but not the `RECORD` line. After a forge-rewrite decision, `pr-creator.md` line 74 says "the next brief's `PUSHED` then adds `<pr>=<head>`", and no line says who adds it. Known items 11 and 14.
- **Conflicts with.** `pr-creator.md` lines 9, 55, 74 and 163; `pr-commands.md` lines 40 and 86; F5.
- **Fix.** Step 2, replace "the roadmap, the feature plan and your phase plan" with:

  > the roadmap, the feature plan, your phase plan, your status file, the phase branch, the local orchestrator branch (never `origin/<orchestrator branch>`, which may lag or not exist), every pull request branch in `pull_requests` as `OWN`, and `pushed` as `PUSHED`

  Step 3, replace with:

  > 3. Record each pull request in `pull_requests`, and the report's `RECORD` line, without the word `RECORD`, as `pushed`. Commit, then send `prs-open` with each number and its `depends_on` list, the code head and the `pushed` line.

  In the `answer` row (line 96), add: "When the answer says a rewritten pull request branch holds no edits of the developer's, or once you have taken them, append `<pr>=<its current head>` to `pushed` and commit, as `pr-creator.md` says."

### P3. No row for the orchestrator's refresh and `prs-open` instructions. Common path.

- **Where.** `handbooks/phase-session.md` line 97.
- **Wrong.** The `instruction` row says to follow it "as an instruction from the developer". The orchestrator sends instructions that ask for a PR creator round and a `prs-open`, not for new work. Readers inferred "start a PR creator" from PR step 2 (`orchestrator-handbook-evidence.md` line 785). Known item 16.
- **Conflicts with.** `orchestrator.md` lines 72, 117, 148 and 181; F7.
- **Fix.** Add to the row:

  > An instruction to refresh a pull request, or to send `prs-open` at your code head, asks for a PR creator round, not new work. In PR, run [PR](#pr) steps 2 and 3. On `DEVELOPER-COMMITS`, run the feedback round. Otherwise the phase stays in PR and no gate runs again. In any other state, reply with `state`.

### P4. PR step 2 sends `prs-open` after a failed round. Common path.

- **Where.** `handbooks/phase-session.md` lines 86 to 88.
- **Wrong.** Only a `STOP` and `DEVELOPER-COMMITS` hold back `prs-open`. "Neither: go on to step 3" covers a `FAIL` with `NOT EQUAL`, a failed push, a failed gate check, a failed repository check, and "a code change a branch needs". The phase then sends `prs-open` for pull requests that were never pushed or proved.
- **Conflicts with.** `pr-creator.md` lines 58, 60, 150, 152, 154, 156 and 167.
- **Fix.** Replace the third bullet ("Neither: go on to step 3.") with:

  > - A `FAIL` line, `NOT EQUAL`, a failed push, a failed gate, a failing repository check or a code change a branch needs: send no `prs-open`. For `<path> differs between the phase and <default>`, merge `origin/<default>` into the phase branch with `git merge --no-ff`, keeping the default branch's version, then pass the gates the new code head needs and run step 2 again. For a code change, move back to Implement and make it. Send a decision request for anything else.
  > - Only a proof that printed `EQUAL`, with every push done: go on to step 3.

### P5. The allowed phase-branch merges leave out the PR creator's remedy. Minor.

- **Where.** `handbooks/phase-session.md` line 43.
- **Wrong.** "The only merges on the phase branch's first-parent line are merges of the orchestrator branch and, in a conflict round, of the default-branch commit it names."
- **Conflicts with.** `pr-creator.md` line 150, where the phase "merges `origin/<default>` into the phase".
- **Fix.** "... and, in a conflict round or after the PR creator reports that a path differs from the default branch, of `origin/<default>` or the commit the round names."

### P6. Moving back to Spec and Plan describes the wrong trigger. Minor.

- **Where.** `handbooks/phase-session.md` lines 124 and 125.
- **Wrong.** Line 125 waits for a `move-back` to Plan "once the update has merged". Line 124 runs Plan "after the planner changed your phase's entry".
- **Conflicts with.** `orchestrator.md` line 177: it sends `move-back` to Plan after the planner's `done-planning`, to "every phase you sent to Spec for this update, whether or not the planner changed its entry". Recorded at `orchestrator-handbook-evidence.md` lines 489, 520 and 575.
- **Fix.** Line 124: "**Plan**, after the planner revised the feature plan. Merge the orchestrator branch, update the phase plan against your entry, which may be unchanged, commit it, and move to Implement." Line 125: "**Spec**, after a roadmap update touched your phase. Wait, with `waits_for` set, for a `move-back` to Plan, which the orchestrator sends once the planner has revised the plan."

### P7. The `answer` handler leaves the request open. Minor.

- **Where.** `handbooks/phase-session.md` line 96.
- **Wrong.** "Record the outcome in `decisions`, commit". It does not remove the request.
- **Conflicts with.** Reference line 125: "It removes the request from `requests` once the answer arrives." The orchestrator's reconcile reads open requests from the header (`orchestrator.md` line 154), so a stale one is put to the developer again.
- **Fix.** "Remove the request from `requests`, record the outcome in `decisions`, clear `waits_for` if the answer ends the wait, commit, and continue the work that waited."

### P8. The feedback round does not cover a developer merge's hand edits. Minor.

- **Where.** `handbooks/phase-session.md` line 107.
- **Wrong.** It takes "each commit the developer made ... with `git cherry-pick -x`". A merge cannot be taken that way.
- **Conflicts with.** `pr-creator.md` line 117: "for a merge's hand edits, makes an ordinary phase commit that gives those paths the merge's content".
- **Fix.** After the first sentence add: "For a developer's merge with hand edits, make an ordinary commit that gives those paths the merge's content."

### P9. The plan-roadmap disagreement has no message kind. Minor.

- **Where.** `handbooks/phase-session.md` line 14.
- **Wrong.** "the roadmap wins, and you tell the orchestrator", with no kind. Only the planner changes the plan.
- **Conflicts with.** `planner.md` line 33 and `phase-session.md` line 129, which both use a decision request for a plan change.
- **Fix.** "... the roadmap wins, and you send the orchestrator a decision request that names both texts."

### P10. `stop` commits the status file even when nothing changed. Cosmetic.

- **Where.** `handbooks/phase-session.md` line 101.
- **Fix.** "Commit unfinished code to the planned pull request it belongs to, commit your status file if it changed, then end your turn."

### P11. "A pull request merged" names a narrower trigger than the sender's. Cosmetic.

- **Where.** `handbooks/phase-session.md` line 111.
- **Wrong.** "One that your pull requests depend on has merged, or another phase's pull request has landed ... and left your generated files stale."
- **Conflicts with.** `orchestrator.md` line 117, which sends it whenever a pull request lacks the default branch's tip.
- **Fix.** "**A pull request merged.** A pull request of yours lacks the default branch's tip, because a dependency merged or the default branch moved. The message names the pull request and the tip."

### P12. Gate-cost: line 26 still re-runs everything. Common path.

- **Where.** `handbooks/phase-session.md` line 26.
- **Wrong.** "verification runs again in full ... Never carry an old verdict forward because the change looks small."
- **Conflicts with.** Gate-cost rule 1 (line 74: "This replaces 'verification runs again in full' in ... `phase-session.md`") and line 159.
- **Fix.** Replace the paragraph with:

  > Compute the code head as the reference file says, with an exclude for each generated path and each generated line the feature plan names. A verdict covers only the code head it names. A commit that moves the code head needs new verdicts, each from a fresh gate agent. Verify covers the blast radius of your own work since the last `VERIFIED` code head, as [verifier.md](verifier.md) says, and Review covers what [reviewer.md](reviewer.md) says. A gate agent may return `WAIVED` under the reference file's waiver rule. Record it as the verdict, with its reason in the evidence file. Never decide yourself that a change needs no gate.

### P13. Gate-cost: the Verify step has no baseline and no `WAIVED`. Common path.

- **Where.** `handbooks/phase-session.md` lines 61 and 65 to 69.
- **Wrong.** The verifier's brief has no baseline head, so it cannot scope. The table has no `WAIVED` row.
- **Conflicts with.** Gate-cost rules 1 and 3 (lines 70 and 82).
- **Fix.** Line 61, add after "the verification skill": ", the code head of your newest `VERIFIED` verdict, or none, and, after a `move-back` for a failed check, the failed check". Add a table row after line 67:

  > | WAIVED, for the current code head | Review |

### P14. Gate-cost: the Review step starts both reviewers and has no `WAIVED`. Common path.

- **Where.** `handbooks/phase-session.md` lines 74 and 77 to 80.
- **Fix.** Line 74: "Run the gate as [reviewer.md](reviewer.md) says. It starts one reviewer first, who may waive." Add a table row after line 79:

  > | WAIVED, for the current code head | PR |

### P15. Gate-cost: "Merge the orchestrator branch" says Verify re-covers every merged phase. Common path.

- **Where.** `handbooks/phase-session.md` line 53.
- **Wrong.** "Verification then covers your phase together with every phase merged so far."
- **Conflicts with.** Gate-cost rule 7 (lines 120 to 126) and run-decision row 67 (the frozen-branch narrowing).
- **Fix.** Replace that sentence with:

  > Code a clean merge brings in counts as verified and reviewed, and the reference file's code head does not move for it. Your own conflict resolution is your work, and the gates cover it. One exception: after merging, read the orchestrator branch tracker's "Merged phases" table. If the newest post-merge check failed and it touches something your phase builds on or changes, treat the merged-in code as your own: name that check, and the merge, in the verifier's and the reviewers' briefs. A red default branch is the same: ignore it unless it fails in something your phase builds on or changes.

### P16. Gate-cost: the verifier always reads the whole phase and runs every check. Common path.

- **Where.** `handbooks/verifier.md` lines 14, 41, 42 and 52.
- **Wrong.** Line 14 reads the whole phase diff. Line 52 runs "the whole verification skill". Line 41 says later verifiers and the merged-branch check run every Rerun check. Line 42 says the phase's verifier runs its Evidence checks "at every code head it verifies".
- **Conflicts with.** Gate-cost rule 1 (lines 70 to 73) and line 157.
- **Fix.**
  - Line 14: "Your scope is the phase's own work since the code head of its newest `VERIFIED` verdict: each commit and merge resolution that [reviewer.md](reviewer.md)'s Running the gate step 1 names, with that head in place of the last reviewed one. With no `VERIFIED` verdict, it is the whole phase diff, `git diff <orchestrator branch>...<phase branch> -- . ':(exclude).foundry'`. The brief may name a failed post-merge check and a merge to add to it. The code you run holds the phase together with every phase merged so far."
  - Line 41, last sentence: "Later verifiers and the orchestrator's post-merge check run those in their blast radius, and the full run at the end of the feature runs all of them."
  - Line 42: "The phase's own verifier runs them when they are in its blast radius."
  - Line 52, step 1: "Work out the blast radius: every behaviour your scope can affect. A check is in it when any file it names or reads changed, and a change to a shared helper takes in every check whose behaviour runs through the helper. Run every check in the radius, from any phase's check file, every new or changed check, and the `## Evidence` checks of your own check file that are in the radius. Run no check outside it."

### P17. Gate-cost: the verifier cannot waive, and "None" is not split. Common path.

- **Where.** `handbooks/verifier.md` lines 22, 60 to 66 and 70 to 76.
- **Conflicts with.** Gate-cost rule 3 (lines 82 and 101 to 104).
- **Fix.**
  - After line 22 add: "**Waived.** When your scope changes nothing that a user, a program or an agent reading the file would act on differently, return `WAIVED` under the reference file's waiver rule, with your reason, and run nothing. When something could observe the change but no check can run here, the verdict is INCONCLUSIVE, not WAIVED."
  - Add a row after line 62: "| WAIVED | The scope passes the reference file's waiver rule. No check ran. |"
  - Add to the report list after line 72: "- The checks you ran, and, for each check file, why the rest are outside the blast radius." and "- For WAIVED, the reason."

### P18. Gate-cost: the reviewer's baseline and the first reviewer's waiver. Common path.

- **Where.** `handbooks/reviewer.md` lines 11, 14, 16 and 20 to 41.
- **Conflicts with.** Gate-cost rules 2, 4 and 5 (lines 78, 108 and 112).
- **Fix.**
  - Line 11, second sentence: "Every later review covers what changed since the code head of the most recent `CLEAR` or `SIGNIFICANT` review, never a `WAIVED` one, and only the phase's own work." Replace `<last reviewed code head>` in both commands with `<last reviewed code head, not waived>`.
  - Before step 4 add: "**One reviewer first.** Start one reviewer on one model family. It reads the scope and either returns `WAIVED` with its reason, or reviews. When it reviews, start the second adversary on the other model family, as `interrogate` says."
  - Line 16: "SIGNIFICANT when at least one finding is significant. CLEAR when none is. WAIVED when the first reviewer waived. The verdict names the code head that the scope ends at."
  - In The brief, after **Probes** add: "**Waiving.** If your brief says you are the first reviewer, you may return `WAIVED` instead of reviewing, under the waiver rule in `references/status-and-messages.md`, with your reason. You may not waive while a probe from an earlier significant finding still shows the failure."

## spec-planner-handbooks: `planner.md`, `spec-writer.md`

### S1. The plan cannot say a dependency must be Done. Minor.

- **Where.** `handbooks/planner.md` line 40.
- **Wrong.** "Depends on: The phases that must be merged into the orchestrator branch before it starts, or none."
- **Conflicts with.** `orchestrator.md` line 71, "or, where the plan says it must be Done", and the board's `depends_on.until` of `"done"` (`assets/status-board.html` lines 54 to 57).
- **Fix.** "The phases that must be merged into the orchestrator branch before it starts, or that must be Done, with every pull request merged into the default branch, or none. Say which for each."

### S2. Which launcher line to report. Cosmetic.

- **Where.** `handbooks/spec-writer.md` line 37.
- **Wrong.** "Report the launcher's output line" does not say which. Recorded at `spec-planner-handbooks-evidence.md` line 232.
- **Fix.** "Report the launcher's `started` or `alive` line, with its pane, to the developer".

## orchestrator-handbook: `orchestrator.md`

### O1. The developer-commit check records live heads. Common path.

- **Where.** `handbooks/orchestrator.md` line 148 (and line 56).
- **Wrong.** "When a `prs-open` arrives, record each of its pull requests' head." A developer commit made between the PR creator's push and the message's arrival becomes the baseline and is never compared. Known item 15. Known item 13 (the cherry-pick line) no longer holds: line 148 now compares heads only.
- **Conflicts with.** Run-decision row 15 and F6.
- **Fix.** Line 148, second sentence: "When a `prs-open` arrives, record for each of its pull requests the last head its `pushed` line names." Line 56: "its head in the `pushed` line of the phase's last `prs-open`".

### O2. Gate-cost: the post-merge check is full and there is no end-of-feature run. Common path.

- **Where.** `handbooks/orchestrator.md` lines 75, 95 and 185.
- **Wrong.** Line 95 runs "the feature's verification skill" in full on every merge. Line 185 ends the feature with no full run.
- **Conflicts with.** Gate-cost rules 8 and 9 (lines 130 to 137) and line 160.
- **Fix.**
  - Line 95: "4. Have a fresh subagent work out the blast radius of the merge's first-parent diff, as `verifier.md` defines it, and run the checks in it on the orchestrator branch. A merge that changes only `.foundry/`, or only generated paths and lines, needs no check. No waiver applies. Record the result, or that none was needed, in the tracker."
  - After step 6 (line 97) add: "When this merge was the last phase of the feature plan to merge, have a fresh subagent run the whole verification skill on the orchestrator branch. Handle a failure as in step 5, sending `move-back` to Implement to the phase that owns the failing paths."
  - Line 75: "When a phase merged and passed its post-merge check, or needed none, or a roadmap update merged, ...".
  - Line 185, first sentence: "When every phase is Done and the full run after the last merge has passed, have a fresh subagent ...".

### O3. "Open pull request" against the board's "draft or open". Minor.

- **Where.** `handbooks/orchestrator.md` lines 115 to 117.
- **Wrong.** "An open pull request is up to date when ...". The board says "a draft or open pull request" (`assets/status-board.html` lines 91 and 93). Every phase pull request is a draft. Known items 10 and 12. Item 10 otherwise holds: the two definitions agree in every other clause.
- **Fix.** Line 115, first sentence: "An open pull request, draft or not, is up to date when, after `git fetch origin`, its head contains ...". No change to the board.

### O4. No handler for a phase's `blocked` or `instruction`. Minor.

- **Where.** `handbooks/orchestrator.md` line 158 and the Supervision section.
- **Wrong.** `blocked` is read only for permission prompts. A phase that cannot merge the orchestrator branch because of a conflict in another phase's file (`phase-session.md` line 56) "waits" for nothing that can come. An `instruction` from a phase (`phase-session.md` line 129) has no handler.
- **Conflicts with.** Reference lines 84 and 86.
- **Fix.** Add to Decisions (line 154): "A `blocked` that names a conflict in another phase's file goes to the developer as a decision request, with the owning phase and the paths. When a phase reports an `instruction`, record it in `run-decisions.md` if it changes a recorded decision, and restart the planner if it changes the plan."

### O5. A decision that changes the plan never restarts the planner. Minor.

- **Where.** `handbooks/orchestrator.md` line 154.
- **Wrong.** Line 154 only sends `answer`. The planner is restarted only for a roadmap update (line 177).
- **Conflicts with.** `planner.md` line 61, "a roadmap update or a discovery changes the phases", `planner.md` line 33 (a contract change is a decision request), and `phase-session.md` line 129 ("only the planner changes the plan").
- **Fix.** Add to line 154: "When the answer changes the feature plan or a contract, restart the planner with an `instruction` that names the decision and the phases it affects. Handle its `done-planning` as Starting the feature step 5 says."

### O6. The stall close and the step 7 `stop` have no quiet test. Minor.

- **Where.** `handbooks/orchestrator.md` lines 14 and 98.
- **Wrong.** Line 14 closes a stalled session "in the next tick" after `stop`. Line 98 sends `stop` with no quiet test.
- **Conflicts with.** Line 125, which closes only once "quiet", and line 126, which sends `stop` only when "it is quiet". Recorded at `orchestrator-handbook-evidence.md` lines 404, 514 and 518.
- **Fix.** Line 14: "gets `stop`, then, once it is quiet in a later tick, `--close` and a launch with `--fresh`". Line 98: "... and it is quiet, send the merged phase `stop`."

### O7. "Return to PR" assumes the phase left PR. Minor.

- **Where.** `handbooks/orchestrator.md` line 13.
- **Wrong.** "answered only by a `prs-open` that follows the phase's return to PR after you sent the round". In a conflict round where the phase already holds the commit, it never leaves PR (`phase-session.md` line 113).
- **Fix.** "... answered only by a `prs-open` sent after the round while the phase is in PR."

### O8. Parallel package versions after a merge have no home. Minor.

- **Where.** `handbooks/orchestrator.md`, "Histories handled by asking" (lines 134 to 142).
- **Wrong.** Prevention landed in `pr-creator.md` line 56. The recovery in run-decision row 10 (two merged pull requests ship one version, and the phase that merged second opens a generated-only pull request) is in no handbook. `pr.sh` cannot build it, because `prove` ignores generated lines (`pr-commands.md` line 93). Known item 17.
- **Fix.** Add a bullet: "a default branch whose checks fail only on generated content after two of the feature's pull requests merged". The developer then decides the fix.

### O9. Board fields that only the template defines. Cosmetic.

- **Where.** `handbooks/orchestrator.md` lines 82, 83 and 162.
- **Wrong.** "scheduling" (line 82) is defined only in the board template (line 43). Line 83 lists no trigger for a new pull request's first `prs/<number>` document. Line 162 says every value comes from a status file, but a phase that has not started has none.
- **Fix.** Line 83: "One `prs/<number>` for each new pull request, and for each whose ...". Line 162, add: "A phase with no status file yet is in Spec, with `scheduling` `queued`, or `blocked` while a dependency is unmet. The template defines `scheduling`."

### O10. A failing default-branch merge is retried every tick. Minor.

- **Where.** `handbooks/orchestrator.md` lines 107 and 108.
- **Wrong.** It tells the developer and aborts, and tick step 2 tries again next tick. Recorded at `orchestrator-handbook-evidence.md` line 252.
- **Fix.** Add to both lines: "Record the tip in the tracker, and do not merge it again until the developer answers or the default branch moves."

## pr-handbook: `pr-creator.md`, `references/pr-commands.md`

### R1. Gate-cost: "Check the gates" refuses `WAIVED`. Common path.

- **Where.** `handbooks/pr-creator.md` line 11.
- **Wrong.** "The status file's newest `verify` verdict must be `VERIFIED` and its newest `review` verdict `CLEAR`". A second copy of the merge rule.
- **Conflicts with.** Gate-cost rule 6 and line 161; F2.
- **Fix.** "**Check the gates.** The merge rule in [references/status-and-messages.md](../references/status-and-messages.md) must hold for the current code head. If it does not, stop and report which verdict fails."

### R2. The proof does not say which orchestrator branch. Minor.

- **Where.** `handbooks/pr-creator.md` lines 28 and 146; `references/pr-commands.md` line 7.
- **Wrong.** `<orchestrator branch>` could be read as `origin/<orchestrator branch>`. The developer pushes that rarely, so the proof gives false merge `FAIL`s. Known item 11.
- **Conflicts with.** `SKILL.md` line 100 (the orchestrator branch is not pushed to a public remote) and `phase-session.md` line 45.
- **Fix.** `pr-creator.md` line 146, after the command: "`<orchestrator branch>` is the local branch, never `origin/<orchestrator branch>`, which may lag or not exist." Same sentence after `pr-commands.md` line 8.

### R3. Raising a version above open pull requests has no method. Minor.

- **Where.** `handbooks/pr-creator.md` line 56.
- **Wrong.** The version "must also be above every version of that package in an open pull request". The regenerate command compares only with the default branch (run-decision row 11), so it cannot do this alone.
- **Fix.** Add: "When the command picks a version that an open pull request already ships, set the `version:` line one patch above the highest, run the command again so the lockfile follows, and keep both in the one regenerate commit."

## board: `assets/status-board.html`

No change. Known item 10: the `needs_update` rule (lines 91 to 97) matches `orchestrator.md` lines 115 to 116 in every clause but "draft or open", which O3 fixes on the orchestrator side.

## Known items: status at the current text

| `integration-items.md` line | Still holds? | Fix |
| --- | --- | --- |
| 5, merged notice before `prs-open` | No. `orchestrator.md` line 127 needs "you have merged its current code head", and line 88 merges a new code head only after a `prs-open` at it. | None |
| 6, `fix-round` rows | Yes | F7 |
| 7, "fact already committed" | Yes | F9 |
| 8, developer commits on `fix-round` | Superseded by run-decision row 15 | F7, P3 |
| 9, "repository root" | Yes | F10 |
| 10, board and orchestrator `needs_update` | Match, apart from item 12 | O3 |
| 11, local orchestrator branch | Yes | R2, P2 |
| 12, draft or open | Yes | O3 |
| 13, cherry-pick line for line 148 | No. Line 148 compares heads only. | None |
| 14, `PUSHED` from status | Yes | F5, P2 |
| 15, pushed heads in `prs-open` | Yes | F6, O1 |
| 16, refresh instruction row | Yes | F7, P3 |
| 17, parallel package versions | Prevention landed (`pr-creator.md` line 56). Recovery has no home. | R3, O8 |

Evidence-file items already closed at the current text: phase-session's "A pull request merged" handler (line 111); a fix after every pull request merged (`phase-session.md` line 85); `stop` answering a round (`orchestrator.md` line 13); generated lines in the code head (`phase-session.md` line 26); `restack` and the failed-check `move-back` in the reference (lines 101 and 102); the `.foundry/` merge exception (`SKILL.md` line 75); `SKILL.md` lines 16 and 24; the rebased stack child (run-decision row 21, `pr-creator.md` line 74); check 8's `## Evidence` wording (`verify-s-stack/SKILL.md` line 160).

## Roadmap files for the spec writer

- `workflow.md` line 77 (States rule 5): the code head as in F1, scoped Verify, `WAIVED` in the verdict list. Line 78 (rule 6): the merge rule as in F2. Line 118 (Branches step 6): the scoped post-merge check and the full run at the end. Line 164 (Fix rounds step 2): "for the new code head, each gate scoped to what changed".
- `decisions.md` D9 (lines 76 to 84): the decision and cost lines for the scoped check. Add a decision for gate-cost, with F1's choice of a code head that ignores clean merges of the orchestrator branch.
- `roles.md` Verifier (lines 96 to 107): scoping and waiving. Reviewer (lines 109 to 117): the first reviewer's waiver.
- `coordination.md` line 104 (tick step 3): the scoped check and `WAIVED`. Its message tables (lines 45 to 67) still list `restack` and one `fix-round` row, and `prs-open` without heads. Align them with F6 and F7.
- `README.md` line 71 ("No skipped gate"): name `WAIVED`, and F3's rule that a waiver does not follow a failed verdict of the same gate.
- `run-decisions.md`: the orchestrator folds `launcher-r3` (row 51) into gate-cost rule 7 and retires it, as row 66 already says. Fold row 67 into P15's wording.

The feature plan's contracts C2 and C3 (`.foundry/plans/2026-11-20_21-37-12-s-stack/README.md` lines 213 to 278) are the planner's. They are superseded by the reference file, as C2 says at line 215, so they need no change.
