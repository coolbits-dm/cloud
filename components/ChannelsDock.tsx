'use client'

import React, { useMemo } from 'react'
import {
  ChartBarIcon,
  DevicePhoneMobileIcon,
  BeakerIcon,
  BriefcaseIcon,
  HashtagIcon,
  GlobeAltIcon,
  EnvelopeIcon,
  UserGroupIcon,
  CpuChipIcon,
} from '@heroicons/react/24/outline'
import { useFacts } from '@/lib/facts/store'
import {
  type ChannelKey,
  CHANNEL_LABELS,
  deriveActiveChannels,
  getChannelCompletion,
} from '@/lib/channels/score'

type Channel = {
  id: ChannelKey
  label: string
  icon: React.ComponentType<React.SVGProps<SVGSVGElement>>
  status: 'available' | 'coming_soon'
}

const CHANNELS: Channel[] = [
  { id: 'google_ads',    label: CHANNEL_LABELS.google_ads,    icon: ChartBarIcon,          status: 'available' },
  { id: 'meta_ads',      label: CHANNEL_LABELS.meta_ads,      icon: DevicePhoneMobileIcon, status: 'coming_soon' },
  { id: 'tiktok_ads',    label: CHANNEL_LABELS.tiktok_ads,    icon: BeakerIcon,            status: 'coming_soon' },
  { id: 'linkedin_ads',  label: CHANNEL_LABELS.linkedin_ads,  icon: BriefcaseIcon,         status: 'coming_soon' },
  { id: 'x_ads',         label: CHANNEL_LABELS.x_ads,         icon: HashtagIcon,           status: 'coming_soon' },
  { id: 'seo',           label: CHANNEL_LABELS.seo,           icon: GlobeAltIcon,          status: 'coming_soon' },
  { id: 'email',         label: CHANNEL_LABELS.email,         icon: EnvelopeIcon,          status: 'coming_soon' },
  { id: 'referral',      label: CHANNEL_LABELS.referral,      icon: UserGroupIcon,         status: 'coming_soon' },
  { id: 'ai_optimization', label: CHANNEL_LABELS.ai_optimization, icon: CpuChipIcon,       status: 'coming_soon' },
]

export default function ChannelsDock({
  onOpen,
  className = '',
}: {
  onOpen: (id: ChannelKey) => void
  className?: string
}) {
  const { facts } = useFacts()
  const activeSet = useMemo(() => deriveActiveChannels(facts), [facts])

  return (
    <div
      className={`grid gap-2
        [grid-template-columns:repeat(auto-fit,minmax(160px,1fr))]
        sm:[grid-template-columns:repeat(auto-fit,minmax(170px,1fr))]
        ${className}`}
    >
      {CHANNELS.map((ch) => {
        const Icon = ch.icon
        const isActive = activeSet.has(ch.id)
        const completion = getChannelCompletion(facts, ch.id)

        const base =
          'w-full min-w-0 min-h-[48px] inline-flex flex-col items-stretch rounded-xl border shadow-sm transition focus:outline-none'
        const state = isActive
          ? 'bg-blue-600 text-white border-blue-600 hover:bg-blue-700'
          : 'bg-white text-gray-900 hover:shadow-md'

        return (
          <button
            key={ch.id}
            onClick={() => onOpen(ch.id)}
            title={isActive ? `${ch.label} (active)` : ch.label}
            className={`${base} ${state}`}
          >
            <div className="flex items-center gap-2 px-3 pt-2 pb-1 text-[11.5px] sm:text-xs md:text-sm leading-tight">
              <Icon className="h-4 w-4 shrink-0" />
              <span className="flex-1 whitespace-normal break-words">{ch.label}</span>
              {ch.status === 'coming_soon' && (
                <span className={`ml-1 inline-flex items-center rounded-full border px-1.5 py-0.5 text-[10px] ${
                  isActive ? 'border-white/40 text-white/90' : 'bg-gray-50 text-gray-600'
                }`}>
                  soon
                </span>
              )}
            </div>
            {/* progress bar only (no % text) */}
            <div className="px-3 pb-2">
              <div className={`h-1 w-full overflow-hidden rounded-full ${isActive ? 'bg-white/30' : 'bg-gray-200'}`}>
                <div
                  className={`h-1 rounded-full ${isActive ? 'bg-white' : 'bg-blue-600'}`}
                  style={{ width: `${Math.min(100, completion)}%` }}
                />
              </div>
            </div>
          </button>
        )
      })}
    </div>
  )
}
