// components/analysis/DeepAnalysisModal.tsx
'use client'

import { useState } from 'react'
import { useDeepAnalysis } from '@/lib/analysis/deepStore'
import { useUsage } from '@/lib/billing/usage'

type Step = 'prepare' | 'running' | 'done'
type Engine = 'kim'

export default function DeepAnalysisModal() {
  const { isOpen, close } = useDeepAnalysis()
  const addUsage = useUsage(s => s.add)

  const [step, setStep] = useState<Step>('prepare')
  const [engine] = useState<Engine>('kim')
  const [includeWeb, setIncludeWeb] = useState(true)
  const [channels, setChannels] = useState<string[]>(['google_ads'])
  const [jobId, setJobId] = useState<string | null>(null)
  const [result, setResult] = useState<string>('')

  if (!isOpen) return null

  async function start() {
    try {
      const res = await fetch('/api/deep-analysis/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ engine, includeWeb, channels })
      }).then(r => r.json()).catch(() => ({} as any))

      const id = res?.jobId || crypto.randomUUID()
      setJobId(id)
      setStep('running')

      // notify right panel / chat header listeners
      window.dispatchEvent(new CustomEvent('cb:deep-analysis-started', {
        detail: { engine, jobId: id }
      }))

      // demo progress + token usage (simulated)
      let ticks = 0
      const int = setInterval(() => {
        ticks++
        // rough simulated usage while running (xAI)
        addUsage('xai', { inTokens: 1200, outTokens: 800 })
        if (ticks >= 4) {
          clearInterval(int)
          setResult(
            [
              'Deep analysis summary (preview)',
              '• 5 quick wins',
              '• 3 critical gaps',
              '• 30-60-90 roadmap (key milestones)',
              '(placeholder content)'
            ].join('\n')
          )
          setStep('done')
        }
      }, 900)
    } catch {
      // graceful no-op; modal stays open
    }
  }

  function toggleChannel(c: string, checked: boolean) {
    setChannels(prev => checked ? Array.from(new Set([...prev, c])) : prev.filter(x => x !== c))
  }

  function sendToAndy() {
    if (!result) return
    window.dispatchEvent(new CustomEvent('cb:analysis-briefing', {
      detail: { result, engine, jobId }
    }))
    // reset basic state for next open
    setStep('prepare')
    setResult('')
    setJobId(null)
    close()
  }

  function onClose() {
    // reset when user closes the modal
    setStep('prepare')
    setResult('')
    setJobId(null)
    close()
  }

  return (
    <div className="fixed inset-0 z-[120]">
      <div className="absolute inset-0 bg-black/40" onClick={onClose} />
      <div className="absolute inset-0 flex items-center justify-center p-4">
        <div className="w-full max-w-3xl rounded-2xl bg-white border shadow-xl">
          <div className="flex items-center justify-between border-b p-4">
            <div className="text-lg font-semibold">Deep Current Analysis</div>
            <button className="rounded-md border px-2 py-1 text-sm hover:bg-gray-50" onClick={onClose}>Close</button>
          </div>

          <div className="p-4 space-y-4">
            {step === 'prepare' && (
              <div className="space-y-5">
                <p className="text-sm text-gray-700">
                  I’ll run a deep audit with <strong>Kim</strong> (xAI). Choose scope & options; you’ll see a token estimate.
                </p>

                <div className="grid gap-4">
                  <div className="text-sm">
                    <div className="font-medium mb-2">Channels</div>
                    <div className="flex flex-wrap gap-2">
                      {['google_ads','meta_ads','seo','email','referral','ai_optimization'].map(c => (
                        <label key={c} className="inline-flex items-center gap-2 rounded-full border bg-white px-3 py-1 text-xs">
                          <input
                            type="checkbox"
                            checked={channels.includes(c)}
                            onChange={(e) => toggleChannel(c, e.target.checked)}
                          />
                          {c.replace(/_/g,' ')}
                        </label>
                      ))}
                    </div>
                  </div>

                  <div className="text-sm">
                    <label className="inline-flex items-center gap-2">
                      <input type="checkbox" checked={includeWeb} onChange={e => setIncludeWeb(e.target.checked)} />
                      Include web research
                    </label>
                  </div>
                </div>

                <div className="flex items-center justify-between text-sm">
                  <div className="text-gray-600">Engine: Kim (xAI)</div>
                  <EstimatorHint channels={channels} includeWeb={includeWeb} />
                </div>

                <div className="flex justify-end gap-2">
                  <button className="rounded-md border px-3 py-1.5 text-sm" onClick={onClose}>Cancel</button>
                  <button className="rounded-md bg-gray-900 text-white px-3 py-1.5 text-sm" onClick={start}>
                    Start analysis
                  </button>
                </div>
              </div>
            )}

            {step === 'running' && (
              <div className="space-y-4">
                <div className="text-sm">
                  Running deep analysis (Kim)… job <code>{jobId?.slice(0,8)}…</code>
                </div>
                <ProgressList />
                <div className="h-2 w-full rounded-full bg-gray-200 overflow-hidden">
                  <div className="h-2 bg-gray-900 animate-[progress_3s_ease-in-out_infinite]" style={{ width: '60%' }} />
                </div>
                <style jsx>{`
                  @keyframes progress {
                    0% { transform: translateX(-60%); }
                    50% { transform: translateX(0%); }
                    100% { transform: translateX(100%); }
                  }
                `}</style>
                <div className="text-xs text-gray-500">We’ll send the summary to Andy automatically when finished.</div>
              </div>
            )}

            {step === 'done' && (
              <div className="space-y-4">
                <div className="text-sm font-medium">Result preview</div>
                <div className="rounded-md border bg-gray-50 p-3 text-sm whitespace-pre-wrap">
                  {result}
                </div>
                <div className="flex justify-end gap-2">
                  <a
                    className="rounded-md border px-3 py-1.5 text-sm hover:bg-gray-50"
                    href={`/api/deep-analysis/export?id=${jobId}`}
                  >
                    Export PDF
                  </a>
                  <button
                    className="rounded-md bg-amber-600 text-white px-3 py-1.5 text-sm"
                    onClick={sendToAndy}
                  >
                    Send to Andy
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

function EstimatorHint({ channels, includeWeb }: { channels: string[]; includeWeb: boolean }) {
  // ultra-simple token estimate (client-side hint)
  const base = 6_000
  const perCh = 4_000 * Math.max(channels.length, 1)
  const web = includeWeb ? 8_000 : 0
  const est = base + perCh + web
  return <div className="text-xs text-gray-600">Est. tokens (xAI): ~{est.toLocaleString()}</div>
}

function ProgressList() {
  const steps = ['Collecting facts', 'Fetching public data', 'Channel audits', 'Drafting roadmap']
  return (
    <div className="space-y-2">
      {steps.map((s,i) => (
        <div key={s} className="flex items-center gap-2 text-sm">
          <span className={`inline-block h-2 w-2 rounded-full ${i<2 ? 'bg-green-500' : i===2 ? 'bg-amber-500' : 'bg-gray-300'}`} />
          <span>{s}</span>
        </div>
      ))}
    </div>
  )
}
