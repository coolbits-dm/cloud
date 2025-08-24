import ChatWindow from '@/components/ChatWindow'

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            AI Chat Dashboard
          </h1>
          <p className="text-gray-600">
            Chat with Jean (GPT-4) and Gelu (Grok) to get intelligent assistance for your business needs.
          </p>
        </div>

        {/* Chat Interface */}
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          <ChatWindow className="h-[600px]" />
        </div>

        {/* Additional Features */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Quick Actions */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
            <div className="space-y-3">
              <button className="w-full text-left p-3 rounded-lg hover:bg-gray-50 transition-colors">
                <div className="font-medium text-gray-900">Generate Taglines</div>
                <div className="text-sm text-gray-500">Create compelling brand messaging</div>
              </button>
              <button className="w-full text-left p-3 rounded-lg hover:bg-gray-50 transition-colors">
                <div className="font-medium text-gray-900">Write Content</div>
                <div className="text-sm text-gray-500">Blog posts, emails, and more</div>
              </button>
              <button className="w-full text-left p-3 rounded-lg hover:bg-gray-50 transition-colors">
                <div className="font-medium text-gray-900">Analyze Data</div>
                <div className="text-sm text-gray-500">Get insights from your data</div>
              </button>
            </div>
          </div>

          {/* Recent Conversations */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Conversations</h3>
            <div className="space-y-3">
              <div className="p-3 rounded-lg bg-gray-50">
                <div className="font-medium text-gray-900">Business Strategy Discussion</div>
                <div className="text-sm text-gray-500">2 hours ago • Jean</div>
              </div>
              <div className="p-3 rounded-lg bg-gray-50">
                <div className="font-medium text-gray-900">Content Creation Help</div>
                <div className="text-sm text-gray-500">1 day ago • Gelu</div>
              </div>
              <div className="p-3 rounded-lg bg-gray-50">
                <div className="font-medium text-gray-900">Technical Support</div>
                <div className="text-sm text-gray-500">3 days ago • Jean</div>
              </div>
            </div>
          </div>

          {/* Usage Stats */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Usage This Month</h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Jean (GPT-4)</span>
                  <span className="font-medium">75%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-primary-600 h-2 rounded-full" style={{ width: '75%' }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Gelu (Grok)</span>
                  <span className="font-medium">45%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-purple-600 h-2 rounded-full" style={{ width: '45%' }}></div>
                </div>
              </div>
              <div className="pt-2 border-t border-gray-200">
                <div className="text-sm text-gray-600">
                  Total conversations: <span className="font-medium text-gray-900">127</span>
                </div>
                <div className="text-sm text-gray-600">
                  Tokens used: <span className="font-medium text-gray-900">45.2K</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
