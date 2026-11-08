export type Diagram =
  | { id: string; source: string; status: 'rendering' }
  | {
      id: string
      source: string
      status: 'ready'
      svgPath: string
      pngPath: string
      width: number
      height: number
    }
  | { id: string; source: string; status: 'failed'; error: string }

declare module 'claude-code' {
  interface PluginState {
    'mermaid-pane': {
      diagrams: Shaped<Diagram[]>
      selected: Shaped<string | null>
    }
  }
}
