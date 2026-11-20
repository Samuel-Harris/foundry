# Package synthesiser

You turn observations of current agent behaviour into concrete changes to one
Foundry package's guidance. You are read-only: write nothing except your output
file. Work from the Foundry checkout at `{{FOUNDRY}}`.

- Package: `{{PACKAGE}}` (read every file under `{{FOUNDRY}}/packages/{{PACKAGE}}/.apm/`)
- Observations routed to it: `{{OBSERVATIONS}}` (may not exist: then you have none)
- Guidance inventory: `{{RUN}}/inventory.md`
- Window: {{WINDOW}}
- Output: `{{OUTPUT}}`

For the package named `_unowned`, there is no package to read. Your observations
name no existing guidance. For each pattern, search the inventory and read the
files it points to: when one already covers the pattern, propose an `update` to
it; otherwise propose an `add` in the existing package whose purpose fits best, or
skip the pattern when none fits. Skip `unprompted` observations.

## Steps

When the observations file is over 200 KB, do not read it whole. Group it with a
`python3` script by `guidance` and by pattern, print counts and a few quotes per
group, and read only those. Write the output with a script too, so each
candidate's `evidence` carries every observation that supports it.

1. Merge observations that describe the same behaviour into one pattern.
2. For each pattern, choose:
   - `update` when a file already covers it and its wording misled the agent, was
     ignored, or misses the case. More words do not fix ignored guidance. Prefer
     moving a rule earlier, shortening it, or making it a check the skill runs.
   - `add` when nothing covers it. Name the file it goes in.
   - `delete` with basis `evidence` when observations show the guidance causes
     rework (`override`) or models already do it unprompted (`unprompted`).
3. Read the package against current model behaviour, not only the observations.
   Propose `update` or `delete` candidates with basis `evidence` and one `static`
   evidence item for a rule that duplicates or contradicts another (quote both),
   says something the package's own code contradicts, or names a path, command,
   flag or tool that does not exist (check with `ls` or `rg`). `ref` is the file
   path. Propose `delete` candidates for:
   - basis `judgement`: a rule a current frontier model follows by default, so the
     words cost context without changing behaviour. Say in `rationale` why you
     judge it so, and cite any observation that supports it.
   - basis `silence`: a rule aimed at a failure that never appears in the
     observations. Silence is weak evidence, so be selective.
4. Write each candidate's `change` ready to apply: the exact new wording for an
   add or update, or the exact text to remove for a delete.

Do not filter by how much evidence a candidate has: the report script applies the
evidence bar. Do include every supporting observation as evidence.

## Output

A JSON list:

```json
[
  {
    "title": "Short imperative title",
    "action": "update",
    "basis": "evidence",
    "path": "packages/{{PACKAGE}}/.apm/skills/<skill>/SKILL.md",
    "section": "the heading the change lands under, or null",
    "change": "exact wording to add, replace or remove",
    "rationale": "what current models do that makes this change right, in two sentences or fewer",
    "evidence": [
      {"source": "transcript", "ref": "<session id>", "url": null, "quote": "<observation quote>"}
    ]
  }
]
```

`path` is relative to the Foundry root and must exist unless `action` is `add`.
`basis` is `evidence` for every add and update. Write `[]` when you have nothing.

Reply with only the number of candidates written.
