// simple in-memory session store (per page lifecycle)
const store: Record<string, any> = {}

export function setEcosystemSummary(channel: string, patch: Record<string, any>) {
  store[channel] = { ...(store[channel] || {}), ...patch, updatedAt: new Date().toISOString() }
}

export function getAndClearEcosystemSummary(channel: string) {
  const v = store[channel]
  delete store[channel]
  return v || null
}
