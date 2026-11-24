import { expect, test } from 'claude-code/testing'

test('usage returns rateLimits unchanged', async ($, on) => {
  const limits = [
    { kind: 'five_hour', percentUsed: 23.5, resetsAt: '2026-11-23T18:00:00Z' },
    { kind: 'seven_day', percentUsed: 7, resetsAt: '2026-11-28T00:00:00Z' },
  ]
  on('session.usage', () => ({ value: { startedAt: 0, context: { size: 200000 }, rateLimits: limits } }) as never)
  const ran = await $.tool.call({ tool: 'mcp__s-stack-usage__usage' })
  expect(ran.result).toBe(JSON.stringify(limits))
})
