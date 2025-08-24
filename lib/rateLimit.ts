import { RateLimiterMemory } from 'rate-limiter-flexible'
import { NextRequest, NextResponse } from 'next/server'

// In-memory rate limiter (for development)
// In production, consider using Redis or database-based rate limiting
const rateLimiters = new Map<string, RateLimiterMemory>()

export interface RateLimitConfig {
  maxRequests: number
  windowMs: number
  keyGenerator?: (req: NextRequest) => string
}

export function createRateLimiter(
  name: string,
  config: RateLimitConfig
): RateLimiterMemory {
  const limiter = new RateLimiterMemory({
    points: config.maxRequests,
    duration: config.windowMs / 1000, // Convert to seconds
  })

  // Store the key generator separately
  ;(limiter as any).keyGenerator = config.keyGenerator || ((req: NextRequest) => {
    // Default: use IP address as key
    const forwarded = req.headers.get('x-forwarded-for')
    const ip = forwarded ? forwarded.split(',')[0] : 'unknown'
    return `${name}:${ip}`
  })

  rateLimiters.set(name, limiter)
  return limiter
}

export async function checkRateLimit(
  name: string,
  req: NextRequest
): Promise<{ allowed: boolean; remaining: number; resetTime: number }> {
  // Temporarily disable rate limiting to debug the issue
  console.log(`Rate limiting temporarily disabled for ${name}`)
  return { allowed: true, remaining: 999, resetTime: 0 }
  
  // Original code commented out for debugging
  /*
  const limiter = rateLimiters.get(name)
  
  if (!limiter) {
    throw new Error(`Rate limiter '${name}' not found`)
  }

  try {
    const key = limiter.keyGenerator!(req)
    const result = await limiter.get(key)
    
    // Check if result exists and has required properties
    if (!result || typeof result.remainingPoints === 'undefined') {
      console.warn('Rate limiter returned invalid result, allowing request')
      return { allowed: true, remaining: 999, resetTime: 0 }
    }
    
    if (result.remainingPoints <= 0) {
      return {
        allowed: false,
        remaining: 0,
        resetTime: result.msBeforeNext || 0,
      }
    }

    return {
      allowed: true,
      remaining: result.remainingPoints,
      resetTime: result.msBeforeNext || 0,
    }
  } catch (error) {
    console.error('Rate limit check failed:', error)
    // Allow request if rate limiting fails
    return { allowed: true, remaining: 999, resetTime: 0 }
  }
  */
}

export async function consumeRateLimit(
  name: string,
  req: NextRequest
): Promise<{ allowed: boolean; remaining: number; resetTime: number }> {
  // Temporarily disable rate limiting to debug the issue
  console.log(`Rate limiting consume temporarily disabled for ${name}`)
  return { allowed: true, remaining: 999, resetTime: 0 }
  
  // Original code commented out for debugging
  /*
  const limiter = rateLimiters.get(name)
  
  if (!limiter) {
    throw new Error(`Rate limiter '${name}' not found`)
  }

  try {
    const key = limiter.keyGenerator!(req)
    const result = await limiter.consume(key)
    
    // Check if result exists and has required properties
    if (!result || typeof result.remainingPoints === 'undefined') {
      console.warn('Rate limiter consume returned invalid result')
      return { allowed: true, remaining: 999, resetTime: 0 }
    }
    
    return {
      allowed: true,
      remaining: result.remainingPoints,
      resetTime: result.msBeforeNext || 0,
    }
  } catch (error) {
    if (error instanceof Error && error.message.includes('too many requests')) {
      try {
        const key = limiter.keyGenerator!(req)
        const result = await limiter.get(key)
        
        return {
          allowed: false,
          remaining: 0,
          resetTime: result?.msBeforeNext || 0,
        }
      } catch (getError) {
        console.error('Failed to get rate limit info after consume error:', getError)
        return { allowed: false, remaining: 0, resetTime: 0 }
      }
    }
    
    console.error('Rate limit consumption failed:', error)
    return { allowed: true, remaining: 999, resetTime: 0 }
  }
  */
}

// Pre-configured rate limiters for common use cases
export const commonRateLimiters = {
  // API endpoints: 100 requests per minute
  api: createRateLimiter('api', {
    maxRequests: 100,
    windowMs: 60 * 1000,
  }),

  // Chat endpoints: 20 requests per minute
  chat: createRateLimiter('chat', {
    maxRequests: 20,
    windowMs: 60 * 1000,
  }),

  // Lead submission: 5 requests per hour
  leadSubmission: createRateLimiter('leadSubmission', {
    maxRequests: 5,
    windowMs: 60 * 60 * 1000,
  }),

  // Authentication: 10 attempts per hour
  auth: createRateLimiter('auth', {
    maxRequests: 10,
    windowMs: 60 * 60 * 1000,
  }),
}

// Middleware function for Next.js API routes
export async function withRateLimit(
  req: NextRequest,
  limiterName: keyof typeof commonRateLimiters,
  handler: () => Promise<NextResponse>
): Promise<NextResponse> {
  const rateLimitResult = await checkRateLimit(limiterName, req)
  
  if (!rateLimitResult.allowed) {
    return NextResponse.json(
      {
        success: false,
        message: 'Rate limit exceeded',
        errors: ['Too many requests. Please try again later.'],
      },
      {
        status: 429,
        headers: {
          'X-RateLimit-Limit': '100',
          'X-RateLimit-Remaining': '0',
          'X-RateLimit-Reset': new Date(Date.now() + rateLimitResult.resetTime).toISOString(),
        },
      }
    )
  }

  // Consume the rate limit
  await consumeRateLimit(limiterName, req)
  
  // Execute the handler
  return handler()
}
