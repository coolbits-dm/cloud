import { NextRequest, NextResponse } from 'next/server'
import { chatRequestSchema } from '@/schemas/chat'
import { aCursor } from '@/lib/ai/acursor'
import { withRateLimit } from '@/lib/rateLimit'
import { createApiResponse } from '@/lib/validation'
import { prisma } from '@/lib/db'
import logger, { logChatMessage } from '@/lib/logger'

export async function POST(request: NextRequest) {
  return withRateLimit(request, 'chat', async () => {
    let chatRequest: any = null
    
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

      chatRequest = validation.data

      // Get chat response from aCursor (legacy Gelu endpoint now uses aCursor)
      const response = await aCursor.chatWithaCursor(chatRequest)

      // Store messages in database
      try {
        // Store user message
        await prisma.chatMessage.create({
          data: {
            sessionId: response.sessionId,
            role: 'user',
            content: chatRequest.message,
            model: 'gelu', // Keep legacy model name for database
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
            model: 'gelu', // Keep legacy model name for database
            metadata: {
              timestamp: new Date().toISOString(),
              usage: response.usage,
              actualModel: response.model, // Store actual model used
              cost: response.metadata?.cost,
            }
          }
        })
      } catch (dbError) {
        logger.error('Failed to store chat messages', { error: dbError, sessionId: response.sessionId })
        // Don't fail the request if database storage fails
      }

      // Log the chat interaction
      logChatMessage('gelu', response.sessionId, 'assistant', response.message.length)

      // Return response with legacy model name for compatibility
      const legacyResponse = {
        message: response.message,
        sessionId: response.sessionId,
        model: 'gelu', // Legacy model name
        usage: response.usage,
      }

      return NextResponse.json(
        createApiResponse(true, 'Chat response generated successfully', legacyResponse),
        { status: 200 }
      )

    } catch (error) {
      logger.error('Gelu chat error', { error })
      
      if (error instanceof Error && error.message.includes('Failed to get response from aCursor')) {
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

