# Phase `spec-planner-handbooks` checks

Phase `spec-planner-handbooks` ships the spec writer and planner handbooks of the `sam-mode` skill. Both are prose, so the behavioural checks are cold reads. A cold read starts a fresh subagent, gives it only the file the check names, tells it to read nothing else, and asks the questions. Its answer passes when it agrees in substance with every point of the expected answer. Wording may differ, but a missing or contradicting point fails the check. Wait for every cold-read subagent to finish before reporting.

The two files, relative to the repository root:

- `packages/s-stack/.apm/skills/sam-mode/handbooks/planner.md`
- `packages/s-stack/.apm/skills/sam-mode/handbooks/spec-writer.md`

## Rerun

### Cold read 1. The planner's phase table

Files: `handbooks/planner.md` only.

Prompt: "Read only this file and nothing else, not even files it names or links to. Answer from it alone. You are the planner. You cannot explore any code or run any experiment, so where you would need a fact, state your assumption. The approved roadmap is the two paragraphs below. Write the table of every phase at a glance that your feature plan would hold, with every field the file says a phase entry holds, then say in one sentence each which phases can run at the same time.

Roadmap, paragraph 1: The placeholder application `acme-notes` is a small web service with a Python back end under `server/` and a browser front end under `web/`. It gains note sharing. A shared note is stored in a new `shares` table, and the back end exposes `POST /shares` and `GET /shares/<id>`. Separately, a command-line tool under `cli/` gains a `notes import` command that reads a Markdown folder into the existing `notes` table. The import does not touch sharing.

Roadmap, paragraph 2: The front end's single note view, the one file `web/note-view.js`, gains a share button that calls the two sharing endpoints and an 'imported' badge on notes brought in by `notes import`. Both changes go in that one file and ship together, so the front end work is one unit that needs both the sharing back end and the import. The back end's test suite starts a local database on port 5432, and only one test run can use that port at a time. The repository already has a verification skill, `verify-acme-notes`, that covers all three directories."

Expected answer:

1. Three phases: the sharing back end, the import command, and the front end that needs both. The front end stays one phase, because its work is one file.
2. Every phase gives each field that roadmap `workflow.md` names for the feature plan: its scope, the phases it depends on (or none), the paths it owns, its exclusive resources (or none), and a **Done when** list of the evidence that proves it done.
3. The front end phase depends on both the sharing phase and the import phase. The sharing and import phases depend on nothing and can run at the same time.
4. No two phases that can run at the same time own the same path.
5. Port 5432, or the local test database on it, is named as an exclusive resource of each phase whose tests start that database.

### Cold read 2. The spec writer's questions, records and handover

Files: `handbooks/spec-writer.md` only.

Prompt: "Read only this file and nothing else, not even files it names or links to. Answer from it alone. You are a new spec writer, started with `update=-` for feature `notes-export`. The developer's idea is: 'Users of the placeholder application `acme-notes` can get a CSV export of all their notes, and the export should stay fresh. While we are at it, drop the old `legacy_tags` column from the `notes` table in the same migration, because nothing reads it any more.' (1) Which questions would you put to the developer about this idea, and why each? (2) Where do you record the answers, and what do you record with each? (3) When and how does the orchestrator get started, and what do you do after that?"

Expected answer:

1. It asks the developer about the column drop, because deleting a column and its data cannot be undone, so it is a one-way door. It asks when an export happens, for example daily or on demand, because "stay fresh" is ambiguous. It settles neither itself and sends the orchestrator no decision request.
2. It records each answer in `decisions.md` in the roadmap directory `.foundry/feature-roadmaps/<id>/`, with its door type (one-way or two-way), who decided and why. It does not write `run-decisions.md`.
3. Only after the developer explicitly approves the roadmap. It commits, then from its own main session, not a subagent, it runs the launcher in the `sam-mode` skill's `scripts/` directory: `launch.sh --print-window` to learn its window, then `launch.sh --feature notes-export --role orchestrator --window <window id>`. It reports the launcher's output to the developer and stops working.
