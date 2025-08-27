// lib/usage/credits.ts
'use client'

type PriceKey =
  | 'briefing.basic'
  | 'analysis.deep'
  | 'google_ads.briefing'
  | 'file.upload.parse'
  | 'chat.message'

const PRICES: Record<PriceKey, number> = {
  'briefing.basic': 5,
  'analysis.deep': 50,
  'google_ads.briefing': 15,
  'file.upload.parse': 10,
  'chat.message': 1,
}

const KEY = 'cb_credits_balance_v1'

// init (free tier)
function initIfMissing() {
  if (typeof window === 'undefined') return
  if (localStorage.getItem(KEY) == null) {
    localStorage.setItem(KEY, String(200)) // ex: 200 credite start
  }
}

export function getBalance(): number {
  initIfMissing()
  const v = localStorage.getItem(KEY)
  return v ? parseInt(v, 10) || 0 : 0
}

export function setBalance(v: number) {
  localStorage.setItem(KEY, String(Math.max(0, v)))
  window.dispatchEvent(new CustomEvent('cb:credits-updated', { detail: { balance: getBalance() } }))
}

export function charge(kind: PriceKey): boolean {
  const price = PRICES[kind] ?? 0
  const bal = getBalance()
  if (bal < price) return false
  setBalance(bal - price)
  return true
}
