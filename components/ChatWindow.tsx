'use client'

import { useState, useRef, useEffect } from 'react'
import { ChatMessage } from '@/schemas/chat'
import MessageList from './MessageList'
import MessageInput from './MessageInput'
import { getModelInfo, generateSessionId } from '@/lib/client-ai'

interface ChatWindowProps {
  initialModel?: 'jean' | 'gelu'
  className?: string
}

export default function ChatWindow({ initialModel = 'jean', className = '' }: ChatWindowProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [currentModel, setCurrentModel] = useState<'jean' | 'gelu'>(initialModel)
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState<string>('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Generate session ID on component mount
  useEffect(() => {
    if (!sessionId) {
      setSessionId(generateSessionId())
    }
  }, [sessionId])

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSendMessage = async (content: string) => {
    if (!content.trim() || isLoading) return

    const userMessage: ChatMessage = {
      id: `msg_${Date.now()}`,
      sessionId,
      role: 'user',
      content: content.trim(),
      model: currentModel,
      createdAt: new Date(),
    }

    // Add user message immediately
    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)

    try {
      // Send message to API
      const response = await fetch(`/api/ai/${currentModel}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: content.trim(),
          model: currentModel,
          sessionId,
          context: messages.slice(-10), // Send last 10 messages for context
        }),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()

      if (data.success) {
        const assistantMessage: ChatMessage = {
          id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          sessionId,
          role: 'assistant',
          content: data.data.message,
          model: currentModel,
          createdAt: new Date(),
          metadata: {
            usage: data.data.usage,
            responseTime: Date.now() - (userMessage.createdAt?.getTime() || Date.now()),
          },
        }

        setMessages(prev => [...prev, assistantMessage])
      } else {
        throw new Error(data.message || 'Failed to get response')
      }
    } catch (error) {
      console.error('Chat error:', error)
      
      const errorMessage: ChatMessage = {
        id: `error_${Date.now()}`,
        sessionId,
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        model: currentModel,
        createdAt: new Date(),
        metadata: { error: true },
      }

      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleModelSwitch = (model: 'jean' | 'gelu') => {
    if (model === currentModel) return
    
    setCurrentModel(model)
    
    // Add system message about model switch
    const switchMessage: ChatMessage = {
      id: `switch_${Date.now()}`,
      sessionId,
      role: 'assistant',
      content: `Switched to ${getModelInfo(model).name}. ${getModelInfo(model).description}`,
      model,
      createdAt: new Date(),
      metadata: { systemMessage: true },
    }
    
    setMessages(prev => [...prev, switchMessage])
  }

  const clearChat = () => {
    setMessages([])
    setSessionId(`session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`)
  }

  const modelInfo = getModelInfo(currentModel)

  return (
    <div className={`flex flex-col h-full bg-white rounded-lg shadow-lg ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-gray-50 rounded-t-lg">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
            <span className="text-primary-600 font-semibold text-sm">
              {currentModel === 'jean' ? 'J' : 'G'}
            </span>
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">{modelInfo.name}</h3>
            <p className="text-sm text-gray-500">{modelInfo.description}</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          {/* Model Switcher */}
          <div className="flex bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => handleModelSwitch('jean')}
              className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${
                currentModel === 'jean'
                  ? 'bg-white text-primary-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Jean
            </button>
            <button
              onClick={() => handleModelSwitch('gelu')}
              className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${
                currentModel === 'gelu'
                  ? 'bg-white text-primary-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Gelu
            </button>
          </div>
          
          {/* Clear Chat */}
          <button
            onClick={clearChat}
            className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
            title="Clear chat"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 mt-8">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Start a conversation with {modelInfo.name}
            </h3>
            <p className="text-gray-500">
              {modelInfo.capabilities.join(', ')}
            </p>
          </div>
        ) : (
          <MessageList messages={messages} currentModel={currentModel} />
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-200 p-4">
        <MessageInput
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
          placeholder={`Message ${modelInfo.name}...`}
        />
      </div>
    </div>
  )
}
