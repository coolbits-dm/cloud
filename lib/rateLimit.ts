import { RateLimiterMemory } from 'rate-limiter-flexible'
import { NextRequest, NextResponse } from 'next/server'

/** Env flags */
const RL_DISABLED =
  String(process.env.RATE_LIMIT_DISABLED || '').toLowerCase() === '1' ||
  String(process.env.RATE_LIMIT_DISABLED || '').toLowerCase() === 'true'

/** Upstash Redis (opțional) */
type UpstashLike = {
  get: (key: string) => Promise<any>
  incr: (key: string) => Promise<number>
  expire: (key: string, seconds: number) => Promise<number>
  ttl: (key: string) => Promise<number>
}
let redis: UpstashLike | null = null
try {
  // Lazy import ca să nu stricăm buildul dacă nu e prezent
  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  // @ts-ignore
  const { Redis } = await import('@upstash/redis')
  const url = process.env.UPSTASH_REDIS_URL
  const token = process.env.UPSTASH_REDIS_TOKEN
  if (url && token) {
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore
    redis = new Redis({ url, token }) as UpstashLike
  }
} catch {
  // no-op
}

/** Config + registry */
export interface RateLimitConfig {
  maxRequests: number
  windowMs: number
  keyGenerator?: (req: NextRequest) => string
}
type RegistryEntry = {
  limiter: RateLimiterMemory
  keyGen: (req: NextRequest) => string
  limit: number
  windowMs: number
}
const registry = new Map<string, RegistryEntry>()

export function ipFromRequest(req: NextRequest): string {
  const xff = req.headers.get('x-forwarded-for')
  if (xff) return xff.split(',')[0].trim()
  const xrip = req.headers.get('x-real-ip')
  if (xrip) return xrip
  return 'unknown'
}

export function createRateLimiter(name: string, config: RateLimitConfig): RateLimiterMemory {
  const limiter = new RateLimiterMemory({
    points: config.maxRequests,
    duration: Math.ceil(config.windowMs / 1000),
  })
  const keyGen =
    config.keyGenerator ||
    ((req: NextRequest) => {
      const ip = ipFromRequest(req)
      return `${name}:${ip}`
    })

  registry.set(name, { limiter, keyGen, limit: config.maxRequests, windowMs: config.windowMs })
  return limiter
}

function ensureEntry(name: string): RegistryEntry {
  const entry = registry.get(name)
  if (!entry) throw new Error(`Rate limiter '${name}' not found. Define it via createRateLimiter().`)
  return entry
}

/** ---- CHECK (non-mutating dacă e Upstash), fallback Memory.get() ---- */
export async function checkRateLimit(
  name: string,
  req: NextRequest
): Promise<{ allowed: boolean; remaining: number; resetTime: number }> {
  if (RL_DISABLED) return { allowed: true, remaining: 9_999, resetTime: 0 }

  const entry = ensureEntry(name)
  const key = entry.keyGen(req)

  // Upstash: încercăm să citim fără să incrementăm
  if (redis) {
    try {
      const raw = await redis.get(key)
      const current = Number(raw ?? 0)
      let ttl = await redis.ttl(key) // secunde (-2 = no key, -1 = no expire)
      if (ttl < 0) ttl = Math.ceil(entry.windowMs / 1000)
      const remaining = Math.max(0, entry.limit - current)
      return {
        allowed: remaining > 0,
        remaining,
        resetTime: Date.now() + ttl * 1000,
      }
    } catch (e) {
      console.warn('[rateLimit] Upstash check failed, allowing. Err:', e)
      return { allowed: true, remaining: entry.limit, resetTime: entry.windowMs }
    }
  }

  // Memory fallback
  try {
    // get() nu consumă; poate întoarce null
    // @ts-ignore rate-limiter-flexible types
    const res = await entry.limiter.get(key)
    if (!res) {
      return { allowed: true, remaining: entry.limit, resetTime: entry.windowMs }
    }
    const remaining = Math.max(0, res.remainingPoints)
    return {
      allowed: remaining > 0,
      remaining,
      resetTime: res.msBeforeNext || 0,
    }
  } catch (e) {
    console.warn('[rateLimit] Memory check failed, allowing. Err:', e)
    return { allowed: true, remaining: entry.limit, resetTime: entry.windowMs }
  }
}

/** ---- CONSUME (mutating) ---- */
export async function consumeRateLimit(
  name: string,
  req: NextRequest
): Promise<{ allowed: boolean; remaining: number; resetTime: number }> {
  if (RL_DISABLED) return { allowed: true, remaining: 9_999, resetTime: 0 }

  const entry = ensureEntry(name)
  const key = entry.keyGen(req)
  const windowSec = Math.ceil(entry.windowMs / 1000)

  if (redis) {
    try {
      const current = await redis.incr(key)
      if (current === 1) {
        await redis.expire(key, windowSec)
      }
      let ttl = await redis.ttl(key)
      if (ttl < 0) ttl = windowSec
      const remaining = Math.max(0, entry.limit - current)
      const allowed = current <= entry.limit
      return {
        allowed,
        remaining,
        resetTime: Date.now() + ttl * 1000,
      }
    } catch (e) {
      console.warn('[rateLimit] Upstash consume failed, allowing. Err:', e)
      return { allowed: true, remaining: entry.limit - 1, resetTime: entry.windowMs }
    }
  }

  // Memory fallback
  try {
    const res = await entry.limiter.consume(key, 1) // aruncă RateLimiterRes dacă e depășit
    return {
      allowed: true,
      remaining: Math.max(0, res.remainingPoints),
      resetTime: res.msBeforeNext || 0,
    }
  } catch (err: any) {
    const ms = typeof err?.msBeforeNext === 'number' ? err.msBeforeNext : entry.windowMs
    return { allowed: false, remaining: 0, resetTime: ms }
  }
}

/** Middleware helper pentru Next API routes */
export async function withRateLimit(
  req: NextRequest,
  limiterName: keyof typeof commonRateLimiters,
  handler: () => Promise<NextResponse>
): Promise<NextResponse> {
  const entry = ensureEntry(String(limiterName))
  const pre = await checkRateLimit(String(limiterName), req)
  if (!pre.allowed) {
    return NextResponse.json(
      {
        success: false,
        message: 'Rate limit exceeded',
        errors: ['Too many requests. Please try again later.'],
      },
      {
        status: 429,
        headers: {
          'X-RateLimit-Limit': String(entry.limit),
          'X-RateLimit-Remaining': String(pre.remaining),
          'X-RateLimit-Reset': new Date(Date.now() + pre.resetTime).toISOString(),
          'Retry-After': String(Math.ceil(pre.resetTime / 1000)),
        },
      }
    )
  }

  const post = await consumeRateLimit(String(limiterName), req)
  const res = await handler()
  res.headers.set('X-RateLimit-Limit', String(entry.limit))
  res.headers.set('X-RateLimit-Remaining', String(post.remaining))
  res.headers.set('X-RateLimit-Reset', new Date(Date.now() + post.resetTime).toISOString())
  return res
}

/** Preconfig standard */
export const commonRateLimiters = {
  api: createRateLimiter('api', {
    maxRequests: 100,
    windowMs: 60_000,
  }),
  chat: createRateLimiter('chat', {
    maxRequests: 20,
    windowMs: 60_000,
  }),
  leadSubmission: createRateLimiter('leadSubmission', {
    maxRequests: 5,
    windowMs: 60 * 60_000,
  }),
  auth: createRateLimiter('auth', {
    maxRequests: 10,
    windowMs: 60 * 60_000,
  }),
}
