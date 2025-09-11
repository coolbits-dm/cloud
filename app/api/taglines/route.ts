import { NextRequest, NextResponse } from 'next/server'
import { generateTaglines, generatePrompts } from '@/utils/nlpProcessor'
import { withRateLimit } from '@/lib/rateLimit'
import { createApiResponse } from '@/lib/validation'
import logger from '@/lib/logger'

export async function POST(request: NextRequest) {
  return withRateLimit(request, 'api', async () => {
    try {
      const body = await request.json()
      const { type, ...data } = body

      if (type === 'taglines') {
        // Generate taglines
        const result = await generateTaglines(data)
        
        logger.info('Taglines generated successfully', { 
          company: data.companyName, 
          industry: data.industry 
        })

        return NextResponse.json(
          createApiResponse(true, 'Taglines generated successfully', result),
          { status: 200 }
        )
      } else if (type === 'prompts') {
        // Generate prompts
        const result = await generatePrompts(data)
        
        logger.info('Prompts generated successfully', { 
          goal: data.goal, 
          audience: data.audience 
        })

        return NextResponse.json(
          createApiResponse(true, 'Prompts generated successfully', result),
          { status: 200 }
        )
      } else {
        return NextResponse.json(
          createApiResponse(false, 'Invalid type. Must be "taglines" or "prompts"'),
          { status: 400 }
        )
      }

    } catch (error) {
      logger.error('NLP processing error', { error })
      
      return NextResponse.json(
        createApiResponse(false, 'Failed to process request'),
        { status: 500 }
      )
    }
  })
}

export async function GET(request: NextRequest) {
  return withRateLimit(request, 'api', async () => {
    try {
      const { searchParams } = new URL(request.url)
      const type = searchParams.get('type')

      if (type === 'taglines') {
        return NextResponse.json(
          createApiResponse(true, 'Tagline generation endpoint', {
            endpoint: '/api/taglines',
            method: 'POST',
            requiredFields: ['type', 'industry', 'companyName', 'description', 'tone', 'length'],
            example: {
              type: 'taglines',
              industry: 'Technology',
              companyName: 'TechCorp',
              description: 'Innovative software solutions for modern businesses',
              tone: 'professional',
              length: 'short'
            }
          }),
          { status: 200 }
        )
      } else if (type === 'prompts') {
        return NextResponse.json(
          createApiResponse(true, 'Prompt generation endpoint', {
            endpoint: '/api/taglines',
            method: 'POST',
            requiredFields: ['type', 'context', 'goal', 'audience', 'style', 'length'],
            example: {
              type: 'prompts',
              context: 'Business strategy consultation',
              goal: 'Generate strategic recommendations',
              audience: 'C-level executives',
              style: 'formal',
              length: 'detailed'
            }
          }),
          { status: 200 }
        )
      } else {
        return NextResponse.json(
          createApiResponse(true, 'NLP Processing API', {
            endpoints: [
              {
                type: 'taglines',
                description: 'Generate creative taglines for businesses',
                url: '/api/taglines?type=taglines'
              },
              {
                type: 'prompts',
                description: 'Generate effective AI prompts',
                url: '/api/taglines?type=prompts'
              }
            ],
            usage: 'Send POST request with type and required data fields'
          }),
          { status: 200 }
        )
      }

    } catch (error) {
      logger.error('API documentation error', { error })
      
      return NextResponse.json(
        createApiResponse(false, 'Internal server error'),
        { status: 500 }
      )
    }
  })
}


