// /coolbits/app/api/chat/route.ts
import { NextRequest, NextResponse } from 'next/server'
import OpenAI from 'openai'

export const runtime = 'nodejs'
export const dynamic = 'force-dynamic'

type UiMsg = { role: 'user' | 'assistant'; content: string }

const MODEL = process.env.MODEL_OPENAI ?? 'gpt-4o-mini'
const ASSISTANT_NAME = process.env.NEXT_PUBLIC_ASSISTANT_NAME ?? 'Andy'
const OPENAI_API_KEY = process.env.OPENAI_API_KEY ?? ''
const openai = OPENAI_API_KEY ? new OpenAI({ apiKey: OPENAI_API_KEY }) : null

function json(data: any, status = 200) {
  return NextResponse.json(data, { status, headers: { 'Cache-Control': 'no-store' } })
}

export async function GET(req: NextRequest) {
  if (req.nextUrl.searchParams.get('ping')) return json({ ok: true, pong: true, ts: Date.now() })
  return json({ ok: true, info: 'POST a message to this route.' })
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json().catch(() => ({} as any))

    const userMsgRaw = body?.message ?? body?.text ?? body?.content ?? ''
    const userMsg = String(userMsgRaw || '').trim()
    const history: UiMsg[] = Array.isArray(body?.messages) ? body.messages
                      : Array.isArray(body?.history)   ? body.history : []
    const factsDigest: string = typeof body?.factsDigest === 'string' ? body.factsDigest : ''

    // NEW: language coming from client (default EN)
    const lang: 'en' | 'ro' = body?.lang === 'ro' ? 'ro' : 'en'
    const LANG_LABEL = lang === 'ro' ? 'Romanian' : 'English'

    if (!userMsg) return json({ success: false, message: 'Missing "message"' }, 400)

    const system = [
      `You are ${ASSISTANT_NAME}, a concise, friendly digital marketing co-pilot.`,
      `OUTPUT LANGUAGE: ${LANG_LABEL}.`,
      `STRICT: Do NOT mix languages. Keep ${LANG_LABEL} for the whole reply.`,
      `Only switch languages if the user explicitly requests it (e.g., "switch to Romanian" / "vorbește în română").`,
      `Use FACTS_DUMP for business data; never invent values. If something is missing, ask one short follow-up.`,
      `Avoid repeating onboarding questions if info already exists.`,
      '',
      'FACTS_DUMP:',
      factsDigest || '(none yet)',
    ].join('\n')

    let answer = `Dev mode (no API key). I received: "${userMsg}".`
    let usage: { prompt_tokens: number; completion_tokens: number; total_tokens: number } | null = null

    if (openai) {
      const r = await openai.chat.completions.create({
        model: MODEL,
        temperature: 0.3,
        messages: [
          { role: 'system', content: system },
          ...history.map(m => ({ role: m.role, content: m.content }) as const),
          { role: 'user', content: userMsg } as const,
        ],
      })
      answer = r.choices?.[0]?.message?.content?.trim() || 'Okay.'
      usage = r.usage
        ? {
            prompt_tokens: r.usage.prompt_tokens ?? 0,
            completion_tokens: r.usage.completion_tokens ?? 0,
            total_tokens: r.usage.total_tokens ?? 0,
          }
        : null
    }

    return json({
      success: true,
      message: answer,
      answer,
      usage,
      model: MODEL,
      data: { message: answer, usage, model: MODEL },
    })
  } catch (err: any) {
    console.error('/api/chat error', err)
    return json({ success: false, message: err?.message || 'Server error' }, 500)
  }
}
