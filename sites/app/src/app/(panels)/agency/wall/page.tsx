import { WallView } from '@/components/WallView'
import { AskRAG } from '@/components/AskRAG'

export default function AgencyWallPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto p-4">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <WallView panel="agency" />
          </div>
          <div className="lg:col-span-1">
            <AskRAG panel="agency" />
          </div>
        </div>
      </div>
    </div>
  )
}
