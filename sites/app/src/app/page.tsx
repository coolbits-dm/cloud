// src/app/page.tsx
import Link from 'next/link'
import { MessageSquare, Users, Settings, Coins, Bot } from 'lucide-react'

export default function HomePage() {
  const panels = [
    { name: 'user', label: 'User', color: 'blue' },
    { name: 'business', label: 'Business', color: 'green' },
    { name: 'agency', label: 'Agency', color: 'purple' },
    { name: 'dev', label: 'Dev', color: 'orange' },
  ]

  const getColorClasses = (color: string) => {
    const colors = {
      blue: 'bg-blue-50 border-blue-200 text-blue-700 hover:bg-blue-100',
      green: 'bg-green-50 border-green-200 text-green-700 hover:bg-green-100',
      purple: 'bg-purple-50 border-purple-200 text-purple-700 hover:bg-purple-100',
      orange: 'bg-orange-50 border-orange-200 text-orange-700 hover:bg-orange-100',
    }
    return colors[color as keyof typeof colors] || colors.blue
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto p-8">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Welcome to CoolBits.ai M18.2
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Walls, Boards, Bits Orchestrator & cbT Economy
          </p>
          <div className="flex items-center justify-center gap-4 text-sm text-gray-500">
            <div className="flex items-center gap-1">
              <Coins className="w-4 h-4" />
              <span>cbT Economy</span>
            </div>
            <div className="flex items-center gap-1">
              <Bot className="w-4 h-4" />
              <span>RAG Local v0</span>
            </div>
            <div className="flex items-center gap-1">
              <Settings className="w-4 h-4" />
              <span>Bits Orchestrator</span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {panels.map((panel) => (
            <div key={panel.name} className="space-y-4">
              <h2 className="text-lg font-semibold text-gray-900 capitalize">
                {panel.label} Panel
              </h2>
              <div className="space-y-2">
                <Link
                  href={`/${panel.name}/wall`}
                  className={`flex items-center gap-3 p-4 border rounded-lg transition-colors ${getColorClasses(panel.color)}`}
                >
                  <MessageSquare className="w-5 h-5" />
                  <span className="font-medium">{panel.label} Wall</span>
                </Link>
                <Link
                  href={`/${panel.name}/board`}
                  className={`flex items-center gap-3 p-4 border rounded-lg transition-colors ${getColorClasses(panel.color)}`}
                >
                  <Users className="w-5 h-5" />
                  <span className="font-medium">{panel.label} Board</span>
                </Link>
              </div>
            </div>
          ))}
        </div>

        <div className="bg-white border rounded-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Bits Orchestrator
          </h2>
          <p className="text-gray-600 mb-4">
            Create and manage automation flows with triggers, actions, and filters.
          </p>
          <Link
            href="/bits"
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Settings className="w-4 h-4" />
            Open Bits Orchestrator
          </Link>
        </div>

        <div className="mt-8 text-center text-sm text-gray-500">
          <p>M18.2 - Non-interactive UI with cbT Economy and RAG Local v0</p>
          <p className="mt-1">All actions are debited from your cbT balance</p>
        </div>
      </div>
    </div>
  )
}