# Decisions made during the run

The orchestrator records here the decisions taken while the s-stack package is built. Read this file together with `decisions.md`.

| Date | Decision | Door | Reason |
| --- | --- | --- | --- |
| 2026-11-21 | The tick fires at minutes 7, 27 and 47 of each hour. | Two-way | Twenty minutes apart, and off the busy minutes on the hour and half hour. |
| 2026-11-21 | The run's workflow is driven by hand, with the briefs the developer wrote, until the launcher and `sam-mode` exist. | Two-way | The developer's instruction for this run. |
| 2026-11-21 | The 2,500-line pull request limit does not count auto-generated files such as `apm.lock.yaml`. The PR that adds `packages/s-stack` and the `default-stack` PR proceed with their full lockfiles, and each description states the hand-written line count. | Two-way, asked because the coding rules require it | The developer: "The 2500 line PR limit should ignore auto-generated config like lockfiles". Raised by the planner. |
| 2026-11-21 | The orchestrator branch for this run is `s-stack-package`, not `s-stack` as `workflow.md` would name it. Phase branches are `s-stack-phase-<phase>`, cut from `s-stack-package`. | Two-way | The roadmap was written and pushed as pull request 76 on `s-stack-package` before the run started. |
| 2026-11-21 | For this run, a commit that touches only generated files (`**/apm.lock.yaml` and the `version:` line of `packages/*/apm.yml`) does not move the code head and cancels no verdict. A stale lockfile or version on a pull request branch is a regenerate-only fix round. The PR creator refreshes the regenerate commit and repeats the equality proof, the phase stays in PR, and neither gate runs again. This amends `workflow.md` States rule 5 for this run. | Two-way | The developer chose the planner's option B. Without it, each of eight or more merges into `main` would send every other open phase back through both gates on unchanged code. The pre-commit hook, CI's frozen-lockfile and versioning checks, and Tier 1 on every merge into `s-stack-package` still catch a bad regeneration. |
