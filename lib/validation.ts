import { z } from 'zod'

// Common validation patterns
export const commonValidations = {
  email: z.string().email('Invalid email address'),
  phone: z.string().regex(/^\+?[\d\s\-\(\)]+$/, 'Invalid phone number'),
  name: z.string().min(2, 'Must be at least 2 characters').max(100, 'Must be less than 100 characters'),
  company: z.string().min(1, 'Company name is required').max(200, 'Company name too long'),
  message: z.string().min(10, 'Message must be at least 10 characters').max(1000, 'Message too long'),
  url: z.string().url('Invalid URL'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
}

// Sanitization helpers
export function sanitizeInput(input: string): string {
  return input
    .trim()
    .replace(/[<>]/g, '') // Remove potential HTML tags
    .replace(/&/g, '&amp;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    .replace(/\//g, '&#x2F;')
}

export function validateAndSanitize<T>(
  schema: z.ZodSchema<T>,
  data: unknown
): { success: true; data: T } | { success: false; errors: string[] } {
  try {
    const result = schema.parse(data)
    return { success: true, data: result }
  } catch (error) {
    if (error instanceof z.ZodError) {
      const errors = error.errors.map(err => err.message)
      return { success: false, errors }
    }
    return { success: false, errors: ['Validation failed'] }
  }
}

// Rate limiting validation
export const rateLimitSchema = z.object({
  identifier: z.string(),
  maxRequests: z.number().min(1),
  windowMs: z.number().min(1000),
})

// API response validation
export const apiResponseSchema = z.object({
  success: z.boolean(),
  message: z.string(),
  data: z.any().optional(),
  errors: z.array(z.string()).optional(),
})

export type ApiResponse<T = any> = {
  success: boolean
  message: string
  data?: T
  errors?: string[]
}

// Helper function to create consistent API responses
export function createApiResponse<T>(
  success: boolean,
  message: string,
  data?: T,
  errors?: string[]
): ApiResponse<T> {
  return {
    success,
    message,
    ...(data && { data }),
    ...(errors && { errors }),
  }
}

// Validation for file uploads
export const fileUploadSchema = z.object({
  filename: z.string(),
  mimetype: z.string().refine(
    (type) => ['image/jpeg', 'image/png', 'image/gif', 'application/pdf'].includes(type),
    'Unsupported file type'
  ),
  size: z.number().max(5 * 1024 * 1024, 'File size must be less than 5MB'),
})

// Validation for search queries
export const searchQuerySchema = z.object({
  q: z.string().min(1, 'Search query cannot be empty'),
  page: z.number().min(1).default(1),
  limit: z.number().min(1).max(100).default(20),
  filters: z.record(z.any()).optional(),
  sortBy: z.string().optional(),
  sortOrder: z.enum(['asc', 'desc']).default('desc'),
})
