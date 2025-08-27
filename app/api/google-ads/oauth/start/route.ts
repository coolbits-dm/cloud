import { NextResponse } from 'next/server'

export async function GET() {
  const clientId = process.env.GOOGLE_CLIENT_ID!
  const base = process.env.NEXT_PUBLIC_BASE_URL!
  const redirectUri = base + '/api/google-ads/oauth/callback'
  const scope = encodeURIComponent('https://www.googleapis.com/auth/adwords openid email profile')
  const state = crypto.randomUUID()
  const url =
    'https://accounts.google.com/o/oauth2/v2/auth' +
    `?client_id=${clientId}` +
    `&redirect_uri=${encodeURIComponent(redirectUri)}` +
    `&response_type=code` +
    `&access_type=offline` +
    `&prompt=consent` +
    `&scope=${scope}` +
    `&state=${state}`
  // TODO: persist `state` in session to validate later
  return NextResponse.redirect(url)
}
