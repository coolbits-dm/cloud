import { NextRequest, NextResponse } from 'next/server'
import { chatRequestSchema } from '@/schemas/chat'
import { chatWithJean } from '@/lib/ai'
import { withRateLimit } from '@/lib/rateLimit'
import { createApiResponse } from '@/lib/validation'
import { prisma } from '@/lib/db'
import logger from '@/lib/logger'

export async function POST(request: NextRequest) {
  return withRateLimit(request, 'chat', async () => {
    try {
      const body = await request.json()
      
      // Validate input
      const validation = chatRequestSchema.safeParse(body)
      if (!validation.success) {
        return NextResponse.json(
          createApiResponse(false, 'Validation failed', undefined, validation.error.errors.map(e => e.message)),
          { status: 400 }
        )
      }

      const chatRequest = validation.data

      // Get chat response from Jean
      const response = await chatWithJean(chatRequest)

      // Store messages in database
      try {
        // Store user message
        await prisma.chatMessage.create({
          data: {
            sessionId: response.sessionId,
            role: 'user',
            content: chatRequest.message,
            model: 'jean',
            metadata: {
              timestamp: new Date().toISOString(),
            }
          }
        })

        // Store assistant message
        await prisma.chatMessage.create({
          data: {
            sessionId: response.sessionId,
            role: 'assistant',
            content: response.message,
            model: 'jean',
            metadata: {
              timestamp: new Date().toISOString(),
              usage: response.usage,
            }
          }
        })
      } catch (dbError) {
        logger.error('Failed to store chat messages', { error: dbError, sessionId: response.sessionId })
        // Don't fail the request if database storage fails
      }

      // Log the chat interaction
      logger.logChatMessage('jean', response.sessionId, 'assistant', response.message.length)

      return NextResponse.json(
        createApiResponse(true, 'Chat response generated successfully', response),
        { status: 200 }
      )

    } catch (error) {
      logger.error('Jean chat error', { error })
      
      if (error instanceof Error && error.message.includes('Failed to get response from Jean')) {
        return NextResponse.json(
          createApiResponse(false, 'AI service temporarily unavailable. Please try again later.'),
          { status: 503 }
        )
      }

      return NextResponse.json(
        createApiResponse(false, 'Internal server error'),
        { status: 500 }
      )
    }
  })
}
