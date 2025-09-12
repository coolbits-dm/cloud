// src/app/api/tokens/route.ts
import { NextResponse } from 'next/server'
import { readJson } from '@/lib/fsjson'

export const runtime = 'nodejs'
export const dynamic = 'force-dynamic'

export async function GET() {
  try {
    const data = readJson<any>('tokens/ledger.json')
    return NextResponse.json(data)
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to load tokens data' },
      { status: 500 }
    )
  }
}
