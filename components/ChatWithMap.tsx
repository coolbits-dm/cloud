'use client'

import BusinessMapPanel from '@/components/BusinessMapPanel'
import ChatWindow from '@/components/ChatWindow'

export default function ChatWithMap() {
  return (
    <div className="grid h-full grid-cols-1 md:grid-cols-[minmax(520px,1fr)_minmax(380px,440px)] gap-6">
      {/* Chat (left) */}
      <div className="h-full overflow-hidden">
        <ChatWindow className="h-full" />
      </div>

      {/* Business Map (right) */}
      <div className="h-full overflow-hidden">
        <BusinessMapPanel />
      </div>
    </div>
  )
}
