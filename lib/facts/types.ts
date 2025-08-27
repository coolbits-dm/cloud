export type Currency = 'EUR' | 'USD' | 'RON'
export type Money = { amount: number; currency: Currency }

export type AdChannelFacts = {
  runSince?: string;              // "2023-05" or "2y" is fine
  monthlyBudget?: Money;          // { amount: 7000, currency: 'RON' }
  locations?: string[];           // countries/cities
  conversions?: string[];         // names (e.g., Purchase, Lead)
  campaignTypes?: string[];       // e.g., ['Search', 'PMax', 'YouTube']
  audiences?: string[];           // e.g., ['Remarketing', 'In-market']
  pixel?: boolean;                // for social channels
}

export type EmailFacts = {
  providers?: string[];           // e.g., ['Klaviyo', 'Mailchimp']
  monthlyBudget?: Money;
  audiences?: string[];
  conversions?: string[];
}

export type SeoFacts = {
  focus?: string[];               // e.g., ['Technical', 'Content', 'Link-building']
  keywords?: string[];
  runSince?: string;
}

export type PartialFacts = {
  // Company core
  businessName?: string
  website?: string
  industry?: string
  employees?: number | string

  // Marketing high-level
  objectives?: string[]
  channels?: string[]
  tools?: string[]
  tracking?: string[]
  trackingImplementation?: 'yes' | 'no' | 'partial'

  // Contact
  contactName?: string
  contactEmail?: string
  contactPhone?: string
  otherDetails?: string

  // Channels specific (all optional; fill whatever you can)
  googleAds?: AdChannelFacts
  metaAds?: AdChannelFacts
  tiktokAds?: AdChannelFacts
  linkedinAds?: AdChannelFacts
  amazonAds?: AdChannelFacts
  bingAds?: AdChannelFacts
  xAds?: AdChannelFacts

  email?: EmailFacts
  seo?: SeoFacts

  // Competitive
  competitors?: string[]
}

export type Facts = PartialFacts

export type FactsContextType = {
  facts: Facts
  upsertManual: (patch: PartialFacts) => void
  reset: () => void
}
