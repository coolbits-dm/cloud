// lib/cb/cbml.ts
// cbML v0.1 — parser + executor minimal (JSON sau ```cbml ... ```)

import { CB, emit } from './events'

export type CbmlAction =
  | { do: 'briefing.generate'; with?: { level?: 'basic' | 'deep' } }
  | { do: 'analysis.deep'; with?: { engine?: 'kim' | 'auto' } }
  | { do: 'ecosystem.sync'; with: { channel: string; summary: Record<string, any> } }
  | { do: 'channel.connect'; with: { name: 'google_ads' | 'meta_ads' | 'tiktok_ads' | 'linkedin_ads' | 'x_ads' | 'seo' | 'email' | 'referral'; navigate?: boolean } }
  | { do: 'channel.assess'; with?: { name: string; depth?: 'basic' | 'deep' } }
  | { do: string; with?: Record<string, any> } // extensibil

export type CbmlPlan = {
  version?: string
  context?: Record<string, any>
  plan: CbmlAction[]
}

export type CbmlResult = {
  ok: boolean
  steps: Array<{ action: string; status: 'ok' | 'error'; info?: any }>
}

export function isCbmlBlock(input: string): boolean {
  return /```cbml([\s\S]*?)```/i.test(input.trim()) || input.trim().startsWith('{')
}

export function extractCbmlPayload(input: string): string {
  const m = input.match(/```cbml([\s\S]*?)```/i)
  if (m) return m[1].trim()
  // fallback: tot mesajul
  return input.trim()
}

function safeParseJSON(s: string): any {
  try { return JSON.parse(s) } catch { return null }
}

export async function runCbml(raw: string): Promise<CbmlResult> {
  // 1) parse
  const src = extractCbmlPayload(raw)
  const obj = safeParseJSON(src)
  if (!obj || !Array.isArray(obj.plan)) {
    return { ok: false, steps: [{ action: 'parse', status: 'error', info: 'Invalid cbML JSON. Expect {"plan":[...]}' }] }
  }
  const plan: CbmlPlan = obj

  // 2) execute
  const steps: CbmlResult['steps'] = []
  for (const act of plan.plan) {
    const name = (act as any).do || 'unknown'
    try {
      // eslint-disable-next-line no-await-in-loop
      const info = await execAction(act as CbmlAction)
      steps.push({ action: name, status: 'ok', info })
    } catch (e: any) {
      steps.push({ action: name, status: 'error', info: String(e?.message || e) })
    }
  }
  return { ok: steps.every(s => s.status === 'ok'), steps }
}

async function execAction(a: CbmlAction) {
  switch (a.do) {
    case 'briefing.generate': {
      // declanșează briefingul basic din UI
      CB.basicBriefing()
      return { emitted: 'cb:basic-briefing', level: a.with?.level ?? 'basic' }
    }
    case 'analysis.deep': {
      // pornește jobul și anunță UI-ul
      const res = await fetch('/api/deep-analysis/start', { method: 'POST' })
      const json = await res.json().catch(() => ({}))
      CB.deepAnalysisStarted(json)
      return { started: true, engine: a.with?.engine ?? 'kim', job: json?.jobId ?? null }
    }
    case 'ecosystem.sync': {
      CB.ecosystemSummary({ channel: a.with.channel, summary: a.with.summary })
      return { emitted: 'cb:ecosystem-summary', channel: a.with.channel }
    }
    case 'channel.connect': {
      const ch = a.with.name
      if (ch === 'google_ads') {
        const navigate = a.with.navigate !== false
        if (navigate && typeof window !== 'undefined') {
          window.open('/api/google-ads/oauth/start', '_self')
        } else {
          emit('cb:ecosystem:google_ads:connect', { navigate })
        }
        return { channel: ch, navigate }
      }
      // alte canale — doar event deocamdată
      emit(`cb:ecosystem:${ch}:connect`, { navigate: a.with.navigate !== false })
      return { channel: ch, navigate: a.with.navigate !== false }
    }
    case 'channel.assess': {
      // pentru acum mapez "basic" la briefing
      if (a.with?.depth !== 'deep') CB.basicBriefing()
      else {
        const res = await fetch('/api/deep-analysis/start', { method: 'POST' })
        const json = await res.json().catch(() => ({}))
        CB.deepAnalysisStarted(json)
      }
      return { name: a.with?.name, depth: a.with?.depth ?? 'basic' }
    }
    default: {
      // extensibil: ridică un eveniment generic pentru handlers custom
      emit(`cb:${(a as any).do}`, a.with)
      return { forwarded: true, action: (a as any).do }
    }
  }
}
