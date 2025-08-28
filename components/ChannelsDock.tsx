'use client'

import React from 'react'
import { useChannelModal } from '@/lib/store/useChannelModal'
import { Badge } from '@/components/ui/badge'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import BrandIcon from '@/components/ui/BrandIcon'

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

type Channel = {
  id: ChannelKey
  label: string
  brand: string            // cheie pentru BrandIcon
  status: 'available' | 'coming_soon'
}

export const CHANNELS: Channel[] = [
  { id: 'google_ads',      label: 'Google Ads',      brand: 'google-ads',      status: 'available' },
  { id: 'meta_ads',        label: 'Meta Ads',        brand: 'meta',            status: 'coming_soon' },
  { id: 'tiktok_ads',      label: 'TikTok Ads',      brand: 'tiktok',          status: 'coming_soon' },
  { id: 'linkedin_ads',    label: 'LinkedIn Ads',    brand: 'linkedin',        status: 'coming_soon' },
  { id: 'x_ads',           label: 'X Ads',           brand: 'x',               status: 'coming_soon' },
  { id: 'seo',             label: 'Organic (SEO)',   brand: 'seo',             status: 'coming_soon' },
  { id: 'email',           label: 'Email',           brand: 'email',           status: 'coming_soon' },
  { id: 'referral',        label: 'Referral',        brand: 'referral',        status: 'coming_soon' },
  { id: 'ai_optimization', label: 'AI Optimization', brand: 'ai-optimization', status: 'coming_soon' },
]

export default function ChannelsDock() {
  const open = useChannelModal(s => s.open)

  return (
    <TooltipProvider>
      <div className="flex flex-wrap items-center gap-2">
        {CHANNELS.map(ch => {
          const disabled = ch.status === 'coming_soon'
          return (
            <Tooltip key={ch.id}>
              <TooltipTrigger asChild>
                <button
                  onClick={() => open(ch.id)}
                  className={[
                    'inline-flex items-center gap-2 rounded-2xl px-3 py-2 text-sm border shadow-sm transition',
                    disabled ? 'opacity-90 hover:opacity-100' : 'hover:shadow-md'
                  ].join(' ')}
                >
                  <BrandIcon brand={ch.brand} size={16} variant="solid" />
                  <span className="truncate max-w-[10rem]">{ch.label}</span>
                  {disabled && <Badge variant="secondary" className="ml-1">soon</Badge>}
                </button>
              </TooltipTrigger>
              <TooltipContent side="bottom">
                <p>{disabled ? 'Preview & roadmap' : 'Open ecosystem'}</p>
              </TooltipContent>
            </Tooltip>
          )
        })}
      </div>
    </TooltipProvider>
  )
}
