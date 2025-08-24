import { z } from 'zod'

export const auditLogSchema = z.object({
  action: z.string().min(1, 'Action is required'),
  resource: z.string().min(1, 'Resource is required'),
  userId: z.string().optional(),
  ipAddress: z.string().ip().optional(),
  userAgent: z.string().optional(),
  metadata: z.record(z.any()).optional(),
})

export const auditLogQuerySchema = z.object({
  action: z.string().optional(),
  resource: z.string().optional(),
  userId: z.string().optional(),
  startDate: z.string().datetime().optional(),
  endDate: z.string().datetime().optional(),
  limit: z.number().min(1).max(100).default(50),
  offset: z.number().min(0).default(0),
})

export type AuditLog = z.infer<typeof auditLogSchema>
export type AuditLogQuery = z.infer<typeof auditLogQuerySchema>
export type AuditLogWithId = AuditLog & { id: string; createdAt: Date }
