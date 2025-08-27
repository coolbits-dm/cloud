// components/StatusBubbles.tsx
'use client'

import React from 'react'
import { CheckCircleIcon, ExclamationTriangleIcon, BoltIcon, LinkIcon, ChartBarIcon } from '@heroicons/react/24/outline'

type Bubble = {
  label: string
  tone: 'ok' | 'warn' | 'info'
  icon: React.ComponentType<React.SVGProps<SVGSVGElement>>
  hint?: string
}

export default function StatusBubbles({
  completeness,
  trackingLabel,          // e.g., 'None' | 'Partial' | 'Full' | 'Enhanced'
  connections,            // number of connected accounts/tools (e.g., Google Ads linked)
  aiReady,                // e.g., { andy: true, kim: true }
}: {
  completeness: number
  trackingLabel?: string
  connections?: number
  aiReady?: { andy?: boolean; kim?: boolean }
}) {
  const bubbles: Bubble[] = [
    {
      label: `Profile ${Math.min(100, completeness)}%`,
      tone: completeness >= 70 ? 'ok' : completeness >= 30 ? 'warn' : 'info',
      icon: ChartBarIcon,
      hint: 'Profile completeness based on company/channels/contact',
    },
    {
      label: trackingLabel ? `Tracking: ${trackingLabel}` : 'Tracking: n/a',
      tone: trackingLabel?.toLowerCase().includes('full') ? 'ok'
          : trackingLabel?.toLowerCase().includes('partial') ? 'warn'
          : 'info',
      icon: CheckCircleIcon,
      hint: 'Implementation level (GA4/GTM/Pixel etc.)',
    },
    {
      label: `Connections: ${connections ?? 0}`,
      tone: (connections ?? 0) > 0 ? 'ok' : 'info',
      icon: LinkIcon,
      hint: 'OAuth/API linked accounts',
    },
    {
      label: `AI: Andy${aiReady?.kim ? ' + Kim' : ''}`,
      tone: aiReady?.kim ? 'ok' : 'info',
      icon: BoltIcon,
      hint: 'Assistants available for analysis',
    },
  ]

  return (
    <div className="flex flex-wrap gap-2">
      {bubbles.map((b, i) => {
        const cls =
          b.tone === 'ok'
            ? 'bg-green-50 text-green-700 border-green-200'
            : b.tone === 'warn'
            ? 'bg-amber-50 text-amber-800 border-amber-200'
            : 'bg-gray-50 text-gray-700 border-gray-200'
        const Icon = b.icon
        return (
          <div
            key={i}
            title={b.hint}
            className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs ${cls}`}
          >
            <Icon className="h-4 w-4" />
            <span>{b.label}</span>
          </div>
        )
      })}
    </div>
  )
}
