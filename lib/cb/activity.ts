// lib/cb/activity.ts
'use client'
import { create } from 'zustand'

export type Activity = {
  id: string
  ts: number
  title: string
  subtitle?: string
  kind?: 'info'|'success'|'warning'|'error'
  sig?: string // pentru dedup (ex: jobId, channel+ts rounded)
}

type ActivityState = {
  items: Activity[]
  add: (a: Omit<Activity, 'id' | 'ts'>) => void
  addOnce: (sig: string, a: Omit<Activity, 'id' | 'ts' | 'sig'>) => void
  clear: () => void
}

export const useActivity = create<ActivityState>((set, get) => ({
  items: [],
  add: (a) => set(s => ({
    items: [{ id: crypto.randomUUID(), ts: Date.now(), ...a }, ...s.items].slice(0, 50)
  })),
  addOnce: (sig, a) => {
    const exists = get().items.some(it => it.sig === sig)
    if (exists) return
    set(s => ({
      items: [{ id: crypto.randomUUID(), ts: Date.now(), sig, ...a }, ...s.items].slice(0, 50)
    }))
  },
  clear: () => set({ items: [] }),
}))
