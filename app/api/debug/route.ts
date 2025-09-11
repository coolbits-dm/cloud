import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    // Test external connectivity
    const testUrls = [
      'https://api.openai.com/v1/models',
      'https://api.x.ai/v1/models',
      'https://httpbin.org/get'
    ]

    const connectivityResults = await Promise.allSettled(
      testUrls.map(async (url) => {
        const start = Date.now()
        const response = await fetch(url, { 
          method: 'GET',
          headers: { 'User-Agent': 'CoolBits-Debug/1.0' }
        })
        const end = Date.now()
        return {
          url,
          status: response.status,
          responseTime: end - start,
          ok: response.ok
        }
      })
    )

    return NextResponse.json({
      success: true,
      timestamp: new Date().toISOString(),
      environment: process.env.NODE_ENV || 'unknown',
      connectivity: {
        openai: connectivityResults[0].status === 'fulfilled' ? connectivityResults[0].value : { error: connectivityResults[0].reason?.message },
        xai: connectivityResults[1].status === 'fulfilled' ? connectivityResults[1].value : { error: connectivityResults[1].reason?.message },
        httpbin: connectivityResults[2].status === 'fulfilled' ? connectivityResults[2].value : { error: connectivityResults[2].reason?.message }
      },
      secrets: {
        hasOpenAIKey: !!process.env.OPENAI_API_KEY,
        hasXAIKey: !!process.env.XAI_API_KEY,
        hasSecretManager: !!process.env.GOOGLE_APPLICATION_CREDENTIALS
      }
    })
  } catch (error) {
    console.error('Debug route error:', error)
    return NextResponse.json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString()
    }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    return NextResponse.json({
      success: true,
      message: 'Debug endpoint working',
      received: body,
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    return NextResponse.json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString()
    }, { status: 500 })
  }
}
