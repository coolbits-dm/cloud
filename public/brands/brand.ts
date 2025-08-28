// lib/brand/brand.ts

export type BrandId =
  | 'google_ads'
  | 'meta_ads'
  | 'tiktok_ads'
  | 'linkedin_ads'
  | 'x_ads'
  | 'seo'
  | 'email'
  | 'referral'
  | 'ai_ops' // ← noul ID canonic
  // tools
  | 'ga4'
  | 'gtm'
  | 'gsc'
  | 'meta_pixel'
  | 'sheets'
  | 'zapier'
  | 'plaud'
  | 'semrush'

/** Numele afișate în UI */
const BRAND_LABELS: Record<BrandId, string> = {
  google_ads: 'Google Ads',
  meta_ads: 'Meta Ads',
  tiktok_ads: 'TikTok Ads',
  linkedin_ads: 'LinkedIn Ads',
  x_ads: 'X Ads',
  seo: 'Organic (SEO)',
  email: 'Email',
  referral: 'Referral',
  ai_ops: 'AI Ops', // ← label
  // tools
  ga4: 'Google Analytics 4',
  gtm: 'Google Tag Manager',
  gsc: 'Google Search Console',
  meta_pixel: 'Meta Pixel',
  sheets: 'Google Sheets',
  zapier: 'Zapier',
  plaud: 'Plaud',
  semrush: 'SEMrush',
}

/** Aliasuri tolerate → ID canonic.
 *  Păstrăm compatibilitate cu vechiul `ai_optimization`/“ai optimization”.
 */
const BRAND_ALIASES: Record<string, BrandId> = {
  'ai ops': 'ai_ops',
  'ai_ops': 'ai_ops',
  'ai-ops': 'ai_ops',
  'aiops': 'ai_ops',
  'ai optimization': 'ai_ops',
  'ai_optimization': 'ai_ops',
  'ai-optimization': 'ai_ops',
  'aioptimization': 'ai_ops',
}

/** Normalizează un id/label liber la id canonic folosit de fișierele din /public/brands */
export function normalizeBrandId(id: string): BrandId | null {
  if (!id) return null
  const k = id.trim().toLowerCase().replace(/\s+/g, '_')
  if ((BRAND_LABELS as any)[k]) return k as BrandId
  if (BRAND_ALIASES[k]) return BRAND_ALIASES[k]
  return null
}

/** Calea către SVG-ul din /public/brands */
export function brandFile(id: string): string {
  const norm = normalizeBrandId(id) ?? (id as BrandId)
  return `/brands/${norm}.svg` // ex: /brands/ai_ops.svg
}

/** Eticheta afișată în UI */
export function brandLabel(id: string): string {
  const norm = normalizeBrandId(id) as BrandId | null
  if (norm && BRAND_LABELS[norm]) return BRAND_LABELS[norm]
  return id
    .replace(/[_-]+/g, ' ')
    .replace(/\b\w/g, (m) => m.toUpperCase())
}
