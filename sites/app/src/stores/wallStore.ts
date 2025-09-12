// src/stores/wallStore.ts
import { create } from 'zustand'

export interface Post {
  id: string
  author: string
  ts: string
  text: string
  attachments: string[]
  mentions: string[]
  nha_invocations: Array<{
    agent_id: string
    role: string
    status: 'queued' | 'running' | 'done' | 'error'
    result_ref?: string
  }>
  comments: Array<{
    author: string
    ts: string
    text: string
  }>
}

export interface WallData {
  panel: string
  posts: Post[]
}

interface WallStore {
  walls: Record<string, WallData>
  loading: boolean
  error: string | null
  
  // Actions
  loadWall: (panel: string) => Promise<void>
  addPost: (panel: string, text: string, author: string) => Promise<void>
  addComment: (panel: string, postId: string, text: string, author: string) => Promise<void>
}

export const useWallStore = create<WallStore>((set, get) => ({
  walls: {},
  loading: false,
  error: null,

  loadWall: async (panel: string) => {
    set({ loading: true, error: null })
    try {
      const response = await fetch(`/api/walls/${panel}`)
      if (!response.ok) throw new Error('Failed to load wall')
      const wallData = await response.json()
      
      set(state => ({
        walls: { ...state.walls, [panel]: wallData },
        loading: false
      }))
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Unknown error', loading: false })
    }
  },

  addPost: async (panel: string, text: string, author: string) => {
    set({ loading: true, error: null })
    try {
      const response = await fetch(`/api/walls/${panel}/posts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, author })
      })
      if (!response.ok) throw new Error('Failed to add post')
      
      // Reload wall after adding post
      await get().loadWall(panel)
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Unknown error', loading: false })
    }
  },

  addComment: async (panel: string, postId: string, text: string, author: string) => {
    set({ loading: true, error: null })
    try {
      const response = await fetch(`/api/walls/${panel}/posts/${postId}/comments`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, author })
      })
      if (!response.ok) throw new Error('Failed to add comment')
      
      // Reload wall after adding comment
      await get().loadWall(panel)
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Unknown error', loading: false })
    }
  }
}))
