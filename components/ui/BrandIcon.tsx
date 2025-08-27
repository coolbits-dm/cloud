'use client'
import React from 'react'
import {
  siGoogleads,
  siMeta,
  siTiktok,
  siLinkedin,
  siX,
  siGoogleanalytics,
  siGoogletagmanager,
  siGooglesearchconsole,
  siZapier,
  siSemrush,
  siGoogle,
  siGmail,
} from 'simple-icons/icons'
import { BrainCircuit, Users, Mail, Globe2 } from 'lucide-react'

type Props = { name: string; className?: string }

/**
 * Renders brand SVGs (Simple Icons) with currentColor fill.
 * Falls back to Lucide for non-brand concepts.
 * Swap to your own /public/brands/cb-*.svg later (keep same API).
 */
export default function BrandIcon({ name, className }: Props) {
  // keep keys lowercase
  const map: Record<string, { title: string; path: string } | null> = {
    // Channels
    google_ads: siGoogleads,
    meta_ads: siMeta,
    tiktok_ads: siTiktok,
    linkedin_ads: siLinkedin,
    x_ads: siX,
    seo: siGoogle,     // generic G for organic; adjust anytime
    email: siGmail,    // brand-y email mark; can swap to Lucide

    // Tools
    ga4: siGoogleanalytics,
    gtm: siGoogletagmanager,
    gsc: siGooglesearchconsole,
    zapier: siZapier,
    semrush: siSemrush,

    // Concepts (null → Lucide below)
    referral: null,
    ai_optimization: null,
  }

  const icon = map[name]
  if (icon) {
    return (
      <svg
        role="img"
        aria-label={icon.title}
        viewBox="0 0 24 24"
        className={className}
        fill="currentColor"
      >
        <path d={icon.path} />
      </svg>
    )
  }

  // Lucide fallbacks for concepts
  const Fallback =
    name === 'ai_optimization' ? BrainCircuit :
    name === 'referral' ? Users :
    name === 'email' ? Mail :
    Globe2

  return <Fallback className={className} />
}
