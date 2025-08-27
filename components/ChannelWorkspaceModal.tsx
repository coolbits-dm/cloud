'use client'

import { useFacts } from '@/lib/facts/store'

export default function ChannelWorkspaceModal({
  channel,
  onClose,
}: {
  channel: string
  onClose: () => void
}) {
  const { facts } = useFacts()

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="w-full max-w-3xl rounded-xl border bg-white shadow-xl">
        <div className="flex items-center justify-between border-b px-4 py-3">
          <div className="text-sm font-semibold">{channel} — Workspace</div>
          <button
            onClick={onClose}
            className="rounded-md border px-2 py-1 text-xs hover:bg-gray-50"
          >
            Close
          </button>
        </div>

        <div className="max-h-[70vh] overflow-y-auto p-4">
          {/* Placeholder: aici vei itera pe frameworkul în nivele (Campaigns → Ad groups → Keywords → Ads → Assets) */}
          <p className="text-sm text-gray-700">
            Coming soon: full {channel} framework (campaigns, budgets, geo, audiences, assets, etc.).
          </p>

          <div className="mt-4 rounded-lg border bg-gray-50 p-3">
            <div className="text-xs text-gray-500">Snapshot from Business Map</div>
            <pre className="mt-2 overflow-auto rounded bg-white p-2 text-xs">
{JSON.stringify(facts?.[channel.toLowerCase().replace(/\s+/g,'')] ?? {}, null, 2)}
            </pre>
          </div>
        </div>

        <div className="flex items-center justify-end gap-2 border-t px-4 py-3">
          <button className="rounded bg-primary-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-primary-700">
            Save
          </button>
          <button className="rounded border px-3 py-1.5 text-sm hover:bg-gray-50" onClick={onClose}>
            Cancel
          </button>
        </div>
      </div>
    </div>
  )
}
