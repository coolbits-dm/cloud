param(
    [string]$Root = "C:\Users\andre\Desktop\coolbits\board",
    [switch]$CreateLogonTask
)

$ErrorActionPreference = 'Stop'

Write-Host "[oCopilot] Setting up Board Orchestrator at $Root" -ForegroundColor Cyan

# Create folder structure
New-Item -ItemType Directory -Force -Path $Root, 
(Join-Path $Root 'bin'), 
(Join-Path $Root 'config'), 
(Join-Path $Root 'lib\boardlib'), 
(Join-Path $Root 'logs'), 
(Join-Path $Root 'runtime'), 
(Join-Path $Root 'scripts') | Out-Null

# Create requirements.txt
$req = @'
pyyaml
websockets
fastapi
uvicorn[standard]
psutil
requests
aiohttp
colorlog
watchdog
sounddevice
vosk
opencv-python

# Optional for GPU tests (install matching CUDA wheel manually if needed):
# torch
'@

Set-Content -Path (Join-Path $Root 'requirements.txt') -Value $req -Encoding UTF8

# Create bin/env.ps1
$envPs1 = @"
# Common env vars for Board
`$env:BOARD_ROOT = '$Root'
`$env:BOARD_CONFIG = Join-Path `$env:BOARD_ROOT 'config'
`$env:BOARD_LOGS   = Join-Path `$env:BOARD_ROOT 'logs'
`$env:BOARD_RUNTIME= Join-Path `$env:BOARD_ROOT 'runtime'
`$env:OCIM_VER = 'ocim-0.1'
"@

Set-Content -Path (Join-Path $Root 'bin/env.ps1') -Value $envPs1 -Encoding UTF8

# Create bin/board.ps1
$boardPs1 = @"
param([ValidateSet('start','stop','restart')] [string] `$Action = 'start')

. (Join-Path `$PSScriptRoot 'env.ps1')

`$python = (Get-Command python).Source
if (-not `$python) { throw 'Python not found in PATH.' }

function Start-Orchestrator {
    Write-Host '[oCopilot] Launching bridge_communication.py' -ForegroundColor Cyan
    Push-Location (Join-Path `$env:BOARD_ROOT 'scripts')
    & `$python bridge_communication.py 2>> (Join-Path `$env:BOARD_LOGS 'board_runtime.log')
    Pop-Location
}

switch (`$Action) {
    'start'   { Start-Orchestrator }
    'stop'    { Write-Host 'Use Task Manager / stop window for now.' }
    'restart' { Write-Host 'Restart: stop then start.'; Start-Orchestrator }
}
"@

Set-Content -Path (Join-Path $Root 'bin/board.ps1') -Value $boardPs1 -Encoding UTF8

# Create minimal config templates
$agentsYaml = @'
agents: []
'@
Set-Content -Path (Join-Path $Root 'config/board.agents.yaml') -Value $agentsYaml -Encoding UTF8

$libraryYaml = @'
version: 1
agents: []  # populated from discovery; enrich manually as needed
'@
Set-Content -Path (Join-Path $Root 'config/board.library.yaml') -Value $libraryYaml -Encoding UTF8

# Create board.exec.yaml with CBLM Agent Stress Test v0.3
$execYaml = @'
version: 0.1
plan_name: CBLM Agent Stress Test v0.3
steps:
  - id: discover_agents
    run: python scripts/agent_discovery.py --write
  - id: sync_library
    run: python scripts/agent_discovery.py --sync-library
  - id: enable_heartbeat
    run: python scripts/heartbeat_service.py --start --interval 15
  - id: cpu_probe
    run: python scripts/heartbeat_service.py --probe cpu
  - id: gpu_probe
    run: python scripts/heartbeat_service.py --probe gpu
  - id: mic_test
    run: python scripts/av_bridge.py --record-audio 5
  - id: cam_test
    run: python scripts/av_bridge.py --capture-frame
'@
Set-Content -Path (Join-Path $Root 'config/board.exec.yaml') -Value $execYaml -Encoding UTF8

# Create OCIM schema
$ocimSchema = @'
{
  "type": "object",
  "properties": {
    "type": {"type": "string"},
    "id": {"type": "string"},
    "meta": {
      "type": "object",
      "properties": {
        "name": {"type": "string"},
        "protocols": {"type": "array"},
        "capabilities": {"type": "array"},
        "tags": {"type": "array"}
      }
    }
  }
}
'@
Set-Content -Path (Join-Path $Root 'config/ocim.schema.json') -Value $ocimSchema -Encoding UTF8

Write-Host "✅ Setup Pack created successfully!" -ForegroundColor Green
Write-Host "📁 Structure: $Root" -ForegroundColor Cyan
Write-Host "Ready to run: pwsh bin/board.ps1 start" -ForegroundColor Yellow
