// /coolbits/app/api/submit/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { leadSchema } from '@/schemas/lead'
import { prisma } from '@/lib/db'
import { sendWelcomeEmail, sendNotificationEmail } from '@/lib/email'
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

// Health check (optional): GET /api/submit
export async function GET() {
  return json({ ok: true })
}

export async function POST(request: NextRequest) {
  return withRateLimit(request, 'leadSubmission', async () => {
    try {
      const body = await request.json().catch(() => null)
      if (!body || typeof body !== 'object') {
        return json(createApiResponse(false, 'Invalid JSON body'), 400)
      }

      // Validate input
      const parsed = leadSchema.safeParse(body)
      if (!parsed.success) {
        const errors = parsed.error.errors.map(e => e.message)
        return json(
          createApiResponse(false, 'Validation failed', undefined, errors),
          400
        )
      }

      const leadData = parsed.data

      // Prevent duplicates (and avoid race issues with a pre-check)
      const existing = await prisma.lead.findUnique({
        where: { email: leadData.email },
      })
      if (existing) {
        return json(
          createApiResponse(false, 'A lead with this email already exists'),
          409
        )
      }

      // Create lead in DB
      const lead = await prisma.lead.create({ data: leadData })

      // Log
      try {
        // e.g., logger.logLeadSubmission may be optional
        // @ts-ignore - safe if your logger has this method
        logger?.logLeadSubmission?.(leadData)
      } catch (e) {
        logger?.error?.('Logger error on lead submission', { e, leadId: lead.id })
      }

      // Fire-and-forget emails (do not block the response)
      const adminEmail = process.env.ADMIN_EMAIL || 'admin@coolbits.ro'
      Promise.allSettled([
        sendWelcomeEmail(leadData),
        sendNotificationEmail(leadData, adminEmail),
      ]).catch(err => {
        logger?.error?.('Email dispatch error', { err, leadId: lead.id })
      })

      return json(
        createApiResponse(true, 'Lead submitted successfully', { leadId: lead.id }),
        201
      )
    } catch (error: any) {
      logger?.error?.('Lead submission error', { error })
      return json(createApiResponse(false, 'Internal server error'), 500)
    }
  })
}
