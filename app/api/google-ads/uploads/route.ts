import { NextRequest, NextResponse } from 'next/server'
export const runtime = 'nodejs'

export async function POST(req: NextRequest) {
  const form = await req.formData()
  const files = form.getAll('files') as File[]
  if (!files?.length) return NextResponse.json({ ok: false, error: 'no_files' }, { status: 400 })
  const meta = files.map((f) => ({ name: f.name, type: f.type, size: f.size }))
  // TODO: persist & enqueue parsers
  return NextResponse.json({ ok: true, received: meta })
}
