import OpenAI from 'openai'
import { ChatRequest, ChatResponse } from '@/schemas/chat'
import { aCursor } from './ai/acursor'

// OpenAI (Jean) configuration - SERVER SIDE ONLY
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY || 'demo-key-for-development',
  dangerouslyAllowBrowser: false, // Never allow browser usage
})

// xAI (Gelu) configuration - placeholder for when xAI API becomes available
// const xai = new XAI({
//   apiKey: process.env.XAI_API_KEY,
// })

export async function chatWithJean(request: ChatRequest): Promise<ChatResponse> {
  try {
    // Check if we have a valid API key
    if (!process.env.OPENAI_API_KEY || process.env.OPENAI_API_KEY === 'demo-key-for-development') {
      throw new Error('OPENAI_API_KEY is not configured. Please set a valid API key in your .env file.')
    }

    const messages = request.context?.map(msg => ({
      role: msg.role as 'user' | 'assistant',
      content: msg.content,
    })) || []

    // Add current message
    messages.push({
      role: 'user',
      content: request.message,
    })

    const completion = await openai.chat.completions.create({
      model: 'gpt-4',
      messages,
      max_tokens: 1000,
      temperature: 0.7,
    })

    const response = completion.choices[0]?.message?.content || 'Sorry, I could not generate a response.'

    return {
      message: response,
      sessionId: request.sessionId || generateSessionId(),
      model: 'jean',
      usage: {
        promptTokens: completion.usage?.prompt_tokens || 0,
        completionTokens: completion.usage?.completion_tokens || 0,
        totalTokens: completion.usage?.total_tokens || 0,
      },
    }
  } catch (error) {
    console.error('Error in Jean chat:', error)
    throw new Error('Failed to get response from Jean')
  }
}

export async function chatWithGelu(request: ChatRequest): Promise<ChatResponse> {
  // Placeholder for xAI integration
  // This will be implemented when xAI API becomes available
  throw new Error('Gelu (xAI) integration not yet available')
  
  // Future implementation:
  // const response = await xai.chat.completions.create({
  //   model: 'grok-beta',
  //   messages: [...],
  // })
}

// Export aCursor functionality
export { aCursor } from './ai/acursor'

function generateSessionId(): string {
  return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}
