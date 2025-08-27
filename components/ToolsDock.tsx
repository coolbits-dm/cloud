'use client'

import React, { useMemo, useState } from 'react'
import {
  Cog6ToothIcon,
  WrenchScrewdriverIcon,
  DocumentChartBarIcon,
  LinkIcon,
  ChartBarIcon,
  ChartPieIcon,
  QueueListIcon,
  BuildingStorefrontIcon,
  ServerStackIcon,
  RectangleGroupIcon,
  EnvelopeIcon,
  BoltIcon,
  GlobeAltIcon,
  ArrowTrendingUpIcon,
  CommandLineIcon,
} from '@heroicons/react/24/outline'

export type ToolKey =
  | 'ga4' | 'gtm' | 'gsc' | 'looker'
  | 'sheets' | 'bigquery'
  | 'zapier' | 'plaud'
  | 'semrush' | 'ahrefs'
  | 'hubspot' | 'klaviyo' | 'mailchimp'
  | 'shopify' | 'woocommerce'
  | 'gmb' | 'server_side'
  | 'notion' | 'airtable'
  | 'custom_scripts'

type Tool = {
  id: ToolKey
  label: string
  icon: React.ComponentType<React.SVGProps<SVGSVGElement>>
  vendor?: 'Google'|'Meta'|'TikTok'|'X'|'Other'
  status: 'available' | 'coming_soon'
}

const TOOLS: Tool[] = [
  { id:'ga4', label:'Google Analytics 4', icon: ChartPieIcon, vendor:'Google', status:'coming_soon' },
  { id:'gtm', label:'Google Tag Manager', icon: Cog6ToothIcon, vendor:'Google', status:'coming_soon' },
  { id:'gsc', label:'Google Search Console', icon: GlobeAltIcon, vendor:'Google', status:'coming_soon' },
  { id:'looker', label:'Looker Studio', icon: DocumentChartBarIcon, vendor:'Google', status:'coming_soon' },
  { id:'sheets', label:'Google Sheets', icon: QueueListIcon, vendor:'Google', status:'coming_soon' },
  { id:'bigquery', label:'BigQuery', icon: ServerStackIcon, vendor:'Google', status:'coming_soon' },

  { id:'zapier', label:'Zapier', icon: LinkIcon, vendor:'Other', status:'coming_soon' },
  { id:'plaud', label:'Plaud', icon: BoltIcon, vendor:'Other', status:'coming_soon' },

  { id:'semrush', label:'Semrush', icon: ArrowTrendingUpIcon, vendor:'Other', status:'coming_soon' },
  { id:'ahrefs', label:'Ahrefs', icon: RectangleGroupIcon, vendor:'Other', status:'coming_soon' },

  { id:'hubspot', label:'HubSpot', icon: WrenchScrewdriverIcon, vendor:'Other', status:'coming_soon' },
  { id:'klaviyo', label:'Klaviyo', icon: EnvelopeIcon, vendor:'Other', status:'coming_soon' },
  { id:'mailchimp', label:'Mailchimp', icon: EnvelopeIcon, vendor:'Other', status:'coming_soon' },

  { id:'shopify', label:'Shopify', icon: BuildingStorefrontIcon, vendor:'Other', status:'coming_soon' },
  { id:'woocommerce', label:'WooCommerce', icon: BuildingStorefrontIcon, vendor:'Other', status:'coming_soon' },

  { id:'gmb', label:'Google Business Profile', icon: ChartBarIcon, vendor:'Google', status:'coming_soon' },
  { id:'server_side', label:'Server-Side Tracking', icon: CommandLineIcon, vendor:'Other', status:'coming_soon' },

  { id:'notion', label:'Notion', icon: DocumentChartBarIcon, vendor:'Other', status:'coming_soon' },
  { id:'airtable', label:'Airtable', icon: QueueListIcon, vendor:'Other', status:'coming_soon' },
  { id:'custom_scripts', label:'Custom Scripts', icon: WrenchScrewdriverIcon, vendor:'Other', status:'coming_soon' },
]

export default function ToolsDock({
  onOpen,
  className = '',
  showSearch = true,
  limit = 999,          // change to e.g. 12 if you want a "Show all" button
}: {
  onOpen: (id: ToolKey) => void
  className?: string
  showSearch?: boolean
  limit?: number
}) {
  const [q, setQ] = useState('')

  const filtered = useMemo(() => {
    const term = q.trim().toLowerCase()
    if (!term) return TOOLS
    return TOOLS.filter(t => t.label.toLowerCase().includes(term))
  }, [q])

  const list = filtered.slice(0, limit)

  return (
    <div className={className}>
      {showSearch && (
        <div className="mb-2">
          <input
            value={q}
            onChange={(e)=>setQ(e.target.value)}
            placeholder="Search tools…"
            className="w-full h-9 rounded-lg border px-3 text-xs outline-none focus:ring-2 focus:ring-primary-300"
          />
        </div>
      )}

      <div
        className="grid gap-2
        [grid-template-columns:repeat(auto-fit,minmax(160px,1fr))]
        sm:[grid-template-columns:repeat(auto-fit,minmax(170px,1fr))]"
      >
        {list.map((t) => {
          const Icon = t.icon
          const isSoon = t.status === 'coming_soon'
          return (
            <button
              key={t.id}
              onClick={() => onOpen(t.id)}
              title={isSoon ? `${t.label} — preview` : `Open ${t.label}`}
              className="w-full min-w-0 min-h-[44px]
                inline-flex items-center gap-2 rounded-xl border bg-white
                px-3 py-2 text-[11.5px] sm:text-xs md:text-sm leading-tight
                shadow-sm hover:shadow-md transition"
            >
              <Icon className="h-4 w-4 shrink-0" />
              <span className="flex-1 whitespace-normal break-words">{t.label}</span>
              {isSoon && (
                <span className="ml-1 inline-flex items-center rounded-full border bg-gray-50 px-1.5 py-0.5 text-[10px] text-gray-600 shrink-0">
                  soon
                </span>
              )}
            </button>
          )
        })}
      </div>

      {filtered.length > list.length && (
        <div className="mt-2 text-center">
          <button
            className="text-xs text-primary-700 hover:underline"
            onClick={() => (window as any).__expandTools
              ? (window as any).__expandTools()
              : alert('Increase the `limit` prop on <ToolsDock /> to show more.')}
          >
            Show all {filtered.length} tools
          </button>
        </div>
      )}
    </div>
  )
}
