// src/components/AskRAG.tsx
'use client'

import { useState } from 'react'
import { Search, Bot, FileText } from 'lucide-react'

interface AskRAGProps {
  panel: string
}

interface RAGResult {
  chunk: string
  source: string
  score: number
}

export function AskRAG({ panel }: AskRAGProps) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<RAGResult[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    setError(null)
    setResults([])

    try {
      const r = await fetch("/api/gw/rag/query", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ panel, query, topk: 3 })
      });
      const data = await r.json();
      setResults(data.results ?? []);
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white border rounded-lg p-4">
      <div className="flex items-center gap-2 mb-4">
        <Bot className="w-5 h-5 text-blue-500" />
        <h3 className="font-medium">Ask RAG ({panel})</h3>
      </div>

      <form onSubmit={handleSearch} className="mb-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask about this panel..."
            className="flex-1 p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="flex items-center gap-2 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Search className="w-4 h-4" />
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </form>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-600">
          Error: {error}
        </div>
      )}

      {results.length > 0 && (
        <div className="space-y-3">
          <div className="text-sm text-gray-600">
            Found {results.length} relevant chunks:
          </div>
          {results.map((result, index) => (
            <div key={index} className="p-3 bg-gray-50 border rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <FileText className="w-4 h-4 text-gray-500" />
                <span className="text-sm text-gray-600">
                  Score: {(result.score * 100).toFixed(1)}%
                </span>
                <span className="text-sm text-gray-500">
                  Source: {result.source}
                </span>
              </div>
              <p className="text-sm">{result.chunk}</p>
            </div>
          ))}
        </div>
      )}

      {results.length === 0 && !loading && !error && query && (
        <div className="text-center text-gray-500 py-4">
          No results found. Try a different query.
        </div>
      )}
    </div>
  )
}
