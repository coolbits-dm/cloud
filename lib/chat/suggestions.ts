import type { QuickReplyGroup } from './quickTypes'
import type { Facts } from '@/lib/facts/types'

export function buildQuickReplies(facts: Facts, lastAssistantText?: string): QuickReplyGroup[] {
  const groups: QuickReplyGroup[] = []

  // 1) Website lipsă
  if (!facts.website) {
    groups.push({
      id: 'ask_website',
      title: 'What is your company website?',
      options: [],
      allowCustom: true,
      customPlaceholder: 'e.g., coolbits.ro'
    })
  }

  // 2) Canale lipsă
  if ((facts.channels?.length ?? 0) === 0) {
    groups.push({
      id: 'ask_channels',
      title: 'Which channels do you use?',
      multi: true,
      options: [
        { id: 'google_ads', label: 'Google Ads', payload: { type: 'channel', value: 'Google Ads' } },
        { id: 'meta_ads', label: 'Meta (Facebook/Instagram)', payload: { type: 'channel', value: 'Meta' } },
        { id: 'tiktok', label: 'TikTok', payload: { type: 'channel', value: 'TikTok' } },
        { id: 'linkedin', label: 'LinkedIn', payload: { type: 'channel', value: 'LinkedIn' } },
        { id: 'seo', label: 'SEO', payload: { type: 'channel', value: 'SEO' } },
        { id: 'email', label: 'Email', payload: { type: 'channel', value: 'Email' } }
      ],
      allowCustom: true,
      customPlaceholder: 'Add another channel…'
    })
  }

  // 3) Obiective lipsă
  if ((facts.objectives?.length ?? 0) === 0) {
    groups.push({
      id: 'ask_objectives',
      title: 'What are your primary marketing goals?',
      multi: true,
      options: [
        { id: 'leads', label: 'Leads', payload: { type: 'objective', value: 'Leads' } },
        { id: 'sales', label: 'Sales', payload: { type: 'objective', value: 'Sales' } },
        { id: 'traffic', label: 'Traffic', payload: { type: 'objective', value: 'Traffic' } },
        { id: 'awareness', label: 'Brand Awareness', payload: { type: 'objective', value: 'Brand Awareness' } },
        { id: 'engagement', label: 'Engagement', payload: { type: 'objective', value: 'Engagement' } }
      ],
      allowCustom: true,
      customPlaceholder: 'Add another goal…'
    })
  }

  const hasGoogleAds = facts.channels?.some(c => c.toLowerCase().includes('google'))
  if (hasGoogleAds) {
    // 4) Buget Google Ads (dacă lipsește)
    if (!facts.googleAds?.monthlyBudget) {
      groups.push({
        id: 'ask_googleads_budget',
        title: 'What is your monthly Google Ads budget?',
        options: [
          { id: '1-3k', label: '€1k–3k', payload: { type: 'ga_budget', value: { amount: 2000, currency: 'EUR' } } },
          { id: '3-10k', label: '€3k–10k', payload: { type: 'ga_budget', value: { amount: 5000, currency: 'EUR' } } },
          { id: '10-30k', label: '€10k–30k', payload: { type: 'ga_budget', value: { amount: 15000, currency: 'EUR' } } }
        ],
        allowCustom: true,
        customPlaceholder: 'e.g., 3000 EUR'
      })
    }

    // 5) Țări/Geo target (dacă lipsește ceva)
    if ((facts.googleAds?.locations?.length ?? 0) === 0) {
      groups.push({
        id: 'ask_googleads_geo',
        title: 'Which locations do you target in Google Ads?',
        multi: true,
        options: [
          { id: 'RO', label: 'Romania', payload: { type: 'ga_geo', value: 'RO' } },
          { id: 'BG', label: 'Bulgaria', payload: { type: 'ga_geo', value: 'BG' } },
          { id: 'HU', label: 'Hungary', payload: { type: 'ga_geo', value: 'HU' } }
        ],
        allowCustom: true,
        customPlaceholder: 'Add country code or name…'
      })
    }

    // 6) Conversions (dacă lipsesc)
    if ((facts.googleAds?.conversions?.length ?? 0) === 0) {
      groups.push({
        id: 'ask_googleads_conversions',
        title: 'Which conversion actions do you optimize for?',
        multi: true,
        options: [
          { id: 'lead', label: 'Leads', payload: { type: 'ga_conv', value: 'Lead' } },
          { id: 'purchase', label: 'Purchases', payload: { type: 'ga_conv', value: 'Purchase' } },
          { id: 'signup', label: 'Sign-ups', payload: { type: 'ga_conv', value: 'Sign-up' } },
          { id: 'call', label: 'Phone calls', payload: { type: 'ga_conv', value: 'Phone call' } }
        ],
        allowCustom: true,
        customPlaceholder: 'Add another conversion…'
      })
    }
  }

  // Heuristic mic: dacă ultima întrebare a lui Andy conține „channels/budget/country/conversions” — putem prioritiza,
  // dar pentru simplitate returnăm top 3
  return groups.slice(0, 3)
}

// Ajută la sintetizarea unui mesaj „natural” care să apară în chat când confirmi selecțiile
export function quickSelectionToMessage(groupId: string, labels: string[], custom?: string) {
  switch (groupId) {
    case 'ask_website':
      if (custom) return `Our website is ${custom.trim()}.`
      return null
    case 'ask_channels': {
      const all = [...labels, custom?.trim()].filter(Boolean)
      if (all.length) return `We use ${all.join(' and ')}.`
      return null
    }
    case 'ask_objectives': {
      const all = [...labels, custom?.trim()].filter(Boolean)
      if (all.length) return `Our primary goals are ${all.join(', ')}.`
      return null
    }
    case 'ask_googleads_budget':
      if (custom) return `Our monthly Google Ads budget is ${custom.trim()}.`
      if (labels[0]) return `Our monthly Google Ads budget is around ${labels[0]}.`
      return null
    case 'ask_googleads_geo': {
      const all = [...labels, custom?.trim()].filter(Boolean)
      if (all.length) return `We target ${all.join(', ')} in Google Ads.`
      return null
    }
    case 'ask_googleads_conversions': {
      const all = [...labels, custom?.trim()].filter(Boolean)
      if (all.length) return `We optimize for ${all.join(', ')} in Google Ads.`
      return null
    }
    default:
      return null
  }
}
