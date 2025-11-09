// Simple Flow Builder UI for M19.4
import React, { useState, useEffect } from 'react'

const NODE_TYPES = [
  { id: 'Trigger.NewPost', label: 'New Post Trigger', color: '#e1f5fe' },
  { id: 'Action.NHA.Invoke', label: 'NHA Invoke', color: '#f3e5f5' },
  { id: 'Action.RAG.Query', label: 'RAG Query', color: '#e8f5e8' },
  { id: 'Action.PostComment', label: 'Post Comment', color: '#fff3e0' },
  { id: 'Filter.Expression', label: 'Filter', color: '#fce4ec' },
  { id: 'Enrich.Map', label: 'Enrich', color: '#e0f2f1' },
  { id: 'Delay', label: 'Delay', color: '#f1f8e9' },
  { id: 'Emit.Event', label: 'Emit Event', color: '#e3f2fd' }
]

interface FlowNode {
  id: string
  type: string
  params: Record<string, any>
  condition: string
}

interface FlowEdge {
  from: string
  to: string
}

const FlowBuilder = () => {
  const [nodes, setNodes] = useState<FlowNode[]>([])
  const [edges, setEdges] = useState<FlowEdge[]>([])
  const [selectedNode, setSelectedNode] = useState<FlowNode | null>(null)
  const [flowName, setFlowName] = useState('')
  const [flowPanel, setFlowPanel] = useState('user')
  const [jsonSpec, setJsonSpec] = useState('')
  const [isValid, setIsValid] = useState(true)

  // Generate JSON spec
  useEffect(() => {
    const spec = {
      id: `flow_${flowName.toLowerCase().replace(/\s+/g, '_')}`,
      panel: flowPanel,
      version: 1,
      trigger: nodes.find(n => n.type === 'Trigger.NewPost')?.params || { type: 'Trigger.NewPost', match: { panel: flowPanel } },
      nodes: nodes.map((node, index) => ({
        id: `n${index + 1}`,
        type: node.type,
        params: node.params,
        ...(node.condition && { if: node.condition })
      })),
      edges: edges.map(edge => ({
        from: `n${nodes.findIndex(n => n.id === edge.from) + 1}`,
        to: `n${nodes.findIndex(n => n.id === edge.to) + 1}`
      }))
    }
    
    setJsonSpec(JSON.stringify(spec, null, 2))
    
    // Basic validation
    const valid = flowName.length > 0 && nodes.length > 0
    setIsValid(valid)
  }, [nodes, edges, flowName, flowPanel])

  const addNode = (nodeType: string) => {
    const newNode: FlowNode = {
      id: `node_${Date.now()}`,
      type: nodeType,
      params: getDefaultParams(nodeType),
      condition: ''
    }
    setNodes([...nodes, newNode])
  }

  const getDefaultParams = (nodeType: string) => {
    switch (nodeType) {
      case 'Action.NHA.Invoke':
        return { agent: 'sentiment', text: '{{trigger.post.text}}' }
      case 'Action.RAG.Query':
        return { panel: '{{trigger.post.panel}}', q: '{{trigger.post.text}}', k: 5 }
      case 'Action.PostComment':
        return { post_id: '{{trigger.post.id}}', text: 'Comment text', author: '@orchestrator' }
      case 'Filter.Expression':
        return { expr: 'true' }
      case 'Enrich.Map':
        return { mapping: { key: 'value' } }
      case 'Delay':
        return { delay_ms: 1000 }
      case 'Emit.Event':
        return { event_type: 'info', message: 'Event message' }
      default:
        return {}
    }
  }

  const updateNode = (nodeId: string, updates: Partial<FlowNode>) => {
    setNodes(nodes.map(node => 
      node.id === nodeId ? { ...node, ...updates } : node
    ))
  }

  const deleteNode = (nodeId: string) => {
    setNodes(nodes.filter(node => node.id !== nodeId))
    setEdges(edges.filter(edge => edge.from !== nodeId && edge.to !== nodeId))
  }

  const addEdge = (fromId: string, toId: string) => {
    const newEdge: FlowEdge = { from: fromId, to: toId }
    setEdges([...edges, newEdge])
  }

  const saveFlow = async () => {
    try {
      const spec = JSON.parse(jsonSpec)
      const flowData = {
        name: flowName,
        panel: flowPanel,
        spec: spec
      }

      const response = await fetch('/v1/flows', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(flowData)
      })

      if (response.ok) {
        alert('Flow saved successfully!')
      } else {
        alert('Failed to save flow')
      }
    } catch (error) {
      alert('Error saving flow: ' + (error as Error).message)
    }
  }

  const dryRunFlow = async () => {
    try {
      const spec = JSON.parse(jsonSpec)
      const runData = {
        input: {
          post: {
            id: 'dry-test-123',
            panel: flowPanel,
            author: 'test_user',
            text: 'Dry run test post'
          }
        },
        mode: 'dry'
      }

      // First create the flow
      const flowData = {
        name: flowName + ' (Dry Run)',
        panel: flowPanel,
        spec: spec
      }

      const createResponse = await fetch('/v1/flows', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(flowData)
      })

      if (createResponse.ok) {
        const flow = await createResponse.json()
        
        // Run the flow
        const runResponse = await fetch(`/v1/flows/${flow.id}/run`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(runData)
        })

        if (runResponse.ok) {
          const run = await runResponse.json()
          alert(`Dry run started! Run ID: ${run.run_id}`)
        } else {
          alert('Failed to start dry run')
        }
      } else {
        alert('Failed to create flow for dry run')
      }
    } catch (error) {
      alert('Error running dry run: ' + (error as Error).message)
    }
  }

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      {/* Node Palette */}
      <div style={{ width: '200px', padding: '20px', borderRight: '1px solid #ccc' }}>
        <h3>Node Types</h3>
        {NODE_TYPES.map(nodeType => (
          <div
            key={nodeType.id}
            style={{
              padding: '10px',
              margin: '5px 0',
              backgroundColor: nodeType.color,
              cursor: 'pointer',
              borderRadius: '4px'
            }}
            onClick={() => addNode(nodeType.id)}
          >
            {nodeType.label}
          </div>
        ))}
      </div>

      {/* Flow Canvas */}
      <div style={{ flex: 1, padding: '20px' }}>
        <div style={{ marginBottom: '20px' }}>
          <input
            type="text"
            placeholder="Flow Name"
            value={flowName}
            onChange={(e) => setFlowName(e.target.value)}
            style={{ marginRight: '10px', padding: '5px' }}
          />
          <select
            value={flowPanel}
            onChange={(e) => setFlowPanel(e.target.value)}
            style={{ marginRight: '10px', padding: '5px' }}
          >
            <option value="user">User</option>
            <option value="business">Business</option>
            <option value="agency">Agency</option>
            <option value="dev">Dev</option>
          </select>
          <button onClick={saveFlow} disabled={!isValid} style={{ marginRight: '10px' }}>
            Save Flow
          </button>
          <button onClick={dryRunFlow} disabled={!isValid}>
            Dry Run
          </button>
        </div>

        {/* Flow Nodes */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '20px' }}>
          {nodes.map((node, index) => (
            <div
              key={node.id}
              style={{
                padding: '15px',
                border: selectedNode?.id === node.id ? '2px solid #007bff' : '1px solid #ccc',
                borderRadius: '8px',
                backgroundColor: NODE_TYPES.find(t => t.id === node.type)?.color || '#f8f9fa',
                minWidth: '200px',
                cursor: 'pointer'
              }}
              onClick={() => setSelectedNode(node)}
            >
              <div style={{ fontWeight: 'bold', marginBottom: '10px' }}>
                {NODE_TYPES.find(t => t.id === node.type)?.label}
              </div>
              <div style={{ fontSize: '0.9em', marginBottom: '10px' }}>
                {Object.entries(node.params).map(([key, value]) => (
                  <div key={key}>
                    <strong>{key}:</strong> {JSON.stringify(value)}
                  </div>
                ))}
              </div>
              {node.condition && (
                <div style={{ fontSize: '0.9em', fontStyle: 'italic' }}>
                  <strong>if:</strong> {node.condition}
                </div>
              )}
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  deleteNode(node.id)
                }}
                style={{ marginTop: '10px', padding: '5px 10px', fontSize: '0.8em' }}
              >
                Delete
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Properties Panel */}
      <div style={{ width: '300px', padding: '20px', borderLeft: '1px solid #ccc' }}>
        {selectedNode ? (
          <div>
            <h3>Node Properties</h3>
            <div style={{ marginBottom: '10px' }}>
              <label>Type: {selectedNode.type}</label>
            </div>
            {Object.entries(selectedNode.params).map(([key, value]) => (
              <div key={key} style={{ marginBottom: '10px' }}>
                <label>{key}:</label>
                <input
                  type="text"
                  value={String(value)}
                  onChange={(e) => updateNode(selectedNode.id, {
                    params: { ...selectedNode.params, [key]: e.target.value }
                  })}
                  style={{ width: '100%', padding: '5px' }}
                />
              </div>
            ))}
            <div style={{ marginBottom: '10px' }}>
              <label>Condition (if):</label>
              <input
                type="text"
                value={selectedNode.condition}
                onChange={(e) => updateNode(selectedNode.id, { condition: e.target.value })}
                style={{ width: '100%', padding: '5px' }}
                placeholder="e.g., n1.passed"
              />
            </div>
          </div>
        ) : (
          <div>
            <h3>JSON Specification</h3>
            <pre style={{ 
              backgroundColor: '#f8f9fa', 
              padding: '10px', 
              fontSize: '0.8em',
              overflow: 'auto',
              height: '400px'
            }}>
              {jsonSpec}
            </pre>
          </div>
        )}
      </div>
    </div>
  )
}

export default FlowBuilder