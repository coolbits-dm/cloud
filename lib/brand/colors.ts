export type BrandPalette = {
  bg: string   // fundal chip
  fg: string   // text/fallback
  border: string
}

export const BRAND_COLORS: Record<string, BrandPalette> = {
  'google-ads': { bg: '#E8F0FE', fg: '#1A73E8', border: '#D2E3FC' },
  meta:         { bg: '#EEF2FF', fg: '#2563EB', border: '#E0E7FF' },
  tiktok:       { bg: '#ECFEFF', fg: '#0891B2', border: '#CFFAFE' },
  linkedin:     { bg: '#E0F2FE', fg: '#0284C7', border: '#BAE6FD' },
  x:            { bg: '#F4F4F5', fg: '#18181B', border: '#E4E4E7' },
  seo:          { bg: '#F0FDF4', fg: '#16A34A', border: '#DCFCE7' },
  email:        { bg: '#FEFCE8', fg: '#CA8A04', border: '#FEF9C3' },
  referral:     { bg: '#FFF1F2', fg: '#E11D48', border: '#FFE4E6' },
  'ai-optimization': { bg: '#F5F3FF', fg: '#7C3AED', border: '#EDE9FE' },

  // fallback generic
  default:      { bg: '#F3F4F6', fg: '#374151', border: '#E5E7EB' },
}

export function getBrandColors(brand?: string): BrandPalette {
  if (!brand) return BRAND_COLORS.default
  return BRAND_COLORS[brand] ?? BRAND_COLORS.default
}
