import { NextRequest, NextResponse } from 'next/server'
import { chatRequestSchema } from '@/schemas/chat'
import { aCursor } from '@/lib/ai/acursor'
import { withRateLimit } from '@/lib/rateLimit'
import { createApiResponse } from '@/lib/validation'
import { prisma } from '@/lib/db'
import logger, { logChatMessage } from '@/lib/logger'

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

      // Get chat response from aCursor
      const response = await aCursor.chatWithaCursor(chatRequest)

      // Store messages in database
      try {
        // Store user message
        await prisma.chatMessage.create({
          data: {
            sessionId: response.sessionId,
            role: 'user',
            content: chatRequest.message,
            model: 'acursor',
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
            model: 'acursor',
            metadata: {
              timestamp: new Date().toISOString(),
              usage: response.usage,
              modelUsed: response.model,
              cost: response.metadata?.cost,
            }
          }
        })
      } catch (dbError) {
        logger.error('Failed to store chat messages', { error: dbError, sessionId: response.sessionId })
        // Don't fail the request if database storage fails
      }

      // Log the chat interaction
      logChatMessage('acursor', response.sessionId, 'assistant', response.message.length)

      return NextResponse.json(
        createApiResponse(true, 'aCursor response generated successfully', response),
        { status: 200 }
      )

    } catch (error) {
      logger.error('aCursor chat error', { error })
      
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

export async function GET() {
  return NextResponse.json({
    success: true,
    message: 'aCursor - Andrei\'s AI Assistant',
    data: {
      name: 'aCursor',
      description: 'Andrei\'s personal AI assistant for CoolBits.ai',
      capabilities: [
        'Business strategy and growth',
        'Digital marketing and AI tools',
        'Technology and development',
        'Personal productivity and optimization',
        'Context-aware conversations',
        'Model switching (GPT-4 with GPT-3.5 fallback)'
      ],
      endpoints: {
        chat: 'POST /api/ai/acursor',
        health: 'GET /api/v1/health'
      },
      version: '1.0.0'
    }
  })
}
