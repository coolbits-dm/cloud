'use client'
import { useEffect, useState } from 'react'
import { on } from '@/lib/bus'
import GoogleAdsWorkspace from './channels/google/GoogleAdsWorkspace'

type ModalState = null | { id: string }

export default function ChannelModalHost() {
  const [open, setOpen] = useState<ModalState>(null)

  useEffect(() => {
    const offOpen = on('channel:open', (d) => setOpen({ id: d?.id }))
    const offClose = on('channel:close', () => setOpen(null))
    return () => { offOpen(); offClose() }
  }, [])

  if (!open) return null

  const close = () => setOpen(null)

  return (
    <div className="fixed inset-0 z-[999]">
      <div className="absolute inset-0 bg-black/40" onClick={close} />
      <div className="absolute right-0 top-0 h-full w-full md:w-[920px] bg-white shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b px-4 py-3">
          <div className="font-semibold">Workspace: {open.id === 'google' ? 'Google Ads' : open.id}</div>
          <button onClick={close} className="rounded border px-2 text-sm">Close</button>
        </div>

        {/* Body */}
        <div className="h-[calc(100%-48px)] overflow-auto">
          {open.id === 'google' && <GoogleAdsWorkspace />}
          {/* Future: other channels here */}
        </div>
      </div>
    </div>
  )
}
