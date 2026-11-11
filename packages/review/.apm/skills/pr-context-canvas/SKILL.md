---
name: pr-context-canvas
description: "Build a Cursor canvas of state charts that gives a pull request's reviewer the high-level picture, covering the behaviour the PR introduces and the system it is introduced into. Not a code review and no walkthrough of the diff. Use when asked for state charts, a big-picture overview, a high-level map or review context for a PR."
---

# PR Context Canvas

Build a Cursor canvas of state charts for one pull request, so its reviewer sees the
behaviour the PR introduces and the system it is introduced into before reading the
diff. The reviewer decides whether the PR is right. This skill only gives them the
picture. It changes nothing in the repository or on the PR.

## Inputs

- A pull request number or URL. Without one, ask for it and stop.
- The PR itself: `gh pr view <n> --json title,body,baseRefName,headRefName,files`,
  then its diff against its **own base branch**
  (`git diff origin/<base>...origin/<head>`). A stacked PR's base is the parent
  PR's branch, not the repository default branch.
- The stack: `gh pr list --state open --json number,title,baseRefName,headRefName`.
  Read the default branch with
  `gh repo view --json defaultBranchRef --jq .defaultBranchRef.name`.
  Follow base branches down to that branch and head branches up, to learn what
  the PR builds on and which later PR first uses it.
- The design: the Linear ticket the PR names and any architecture or feature map it
  links. A map may live on an unmerged branch. Fetch that branch and read it there.
- The PR's test names. They list the behaviours the author thinks matter.

## Non-negotiables

- **No review.** No verdict, findings or suggestions. Where the PR and a design
  document word one rule differently, show both wordings and judge neither.
- **No code.** No function, class, module or file names, and no walkthrough of the
  diff. Describe behaviour in the reader's words. Name a table or a contract only
  when the reviewer will meet that name in the PR.
- **Two pictures.** Always show the system around the PR as well as the PR. A canvas
  with only the PR is a diff summary.
- **Cite what you read.** Every chart and table names its source. Leave out any
  fact you did not read this session.

## Workflow

### 1. Pick the charts

Draw only the rows the PR needs.

| The PR has                                                | Draw                   | Shows                                                       | Source                        |
| --------------------------------------------------------- | ---------------------- | ----------------------------------------------------------- | ----------------------------- |
| Any stateful behaviour                                    | System flow            | One end-to-end run, with the steps this PR touches outlined | Design documents              |
| Behaviour that depends on a lifecycle that already exists | Existing state machine | That lifecycle as it already is, one chart each             | Design documents, base branch |
| A new thing that has a life                               | New state machine      | Every state it can be in and every event that moves it      | The PR                        |
| A new question with several outcomes                      | Decision flow          | The questions in order, each ending in an outcome           | The PR                        |

### 2. Get the states and arrows right

For each **new** state machine, check whether a skill named `statechart` is available.

- **Available.** Follow it. Model the behaviour, write the rules the PR promises as
  invariants, and label states and steps in the reader's words. Take the canvas
  chart's states and arrows from its output. A rule that breaks in the model is a
  finding, so keep it out of the canvas and report it in the reply as that skill's
  hand-off describes.
- **Not available.** List every state the thing can be in, then for each state every
  event that can happen to it, including the passive ones (time passing, a crash,
  another actor moving first). A state with no arrow in or no arrow out is an end
  state or a gap in your reading. Find out which.

Draw existing state machines from the design documents without modelling them.

### 3. Draw the canvas

Read the `canvas` skill. Paste
[`references/state-chart.tsx`](references/state-chart.tsx) into the canvas. A canvas
is one file, so this component cannot be imported. Merge its `cursor/canvas` import
into the canvas file's own import. Give each `StateChart` a unique `id`, a `width`
and `height` for its viewBox, and its nodes and edges. Layout is by hand:

- A node has a top-left corner (`x`, `y`), a size (`w`, `h`), a `title` and optional
  `sub` lines. A line fits about one character per 6 px of width.
- A node's `kind` is `state` by default, `accent` for what the PR adds, `decision`
  for a question, or `terminal` for an outcome.
- An edge names the side it leaves (`fromSide`) and the side it enters (`toSide`):
  `t`, `b`, `l` or `r`. `fromOff` and `toOff` shift the anchor along that side, to
  separate two edges between the same nodes.
- `bend` sets how far a curve bulges. Set it when an edge leaves and enters on the
  same side. `labelT` (0 to 1), `labelDx` and `labelDy` move the label.
- `dashed` marks a passive transition.

- About 20 arrows a chart at most. Past that, merge states the reader need not tell
  apart, or split the chart.
- Leave everything the PR does not add neutral, so the accent outline shows the PR
  against its surroundings. Say under the chart what the outline and the dashes mean.
- Check each chart's coordinates for overlapping labels before writing the canvas.

Order the canvas top to bottom:

1. A title and a link to the PR.
2. One callout with the single idea the reviewer must hold.
3. The system the PR lands in.
4. The existing state machines it depends on.
5. What the PR introduces.
6. The tables that apply: what blocks what, how each failure surfaces and how far it
   reaches, what a crash at each point leaves behind and what recovers it, where the
   PR sits in its stack, a vocabulary of the canvas's terms, and the design pages to
   hold the PR against.
7. The sources read.

Without the canvas tool, give the same charts as Mermaid `stateDiagram-v2` and
`flowchart` blocks, and the same tables in Markdown.

### 4. Reply

- Link the canvas and say its layout is unchecked, since you cannot see it.
- List what it contains in a few bullets and name the sources read.
- Name anything included that sits close to the review line, so the user can ask
  for it to be removed.
- With `statechart`, add its Mermaid text and any rule that broke.

## Stop conditions

- No PR was given. Ask for it and stop.
- The PR has no state (a rename, a dependency bump, a pure refactor). Say this skill
  does not fit and stop.
- The PR links no design and its description does not say what system it lands in.
  Ask where the surrounding design is written down before drawing that half.

## Verification

Test case: run the skill on an open PR that adds a lifecycle to an existing system.
It passes when all of these hold:

- The canvas writer accepts the canvas, or the Mermaid fallback renders.
- The canvas has at least one chart of the surrounding system and one of what the
  PR introduces.
- No function, class, module or file name appears, and nothing reads as a verdict.
- Every chart and table names a source that was read in the session.
- Each new state machine's states all have an arrow in, and an arrow out unless
  they are end states.
