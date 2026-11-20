---
name: reflect
description: Spawn three parallel review subagents over the active transcript, surface learnings, and route each to a concrete edit on an existing skill. Use when the user says reflect.
disable-model-invocation: true
---

# Reflect

Mine the current conversation for durable learnings, then route them into skill edits.

Invoke when the user says "reflect" or "/reflect". Skip when the conversation is trivial, off-topic, or already covered by an existing skill the parent followed correctly. One-offs are not learnings.

## 1. Locate the active transcript

Before fanning out, find this conversation's transcript in the active workspace's transcript directory. Read only this workspace's folder. Do not glob across every project's transcripts. That crosses workspace boundaries and reads private chats from unrelated projects.

- **Cursor.** The system prompt names the `agent-transcripts/` directory, under `~/.cursor/projects/<slug>/agent-transcripts/`. List the candidates:

  ```bash
  ls -t <agent-transcripts>/*.jsonl <agent-transcripts>/*/*.jsonl <agent-transcripts>/*/subagents/*.jsonl 2>/dev/null | head -10
  ```

  That covers the legacy flat (`<id>.jsonl`), current nested (`<id>/<id>.jsonl`), and subagent (`<parent>/subagents/<child>.jsonl`) layouts.
- **Claude Code.** Transcripts are `~/.claude/projects/<slug>/<session>.jsonl`. The slug is the workspace path with each `/` and `.` changed to `-`, so `/Users/you/proj` is `-Users-you-proj`. The newest `.jsonl` directly in that folder is the current session. Its `<session>/subagents/` folder holds subagent transcripts.
- **Other hosts.** Use the transcript location the host documents for this workspace. If it has none, pass a digest.

For each candidate, read the first JSONL line. Take the file whose first line contains the conversation's opening user prompt (in Cursor, `message.content[0].text`). If none matches, pass a tight digest of the session instead.

## 2. Spawn three reviewers in parallel

In one message, spawn three general-purpose subagents in parallel. Do not make them read-only. Reviewers need MCP access to look up the tickets, chat threads, and observability traces the transcript references, and a read-only subagent can lose MCPs.

Each reviewer and the synthesiser name a role line in the `pstack-models` rule that [`/setup-pstack`](../setup-pstack/SKILL.md) writes, and a default. Set the subagent's model to that line's value, or to the default if the rule or the line is missing. Leave the model unset when the value is `auto` or `inherit-parent`. The defaults below are model choices the host maps to its own names: Opus 5.5 at xhigh effort is the slug `claude-opus-5-5-xhigh` in Cursor and model `opus` with effort `xhigh` in Claude Code. Where a model is unavailable on the host, such as Grok outside Cursor, leave the model unset so the subagent runs on the session model, and say so. If the subagent tool rejects a model, use the default and say so. If it rejects the default, use the closest valid model of the same family from its error message. Pick each subagent's reasoning level and fast or standard speed for the job, per the Subagents section of the **poteto-mode** skill.

| Lens | Role line | Default model | Prompt template |
|---|---|---|---|
| Judgement | `reflect judgment, divergent, synthesizer` | Opus 5.5, xhigh (`claude-opus-5-5-xhigh`) | `references/judgment-reviewer.md` |
| Tooling | `reflect tooling` | Grok 4.7, xhigh, fast (`grok-4.7-xhigh-fast`) | `references/tooling-reviewer.md` |
| Divergent | `reflect judgment, divergent, synthesizer` | Opus 5.5, xhigh (`claude-opus-5-5-xhigh`) | `references/divergent-reviewer.md` |

Pass each template verbatim, substituting the transcript path or digest where marked. Reviewers return findings in the subagent's response body.

## 3. Synthesise

Spawn one general-purpose subagent, with its model from the `reflect judgment, divergent, synthesizer` line (default Opus 5.5 at xhigh effort, `claude-opus-5-5-xhigh`). Do not make it read-only. It spot-verifies citations through MCP, and a read-only subagent can lose MCPs. Pass `references/synthesizer.md` verbatim, with each reviewer's full output inlined where marked. It returns an Accepted / Rejected / Backlog list.

## 4. Structural enforcement check

Move any Accepted item that a lint rule, script, metadata flag, or runtime check would enforce more reliably to Backlog. See the **encode-lessons-in-structure** principle skill.

## 5. Apply

Present the synthesiser's full Accepted / Rejected / Backlog output and wait for explicit approval before applying any Accepted edit. The user picks the subset and may redirect routings. Skill changes affect every future agent in the org. Do not auto-apply.

File each Backlog item to your team's devex or backlog tracker without waiting. Only the Accepted list waits for approval.

Never edit a skill inside a plugin or package cache, such as `plugins/cache/` or `apm_modules/`. Before approval, show its destination: the project's deployed skills directory (`.agents/skills/<skill>/` or `.claude/skills/<skill>/`) or the user-level equivalent (`~/.cursor/skills/<skill>/` or `~/.claude/skills/<skill>/`). After approval, copy the skill folder there and edit the copy. Never open a PR or push.

Follow each approved row's Routing exactly:

- Trivial existing-skill edit (a one-line bullet, a tightened sentence, a stale fact corrected): the parent does it directly.
- Substantive existing-skill edit (a new section, a new pattern table, more than ~10 lines): hand to the host's skill-authoring skill (Cursor's built-in `create-skill`, or the equivalent installed on other hosts) and run its draft / test / iterate loop.
- `tune description: <skill path>` (the skill exists but didn't trigger when it should have): hand to the skill-authoring skill and run its description-optimisation loop.
- `new skill via create-skill: <kebab-name>`: hand creation to the skill-authoring skill. Do not invent the shape ad hoc.

If your environment ships a SKILL.md validator, run it on every touched skill before declaring done.

## 6. Summarise for the user

Short list, no preamble:

- Edits applied: `<skill path>`. What changed, one line each.
- New skills created: `<skill path>`. One line each (rare).
- Backlog filed to the devex tracker: `<issue title>` (`<tags>`). One line each.
- Dropped: one line per rejected finding + reason from the synthesiser.
