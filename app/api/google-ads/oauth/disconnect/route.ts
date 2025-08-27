import { NextResponse } from 'next/server'

export async function GET() {
  // TODO: revoke token & delete from DB
  return NextResponse.redirect(process.env.NEXT_PUBLIC_BASE_URL! + '/?unlinked=google-ads')
}
