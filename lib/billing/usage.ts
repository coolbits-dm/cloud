'use client'

import { create } from 'zustand'

export type Provider = 'openai' | 'xai'

export type UsageEntry = {
  provider: Provider
  inTokens: number
  outTokens: number
  usd: number
  at: number
}

type UsageState = {
  entries: UsageEntry[]
  // running totals kept as primitives (stable snapshots)
  totalTokens: number
  totalUsd: number
  add: (provider: Provider, delta: { inTokens?: number; outTokens?: number; usd?: number }) => void
  reset: () => void
}

// very rough price hints — adjust to your models as needed
const PRICES_PER_1K: Record<Provider, { in: number; out: number }> = {
  openai: { in: 0.005, out: 0.015 },
  xai:    { in: 0.004, out: 0.012 },
}

function estimateUsd(provider: Provider, inTok = 0, outTok = 0) {
  const p = PRICES_PER_1K[provider]
  return (inTok / 1000) * p.in + (outTok / 1000) * p.out
}

export const useUsage = create<UsageState>()((set) => ({
  entries: [],
  totalTokens: 0,
  totalUsd: 0,
  add(provider, delta) {
    const inTokens = Math.max(0, Math.floor(delta.inTokens ?? 0))
    const outTokens = Math.max(0, Math.floor(delta.outTokens ?? 0))
    const usd = delta.usd ?? estimateUsd(provider, inTokens, outTokens)
    const tokens = inTokens + outTokens

    set((s) => ({
      entries: [
        ...s.entries,
        { provider, inTokens, outTokens, usd, at: Date.now() },
      ],
      totalTokens: s.totalTokens + tokens,
      totalUsd: s.totalUsd + usd,
    }))
  },
  reset() {
    set({ entries: [], totalTokens: 0, totalUsd: 0 })
  },
}))
