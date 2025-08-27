'use client'

import { useUsage } from '@/lib/billing/usage'

export default function TokenMeter() {
  // select primitives (no new objects => no warning)
  const tokens = useUsage((s) => s.totalTokens)
  const usd = useUsage((s) => s.totalUsd)

  return (
    <div className="text-[11px] text-gray-600">
      Tokens ~{Math.round(tokens)} • ${usd.toFixed(2)}
    </div>
  )
}
