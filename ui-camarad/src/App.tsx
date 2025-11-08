import AgentInterface from "./components/AgentInterface"

export default function App() {
  return (
    <div className="min-h-screen bg-black text-cyan-400 font-mono">
      <div className="p-8">
        <h1 className="text-6xl font-bold mb-4 animate-pulse">
          Camarad Console
        </h1>
        <p className="text-2xl mb-8">
          Human in the Loop.<br/>
          Super Admin Protocol.<br/>
          You are Camarad.
        </p>
        <AgentInterface />
      </div>
    </div>
  )
}
