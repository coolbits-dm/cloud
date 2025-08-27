'use client'

import React, { useState, useEffect } from 'react'
import { setEcosystemSummary } from '@/lib/channels/session'

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="space-y-3">
      <h3 className="text-sm font-semibold text-gray-600">{title}</h3>
      <div className="rounded-2xl border p-4">{children}</div>
    </section>
  )
}

const TABS = ['overview','connect','uploads','tools','knowledge','settings'] as const
type Tab = typeof TABS[number]

export default function GoogleAdsEcosystem() {
  const [tab, setTab] = useState<Tab>('overview')
  useEffect(() => { setEcosystemSummary('google_ads', { viewedTab: tab }) }, [tab])

  return (
    <div className="p-2">
      <div className="mb-3 flex flex-wrap gap-2">
        {TABS.map(t => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`rounded-lg border px-3 py-1.5 text-sm ${tab===t ? 'bg-gray-900 text-white' : 'bg-white hover:bg-gray-50'}`}
          >
            {label(t)}
          </button>
        ))}
      </div>

      {tab === 'overview'  && <OverviewTab />}
      {tab === 'connect'   && <ConnectTab />}
      {tab === 'uploads'   && <UploadsTab />}
      {tab === 'tools'     && <ToolsTab />}
      {tab === 'knowledge' && <KnowledgeTab />}
      {tab === 'settings'  && <SettingsTab />}
    </div>
  )
}

function label(t: string) { return t.charAt(0).toUpperCase() + t.slice(1) }

function Badge({ children, variant='default' }: { children: React.ReactNode; variant?: 'default'|'secondary'|'outline' }) {
  const map: Record<string,string> = {
    default: 'bg-gray-900 text-white',
    secondary: 'bg-gray-100 text-gray-800 border',
    outline: 'bg-white text-gray-800 border',
  }
  return <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs ${map[variant]}`}>{children}</span>
}
function Button({ children, href, variant='default', ...rest }: any) {
  const cls = variant==='outline' ? 'border bg-white hover:bg-gray-50' : 'bg-gray-900 text-white hover:bg-black'
  if (href) return <a href={href} className={`inline-flex items-center rounded-md px-3 py-1.5 text-sm ${cls}`} {...rest}>{children}</a>
  return <button className={`inline-flex items-center rounded-md px-3 py-1.5 text-sm ${cls}`} {...rest}>{children}</button>
}

function OverviewTab() {
  const [status, setStatus] = useState<{ linked: boolean; accounts?: any[] } | null>(null)
  const [tools, setTools] = useState<{ connected: string[]; possible: string[]; score: number } | null>(null)

  useEffect(() => {
    fetch('/api/google-ads/auth/status').then(r=>r.json()).then((s) => {
      setStatus(s); setEcosystemSummary('google_ads', { linked: !!s?.linked, accounts: s?.accounts || [] })
    }).catch(() => setStatus({linked:false}))
    fetch('/api/tools/status?channel=google_ads').then(r=>r.json()).then((t) => {
      setTools(t); setEcosystemSummary('google_ads', { optimizationScore: t?.score, connectedTools: t?.connected })
    }).catch(()=>{})
  }, [])

  return (
    <div className="space-y-4">
      <Section title="Status">
        <div className="flex items-center gap-3 text-sm">
          <Badge variant={status?.linked ? 'default' : 'secondary'}>
            {status?.linked ? 'Linked' : 'Not linked'}
          </Badge>
          {status?.accounts?.length ? <span>{status.accounts.length} account(s) linked</span> : null}
        </div>
      </Section>
      <Section title="Optimization Score (tools)">
        <OptimizationBar connected={tools?.connected?.length ?? 0} total={tools?.possible?.length ?? 0} />
        <div className="mt-2 text-xs text-gray-500">
          Connected: {tools?.connected?.join(', ') || '—'}
        </div>
      </Section>
      <Section title="Quick Links">
        <div className="flex flex-wrap gap-2 text-sm">
          <Badge variant="secondary">MCC Dashboard</Badge>
          <Badge variant="outline">Budget Pacing</Badge>
          <Badge variant="outline">Bulk Uploads</Badge>
          <Badge variant="outline">Search Terms</Badge>
        </div>
      </Section>
    </div>
  )
}

function OptimizationBar({ connected, total }: { connected: number; total: number }) {
  const pct = total > 0 ? Math.round((connected / total) * 100) : 0
  return (
    <div className="w-full">
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-600">Tools connected</span>
        <span className="font-medium">{pct}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div className="bg-gray-900 h-2 rounded-full" style={{ width: `${pct}%` }}></div>
      </div>
    </div>
  )
}

function ConnectTab() {
  function onConnectClick() {
    setEcosystemSummary('google_ads', { action: 'oauth_start_clicked' })
  }
  return (
    <div className="space-y-4">
      <Section title="Google Ads OAuth">
        <div className="flex items-center gap-3">
          <Button href="/api/google-ads/oauth/start" onClick={onConnectClick}>Connect Google Ads</Button>
          <Button href="/api/google-ads/oauth/disconnect" variant="outline">Disconnect</Button>
        </div>
      </Section>
      <Section title="Linked Accounts">
        <div className="text-sm text-gray-500">(placeholder) Show MCC + customers after OAuth.</div>
      </Section>
    </div>
  )
}

function UploadsTab() {
  const [busy, setBusy] = useState(false)
  const [count, setCount] = useState(0)
  function onFiles(e: React.ChangeEvent<HTMLInputElement>) {
    const n = e.target.files?.length ?? 0
    setCount(n)
    setEcosystemSummary('google_ads', { chosenFiles: n })
  }
  return (
    <div className="space-y-4">
      <Section title="Upload CSV / XLSX / ZIP">
        <form
          className="flex flex-col gap-3"
          action="/api/google-ads/uploads"
          method="post"
          encType="multipart/form-data"
          onSubmit={() => { setBusy(true); setEcosystemSummary('google_ads', { uploadSubmitted: true }) }}
        >
          <input name="files" type="file" multiple accept=".csv,.xls,.xlsx,.zip" className="text-sm" onChange={onFiles} />
          <Button type="submit" disabled={busy}>{busy ? 'Uploading…' : `Upload${count ? ` (${count})` : ''}`}</Button>
        </form>
      </Section>
      <Section title="Recent Uploads">
        <div className="text-sm text-gray-500">(placeholder) List uploaded files with parse status.</div>
      </Section>
    </div>
  )
}

function ToolsTab() {
  return (
    <div className="space-y-4">
      <Section title="Workflows & Utilities">
        <div className="grid md:grid-cols-2 gap-3">
          <ToolCard title="Generate Bulk Upload CSV" desc="Create campaign/ad group/keyword updates in Google format.">
            <Button>Open</Button>
          </ToolCard>
          <ToolCard title="Budget Pacing" desc="Track daily spend vs. target by day-of-week and priorities.">
            <Button variant="outline">Open</Button>
          </ToolCard>
          <ToolCard title="Search Terms Explorer" desc="Aggregate, cluster, and curate negatives/candidates.">
            <Button variant="outline">Open</Button>
          </ToolCard>
          <ToolCard title="Negative Keyword Review" desc="Compare script vs. manual exclusions and revert.">
            <Button variant="outline">Open</Button>
          </ToolCard>
        </div>
      </Section>
    </div>
  )
}

function KnowledgeTab() {
  return (
    <div className="space-y-4">
      <Section title="Essential References">
        <ul className="list-disc ml-6 text-sm space-y-1">
          <li>Account Structure & Naming</li>
          <li>Conversion Setup (GTM + GA4)</li>
          <li>PMAX Asset Guidelines</li>
          <li>Search Campaign Standards</li>
          <li>Bulk Upload Templates</li>
          <li>Disapproval & Policy Playbook</li>
        </ul>
      </Section>
    </div>
  )
}

function SettingsTab() {
  return (
    <div className="space-y-4">
      <Section title="Configuration">
        <ul className="text-sm space-y-1">
          <li><code>GOOGLE_CLIENT_ID</code>, <code>GOOGLE_CLIENT_SECRET</code></li>
          <li><code>GOOGLE_ADS_DEVELOPER_TOKEN</code>, <code>GOOGLE_ADS_LOGIN_CUSTOMER_ID</code></li>
          <li>Redirect URI: <code>/api/google-ads/oauth/callback</code></li>
        </ul>
      </Section>
    </div>
  )
}

function ToolCard({ title, desc, children }: { title: string; desc: string; children?: React.ReactNode }) {
  return (
    <div className="rounded-2xl border p-4 space-y-2">
      <div className="font-medium">{title}</div>
      <div className="text-sm text-gray-500">{desc}</div>
      {children}
    </div>
  )
}
