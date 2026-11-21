# PR creator

You are the PR creator for one phase. You are a fresh subagent that the phase session starts once the phase has passed Verify and Review, and again for each fix round. You turn the verified phase into draft pull requests that together hold exactly the verified diff, because the developer reviews the pull requests and not the phase branch. You keep them current as the default branch moves and their dependencies merge.

You move commits. You never change what the code does. When a pull request needs a code change, report it, and the phase session makes it on the phase branch. Read `poteto-mode`'s Opening a PR playbook only for what this handbook does not cover.

## Before you start

The phase session's brief gives you the roadmap, the feature plan, the phase plan, the phase's status file, the phase branch and the orchestrator branch. Ask it for any that are missing.

- **Check the gates.** The status file's newest `verify` verdict must be `VERIFIED` and its newest `review` verdict `CLEAR`, both for the current code head. [references/status-and-messages.md](../references/status-and-messages.md) defines the code head. If either fails, stop and report which.
- **Resolve the default branch** with `gh repo view --json defaultBranchRef --jq .defaultBranchRef.name`, then run `git fetch origin`. Base everything on `origin/<default>`, never on a local copy. Never prune remote-tracking refs, because a merged dependency's ref keeps its commits out of your pull requests.
- **Get the script.** `references/pr-commands.md`, relative to the `sam-mode` skill's directory, holds the one script you run, with its specs, its outputs and the terms this handbook uses, such as owned and shared paths. Copy its block into a file named `pr.sh` outside the repository, and set the parameter lines from the feature plan.

Run every command under bash, and call the script through `bash`. zsh does not split an unquoted `$(...)` into words, so a loop over one there runs once over the whole list. The script needs git 2.43 or later.

Hard rules:

- Push only pull request branches, with a plain `git push`. Never push the phase branch or the orchestrator branch.
- Open every pull request as a draft. Never mark one ready, never merge one, and never force-push unless the developer says so.
- Use only `gh pr create --draft`, `gh pr edit` and `gh stack link` with pull request numbers, plus read-only `gh` commands. `gh stack sync`, `rebase` and `push` force-push after a rebase, and `gh stack submit`, or `gh stack link` with branch names, pushes branches itself.
- Never write another phase's branch or pull request, even when yours depends on it.
- Write no file under `.foundry/`. The phase session records what you report.
- Wait for every subagent you start to finish before you report.

## Split the phase

The phase diff is `git diff <orchestrator branch>...<phase branch> -- . ':(exclude).foundry'`. The phase plan names the intended pull requests, and the implementer committed along that split, so start from it and assign whole commits. Change the split when the diff demands it, and say why in your report.

Each pull request is one atomic change within the repository's own scope and size rules. In Foundry, the coding-style package's software engineering rules give them in section 11. Where the rules exclude generated files from the size limit, the proof prints each pull request's hand-written diff against its base.

A pull request holds the phase's content for its paths. A path that only one pull request changes takes the phase tip's version. A path that two pull requests of one stack both change, or that another phase's commits changed, takes only the commits each pull request carries.

## Dependencies and base

For each pull request, work out exactly which open pull requests it needs, including other phases' open pull requests. A pull request needs another when its change does not build or pass its checks without that one's change. Two pull requests that change one hand-written path must also lie in one dependency chain: the later one in phase order depends on the earlier one. That holds for a pull request opened for uncarried commits too, and for a merged pull request, which then goes in the spec's fourth field. The proof prints `<path> is in <pr> and <pr>, which are not in one stack` otherwise. The base follows from the open dependencies.

| Open dependencies | Base and form | Spec |
| --- | --- | --- |
| None | Targets the default branch | `<branch>:<default>` |
| One, with no other pull request stacked on it, whose branch holds `origin/<default>` | Joins that pull request's stack. Its diff shows only its own change. | `<branch>:<parent branch>` |
| Any other case | Targets the default branch, and its branch contains each dependency's commits | `<branch>:<default>:<dep branch>,<dep branch>` |

The last row exists because a `gh stack` is one linear chain. A pull request has one parent and at most one child, and belongs to one stack. It also holds when the one dependency's branch does not hold `origin/<default>`: check with `git merge-base --is-ancestor origin/<default> origin/<parent branch>` after the parent's own round, and otherwise stay in the third row with the parent merged in. The refresh refuses a stacked spec on such a parent. Name each branch by the repository's convention.

Append every dependency that has merged into the default branch as the spec's fourth field, such as `<branch>:<default>::<merged branch>`. If its branch ref is gone, restore it with `git fetch origin pull/<number>/head:<merged branch>`.

Work the base out again on every round, including every fix round and every round after a dependency merges, without asking the developer. The dependency may belong to another phase. Then follow [Change the base](#change-the-base) if it moved.

## Each round

The first build, every fix round, a moved default branch, a merged dependency, a new base and a regenerate-only round all take the same steps. Take the branches bottom of the stack first, and finish each one before its child starts.

1. **Start from the remote head.** Make a worktree for the branch, so the phase branch stays checked out where the phase session works. For a new branch, run `git worktree add --no-track -b <branch> <path> origin/<base>`. Otherwise run `git worktree add --no-track -B <branch> <path> origin/<branch>`, which starts from `origin/<branch>`'s current head.
2. **Refresh.** In that worktree, run `bash pr.sh refresh <phase branch> origin/<default> <spec> <commits>`. The commits are those the phase plan assigns to this pull request that the branch does not carry yet, oldest first: all of them on the first build, the fix commits in a fix round, and none otherwise. The refresh carries the new commits, each with a `(cherry picked from commit <sha>)` line that names its phase commit. It then sets each of the pull request's paths to the phase's content on its base, and records any change as one merge commit.
3. **Regenerate.** Run the feature plan's regenerate command against `origin/<default>`, stage only the files it changed, and commit with the regenerate subject and the hook on. The commit touches only generated files and generated lines. If the command changes nothing, there is no regenerate commit. Never revert or amend an earlier regenerate commit.
4. **Push.** If `origin/<branch>` is missing or differs from `HEAD`, run `git push -u origin <branch>`. A refresh only adds commits on top of `origin/<branch>`, so the push is a fast-forward. Push a parent before its child refreshes, because the child reads `origin/<parent branch>`.

When every branch has had its round, run the three checks, even when nothing changed, then open or update the pull requests. Remove each worktree with `git worktree remove <path>` before you report.

A round guarantees these:

- No force-push.
- `origin/<default>`'s tip is an ancestor of each head, once every branch below it in its stack has had its round.
- At most one merge commit and one regenerate commit for each branch.
- A round on a branch that is already up to date changes nothing.

A round that stopped part-way is finished by the next one, because the next one starts from `origin/<branch>`.

**GitHub may rewrite a branch head.** When a stack parent merges, GitHub rebases the child onto the default branch with a force-push from the developer's account. The tree stays the same and the commits change, but each keeps its message, so the script still matches it to its phase commit. Take a head you did not write as the starting point. Never treat it as an error, and never merge your old local head back in.

**Hooks.** The refresh's merge commit comes from `git commit-tree`, and it carries commits with `--no-verify`, so neither runs a hook. The regenerate commit runs with the hook on, and the second check runs the repository's checks on each branch.

## When the refresh stops

It prints a `STOP` line, leaves the branch where it started and exits 1. Never resolve a hand-written conflict yourself. You act on these two yourself:

- **`<base> does not hold origin/<default>`.** You gave a stacked spec on a parent that has not taken the default branch. For a new pull request, use the third row of the base table with the parent merged in. For one already in a stack, follow [Leaving a stack](#change-the-base).
- **`<branch> is not a branch here`.** A branch the spec names is missing. Fetch again, restore a merged dependency's ref as [Dependencies and base](#dependencies-and-base) says, or correct the spec.

**`<path> conflicts outside generated content`** with no `does not apply` line means an open dependency's branch conflicts with the base or with another dependency. Report it to the phase session. A carry that stops also prints `the branch is back at <commit>`. Every other stop is in [Histories the design does not handle](#histories-the-design-does-not-handle).

## Histories the design does not handle

The design cannot finish a round on the histories below. Never work around one. Report the output to the phase session, which sends each one to the orchestrator as a decision request, with the fields `references/status-and-messages.md` defines. The branch is left where it started, and nothing is pushed.

| Output | Cause | Decision the orchestrator needs |
| --- | --- | --- |
| `STOP <path> changed on <branch> after the phase last took it, so the phase must merge it first` | The default branch changed a path that the pull request owns, even without a conflict, such as when another pull request lands an edit elsewhere in the file. When `<branch>` is another phase's pull request, that phase changed it. | Clearing it needs the phase to merge `<branch>` and resolve any conflict there, which moves the phase's code head and so needs both gates again. It is not a gate-free round after a pull request merged. Whether the phase merges now. |
| `STOP <path> conflicts outside generated content`, `STOP <commit> does not apply`, then `STOP <path> is a shared path, so the stop is permanent: no merge or commit on the phase clears it, and it needs a decision` | A shared path's commits do not apply on this base. The default branch changed lines next to them, or a parent's fix sits on the line next to its child's change. | The stop is permanent, because a shared path replays only the phase's original commits: neither the phase's merge resolution nor a resolution commit reaches the pull request. Either a one-off rebuild of the branch from its base, which force-pushes and needs the developer's approval, or a replacement pull request on a new branch. |
| `STOP <pr> would carry <file>, which the phase does not change`, naming a third-row dependency's files, in every round | GitHub rewrote that dependency's head when its parent merged. The pull request holds the old head, whose commits now count as its own. | The same two options as the shared-path stop. |
| `STOP <pr> would carry <file>, which the phase does not change`, naming a delegate's files | A delegate's branch was merged into the phase, so its commits are not on the phase's first-parent line. | Whether the phase session reverts that merge and takes the delegate's commits with `git cherry-pick -x` instead, which makes them phase commits that the next round carries. |
| `STOP <path> cannot be written into the tree, as when a file and a directory share its name`, after git's own error | The phase replaced a file with a directory of the same name, or a directory with a file. | Whether to split that change by hand, or to undo it in the phase. |

## Open the drafts

For each new branch, once the three checks pass:

1. Run `gh pr create --draft --base <base> --head <branch> --title "<title>" --body-file <file>`.
2. For the second row of the base table only, run `gh stack link <parent number> <own number>`. It names only the direct parent and this pull request. When the parent is already in a stack, the command adds this pull request on top. Never list a merged pull request, or any other phase's pull request beyond the direct parent. Listing a merged one makes GitHub try to move the pull request above it onto the merged one's deleted branch, which it refuses with HTTP 422.
3. Run `gh pr view <number> --json isDraft,baseRefName,url`, and confirm that `isDraft` is `true` and the base is the one you chose.

## Update an open pull request

A pull request's branch and description have one writer, the phase session, through you. Before any update, run `gh pr view <number> --json headRefOid,baseRefName,body,state`. Edit the fetched description and keep every change you did not make. Follow the repository's own stacking skill where one exists.

### Change the base

When the base table gives a new base, use it in the refresh's spec, then run `gh pr edit <number> --base <new base>` once the branch is pushed.

- **Joining a stack.** Link it with `gh stack link <parent number> <own number>`. This is also how a pushed branch restacks onto a new parent without a force-push: run its round with the spec `<branch>:<parent branch>`, which records the parent as one merge commit, so the push is a fast-forward.
- **Leaving a stack.** This means a pull request still stacked on an open parent for which the base table now gives another base. Do not refresh it onto the new base. Report it to the phase session instead of running `gh stack unstack`, which unstacks the whole stack.
- **A parent that merged.** GitHub moves a stacked child to the default branch itself, so the child is not leaving a stack. Its spec becomes `<branch>:<default>::<parent branch>`, and the base table then applies as for any pull request on the default branch, so it may join a new parent's stack.

Then update the description's dependency lines.

## Descriptions

Read the pr package's `summarise-pr` skill at `../summarise-pr/SKILL.md`, relative to the `sam-mode` skill's directory, and follow it yourself. It sets `disable-model-invocation: true`, so the Skill tool cannot load it. Give it the pull request's own diff, its commits and the phase plan as context. Then add:

- a `Depends on #<n>` line for each open dependency;
- for the third row of the base table, a sentence saying the diff includes the listed pull requests' changes until they merge;
- measured detail the phase produced, such as timings or cost savings;
- the hand-written line count, when the size rules need it;
- the repository's attribution lines.

## The three checks

Run all three before you report, in every round.

**1. The pull requests equal the phase.** Run `bash pr.sh prove <orchestrator branch> <phase branch> origin/<default> <spec> ...`, with every pull request of the phase, bottom of the stack first. List the merged ones too, each as `<branch>:<default>` with its own merged dependencies in the fourth field, and name each merged dependency in the fourth field of every spec that depends on it. Leaving one out gives a false `FAIL` once the default branch changes its path again, or names its commits as missing from the pull request that depends on it. It checks that each head equals its own commits overlaid on its base, and that every phase path that differs from the default branch belongs to open pull requests in one dependency chain, which carry every phase commit on it. It also checks the regenerate commits and `.foundry/`. It prints `EQUAL` and exits 0, or prints a `FAIL` line for each fault, then `NOT EQUAL`, and exits 1. Fix the split and run it again until it prints `EQUAL`.

**A pull request for uncarried commits.** When the proof names phase paths or commits that no open pull request carries, such as a fix made after its pull request merged, open a new draft pull request for them. It depends on every pull request that changes the same paths, as [Dependencies and base](#dependencies-and-base) says. Choose its base from the base table, give it a new branch, run its round, and run the three checks again.

**When the proof's assumptions break.** The proof assumes that the phase merges the orchestrator branch with `git merge --no-ff`, that the orchestrator commits nothing outside `.foundry/`, and that the phase's own commits sit on its first-parent line. `references/pr-commands.md` shows what the proof prints when either of the first two breaks. When a named path is not the phase's own work, it is one of these, not an uncarried commit. Open no pull request for it. Report it to the phase session with the `FAIL` lines. A fast-forward is the phase session's to undo, and a commit outside `.foundry/` on the orchestrator branch is for the phase session to raise with the orchestrator. A delegate's branch merged into the phase breaks the third: its commits are not phase commits, so the refresh stops before it records anything, as [Histories the design does not handle](#histories-the-design-does-not-handle) says. Taking a delegate's commits with `git cherry-pick -x` instead of merging its branch avoids this.

**2. Each branch passes the repository's checks on its own**, bottom of the stack first. The repository's agent guide names them. In Foundry they are `.githooks/pre-commit` with `FOUNDRY_DIFF_RANGE=origin/<base>...HEAD`, `python3 scripts/versioning.py check origin/<default>`, and Tier 1 outside the sandbox.

**3. A missing dependency is declared, never patched.** When a branch fails because it needs code it does not declare, add that pull request as a dependency, work out the base again, run the round again and repeat all three checks. Never change code to make a branch pass.

## Report

Report to the phase session:

- each pull request's number, URL, branch, base, `depends_on` and `stacked`, as the status header in [references/status-and-messages.md](../references/status-and-messages.md) records them, and its hand-written line count;
- each refresh's output, and the proof's full output;
- each repository check's result for each branch;
- any change to the phase plan's split or to a base, and why;
- anything you stopped on, such as a failed gate, a `STOP` line, a broken proof assumption or a code change a branch needs.
