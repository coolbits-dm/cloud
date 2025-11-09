import { Redis } from '@upstash/redis'

// Initialize Redis client if UPSTASH_REDIS_REST_URL is available
let redis: Redis | null = null

if (process.env.UPSTASH_REDIS_REST_URL && process.env.UPSTASH_REDIS_REST_TOKEN) {
  redis = new Redis({
    url: process.env.UPSTASH_REDIS_REST_URL,
    token: process.env.UPSTASH_REDIS_REST_TOKEN,
  })
}

export interface CacheOptions {
  ttl?: number // Time to live in seconds
}

export class KVStore {
  private redis: Redis | null

  constructor() {
    this.redis = redis
  }

  async get<T>(key: string): Promise<T | null> {
    if (!this.redis) {
      console.warn('Redis not configured, falling back to memory storage')
      return this.getFromMemory<T>(key)
    }

    try {
      const value = await this.redis.get(key)
      return value as T
    } catch (error) {
      console.error('Redis get error:', error)
      return this.getFromMemory<T>(key)
    }
  }

  async set<T>(key: string, value: T, options: CacheOptions = {}): Promise<void> {
    if (!this.redis) {
      console.warn('Redis not configured, using memory storage')
      this.setInMemory(key, value, options.ttl)
      return
    }

    try {
      if (options.ttl) {
        await this.redis.setex(key, options.ttl, value)
      } else {
        await this.redis.set(key, value)
      }
    } catch (error) {
      console.error('Redis set error:', error)
      this.setInMemory(key, value, options.ttl)
    }
  }

  async delete(key: string): Promise<void> {
    if (!this.redis) {
      this.deleteFromMemory(key)
      return
    }

    try {
      await this.redis.del(key)
    } catch (error) {
      console.error('Redis delete error:', error)
      this.deleteFromMemory(key)
    }
  }

  async exists(key: string): Promise<boolean> {
    if (!this.redis) {
      return this.existsInMemory(key)
    }

    try {
      const result = await this.redis.exists(key)
      return result === 1
    } catch (error) {
      console.error('Redis exists error:', error)
      return this.existsInMemory(key)
    }
  }

  async increment(key: string, amount: number = 1): Promise<number> {
    if (!this.redis) {
      return this.incrementInMemory(key, amount)
    }

    try {
      return await this.redis.incrby(key, amount)
    } catch (error) {
      console.error('Redis increment error:', error)
      return this.incrementInMemory(key, amount)
    }
  }

  // Memory fallback storage
  private memoryStorage = new Map<string, { value: any; expiresAt?: number }>()

  private getFromMemory<T>(key: string): T | null {
    const item = this.memoryStorage.get(key)
    if (!item) return null

    if (item.expiresAt && Date.now() > item.expiresAt) {
      this.memoryStorage.delete(key)
      return null
    }

    return item.value as T
  }

  private setInMemory<T>(key: string, value: T, ttl?: number): void {
    const expiresAt = ttl ? Date.now() + (ttl * 1000) : undefined
    this.memoryStorage.set(key, { value, expiresAt })
  }

  private deleteFromMemory(key: string): void {
    this.memoryStorage.delete(key)
  }

  private existsInMemory(key: string): boolean {
    return this.memoryStorage.has(key)
  }

  private incrementInMemory(key: string, amount: number): number {
    const current = this.getFromMemory<number>(key) || 0
    const newValue = current + amount
    this.setInMemory(key, newValue)
    return newValue
  }
}

// Session management utilities
export class SessionManager {
  private kv: KVStore

  constructor() {
    this.kv = new KVStore()
  }

  async createSession(userId: string, data: any): Promise<string> {
    const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    await this.kv.set(`session:${sessionId}`, {
      userId,
      data,
      createdAt: Date.now(),
    }, { ttl: 24 * 60 * 60 }) // 24 hours

    return sessionId
  }

  async getSession(sessionId: string): Promise<any> {
    return await this.kv.get(`session:${sessionId}`)
  }

  async updateSession(sessionId: string, data: any): Promise<void> {
    const existing = await this.getSession(sessionId)
    if (existing) {
      await this.kv.set(`session:${sessionId}`, {
        ...existing,
        ...data,
        updatedAt: Date.now(),
      }, { ttl: 24 * 60 * 60 })
    }
  }

  async deleteSession(sessionId: string): Promise<void> {
    await this.kv.delete(`session:${sessionId}`)
  }

  async extendSession(sessionId: string): Promise<void> {
    const session = await this.getSession(sessionId)
    if (session) {
      await this.kv.set(`session:${sessionId}`, session, { ttl: 24 * 60 * 60 })
    }
  }
}

// Cache utilities
export class CacheManager {
  private kv: KVStore

  constructor() {
    this.kv = new KVStore()
  }

  async getCached<T>(key: string): Promise<T | null> {
    return await this.kv.get<T>(key)
  }

  async setCached<T>(key: string, value: T, ttl: number = 3600): Promise<void> {
    await this.kv.set(key, value, { ttl })
  }

  async invalidatePattern(pattern: string): Promise<void> {
    // Note: This is a simplified implementation
    // In production with Redis, you'd use SCAN or similar
    console.log(`Cache invalidation requested for pattern: ${pattern}`)
  }

  async clearAll(): Promise<void> {
    // Note: This is a simplified implementation
    // In production with Redis, you'd use FLUSHDB or similar
    console.log('Cache clear requested')
  }
}

// Export instances
export const kvStore = new KVStore()
export const sessionManager = new SessionManager()
export const cacheManager = new CacheManager()

// Utility functions
export async function withCache<T>(
  key: string,
  ttl: number,
  fetcher: () => Promise<T>
): Promise<T> {
  const cached = await cacheManager.getCached<T>(key)
  if (cached) return cached

  const fresh = await fetcher()
  await cacheManager.setCached(key, fresh, ttl)
  return fresh
}
