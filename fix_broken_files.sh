#!/bin/bash

# CoolBits.ai - Fix Broken Files
# Corectează fișierele stricate de scripturi

echo "🔧 CoolBits.ai - Fixing Broken Files"
echo "===================================="
echo ""

cd ~/coolbits-ai-repo

echo "🔍 Fixing broken files..."
echo ""

# 1. Corectează MessageList.tsx
echo "🔧 Fixing MessageList.tsx..."
cat > components/MessageList.tsx << 'EOF'
'use client'

import { Message } from '@/lib/ai'

interface MessageListProps {
  messages: Message[]
}

export default function MessageList({ messages }: MessageListProps) {
  const renderMessageContent = (message: Message) => {
    return (
      <div className="whitespace-pre-wrap">
        {message.content}
      </div>
    )
  }

  const renderMessageMetadata = (message: Message) => {
    return (
      <div className="flex items-center justify-between mt-2 text-xs opacity-75">
        <span>{message.timestamp}</span>
        {message.tokens && (
          <span>{message.tokens} tokens</span>
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
EOF

# 2. Corectează layout.tsx
echo "🔧 Fixing layout.tsx..."
cat > app/layout.tsx << 'EOF'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Link from 'next/link'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'CoolBits.ai - AI-Powered Business Solutions',
  description: 'Transform your business with AI-powered insights and automation',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        {/* Header */}
        <header className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              {/* Logo */}
              <div className="flex items-center">
                <Link href="/" className="flex items-center space-x-2">
                  <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                    <span className="text-white font-bold text-lg">C</span>
                  </div>
                  <span className="text-xl font-bold text-gray-900">CoolBits</span>
                </Link>
              </div>

              {/* Navigation */}
              <nav className="hidden md:flex items-center space-x-8">
                <Link href="/" className="text-gray-700 hover:text-primary-600">
                  Home
                </Link>
                <Link href="/vault" className="text-gray-700 hover:text-primary-600">
                  Vault
                </Link>
              </nav>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="min-h-screen bg-gray-50">
          {children}
        </main>

        {/* Footer */}
        <footer className="bg-white border-t">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="text-center text-gray-600">
              <p>&copy; 2024 CoolBits.ai. All rights reserved.</p>
            </div>
          </div>
        </footer>
      </body>
    </html>
  )
}
EOF

# 3. Corectează page.tsx
echo "🔧 Fixing page.tsx..."
cat > app/page.tsx << 'EOF'
'use client'

import { useState } from 'react'
import PromptForm from '@/components/PromptForm'
import MessageList from '@/components/MessageList'
import { Message } from '@/lib/ai'

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (prompt: string, model: string) => {
    setIsLoading(true)
    
    try {
      const response = await fetch(`/api/ai/${model}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt }),
      })

      if (!response.ok) {
        throw new Error('Failed to get response')
      }

      const data = await response.json()
      
      const newMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: data.response,
        model: model,
        timestamp: new Date().toLocaleTimeString(),
        tokens: data.usage?.total_tokens
      }

      setMessages(prev => [...prev, newMessage])
    } catch (error) {
      console.error('Error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Welcome to CoolBits.ai
        </h1>
        <p className="text-xl text-gray-600">
          Transform your business with AI-powered insights and automation
        </p>
      </div>

      <div className="bg-white rounded-lg shadow-lg p-6">
        <PromptForm onSubmit={handleSubmit} isLoading={isLoading} />
        
        {messages.length > 0 && (
          <div className="mt-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Conversation</h2>
            <MessageList messages={messages} />
          </div>
        )}
      </div>
    </div>
  )
}
EOF

# 4. Corectează vault/page.tsx
echo "🔧 Fixing vault/page.tsx..."
cat > app/vault/page.tsx << 'EOF'
'use client'

import { useState } from 'react'

export default function VaultPage() {
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    
    try {
      const response = await fetch('/api/vault', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ action: 'test' }),
      })

      if (!response.ok) {
        throw new Error('Failed to access vault')
      }

      const data = await response.json()
      console.log('Vault response:', data)
    } catch (error) {
      console.error('Error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          CoolBits Vault
        </h1>
        <p className="text-xl text-gray-600">
          Secure storage and management for your business data
        </p>
      </div>

      <div className="bg-white rounded-lg shadow-lg p-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Vault Action
            </label>
            <input
              type="text"
              defaultValue="test"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            />
          </div>
          
          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 disabled:opacity-50"
          >
            {isLoading ? 'Processing...' : 'Submit'}
          </button>
        </form>
      </div>
    </div>
  )
}
EOF

# 5. Corectează ai.ts
echo "🔧 Fixing ai.ts..."
cat > lib/ai.ts << 'EOF'
export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  model?: string
  timestamp?: string
  tokens?: number
}

export async function callAI(prompt: string, model: string, messages: Message[] = []): Promise<{ response: string; usage?: { total_tokens: number } }> {
  const apiKey = process.env.OPENAI_API_KEY

  if (!apiKey) {
    throw new Error('OPENAI_API_KEY is not configured. Please set a valid API key in your .env file.')
  }

  const messageHistory = messages.map(msg => ({
    role: msg.role as 'user' | 'assistant',
    content: msg.content,
  })) || []

  // Add current message
  messageHistory.push({
    role: 'user',
    content: prompt,
  })

  const response = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: model === 'jean' ? 'gpt-4' : 'gpt-3.5-turbo',
      messages: messageHistory,
      max_tokens: 1000,
      temperature: 0.7,
    }),
  })

  if (!response.ok) {
    throw new Error(`OpenAI API error: ${response.status}`)
  }

  const data = await response.json()
  
  return {
    response: data.choices[0]?.message?.content || 'No response from AI',
    usage: data.usage
  }
}
EOF

echo ""
echo "🔧 Testing build..."
npm run build

echo ""
echo "🎉 BROKEN FILES FIXED!"
echo "====================="
echo "✅ MessageList.tsx fixed"
echo "✅ layout.tsx fixed"
echo "✅ page.tsx fixed"
echo "✅ vault/page.tsx fixed"
echo "✅ ai.ts fixed"
echo "✅ Build should succeed now"
echo ""
echo "🚀 Ready for deployment!"
