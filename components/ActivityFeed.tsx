'use client'

import React from 'react'
import { useActivity } from '@/lib/cb/activity'
import {
  BoltIcon,
  ClockIcon,
  LinkIcon,
  AdjustmentsHorizontalIcon,
} from '@heroicons/react/24/outline'

function iconFor(type: string) {
  switch (type) {
    case 'briefing': return AdjustmentsHorizontalIcon
    case 'deep_analysis': return BoltIcon
    case 'ecosystem': return LinkIcon
    default: return ClockIcon
  }
}

export default function ActivityFeed() {
  const items = useActivity()

  if (!items.length) {
    return <div className="text-sm text-gray-400">No updates yet.</div>
  }

  return (
    <div className="space-y-2">
      {items.slice(0, 10).map((it) => {
        const Icon = iconFor(it.type)
        const when = new Date(it.ts).toLocaleTimeString()
        return (
          <div key={it.id} className="flex items-start gap-2 rounded-lg border bg-white p-2 text-xs">
            <Icon className="h-4 w-4 text-gray-500 mt-0.5" />
            <div className="flex-1">
              <div className="font-medium text-gray-800">{it.title}</div>
              {it.meta ? (
                <pre className="mt-1 max-h-28 overflow-auto rounded bg-gray-50 p-2 text-[10px] text-gray-600">
                  {JSON.stringify(it.meta, null, 2)}
                </pre>
              ) : null}
              <div className="mt-1 text-[10px] text-gray-500">{when}</div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
