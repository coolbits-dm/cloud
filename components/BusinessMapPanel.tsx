// components/BusinessMapPanel.tsx
'use client'

import React, { useEffect, useMemo, useState } from 'react'
import { useFacts } from '@/lib/facts/store'
import { useChannelModal } from '@/lib/store/useChannelModal'
import ChannelEcosystemModal from '@/components/ChannelEcosystemModal'
import TokenMeter from '@/components/analysis/TokenMeter'
import BrandIcon from '@/components/ui/BrandIcon'
import type { BrandId } from '@/lib/brand/brand'

type Item = { id: BrandId; label: string; soon?: boolean }

const CHANNELS: Item[] = [
  { id: 'google_ads', label: 'Google Ads' },
  { id: 'meta_ads', label: 'Meta Ads', soon: true },
  { id: 'tiktok_ads', label: 'TikTok Ads', soon: true },
  { id: 'linkedin_ads', label: 'LinkedIn Ads', soon: true },
  { id: 'x_ads', label: 'X Ads', soon: true },
  { id: 'seo', label: 'Organic (SEO)', soon: true },
  { id: 'email', label: 'Email', soon: true },
  { id: 'referral', label: 'Referral', soon: true },
  { id: 'ai_ops', label: 'AI Ops', soon: true },               // 🔁 renamed
]

const TOOLS: Item[] = [
  { id: 'ga4', label: 'Google Analytics 4' },
  { id: 'gtm', label: 'Google Tag Manager' },
  { id: 'gsc', label: 'Google Search Console' },
  { id: 'meta_pixel', label: 'Meta Pixel' },
  { id: 'sheets', label: 'Google Sheets', soon: true },
  { id: 'zapier', label: 'Zapier', soon: true },
  { id: 'plaud', label: 'Plaud', soon: true },
  { id: 'semrush', label: 'SEMrush', soon: true },
]

// map free-text → canonical id
const CH_LABEL_TO_ID: Record<string, BrandId> = {
  'google ads': 'google_ads',
  'meta ads': 'meta_ads',
  facebook: 'meta_ads',
  instagram: 'meta_ads',
  'tiktok ads': 'tiktok_ads',
  'linkedin ads': 'linkedin_ads',
  'x ads': 'x_ads',
  seo: 'seo',
  'organic (seo)': 'seo',
  email: 'email',
  referral: 'referral',
  'ai ops': 'ai_ops',                              // 🔁 new
  'ai-ops': 'ai_ops',
  'ai operations': 'ai_ops',
  // legacy aliases we may have stored previously:
  'ai optimization': 'ai_ops',                     // 🔁 alias to avoid 404s
  'ai_optimization': 'ai_ops',
}

export default function BusinessMapPanel() {
  const { facts } = useFacts()
  const { open } = useChannelModal()

  const activeChannels = useMemo(() => {
    const list = (facts.channels || []) as string[]
    return new Set<BrandId>(
      list.map((raw) => {
        const key = raw.trim().toLowerCase()
        return CH_LABEL_TO_ID[key] ?? (key.replace(/\s+/g, '_') as BrandId)
      }),
    )
  }, [facts.channels])

  const [progress, setProgress] = useState<Record<string, number>>({})
  useEffect(() => {
    setProgress((prev) => {
      const next = { ...prev }
      activeChannels.forEach((id) => {
        if (next[id] == null) next[id] = 30
      })
      return next
    })
  }, [activeChannels])

  const [updates, setUpdates] = useState<Array<{ id: string; ts: Date; text: string }>>([])
  useEffect(() => {
    const add = (text: string) =>
      setUpdates((u) => [{ id: crypto.randomUUID(), ts: new Date(), text }, ...u].slice(0, 25))

    const onDeep = (e: any) => {
      const { jobId, engine } = e?.detail || {}
      add(`Deep Current Analysis started (${engine ?? 'Kim'}), job ${jobId?.slice(0, 8)}…`)
    }
    const onEco = (e: any) => {
      const { channel } = e?.detail || {}
      if (channel) add(`Ecosystem updated — ${channel.replace(/_/g, ' ')}`)
    }
    const onBrief = (e: any) => {
      const { engine } = e?.detail || {}
      add(`Deep analysis finished — summary from ${engine ?? 'Kim'} sent to Andy.`)
    }

    window.addEventListener('cb:deep-analysis-started', onDeep as EventListener)
    window.addEventListener('cb:ecosystem-summary', onEco as EventListener)
    window.addEventListener('cb:analysis-briefing', onBrief as EventListener)
    return () => {
      window.removeEventListener('cb:deep-analysis-started', onDeep as EventListener)
      window.removeEventListener('cb:ecosystem-summary', onEco as EventListener)
      window.removeEventListener('cb:analysis-briefing', onBrief as EventListener)
    }
  }, [])

  const Stat = ({ label, value }: { label: string; value: React.ReactNode }) => (
    <div className="rounded-xl border px-2.5 py-1.5 text-xs flex items-center gap-2">
      <span className="text-gray-500">{label}:</span>
      <span className="font-medium">{value}</span>
    </div>
  )

  const Section = ({ title, children }: { title: string; children: React.ReactNode }) => (
    <section className="space-y-2">
      <h3 className="text-[11px] font-semibold uppercase tracking-wide text-gray-500">{title}</h3>
      {children}
    </section>
  )

  return (
    <div className="flex h-full flex-col rounded-lg border bg-white shadow-sm">
      {/* header */}
      <div className="sticky top-0 z-10 border-b bg-white/95 backdrop-blur px-3 py-2">
        <div className="flex items-center justify-between">
          <div className="text-sm font-semibold">Business Map</div>
          <div className="flex items-center gap-2">
            <button
              className="rounded-md bg-amber-500 px-3 py-1.5 text-xs font-semibold text-white hover:bg-amber-600"
              onClick={() => window.dispatchEvent(new CustomEvent('cb:basic-briefing'))}
            >
              Generate Basic Briefing
            </button>
            <button
              className="rounded-md bg-gray-900 px-3 py-1.5 text-xs font-semibold text-white hover:bg-black"
              onClick={() => window.dispatchEvent(new CustomEvent('cb:open-deep-analysis'))}
            >
              Deep Current Analysis (Kim)
            </button>
          </div>
        </div>
        <div className="mt-2 flex flex-wrap items-center gap-2">
          <Stat label="Connections" value={0} />
          <Stat label="AI" value="Andy + Kim" />
          <div className="rounded-xl border px-2.5 py-1.5 text-[11px] text-gray-600">
            <TokenMeter />
          </div>
        </div>
      </div>

      {/* body scroll */}
      <div className="flex-1 space-y-6 overflow-y-auto p-3">
        {/* Channels */}
        <Section title="Channels (click to open ecosystem)">
          <div className="space-y-2">
            {CHANNELS.map((ch) => (
              <ChannelRow
                key={ch.id}
                item={ch}
                active={activeChannels.has(ch.id)}
                progress={progress[ch.id] ?? 0}
                onOpen={() => open(ch.id)}
              />
            ))}
          </div>
          <p className="mt-2 text-[11px] text-gray-500">
            Tip: active channels highlight; progress bar shows setup completeness.
          </p>
        </Section>

        {/* Company + Completeness */}
        <div className="grid grid-cols-2 gap-3">
          <Section title="Company">
            <div className="rounded-xl border p-3 text-sm">
              <Row label="Name" value={facts.businessName || '—'} />
              <Row label="Website" value={facts.website || '—'} />
              <Row label="Industry" value={facts.industry || '—'} />
              <Row
                label="Employees"
                value={
                  typeof facts.employees === 'number'
                    ? String(facts.employees)
                    : (facts.employees as any) || '—'
                }
              />
            </div>
          </Section>

          <Section title="Completeness">
            <div className="rounded-xl border p-3">
              <div className="text-[11px] text-gray-500 mb-1">profile readiness</div>
              <div className="h-2 w-full rounded-full bg-gray-200">
                <div
                  className="h-2 rounded-full bg-gray-900"
                  style={{ width: `${calcProfilePct(facts)}%` }}
                />
              </div>
            </div>
          </Section>
        </div>

        {/* Objectives */}
        <Section title="Objectives">
          <div className="rounded-xl border p-3 text-sm">
            {facts.objectives?.length ? (
              <div className="flex flex-wrap gap-2">
                {facts.objectives.map((o, i) => (
                  <span key={`${o}-${i}`} className="rounded-full border bg-white px-2.5 py-1 text-xs">
                    {o}
                  </span>
                ))}
              </div>
            ) : (
              <div className="text-gray-500 text-sm">No objectives yet</div>
            )}
          </div>
        </Section>

        {/* Marketing Tools */}
        <Section title="Marketing Tools">
          <div className="space-y-2">
            {TOOLS.map((t) => (
              <ChannelRow
                key={t.id}
                item={t}
                active={Array.isArray(facts.tools) && facts.tools.some((x) => matchToolId(x) === t.id)}
                progress={progress[t.id] ?? 0}
                onOpen={() => {/* hook tools modal later */}}
              />
            ))}
          </div>
        </Section>

        {/* Recent updates */}
        <Section title="Recent Updates">
          <div className="rounded-xl border p-3">
            {updates.length === 0 ? (
              <div className="text-sm text-gray-500">Nothing yet</div>
            ) : (
              <ul className="space-y-2 text-sm">
                {updates.map((u) => (
                  <li key={u.id} className="flex items-start gap-2">
                    <span className="mt-1 inline-block h-1.5 w-1.5 rounded-full bg-gray-400" />
                    <div>
                      <div className="text-gray-900">{u.text}</div>
                      <div className="text-[11px] text-gray-500">{u.ts.toLocaleTimeString()}</div>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </Section>
      </div>

      <ChannelEcosystemModal />
    </div>
  )
}

function Row({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="grid grid-cols-[120px_1fr] py-1">
      <div className="text-gray-500">{label}</div>
      <div className="font-medium">{value}</div>
    </div>
  )
}

function ChannelRow({
  item,
  active,
  progress,
  onOpen,
}: {
  item: Item
  active: boolean
  progress: number
  onOpen: () => void
}) {
  return (
    <button
      onClick={onOpen}
      className={`w-full rounded-2xl border px-3 py-2 text-left transition ${
        active ? 'bg-indigo-50 border-indigo-200' : 'bg-white hover:bg-gray-50'
      }`}
    >
      <div className="flex items-center gap-3">
        <div className="flex h-7 w-7 items-center justify-center rounded-xl bg-white shadow-sm border">
          <BrandIcon id={item.id} size={16} />
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <div className="text-sm font-medium">{item.label}</div>
            {item.soon && (
              <span className="rounded-full border px-1.5 py-0.5 text-[10px] text-gray-600">soon</span>
            )}
          </div>
          {active && (
            <div className="mt-1 h-1.5 w-36 rounded-full bg-gray-200">
              <div
                className="h-1.5 rounded-full bg-gray-900"
                style={{ width: `${Math.max(0, Math.min(100, progress))}%` }}
              />
            </div>
          )}
        </div>
      </div>
    </button>
  )
}

function calcProfilePct(facts: any) {
  let n = 0,
    have = 0
  const check = (v: any) => {
    n++
    if (v && ((Array.isArray(v) && v.length) || !Array.isArray(v))) have++
  }
  check(facts.businessName)
  check(facts.website)
  check(facts.industry)
  check(facts.employees)
  check(facts.objectives?.length)
  check(facts.channels?.length)
  check(facts.tools?.length)
  return Math.round((have / Math.max(1, n)) * 100)
}

function matchToolId(label: string): BrandId | string {
  const s = label.trim().toLowerCase()
  if (/analytics\s*4|ga4/.test(s)) return 'ga4'
  if (/tag manager|gtm/.test(s)) return 'gtm'
  if (/search console|gsc/.test(s)) return 'gsc'
  if (/meta\s*pixel|facebook\s*pixel/.test(s)) return 'meta_pixel'
  if (/sheets/.test(s)) return 'sheets'
  if (/zapier/.test(s)) return 'zapier'
  if (/plaud/.test(s)) return 'plaud'
  if (/semrush/.test(s)) return 'semrush'
  return s.replace(/\s+/g, '_')
}
