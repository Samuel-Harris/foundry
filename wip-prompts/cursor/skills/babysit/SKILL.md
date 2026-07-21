---
name: babysit
description: >-
  Keep a GitHub pull request merge-ready in a persistent loop by inspecting its
  current head, resolving unambiguous merge conflicts, addressing valid review
  comments, fixing PR-caused CI failures, pushing scoped fixes, and monitoring
  until required checks and review threads are clear. Use when the user asks
  Codex to babysit, watch, shepherd, or keep working on a PR until it is ready
  to merge.
---

# Babysit PR

Get the pull request to a merge-ready state and keep monitoring it until it is
ready or a genuine blocker requires the user.

## Guardrails

- Read the repository's `AGENTS.md` files and obey the instructions that apply
  to every file changed.
- Preserve unrelated work in a dirty worktree. Never discard user changes,
  force-push, rewrite published history, merge the PR, approve reviews, dismiss
  reviews, or weaken branch protections unless the user explicitly requests it.
- Treat the current pull request as the scope boundary. Do not fix unrelated
  failures or change CI workflows merely to obtain a green result.
- Read only the GitHub fields needed for the next decision. Avoid dumping full
  API responses or logs into context; filter unresolved threads and failed job
  output before reading details.
- Keep the user informed during long checks or monitoring. Do not silently wait
  for more than 60 seconds.

## Establish the target

1. Inspect the current branch, worktree, remotes, and its open pull request.
2. Record the PR number, URL, head branch and SHA, base branch and SHA, draft
   state, mergeability, review decision, unresolved review threads, and required
   checks for the current head SHA.
3. Confirm that the checked-out branch is the PR head before editing or pushing.
   If the branch or PR cannot be identified unambiguously, stop and ask for the
   PR URL or number.
4. Treat results for an older head SHA as stale and refresh them.

Prefer the GitHub connector for concise PR metadata when available. Use `gh`
for Actions logs and GraphQL queries when thread-level resolution state or inline
context is required.

## Run the readiness loop

Repeat the following cycle after every push and whenever GitHub state changes.

### 1. Refresh and classify

Fetch the relevant remote refs, then refresh mergeability, review threads, and
required checks for the current head SHA. Classify each problem as:

- an unambiguous merge conflict;
- an actionable, valid review comment;
- a CI failure caused by this PR;
- transient or stale external state that should be refreshed or monitored; or
- a blocker outside the PR's safe scope.

Work on causal problems one at a time so each change can be verified.

### 2. Resolve merge conflicts

Merge the latest base branch into the PR branch without rewriting history.
Resolve conflicts by preserving the intended behavior from both branches, read
the surrounding code and tests before editing, and run focused verification. If
the two intents conflict or the correct behavior is ambiguous, abort only the
merge started by this workflow, preserve the pre-existing worktree, and ask the
user for a decision.

### 3. Address review threads

Inspect active unresolved threads, including automated reviewers such as
Bugbot. For each thread:

1. Read the comment body plus only the minimum file, line, diff, and URL context
   needed to evaluate it.
2. Reproduce or verify the claim from repository evidence. Do not accept bot
   findings automatically.
3. Implement the smallest complete fix when the finding is valid, adding a
   regression test when practical.
4. If the finding is invalid, explain the concrete reason. If it exposes a
   product or architectural ambiguity, ask the user rather than guessing.
5. Resolve a thread only after its fix or explanation is posted and any local
   verification needed for that conclusion has passed.

Do not treat general discussion, praise, already-resolved threads, or outdated
comments as change requests.

### 4. Diagnose CI

Inspect the failed required job and its relevant log excerpt. Reproduce the
failure locally when practical, then fix its root cause if it is attributable to
the PR. Run the narrow failing check first, followed by the repository's broader
required checks in proportion to the change.

For a failure that appears unrelated:

1. Check whether the PR is behind the base branch and whether the base branch
   already contains a fix.
2. Merge the latest base branch when that is the safe, relevant correction.
3. Retry a demonstrably transient failed job at most once before gathering new
   evidence.
4. Report the blocker instead of changing unrelated code or CI policy.

### 5. Publish and monitor

Review the diff and verification evidence. Commit only scoped changes with a
descriptive message and push normally to the PR branch. Never include unrelated
worktree changes. Refresh the PR using its new head SHA, then continue the loop
while checks are pending or new review activity is arriving.

Use bounded polling or the available wait mechanism so the user receives an
update at least once per minute. Do not declare success from cached status or
from a check run attached to an older commit.

## Stop conditions

Declare the PR merge-ready only when all of the following are true for the
current head SHA:

- GitHub reports no merge conflict;
- every required check has completed successfully or with an allowed neutral or
  skipped conclusion;
- there are no unresolved actionable review threads or requested changes; and
- no repository rule still blocks merging.

Report the PR URL and head SHA, changes pushed, checks run, current required-check
status, and review-thread status. Clearly distinguish checks run locally from
checks observed on GitHub.

Stop early only for a genuine blocker: ambiguous conflicting intent, missing
authorization or access, a required product decision, a failure outside the PR's
scope, or a repository rule that cannot be satisfied safely. State the exact
blocker, evidence gathered, and the smallest user action needed. A draft PR or a
missing human approval is external waiting state rather than permission to make
unrelated changes; keep monitoring when the user's request requires persistence.
