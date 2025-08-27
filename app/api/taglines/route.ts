// /coolbits/app/api/taglines/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { generateTaglines, generatePrompts } from '@/utils/nlpProcessor'
import { withRateLimit } from '@/lib/rateLimit'
import { createApiResponse } from '@/lib/validation'
import logger from '@/lib/logger'

export const runtime = 'nodejs'
export const dynamic = 'force-dynamic'

function json(data: any, status = 200) {
  return NextResponse.json(data, {
    status,
    headers: { 'Cache-Control': 'no-store' },
  })
}

type TaglinesPayload = {
  type?: string
  industry?: string
  companyName?: string
  description?: string
  tone?: string
  length?: 'short' | 'medium' | 'long' | string
  [k: string]: any
}

type PromptsPayload = {
  type?: string
  context?: string
  goal?: string
  audience?: string
  style?: string
  length?: 'short' | 'detailed' | string
  [k: string]: any
}

// GET /api/taglines  → health & mini-doc
export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url)
  const type = (searchParams.get('type') || '').toLowerCase()

  if (type === 'taglines') {
    return json(
      createApiResponse(true, 'Tagline generation endpoint', {
        endpoint: '/api/taglines',
        method: 'POST',
        requiredFields: ['type', 'industry', 'companyName', 'description', 'tone', 'length'],
        example: {
          type: 'taglines',
          industry: 'Technology',
          companyName: 'TechCorp',
          description: 'Innovative software solutions for modern businesses',
          tone: 'confident',
          length: 'short',
        },
      }),
    )
  }
  if (type === 'prompts') {
    return json(
      createApiResponse(true, 'Prompt generation endpoint', {
        endpoint: '/api/taglines',
        method: 'POST',
        requiredFields: ['type', 'context', 'goal', 'audience', 'style', 'length'],
        example: {
          type: 'prompts',
          context: 'Business strategy consultation',
          goal: 'Generate strategic recommendations',
          audience: 'C-level executives',
          style: 'formal',
          length: 'detailed',
        },
      }),
    )
  }

  return json(createApiResponse(true, 'NLP Processing API OK', { ok: true, ts: Date.now() }))
}

// POST /api/taglines  → main handler
export async function POST(request: NextRequest) {
  return withRateLimit(request, 'api-taglines', async () => {
    try {
      const body = await request.json().catch(() => null)
      if (!body || typeof body !== 'object') {
        return json(createApiResponse(false, 'Invalid JSON body'), 400)
      }

      // Acceptă și valori “aproximate” (ex. TagLines / TAGLINES / generate_taglines)
      const rawType = String(body.type || '').trim()
      const normalized = rawType.toLowerCase().replace(/[\s_-]+/g, '')
      const type: 'taglines' | 'prompts' | '' =
        normalized === 'taglines'
          ? 'taglines'
          : normalized === 'prompts'
          ? 'prompts'
          : ('' as const)

      if (!type) {
        return json(
          createApiResponse(false, 'Invalid type. Must be "taglines" or "prompts"'),
          400,
        )
      }

      if (type === 'taglines') {
        const data = body as TaglinesPayload
        const required = ['industry', 'companyName', 'description', 'tone', 'length'] as const
        const missing = required.filter((k) => !String((data as any)[k] || '').trim())

        if (missing.length) {
          return json(
            createApiResponse(false, `Missing fields: ${missing.join(', ')}`),
            400,
          )
        }

        const result = await generateTaglines(data)

        try {
          ;(logger as any)?.info?.('Taglines generated successfully', {
            company: data.companyName,
            industry: data.industry,
          })
        } catch {}

        // compat: includem și un câmp `answer` dacă frontul îl așteaptă
        return json(
          createApiResponse(true, 'Taglines generated successfully', {
            ...result,
            answer: result?.taglines ?? result, // fallback
          }),
        )
      }

      // type === 'prompts'
      const data = body as PromptsPayload
      const required = ['context', 'goal', 'audience', 'style', 'length'] as const
      const missing = required.filter((k) => !String((data as any)[k] || '').trim())

      if (missing.length) {
        return json(
          createApiResponse(false, `Missing fields: ${missing.join(', ')}`),
          400,
        )
      }

      const result = await generatePrompts(data)

      try {
        ;(logger as any)?.info?.('Prompts generated successfully', {
          goal: data.goal,
          audience: data.audience,
        })
      } catch {}

      return json(
        createApiResponse(true, 'Prompts generated successfully', {
          ...result,
          answer: result?.prompts ?? result,
        }),
      )
    } catch (error: any) {
      try {
        ;(logger as any)?.error?.('NLP processing error', { error })
      } catch {}
      return json(createApiResponse(false, 'Failed to process request'), 500)
    }
  })
}
