'use client'
import { useState } from 'react'

type Tab = 'overview' | 'structure' | 'assets' | 'insights' | 'sync'

export default function GoogleAdsWorkspace() {
  const [tab, setTab] = useState<Tab>('overview')

  return (
    <div className="p-4">
      <div className="mb-3 flex gap-2 border-b">
        {(['overview','structure','assets','insights','sync'] as Tab[]).map(t => (
          <button key={t}
            onClick={() => setTab(t)}
            className={`px-3 py-2 text-sm border-b-2 ${tab===t?'border-primary-600 text-primary-700':'border-transparent text-gray-600 hover:text-gray-800'}`}>
            {t[0].toUpperCase()+t.slice(1)}
          </button>
        ))}
      </div>

      {tab === 'overview' && (
        <div className="space-y-3">
          <h3 className="font-semibold">Overview</h3>
          <p className="text-sm text-gray-600">Connect account, define goals, budgets, geos.</p>
          {/* CTA to connect / or show account status */}
          <div className="rounded border p-3">
            <div className="flex items-center justify-between">
              <div className="text-sm">Account: <span className="text-gray-500">(not connected)</span></div>
              <a href="/api/integrations/google/start" className="rounded bg-primary-600 px-3 py-1.5 text-sm text-white">Connect Google Ads</a>
            </div>
          </div>
        </div>
      )}

      {tab === 'structure' && (
        <div className="space-y-3">
          <h3 className="font-semibold">Structure</h3>
          <p className="text-sm text-gray-600">Campaigns → Ad groups → Keywords. Upload or add manually.</p>
          <div className="rounded border p-3 text-sm">
            <button className="rounded border px-2 py-1 text-xs">+ Campaign</button>
            {/* Later: list, drawers for campaign → ad group → keyword */}
          </div>
        </div>
      )}

      {tab === 'assets' && (
        <div className="space-y-3">
          <h3 className="font-semibold">Assets</h3>
          <p className="text-sm text-gray-600">Generate RSAs, callouts, sitelinks, snippets with guardrails.</p>
          <div className="rounded border p-3 text-sm">
            <button className="rounded bg-primary-600 px-2 py-1 text-xs text-white">Generate RSA Suggestions</button>
          </div>
        </div>
      )}

      {tab === 'insights' && (
        <div className="space-y-3">
          <h3 className="font-semibold">Insights</h3>
          <p className="text-sm text-gray-600">Drop reports (CSV) for analysis; we’ll surface actions.</p>
          <div className="rounded border p-3 text-sm">
            <input type="file" className="text-xs" />
          </div>
        </div>
      )}

      {tab === 'sync' && (
        <div className="space-y-3">
          <h3 className="font-semibold">Sync</h3>
          <p className="text-sm text-gray-600">Pick accounts to sync, schedule pulls, view logs.</p>
          <div className="rounded border p-3 text-sm">Coming soon.</div>
        </div>
      )}
    </div>
  )
}
