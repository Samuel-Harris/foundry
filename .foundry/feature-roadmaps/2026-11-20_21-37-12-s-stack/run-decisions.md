# Decisions made during the run

The orchestrator records here the decisions taken while the s-stack package is built. Read this file together with `decisions.md`.

| Date | Decision | Door | Reason |
| --- | --- | --- | --- |
| 2026-11-21 | The tick fires at minutes 7, 27 and 47 of each hour. | Two-way | Twenty minutes apart, and off the busy minutes on the hour and half hour. |
| 2026-11-21 | The run's workflow is driven by hand, with the briefs the developer wrote, until the launcher and `sam-mode` exist. | Two-way | The developer's instruction for this run. |
| 2026-11-21 | The 2,500-line pull request limit does not count auto-generated files such as `apm.lock.yaml`. The PR that adds `packages/s-stack` and the `default-stack` PR proceed with their full lockfiles, and each description states the hand-written line count. | Two-way, asked because the coding rules require it | The developer: "The 2500 line PR limit should ignore auto-generated config like lockfiles". Raised by the planner. |
