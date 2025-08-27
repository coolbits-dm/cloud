// lib/store/useChannelModal.ts
'use client'

import { create } from 'zustand'

export type ChannelKey =
  | 'google_ads' | 'meta_ads' | 'tiktok_ads' | 'linkedin_ads' | 'x_ads'
  | 'seo' | 'email' | 'referral' | 'ai_optimization'
  | 'ga4' | 'gtm' | 'gsc' | 'meta_pixel' | 'zapier' | 'semrush' | 'plaud' | 'sheets'

type ChannelModalState = {
  current: ChannelKey | null
  isOpen: boolean
  open: (id: ChannelKey) => void
  close: () => void
}

export const useChannelModal = create<ChannelModalState>((set) => ({
  current: null,
  isOpen: false,
  open: (id) => set({ current: id, isOpen: true }),
  close: () => set({ isOpen: false }),
}))
