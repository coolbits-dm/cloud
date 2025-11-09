const root = document.getElementById("console-root");

if (root) {
  const panels = Array.from(document.querySelectorAll("[data-panel]"));
  const modeButtons = Array.from(document.querySelectorAll("[data-mode]"));
  const input = document.getElementById("console-input");
  const output = document.getElementById("console-output");
  const executeButton = document.getElementById("console-execute");

  const RESPONSES = {
    "status empire": "€1.5M seed closed · €23,194 MRR · 0 humans required",
    "status billing": "Billing: LIVE · €23,194 MRR · 47 customers · next payout €24,617",
    "status cache": "Cache layers purged · CDN cool · browser silence enforced",
    "status nginx": "Nginx reloaded · TLS locked · /healthz → 200 in 38ms",
    "status security": "Biometric + passkey + YubiKey confirmed · IP whitelist intact",
    uptime: "∞ · no reboot since 2025-03-17 · emperor heartbeat steady",
    whoami: "You are Camarad-Prime · Emperor of Uptime",
  };

  let mode = "byok";

  const placeholders = {
    mock: "Command the Agent...",
    byok: "Command the Empire...",
  };

  const appendLog = (type, text) => {
    if (!output) return;
    const span = document.createElement("span");
    span.className = `log-line ${type}`;
    span.textContent = text;
    output.appendChild(span);
    output.scrollTop = output.scrollHeight;
  };

  const execute = () => {
    if (!input || !input.value) return;
    const command = input.value.trim();
    if (!command) return;

    appendLog("command", `> ${command}`);

    const response =
      RESPONSES[command.toLowerCase()] ||
      (mode === "byok"
        ? "Command received. Reality already complied."
        : "Mock acknowledged. Empire unchanged.");

    appendLog("response", `← ${response}`);
    input.value = "";
  };

  executeButton?.addEventListener("click", execute);
  input?.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      execute();
    }
  });

  panels.forEach((panel) => {
    panel.addEventListener("click", () => {
      panels.forEach((btn) => btn.classList.remove("active"));
      panel.classList.add("active");
      const focusLabel = panel.querySelector(".panel-title")?.textContent ?? "";
      appendLog("command", `> ${focusLabel} focus locked`);
    });
  });

  modeButtons.forEach((button) => {
    button.addEventListener("click", () => {
      modeButtons.forEach((btn) => btn.classList.remove("active"));
      button.classList.add("active");
      mode = button.dataset.mode === "mock" ? "mock" : "byok";
      if (input) {
        input.placeholder = placeholders[mode];
      }
      appendLog(
        "response",
        mode === "byok"
          ? "BYOK real mode: live agents listening."
          : "Mock sandbox engaged."
      );
    });
  });

  if (input) {
    input.placeholder = placeholders[mode];
  }
} else {
  console.log("camarad.ai · public facade");
}
