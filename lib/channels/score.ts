// lib/channels/score.ts
import type { Facts } from '@/lib/facts/types'

export type ChannelKey =
  | 'google_ads'
  | 'meta_ads'
  | 'tiktok_ads'
  | 'linkedin_ads'
  | 'x_ads'
  | 'seo'
  | 'email'
  | 'referral'
  | 'ai_optimization'

export const CHANNEL_LABELS: Record<ChannelKey, string> = {
  google_ads: 'Google Ads',
  meta_ads: 'Meta Ads',
  tiktok_ads: 'TikTok Ads',
  linkedin_ads: 'LinkedIn Ads',
  x_ads: 'X Ads',
  seo: 'Organic (SEO)',
  email: 'Email',
  referral: 'Referral',
  ai_optimization: 'AI Optimization',
}

// label → key (basic, case-insensitive)
const LABEL_TO_KEY: Record<string, ChannelKey> = Object.fromEntries(
  (Object.keys(CHANNEL_LABELS) as ChannelKey[]).map(k => [CHANNEL_LABELS[k].toLowerCase(), k])
)

function presentScore(obj: any, fields: string[]): { present: number; total: number } {
  if (!obj) return { present: 0, total: fields.length }
  let p = 0
  for (const f of fields) {
    const v = obj?.[f]
    const ok =
      typeof v === 'number' ||
      typeof v === 'boolean' ||
      (typeof v === 'string' && v.trim().length > 0) ||
      (Array.isArray(v) && v.length > 0) ||
      (v && typeof v === 'object' && Object.keys(v).length > 0)
    if (ok) p++
  }
  return { present: p, total: fields.length }
}

const DEF: Record<ChannelKey, string[]> = {
  google_ads:   ['runSince','monthlyBudget','locations','conversions','campaignTypes','audiences'],
  meta_ads:     ['runSince','monthlyBudget','locations','conversions','campaignTypes','audiences','pixel'],
  tiktok_ads:   ['runSince','monthlyBudget','locations','conversions','campaignTypes','audiences','pixel'],
  linkedin_ads: ['runSince','monthlyBudget','locations','conversions','campaignTypes','audiences'],
  x_ads:        ['runSince','monthlyBudget','locations','conversions','campaignTypes','audiences'],
  seo:          ['runSince','focus','keywords'],
  email:        ['providers','monthlyBudget','audiences','conversions'],
  referral:     [],  // completion is driven by selection only
  ai_optimization: [], // idem
}

const clampPct = (x: number) => Math.max(0, Math.min(100, Math.round(x)))

/** Was the channel explicitly picked in the onboarding “meeting journey”? */
export function selectedInWizard(facts: Facts, key: ChannelKey): boolean {
  const lbl = CHANNEL_LABELS[key].toLowerCase()
  return Array.isArray(facts.channels) && facts.channels.some(c => c.toLowerCase().trim() === lbl)
}

function toPct(obj: any, fields: string[]) {
  const { present, total } = presentScore(obj, fields)
  if (total === 0) return present > 0 ? 100 : 0
  return clampPct((present / total) * 100)
}

export function getChannelCompletion(facts: Facts, key: ChannelKey): number {
  let pct = 0
  switch (key) {
    case 'google_ads':   pct = toPct(facts.googleAds, DEF.google_ads); break
    case 'meta_ads':     pct = toPct(facts.metaAds, DEF.meta_ads); break
    case 'tiktok_ads':   pct = toPct(facts.tiktokAds, DEF.tiktok_ads); break
    case 'linkedin_ads': pct = toPct(facts.linkedinAds, DEF.linkedin_ads); break
    case 'x_ads':        pct = toPct(facts.xAds, DEF.x_ads); break
    case 'seo':          pct = toPct(facts.seo, DEF.seo); break
    case 'email':        pct = toPct(facts.email, DEF.email); break
    case 'referral':
    case 'ai_optimization':
      pct = 0
      break
  }
  // Floor to 30% when the user selected the channel in the onboarding.
  if (selectedInWizard(facts, key) && pct < 30) pct = 30
  return clampPct(pct)
}

/** Active = either selected in wizard OR has any channel-specific object present */
export function deriveActiveChannels(facts: Facts): Set<ChannelKey> {
  const active = new Set<ChannelKey>()
  // wizard selection
  for (const raw of (facts.channels || [])) {
    const k = LABEL_TO_KEY[raw.toLowerCase().trim()]
    if (k) active.add(k)
  }
  // presence of channel-specific data
  if (facts.googleAds)   active.add('google_ads')
  if (facts.metaAds)     active.add('meta_ads')
  if (facts.tiktokAds)   active.add('tiktok_ads')
  if (facts.linkedinAds) active.add('linkedin_ads')
  if (facts.xAds)        active.add('x_ads')
  if (facts.seo)         active.add('seo')
  if (facts.email)       active.add('email')
  return active
}
