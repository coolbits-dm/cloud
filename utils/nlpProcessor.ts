import OpenAI from 'openai'

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
})

export interface TaglineRequest {
  industry: string
  companyName: string
  description: string
  tone: 'professional' | 'casual' | 'creative' | 'humorous'
  length: 'short' | 'medium' | 'long'
}

export interface TaglineResponse {
  taglines: string[]
  suggestions: string[]
  analysis: {
    strengths: string[]
    improvements: string[]
  }
}

export async function generateTaglines(request: TaglineRequest): Promise<TaglineResponse> {
  try {
    const prompt = createTaglinePrompt(request)
    
    const completion = await openai.chat.completions.create({
      model: 'gpt-4',
      messages: [
        {
          role: 'system',
          content: 'You are a professional marketing copywriter specializing in creating compelling taglines and brand messaging. Provide creative, memorable, and industry-appropriate taglines.'
        },
        {
          role: 'user',
          content: prompt
        }
      ],
      max_tokens: 1000,
      temperature: 0.8,
    })

    const response = completion.choices[0]?.message?.content || ''
    return parseTaglineResponse(response)
  } catch (error) {
    console.error('Error generating taglines:', error)
    throw new Error('Failed to generate taglines')
  }
}

export interface PromptRequest {
  context: string
  goal: string
  audience: string
  style: 'conversational' | 'formal' | 'creative' | 'technical'
  length: 'brief' | 'detailed' | 'comprehensive'
}

export interface PromptResponse {
  prompts: string[]
  variations: string[]
  tips: string[]
}

export async function generatePrompts(request: PromptRequest): Promise<PromptResponse> {
  try {
    const prompt = createPromptGenerationPrompt(request)
    
    const completion = await openai.chat.completions.create({
      model: 'gpt-4',
      messages: [
        {
          role: 'system',
          content: 'You are an expert at creating effective prompts for AI interactions. Generate clear, specific, and actionable prompts that will produce the desired results.'
        },
        {
          role: 'user',
          content: prompt
        }
      ],
      max_tokens: 1000,
      temperature: 0.7,
    })

    const response = completion.choices[0]?.message?.content || ''
    return parsePromptResponse(response)
  } catch (error) {
    console.error('Error generating prompts:', error)
    throw new Error('Failed to generate prompts')
  }
}

function createTaglinePrompt(request: TaglineRequest): string {
  const lengthGuide = {
    short: '5-8 words',
    medium: '8-12 words', 
    long: '12-15 words'
  }

  return `
Create taglines for a company with the following specifications:

Company: ${request.companyName}
Industry: ${request.industry}
Description: ${request.description}
Tone: ${request.tone}
Length: ${lengthGuide[request.length]}

Please provide:
1. 5 creative taglines that match the specifications
2. 3 alternative approaches to consider
3. Analysis of what makes each tagline effective
4. Suggestions for improvement

Format the response as:
TAGLINES:
- [tagline 1]
- [tagline 2]
...

SUGGESTIONS:
- [suggestion 1]
- [suggestion 2]
...

ANALYSIS:
Strengths:
- [strength 1]
- [strength 2]

Improvements:
- [improvement 1]
- [improvement 2]
`
}

function createPromptGenerationPrompt(request: PromptRequest): string {
  const lengthGuide = {
    brief: '1-2 sentences',
    detailed: '3-5 sentences',
    comprehensive: '5+ sentences with examples'
  }

  return `
Create effective prompts based on the following requirements:

Context: ${request.context}
Goal: ${request.goal}
Target Audience: ${request.audience}
Style: ${request.style}
Length: ${lengthGuide[request.length]}

Please provide:
1. 3 main prompts optimized for the goal
2. 2 variations with different approaches
3. Tips for using and customizing these prompts

Format the response as:
PROMPTS:
- [prompt 1]
- [prompt 2]
- [prompt 3]

VARIATIONS:
- [variation 1]
- [variation 2]

TIPS:
- [tip 1]
- [tip 2]
- [tip 3]
`
}

function parseTaglineResponse(response: string): TaglineResponse {
  // Simple parsing - in production, you might want more sophisticated parsing
  const lines = response.split('\n').filter(line => line.trim())
  
  const taglines: string[] = []
  const suggestions: string[] = []
  const strengths: string[] = []
  const improvements: string[] = []
  
  let currentSection = ''
  
  for (const line of lines) {
    if (line.includes('TAGLINES:')) {
      currentSection = 'taglines'
    } else if (line.includes('SUGGESTIONS:')) {
      currentSection = 'suggestions'
    } else if (line.includes('ANALYSIS:')) {
      currentSection = 'analysis'
    } else if (line.includes('Strengths:')) {
      currentSection = 'strengths'
    } else if (line.includes('Improvements:')) {
      currentSection = 'improvements'
    } else if (line.startsWith('-') && line.trim().length > 1) {
      const content = line.substring(1).trim()
      
      switch (currentSection) {
        case 'taglines':
          taglines.push(content)
          break
        case 'suggestions':
          suggestions.push(content)
          break
        case 'strengths':
          strengths.push(content)
          break
        case 'improvements':
          improvements.push(content)
          break
      }
    }
  }
  
  return {
    taglines: taglines.slice(0, 5),
    suggestions: suggestions.slice(0, 3),
    analysis: {
      strengths: strengths.slice(0, 3),
      improvements: improvements.slice(0, 3),
    }
  }
}

function parsePromptResponse(response: string): PromptResponse {
  const lines = response.split('\n').filter(line => line.trim())
  
  const prompts: string[] = []
  const variations: string[] = []
  const tips: string[] = []
  
  let currentSection = ''
  
  for (const line of lines) {
    if (line.includes('PROMPTS:')) {
      currentSection = 'prompts'
    } else if (line.includes('VARIATIONS:')) {
      currentSection = 'variations'
    } else if (line.includes('TIPS:')) {
      currentSection = 'tips'
    } else if (line.startsWith('-') && line.trim().length > 1) {
      const content = line.substring(1).trim()
      
      switch (currentSection) {
        case 'prompts':
          prompts.push(content)
          break
        case 'variations':
          variations.push(content)
          break
        case 'tips':
          tips.push(content)
          break
      }
    }
  }
  
  return {
    prompts: prompts.slice(0, 3),
    variations: variations.slice(0, 2),
    tips: tips.slice(0, 3),
  }
}
