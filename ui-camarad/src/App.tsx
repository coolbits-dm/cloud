import AgentInterface from "./components/AgentInterface"

export default function App() {
  return (
    <div className="console-shell">
      <header className="console-header">
        <p className="console-pill">Δ-∞ · Super Admin Protocol</p>
        <h1 className="console-title">Camarad Console</h1>
        <p className="console-subtitle">
          The empire is online. The throne is warm. Execute with quiet pride.
        </p>
      </header>
      <main className="console-main">
        <AgentInterface />
      </main>
    </div>
  )
}
