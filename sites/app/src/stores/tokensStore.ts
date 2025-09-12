// src/stores/tokensStore.ts
import { create } from 'zustand'

export interface TokenEntry {
  ts: string
  ref: string
  delta: number
  reason: string
  meta?: Record<string, any>
}

export interface TokensData {
  unit: 'cbT'
  balance: number
  entries: TokenEntry[]
}

interface TokensStore {
  tokensData: TokensData | null
  loading: boolean
  error: string | null
  
  // Actions
  loadTokens: () => Promise<void>
  debitTokens: (amount: number, reason: string, ref?: string) => Promise<void>
  creditTokens: (amount: number, reason: string, ref?: string) => Promise<void>
}

export const useTokensStore = create<TokensStore>((set, get) => ({
  tokensData: null,
  loading: false,
  error: null,

  loadTokens: async () => {
    set({ loading: true, error: null })
    try {
      const response = await fetch('/api/tokens')
      if (!response.ok) throw new Error('Failed to load tokens')
      const tokensData = await response.json()
      
      set({ tokensData, loading: false })
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Unknown error', loading: false })
    }
  },

  debitTokens: async (amount: number, reason: string, ref?: string) => {
    set({ loading: true, error: null })
    try {
      const response = await fetch('/api/tokens/debit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ amount, reason, ref })
      })
      if (!response.ok) throw new Error('Failed to debit tokens')
      
      // Reload tokens after debit
      await get().loadTokens()
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Unknown error', loading: false })
    }
  },

  creditTokens: async (amount: number, reason: string, ref?: string) => {
    set({ loading: true, error: null })
    try {
      const response = await fetch('/api/tokens/credit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ amount, reason, ref })
      })
      if (!response.ok) throw new Error('Failed to credit tokens')
      
      // Reload tokens after credit
      await get().loadTokens()
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Unknown error', loading: false })
    }
  }
}))
