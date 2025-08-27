import { NextRequest, NextResponse } from 'next/server'

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url)
  const ch = searchParams.get('channel') || 'google_ads'

  // exemplu static — înlocuiește cu detecția reală a conexiunilor
  if (ch === 'google_ads') {
    const possible = ['gtm', 'ga4', 'gmc', 'lookerstudio', 'optimize']
    const connected: string[] = [] // ex: ['gtm','ga4']
    const score = Math.round((connected.length / possible.length) * 100)
    return NextResponse.json({ channel: ch, connected, possible, score })
  }

  return NextResponse.json({ channel: ch, connected: [], possible: [], score: 0 })
}
