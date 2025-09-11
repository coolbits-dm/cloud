import { NextRequest, NextResponse } from 'next/server'
import { leadSchema } from '@/schemas/lead'
import { prisma } from '@/lib/db'
import { sendWelcomeEmail, sendNotificationEmail } from '@/lib/email'
import { withRateLimit } from '@/lib/rateLimit'
import { createApiResponse } from '@/lib/validation'
import logger, { logLeadSubmission } from '@/lib/logger'

export async function POST(request: NextRequest) {
  return withRateLimit(request, 'leadSubmission', async () => {
    try {
      const body = await request.json()
      
      // Validate input
      const validation = leadSchema.safeParse(body)
      if (!validation.success) {
        return NextResponse.json(
          createApiResponse(false, 'Validation failed', undefined, validation.error.errors.map(e => e.message)),
          { status: 400 }
        )
      }

      const leadData = validation.data

      // Check if email already exists
      const existingLead = await prisma.lead.findUnique({
        where: { email: leadData.email }
      })

      if (existingLead) {
        return NextResponse.json(
          createApiResponse(false, 'A lead with this email already exists'),
          { status: 409 }
        )
      }

      // Create lead in database
      const lead = await prisma.lead.create({
        data: leadData
      })

      // Log the lead submission
      logLeadSubmission(leadData)

      // Send welcome email to lead
      try {
        await sendWelcomeEmail(leadData)
      } catch (emailError) {
        logger.error('Failed to send welcome email', { error: emailError, leadId: lead.id })
        // Don't fail the request if email fails
      }

      // Send notification email to admin
      try {
        const adminEmail = process.env.ADMIN_EMAIL || 'admin@coolbits.com'
        await sendNotificationEmail(leadData, adminEmail)
      } catch (emailError) {
        logger.error('Failed to send notification email', { error: emailError, leadId: lead.id })
        // Don't fail the request if email fails
      }

      return NextResponse.json(
        createApiResponse(true, 'Lead submitted successfully', { leadId: lead.id }),
        { status: 201 }
      )

    } catch (error) {
      logger.error('Lead submission error', { error })
      
      return NextResponse.json(
        createApiResponse(false, 'Internal server error'),
        { status: 500 }
      )
    }
  })
}
