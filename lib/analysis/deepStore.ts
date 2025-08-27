// lib/analysis/deepStore.ts
'use client'
import { create } from 'zustand'

type DeepState = {
  isOpen: boolean
  open: () => void
  close: () => void
}

export const useDeepAnalysis = create<DeepState>((set) => ({
  isOpen: false,
  open: () => set({ isOpen: true }),
  close: () => set({ isOpen: false }),
}))
