# Analysis Process

## Step 1: Gather PR inventory

Fetch all open, non-draft PRs for the target author:

```bash
AUTHOR="${ARGUMENTS:-@me}"
gh pr list --author "$AUTHOR" --state open --json number,title,headRefName,baseRefName,createdAt,url,isDraft,labels \
  --jq '[.[] | select(.isDraft == false)]'
```

If no PRs are found, report that and stop.

## Step 2: Collect changed files per PR

Run `gh pr diff <NUMBER> --name-only` for all PRs as parallel bash calls (one per PR). Do NOT use subagents for this — parallel bash calls are faster.

If a PR diff is too large (HTTP 406 / "too_large" error), fall back to:

```bash
gh api repos/{owner}/{repo}/pulls/<NUMBER>/files --paginate --jq '.[].filename'
```

Note: the GitHub API caps at ~100 files per PR. For PRs exceeding this, use local git diff:

```bash
git fetch origin <branch> --quiet
git diff --name-only origin/dev...origin/<branch>
```

For PRs with large numbers of data/asset files (images, documents, metadata), filter them out for the overlap analysis and note the count separately:

```bash
git diff --name-only origin/dev...origin/<branch> | grep -v '^path/to/data/' | sort
```

Store the mapping: PR number -> list of changed file paths (code files only for overlap analysis).

## Step 3: Check merge status and staleness

Run these as a single batch of parallel bash calls (not subagents):

**Merge status** for all PRs in one command:
```bash
for pr in <PR1> <PR2> <PR3>; do
  echo "PR #$pr: $(gh pr view $pr --json mergeable --jq '.mergeable')"
done
```

Values: `MERGEABLE`, `CONFLICTING`, `UNKNOWN`. Record any `CONFLICTING` PRs.

**Staleness** for all branches in one command:
```bash
git fetch origin dev --quiet
for branch in <branch1> <branch2> <branch3>; do
  git fetch origin "$branch" --quiet
  ahead=$(git rev-list --count "origin/dev..origin/$branch")
  behind=$(git rev-list --count "origin/$branch..origin/dev")
  echo "=== $branch === Ahead: $ahead | Behind: $behind"
done
```

PRs that are 50+ commits behind dev are at higher risk for hidden conflicts.

## Step 4: Identify file overlaps

Build a matrix of which files are touched by multiple PRs. For each PR pair, list the shared files. Count them but also classify by type (code vs config vs docs vs data).

## Step 5: Identify hot files

Find files touched by 3+ PRs. These are prime candidates for extraction into a dedicated prep PR.

## Step 6: Investigate actual conflicts

This is the most important step. Do NOT assume that file overlap means dependency.

For each PR pair with shared files, use a subagent to investigate the actual diffs. Parallelise across pairs — one subagent per pair.

Each subagent should:

1. For each shared file, run `git diff origin/dev...origin/<branch> -- <file>` on both branches
2. Run `git merge-tree $(git merge-base origin/<branchA> origin/<branchB>) origin/<branchA> origin/<branchB>` to get the definitive merge result
3. Classify each file:
   - **IDENTICAL**: Same diff in both PRs (shared prerequisite work duplicated across branches). Whichever merges first, the second becomes a no-op for this file.
   - **INDEPENDENT**: Changes touch different sections. Git auto-merges cleanly. No dependency.
   - **CONFLICTING**: Same lines/blocks modified differently. Git reports conflict. These PRs cannot merge in parallel without manual resolution.
   - **DEPENDENT**: One PR's changes extend or require the other's (e.g., one is a superset). May auto-merge but has semantic coupling.
4. For CONFLICTING files, briefly describe what each PR does to the file (which sections/functions/blocks each touches)

The output should be a summary table per pair plus the list of CONFLICTING files with descriptions.

## Step 7: Determine true dependency graph

Using the conflict investigation results, build the actual dependency graph:

- Two PRs are **independent** if all their shared files are IDENTICAL or INDEPENDENT
- Two PRs are **dependent** if they have CONFLICTING or DEPENDENT files
- For dependent pairs, determine direction: which should merge first based on which is more foundational, which is a superset, or which has fewer conflicts to resolve

The goal is to maximise the number of PRs that can merge in parallel.
