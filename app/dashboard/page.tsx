import ChatWindow from '@/components/ChatWindow'

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            AI Chat Dashboard
          </h1>
          <p className="text-gray-600">
            Chat with <strong>Andy</strong> for intelligent assistance tailored to your business.
          </p>
        </div>
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          <ChatWindow className="h-[600px]" />
        </div>
      </div>
    </div>
  )
}
