import { useState } from 'react'
import { Button } from "./ui/button"
import { Input } from "./ui/input"

export default function AgentInterface() {
  const [query, setQuery] = useState('')
  const [response, setResponse] = useState<any>(null)
  const [mode, setMode] = useState<'mock' | 'byok'>('mock')

  const execute = async () => {
    const headers: any = { 'Content-Type': 'application/json' }
    if (mode === 'byok') {
      const key = prompt("Camarad BYOK Key (andrei@cblm.ai):")
      if (key) headers['X-API-Key'] = key
    }

    const res = await fetch('/api/agents/query', {
      method: 'POST',
      headers,
      body: JSON.stringify({ query, requires_realtime: mode === 'mock' })
    })
    setResponse(await res.json())
  }

  return (
    <div className="p-8 bg-black text-cyan-400 border border-cyan-600 rounded-lg">
      <h2 className="text-3xl mb-6">Camarad Executor – Super Admin</h2>
      <div className="flex gap-4 mb-6">
        <Button onClick={() => setMode('mock')} variant={mode === 'mock' ? "default" : "outline"} className="text-xl">
          CAMARAD MOCK (0$)
        </Button>
        <Button onClick={() => setMode('byok')} variant={mode === 'byok' ? "default" : "outline"} className="text-xl">
          CAMARAD BYOK (real)
        </Button>
      </div>
      <Input value={query} onChange={(e: any) => setQuery(e.target.value)} placeholder="Command the Agent..." className="mb-6 text-xl" />
      <Button onClick={execute} className="bg-cyan-600 hover:bg-cyan-500 text-black font-bold text-2xl px-12 py-8">
        EXECUTE AS CAMARAD
      </Button>
      {response && (
        <pre className="mt-8 p-6 bg-gray-900 rounded overflow-x-auto text-lg">
          {JSON.stringify(response, null, 2)}
        </pre>
      )}
    </div>
  )
}