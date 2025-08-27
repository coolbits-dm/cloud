import { NextRequest, NextResponse } from 'next/server'

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url)
  const code = searchParams.get('code')
  if (!code) return NextResponse.json({ error: 'missing_code' }, { status: 400 })

  const tokenRes = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      code,
      client_id: process.env.GOOGLE_CLIENT_ID!,
      client_secret: process.env.GOOGLE_CLIENT_SECRET!,
      redirect_uri: process.env.NEXT_PUBLIC_BASE_URL! + '/api/google-ads/oauth/callback',
      grant_type: 'authorization_code',
    }),
  })
  const tokenJson = await tokenRes.json()
  // TODO: verify id_token, fetch userinfo, save refresh_token to DB for this tenant/user

  return NextResponse.redirect(process.env.NEXT_PUBLIC_BASE_URL! + '/?linked=google-ads')
}
