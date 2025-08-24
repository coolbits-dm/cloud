import { z } from 'zod'

export const leadSchema = z.object({
  email: z.string().email('Invalid email address'),
  name: z.string().min(2, 'Name must be at least 2 characters').optional(),
  company: z.string().min(1, 'Company name is required').optional(),
  phone: z.string().regex(/^\+?[\d\s\-\(\)]+$/, 'Invalid phone number').optional(),
  message: z.string().min(10, 'Message must be at least 10 characters').optional(),
  source: z.string().default('website'),
})

export const leadUpdateSchema = leadSchema.partial().extend({
  id: z.string().cuid(),
  status: z.enum(['new', 'contacted', 'qualified', 'converted', 'lost']).optional(),
})

export type Lead = z.infer<typeof leadSchema>
export type LeadUpdate = z.infer<typeof leadUpdateSchema>
export type LeadWithId = Lead & { id: string; createdAt: Date; updatedAt: Date }
