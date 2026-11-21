# Decisions made during the run

The orchestrator records here the decisions taken while the s-stack package is built. Read this file together with `decisions.md`.

| Date | Decision | Door | Reason |
| --- | --- | --- | --- |
| 2026-11-21 | The tick fires at minutes 7, 27 and 47 of each hour. | Two-way | Twenty minutes apart, and off the busy minutes on the hour and half hour. |
| 2026-11-21 | The run's workflow is driven by hand, with the briefs the developer wrote, until the launcher and `sam-mode` exist. | Two-way | The developer's instruction for this run. |
