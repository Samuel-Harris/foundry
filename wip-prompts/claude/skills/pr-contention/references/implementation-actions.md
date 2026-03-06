# Implementation Actions

After the user reviews the recommendations and confirms which ones to proceed with, execute only the approved actions. NEVER execute these without explicit user approval.

Always refer to PRs by number AND title when communicating with the user.

## Action: Stack PRs (retarget base)

```bash
gh pr edit <DEPENDENT_PR> --base <BASE_BRANCH_NAME>
```

After retargeting, verify with:
```bash
gh pr view <DEPENDENT_PR> --json baseRefName --jq '.baseRefName'
```

## Action: Rebase a branch onto dev

```bash
git fetch origin dev
git checkout <BRANCH>
git rebase origin/dev
```

If there are conflicts, report them to the user and stop. Do not force-resolve.

After a successful rebase:
```bash
git push --force-with-lease origin <BRANCH>
```

Always use `--force-with-lease`, never `--force`.

## Action: Combine two PRs

1. Confirm with the user which PR to keep and which to close
2. Cherry-pick or merge the changes from the closing PR into the keeping PR's branch
3. Update the kept PR's description to cover both sets of changes
4. Close the other PR with a comment linking to the kept PR

## Action: Extract a prep PR from shared changes

Use this to decouple two dependent PRs by pulling shared conflicting changes into a base PR that both can build on.

1. Create a new branch from dev
2. Cherry-pick or manually apply only the shared file changes
3. Remove those changes from the source PRs (interactive rebase or fresh commits)
4. Create the prep PR
5. Retarget the source PRs to merge after the prep PR

This is complex — always confirm the exact file list with the user first.

## Action: Split a PR into infra + logic (or code + data)

1. Create a new branch from dev for the extracted portion
2. Cherry-pick only the relevant commits (or manually split)
3. Create a new PR for the extracted portion
4. Rebase the original PR's branch to remove the extracted commits
5. Retarget the original PR if needed

## Action: Add dependency annotations

```bash
gh pr edit <PR_NUMBER> --body "$(gh pr view <PR_NUMBER> --json body --jq '.body')

---
**Merge order**: This PR should merge after #<DEPENDENCY_PR>."
```
