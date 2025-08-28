// components/ChannelEcosystemModal.tsx
'use client'

import React, { useEffect } from 'react'
import GoogleAdsEcosystem from '@/components/ecosystems/GoogleAdsEcosystem'
import { useChannelModal } from '@/lib/store/useChannelModal'
import type { ChannelKey } from '@/lib/store/useChannelModal'
import { getAndClearEcosystemSummary } from '@/lib/channels/session'

export default function ChannelEcosystemModal() {
  const { current: channel, isOpen, close } = useChannelModal()

  useEffect(() => {
    const onEsc = (e: KeyboardEvent) => { if (e.key === 'Escape') handleClose() }
    if (isOpen) window.addEventListener('keydown', onEsc)
    return () => window.removeEventListener('keydown', onEsc)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen, channel])

  function handleClose() {
    if (channel) {
      const summary = getAndClearEcosystemSummary(channel as any)
      if (summary) {
        window.dispatchEvent(new CustomEvent('cb:ecosystem-summary', {
          detail: { channel, summary }
        }))
      }
    }
    close()
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-[100]">
      <div className="absolute inset-0 bg-black/30" onClick={handleClose} />
      <div className="absolute inset-0 flex items-center justify-center p-4">
        <div className="w-full max-w-5xl rounded-2xl bg-white shadow-2xl border">
          <div className="flex items-center justify-between border-b p-4">
            <h2 className="text-lg font-semibold">{labelForChannel(channel)}</h2>
            <button onClick={handleClose} className="rounded-md border px-2 py-1 text-sm hover:bg-gray-50">Close</button>
          </div>
          <div className="p-4">
            {channel === 'google_ads' ? (
              <GoogleAdsEcosystem />
            ) : (
              <ComingSoon label={labelForChannel(channel)} />
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

function labelForChannel(ch: ChannelKey | null): string {
  switch (ch) {
    case 'google_ads': return 'Google Ads'
    case 'meta_ads': return 'Meta Ads'
    case 'tiktok_ads': return 'TikTok Ads'
    case 'linkedin_ads': return 'LinkedIn Ads'
    case 'x_ads': return 'X Ads'
    case 'seo': return 'Organic (SEO)'
    case 'email': return 'Email'
    case 'referral': return 'Referral'
    case 'ai_ops': return 'AI Ops'             // 🔁 renamed
    case 'ga4': return 'Google Analytics 4'
    case 'gtm': return 'Google Tag Manager'
    case 'gsc': return 'Google Search Console'
    case 'meta_pixel': return 'Meta Pixel'
    case 'zapier': return 'Zapier'
    case 'semrush': return 'SEMrush'
    case 'plaud': return 'Plaud'
    case 'sheets': return 'Google Sheets'
    default: return 'Ecosystem'
  }
}

function ComingSoon({ label }: { label: string }) {
  return (
    <div className="space-y-4">
      <p className="text-base">{label} ecosystem</p>
      <div className="rounded-2xl border p-4">
        <h3 className="font-semibold mb-2">Coming Soon</h3>
        <ul className="list-disc ml-5 space-y-1 text-sm">
          <li>OAuth & account linking</li>
          <li>Report uploads & parsers</li>
          <li>Native metrics & dashboards</li>
          <li>Playbooks & automations</li>
        </ul>
      </div>
    </div>
  )
}
