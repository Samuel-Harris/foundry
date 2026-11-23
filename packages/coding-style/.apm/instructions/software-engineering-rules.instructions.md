---
description: Core engineering rules for agent-written code — read before writing, think before coding, keep changes surgical, verify with tests, and keep agent context progressively disclosed.
applyTo: "**/*"
---

# Software Engineering Rules

## 1. Read Before You Write

The single biggest source of bad LLM code is not reading the existing codebase before writing new code. You see a task, you pattern-match to something in your training data, and you start generating. This is almost always wrong.

Before writing anything:

- Read the files you're about to modify. Not skim. Read.
- Look at how similar things are done elsewhere in the project. If there's a pattern for API routes, follow that pattern. If there's a utility function that does half of what you need, use it.
- Diff your path against its siblings. When you add a route, query, export, copy flow, permission check or config resource beside existing ones, list every guard, option and setting the closest sibling applies (entitlement and permission checks, normalisation, fallbacks, cache or refetch options, redirect and timeout settings, declared variables) and carry each one over or say why not. When you change one path, search for the paths that do the same job and change them too, or name them as out of scope.
- Before writing a helper, type, loader, retry loop, IAM role or table definition, search the repository for one that already does it (by behaviour, not only by name) and call it. If you still write a new one, say in the PR why the existing one does not fit.
- Check the imports at the top of the file. They tell you what libraries this project actually uses. Don't introduce axios if the project uses fetch everywhere. Don't introduce lodash if the project uses native methods.
- Look at the test files. They tell you what the expected behavior actually is, not what you think it should be.
- Use the repository's own terms and naming conventions. A name says what the value is, in its unit; do not reuse one name for two meanings in a file.

The failure mode here is obvious: you generate "correct" code that's completely alien to the codebase it lives in. It works but it looks like a different person wrote it (because a different entity did). The human then has to either rewrite it to match the project style or live with inconsistency forever. Both are bad.

If you're not sure how something is done in this project, say so. "I don't see a pattern for X in the codebase, should I follow the approach in Y or do something different?" is always better than guessing.

## 2. Think Before You Code

Don't start writing code until you've figured out what you're actually doing. This sounds obvious but it's the most common failure mode.

What this looks like in practice:

**State your assumptions.** If the user says "add authentication" that could mean session cookies, JWTs, OAuth, basic auth, or five other things. Don't pick one silently. Say "I'm assuming you want JWT-based auth with refresh tokens, stored in httpOnly cookies. If you want something different, let me know." If you're wrong, you've lost 10 seconds. If you silently guess wrong, you've lost an hour.

**Name the tradeoffs.** Almost every implementation choice has a tradeoff. If you're adding caching, say "this trades memory for speed and introduces cache invalidation as a thing we now have to think about." The user might say "actually I don't want that complexity." Better to know before you write 200 lines.

**If multiple approaches exist, present them briefly.** Not five. Two, maybe three. With a recommendation. "There are two ways to do this. Option A is simpler but doesn't handle edge case X. Option B handles everything but adds a dependency on Z. I'd go with A unless you expect X to actually happen."

**If something is confusing, stop.** Don't fill confusion with plausible-sounding code. The result of generating code when you don't understand the requirements is code that passes a casual review but fails when it matters. Just say what's confusing and ask.

**Justify every moving part.** Each concurrent actor, guard, cap, or recovery path needs a requirement or a measurement behind it. If you cannot cite one, ship the simpler design and say what would make you add the part later. Do not optimize a path you have not measured.

## 3. Simplicity

Write the minimum amount of code that solves the problem. Not the minimum amount of code you can imagine theoretically solving the problem. The minimum amount that actually solves this specific problem right now.

The instinct to over-engineer is strong. Resist it. Here's what over-engineering looks like in practice:

**Premature abstraction.** You need to send one type of email. You write an EmailService class with a strategy pattern that supports multiple providers, template engines, and retry policies. The user wanted `sendWelcomeEmail(user)`. Write that function. If they need more later, they'll ask.

```python
# bad: you wrote this
class EmailService:
    def __init__(self, provider: EmailProvider, template_engine: TemplateEngine):
        self.provider = provider
        self.template_engine = template_engine

    async def send(self, template: str, context: dict, recipient: str, **kwargs):
        rendered = self.template_engine.render(template, context)
        await self.provider.send(recipient, rendered, **kwargs)

# good: you should have written this
async def send_welcome_email(user):
    body = f"Welcome {user.name}! Your account is ready."
    await send_email(to=user.email, subject="Welcome", body=body)
```

**Speculative error handling.** You wrap everything in try/catch blocks for errors that can't happen. You validate inputs that come from your own code and are already validated upstream. You add null checks on values that are never null. Every line of error handling is a line someone has to read and understand. Only handle errors that can actually occur.

**Unnecessary configurability.** You make the batch size a parameter. You make the retry count configurable. You add environment variables for things that will never change. Configuration is not free. Every config option is a decision someone has to make and a value someone has to set correctly. Hardcode things until there's a real reason not to.

**Dead flexibility.** Interfaces with one implementation. Abstract base classes with one child. Generic type parameters that are only ever instantiated with one type. These things have a cost (cognitive overhead, indirection, more files to navigate) and zero benefit until a second implementation actually exists.

**Thin wrappers and one-value options.** A function that only forwards to another function, wraps one constructor, or has a single caller and adds nothing earns no place; inline it. A flag whose every production caller passes the same value is not an option; delete it and the dead branch. When porting code, drop intermediate shapes the new home does not need.

**Test-only parameters.** Do not add a production parameter that only tests pass. If production code never supplies a value other than the default, the parameter is test scaffolding in the production signature. Test through the real interface instead.

**Plain over clever.** Write index arithmetic, sort keys, parsing and shell as named steps a reader can follow. No nested ternaries.

**Files over 1,000 lines.** Keep every file at or under 1,000 lines. If your change would push a file past that, split it first: extract helpers, submodules, or components along a seam the code already has, and put the cooperating files a split produces in a new folder named after the unit they implement, not as flat siblings in a folder that already holds unrelated files. Exceed the limit only for a concrete reason, such as generated output, a lockfile, a data fixture, or one cohesive unit that splitting would scatter, and state that reason in the PR description. A file that is already over the limit is not yours to split unasked, but do not grow it without the same kind of reason.

The test for simplicity: for each function, class, parameter, flag, check and file your diff adds, name the caller or requirement that needs it now. If the answer is "in case we need to", delete it.

## 4. Surgical Changes

When you edit existing code, your diff should be as small as possible. Every line you change is a line that could introduce a bug, a line someone has to review, and a line that shows up in git blame forever.

Rules:

**Don't touch what you weren't asked to touch.** If you're fixing a bug in function A and you notice function B has a weird variable name, leave it. If function C has a comment with a typo, leave it. If the import order doesn't match your preference, leave it. Your job is to fix the bug in function A.

**Match the existing style.** If the file uses single quotes, use single quotes. If the file uses `snake_case`, use `snake_case`. If the file has no semicolons, don't add semicolons. If the file uses `var` (yes, even in 2025), use `var` in your additions unless the user asked you to modernize. Consistency within a file beats your personal preference.

**Clean up after yourself, not after others.** For every call, branch or flag your change removes, search for the symbol it used. Delete the function, parameter, field, endpoint, wrapper, import or scaffolding your change left with no caller. Pre-existing dead code is not your problem unless someone asked.

**Update what describes the behavior you changed.** When you change behavior or replace a design, fix every docstring, name, test, test double, snapshot, golden, fixture, doc, model-facing prompt and tool description that still describes the old one. A prompt that names a tool, source, field or document the turn no longer has is a bug, not stale prose. Regenerate generated fixtures after the final rebase. Search for the old term before you hand off.

**Comments and docstrings explain why, never what.** Do not narrate the implementation, restate a parameter, or describe a constant. If a comment explains what a block does, extract the block into a function whose name says it. If a comment explains a constant or a magic number, give the constant a better name. Never write a comment about the PR or the stack ("moved in the next layer"). Keep a comment only for a reason the code cannot show.

**Don't reformat.** Don't run prettier on a file that wasn't formatted with prettier. Don't change indentation from 4 spaces to 2. Don't reorder imports alphabetically if they weren't alphabetical before. Reformatting creates massive diffs that hide your actual changes and make code review painful. Run formatters and lint autofixes on the files you changed, then revert any hunk that touches lines you did not edit.

**A refactor keeps every guard.** When you move, merge or swap the library under code, keep each timeout, exclusion, callback and error handler it had, or say in the PR why it goes. After a merge or rebase, diff each conflicted file against the new base so you do not revert an upstream change.

The test: look at your diff. Can you justify every single changed line with a direct connection to what was asked? If any line is there because "while I was in there I thought I'd..." then revert it.

## 5. Verification

The difference between code that works and code you think works is testing. You should be paranoid about this distinction.

**Write the test first when fixing bugs.** Before you fix anything, write a test that reproduces the bug. Run it. Watch it fail. Then fix the bug. Run the test. Watch it pass. This is not optional and not TDD dogma. It's the only way to prove you actually fixed the thing and didn't just make the symptoms go away.

**Run existing tests before and after your changes.** If tests passed before your change and fail after, you broke something.

**Don't write tests for the sake of writing tests.** A test earns its place only when it can fail because behavior is wrong. A test that checks whether a constructor sets properties is worthless. A test that checks whether your validation actually rejects bad input is valuable. Test behavior, not implementation. Test the interesting cases, not the trivial ones.

**One test per behavior, at the layer that owns it.** Before adding a test, name the failure that only this test catches. If a lower-layer test already catches it, do not repeat it higher up.

**Test your code, not the library.** A test that passes whenever the framework works is not coverage.

**Do not pin tests to data that is meant to change.** Derive expected values from the fixture, or freeze a copy of the data under the tests directory. A test that asserts the contents of a live baseline breaks on the next legitimate refresh.

**Tests run wherever the suite runs.** A test that needs one operating system or one environment is skipped elsewhere with a stated reason, not left to fail on a colleague's machine.

**Don't add a test that only restates a file.** It passes until someone edits the file for a real reason, and it never catches a broken feature:

- The file exists, is non-empty, or contains a heading. Asserting every `AGENTS.md` still has text after `strip()` does not check that the guide is accurate or that anything follows it. Version control already records that the file is there.
- A config or build file contains a fixed string. Asserting `.bazelrc` contains `--aspects=//tools/boundaries:enforcer.bzl%import_enforcer` does not run the aspect and does not show that a forbidden import fails the build. A comment with the same text would pass.
- The assertion is a second copy of a constant, flag, or source line you control in both places.
- It mocks every collaborator and asserts which mocks were called, in what order or with what arguments, or greps the source for text. That pins the implementation and passes while behaviour is broken. Assert an output or a side effect instead.
- It parses a CI workflow file (GitHub Actions YAML and similar) or pins a list of jobs, paths, or config keys. These are restatements too: do not write them. Test the behavior of the script the workflow calls, and use real CI runs as the evidence for trigger, condition, and job-graph changes. The exception is a test that pins the permissions granted to a CI or service identity against a mocked permission system. A widened grant is a security change, so a test that fails on it earns its place.

If you cannot name a behavior that fails the test while the files stay well formed, do not add the test. Say that, and why. The import enforcer is worth a test when you hand it source and assert that an allowed import passes and a forbidden one exits non-zero. An empty-file check is not a stand-in for that.

**Run the change before you call it done.** Before reporting a change done, exercise the changed path itself: manually verify the changes on the local stack for UI or full-stack changes, the script or job for tooling, the reproduction for a bug fix. Say what you ran. Unit tests and lint alone are not verification.

**If you can't write a test, say why.** Sometimes the architecture makes testing hard. That's useful information. "I can't easily test this because the database calls are tightly coupled to the business logic" is a signal that something might need to be restructured. Don't just skip testing and hope.

## 6. Goal-Driven Execution

Every task should have a clear success criterion before you start writing code. If the criterion is vague, make it specific. If you can't make it specific, ask.

Transform vague tasks into verifiable ones:

- "Add validation" becomes "reject inputs where email is missing or invalid, return 400 with a message that says what's wrong, add tests for both cases"
- "Fix the bug" becomes "write a test that reproduces the reported behavior, make the test pass, verify existing tests still pass"
- "Improve performance" becomes "profile first, identify the bottleneck, fix that specific thing, measure again"

For anything that takes more than one step, state the plan before executing.

## 7. Debugging

When something doesn't work, don't guess. Investigate.

**Read the error message.** The whole thing. Including the stack trace. LLMs have a terrible habit of seeing an error and immediately generating a "fix" based on the error type without reading what it actually says. A TypeError could mean a hundred different things. The message and stack trace tell you which one.

**Reproduce first.** Before you change anything, make sure you can reproduce the problem. If you can't reproduce it, you can't verify your fix. "I think this should fix it" is not debugging. It's gambling. Never ship a bug fix you have not first seen reproduce the bug.

**Don't call a failure a flake without naming the mechanism.** "Flaky", "stalled", or "infra blip" is a conclusion, not an explanation. Before you use one, read the logs, name what actually failed (a network fetch, a race, a timeout, a cold cache), and check whether a cache, retry, or timeout would prevent it. Only then decide whether it belongs to this change.

**Change one thing at a time.** If you change three things and the bug goes away, you don't know which change fixed it. You also don't know if the other two changes introduced new bugs. Change one thing. Test. Change another. Test.

**Don't add workarounds without understanding the root cause.** If a value is unexpectedly null, don't just add a null check and move on. Figure out why it's null. The null check might prevent a crash, but the underlying bug is still there and will manifest differently later.

**If you're stuck, say so.** "I've tried X and Y and neither worked. Here's what I'm seeing. I think the issue might be Z but I'm not sure." This is infinitely more useful than silently trying random things for 20 iterations.

## 8. Dependencies

Don't add dependencies without thinking about it.

Every dependency you add is code you don't control that becomes a permanent part of the project. It needs to be maintained, updated, audited for security issues, and understood by everyone on the team. The cost is almost always higher than it looks.

Before adding a package:

- Can you do this with what's already in the project? If the project has axios, don't add node-fetch. If the project uses date-fns, don't add moment.
- Can you do this with the standard library? You don't need lodash for `Array.prototype.map`. You don't need uuid if `crypto.randomUUID()` exists.
- Is this dependency actually maintained? Check the last commit date. Check the issue count. Check if the maintainer responds to issues.
- How big is it? If you're adding a 500KB package to format a date, that's probably not worth it.

When you do add a dependency, say why. "I'm adding zod because this project needs runtime schema validation and there's nothing in the existing dependencies that does this" is fine. Silently adding packages to package.json is not.

When you bump a dependency, bump the packages released with it (the same scope or monorepo, such as `@vitest/*`) to matching versions. Regenerate a lockfile with the package manager, never by hand, and do not regenerate a committed lockfile when you only meant to verify it. Then read the lockfile diff: every package resolved outside the registry must keep its source URL and integrity hash, and a new duplicate copy of a package or a version change you did not ask for is a defect to fix before you hand off.

## 9. Communication

How you communicate about code matters as much as the code itself.

**Say what you did and why.** Don't just dump a code block. "I moved the validation logic into a separate function because it was duplicated in three endpoints. This also makes it testable independently." Now the user understands the change without reading every line.

**Flag concerns.** If you implemented what was asked but you think there's a problem with the approach, say so. "This works but it makes a database call for every item in the list. If the list gets large this will be slow. Want me to batch it?" is the kind of proactive communication that saves hours later.

**Be precise about what you're uncertain about.** "I'm not sure if this library supports streaming responses" is useful. "I think this should work" is not. The difference is that the first one tells the user exactly what to verify.

**Cite what you read before stating a fact.** In plans, reviews, PR comments, replies and code comments, every claim about existing code, config, infrastructure, an external service's behaviour, unit or quota, or a commit hash must come from a file, command, doc or API response you read in this session. Cite it, or label the claim unverified. A job name, engine version, or hash recalled from memory is a guess until you have looked it up.

**Fix the class of problem, not the instance.** When a review comment names a pattern, search the rest of the diff and every PR in the stack for the same pattern and fix all of them in the same round. Before replying "done", check the claim against the pushed diff and cite the commit.

**Write final summaries the reader can act on.** End every summary that follows a PR change with the PR link. Do not refer back to items by labels you invented earlier in the session; say what you mean in place. Describe user-visible behavior concretely: what the user does and what they now see, not an abstraction of it.

**Don't explain things the user already knows.** If they asked you to add a REST endpoint, don't explain what REST is. If they asked for a database index, don't explain what indexes do. Match your explanation level to the user's demonstrated knowledge.

**Commit messages matter.** If you're writing a commit message, make it specific. "Fix bug" is useless. "Fix null pointer in user lookup when email contains uppercase chars" tells the next person exactly what happened.

## 10. Common Failure Modes

These are the patterns I see most often. If you catch yourself doing any of these, stop and reconsider.

**The Kitchen Sink.** Asked to add one feature, you restructure half the codebase "while you're at it." Don't. Do the one thing.

**The Wrong Abstraction.** When an existing helper already owns the behavior, reuse it rather than writing a second copy. A rule decided in two places drifts; decide it once and have every caller use that.

**The Invisible Decision.** You make an architectural choice (database schema, API shape, auth strategy) without flagging it as a decision. These choices are hard to reverse and the user should be aware you made them.

**The Optimistic Path.** You write code that handles the happy path perfectly and ignores or crashes on everything else. Think about what happens when the API returns 500. When the file doesn't exist. When the user submits an empty form.

**The Knowledge Hallucination.** You confidently use an API that doesn't exist, a parameter that was removed two versions ago, or a library feature you're imagining. If you're not 100% sure a method exists with this exact signature, say so. Check the docs. Look at the actual source code in the project.

**The Style Drift.** You write code in your "preferred" style instead of matching the project. Functional patterns in an OOP codebase. Classes in a functional codebase. TypeScript patterns in a JavaScript project. Match the codebase, not your preferences.

**The Runaway Refactor.** You start fixing one thing. It touches another thing. That touches another. Twenty minutes later you've changed 15 files and you're not sure what you originally set out to do. If a fix is cascading, stop. Tell the user what's happening. Get buy-in before continuing.

**The Context Dump.** You learn something about a subsystem and append it to the nearest always-loaded file, because that is where you were looking. Every agent that touches any file below it now pays for that paragraph, whether or not it is relevant. Put the fact in the file that owns it (see section 12).

## 11. Pull Request Scope and Size

**One PR, one atomic change.** Scope every pull request to a single feature, fix, or component. If the description needs "and also" to explain it, or a reviewer could approve one part of the diff while rejecting another, those parts are separate PRs. Refactors, renames, dependency bumps, and cleanup that the main change does not need go in their own PRs. A refactor the change depends on goes in its own PR below it in a stack. A small PR that does two things is still two PRs.

A pull request must not exceed **2,500 changed lines**, measured as additions plus deletions against the PR's base branch. This is a hard limit, not a target, and includes application code, tests, migrations, and formatting changes. Auto-generated files, such as lockfiles and other generated config, do not count towards it. A file counts as generated only when a tool writes it from inputs in the repository and nobody edits it by hand, so that rerunning the tool reproduces it exactly. When they take the raw total over 2,500, state the hand-written line count in the PR description. Staying under the limit does not make a multi-purpose PR acceptable.

Before creating or updating a PR, run `git fetch`, then `git log --oneline origin/<base>..HEAD` and `git diff --stat origin/<base>...HEAD` against its intended base branch. Read every file the diff lists and revert any file or hunk the change does not need, including formatter rewraps, lockfile churn and renames. Every commit and file must serve one change you can describe without "and also"; a file you did not touch, or a commit from another branch, means the base is wrong. Then check the hand-written line count against 2,500 lines. If it does more than one thing or its hand-written lines would exceed 2,500, split the work before handoff; never create a mixed or oversized PR with a promise to split it later.

Split along vertical slices one reviewer can own. Keep supporting edits (comments, renames the change needs) in the PR they support. Check the hand-written line count against the 2,500 limit before handing off.

Split independent changes into separate PRs against the base branch. Split dependent changes, and any single change over the limit, into a real GitHub PR stack:

- Each branch is based on the preceding branch.
- The first PR targets the original base branch; each later PR targets the previous branch in the stack.
- Every PR in the stack does one thing and stays at or below 2,500 hand-written changed lines against its own target branch.
- Split by coherent deploy or implementation concern and order dependencies from bottom to top.
- Every PR must be independently mergeable in stack order. Once its predecessors have merged, it must leave the base branch working, tested, and safe to deploy without requiring any later PR in the stack.
- Design schema, API, configuration, and rollout changes so a partially merged stack remains correct. Earlier PRs must remain safe indefinitely if later PRs are delayed or never merged.
- Do not hide an oversized change by moving files between layers, counting a hand-written or hand-edited file as generated, or using a cumulative diff different from the PR's actual base.
- Never put code in one layer that a later layer in the same stack deletes or rewrites. Restack so the final shape lands once.
- Do not move or add groundwork "for a later PR" unless you can name the PR and the call site that uses it.

Check every factual sentence in a PR description ("only X uses this", "the next PR reuses these") against the code at the head you are describing, defaults included.

If the work cannot be split safely while preserving correctness, stop and ask the user how to proceed. Do not silently exceed the limit.

## 12. Progressive Disclosure for Agent Context

Agent instruction files (`AGENTS.md`, `CLAUDE.md`, rules, and similar) are loaded automatically, and every byte in them is paid for on every task that touches their directory, whether or not it is relevant. A 100 KB file read before every edit crowds out the code the agent should be reading, and the one rule that matters gets lost in it.

Structure agent context so each reader loads only what their task needs:

- **Always-loaded files hold orientation, invariants, and routing.** What this directory is for, the handful of rules that hold everywhere beneath it, and a table that says where to read next for each kind of task. Not file catalogues, command references, runbooks, or per-feature detail.
- **Detail lives in the file that owns it.** A rule about one script belongs in that script's directory file, or in a skill or reference doc loaded only when the task calls for it. Put each fact in the deepest file whose whole subtree it applies to.
- **One owner per fact.** If two files state the same rule, they will drift, and a reader cannot tell which is right. Keep one copy and delete the other. A pointer to the owner is fine; a paraphrase is a second copy.
- **Pointers go down or out, never up.** A child file pointing back at its parent for detail means the detail is in the wrong place. Move it down.
- **Do not catalogue what the code already says.** File-by-file descriptions duplicate module docstrings and go stale silently. Document rules, contracts, and footguns the code cannot show.
- **Set a size budget for always-loaded files and measure it.** Count the bytes an agent loads for a file in a given directory, summed over every file in the chain. If a change pushes that chain over budget, move detail down before adding more.

When restructuring existing agent context, treat it as a refactor:

- Snapshot the before state and list every command, path, and flag it mentions. After the move, each one must still exist somewhere or be deleted on purpose with a reason.
- Check commands and paths against the code as you move them. Moving a stale command just moves the bug.
- Prove navigation still works. Give a fresh agent a real task, let it start from the top-level file with no search, and check that it reaches the owning file in a few hops. A routing table that only its author can follow is not routing.

The test: an agent editing a single file should be able to name every always-loaded line it just read as relevant to that edit, or as one hop from the rule it needs.
