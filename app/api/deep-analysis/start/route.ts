// app/api/deep-analysis/start/route.ts
import { NextRequest, NextResponse } from 'next/server'

export async function POST(req: NextRequest) {
  const body = await req.json().catch(() => ({}))
  // body: { engine: 'kim', includeWeb: boolean, channels: string[] }
  const jobId = crypto.randomUUID()

  // TODO: enqueue background job (queue/worker) cu `body` + user/tenant context
  // ex: await jobs.enqueue('deep-analysis', { jobId, ...body, userId })

  return NextResponse.json({ ok: true, jobId })
}

// app/api/analysis/deep/start/route.ts
import { NextRequest, NextResponse } from 'next/server'

export async function POST(req: NextRequest) {
  const url = new URL('/api/deep-analysis/start', req.nextUrl)
  const body = await req.text()
  const r = await fetch(url, { method: 'POST', headers: { 'content-type': 'application/json' }, body })
  const json = await r.json()
  return NextResponse.json(json, { status: r.status })
}
