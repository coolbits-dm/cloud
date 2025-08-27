// lib/cb/events.ts
// Tiny wrapper peste window events cu namespace "cb:*"

export type CbEventName =
  | 'cb:basic-briefing'
  | 'cb:deep-analysis-started'
  | 'cb:ecosystem-summary'
  // extensibil:
  | `cb:ecosystem:${string}:${string}`
  | `cb:${string}`

export function emit<T = any>(name: CbEventName | string, detail?: T) {
  if (typeof window === 'undefined') return
  const ev = new CustomEvent(name, { detail })
  window.dispatchEvent(ev)
}

export function on<T = any>(name: CbEventName | string, handler: (e: CustomEvent<T>) => void) {
  if (typeof window === 'undefined') return () => {}
  const h = handler as EventListener
  window.addEventListener(name, h)
  return () => window.removeEventListener(name, h)
}

// sugar helpers
export const CB = {
  basicBriefing() { emit('cb:basic-briefing') },
  deepAnalysisStarted(payload: any) { emit('cb:deep-analysis-started', payload) },
  ecosystemSummary(payload: { channel: string; summary: any }) { emit('cb:ecosystem-summary', payload) },
}
