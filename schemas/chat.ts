import { z } from 'zod'

export const chatMessageSchema = z.object({
  sessionId: z.string().min(1, 'Session ID is required'),
  role: z.enum(['user', 'assistant'], {
    errorMap: () => ({ message: 'Role must be either "user" or "assistant"' })
  }),
  content: z.string().min(1, 'Message content cannot be empty'),
  model: z.enum(['jean', 'gelu'], {
    errorMap: () => ({ message: 'Model must be either "jean" or "gelu"' })
  }),
  metadata: z.record(z.any()).optional(),
})

export const chatRequestSchema = z.object({
  message: z.string().min(1, 'Message cannot be empty'),
  model: z.enum(['jean', 'gelu']),
  sessionId: z.string().optional(),
  context: z.array(chatMessageSchema).optional(),
})

export const chatResponseSchema = z.object({
  message: z.string(),
  sessionId: z.string(),
  model: z.enum(['jean', 'gelu']),
  usage: z.object({
    promptTokens: z.number(),
    completionTokens: z.number(),
    totalTokens: z.number(),
  }).optional(),
})

export type ChatMessage = z.infer<typeof chatMessageSchema>
export type ChatRequest = z.infer<typeof chatRequestSchema>
export type ChatResponse = z.infer<typeof chatResponseSchema>
