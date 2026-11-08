import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Diagram } from '../types'

const PANE = 'mermaid'
const KEEP = 50
const SVG_LIMIT = 131072
const PNG_BYTES_LIMIT = 2 * 1024 * 1024
const MMDC = ['npx', '-y', '@mermaid-js/mermaid-cli@11.12.0', '-q']
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
// Labels as plain SVG text: the desktop's SVG scrub drops foreignObject,
// which is where HTML labels would go.
const MERMAID_CONFIG = JSON.stringify({
  htmlLabels: false,
  flowchart: { htmlLabels: false },
  state: { htmlLabels: false },
})
const EMPTY =
  "No Mermaid diagrams yet. Claude's next mermaid code block will show here."

const diagrams = atom(
  { plugin: 'mermaid-pane', key: 'diagrams' } as const,
  [] as Diagram[],
  { shape: 'diagrams-1' },
)
const selected = atom(
  { plugin: 'mermaid-pane', key: 'selected' } as const,
  null as string | null,
  { shape: 'selected-1' },
)

const fencedMermaid = (text: string) =>
  [...text.replace(/\r\n/g, '\n').matchAll(/^```mermaid[ \t]*\n([\s\S]*?)\n```/gm)].map(
    match => match[1] ?? '',
  )

const hashOf = async (source: string) => {
  const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(source))

  return Array.from(new Uint8Array(digest), byte => byte.toString(16).padStart(2, '0'))
    .join('')
    .slice(0, 16)
}

const pngSize = (base64: string) => {
  const head = atob(base64.slice(0, 32))
  const uint32 = (at: number) =>
    ((head.charCodeAt(at) << 24) |
      (head.charCodeAt(at + 1) << 16) |
      (head.charCodeAt(at + 2) << 8) |
      head.charCodeAt(at + 3)) >>>
    0

  return { width: uint32(16), height: uint32(20) }
}

const altOf = (source: string) => {
  const title = /^---\n[\s\S]*?^title:\s*(.+)$[\s\S]*?^---$/m.exec(source)?.[1]?.trim()
  if (title === undefined) return 'Mermaid diagram'

  return title.startsWith('"') ? String(JSON.parse(title)) : title
}

const put = ($: EngineInterface, diagram: Diagram) =>
  update($, diagrams, list =>
    [...list.filter(one => one.id !== diagram.id), diagram].slice(-KEEP),
  )

const settle = ($: EngineInterface, diagram: Diagram) =>
  update($, diagrams, list =>
    list.map(one => (one.id === diagram.id ? diagram : one)),
  )

const mmdcArgs = async ($: EngineInterface, dir: string) => {
  const mermaidConfig = `${dir}/mermaid-config.json`
  await $.fs.write(mermaidConfig, MERMAID_CONFIG)
  if (!(await $.fs.exists(CHROME))) return [...MMDC, '-c', mermaidConfig, '-i', '-']
  const puppeteerConfig = `${dir}/puppeteer-config.json`
  await $.fs.write(puppeteerConfig, JSON.stringify({ executablePath: CHROME }))

  return [...MMDC, '-p', puppeteerConfig, '-c', mermaidConfig, '-i', '-']
}

const lastLines = (text: string) => text.trim().split('\n').slice(-10).join('\n')

const renderDiagram = async ($: EngineInterface, id: string, source: string) => {
  try {
    const dir = `${await $.env.get('HOME')}/.cache/mermaid-pane`
    const svgPath = `${dir}/${id}.svg`
    const pngPath = `${dir}/${id}.png`
    const cached = await Promise.all([$.fs.exists(svgPath), $.fs.exists(pngPath)])
    if (!cached.every(Boolean)) {
      const args = await mmdcArgs($, dir)
      const runs = await Promise.all(
        [['-o', svgPath], ['-o', pngPath, '-s', '2', '-b', 'white']].map(out =>
          $.process.run([...args, ...out], {
            stdin: source,
            timeoutMs: 180000,
            env: { PUPPETEER_SKIP_DOWNLOAD: '1' },
          }),
        ),
      )
      const failed = runs.find(run => run.exitCode !== 0)
      if (failed) {
        const error = lastLines(failed.stderr) || `mmdc exited ${failed.exitCode}`
        await settle($, { id, source, status: 'failed', error })

        return
      }
    }
    const { base64 } = await $.fs.read(pngPath, { as: 'bytes' })
    await settle($, { id, source, status: 'ready', svgPath, pngPath, ...pngSize(base64) })
  } catch (error) {
    await settle($, { id, source, status: 'failed', error: String(error) })
  }
}

const fit = (width: number, height: number, cols: number, bodyRows: number) => {
  const room = Math.max(4, bodyRows - 2)
  const clamp = (n: number) => Math.min(255, Math.max(1, Math.round(n)))
  const rows = (cols * height) / width / 2
  if (rows <= room) return { columns: clamp(cols), rows: clamp(rows) }

  return { columns: clamp((room * 2 * width) / height), rows: clamp(room) }
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'mermaid',
      description: 'Show Mermaid diagrams from this session in a pane',
    })

    return next(e)
  })

  on('command.run', { command: 'mermaid' }, async $ => {
    await $.ui.open({ id: PANE, title: 'Mermaid' })

    return { text: 'Mermaid pane opened.' }
  })

  on('session.append', { door: 'response' }, async ($, e, next) => {
    const stored = await next(e)
    if (e.agentId !== undefined) return stored
    const sources = e.message.content.flatMap(block =>
      block.type === 'text' && typeof block.text === 'string' ? fencedMermaid(block.text) : [],
    )
    for (const source of sources) {
      const id = await hashOf(source)
      const known = (await read($, diagrams)).find(one => one.id === id)
      await put($, known?.status === 'ready' ? known : { id, source, status: 'rendering' })
      await update($, selected, () => null)
      void $.ui.open({ id: PANE, title: 'Mermaid' })
      // Not awaited: the conversation must never wait on a headless Chrome.
      if (known?.status !== 'ready') void renderDiagram($, id, source)
    }

    return stored
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text, Button, Code } = $.ui.resolve(e)
    const list = await read($, diagrams)
    const chosen = await read($, selected)
    if (list.length === 0) return <Text dimColor>{EMPTY}</Text>

    const found = list.findIndex(one => one.id === chosen)
    const at = found === -1 ? list.length - 1 : found
    const diagram = list[at] as Diagram
    const go = (to: number) => () =>
      update($, selected, () => (to >= list.length - 1 ? null : (list[to]?.id ?? null)))

    const header = (
      <Box flexDirection="row" gap={1}>
        <Text>
          Diagram {at + 1} of {list.length}
        </Text>
        {at > 0 && (
          <Button key="prev" hotkey="p" onPress={go(at - 1)}>
            ‹ Prev
          </Button>
        )}
        {at < list.length - 1 && (
          <Button key="next" hotkey="n" onPress={go(at + 1)}>
            Next ›
          </Button>
        )}
        {at < list.length - 1 && (
          <Button key="latest" hotkey="l" onPress={go(list.length - 1)}>
            Latest
          </Button>
        )}
      </Box>
    )

    const body = await (async () => {
      if (diagram.status === 'rendering') return <Text dimColor>Rendering…</Text>
      if (diagram.status === 'failed') {
        return (
          <Box flexDirection="column">
            <Text color="error">{diagram.error}</Text>
            <Code language="mermaid" source={diagram.source} />
          </Box>
        )
      }
      const alt = altOf(diagram.source)
      if (e.surface === 'terminal') {
        const { Image } = $.ui.resolve(e)
        const size = fit(
          diagram.width,
          diagram.height,
          e.props.bodyColumns,
          e.props.scroll.bodyRows,
        )

        const { base64 } = await $.fs.read(diagram.pngPath, { as: 'bytes' })
        // iTerm2 draws only bytes; a file source shows the alt there. Bytes
        // stop at 2 MiB, past which kitty and Ghostty can still read the file.
        const source =
          base64.length * 0.75 <= PNG_BYTES_LIMIT
            ? { png: base64 }
            : { file: diagram.pngPath, format: 'png' as const }

        return <Image source={source} alt={alt} {...size} />
      }
      const { Svg } = $.ui.resolve(e)
      const svg = await $.fs.read(diagram.svgPath)
      if (svg.length > SVG_LIMIT) {
        return (
          <Text dimColor>
            Diagram too large to draw here ({svg.length} characters, limit {SVG_LIMIT}). Open{' '}
            {diagram.svgPath}.
          </Text>
        )
      }

      return <Svg source={svg} alt={alt} />
    })()

    return (
      <Box flexDirection="column" gap={1}>
        {header}
        {body}
      </Box>
    )
  })
}
