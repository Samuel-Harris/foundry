# Interview: s-stack

## Metadata

- Rounds: 7, plus two clarifications of round 1
- Final Ambiguity Score: 16%
- Type: brownfield
- Generated: 2026-11-20_21-37-12
- Threshold: 20%
- Status: PASSED

## Clarity Breakdown

| Dimension | Score | Weight | Weighted |
| --- | --- | --- | --- |
| Goal Clarity | 0.90 | 0.35 | 0.315 |
| Constraint Clarity | 0.80 | 0.25 | 0.200 |
| Success Criteria | 0.80 | 0.25 | 0.200 |
| Context Clarity | 0.85 | 0.15 | 0.128 |
| **Total Clarity** | | | **0.84** |
| **Ambiguity** | | | **0.16** |

## Goal

Formalise the multi-session workflow that the developer ran by hand for a large feature in a private repository. A spec writer writes a feature roadmap. An orchestrator starts a planner and one Claude Code session for each phase, in worktrees and in panes of the current tmux window. Each phase opens draft pull requests as soon as agents have verified and reviewed it.

The specification is the feature roadmap at `.foundry/feature-roadmaps/2026-11-20_21-37-12-s-stack/`.

## Constraints

- s-stack builds on pstack and ships as a Foundry package that `default-stack` installs.
- workmux manages worktrees and sessions. New sessions open as panes in the current tmux window.
- No session assumes that the default branch is `main`.
- The developer's contact points are the spec writer and the orchestrator.
- s-stack ships prose and one launcher. It has no command-line tool that enforces state changes.
- Nothing is approved in advance for phase sessions.

## Non-Goals

- Small patches and minor bug fixes.
- Claude Code agent teams.
- Hosts other than Claude Code.

## Acceptance Criteria

- [ ] The developer never reminds the orchestrator to update the status board or the roadmap.
- [ ] The first phase's draft pull requests are open while another phase is still being built.
- [ ] The developer types only into the spec writer and orchestrator panes, apart from permission prompts and sessions visited by choice.
- [ ] A restart of the orchestrator or of a phase session loses no report and no state.

## Assumptions Exposed & Resolved

| Assumption | Challenge | Resolution |
| --- | --- | --- |
| Pull requests are split out after every phase has merged | "Doesn't that mean all the phases would need to be completed before they can be reviewed?" | Each phase opens its pull requests as soon as its gates pass. |
| The default branch is `main` | "Don't assume main is the default branch." | Every session resolves the default branch. |
| The orchestrator branch is a preview that nothing is cut from | The developer proposed their own model | Phase worktrees are cut from the orchestrator branch. Pull requests target the default branch. The phase merges into the orchestrator branch before dependent phases start. |
| A phase with two unmerged parents holds its pull requests | The developer's note on round 2 | The pull requests are created. Each records the pull requests it depends on. |
| Each role in the first-draft rubric is its own session | The November run used three kinds of session | The verifier, the reviewers and the PR creator are fresh subagents of the phase session. |

## Technical Context

The roadmap's `evidence.md` holds the findings from the November transcripts, the Claude Code documentation, the experiments and the Foundry repository.

## Ontology (Key Entities)

| Entity | Fields | Relationships |
| --- | --- | --- |
| Feature roadmap | Problems, intended behaviour, decisions, constraints | Written by the spec writer. Read by every main session. |
| Feature plan | Phases, dependencies, owned paths, exclusive resources, evidence of done | Written by the planner. Splits the roadmap into phases. |
| Phase | State, branch, head commit, verdicts, pull requests | Owned by one phase session. Depends on other phases. |
| Pull request | Number, branch, base, open dependencies | Belongs to one phase. Depends on other pull requests. |
| Decision request | Question, options, recommendation, door type | Sent by a session to the orchestrator. Answered by the developer. |
| Status board | Needs you, review queue, pull requests, phases, heartbeat | Written by the orchestrator. Read by the developer. |

## Interview Transcript

<details>
<summary>Full Q&A (7 rounds)</summary>

### Round 1, first form

**Q:** Which session topology should s-stack use: lean phase sessions, the rubric as written, or a hybrid with an independent verifier?
**A:** The developer did not choose. They asked: "Why would the PR creator split the PRs after merging back into the orchestrator branch? Doesn't that mean all the phases would need to be completed before they can be reviewed? I would like to be able to start reviewing code myself as soon as it has been verified and reviewed by agents".
**Ambiguity when asked:** 49%

### Round 1, second form

**Q:** When a phase passes agent verification and review, its pull requests open straight away as drafts. Where do they point, and what is the orchestrator's integration branch for?
**A:** The developer did not choose. They wrote: "Don't assume main is the default branch. What if we make per-phase sessions, branch phase worktrees off of the orchestrator branch, did the PR splitting (targetting the repo's default branch), then merged each branch into the orchestrator's branch before branching off the orchestrator branch to kick off phases that had depended on the phase we just finished."
**Ambiguity when asked:** 49%

### Round 2

**Q:** A pull request has one base. Phase 05 depends on phases 03 and 04, and neither has merged into the default branch. Where do 05's pull requests go?
**A:** "Hold until a parent merges", with this note: "The PRs should be created, but the PR creator should identify exactly which parent phase PRs the child phase's PRs are each dependent on, using gh stacks when there is a single dependency and explaining in the PR description when there are multiple dependencies. The orchestrator's status artefact should show which PRs depend on which other PRs and what the status of each is. If PR A depends on PRs B and C, and C gets merged in, the orchestrator should highlight that PR A can be stacked on top of PR B and if the developer asks the orchestrator to do this, the orchestrator should communicate this request to that phase's main agent which should use a PR creator subagent to apply this change."
**Ambiguity when asked:** 42%

### Round 3

**Q:** Who verifies and reviews each phase?
**A:** Fresh subagents. The phase's main session starts a fresh verifier subagent and a fresh reviewer subagent that gets the diff and never the plan. Both are gates before the PR creator subagent. Each phase adds its own checks file to the verification skill.
**Ambiguity when asked:** 40%

### Round 4

**Q:** Which of these are real requirements: no upkeep reminders, an early first pull request, two contact points, surviving restarts?
**A:** All four.
**Ambiguity when asked:** 35%

### Round 5

**Q:** Who writes the implementation plan, and when?
**A:** Two levels. A planner session writes the phase graph once the roadmap is approved. Each phase session writes its own detailed phase plan as its first step.
**Ambiguity when asked:** 27%

### Round 6

**Q:** How much code should s-stack ship?
**A:** Prose and one launcher. One status file for each phase, owned by that phase's session. No state-machine command-line tool.
**Ambiguity when asked:** 22%

### Round 7

**Q:** How should s-stack handle permission prompts in panes that the developer is not watching?
**A:** Notify, and the developer approves. The orchestrator checks `workmux status` on each loop, sends a push notification that names the pane and the action, and flags the session on the status board. Nothing is approved in advance.
**Ambiguity when asked:** 16%

</details>

## Review of the first version

The developer read the first version of the roadmap on the same day and replied to its list of points to confirm. The roadmap's `decisions.md` records the outcome of each.

| Point | The developer's answer |
| --- | --- |
| The two sentences that were cut off in the brief | "I meant built on top of p-stack and not replacing p-stack. I don't know what I meant by 'explicityl designed for'." |
| The pull request model and its second copy of each change | "keep my PR model with the safeguards." |
| The names `s-stack` and `sam-mode` | "these names are fine. p-stack should already be in the default stack (see origin/main)." |
| `.foundry/` staying off pull request branches | "just gitignore the .foundry directory if it isn't already gitignored." |
| The status board template | "sure." |
| Fix rounds that start from pull request comments | "I like this." |
| A default limit of five live phase sessions | "why limit it?" |
| The architecture page being out of scope | "I actually want an architecture explainer page. I found that really useful." |

The second version set out what ignoring `.foundry/` would change. The developer replied: "Sure. We don't need to ignore the .foundry directory. What's our next step?" The roadmap went back to tracking `.foundry/` in git.
