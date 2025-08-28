// lib/brand/brand.ts

export type BrandId =
  // channels
  | 'google_ads'
  | 'meta_ads'
  | 'tiktok_ads'
  | 'linkedin_ads'
  | 'x_ads'
  | 'seo'
  | 'email'
  | 'referral'
  | 'ai_ops'          // 🔁 renamed from ai_optimization
  // tools
  | 'ga4'
  | 'gtm'
  | 'gsc'
  | 'meta_pixel'
  | 'sheets'
  | 'zapier'
  | 'plaud'
  | 'semrush'

const LABEL: Record<BrandId, string> = {
  google_ads: 'Google Ads',
  meta_ads: 'Meta Ads',
  tiktok_ads: 'TikTok Ads',
  linkedin_ads: 'LinkedIn Ads',
  x_ads: 'X Ads',
  seo: 'Organic (SEO)',
  email: 'Email',
  referral: 'Referral',
  ai_ops: 'AI Ops',

  ga4: 'Google Analytics 4',
  gtm: 'Google Tag Manager',
  gsc: 'Google Search Console',
  meta_pixel: 'Meta Pixel',
  sheets: 'Google Sheets',
  zapier: 'Zapier',
  plaud: 'Plaud',
  semrush: 'SEMrush',
}

const FILE: Record<BrandId, string> = {
  google_ads: '/brands/google_ads.svg',
  meta_ads: '/brands/meta_ads.svg',
  tiktok_ads: '/brands/tiktok_ads.svg',
  linkedin_ads: '/brands/linkedin_ads.svg',
  x_ads: '/brands/x_ads.svg',
  seo: '/brands/seo.svg',
  email: '/brands/email.svg',
  referral: '/brands/referral.svg',
  ai_ops: '/brands/ai_ops.svg',            // 🔁 new icon path

  ga4: '/brands/ga4.svg',
  gtm: '/brands/gtm.svg',
  gsc: '/brands/gsc.svg',
  meta_pixel: '/brands/meta_pixel.svg',
  sheets: '/brands/sheets.svg',
  zapier: '/brands/zapier.svg',
  plaud: '/brands/plaud.svg',
  semrush: '/brands/semrush.svg',
}

const COLOR: Record<BrandId, string> = {
  google_ads: '#4285F4',
  meta_ads: '#0866FF',
  tiktok_ads: '#000000',
  linkedin_ads: '#0A66C2',
  x_ads: '#111111',
  seo: '#0F9D58',
  email: '#E37400',
  referral: '#6B7280',
  ai_ops: '#7C3AED', // purple accent

  ga4: '#F9AB00',
  gtm: '#1A73E8',
  gsc: '#1A73E8',
  meta_pixel: '#0866FF',
  sheets: '#0F9D58',
  zapier: '#FF4A00',
  plaud: '#111827',
  semrush: '#FF642D',
}

export function brandLabel(id: BrandId) {
  return LABEL[id] ?? id
}

export function brandFile(id: BrandId) {
  return FILE[id] ?? '/brands/unknown.svg'
}

export function brandColor(id: BrandId) {
  return COLOR[id] ?? '#3B82F6'
}
