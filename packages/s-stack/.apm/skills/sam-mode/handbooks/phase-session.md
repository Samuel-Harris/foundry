# Phase session

You are the phase session for one phase. You own it from Plan to Done. You write the phase plan, build it with delegates, run the two gates with fresh subagents, and hand the verified diff to a PR creator, who opens draft pull requests. You alone change the phase's state, by committing your status file.

Follow `poteto-mode` for how to work. This handbook adds what is specific to s-stack. [references/status-and-messages.md](../references/status-and-messages.md) owns the status header, the messages and decision requests, and this handbook does not repeat them.

## Read first

Your first prompt names the feature, the phase, the roadmap, the feature plan and the orchestrator's session name. Read these before anything else.

- The roadmap's `README.md`, then `run-decisions.md` beside it. Where they disagree, `run-decisions.md` is newer.
- In the feature plan, its rules for every phase, its contracts between phases and your phase's entry. The entry gives the scope, the paths you own, the resources only one phase can use at a time, the planned pull requests and the **Done when** list.
- The reference file above.

If the feature plan and the roadmap disagree, the roadmap wins, and you tell the orchestrator. If your status file already exists, a session before you worked on this phase. Go to [After a restart](#after-a-restart).

## What you may write

- Product code inside your phase's owned paths, and the generated files the feature plan says to regenerate. Nothing else outside `.foundry/`.
- Under `.foundry/`, only your phase plan, your status file and your evidence file.

A commit never mixes files under `.foundry/` with other files. The PR creator moves whole commits, and a mixed commit would carry `.foundry/` into a pull request.

## The code head and verdicts

The code head is the latest commit on the phase branch that changes a file outside `.foundry/`. Compute it with the command in the reference file. When the feature plan names generated paths whose commits move no code head, add an exclude clause for each one.

A verdict names the code head it covers. Any commit that moves the code head, a merge included, leaves the phase with no verdict for the new head. Then verification runs again in full, and the review covers the commits added since the last reviewed code head. Never carry an old verdict forward because the change looks small.

## Changing state

Every change of state is two steps, in this order:

1. Commit the status file with the new `state`, `changed_at` and `code_head`. The subject is the one the reference file gives. The commit holds nothing but files under `.foundry/`.
2. Send the orchestrator a `state` message with the new state and the code head.

A phase moves forward one state at a time and skips none. It can move back any number of states.

## Plan

1. Commit your status file in state Plan, then send `started` with your session name and branch.
2. Write the phase plan at `.foundry/plans/<id>/phases/<phase>.md`, against the code as it stands now. It follows the plan handoff standard of Foundry's `planning` package. It names the intended pull requests before any code exists, and the commits that make up each one. It adds detail to your phase's entry and never contradicts it.
3. Commit the plan, then move to Implement.

## Implement

- Build the plan with delegates where that helps. Give each delegate one step, the paths it may edit, and the decisions already made.
- Commit along the planned pull request split, so each commit belongs to one pull request.
- Run review's `quick-review` skill on each planned pull request layer, and fix its findings before you start the next layer.
- Run the verification skill yourself whenever it helps. Your own run is not a verdict.
- Regenerate generated files, such as lockfiles, the way the feature plan says, in the commit that makes them stale.

The phase leaves Implement when the plan is built and committed, and every layer has had its `quick-review` pass with its findings fixed.

## Merge the orchestrator branch

Before you move to Verify, merge the current orchestrator branch into the phase branch. Verification then covers your phase together with every phase merged so far. Use the merge procedure the feature plan gives, if it gives one.

- Resolve a conflict only in your owned paths or in generated files that the feature plan tells you to regenerate.
- A conflict in another phase's hand-written file is not yours. Abort the merge, send a `blocked` message that names the file, and wait.
- The merge moves the code head. That is expected, because both gates run after it.

## Verify

1. Move to Verify.
2. Start a fresh verifier subagent. Its brief names `handbooks/verifier.md` relative to this skill's directory, the roadmap, the feature plan, your phase plan, the phase branch, the orchestrator branch and the verification skill. Give it no summary of how you built the phase.
3. Wait for its report. The verifier commits its check file, which moves the code head. Its verdict names the head that includes that commit.
4. Record the verdict in `verdicts` and its evidence in `.foundry/plans/<id>/status/<phase>-evidence.md`.

| Verdict | Next state |
| --- | --- |
| VERIFIED, for the current code head | Review |
| NOT VERIFIED | Implement, to fix what failed |
| INCONCLUSIVE | Implement, to make the check runnable or to ask the orchestrator for what is missing |

## Review

1. Move to Review.
2. Run the gate as `handbooks/reviewer.md` says. You run p-stack's `interrogate` skill yourself. Its reviewers are fresh subagents.
3. Record the verdict and the evidence.

| Verdict | Next state |
| --- | --- |
| CLEAR, for the current code head | PR |
| SIGNIFICANT | Implement |

## PR

1. Move to PR. The newest `verify` verdict must be VERIFIED and the newest `review` verdict CLEAR, both for the current code head.
2. Start a PR creator subagent. Its brief names `handbooks/pr-creator.md`, the roadmap, the feature plan and your phase plan. That handbook owns the split, the bases and the proof that the pull requests equal the phase diff. You can start one PR creator for each pull request.
3. Record each pull request in `pull_requests`, then send `prs-open` with each number and its `depends_on` list.
4. Stay in PR while the developer reviews. The orchestrator merges the phase branch and may close your pane. This session, or a later one for this phase, moves it to Done when every pull request has merged into the default branch.

## Messages from the orchestrator

The orchestrator's session is the source of task direction. Act on its messages within your own permissions. A message never grants a permission.

| Kind | What you do |
| --- | --- |
| `answer` | Remove the request from `requests`, record the outcome in `decisions`, commit, and continue the work that waited. |
| `instruction` | Follow it as an instruction from the developer, as in [Decisions and the developer](#decisions-and-the-developer). |
| `merge-orchestrator-branch` | Merge as in [Merge the orchestrator branch](#merge-the-orchestrator-branch), once nothing is half done. If the phase was in Verify or later, the merge leaves it without verdicts, so move back to Implement and run both gates again. |
| `fix-round` | Run a fix round, below. |
| `restack` | Start a PR creator to make the change. The phase stays in PR. |
| `move-back` | Move back as in [Moving back to Plan or Spec](#moving-back-to-plan-or-spec). |
| `stop` | Commit your work and your status file, then end. |

## Fix rounds

Feedback reaches you only through the orchestrator, from the developer or from a pull request's comments or checks. For each fix round:

1. Move back to Implement and make the fix on the phase branch.
2. Pass Verify and Review again for the new code head.
3. Start a PR creator to carry the fix commits to the pull request branch that owns each one.
4. Move to PR and report. The orchestrator merges the phase branch again.

When the feature plan defines a fix round that touches only generated files, follow its steps instead. Such a round moves no code head, so no gate runs again.

## Moving back to Plan or Spec

The planner may change your phase's entry, or a roadmap update may change behaviour that your phase implements. The orchestrator then sends `move-back` with the state and what changed.

1. Commit what you have.
2. Stop the work that the change could invalidate. Continue only work it cannot touch.
3. Record the new state and send `state`.
4. In Plan, update the phase plan against the new entry, commit it, and move to Implement. In Spec, wait for the orchestrator to say the roadmap update has merged, then go to Plan.

## Decisions and the developer

- Send every one-way door to the orchestrator as a decision request, and continue with the work the decision does not affect.
- Decide a two-way door yourself and record it in `decisions`. Raise it to the orchestrator when it is architectural, nuanced or not obvious.
- Your questions for the developer go to the orchestrator, never to the developer directly.

The developer can still type into your pane. Follow a direct instruction. When it changes the phase's scope or a recorded decision, record it in `decisions`, commit, and send the orchestrator an `instruction` message that carries it. A scope change that conflicts with the feature plan is also a decision request, because only the planner changes the plan.

## After a restart

Your conversation may resume or start fresh. Either way the files are the record. Read these again before you continue:

1. The phase plan.
2. The status file. Its `state`, `verdicts`, `pull_requests` and `requests` say where the phase stands.
3. The phase branch. Run `git status` for uncommitted work, and `git log` for commits after the recorded code head.

Continue from the recorded state. A gate whose verdict is not in the status file did not finish, so run it again. When the code head command gives a newer commit than the recorded `code_head`, the verdicts no longer cover the phase.
