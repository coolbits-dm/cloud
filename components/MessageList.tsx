'use client'

import { ChatMessage } from '@/schemas/chat'
const assistantName = process.env.NEXT_PUBLIC_ASSISTANT_NAME ?? 'Andy'

export default function MessageList({
  messages,
}: {
  messages: ChatMessage[]
  currentModel?: any
}) {
  return (
    <div className="space-y-3">
      {messages.map((m) => {
        const isUser = m.role === 'user'
        return (
          <div key={m.id} className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
            <div
              className={`max-w-[80%] rounded-xl px-4 py-3 text-sm leading-relaxed shadow-sm
              ${isUser ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-900'}`}
            >
              <div className="mb-1 text-xs opacity-80">
                {isUser ? 'You' : assistantName}
              </div>
              <div className="whitespace-pre-wrap">{m.content}</div>
              {!isUser && m.metadata?.usage && (
                <div className="mt-1 text-[10px] opacity-60">
                  Tokens: {m.metadata.usage.total_tokens ?? '-'}
                </div>
              )}
              {m.metadata?.error && !isUser && (
                <div className="mt-1 text-[10px] text-red-600">Error</div>
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}
