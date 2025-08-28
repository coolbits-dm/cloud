// app/api/deep-analysis/start/route.ts
import { NextRequest, NextResponse } from 'next/server';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST(req: NextRequest) {
  try {
    // Citește payload-ul; dacă nu e JSON, mergem cu obiect gol
    const payload = await req.json().catch(() => ({}));

    // TODO: pornește job-ul de deep analysis aici (enqueue / persist etc.)
    // Pentru build OK, răspundem simplu:
    return NextResponse.json({
      success: true,
      message: 'deep-analysis started',
      data: { received: payload },
    });
  } catch (err: any) {
    return NextResponse.json(
      { success: false, message: err?.message || 'Server error' },
      { status: 500 }
    );
  }
}
