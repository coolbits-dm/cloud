'use client'

import { useCallback, useState } from 'react'

type Props = {
  onSendMessage?: (text: string) => void
  isLoading?: boolean
  placeholder?: string
  className?: string
}

export default function MessageInput({
  onSendMessage,
  isLoading = false,
  placeholder = 'Message…',
  className = '',
}: Props) {
  const [val, setVal] = useState('')

  const send = useCallback(() => {
    const s = val.trim()
    if (!s || isLoading) return
    // protejat: dacă nu există handler, nu aruncăm eroare
    onSendMessage?.(s)
    setVal('')
  }, [val, isLoading, onSendMessage])

  return (
    <div className={`flex items-end gap-2 ${className}`}>
      <textarea
        className="flex-1 resize-none rounded-lg border bg-white p-3 text-sm leading-5 outline-none focus:ring-2 focus:ring-primary-300"
        rows={2}
        placeholder={placeholder}
        value={val}
        onChange={(e) => setVal(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            send()
          }
        }}
      />
      <button
        onClick={send}
        disabled={isLoading || !val.trim()}
        className="inline-flex h-10 items-center justify-center rounded-lg bg-primary-600 px-3 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-50"
        title="Send"
      >
        ▷
      </button>
    </div>
  )
}
