'use client';

import { useState, useEffect, useRef } from 'react';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  model?: string;
}

interface Role {
  id: string;
  name: string;
  provider: 'openai' | 'xai';
  description: string;
  color: string;
  icon: string;
}

interface SecurityStatus {
  certificate: {
    status: string;
    subject: string;
    thumbprint: string;
    validity: string;
    issuer: string;
    expired: boolean;
    daysOverdue: number;
  };
  strSecurity: {
    status: string;
    location: string;
    size: number;
    encrypted: boolean;
    pinProtected: boolean;
    microsoftAccount: string;
  };
  policies: {
    zeroTrust: boolean;
    hmacAuth: boolean;
    ipAllowlist: boolean;
    rateLimiting: boolean;
    auditLogging: boolean;
    efsEncryption: boolean;
    pinProtection: boolean;
    microsoftIntegration: boolean;
  };
}

const ROLES: Role[] = [
  { id: 'ogpt01', name: 'CEO', provider: 'openai', description: 'Chief Executive Officer', color: 'bg-blue-600', icon: '👔' },
  { id: 'ogpt02', name: 'CTO', provider: 'openai', description: 'Chief Technology Officer', color: 'bg-purple-600', icon: '💻' },
  { id: 'ogpt03', name: 'CMO', provider: 'openai', description: 'Chief Marketing Officer', color: 'bg-green-600', icon: '📈' },
  { id: 'ogpt04', name: 'DEV', provider: 'openai', description: 'Lead Developer', color: 'bg-orange-600', icon: '🔧' },
  { id: 'ogpt05', name: 'COO', provider: 'openai', description: 'Chief Operations Officer', color: 'bg-red-600', icon: '⚙️' },
  { id: 'ogpt06', name: 'CFO', provider: 'openai', description: 'Chief Financial Officer', color: 'bg-emerald-600', icon: '💰' },
  { id: 'ogpt07', name: 'CHRO', provider: 'openai', description: 'Chief Human Resources Officer', color: 'bg-pink-600', icon: '👥' },
  { id: 'ogpt08', name: 'CPO', provider: 'openai', description: 'Chief Product Officer', color: 'bg-indigo-600', icon: '📦' },
  { id: 'ogpt09', name: 'CISO', provider: 'openai', description: 'Chief Information Security Officer', color: 'bg-gray-600', icon: '🔒' },
  { id: 'ogpt10', name: 'CCO', provider: 'openai', description: 'Chief Customer Officer', color: 'bg-cyan-600', icon: '🎯' },
  { id: 'ogpt11', name: 'Board', provider: 'openai', description: 'Board Member', color: 'bg-yellow-600', icon: '🏛️' },
  { id: 'ogpt12', name: 'CSO', provider: 'openai', description: 'Chief Strategy Officer', color: 'bg-teal-600', icon: '🎯' },
  { id: 'ogrok01', name: 'CEO', provider: 'xai', description: 'Chief Executive Officer (xAI)', color: 'bg-blue-500', icon: '🤖' },
  { id: 'ogrok02', name: 'CTO', provider: 'xai', description: 'Chief Technology Officer (xAI)', color: 'bg-purple-500', icon: '🤖' },
  { id: 'ogrok03', name: 'CMO', provider: 'xai', description: 'Chief Marketing Officer (xAI)', color: 'bg-green-500', icon: '🤖' },
  { id: 'ogrok04', name: 'DEV', provider: 'xai', description: 'Lead Developer (xAI)', color: 'bg-orange-500', icon: '🤖' },
  { id: 'ogrok05', name: 'COO', provider: 'xai', description: 'Chief Operations Officer (xAI)', color: 'bg-red-500', icon: '🤖' },
  { id: 'ogrok06', name: 'CFO', provider: 'xai', description: 'Chief Financial Officer (xAI)', color: 'bg-emerald-500', icon: '🤖' },
  { id: 'ogrok07', name: 'CHRO', provider: 'xai', description: 'Chief Human Resources Officer (xAI)', color: 'bg-pink-500', icon: '🤖' },
];

export default function AndreiChatPanel() {
  const [selectedRole, setSelectedRole] = useState<Role | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState<Record<string, ChatMessage[]>>({});
  const [activeTab, setActiveTab] = useState<'chat' | 'security'>('chat');
  const [securityStatus, setSecurityStatus] = useState<SecurityStatus | null>(null);
  const [securityLoading, setSecurityLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load chat history for selected role
  useEffect(() => {
    if (selectedRole) {
      const history = chatHistory[selectedRole.id] || [];
      setMessages(history);
    }
  }, [selectedRole, chatHistory]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Load security status
  const loadSecurityStatus = async () => {
    setSecurityLoading(true);
    try {
      const response = await fetch('/api/security/status');
      if (response.ok) {
        const data = await response.json();
        setSecurityStatus(data);
      }
    } catch (error) {
      console.error('Failed to load security status:', error);
    } finally {
      setSecurityLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'security') {
      loadSecurityStatus();
    }
  }, [activeTab]);

  const sendMessage = async () => {
    if (!inputMessage.trim() || !selectedRole || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date(),
    };

    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          role: selectedRole.id,
          message: inputMessage,
          history: messages,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        const assistantMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: data.response,
          timestamp: new Date(),
          model: data.model,
        };

        const finalMessages = [...newMessages, assistantMessage];
        setMessages(finalMessages);
        setChatHistory(prev => ({
          ...prev,
          [selectedRole.id]: finalMessages,
        }));
      }
    } catch (error) {
      console.error('Failed to send message:', error);
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

  const SecurityPanel = () => (
    <div className="h-full flex flex-col">
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">🔐 @SafeNet Security Dashboard</h2>
            <p className="text-gray-600">Real-time security monitoring and certificate management</p>
          </div>

          {securityLoading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
          ) : securityStatus ? (
            <div className="space-y-6">
              {/* Certificate Status */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  📜 Certificate Status
                  {securityStatus.certificate.expired ? (
                    <span className="ml-2 px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full">EXPIRED</span>
                  ) : (
                    <span className="ml-2 px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">VALID</span>
                  )}
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Subject</label>
                    <p className="mt-1 text-sm text-gray-900">{securityStatus.certificate.subject}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Thumbprint</label>
                    <p className="mt-1 text-sm text-gray-900 font-mono">{securityStatus.certificate.thumbprint}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Validity</label>
                    <p className="mt-1 text-sm text-gray-900">{securityStatus.certificate.validity}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Issuer</label>
                    <p className="mt-1 text-sm text-gray-900">{securityStatus.certificate.issuer}</p>
                  </div>
                </div>
                {securityStatus.certificate.expired && (
                  <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
                    <div className="flex">
                      <div className="flex-shrink-0">
                        <span className="text-red-400">⚠️</span>
                      </div>
                      <div className="ml-3">
                        <h3 className="text-sm font-medium text-red-800">Certificate Expired</h3>
                        <div className="mt-2 text-sm text-red-700">
                          <p>Certificate has been expired for {securityStatus.certificate.daysOverdue} days. Immediate renewal required.</p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* str.py Security Status */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  🔒 str.py Security Status
                  <span className="ml-2 px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">SECURE</span>
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Location</label>
                    <p className="mt-1 text-sm text-gray-900 font-mono">{securityStatus.strSecurity.location}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Size</label>
                    <p className="mt-1 text-sm text-gray-900">{securityStatus.strSecurity.size.toLocaleString()} bytes</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Encryption</label>
                    <p className="mt-1 text-sm text-gray-900 flex items-center">
                      {securityStatus.strSecurity.encrypted ? (
                        <>
                          <span className="text-green-500 mr-1">✅</span>
                          EFS (AES-256)
                        </>
                      ) : (
                        <>
                          <span className="text-red-500 mr-1">❌</span>
                          Not Encrypted
                        </>
                      )}
                    </p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">PIN Protection</label>
                    <p className="mt-1 text-sm text-gray-900 flex items-center">
                      {securityStatus.strSecurity.pinProtected ? (
                        <>
                          <span className="text-green-500 mr-1">✅</span>
                          Enabled
                        </>
                      ) : (
                        <>
                          <span className="text-red-500 mr-1">❌</span>
                          Disabled
                        </>
                      )}
                    </p>
                  </div>
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700">Microsoft Account</label>
                    <p className="mt-1 text-sm text-gray-900">{securityStatus.strSecurity.microsoftAccount}</p>
                  </div>
                </div>
              </div>

              {/* Security Policies */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">🛡️ Security Policies</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {Object.entries(securityStatus.policies).map(([key, value]) => (
                    <div key={key} className="flex items-center">
                      <span className={`mr-2 ${value ? 'text-green-500' : 'text-red-500'}`}>
                        {value ? '✅' : '❌'}
                      </span>
                      <span className="text-sm text-gray-900 capitalize">
                        {key.replace(/([A-Z])/g, ' $1').trim()}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Actions */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">🎯 Security Actions</h3>
                <div className="flex flex-wrap gap-3">
                  <button
                    onClick={loadSecurityStatus}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                  >
                    🔄 Refresh Status
                  </button>
                  <button
                    onClick={() => window.open('/api/security/report', '_blank')}
                    className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
                  >
                    📋 Generate Report
                  </button>
                  <button
                    onClick={() => window.open('/api/security/certificate/renew', '_blank')}
                    className="px-4 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700 transition-colors"
                  >
                    🔄 Renew Certificate
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-500">Failed to load security status</p>
              <button
                onClick={loadSecurityStatus}
                className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                Retry
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <div className="h-screen bg-gray-100 flex flex-col">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Andrei Panel</h1>
              <p className="text-gray-600">CoolBits.ai - Multi-Agent Chat System</p>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => setActiveTab('chat')}
                className={`px-4 py-2 rounded-md transition-colors ${
                  activeTab === 'chat'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                💬 Chat
              </button>
              <button
                onClick={() => setActiveTab('security')}
                className={`px-4 py-2 rounded-md transition-colors ${
                  activeTab === 'security'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                🔐 @SafeNet
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex">
        {activeTab === 'chat' ? (
          <>
            {/* Role Selection */}
            <div className="w-80 bg-white shadow-sm border-r">
              <div className="p-4 border-b">
                <h2 className="text-lg font-semibold text-gray-900">Select Role</h2>
              </div>
              <div className="overflow-y-auto h-full">
                <div className="p-4 space-y-2">
                  {ROLES.map((role) => (
                    <button
                      key={role.id}
                      onClick={() => setSelectedRole(role)}
                      className={`w-full text-left p-3 rounded-lg transition-colors ${
                        selectedRole?.id === role.id
                          ? `${role.color} text-white`
                          : 'bg-gray-50 hover:bg-gray-100 text-gray-700'
                      }`}
                    >
                      <div className="flex items-center">
                        <span className="text-xl mr-3">{role.icon}</span>
                        <div>
                          <div className="font-medium">{role.name}</div>
                          <div className="text-sm opacity-75">{role.description}</div>
                          <div className="text-xs opacity-60">{role.provider.toUpperCase()}</div>
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Chat Area */}
            <div className="flex-1 flex flex-col">
              {selectedRole ? (
                <>
                  {/* Chat Header */}
                  <div className="bg-white border-b p-4">
                    <div className="flex items-center">
                      <span className="text-2xl mr-3">{selectedRole.icon}</span>
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">{selectedRole.name}</h3>
                        <p className="text-sm text-gray-600">{selectedRole.description}</p>
                      </div>
                    </div>
                  </div>

                  {/* Messages */}
                  <div className="flex-1 overflow-y-auto p-4 space-y-4">
                    {messages.map((message) => (
                      <div
                        key={message.id}
                        className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                      >
                        <div
                          className={`max-w-3xl px-4 py-2 rounded-lg ${
                            message.role === 'user'
                              ? 'bg-blue-600 text-white'
                              : 'bg-white border shadow-sm'
                          }`}
                        >
                          <div className="whitespace-pre-wrap">{message.content}</div>
                          <div className={`text-xs mt-1 ${
                            message.role === 'user' ? 'text-blue-100' : 'text-gray-500'
                          }`}>
                            {message.timestamp.toLocaleTimeString()}
                            {message.model && ` • ${message.model}`}
                          </div>
                        </div>
                      </div>
                    ))}
                    {isLoading && (
                      <div className="flex justify-start">
                        <div className="bg-white border shadow-sm px-4 py-2 rounded-lg">
                          <div className="flex items-center space-x-2">
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                            <span className="text-gray-600">Thinking...</span>
                          </div>
                        </div>
                      </div>
                    )}
                    <div ref={messagesEndRef} />
                  </div>

                  {/* Input */}
                  <div className="bg-white border-t p-4">
                    <div className="flex space-x-2">
                      <textarea
                        value={inputMessage}
                        onChange={(e) => setInputMessage(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder={`Message ${selectedRole.name}...`}
                        className="flex-1 p-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
                        rows={2}
                        disabled={isLoading}
                      />
                      <button
                        onClick={sendMessage}
                        disabled={!inputMessage.trim() || isLoading}
                        className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                      >
                        Send
                      </button>
                    </div>
                  </div>
                </>
              ) : (
                <div className="flex-1 flex items-center justify-center">
                  <div className="text-center">
                    <div className="text-6xl mb-4">👔</div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">Select a Role</h3>
                    <p className="text-gray-600">Choose a role to start chatting</p>
                  </div>
                </div>
              )}
            </div>
          </>
        ) : (
          <SecurityPanel />
        )}
      </div>
    </div>
  );
}