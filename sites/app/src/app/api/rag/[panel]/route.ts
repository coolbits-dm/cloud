// src/app/api/rag/[panel]/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { readJson } from '@/lib/fsjson'

export const runtime = 'nodejs'
export const dynamic = 'force-dynamic'

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ panel: string }> }
) {
  try {
    const { panel } = await params
    const { query } = await request.json()
    
    const data = readJson<any>(`rag/store/${panel}.json`)
    
    // Simple text matching for M18.2 (fake RAG)
    const results = data.chunks
      .map((chunk: any) => ({
        chunk: chunk.text,
        source: chunk.source || 'unknown',
        score: Math.random() * 0.5 + 0.5 // Random score between 0.5-1.0
      }))
      .filter((result: any) => 
        result.chunk.toLowerCase().includes(query.toLowerCase())
      )
      .slice(0, 3) // Top 3 results
    
    return NextResponse.json({ results })
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to search RAG' },
      { status: 500 }
    )
  }
}
