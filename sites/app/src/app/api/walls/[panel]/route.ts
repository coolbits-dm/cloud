// src/app/api/walls/[panel]/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { readJson, writeJson } from '@/lib/fsjson'

export const runtime = 'nodejs'
export const dynamic = 'force-dynamic'

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ panel: string }> }
) {
  try {
    const { panel } = await params
    const data = readJson<any>(`walls/${panel}.json`)
    return NextResponse.json(data)
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to load wall data' },
      { status: 500 }
    )
  }
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ panel: string }> }
) {
  try {
    const { panel } = await params
    const { text, author } = await request.json()
    
    const data = readJson<any>(`walls/${panel}.json`)
    
    const newPost = {
      id: `post_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      author,
      ts: new Date().toISOString(),
      text,
      attachments: [],
      mentions: (text.match(/@\w+/g) || []),
      nha_invocations: (text.match(/@nha:\w+/g) || []).map((mention: string) => ({
        agent_id: mention.replace('@nha:', ''),
        role: mention.replace('@nha:', ''),
        status: 'queued' as const
      })),
      comments: []
    }
    
    data.posts.unshift(newPost)
    writeJson(`walls/${panel}.json`, data)
    
    return NextResponse.json({ success: true, post: newPost })
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to add post' },
      { status: 500 }
    )
  }
}
