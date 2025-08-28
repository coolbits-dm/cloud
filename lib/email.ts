// lib/email.ts
import { Resend } from "resend";
import nodemailer from "nodemailer";
import type { Lead } from "@/schemas/lead";

const RESEND_API_KEY = process.env.RESEND_API_KEY || "";
const EMAIL_FROM = process.env.EMAIL_FROM || "CoolBits <noreply@coolbits.ai>";
const ADMIN_EMAIL = process.env.ADMIN_EMAIL || "";

const resend = RESEND_API_KEY ? new Resend(RESEND_API_KEY) : null;

function createTransporter() {
  const host = process.env.SMTP_HOST || "smtp.gmail.com";
  const port = Number(process.env.SMTP_PORT || 587);
  const user = process.env.SMTP_USER || "";
  const pass = process.env.SMTP_PASS || "";
  if (!user || !pass) return null;

  return nodemailer.createTransport({
    host,
    port,
    secure: port === 465,
    auth: { user, pass },
  });
}

export async function sendWelcomeEmail(lead: Lead) {
  const subject = "Welcome to CoolBits! 🚀";
  const html = generateWelcomeEmailHTML(lead);

  try {
    if (resend) {
      const { data, error } = await resend.emails.send({
        from: EMAIL_FROM,
        to: lead.email,
        subject,
        html,
      });
      if (error) throw error;
      return { success: true, provider: "resend", messageId: data?.id };
    }

    const transporter = createTransporter();
    if (transporter) {
      const info = await transporter.sendMail({
        from: EMAIL_FROM,
        to: lead.email,
        subject,
        html,
      });
      return {
        success: true,
        provider: "nodemailer",
        messageId: info.messageId,
      };
    }

    console.log("[email] No provider configured. Skipping welcome email.");
    return { success: true, provider: "none", messageId: "skipped" };
  } catch (error: any) {
    console.error("Email sending failed:", error);
    return {
      success: false,
      provider: "error",
      error: String(error?.message || error),
    };
  }
}

export async function sendNotificationEmail(lead: Lead, adminEmail?: string) {
  const to = adminEmail || ADMIN_EMAIL;
  const subject = "New Lead Submission - CoolBits";
  const html = generateNotificationEmailHTML(lead);

  if (!to) {
    console.log("[email] ADMIN_EMAIL missing. Skipping notification.");
    return { success: true, provider: "none", messageId: "skipped" };
  }

  try {
    if (resend) {
      const { data, error } = await resend.emails.send({
        from: EMAIL_FROM,
        to,
        subject,
        html,
      });
      if (error) throw error;
      return { success: true, provider: "resend", messageId: data?.id };
    }

    const transporter = createTransporter();
    if (transporter) {
      const info = await transporter.sendMail({
        from: EMAIL_FROM,
        to,
        subject,
        html,
      });
      return {
        success: true,
        provider: "nodemailer",
        messageId: info.messageId,
      };
    }

    console.log("[email] No provider configured. Skipping admin notification.");
    return { success: true, provider: "none", messageId: "skipped" };
  } catch (error: any) {
    console.error("Notification email failed:", error);
    return {
      success: false,
      provider: "error",
      error: String(error?.message || error),
    };
  }
}

function generateWelcomeEmailHTML(lead: Lead): string {
  return `
    <!doctype html><html><head><meta charset="utf-8"><title>Welcome</title></head>
    <body style="font-family: Arial,sans-serif; line-height:1.6; color:#111">
      <div style="max-width:600px;margin:0 auto;padding:20px">
        <h1 style="color:#3b82f6;margin:0 0 12px">Welcome to CoolBits! 🚀</h1>
        <p>Hi ${lead.name || "there"},</p>
        <p>Thanks for your interest. We'll review your submission and get back to you soon.</p>
        <div style="background:#f8fafc;padding:16px;border-radius:8px;margin:16px 0">
          <h3>Your Submission</h3>
          <p><strong>Email:</strong> ${lead.email}</p>
          ${lead.company ? `<p><strong>Company:</strong> ${lead.company}</p>` : ""}
          ${lead.phone ? `<p><strong>Phone:</strong> ${lead.phone}</p>` : ""}
          ${lead.message ? `<p><strong>Message:</strong> ${lead.message}</p>` : ""}
        </div>
        <p>Best,<br/>The CoolBits Team</p>
      </div>
    </body></html>
  `;
}

function generateNotificationEmailHTML(lead: Lead): string {
  return `
    <!doctype html><html><head><meta charset="utf-8"><title>New Lead</title></head>
    <body style="font-family: Arial,sans-serif; line-height:1.6; color:#111">
      <div style="max-width:600px;margin:0 auto;padding:20px">
        <h1 style="color:#3b82f6;margin:0 0 12px">New Lead Submission 🎯</h1>
        <div style="background:#f8fafc;padding:16px;border-radius:8px;margin:16px 0">
          <p><strong>Name:</strong> ${lead.name || "Not provided"}</p>
          <p><strong>Email:</strong> ${lead.email}</p>
          <p><strong>Company:</strong> ${lead.company || "Not provided"}</p>
          <p><strong>Phone:</strong> ${lead.phone || "Not provided"}</p>
          <p><strong>Message:</strong> ${lead.message || "No message"}</p>
          <p><strong>Source:</strong> ${lead.source || "website"}</p>
          <p><strong>Submitted:</strong> ${new Date().toLocaleString()}</p>
        </div>
        <p>Please follow up asap.</p>
      </div>
    </body></html>
  `;
}
