import { type KeyboardEvent, useMemo, useState } from "react"

const PANELS = [
  { title: "PERSONAL", detail: "1 user · vault: open" },
  { title: "BUSINESS", detail: "12 seats · €1.247/mo" },
  { title: "AGENCY", detail: "23 clients · €8.400/mo" },
  { title: "DEVOPS", detail: "4 clusters · k8s: live" },
]

const RESPONSES: Record<string, string> = {
  "status billing": "€23,194 MRR · 47 customers · next payout €24,617",
  whoami: "You are Camarad-Prime · Emperor of Uptime",
  uptime: "∞ · no reboot since 2025-03-17",
  "status empire":
    "Empire online · throne warm · cathedral sealed · agents synced",
  "status cache": "All layers purged · CDN cool · browser silence confirmed",
  "status nginx": "Reloaded · TLS locked · /healthz → 200 in 38ms",
}

const INITIAL_LOG = [
  "> system ready · Δ-10 heartbeat OK",
  "> council vote: 12/12 YES",
  "> € tick. € tick. € tick.",
]

export default function AgentInterface() {
  const [activePanel, setActivePanel] = useState(0)
  const [mode, setMode] = useState<"mock" | "byok">("mock")
  const [command, setCommand] = useState("")
  const [log, setLog] = useState(INITIAL_LOG)

  const placeholder = useMemo(() => {
    return mode === "mock" ? "Command the Agent..." : "BYOK command…"
  }, [mode])

  const pushLog = (lines: string[]) => {
    setLog((prev) => [...prev, ...lines])
  }

  const execute = () => {
    const trimmed = command.trim()
    if (!trimmed) return
    const response =
      RESPONSES[trimmed.toLowerCase()] ||
      "Command received. Reality already complied."
    pushLog([`> ${trimmed}`, `← ${response}`])
    setCommand("")
  }

  const handleKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Enter") {
      event.preventDefault()
      execute()
    }
  }

  return (
    <section className="console-board">
      <div className="panel-grid">
        {PANELS.map((panel, index) => (
          <button
            key={panel.title}
            type="button"
            className={`panel ${activePanel === index ? "active" : ""}`}
            onClick={() => setActivePanel(index)}
          >
            <span className="panel-title">{panel.title}</span>
            <span className="panel-detail">{panel.detail}</span>
          </button>
        ))}
      </div>

      <div className="mode-switch">
        <button
          type="button"
          className={`mode-button ${mode === "mock" ? "active" : ""}`}
          onClick={() => setMode("mock")}
        >
          CAMARAD MOCK (0$)
        </button>
        <button
          type="button"
          className={`mode-button ${mode === "byok" ? "active" : ""}`}
          onClick={() => setMode("byok")}
        >
          CAMARAD BYOK (real)
        </button>
      </div>

      <div className="executor">
        <input
          value={command}
          onChange={(event) => setCommand(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
        />
        <button type="button" className="execute" onClick={execute}>
          EXECUTE AS CAMARAD
        </button>
      </div>

      <div className="console-output" aria-live="polite">
        {log.map((line, index) => (
          <span
            key={`${line}-${index}`}
            className={
              line.startsWith(">")
                ? "log-line command"
                : line.startsWith("←")
                  ? "log-line response"
                  : "log-line"
            }
          >
            {line}
          </span>
        ))}
      </div>
    </section>
  )
}
