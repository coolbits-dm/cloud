'use client'

import React, { useEffect, useMemo, useState } from 'react'
import { useFacts } from '@/lib/facts/store'
import { useChannelModal } from '@/lib/store/useChannelModal'
import ChannelEcosystemModal from '@/components/ChannelEcosystemModal'
import TokenMeter from '@/components/analysis/TokenMeter'

// lucide icons
import {
  BarChart3, Smartphone, FlaskConical, Hash, Globe2, Mail, Users, Cpu,
  LineChart, Wrench, Search, Zap, PlugZap, Database, Cable, BrainCircuit, ShieldCheck
} from 'lucide-react'

// ---------- brand color helpers (used for icon rings) ----------
const BRAND_COLORS: Record<string, string> = {
  google_ads: '#4285F4',
  meta_ads: '#0866FF',
  tiktok_ads: '#000000',
  linkedin_ads: '#0A66C2',
  x_ads: '#111111',
  seo: '#0F9D58',
  email: '#E37400',
  referral: '#6B7280',
  ai_optimization: '#7C3AED',
  // tools
  ga4: '#F9AB00',
  gtm: '#1A73E8',
  gsc: '#1A73E8',
  meta_pixel: '#0866FF',
  zapier: '#FF4A00',
  semrush: '#FF642D',
  plaud: '#111827',
  sheets: '#0F9D58',
}

function ringFor(id: string) {
  const c = BRAND_COLORS[id] || '#3B82F6'
  return {
    boxShadow: `inset 0 0 0 2px ${c}22, 0 0 0 1px ${c}33`,
  }
}

// ---------- domain lists ----------
type Item = { id: string; label: string; icon: React.ComponentType<any>; soon?: boolean }

const CHANNELS: Item[] = [
  { id: 'google_ads',   label: 'Google Ads',   icon: BarChart3 },
  { id: 'meta_ads',     label: 'Meta Ads',     icon: Smartphone, soon: true },
  { id: 'tiktok_ads',   label: 'TikTok Ads',   icon: FlaskConical, soon: true },
  { id: 'linkedin_ads', label: 'LinkedIn Ads', icon: Users, soon: true },
  { id: 'x_ads',        label: 'X Ads',        icon: Hash, soon: true },
  { id: 'seo',          label: 'Organic (SEO)',icon: Globe2, soon: true },
  { id: 'email',        label: 'Email',        icon: Mail, soon: true },
  { id: 'referral',     label: 'Referral',     icon: Users, soon: true },
  { id: 'ai_optimization', label: 'AI Optimization', icon: Cpu, soon: true },
]

const TOOLS: Item[] = [
  { id: 'ga4',        label: 'Google Analytics 4', icon: LineChart },
  { id: 'gtm',        label: 'Google Tag Manager', icon: Wrench },
  { id: 'gsc',        label: 'Google Search Console', icon: Search },
  { id: 'meta_pixel', label: 'Meta Pixel', icon: Zap },
  { id: 'sheets',     label: 'Google Sheets', icon: Database, soon: true },
  { id: 'zapier',     label: 'Zapier', icon: Cable, soon: true },
  { id: 'plaud',      label: 'Plaud', icon: ShieldCheck, soon: true },
  { id: 'semrush',    label: 'SEMrush', icon: BrainCircuit, soon: true },
]

// map free-text channels from onboarding → canonical ids
const CH_LABEL_TO_ID: Record<string, string> = {
  'google ads': 'google_ads',
  'meta ads': 'meta_ads',
  'facebook': 'meta_ads',
  'instagram': 'meta_ads',
  'tiktok ads': 'tiktok_ads',
  'linkedin ads': 'linkedin_ads',
  'x ads': 'x_ads',
  'seo': 'seo',
  'organic (seo)': 'seo',
  'email': 'email',
  'referral': 'referral',
  'ai optimization': 'ai_optimization',
}

// ---------- component ----------
export default function BusinessMapPanel() {
  const { facts } = useFacts()
  const { open } = useChannelModal()

  // derive “active” from onboarding facts
  const activeChannels = useMemo(() => {
    const list = (facts.channels || []) as string[]
    return new Set(
      list.map(s => CH_LABEL_TO_ID[s.trim().toLowerCase()] || s.trim().toLowerCase().replace(/\s+/g,'_'))
    )
  }, [facts.channels])

  // default progress (when coming from onboarding): 30%
  const [progress, setProgress] = useState<Record<string, number>>({})
  useEffect(() => {
    const next = { ...progress }
    activeChannels.forEach(id => { if (next[id] == null) next[id] = 30 })
    setProgress(next)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeChannels.size])

  // recent updates (panel-only, human text)
  const [updates, setUpdates] = useState<Array<{ id: string; ts: Date; text: string }>>([])
  useEffect(() => {
    const add = (text: string) => setUpdates(u => [{ id: crypto.randomUUID(), ts: new Date(), text }, ...u].slice(0, 25))

    const onDeep = (e: any) => {
      const { jobId, engine } = (e?.detail || {})
      add(`Deep Current Analysis started (${engine ?? 'Kim'}), job ${jobId?.slice(0,8)}…`)
    }
    const onEco = (e: any) => {
      const { channel } = (e?.detail || {})
      if (channel) add(`Ecosystem updated — ${channel.replace(/_/g,' ')}`)
    }
    const onBrief = (e: any) => {
      const { engine } = (e?.detail || {})
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

  // UI helpers
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
            {CHANNELS.map(ch => (
              <ChannelRow
                key={ch.id}
                item={ch}
                active={activeChannels.has(ch.id)}
                progress={progress[ch.id] ?? 0}
                onOpen={() => open(ch.id as any)}
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
              <Row label="Employees" value={
                typeof facts.employees === 'number' ? String(facts.employees)
                : (facts.employees as any) || '—'
              } />
            </div>
          </Section>

          <Section title="Completeness">
            <div className="rounded-xl border p-3">
              <div className="text-[11px] text-gray-500 mb-1">profile readiness</div>
              <div className="h-2 w-full rounded-full bg-gray-200">
                <div className="h-2 rounded-full bg-gray-900" style={{ width: `${calcProfilePct(facts)}%` }} />
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
                  <span key={`${o}-${i}`} className="rounded-full border bg-white px-2.5 py-1 text-xs">{o}</span>
                ))}
              </div>
            ) : (
              <div className="text-gray-500 text-sm">No objectives yet</div>
            )}
          </div>
        </Section>

        {/* Marketing Tools (same behavior as channels) */}
        <Section title="Marketing Tools">
          <div className="space-y-2">
            {TOOLS.map(t => (
              <ChannelRow
                key={t.id}
                item={t}
                active={Array.isArray(facts.tools) && facts.tools.some(x => matchToolId(x) === t.id)}
                progress={progress[t.id] ?? 0}
                onOpen={() => {/* tools modal later */}}
              />
            ))}
          </div>
        </Section>

        {/* Recent Updates (always last) */}
        <Section title="Recent Updates">
          <div className="rounded-xl border p-3">
            {updates.length === 0 ? (
              <div className="text-sm text-gray-500">Nothing yet</div>
            ) : (
              <ul className="space-y-2 text-sm">
                {updates.map(u => (
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

      {/* mount modal once, here */}
      <ChannelEcosystemModal />
    </div>
  )
}

// ---------- bits ----------
function Row({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="grid grid-cols-[120px_1fr] py-1">
      <div className="text-gray-500">{label}</div>
      <div className="font-medium">{value}</div>
    </div>
  )
}

function ChannelRow({
  item, active, progress, onOpen,
}: { item: Item; active: boolean; progress: number; onOpen: () => void }) {
  const Icon = item.icon
  return (
    <button
      onClick={onOpen}
      className={`w-full rounded-2xl border px-3 py-2 text-left transition
        ${active ? 'bg-indigo-50 border-indigo-200' : 'bg-white hover:bg-gray-50'}`}
      style={active ? ringFor(item.id) : undefined}
    >
      <div className="flex items-center gap-3">
        <div className="flex h-7 w-7 items-center justify-center rounded-xl bg-white shadow-sm border">
          <Icon className="h-4 w-4" />
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <div className="text-sm font-medium">{item.label}</div>
            {item.soon && <span className="rounded-full border px-1.5 py-0.5 text-[10px] text-gray-600">soon</span>}
          </div>
          {active && (
            <div className="mt-1 h-1.5 w-36 rounded-full bg-gray-200">
              {/* bar only — no percentage text */}
              <div className="h-1.5 rounded-full bg-gray-900" style={{ width: `${Math.max(0, Math.min(100, progress))}%` }} />
            </div>
          )}
        </div>
      </div>
    </button>
  )
}

function calcProfilePct(facts: any) {
  let n = 0, have = 0
  const check = (v: any) => { n++; if (v && ((Array.isArray(v) && v.length) || (!Array.isArray(v)))) have++ }
  check(facts.businessName)
  check(facts.website)
  check(facts.industry)
  check(facts.employees)
  check(facts.objectives?.length)
  check(facts.channels?.length)
  check(facts.tools?.length)
  return Math.round((have / Math.max(1, n)) * 100)
}

function matchToolId(label: string) {
  const s = label.trim().toLowerCase()
  if (/analytics\s*4|ga4/.test(s)) return 'ga4'
  if (/tag manager|gtm/.test(s)) return 'gtm'
  if (/search console|gsc/.test(s)) return 'gsc'
  if (/meta\s*pixel|facebook\s*pixel/.test(s)) return 'meta_pixel'
  if (/sheets/.test(s)) return 'sheets'
  if (/zapier/.test(s)) return 'zapier'
  if (/plaud/.test(s)) return 'plaud'
  if (/semrush/.test(s)) return 'semrush'
  return s.replace(/\s+/g,'_')
}
