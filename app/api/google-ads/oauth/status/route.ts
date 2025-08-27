import { NextResponse } from 'next/server'

export async function GET() {
  // TODO: replace with DB check
  const linked = false
  return NextResponse.json({ linked, accounts: [] })
}
