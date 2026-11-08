# mermaid-pane

Draws the Mermaid diagrams Claude writes as pictures in a pane beside the chat.

Whenever a reply contains a `mermaid` code block, the "Mermaid" pane opens and
shows the rendered diagram. `/statechart` charts keep their colour marks.
`/mermaid` reopens the pane. Prev, Next and Latest (hotkeys `p`, `n`, `l`) step
through the session's earlier diagrams.

## Install

At the prompt of a Claude Code terminal session:

```text
/plugin install mermaid-pane --marketplace Samuel-Harris/foundry
```

From a shell:

```bash
claude plugin install mermaid-pane --marketplace Samuel-Harris/foundry
```

## Develop

From this folder, `claude plugin validate .` checks the manifest and the hooks
module, and `claude plugin test .` runs `hooks/register.test.tsx`. From the
repository root, `claude --plugin-dir mods/mermaid-pane` starts a session with
the mod loaded from source.

## Requirements

- Node.js with `npx`. The first render downloads `@mermaid-js/mermaid-cli`
  11.12.0.
- Google Chrome at `/Applications/Google Chrome.app` (macOS). Without it,
  puppeteer looks for its own browser, which is not downloaded.
- In the terminal, a terminal that draws images: kitty, Ghostty, or iTerm2 3.5
  or later with Claude Code's fullscreen rendering. Elsewhere the pane shows
  the diagram's title as text. The desktop app, VS Code and mobile draw the SVG.

Rendered files are cached in `~/.cache/mermaid-pane/`, named by a hash of the
diagram source.
