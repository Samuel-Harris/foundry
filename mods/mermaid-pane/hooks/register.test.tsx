import { expect, mock, test } from 'claude-code/testing'
import type { On } from 'claude-code'

const SURFACES = ['terminal', 'desktop', 'vscode', 'mobile'] as const

const PANE = {
  plugin: 'mermaid-pane',
  component: 'Pane',
  requestId: 'mermaid',
  props: {
    title: 'Mermaid',
    isFocused: false,
    bodyColumns: 60,
    placement: 'dock',
    scroll: { offset: 0, bodyRows: 30 },
    view: {},
  },
} as const

const SVG = '<svg xmlns="http://www.w3.org/2000/svg"><text>Idle</text></svg>'

const pngHead = (width: number, height: number) => {
  const uint32 = (n: number) => [n >>> 24, (n >>> 16) & 255, (n >>> 8) & 255, n & 255]
  const bytes = [
    137, 80, 78, 71, 13, 10, 26, 10, ...uint32(13), 73, 72, 68, 82,
    ...uint32(width), ...uint32(height), 8, 2, 0, 0, 0, ...uint32(0),
  ]

  return btoa(String.fromCharCode(...bytes))
}

// Rendering runs unawaited after the append, so a drawing settles a few
// dispatches later.
const settled = async (ui: { find: (q: { type: string; text: RegExp }) => Promise<unknown> }) => {
  for (let tries = 0; tries < 100; tries++) {
    if (!(await ui.find({ type: 'Text', text: /^Rendering/ }))) return
  }
  throw new Error('still rendering')
}

const chart = (body: string) => `Here is the chart.\n\n\`\`\`mermaid\n${body}\n\`\`\`\n`

const engine = (on: On, mmdc: { exitCode: number; stderr: string }) => {
  const argvs: string[][] = []
  mock.env(on, { HOME: '/Users/t' })
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('fs.exists', () => ({ value: false }))
  on('fs.write', () => ({ value: undefined }))
  on('fs.read', (_, e) => ({
    value: e.as === 'bytes' ? { base64: pngHead(800, 400) } : SVG,
  }))
  on('process.run', (_, e) => {
    argvs.push([...e.argv])

    return {
      value: { ...mmdc, stdout: '', isStdoutTruncated: false, isStderrTruncated: false },
    }
  })

  return argvs
}

const respond = (text: string, agentId?: string) => ({
  door: 'response' as const,
  origin: { kind: 'model' as const, model: 'claude' },
  uuid: crypto.randomUUID(),
  message: {
    type: 'assistant' as const,
    role: 'assistant' as const,
    content: [{ type: 'text', text }],
  },
  ...(agentId === undefined ? {} : { agentId }),
})

test('a mermaid block in a response shows as a picture, on every surface', async ($, on) => {
  const argvs = engine(on, { exitCode: 0, stderr: '' })

  await $.session.append(respond(chart('stateDiagram-v2\n  [*] --> Idle')))
  const first = await $.ui.mount({ ...PANE, surface: 'desktop' })
  await settled(first)
  await first.unmount()

  expect(argvs.map(argv => argv[argv.indexOf('-o') + 1])).toEqual([
    expect.stringMatching(/^\/Users\/t\/\.cache\/mermaid-pane\/[0-9a-f]{16}\.svg$/),
    expect.stringMatching(/^\/Users\/t\/\.cache\/mermaid-pane\/[0-9a-f]{16}\.png$/),
  ])
  for (const surface of SURFACES) {
    const ui = await $.ui.mount({ ...PANE, surface })
    await settled(ui)

    expect((await ui.find({ type: 'Text', text: /Diagram 1 of 1/ }))?.text).toBe(
      'Diagram 1 of 1',
    )
    if (surface === 'terminal') {
      const image = await ui.find({ type: 'Image' })
      // iTerm2 draws only bytes: a file source shows the alt there instead.
      expect(image?.props).toMatchObject({
        source: { png: pngHead(800, 400) },
        alt: 'Mermaid diagram',
        columns: 60,
        rows: 15,
      })
    } else {
      expect((await ui.find({ type: 'Svg' }))?.props).toMatchObject({ source: SVG })
    }
    await ui.unmount()
  }
})

test('a failed render shows the error and the source', async ($, on) => {
  engine(on, { exitCode: 1, stderr: 'Error: Parse error on line 2\nExpecting STATE' })

  await $.session.append(respond(chart('stateDiagram-v2\n  [*] -->')))

  for (const surface of SURFACES) {
    const ui = await $.ui.mount({ ...PANE, surface })
    await settled(ui)

    expect((await ui.find({ type: 'Text', text: /Parse error/ }))?.text).toBe(
      'Error: Parse error on line 2\nExpecting STATE',
    )
    expect((await ui.find({ type: 'Code' }))?.props).toMatchObject({
      language: 'mermaid',
      source: 'stateDiagram-v2\n  [*] -->',
    })
    await ui.unmount()
  }
})

test('prev and next move between diagrams, and a new one snaps to the latest', async ($, on) => {
  engine(on, { exitCode: 0, stderr: '' })
  await $.session.append(respond(chart('graph TD\n  A --> B')))
  await $.session.append(respond(chart('graph TD\n  C --> D')))

  for (const [index, surface] of (['terminal', 'desktop'] as const).entries()) {
    const count = index + 2
    const ui = await $.ui.mount({ ...PANE, surface })
    await settled(ui)
    const position = async () => (await ui.find({ type: 'Text', text: /^Diagram/ }))?.text

    expect(await position()).toBe(`Diagram ${count} of ${count}`)
    expect(await ui.find({ key: 'next' })).toBeUndefined()

    await ui.press({ key: 'prev' })
    expect(await position()).toBe(`Diagram ${count - 1} of ${count}`)
    expect(await ui.find({ key: 'latest' })).toBeDefined()

    await ui.press({ key: 'next' })
    expect(await position()).toBe(`Diagram ${count} of ${count}`)

    await ui.press({ key: 'prev' })
    await $.session.append(respond(chart(`graph TD\n  ${surface} --> E`)))
    await settled(ui)
    expect(await position()).toBe(`Diagram ${count + 1} of ${count + 1}`)
    expect(await ui.find({ key: 'latest' })).toBeUndefined()
    await ui.unmount()
  }
})

test("a subagent's mermaid block adds nothing", async ($, on) => {
  const argvs = engine(on, { exitCode: 0, stderr: '' })

  await $.session.append(respond(chart('graph TD\n  A --> B'), 'a1'))

  expect(argvs).toEqual([])
  const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })
  expect((await ui.find({ type: 'Text' }))?.text).toMatch(/^No Mermaid diagrams yet/)
  await ui.unmount()
})
