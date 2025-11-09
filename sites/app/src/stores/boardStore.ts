// src/stores/boardStore.ts
import { create } from 'zustand'

export interface BoardMember {
  id: string
  display: string
  role: string
  agent_type: 'human' | 'non-human'
}

export interface Meeting {
  id: string
  ts: string
  notes: string
  attendees: string[]
}

export interface BoardData {
  panel: string
  board_name: string
  members: BoardMember[]
  charter: string
  meetings: Meeting[]
}

interface BoardStore {
  boards: Record<string, BoardData>
  loading: boolean
  error: string | null
  
  // Actions
  loadBoard: (panel: string) => Promise<void>
  startMeeting: (panel: string, notes: string) => Promise<void>
  addMember: (panel: string, member: Omit<BoardMember, 'id'>) => Promise<void>
}

export const useBoardStore = create<BoardStore>((set, get) => ({
  boards: {},
  loading: false,
  error: null,

  loadBoard: async (panel: string) => {
    set({ loading: true, error: null })
    try {
      const response = await fetch(`/api/boards/${panel}`)
      if (!response.ok) throw new Error('Failed to load board')
      const boardData = await response.json()
      
      set(state => ({
        boards: { ...state.boards, [panel]: boardData },
        loading: false
      }))
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Unknown error', loading: false })
    }
  },

  startMeeting: async (panel: string, notes: string) => {
    set({ loading: true, error: null })
    try {
      const response = await fetch(`/api/boards/${panel}/meetings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ notes })
      })
      if (!response.ok) throw new Error('Failed to start meeting')
      
      // Reload board after starting meeting
      await get().loadBoard(panel)
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Unknown error', loading: false })
    }
  },

  addMember: async (panel: string, member: Omit<BoardMember, 'id'>) => {
    set({ loading: true, error: null })
    try {
      const response = await fetch(`/api/boards/${panel}/members`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(member)
      })
      if (!response.ok) throw new Error('Failed to add member')
      
      // Reload board after adding member
      await get().loadBoard(panel)
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Unknown error', loading: false })
    }
  }
}))
