'use client'
import { useState } from 'react'
import type { QuickReplyGroup, QuickReplyOption } from '@/lib/chat/quickTypes'

export default function QuickReplies({
  groups,
  onConfirm
}: {
  groups: QuickReplyGroup[]
  onConfirm: (group: QuickReplyGroup, picked: QuickReplyOption[], customValue?: string) => void
}) {
  if (!groups || groups.length === 0) return null
  return (
    <div className="mt-3 space-y-3">
      {groups.map(g => <Group key={g.id} group={g} onConfirm={onConfirm} />)}
    </div>
  )
}

function Group({
  group,
  onConfirm
}: {
  group: QuickReplyGroup
  onConfirm: (group: QuickReplyGroup, picked: QuickReplyOption[], customValue?: string) => void
}) {
  const [picked, setPicked] = useState<QuickReplyOption[]>([])
  const [custom, setCustom] = useState('')

  const toggle = (opt: QuickReplyOption) => {
    if (!group.multi) {
      onConfirm(group, [opt])
      return
    }
    setPicked(p => p.find(x => x.id === opt.id) ? p.filter(x => x.id !== opt.id) : [...p, opt])
  }

  const confirm = () => onConfirm(group, picked, custom || undefined)

  return (
    <div className="rounded-lg border p-3 bg-gray-50">
      <div className="text-xs text-gray-600 mb-2">{group.title}</div>
      <div className="flex flex-wrap gap-2">
        {group.options.map(opt => (
          <button
            key={opt.id}
            onClick={() => toggle(opt)}
            className={`px-2 py-1 rounded-full text-xs border transition
              ${picked.find(x => x.id === opt.id) ? 'bg-primary-600 text-white border-primary-600' : 'bg-white hover:bg-gray-100'}`}
          >
            {opt.label}
          </button>
        ))}
      </div>

      {group.allowCustom && (
        <div className="mt-2 flex items-center gap-2">
          <input
            value={custom}
            onChange={e => setCustom(e.target.value)}
            placeholder={group.customPlaceholder || 'Custom…'}
            className="flex-1 px-2 py-1 text-xs border rounded"
          />
          {group.multi && (
            <button onClick={confirm} className="px-2 py-1 text-xs rounded bg-primary-600 text-white">
              Confirm
            </button>
          )}
        </div>
      )}

      {!group.multi && group.allowCustom && (
        <div className="mt-1">
          <button onClick={confirm} className="text-xs text-primary-600 hover:underline">
            Send
          </button>
        </div>
      )}
    </div>
  )
}
