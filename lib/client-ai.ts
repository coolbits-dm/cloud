// Client-side AI utilities - safe for browser usage
// This file contains only static data and safe functions

export function getModelInfo(model: 'jean' | 'gelu') {
  const models = {
    jean: {
      name: 'Jean (GPT-4)',
      description: 'Powered by OpenAI GPT-4',
      capabilities: ['Creative writing', 'Code generation', 'Analysis', 'Conversation'],
    },
    gelu: {
      name: 'Gelu (Grok)',
      description: 'Powered by xAI Grok',
      capabilities: ['Real-time knowledge', 'Creative tasks', 'Problem solving', 'Humor'],
    },
  }
  
  return models[model]
}

export function generateSessionId(): string {
  return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}
