### Eval

**You own the experiment design. Plan, blind, run, synthesise.**

**Non-negotiables for blinding:**

- No `eval`, `test`, `judge`, `experiment`, `rubric`, `score`, `compare`, `benchmark`, `candidate`, or `arena` in any directory, file, or prompt the candidate sees.
- The candidate prompt looks like an organic user request. State the goal, not the meta.
- No chain-eliciting cues. Don't ask the candidate to list which skills, principles, or files they applied. Ask for design notes generally and grade chain-following from code shape, not self-report.
- Sanitise directory and slug names. Use project-shaped names a user might pick.
- Don't tell the candidate other candidates exist.
- The judge can know it's judging but sees outputs by sanitised label only, never by model name.
- Comparing two variants: one judge scores both sets in a single pass on one scale, blind to which set each came from.

**Steps:**

1. **Frame.** State what variant is under test and what behaviour counts as success. Write the rubric (3-6 concrete criteria) for the judge only. Hold it back from candidates.
2. **Set up sanitised environments.** Per-candidate working dir with the variant in place. Plant any context an organic task would have: a project skeleton, the skills the candidate would naturally read.
3. **Author one organic prompt.** What a user would type. No leakage of what's being measured.
4. **Spawn N parallel candidates** on different models per the **arena** skill's Phase B. Each works in its own sanitised dir. Same prompt to each. Pick each subagent's reasoning level and fast or standard speed for the job, per the Subagents section.
5. **Spawn one blinded judge** on a different model family per the **arena** skill's Phase C. Judge sees outputs by sanitised label and the rubric, never a model name.
6. **Verify the chain from transcripts, not self-report.** Read each candidate's local transcript for the active workspace only. In Cursor that is the workspace's `agent-transcripts/` directory under `~/.cursor/projects/<slug>/` (the system prompt names this path). In Claude Code it is `~/.claude/projects/<slug>/<session>.jsonl`, where the slug is the workspace path with each `/` and `.` changed to `-`, and the `<session>/subagents/` folder beside it holds subagent transcripts. Do not glob across `~/.cursor/projects/*/` or `~/.claude/projects/*/`. That crosses workspace boundaries and reads private chats from unrelated projects. Look at which files each candidate actually opened. Grade chain-following from the files it really read plus the shape of the code, never from the candidate's own claims.
7. **Read every candidate output yourself** end to end. Compare to the judge's verdict. Disagreement means a model is biased or the rubric is ambiguous. Synthesise.

**Reply:** variant under test, rubric, per-candidate notes, judge's verdict, your synthesis, and a recommendation for whether to promote the variant.
