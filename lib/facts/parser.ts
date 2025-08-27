import aliases from '@/data/mapping/aliases_v0.1.json'
import type { PartialFacts, Money, Currency } from './types'

type AliasEntry = { category: 'objectives'|'channels'|'tools'|'tracking'; canonical: string }
const aliasMap: Record<string, AliasEntry> = aliases as any

const esc = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
const normalizeDomain = (raw: string) =>
  raw.trim().replace(/^https?:\/\//i, '').replace(/^www\./i, '').replace(/[\/#?].*$/, '').toLowerCase()

function parseCurrencyToken(tok?: string | null): Currency | undefined {
  if (!tok) return undefined
  const t = tok.toLowerCase()
  if (t.includes('€') || t.includes('eur') ) return 'EUR'
  if (t.includes('$') || t.includes('usd') ) return 'USD'
  if (t.includes('ron') || t.includes('lei')) return 'RON'
  return undefined
}
function parseMoney(text: string): Money | undefined {
  const m = text.match(/(\d[\d\.,]*)\s*(eur|usd|ron|lei|€|\$)?/i)
  if (!m) return
  const num = Number(String(m[1]).replace(/[^\d.]/g, ''))
  if (!isFinite(num)) return
  const cur = parseCurrencyToken(m[2]) ?? 'EUR'
  return { amount: num, currency: cur }
}
function splitCSV(s: string) {
  return s.split(/[;,]| and |&/i).map(x => x.trim()).filter(Boolean)
}

export function parseFactsFromMessage(message: string): PartialFacts {
  const out: PartialFacts = {}
  const lower = message.toLowerCase()

  // competitors capture (kept from your version)
  let toScanForSite = message
  {
    const i = lower.indexOf('competit')
    if (i !== -1) {
      const tail = message.slice(i)
      let list = tail
      const colon = tail.indexOf(':')
      const sunt  = tail.toLowerCase().indexOf('sunt')
      if (colon !== -1 && (sunt === -1 || colon < sunt)) list = tail.slice(colon + 1)
      else if (sunt !== -1) list = tail.slice(sunt + 4)
      list = list.trim().replace(/[)!.?]*$/, '')
      if (list) {
        const parts = list.split(/,| și | si | and /i).map(s => s.trim()).filter(Boolean)
        if (parts.length) out.competitors = parts
      }
      toScanForSite = message.slice(0, i)
    }
  }

  // website / domain
  {
    let site: string | null = null
    const m1 = toScanForSite.match(/(?:site-?ul|website-?ul)\s+(?:este|e|se\s+nume[sș]te)\s+([^,.;\n]+)/i)
    if (m1) site = m1[1]
    const dm = toScanForSite.match(/(?:https?:\/\/)?(?:www\.)?([A-Za-z0-9][A-Za-z0-9-]+\.[A-Za-z]{2,}(?:\.[A-Za-z]{2,})?)/)
    if (dm) site = dm[1]
    if (site) out.website = normalizeDomain(site)
  }

  // business / brand name
  {
    const m =
      message.match(/(?:numele|nume|brandul|firma|compania)\s+(?:este|e|se\s+nume[sș]te)\s+([^,.;\n]+)/i) ||
      message.match(/brand name is\s+([^,.;\n]+)/i)
    if (m) out.businessName = m[1].trim().replace(/[)!.?]*$/, '')
  }

  // industry
  {
    const m =
      message.match(/(?:industrie|domeniu(?:l)?(?:\s+de\s+activitate)?)\s*(?:este|e|:)?\s+([^,.;\n]+)/i) ||
      message.match(/we\s+are\s+in\s+the\s+([^,.;\n]+)\s+industry/i)
    if (m) out.industry = m[1].trim().replace(/[)!.?]*$/, '')
  }

  // employees
  {
    const m =
      message.match(/(?:avem|are)\s+(\d{1,6})\s+(?:angajați|angajati|employees?)/i) ||
      message.match(/(\d{1,6})\s+(?:angajați|angajati|employees?)/i) ||
      message.match(/(\d{1,6})-(\d{1,6})\s+(?:angajați|angajati|employees?)/i)
    if (m) out.employees = m[2] ? `${m[1]}-${m[2]}` : parseInt(m[1], 10)
  }

  // alias matches (objectives/channels/tools/tracking)
  {
    const found = { objectives: new Set<string>(), channels: new Set<string>(), tools: new Set<string>(), tracking: new Set<string>() }
    for (const key in aliasMap) {
      const entry = aliasMap[key]
      if (new RegExp(`\\b${esc(key)}\\b`, 'i').test(lower)) {
        ;(found as any)[entry.category].add(entry.canonical)
      }
    }
    if (found.objectives.size) out.objectives = Array.from(found.objectives)
    if (found.channels.size)   out.channels   = Array.from(found.channels)
    if (found.tools.size)      out.tools      = Array.from(found.tools)
    if (found.tracking.size)   out.tracking   = Array.from(found.tracking)
  }

  // ---------- Channel specifics (first wave) ----------

  // Google Ads monthly budget
  {
    const m = lower.match(/google\s+ads?.{0,20}monthly\s+budget\s+(?:is|=|:)?\s*([\d\.,]+\s*(?:eur|usd|ron|lei|€|\$)?)/i)
      || lower.match(/buget(?:ul)?\s+lunar\s+(?:pe|la)\s+google\s+ads?.{0,15}([\d\.,]+\s*(?:eur|usd|ron|lei|€|\$)?)/i)
    if (m) {
      const money = parseMoney(m[1])
      if (money) out.googleAds = { ...(out.googleAds || {}), monthlyBudget: money }
      out.channels = uniqMerge(out.channels, ['Google Ads'])
    }
  }

  // Google Ads campaign types
  {
    const m = lower.match(/google\s+ads?\s+campaign\s+types?\s*[:=]\s*([a-z ,\-]+)/i)
    if (m) {
      const list = splitCSV(m[1]).map(x => {
        const t = x.toLowerCase()
        if (/pmax|performance\s*max/.test(t)) return 'PMax'
        if (/search/.test(t)) return 'Search'
        if (/youtube|video/.test(t)) return 'YouTube'
        if (/display|gdn/.test(t)) return 'Display'
        if (/shopping|p\s*max\s*shopping|gmc/.test(t)) return 'Shopping'
        return x
      })
      if (list.length) out.googleAds = { ...(out.googleAds || {}), campaignTypes: list }
      out.channels = uniqMerge(out.channels, ['Google Ads'])
    }
  }

  // (Scaffold) Meta/TikTok/LinkedIn budgets — same phrase style
  const channelRegexes: Array<{ key: keyof PartialFacts, label: string, rx: RegExp }> = [
    { key: 'metaAds',    label: 'Meta Ads',    rx: /meta\s+ads?.{0,20}monthly\s+budget\s+(?:is|=|:)?\s*([\d\.,]+\s*(?:eur|usd|ron|lei|€|\$)?)/i },
    { key: 'tiktokAds',  label: 'TikTok Ads',  rx: /tiktok\s+ads?.{0,20}monthly\s+budget\s+(?:is|=|:)?\s*([\d\.,]+\s*(?:eur|usd|ron|lei|€|\$)?)/i },
    { key: 'linkedinAds',label: 'LinkedIn Ads',rx: /linkedin\s+ads?.{0,20}monthly\s+budget\s+(?:is|=|:)?\s*([\d\.,]+\s*(?:eur|usd|ron|lei|€|\$)?)/i },
    { key: 'amazonAds',  label: 'Amazon Ads',  rx: /amazon\s+ads?.{0,20}monthly\s+budget\s+(?:is|=|:)?\s*([\d\.,]+\s*(?:eur|usd|ron|lei|€|\$)?)/i },
    { key: 'bingAds',    label: 'Bing Ads',    rx: /bing\s+ads?.{0,20}monthly\s+budget\s+(?:is|=|:)?\s*([\d\.,]+\s*(?:eur|usd|ron|lei|€|\$)?)/i },
    { key: 'xAds',       label: 'X Ads',       rx: /\b(x|twitter)\s+ads?.{0,20}monthly\s+budget\s+(?:is|=|:)?\s*([\d\.,]+\s*(?:eur|usd|ron|lei|€|\$)?)/i },
  ]
  for (const c of channelRegexes) {
    const m = lower.match(c.rx)
    if (m) {
      const money = parseMoney(m[1] ?? m[2])
      if (money) (out as any)[c.key] = { ...((out as any)[c.key] || {}), monthlyBudget: money }
      out.channels = uniqMerge(out.channels, [c.label])
    }
  }

  return out
}

export function parseMessageToFacts(message: string): PartialFacts {
  return parseFactsFromMessage(message)
}

export default parseFactsFromMessage
