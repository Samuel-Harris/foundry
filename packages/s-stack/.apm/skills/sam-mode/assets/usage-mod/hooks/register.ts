import type { Register } from 'claude-code'

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.tool.register({
      name: 'usage',
      description:
        "Returns the account's plan usage windows as JSON: a list of { kind, percentUsed, resetsAt }. An empty list means the figures are unknown.",
      inputSchema: { type: 'object', properties: {} },
      isDeferred: false,
    })
    return next(e)
  })

  on('tool.run', { tool: 'mcp__s-stack-usage__usage' }, async $ => ({
    result: JSON.stringify((await $.session.usage()).rateLimits),
  }))
}
