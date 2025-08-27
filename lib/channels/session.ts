// lib/channels/session.ts
// In-memory snapshot per channel for the current page life

const _store: Record<string, any> = {}

export function setEcosystemSummary(channel: string, patch: Record<string, any>) {
  _store[channel] = { ...( _store[channel] || {} ), ...patch, updatedAt: new Date().toISOString() }
}

export function getAndClearEcosystemSummary(channel: string) {
  const v = _store[channel]
  delete _store[channel]
  return v || null
}

export function peekEcosystemSummary(channel: string) {
  return _store[channel] || null
}
