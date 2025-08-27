'use client'

import React from 'react'

export type ToolKey =
  | 'ga4' | 'gtm' | 'gsc' | 'looker' | 'sheets' | 'bigquery'
  | 'zapier' | 'plaud' | 'semrush' | 'ahrefs' | 'hubspot' | 'klaviyo' | 'mailchimp'
  | 'shopify' | 'woocommerce' | 'gmb' | 'server_side' | 'notion' | 'airtable' | 'custom_scripts'

export default function ToolEcosystemModal({
  open,
  tool,
  onClose,
}: {
  open: boolean
  tool: ToolKey | null
  onClose: () => void
}) {
  if (!open) return null
  const label = TOOL_LABELS[tool || 'ga4'] || 'Tool'
  return (
    <div className="fixed inset-0 z-[60]">
      <div className="absolute inset-0 bg-black/30" onClick={onClose} />
      <div className="absolute inset-x-4 md:inset-x-auto md:left-1/2 md:-translate-x-1/2 top-10 md:top-16 w-auto md:w-[720px] rounded-2xl border bg-white shadow-xl">
        <div className="flex items-center justify-between border-b p-4">
          <div className="text-sm font-semibold">{label} — Ecosystem</div>
          <button className="text-gray-500 hover:text-gray-800 text-sm" onClick={onClose}>Close</button>
        </div>
        <div className="p-5 text-sm space-y-4">
          <div className="rounded-xl border p-4">
            <div className="font-medium mb-1">Coming soon</div>
            <ul className="list-disc ml-5 space-y-1 text-gray-600">
              <li>OAuth / API connection</li>
              <li>Health score & optimization tips</li>
              <li>Report uploads & parsers</li>
              <li>Playbooks & automations</li>
            </ul>
          </div>
          <div className="text-xs text-gray-500">
            P.S. If you need this prioritized, ping me and I’ll move it up the queue.
          </div>
        </div>
      </div>
    </div>
  )
}

const TOOL_LABELS: Record<string, string> = {
  ga4:'Google Analytics 4', gtm:'Google Tag Manager', gsc:'Google Search Console', looker:'Looker Studio',
  sheets:'Google Sheets', bigquery:'BigQuery', zapier:'Zapier', plaud:'Plaud',
  semrush:'Semrush', ahrefs:'Ahrefs', hubspot:'HubSpot', klaviyo:'Klaviyo', mailchimp:'Mailchimp',
  shopify:'Shopify', woocommerce:'WooCommerce', gmb:'Google Business Profile',
  server_side:'Server-Side Tracking', notion:'Notion', airtable:'Airtable', custom_scripts:'Custom Scripts',
}
