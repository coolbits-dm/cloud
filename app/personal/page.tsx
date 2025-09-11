'use client';

import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { useEffect, useState, useRef } from 'react';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  model?: string;
}

export default function PersonalPage() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/auth/signin');
    }
  }, [status, router]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/personal/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputMessage,
          conversationId,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        
        const assistantMessage: ChatMessage = {
          id: data.id,
          role: 'assistant',
          content: data.content,
          timestamp: new Date(),
          model: data.model,
        };

        setMessages(prev => [...prev, assistantMessage]);
        setConversationId(data.conversationId);
      } else {
        throw new Error('Failed to send message');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      // Add error message
      const errorMessage: ChatMessage = {
        id: Date.now().toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  if (status === 'loading') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">
                🧠 Personal AI Assistant
              </h1>
              <p className="text-gray-300">
                Chat with Andrei's AI - Your personal strategic advisor
              </p>
            </div>
            <div className="text-right">
              <p className="text-white font-medium">{session?.user?.name}</p>
              <p className="text-gray-300 text-sm">{session?.user?.email}</p>
            </div>
          </div>
        </div>

        {/* Chat Container */}
        <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 mb-8">
          <div className="h-96 overflow-y-auto mb-6 space-y-4">
            {messages.length === 0 ? (
              <div className="text-center text-gray-300 py-8">
                <div className="text-4xl mb-4">🧠</div>
                <h3 className="text-xl font-semibold mb-2">Welcome to Andrei's AI</h3>
                <p className="text-sm">
                  I'm your personal AI assistant with expertise in business strategy, 
                  technology, and marketing. How can I help you today?
                </p>
              </div>
            ) : (
              messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                      message.role === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-white/20 text-white'
                    }`}
                  >
                    <div className="text-sm mb-1">
                      {message.role === 'user' ? 'You' : 'Andrei'}
                      {message.model && (
                        <span className="text-xs opacity-70 ml-2">({message.model})</span>
                      )}
                    </div>
                    <div className="whitespace-pre-wrap">{message.content}</div>
                    <div className="text-xs opacity-70 mt-1">
                      {message.timestamp.toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              ))
            )}
            
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white/20 text-white px-4 py-2 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>Andrei is thinking...</span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="flex space-x-4">
            <div className="flex-1">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask Andrei anything about business, technology, or strategy..."
                className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                rows={3}
                disabled={isLoading}
              />
            </div>
            <button
              onClick={sendMessage}
              disabled={isLoading || !inputMessage.trim()}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-6 py-3 rounded-lg font-medium transition-colors"
            >
              Send
            </button>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6">
          <h2 className="text-xl font-bold text-white mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button
              onClick={() => setInputMessage("Help me create a business strategy for my startup")}
              className="bg-gradient-to-r from-green-500 to-green-600 text-white p-4 rounded-lg hover:opacity-90 transition-opacity"
            >
              🚀 Business Strategy
            </button>
            <button
              onClick={() => setInputMessage("What are the latest AI trends I should know about?")}
              className="bg-gradient-to-r from-purple-500 to-purple-600 text-white p-4 rounded-lg hover:opacity-90 transition-opacity"
            >
              🤖 AI Trends
            </button>
            <button
              onClick={() => setInputMessage("Help me optimize my marketing budget")}
              className="bg-gradient-to-r from-orange-500 to-orange-600 text-white p-4 rounded-lg hover:opacity-90 transition-opacity"
            >
              📊 Marketing Optimization
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
