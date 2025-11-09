'use client'

import { useState, useRef, useEffect } from 'react'
import { PaperAirplaneIcon } from '@heroicons/react/24/outline'

interface MessageInputProps {
  onSendMessage: (message: string) => void
  isLoading?: boolean
  placeholder?: string
  className?: string
}

export default function MessageInput({
  onSendMessage,
  isLoading = false,
  placeholder = 'Type your message...',
  className = '',
}: MessageInputProps) {
  const [message, setMessage] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }, [message])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!message.trim() || isLoading) return
    
    onSendMessage(message)
    setMessage('')
    
    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e as any)
    }
  }

  const isDisabled = !message.trim() || isLoading

  return (
    <form onSubmit={handleSubmit} className={`flex items-end space-x-3 ${className}`}>
      <div className="flex-1 relative">
        <textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          rows={1}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none transition-colors"
          style={{ minHeight: '44px', maxHeight: '120px' }}
          disabled={isLoading}
        />
        
        {/* Character count */}
        {message.length > 0 && (
          <div className="absolute bottom-2 right-2 text-xs text-gray-400">
            {message.length}
          </div>
        )}
      </div>
      
      <button
        type="submit"
        disabled={isDisabled}
        className={`p-3 rounded-lg transition-all duration-200 ${
          isDisabled
            ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
            : 'bg-primary-600 hover:bg-primary-700 active:bg-primary-800 text-white shadow-lg hover:shadow-xl transform hover:-translate-y-0.5'
        }`}
        title={isDisabled ? 'Type a message to send' : 'Send message'}
      >
        {isLoading ? (
          <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
        ) : (
          <PaperAirplaneIcon className="w-5 h-5" />
        )}
      </button>
    </form>
  )
}
