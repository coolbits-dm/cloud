// Builds a compact digest with all facts the assistant should know.
export function buildFactsDigest(state: any): string {
  if (!state) return ''

  const L: string[] = []

  // Company
  if (state.businessName) L.push(`business_name: ${state.businessName}`)
  if (state.website)      L.push(`website: ${state.website}`)
  if (state.industry)     L.push(`industry: ${state.industry}`)
  if (state.employees!=null) L.push(`employees: ${String(state.employees)}`)

  // High-level
  if (Array.isArray(state.objectives) && state.objectives.length) L.push(`objectives: ${state.objectives.join(', ')}`)
  if (Array.isArray(state.channels) && state.channels.length)     L.push(`channels: ${state.channels.join(', ')}`)
  if (Array.isArray(state.tools) && state.tools.length)           L.push(`tools: ${state.tools.join(', ')}`)
  if (state.trackingImplementation) L.push(`tracking_impl: ${state.trackingImplementation}`)

  // Contact
  if (state.contactName)  L.push(`contact.name: ${state.contactName}`)
  if (state.contactEmail) L.push(`contact.email: ${state.contactEmail}`)
  if (state.contactPhone) L.push(`contact.phone: ${state.contactPhone}`)

  // Competitors
  if (Array.isArray(state.competitors) && state.competitors.length) {
    L.push(`competitors: ${state.competitors.join(', ')}`)
  }

  // Helper for channels
  const ch = [
    ['google_ads','googleAds'],
    ['meta_ads','metaAds'],
    ['tiktok_ads','tiktokAds'],
    ['linkedin_ads','linkedinAds'],
    ['amazon_ads','amazonAds'],
    ['bing_ads','bingAds'],
    ['x_ads','xAds'],
    ['email','email'],
    ['seo','seo'],
  ] as const

  for (const [label, key] of ch) {
    const v = state[key]
    if (!v) continue
    const add = (k: string, val: any) => {
      if (val == null) return
      if (Array.isArray(val) && !val.length) return
      L.push(`${label}.${k}: ${Array.isArray(val) ? val.join(', ') : String(val)}`)
    }
    add('run_since', v.runSince)
    add('monthly_budget', v.monthlyBudget ? `${v.monthlyBudget.amount} ${v.monthlyBudget.currency}` : null)
    add('locations', v.locations)
    add('conversions', v.conversions)
    add('campaign_types', v.campaignTypes)
    add('audiences', v.audiences)
    add('pixel', typeof v.pixel === 'boolean' ? (v.pixel ? 'yes' : 'no') : null)
    if (key === 'email') {
      add('providers', v.providers)
    }
    if (key === 'seo') {
      add('focus', v.focus)
      add('keywords', v.keywords)
    }
  }

  return L.join('\n')
}
