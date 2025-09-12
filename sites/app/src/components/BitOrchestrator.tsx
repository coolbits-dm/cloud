// src/components/BitOrchestrator.tsx
'use client'

import { useState, useEffect } from 'react'
import { useBitsStore } from '@/stores/bitsStore'
import { useTokensStore } from '@/stores/tokensStore'
import { getTariffCost } from '@/lib/cbtokens'
import { Settings, Plus, Play, Trash2, ArrowRight } from 'lucide-react'

export function BitOrchestrator() {
  const [showAddBitForm, setShowAddBitForm] = useState(false)
  const [showAddFlowForm, setShowAddFlowForm] = useState(false)
  const [newBit, setNewBit] = useState({
    name: '',
    kind: 'trigger',
    config: {},
    inputs: [],
    outputs: [],
    scope: 'global' as 'panel' | 'global'
  })
  const [newFlow, setNewFlow] = useState({
    name: '',
    steps: [] as Array<{ bit_id: string; order: number }>
  })
  
  const { bitsData, loading, error, loadBits, addBit, addFlow, dryRunFlow } = useBitsStore()
  const { debitTokens } = useTokensStore()

  useEffect(() => {
    loadBits()
  }, [loadBits])

  const handleAddBit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newBit.name.trim()) return

    try {
      await addBit(newBit)
      setNewBit({
        name: '',
        kind: 'trigger',
        config: {},
        inputs: [],
        outputs: [],
        scope: 'global'
      })
      setShowAddBitForm(false)
    } catch (error) {
      console.error('Failed to add bit:', error)
    }
  }

  const handleAddFlow = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newFlow.name.trim() || newFlow.steps.length === 0) return

    try {
      await addFlow(newFlow)
      setNewFlow({ name: '', steps: [] })
      setShowAddFlowForm(false)
    } catch (error) {
      console.error('Failed to add flow:', error)
    }
  }

  const handleDryRun = async (flowId: string) => {
    try {
      // Debit tokens for dry run
      await debitTokens(Math.abs(getTariffCost('BITS_DRY_RUN')), 'BITS_DRY_RUN', `dry_run_${flowId}`)
      
      // Run dry run
      await dryRunFlow(flowId)
    } catch (error) {
      console.error('Failed to dry run flow:', error)
    }
  }

  const addStepToFlow = (bitId: string) => {
    const order = newFlow.steps.length + 1
    setNewFlow({
      ...newFlow,
      steps: [...newFlow.steps, { bit_id: bitId, order }]
    })
  }

  const removeStepFromFlow = (index: number) => {
    setNewFlow({
      ...newFlow,
      steps: newFlow.steps.filter((_, i) => i !== index)
    })
  }

  if (loading) {
    return <div className="p-4 text-center">Loading bits...</div>
  }

  if (error) {
    return <div className="p-4 text-center text-red-600">Error: {error}</div>
  }

  if (!bitsData) {
    return <div className="p-4 text-center">No bits data</div>
  }

  return (
    <div className="max-w-6xl mx-auto p-4 space-y-6">
      <div className="flex items-center gap-2 mb-6">
        <Settings className="w-6 h-6" />
        <h1 className="text-2xl font-bold">Bits Orchestrator</h1>
      </div>

      {/* Add Bit Form */}
      {showAddBitForm && (
        <div className="bg-white border rounded-lg p-4">
          <h2 className="font-medium mb-4">Add New Bit</h2>
          <form onSubmit={handleAddBit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <input
                type="text"
                value={newBit.name}
                onChange={(e) => setNewBit({ ...newBit, name: e.target.value })}
                placeholder="Bit name"
                className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
              <select
                value={newBit.kind}
                onChange={(e) => setNewBit({ ...newBit, kind: e.target.value })}
                className="p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="trigger">Trigger</option>
                <option value="action">Action</option>
                <option value="filter">Filter</option>
                <option value="enrich">Enrich</option>
                <option value="route">Route</option>
              </select>
            </div>
            <div className="flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setShowAddBitForm(false)}
                className="px-4 py-2 text-gray-600 hover:text-gray-800"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                <Plus className="w-4 h-4" />
                Add Bit
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Bits List */}
      <div className="bg-white border rounded-lg p-4">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-medium">Bits ({bitsData.bits.length})</h2>
          <button
            onClick={() => setShowAddBitForm(!showAddBitForm)}
            className="flex items-center gap-2 px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            <Plus className="w-4 h-4" />
            Add Bit
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {bitsData.bits.map((bit) => (
            <div key={bit.id} className="p-4 border rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-medium">{bit.name}</h3>
                <span className="text-xs px-2 py-1 bg-gray-100 rounded capitalize">
                  {bit.kind}
                </span>
              </div>
              <div className="text-sm text-gray-600 mb-3">
                <div>Scope: {bit.scope}</div>
                <div>Inputs: {bit.inputs.length}</div>
                <div>Outputs: {bit.outputs.length}</div>
              </div>
              {showAddFlowForm && (
                <button
                  onClick={() => addStepToFlow(bit.id)}
                  className="w-full text-sm text-blue-600 hover:text-blue-800"
                >
                  Add to Flow
                </button>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Flows */}
      <div className="bg-white border rounded-lg p-4">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-medium">Flows ({bitsData.flows.length})</h2>
          <button
            onClick={() => setShowAddFlowForm(!showAddFlowForm)}
            className="flex items-center gap-2 px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700"
          >
            <Plus className="w-4 h-4" />
            Add Flow
          </button>
        </div>

        {/* Add Flow Form */}
        {showAddFlowForm && (
          <div className="mb-4 p-3 bg-gray-50 rounded-lg">
            <input
              type="text"
              value={newFlow.name}
              onChange={(e) => setNewFlow({ ...newFlow, name: e.target.value })}
              placeholder="Flow name"
              className="w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent mb-3"
              required
            />
            <div className="text-sm text-gray-600 mb-2">
              Steps: {newFlow.steps.length}
            </div>
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setShowAddFlowForm(false)}
                className="px-3 py-1 text-sm text-gray-600 hover:text-gray-800"
              >
                Cancel
              </button>
              <button
                onClick={handleAddFlow}
                disabled={!newFlow.name.trim() || newFlow.steps.length === 0}
                className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
              >
                Create Flow
              </button>
            </div>
          </div>
        )}

        <div className="space-y-4">
          {bitsData.flows.map((flow) => (
            <div key={flow.id} className="p-4 border rounded-lg">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-medium">{flow.name}</h3>
                <button
                  onClick={() => handleDryRun(flow.id)}
                  className="flex items-center gap-2 px-3 py-1 text-sm bg-orange-600 text-white rounded hover:bg-orange-700"
                >
                  <Play className="w-4 h-4" />
                  Dry Run ({Math.abs(getTariffCost('BITS_DRY_RUN'))} cbT)
                </button>
              </div>
              <div className="flex items-center gap-2">
                {flow.steps.map((step, index) => {
                  const bit = bitsData.bits.find(b => b.id === step.bit_id)
                  return (
                    <div key={index} className="flex items-center gap-2">
                      <div className="px-3 py-1 bg-blue-100 text-blue-800 rounded text-sm">
                        {bit?.name || 'Unknown Bit'}
                      </div>
                      {index < flow.steps.length - 1 && (
                        <ArrowRight className="w-4 h-4 text-gray-400" />
                      )}
                    </div>
                  )
                })}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
