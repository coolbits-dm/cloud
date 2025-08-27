'use client'
import React, { useEffect, useState } from 'react'
import { getBalance } from '@/lib/usage/credits'

export default function CreditsBadge() {
  const [bal, setBal] = useState(0)
  useEffect(() => {
    setBal(getBalance())
    const h = (e: any) => setBal(e?.detail?.balance ?? getBalance())
    window.addEventListener('cb:credits-updated', h as EventListener)
    return () => window.removeEventListener('cb:credits-updated', h as EventListener)
  }, [])
  return (
    <div className="text-xs rounded-full border px-2 py-1 bg-white">
      Credits: <strong>{bal}</strong>
    </div>
  )
}
