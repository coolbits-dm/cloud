import winston from 'winston'

// Define log levels
const levels = {
  error: 0,
  warn: 1,
  info: 2,
  http: 3,
  debug: 4,
}

// Define colors for each level
const colors = {
  error: 'red',
  warn: 'yellow',
  info: 'green',
  http: 'magenta',
  debug: 'white',
}

// Tell winston that you want to link the colors
winston.addColors(colors)

// Define which level to log based on environment
const level = () => {
  const env = process.env.NODE_ENV || 'development'
  const isDevelopment = env === 'development'
  return isDevelopment ? 'debug' : 'warn'
}

// Define different log formats
const logFormat = winston.format.combine(
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss:ms' }),
  winston.format.colorize({ all: true }),
  winston.format.printf(
    (info) => `${info.timestamp} ${info.level}: ${info.message}`,
  ),
)

// Define transports
const transports = [
  // Console transport
  new winston.transports.Console({
    format: logFormat,
  }),
  
  // File transport for errors
  new winston.transports.File({
    filename: 'logs/error.log',
    level: 'error',
    format: winston.format.combine(
      winston.format.timestamp(),
      winston.format.json()
    ),
  }),
  
  // File transport for all logs
  new winston.transports.File({
    filename: 'logs/combined.log',
    format: winston.format.combine(
      winston.format.timestamp(),
      winston.format.json()
    ),
  }),
]

// Create the logger
const logger = winston.createLogger({
  level: level(),
  levels,
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  transports,
})

// Create a stream object for Morgan (HTTP logging middleware)
export const logStream = {
  write: (message: string) => {
    logger.http(message.trim())
  },
}

// Helper functions for common logging scenarios
export function logApiRequest(method: string, url: string, statusCode: number, responseTime: number) {
  const level = statusCode >= 400 ? 'warn' : 'info'
  logger.log(level, `${method} ${url} - ${statusCode} (${responseTime}ms)`)
}

export function logError(error: Error, context?: Record<string, any>) {
  logger.error('Application error', {
    error: error.message,
    stack: error.stack,
    context,
  })
}

export function logLeadSubmission(lead: { email: string; company?: string; source: string }) {
  logger.info('New lead submission', {
    email: lead.email,
    company: lead.company,
    source: lead.source,
    timestamp: new Date().toISOString(),
  })
}

export function logChatMessage(model: string, sessionId: string, role: string, contentLength: number) {
  logger.info('Chat message processed', {
    model,
    sessionId,
    role,
    contentLength,
    timestamp: new Date().toISOString(),
  })
}

export function logRateLimitExceeded(identifier: string, ip: string) {
  logger.warn('Rate limit exceeded', {
    identifier,
    ip,
    timestamp: new Date().toISOString(),
  })
}

export function logDatabaseOperation(operation: string, table: string, duration: number) {
  logger.debug('Database operation', {
    operation,
    table,
    duration,
    timestamp: new Date().toISOString(),
  })
}

export default logger
