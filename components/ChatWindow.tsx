'use client'

import { useEffect, useRef, useState, useCallback } from 'react'
import MessageInput from '@/components/MessageInput'
import type { ChatMessage } from '@/schemas/chat'
import type { PartialFacts } from '@/lib/facts/types'
import { useFacts } from '@/lib/facts/store'
import { parseFactsFromMessage } from '@/lib/facts/parser'
import { buildFactsDigest } from '@/lib/facts/digest'
import { isCbmlBlock, runCbml } from '@/lib/cb/cbml'

const ASSISTANT_NAME = process.env.NEXT_PUBLIC_ASSISTANT_NAME || 'Andy'
type ModelName = 'andy'

type Step =
  | 'GREETING'
  | 'OWN_BUSINESS'
  | 'BUSINESS_NAME'
  | 'WEBSITE'
  | 'INDUSTRY'
  | 'EMPLOYEES'
  | 'CHANNELS'
  | 'OBJECTIVES'
  | 'TOOLS'
  | 'OTHER_DETAILS'
  | 'NAME'
  | 'EMAIL'
  | 'PHONE'
  | 'READY'
  | 'FREECHAT'

/* ====================== UI bits (define first) ====================== */
function Card({ children }: { children: React.ReactNode }) {
  return <div className="rounded-md border bg-white p-3">{children}</div>
}

function Bubble({ role, text }: { role: 'user' | 'assistant'; text: string }) {
  const isUser = role === 'user'
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[75%] whitespace-pre-wrap rounded-lg px-3 py-2 text-sm ${isUser ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-900'}`}
        dangerouslySetInnerHTML={{ __html: text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>') }}
      />
    </div>
  )
}

function QuickField({
  label, placeholder, cta, onConfirm,
}: { label: string; placeholder?: string; cta?: string; onConfirm: (v: string) => void }) {
  const [v, setV] = useState('')
  return (
    <Card>
      <div className="mb-2 text-sm text-gray-800">{label}</div>
      <div className="flex items-center gap-2">
        <input
          className="h-10 flex-1 rounded-lg border bg-white px-3 text-sm outline-none focus:ring-2 focus:ring-primary-300"
          placeholder={placeholder}
          value={v}
          onChange={(e) => setV(e.target.value)}
        />
        <button
          className="h-10 rounded-lg bg-primary-600 px-3 text-sm font-medium text-white disabled:opacity-50"
          onClick={() => onConfirm(v)}
          disabled={!v.trim()}
        >
          {cta || 'Confirm'}
        </button>
      </div>
    </Card>
  )
}

function QuickChips({
  title, items, onAdd, placeholder, onContinue,
}: { title: string; items: string[]; onAdd: (v: string) => void; placeholder?: string; onContinue?: () => void }) {
  const [custom, setCustom] = useState('')
  return (
    <Card>
      <div className="mb-2 text-sm text-gray-800">{title}</div>
      <div className="mb-2 flex flex-wrap gap-2">
        {items.map((it) => (
          <button key={it} onClick={() => onAdd(it)} className="rounded-full border bg-white px-2.5 py-1 text-xs hover:bg-gray-50">
            {it}
          </button>
        ))}
      </div>
      <div className="flex items-center gap-2">
        <input
          className="h-9 flex-1 rounded-lg border bg-white px-3 text-sm outline-none focus:ring-2 focus:ring-primary-300"
          placeholder={placeholder || 'Add…'}
          value={custom}
          onChange={(e) => setCustom(e.target.value)}
        />
        <button
          onClick={() => { const t = custom.trim(); if (t) onAdd(t); setCustom('') }}
          disabled={!custom.trim()}
          className="h-9 rounded-lg border bg-white px-3 text-sm hover:bg-gray-50 disabled:opacity-50"
        >
          Confirm
        </button>
        {onContinue && (
          <button onClick={onContinue} className="h-9 rounded-lg bg-primary-600 px-3 text-sm font-medium text-white">
            Continue
          </button>
        )}
      </div>
    </Card>
  )
}

function Wizard(props: {
  step: Step
  onYes: () => void
  onNo: () => void
  confirmBusinessName: (v: string) => void
  confirmWebsite: (v: string) => void
  confirmIndustry: (v: string) => void
  confirmEmployees: (v: string) => void
  addChannel: (v: string) => void
  addObjective: (v: string) => void
  addTool: (v: string) => void
  confirmOtherDetails: (v: string) => void
  confirmName: (v: string) => void
  confirmEmail: (v: string) => void
  confirmPhone: (v: string) => void
  toNext: (s: Step) => void
  onTalkToAndy: () => void
  otherDetailsInput: string
  setOtherDetailsInput: (v: string) => void
}) {
  const { step } = props
  return (
    <div className="space-y-3">
      {step === 'GREETING' && (
        <Card>
          <div className="mb-2 text-sm text-gray-800">How can we help today? Let’s get to know your business.</div>
          <div className="flex gap-2">
            <button className="rounded bg-primary-600 px-3 py-1 text-sm text-white" onClick={() => props.toNext('OWN_BUSINESS')}>
              Get started
            </button>
          </div>
        </Card>
      )}

      {step === 'OWN_BUSINESS' && (
        <Card>
          <div className="mb-2 text-sm text-gray-800">Do you own a business or website?</div>
          <div className="flex gap-2">
            <button className="rounded bg-primary-600 px-3 py-1 text-sm text-white" onClick={props.onYes}>Yes</button>
            <button className="rounded border bg-white px-3 py-1 text-sm" onClick={props.onNo}>No</button>
          </div>
        </Card>
      )}

      {step === 'BUSINESS_NAME' && (
        <QuickField label="What is your brand or company name?" placeholder="e.g., CoolBits" cta="Confirm" onConfirm={props.confirmBusinessName} />
      )}
      {step === 'WEBSITE' && (
        <QuickField label="What is your website?" placeholder="e.g., coolbits.ai" cta="Confirm" onConfirm={props.confirmWebsite} />
      )}
      {step === 'INDUSTRY' && (
        <QuickField label="Which industry are you in?" placeholder="e.g., Digital marketing / E-commerce / SaaS" cta="Confirm" onConfirm={props.confirmIndustry} />
      )}
      {step === 'EMPLOYEES' && (
        <QuickField label="How many employees?" placeholder="e.g., 10 or 10-20" cta="Confirm" onConfirm={props.confirmEmployees} />
      )}
      {step === 'CHANNELS' && (
        <QuickChips
          title="Which channels do you use?"
          items={[
            'Google Ads', 'Meta Ads', 'TikTok Ads', 'LinkedIn Ads', 'X Ads',
            'Organic (SEO)', 'Email', 'Referral', 'AI Optimization', 'None',
          ]}
          onAdd={props.addChannel}
          placeholder="Add another channel…"
          onContinue={() => props.toNext('OBJECTIVES')}
        />
      )}
      {step === 'OBJECTIVES' && (
        <QuickChips
          title="What are your primary marketing goals?"
          items={['Leads', 'Sales', 'Traffic', 'Brand Awareness', 'Engagement']}
          onAdd={props.addObjective}
          placeholder="Add another goal…"
          onContinue={() => props.toNext('TOOLS')}
        />
      )}
      {step === 'TOOLS' && (
        <QuickChips
          title="Which tools are in place?"
          items={['Google Analytics 4', 'Google Tag Manager', 'Google Search Console', 'Meta Pixel', 'None']}
          onAdd={props.addTool}
          placeholder="Add another tool…"
          onContinue={() => props.toNext('OTHER_DETAILS')}
        />
      )}

      {step === 'OTHER_DETAILS' && (
        <Card>
          <div className="mb-2 text-sm text-gray-800">Any other important details about your business?</div>
          <textarea
            className="w-full rounded-md border px-3 py-2 text-sm"
            rows={3}
            placeholder="(Optional) e.g., target audience, challenges, seasonality, etc."
            value={props.otherDetailsInput}
            onChange={(e) => props.setOtherDetailsInput(e.target.value)}
          />
          <div className="mt-2 flex justify-end gap-2">
            <button className="rounded border bg-white px-3 py-1 text-sm" onClick={() => props.confirmOtherDetails('')}>Skip</button>
            <button className="rounded bg-primary-600 px-3 py-1 text-sm text-white" onClick={() => props.confirmOtherDetails(props.otherDetailsInput)}>Continue</button>
          </div>
        </Card>
      )}

      {step === 'NAME'  && <QuickField label="What's your name?" placeholder="e.g., John Doe" cta="Confirm" onConfirm={props.confirmName} />}
      {step === 'EMAIL' && <QuickField label="What email can we reach you at?" placeholder="e.g., john@example.com" cta="Confirm" onConfirm={props.confirmEmail} />}
      {step === 'PHONE' && <QuickField label="What's your phone number? (optional)" placeholder="e.g., +40 7xx xxx xxx" cta="Finish" onConfirm={props.confirmPhone} />}

      {step === 'READY' && (
        <Card>
          <div className="mb-2 text-sm text-gray-800">
            All set! You can now start chatting with {ASSISTANT_NAME}. I’ll personalize the greeting based on your details.
          </div>
          <button className="rounded bg-primary-600 px-3 py-2 text-sm font-medium text-white" onClick={props.onTalkToAndy}>
            Talk to {ASSISTANT_NAME}
          </button>
        </Card>
      )}
    </div>
  )
}

/* small util */
function escapeHtml(s: string) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
}

/* ====================== Main component ====================== */
export default function ChatWindow({ className = '' }: { className?: string }) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [step, setStep] = useState<Step>('GREETING')
  const [sessionId] = useState<string>(() => `sess_${Date.now()}`)
  const [lang, setLang] = useState<'en' | 'ro'>('en')
  const scrollRef = useRef<HTMLDivElement>(null)
  const idSeq = useRef(0)
  const nextId = () => `${Date.now()}_${idSeq.current++}`

  const [otherDetailsInput, setOtherDetailsInput] = useState('')
  const { facts, upsertManual } = useFacts()

  useEffect(() => {
    const el = scrollRef.current
    if (el) el.scrollTop = el.scrollHeight
  }, [messages, step])

  const pushAssistant = (content: string, meta?: any) => {
    setMessages(prev => [
      ...prev,
      {
        id: `a_${nextId()}`,
        role: 'assistant',
        content,
        createdAt: new Date(),
        model: 'andy' as ModelName,
        sessionId,
        metadata: meta,
      },
    ])
  }

  const pushUser = (content: string): { parsed: PartialFacts } => {
    const parsed = parseFactsFromMessage(content)
    if (Object.keys(parsed).length) upsertManual(parsed)
    setMessages(prev => [
      ...prev,
      {
        id: `u_${nextId()}`,
        role: 'user',
        content,
        createdAt: new Date(),
        model: 'andy',
        sessionId,
      },
    ])
    return { parsed }
  }

  const next = (s: Step) => setStep(s)

  const autoAdvance = (parsed: PartialFacts) => {
    switch (step) {
      case 'BUSINESS_NAME':
        if (parsed.businessName) { next('WEBSITE'); pushAssistant('Thanks! What is your website?') }
        break
      case 'WEBSITE':
        if (parsed.website) { next('INDUSTRY'); pushAssistant('Great — which industry are you in?') }
        break
      case 'INDUSTRY':
        if (parsed.industry) { next('EMPLOYEES'); pushAssistant('How many employees? (e.g., 10 or 10-20)') }
        break
      case 'EMPLOYEES':
        if (typeof parsed.employees !== 'undefined') { next('CHANNELS'); pushAssistant('Which channels do you use?') }
        break
      case 'CHANNELS':
        if (parsed.channels?.length) { next('OBJECTIVES'); pushAssistant('Noted. What are your primary goals?') }
        break
      case 'OBJECTIVES':
        if (parsed.objectives?.length) { next('TOOLS'); pushAssistant('Good. Which tools are in place? (GA4/GTM/GSC/Pixel)') }
        break
      case 'TOOLS':
        if (parsed.tools?.length) {
          next('OTHER_DETAILS')
          pushAssistant('Awesome. Any other important details about your business you’d like to add?')
        }
        break
      case 'NAME':
        if ((parsed as any).contactName) {
          next('EMAIL')
          pushAssistant(`Thanks, **${(parsed as any).contactName}**. What email can we reach you at?`)
        }
        break
      case 'EMAIL':
        if ((parsed as any).contactEmail) {
          next('PHONE')
          pushAssistant('Got it. What’s your phone number? (optional)')
        }
        break
      case 'PHONE':
        next('READY')
        break
      default:
        break
    }
  }

  const greetUser = () => {
    const name = (facts as any).contactName ? `, ${(facts as any).contactName}` : ''
    const biz = facts.businessName ? `**${facts.businessName}**` : 'your business'
    const industry = facts.industry ? ` in the **${facts.industry}** industry` : ''
    const goal = facts.objectives?.[0] ?? null
    const channel = facts.channels?.[0] ?? null

    let intro = `Hi${name}! I’m ${ASSISTANT_NAME}. `
    intro += `I see you run ${biz}${industry}. `
    if (goal && channel) {
      intro += `Your primary goal is **${goal}**, and you’re using **${channel}**. `
    } else if (goal) {
      intro += `Your primary goal is **${goal}**. `
    }
    intro += 'Ask me anything about your marketing. On the right, you can **Generate Basic Briefing** or trigger a **Deep Current Analysis (Kim)** when ready.'
    pushAssistant(intro)
  }

  // send to model (with optional silent mode)
  const sendToModel = useCallback(async (text: string, options?: { silent?: boolean; tag?: string }) => {
    const silent = !!options?.silent
    if (!silent) setIsLoading(true)
    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sessionId,
          message: text,
          messages: messages.slice(-10),
          factsDigest: buildFactsDigest(facts),
          lang,
        }),
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      const reply = data?.data?.message ?? data?.answer ?? data?.message ?? 'Okay.'
      const usage = data?.usage || data?.data?.usage || null
      if (!silent) pushAssistant(reply, { usage })
      return { reply, usage }
    } catch (e) {
      console.error(e)
      if (!silent) pushAssistant('Sorry, I hit an error. Please try again.', { error: true })
      return { error: String(e) }
    } finally {
      if (!silent) setIsLoading(false)
    }
  }, [facts, lang, messages, sessionId])

  const renderCbmlSummary = (res: Awaited<ReturnType<typeof runCbml>>) => {
    const lines = res.steps.map((s) => {
      const ok = s.status === 'ok' ? '✅' : '❌'
      return `${ok} **${s.action}** — ${s.status}${s.info ? `\n<pre>${escapeHtml(JSON.stringify(s.info, null, 2))}</pre>` : ''}`
    })
    return [
      `**cbML executed** (${res.ok ? 'all good' : 'with errors'}).`,
      ...lines,
    ].join('\n\n')
  }

  const handleSendMessage = async (text: string) => {
    // language switches
    if (/^(switch to romanian|vorbește în română|vorbeste in romana)$/i.test(text.trim())) {
      setLang('ro'); pushAssistant('Language switched to Romanian. (Write again to continue.)'); return
    }
    if (/^(switch to english|schimbă pe engleză|schimba pe engleza)$/i.test(text.trim())) {
      setLang('en'); pushAssistant('Language switched to English. (Write again to continue.)'); return
    }

    // cbML: /cb …   sau   ```cbml … ```
    const isSlashCb = text.trim().toLowerCase().startsWith('/cb ')
    if (isSlashCb || isCbmlBlock(text)) {
      // păstrăm mesajul în istoric, dar nu parsăm facts din el
      setMessages(prev => [...prev, {
        id: `u_${nextId()}`, role: 'user', content: text, createdAt: new Date(), model: 'andy', sessionId,
      }])
      const raw = isSlashCb ? text.trim().slice(3).trim() : text
      const res = await runCbml(raw)
      pushAssistant(renderCbmlSummary(res))
      return
    }

    // normal flow
    const { parsed } = pushUser(text)
    if (step !== 'FREECHAT') {
      autoAdvance(parsed)
    } else {
      await sendToModel(text)
    }
  }

  // ===== Event: Generate Basic Briefing =====
  useEffect(() => {
    const handler = () => {
      if (step !== 'FREECHAT') {
        pushAssistant('Finish onboarding first, then hit **Talk to Andy** to start chatting. After that, use **Generate Basic Briefing** anytime.')
        return
      }
      const prompt = [
        'Create a concise **Basic Current Status Briefing** using my Business Map facts.',
        'Structure:',
        '1) Company snapshot (1–2 lines)',
        '2) Channels in use + quick health notes',
        '3) Tracking status & gaps',
        '4) Top 5 quick wins (bullets, imperative, measurable)',
        '5) Next recommended step (single line CTA)',
        'Keep it short and actionable.',
      ].join('\n')
      sendToModel(prompt)
    }
    window.addEventListener('cb:basic-briefing', handler as EventListener)
    return () => window.removeEventListener('cb:basic-briefing', handler as EventListener)
  }, [step, sendToModel])

  // ===== Event: Deep Current Analysis (Kim via xAI) =====
  useEffect(() => {
    const handler = (e: any) => {
      const { jobId, error, engine } = (e?.detail || {}) as { jobId?: string; error?: string; engine?: string }
      if (error) {
        pushAssistant(`Deep analysis could not start: **${error}**`)
        return
      }
      pushAssistant(`Deep Current Analysis started (${engine ?? 'Kim'}). Job ID: \`${jobId || 'n/a'}\`. I’ll incorporate results when ready.`)
    }
    window.addEventListener('cb:deep-analysis-started', handler as EventListener)
    return () => window.removeEventListener('cb:deep-analysis-started', handler as EventListener)
  }, [])

  // ===== Event: Ecosystem session summary → silent update către model =====
  useEffect(() => {
    const handler = (e: any) => {
      const { channel, summary } = (e?.detail || {}) as { channel?: string; summary?: any }
      const label = channel ? channel.replace(/_/g, ' ') : 'ecosystem'
      const sys = [
        `SYSTEM NOTE: Ecosystem session closed: ${label}.`,
        `Session summary (JSON):`,
        '```json',
        JSON.stringify(summary ?? {}, null, 2),
        '```',
        'Update your working context. Do not respond.',
      ].join('\n')
      sendToModel(sys, { silent: true })
      pushAssistant(`Noted. I’ve logged updates from the **${label}** workspace.`)
    }
    window.addEventListener('cb:ecosystem-summary', handler as EventListener)
    return () => window.removeEventListener('cb:ecosystem-summary', handler as EventListener)
  }, [sendToModel])

  // ===== Event: Google Ads ecosystem briefing → show in chat =====
  useEffect(() => {
    const handler = (e: any) => {
      const d = e?.detail || {}
      if (d?.briefing) {
        pushAssistant(`**Google Ads Agent → ${ASSISTANT_NAME}:**\n\n${d.briefing}`)
      } else if (d?.error) {
        pushAssistant('Google Ads Agent: failed to generate briefing. Please try again.', { error: true })
      }
    }
    window.addEventListener('cb:ecosystem-briefing', handler as EventListener)
    return () => window.removeEventListener('cb:ecosystem-briefing', handler as EventListener)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const showWizard = step !== 'FREECHAT'

  return (
    <div className={`flex h-full w-full flex-col rounded-lg border bg-white shadow-sm ${className}`}>
      <div className="flex items-center justify-between border-b p-3">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary-100 text-primary-700">
            {ASSISTANT_NAME?.[0] ?? 'A'}
          </div>
          <div>
            <div className="text-sm font-semibold text-gray-900">{ASSISTANT_NAME}</div>
            <div className="text-xs text-gray-500">Your marketing co-pilot</div>
          </div>
        </div>
      </div>

      <div ref={scrollRef} className="flex-1 overflow-y-auto p-3">
        {showWizard && (
          <div className="sticky top-0 z-10">
            <div className="rounded-md border bg-gray-50 p-3 shadow-sm">
              <Wizard
                step={step}
                onYes={() => { pushAssistant('Great! Let’s capture a few quick details.'); setStep('BUSINESS_NAME') }}
                onNo={() => { pushAssistant("No worries. Let's start with your goals."); setStep('OBJECTIVES') }}
                confirmBusinessName={(v) => { const t = v.trim(); if (!t) return; upsertManual({ businessName: t }); pushAssistant(`Got it — set business name to **${t}**.`); setStep('WEBSITE') }}
                confirmWebsite={(v) => { const cleaned = v.trim().replace(/^https?:\/\//i, '').replace(/^www\./i, '').replace(/[\/#?].*$/, ''); if (!cleaned) return; upsertManual({ website: cleaned }); pushAssistant(`Thanks — website set to **${cleaned}**.`); setStep('INDUSTRY') }}
                confirmIndustry={(v) => { const t = v.trim(); if (!t) return; upsertManual({ industry: t }); pushAssistant(`Great — industry: **${t}**.`); setStep('EMPLOYEES') }}
                confirmEmployees={(v) => { const t = v.trim(); if (!t) return; const m = t.match(/^(\d{1,6})(?:\s*-\s*(\d{1,6}))?$/); const employees = m ? (m[2] ? `${m[1]}-${m[2]}` : parseInt(m[1], 10)) : t; upsertManual({ employees }); pushAssistant(`Noted — employees: **${typeof employees === 'number' ? employees : employees.toString()}**.`); setStep('CHANNELS') }}
                addChannel={(ch) => { upsertManual({ channels: [ch] }); pushAssistant(`Added **${ch}** to Channels.`) }}
                addObjective={(ob) => { upsertManual({ objectives: [ob] }); pushAssistant(`Added **${ob}** to Objectives.`) }}
                addTool={(tl) => { upsertManual({ tools: [tl] }); pushAssistant(`Added **${tl}** to Tools.`) }}
                confirmOtherDetails={(txt) => { const v = txt.trim(); if (v) upsertManual({ otherDetails: v }); setStep('NAME'); pushAssistant("Thanks. What's your name?") }}
                confirmName={(name) => { const v = name.trim(); if (!v) return; (upsertManual as any)({ contactName: v }); pushAssistant(`Nice to meet you, **${v}**. What's the best email for you?`); setStep('EMAIL') }}
                confirmEmail={(email) => { const v = email.trim(); if (!v) return; (upsertManual as any)({ contactEmail: v }); pushAssistant(`Perfect — we'll use **${v}**. Do you want to share a phone number? (optional)`); setStep('PHONE') }}
                confirmPhone={(phone) => { const v = phone.trim(); if (v) { (upsertManual as any)({ contactPhone: v }); pushAssistant(`Noted — phone: **${v}**.`) } else { pushAssistant('No problem, we’ll skip the phone number.') } setStep('READY') }}
                toNext={(s) => setStep(s)}
                onTalkToAndy={() => { greetUser(); setStep('FREECHAT') }}
                otherDetailsInput={otherDetailsInput}
                setOtherDetailsInput={setOtherDetailsInput}
              />
            </div>
          </div>
        )}

        <div className="mt-2 space-y-2">
          {messages.map(m => <Bubble key={m.id} role={m.role} text={m.content} />)}
        </div>
      </div>

      <div className="border-t p-3">
        <MessageInput
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
          placeholder={`Message ${ASSISTANT_NAME}…`}
        />
      </div>
    </div>
  )
}
