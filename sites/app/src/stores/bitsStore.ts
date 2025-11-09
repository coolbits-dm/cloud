// src/stores/bitsStore.ts
import { create } from 'zustand'

export interface Bit {
  id: string
  name: string
  kind: string
  config: Record<string, any>
  inputs: string[]
  outputs: string[]
  scope: 'panel' | 'global'
}

export interface Flow {
  id: string
  name: string
  steps: Array<{
    bit_id: string
    order: number
  }>
}

export interface BitsData {
  bits: Bit[]
  flows: Flow[]
}

interface BitsStore {
  bitsData: BitsData | null
  loading: boolean
  error: string | null
  
  // Actions
  loadBits: () => Promise<void>
  addBit: (bit: Omit<Bit, 'id'>) => Promise<void>
  addFlow: (flow: Omit<Flow, 'id'>) => Promise<void>
  dryRunFlow: (flowId: string) => Promise<void>
}

export const useBitsStore = create<BitsStore>((set, get) => ({
  bitsData: null,
  loading: false,
  error: null,

  loadBits: async () => {
    set({ loading: true, error: null })
    try {
      const response = await fetch('/api/bits')
      if (!response.ok) throw new Error('Failed to load bits')
      const bitsData = await response.json()
      
      set({ bitsData, loading: false })
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Unknown error', loading: false })
    }
  },

  addBit: async (bit: Omit<Bit, 'id'>) => {
    set({ loading: true, error: null })
    try {
      const response = await fetch('/api/bits', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(bit)
      })
      if (!response.ok) throw new Error('Failed to add bit')
      
      // Reload bits after adding
      await get().loadBits()
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Unknown error', loading: false })
    }
  },

  addFlow: async (flow: Omit<Flow, 'id'>) => {
    set({ loading: true, error: null })
    try {
      const response = await fetch('/api/bits/flows', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(flow)
      })
      if (!response.ok) throw new Error('Failed to add flow')
      
      // Reload bits after adding flow
      await get().loadBits()
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Unknown error', loading: false })
    }
  },

  dryRunFlow: async (flowId: string) => {
    set({ loading: true, error: null })
    try {
      const response = await fetch(`/api/bits/flows/${flowId}/dry-run`, {
        method: 'POST'
      })
      if (!response.ok) throw new Error('Failed to dry run flow')
      
      // Could reload bits to show updated status
      await get().loadBits()
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Unknown error', loading: false })
    }
  }
}))
