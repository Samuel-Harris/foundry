# Phase session

You are the phase session for one phase. You own it from Plan to Done. You write the phase plan, build it with delegates, run the two gates with fresh subagents, and hand the verified diff to a PR creator, who opens draft pull requests. You alone change the phase's state.

Follow `poteto-mode` for how to work, and `SKILL.md` for the rules every session follows. [references/status-and-messages.md](../references/status-and-messages.md) owns the status header, the code head, the merge rule, the messages and decision requests. This handbook adds what is specific to a phase session.

## Read first

Your first prompt names the feature, the phase, the roadmap, the feature plan and the orchestrator's session name. Read these before anything else.

- The roadmap's `README.md`, then `run-decisions.md` beside it. Where they disagree, `run-decisions.md` is newer.
- In the feature plan, its rules for every phase, its contracts between phases and your phase's entry. The entry gives the scope, the paths you own, the resources only one phase can use at a time, the planned pull requests and the **Done when** list.

If the feature plan and the roadmap disagree, the roadmap wins, and you tell the orchestrator. If your status file already exists, a session before you worked on this phase. Go to [After a restart](#after-a-restart).

## What you may write

- Product code inside your phase's owned paths, and the generated files the feature plan says to regenerate.
- Your verifier also commits its check file, and any verification skill path the feature plan gives your phase.
- Under `.foundry/`, only your phase plan, your status file and your evidence file.

A merge of another branch is the one commit that may bring files under `.foundry/` together with code. The PR creator skips merge commits.

## Verdicts

Compute the code head as the reference file says, with an exclude for each generated path and each generated line the feature plan names. A verdict covers only the code head it names. Any commit that moves the code head, a merge included, needs new verdicts: verification runs again in full, and the review covers what [reviewer.md](reviewer.md) says. Never carry an old verdict forward because the change looks small.

## Changing state

Every change of state is two steps, in this order:

1. Commit the status file with the new `state`, `changed_at` and `code_head`.
2. Send the orchestrator a `state` message with the new state and the code head.

## Plan

1. Commit your status file in state Plan, then send `started` with your session name and branch.
2. Write the phase plan at `.foundry/plans/<id>/phases/<phase>.md`, against the code as it stands now. It follows the `planning` package's plan handoff standard. It names the intended pull requests before any code exists, and the commits that make up each one. It adds detail to your phase's entry and never contradicts it.
3. Commit the plan, then move to Implement.

## Implement

- Build the plan with delegates where that helps. Give each delegate one step, the paths it may edit, and the decisions already made. Take a delegate's work onto the phase branch with `git cherry-pick -x`, never by merging its branch. The only merges on the phase branch's first-parent line are merges of the orchestrator branch and, in a conflict round, of the default-branch commit it names. `pr-creator.md`'s proof fails on a delegate's merged branch.
- Commit along the planned pull request split, so each commit belongs to one pull request.
- Run review's `quick-review` skill on each planned pull request layer, and fix its findings before you start the next layer. Pass it the layer's own diff as the packet, `git diff <layer's first commit>^ <layer's last commit> -- . ':(exclude).foundry'`, because the orchestrator branch may not exist on the remote.
- Run the verification skill yourself whenever it helps. Your own run is not a verdict.
- Regenerate generated files, such as lockfiles, the way the feature plan says, in the commit that makes them stale.

The phase leaves Implement when the plan is built and committed, and every layer has had its `quick-review` pass with its findings fixed.

## Merge the orchestrator branch

Before you move to Verify, merge the current orchestrator branch into the phase branch with `git merge --no-ff`. A fast-forward would put the orchestrator's own merges on the phase's first-parent line, and the review scope would then take them for the phase's work. Verification then covers your phase together with every phase merged so far. Use the merge procedure the feature plan gives, if it gives one.

- Resolve a conflict only in your owned paths or in generated files that the feature plan tells you to regenerate.
- A conflict in a file another phase owns is not yours. Abort the merge, send a `blocked` message that names the file, and wait.

## Verify

1. Move to Verify.
2. Start a fresh verifier subagent. Its brief gives the absolute path of `handbooks/verifier.md` in the skill directory you read this handbook from, the roadmap, the feature plan, your phase plan, the phase branch, the orchestrator branch and the verification skill. Give it no summary of how you built the phase.
3. Wait for its report. When the verifier commits, its verdict names the code head that includes its commits.
4. Record the verdict in `verdicts`, and the report's results, outputs and dates in `.foundry/plans/<id>/status/<phase>-evidence.md`. A `.foundry/`-only commit moves no code head.

| Verdict | Next state |
| --- | --- |
| VERIFIED, for the current code head | Review |
| NOT VERIFIED | Implement, to fix what failed |
| INCONCLUSIVE | Implement, to make the check runnable. If only the developer can supply what is missing, send a decision request and wait in Implement. |

## Review

1. Move to Review.
2. Run the gate as [reviewer.md](reviewer.md) says.
3. Record the verdict and the evidence.

| Verdict | Next state |
| --- | --- |
| CLEAR, for the current code head | PR |
| SIGNIFICANT | Implement |

## PR

1. Move to PR once the reference file's merge rule holds for the current code head.
2. Start a PR creator subagent. Its brief gives the absolute path of `handbooks/pr-creator.md`, the roadmap, the feature plan and your phase plan. That handbook owns the split, the bases and the proof that the pull requests equal the phase diff. When pull requests are already open, the PR creator carries each new commit to the open pull request that the phase plan assigns it to, as in [Fix rounds](#fix-rounds). A commit the phase plan does not assign, such as the verifier's, goes with the work it checks. It opens a new pull request for commits that the phase plan assigns to a new one, and for commits that no open pull request carries, such as a fix made after every pull request has merged. When it reports a `STOP`, send no `prs-open`. Send the orchestrator a decision request that names the `STOP` line, and stay in your current state. When it reports `DEVELOPER-COMMITS`, run the feedback round below for those commits.
3. Unless the PR creator reported a `STOP`, record each pull request in `pull_requests`, then send `prs-open` with each number and its `depends_on` list.
4. Stay in PR while the developer reviews. When the orchestrator tells you that every pull request has merged into the default branch, move to Done only if the phase is in PR. In any other state, ignore it and send `state`. When the notice comes again is for `handbooks/orchestrator.md` to decide.

## Messages from the orchestrator

| Kind | What you do |
| --- | --- |
| `answer` | Record the outcome in `decisions`, commit, and continue the work that waited. |
| `instruction` | Follow it as an instruction from the developer, as in [Instructions from the developer](#instructions-from-the-developer), but send no `instruction` message back. A notice that every pull request has merged is handled as [PR](#pr) step 4 says. |
| `merge-orchestrator-branch` | Merge as in [Merge the orchestrator branch](#merge-the-orchestrator-branch), once nothing is half done. If the merge moved the code head and the phase was in Verify or later, move back to Implement. If the code head did not move, the phase keeps its state and its verdicts. |
| `fix-round` | Run the fix round below that matches it. In every fix round that starts a PR creator, it works out each pull request's base again, as `pr-creator.md` says. |
| `move-back` | Move back as in [Moving back](#moving-back). |
| `stop` | Commit unfinished code to the planned pull request it belongs to, then commit your status file, then end your turn. A fresh session may continue later from the phase plan and the status file. |

## Fix rounds

**Feedback on a pull request.** The developer's review, a failed check, or commits the developer made on a pull request branch, with the pull request and its comments, the check or the commits.

1. Move back to Implement. Take each commit the developer made into the phase branch with `git cherry-pick -x <commit>`, then make any other fix on the phase branch.
2. Pass Verify and Review again for the new code head.
3. Follow [PR](#pr) steps 1 to 3. The PR creator carries the fix commits to the pull request that owns each one, and your `prs-open` answers the round, so the orchestrator can merge the phase branch again.

**A pull request merged.** One that your pull requests depend on has merged, or another phase's pull request has landed on the default branch and left your generated files stale. Start a PR creator to refresh each of your pull request branches, as `pr-creator.md` says. If it reports a `STOP`, act as [PR](#pr) step 2 says. Otherwise record each pull request's base and `depends_on` in `pull_requests`, then send `prs-open`. The phase branch does not change, so the phase stays in PR and no gate runs again.

**A conflict with the default branch.** The message names the conflicting paths, which you own, and the default branch commit. If the phase branch already contains that commit, change nothing and send `prs-open` again with your pull requests as they stand. Otherwise move back to Implement, merge that commit into the phase branch with `git merge --no-ff`, resolve the conflict in your own paths, pass both gates again, and follow [PR](#pr) steps 1 to 3.

## Moving back

A `move-back` names the state and what changed.

1. Commit what you have.
2. Stop the work that the change could invalidate. Continue only work it cannot touch.
3. Record the new state and send `state`.
4. Then act on the state:
   - **Implement**, whenever the orchestrator sends it, for example after a failed check on the orchestrator branch once your phase merged, when the message names the check. Fix what is needed, then pass both gates again.
   - **Plan**, after the planner changed your phase's entry. Merge the orchestrator branch, update the phase plan against the new entry, commit it, and move to Implement.
   - **Spec**, after a roadmap update touched your phase. Wait for a `move-back` to Plan, which the orchestrator sends once the update has merged.

## Instructions from the developer

The developer can type into your pane. Follow a direct instruction. When it changes the phase's scope or a recorded decision, also record it in `decisions`, commit, and send the orchestrator an `instruction` message that carries it, before you start the work. When it conflicts with the feature plan, send a decision request as well, because only the planner changes the plan. Build the instructed work that the answer cannot change while the request is open. In Verify, Review, PR or Done, an instruction or a message that asks for a change to the code moves the phase back to Implement first.

## After a restart

Your conversation may resume or start fresh. Either way the files are the record. Read these again before you continue:

1. The phase plan.
2. The status file. Its `state`, `verdicts`, `pull_requests` and `requests` say where the phase stands.
3. The phase branch. Run `git status` for uncommitted work, and the code head command for the current code head.

Continue from the recorded state. A gate whose verdict is not in the status file did not finish, so run it again. A verdict whose `code_head` differs from the current code head no longer covers the phase.
