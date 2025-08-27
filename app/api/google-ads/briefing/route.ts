// app/api/google-ads/briefing/route.ts
import { NextRequest, NextResponse } from 'next/server'
import OpenAI from 'openai'

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY })

export async function POST(req: NextRequest) {
  try {
    const { summary, factsDigest } = await req.json()

    const model = process.env.MODEL_OPENAI || 'gpt-4o-mini'
    const system = [
      'You are a specialized Google Ads agent.',
      'Produce a concise, highly actionable briefing for a marketing copilot named Andy.',
      'Focus on: status (linking/oAuth), key config (budget/campaign types/conversions/audiences/locations), quick wins, gaps, next steps.',
      'Write crisp bullet points. 200–300 words max.',
    ].join(' ')

    const user = [
      '=== FACTS DIGEST ===',
      factsDigest || '(none)',
      '=== ECOSYSTEM SUMMARY ===',
      JSON.stringify(summary || {}, null, 2),
      '=== OUTPUT FORMAT ===',
      '# Google Ads Briefing',
      '## Status',
      '• …',
      '## Key Signals',
      '• …',
      '## Quick Wins',
      '• …',
      '## Gaps',
      '• …',
      '## Next Steps',
      '• …',
    ].join('\n')

    const resp = await openai.chat.completions.create({
      model,
      messages: [
        { role: 'system', content: system },
        { role: 'user', content: user }
      ],
      temperature: 0.3,
    })

    const text = resp.choices?.[0]?.message?.content?.trim() || 'Briefing unavailable.'
    return NextResponse.json({ ok: true, briefing: text })
  } catch (e: any) {
    return NextResponse.json({ ok: false, error: e?.message || 'error' }, { status: 500 })
  }
}
