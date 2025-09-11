// Health endpoint based on ogpt04 requirements
import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({ 
    ok: true, 
    svc: 'frontend', 
    ts: new Date().toISOString() 
  });
}
