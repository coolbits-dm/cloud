import { Resend } from 'resend'
import nodemailer from 'nodemailer'
import { Lead } from '@/schemas/lead'

// Initialize Resend
const resend = new Resend(process.env.RESEND_API_KEY || 'demo-key')

// Nodemailer fallback configuration
const createTransporter = () => {
  return nodemailer.createTransport({
    host: process.env.SMTP_HOST || 'smtp.gmail.com',
    port: parseInt(process.env.SMTP_PORT || '587'),
    secure: false,
    auth: {
      user: process.env.SMTP_USER,
      pass: process.env.SMTP_PASS,
    },
  })
}

export async function sendWelcomeEmail(lead: Lead) {
  try {
    // Try Resend first
    if (process.env.RESEND_API_KEY && process.env.RESEND_API_KEY !== 'demo-key') {
      const { data, error } = await resend.emails.send({
        from: 'CoolBits <noreply@coolbits.com>',
        to: lead.email,
        subject: 'Welcome to CoolBits! 🚀',
        html: generateWelcomeEmailHTML(lead),
      })

      if (error) {
        console.error('Resend error:', error)
        throw error
      }

      return { success: true, provider: 'resend', messageId: data?.id }
    }

    // Fallback to Nodemailer
    if (process.env.SMTP_USER && process.env.SMTP_PASS) {
      const transporter = createTransporter()
      
      const info = await transporter.sendMail({
        from: process.env.SMTP_USER,
        to: lead.email,
        subject: 'Welcome to CoolBits! 🚀',
        html: generateWelcomeEmailHTML(lead),
      })

      return { success: true, provider: 'nodemailer', messageId: info.messageId }
    }

    // If no email provider is configured, return success but log it
    console.log('No email provider configured, skipping email send')
    return { success: true, provider: 'none', messageId: 'skipped' }
  } catch (error) {
    console.error('Email sending failed:', error)
    // Don't throw error, just return failure
    return { success: false, provider: 'error', error: error instanceof Error ? error.message : 'Unknown error' }
  }
}

export async function sendNotificationEmail(lead: Lead, adminEmail: string) {
  try {
    const subject = 'New Lead Submission - CoolBits'
    const html = generateNotificationEmailHTML(lead)

    if (process.env.RESEND_API_KEY && process.env.RESEND_API_KEY !== 'demo-key') {
      const { data, error } = await resend.emails.send({
        from: 'CoolBits <noreply@coolbits.com>',
        to: adminEmail,
        subject,
        html,
      })

      if (error) throw error
      return { success: true, provider: 'resend', messageId: data?.id }
    }

    if (process.env.SMTP_USER && process.env.SMTP_PASS) {
      const transporter = createTransporter()
      
      const info = await transporter.sendMail({
        from: process.env.SMTP_USER,
        to: adminEmail,
        subject,
        html,
      })

      return { success: true, provider: 'nodemailer', messageId: info.messageId }
    }

    // If no email provider is configured, return success but log it
    console.log('No email provider configured, skipping notification email')
    return { success: true, provider: 'none', messageId: 'skipped' }
  } catch (error) {
    console.error('Notification email failed:', error)
    // Don't throw error, just return failure
    return { success: false, provider: 'error', error: error instanceof Error ? error.message : 'Unknown error' }
  }
}

function generateWelcomeEmailHTML(lead: Lead): string {
  return `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>Welcome to CoolBits</title>
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
      <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h1 style="color: #3b82f6;">Welcome to CoolBits! 🚀</h1>
        <p>Hi ${lead.name || 'there'},</p>
        <p>Thank you for your interest in CoolBits! We're excited to have you on board.</p>
        <p>We'll review your submission and get back to you soon.</p>
        <div style="background: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0;">
          <h3>Your Submission Details:</h3>
          <p><strong>Email:</strong> ${lead.email}</p>
          ${lead.company ? `<p><strong>Company:</strong> ${lead.company}</p>` : ''}
          ${lead.phone ? `<p><strong>Phone:</strong> ${lead.phone}</p>` : ''}
          ${lead.message ? `<p><strong>Message:</strong> ${lead.message}</p>` : ''}
        </div>
        <p>Best regards,<br>The CoolBits Team</p>
      </div>
    </body>
    </html>
  `
}

function generateNotificationEmailHTML(lead: Lead): string {
  return `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>New Lead - CoolBits</title>
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
      <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h1 style="color: #3b82f6;">New Lead Submission 🎯</h1>
        <div style="background: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0;">
          <h3>Lead Details:</h3>
          <p><strong>Name:</strong> ${lead.name || 'Not provided'}</p>
          <p><strong>Email:</strong> ${lead.email}</p>
          <p><strong>Company:</strong> ${lead.company || 'Not provided'}</p>
          <p><strong>Phone:</strong> ${lead.phone || 'Not provided'}</p>
          <p><strong>Message:</strong> ${lead.message || 'No message'}</p>
          <p><strong>Source:</strong> ${lead.source}</p>
          <p><strong>Submitted:</strong> ${new Date().toLocaleString()}</p>
        </div>
        <p>Please follow up with this lead as soon as possible.</p>
      </div>
    </body>
    </html>
  `
}
