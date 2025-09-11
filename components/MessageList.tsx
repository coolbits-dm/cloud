'use client'

import { ChatMessage } from '@/schemas/chat'
import { formatDistanceToNow } from 'date-fns'

interface MessageListProps {
  messages: ChatMessage[]
  currentModel: 'jean' | 'gelu'
}

export default function MessageList({ messages, currentModel }: MessageListProps) {
  const formatMessageTime = (date: Date | undefined) => {
    if (!date) return 'Just now'
    return formatDistanceToNow(date, { addSuffix: true })
  }

  const renderMessageContent = (message: ChatMessage) => {
    // Handle system messages (like model switches)
    if (message.metadata?.systemMessage) {
      return (
        <div className="text-center">
          <span className="inline-block bg-gray-100 text-gray-600 px-3 py-1 rounded-full text-sm">
            {message.content}
          </span>
        </div>
      )
    }

    // Handle error messages
    if (message.metadata?.error) {
      return (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3">
          <div className="flex items-start">
            <svg className="w-5 h-5 text-red-400 mt-0.5 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="text-red-800">{message.content}</p>
          </div>
        </div>
      )
    }

    // Regular message content
    return (
      <div className="prose prose-sm max-w-none">
        {message.content.split('\n').map((line, index) => (
          <p key={index} className={index > 0 ? 'mt-2' : ''}>
            {line}
          </p>
        ))}
      </div>
    )
  }

  const renderMessageMetadata = (message: ChatMessage) => {
    if (message.metadata?.systemMessage || message.metadata?.error) {
      return null
    }

    return (
      <div className="flex items-center justify-between text-xs text-gray-500 mt-2">
        <span>{formatMessageTime(message.createdAt)}</span>
        
        {message.metadata?.usage && (
          <div className="flex items-center space-x-3">
            <span>Tokens: {message.metadata.usage.totalTokens}</span>
            {message.metadata.responseTime && (
              <span>Response: {message.metadata.responseTime}ms</span>
            )}
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {messages.map((message) => (
        <div
          key={message.id}
          className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
        >
          <div
            className={`max-w-[80%] ${
              message.role === 'user'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-900'
            } rounded-lg p-4 shadow-sm`}
          >
            {/* Message Header */}
            <div className="flex items-center space-x-2 mb-2">
              <div
                className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-semibold ${
                  message.role === 'user'
                    ? 'bg-primary-700 text-white'
                    : 'bg-gray-200 text-gray-700'
                }`}
              >
                {message.role === 'user' ? 'U' : (message.model === 'jean' ? 'J' : 'G')}
              </div>
              <span className="text-xs font-medium opacity-75">
                {message.role === 'user' ? 'You' : message.model === 'jean' ? 'Jean' : 'Gelu'}
              </span>
            </div>

            {/* Message Content */}
            {renderMessageContent(message)}

            {/* Message Metadata */}
            {renderMessageMetadata(message)}
          </div>
        </div>
      ))}
    </div>
  )
}
