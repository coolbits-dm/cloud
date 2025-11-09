# --- Hard guard: NU din Cursor/VS Code ---
$ppid = (Get-CimInstance Win32_Process -Filter "ProcessId=$PID").ParentProcessId
$parent = (Get-Process -Id $ppid -ErrorAction SilentlyContinue).ProcessName
if ($parent -match 'cursor|code|code-insiders') {
  Write-Error "Nu rula din Cursor/VS Code. Deschide PowerShell 7 (pwsh) și rulează scriptul acolo."
  exit 1
}
# -----------------------------------------

param(
  [string]$GatewayDir = "C:\Users\andre\Desktop\coolbits\gateway",
  [string]$ServiceUrl = "http://localhost:8000"
)

$ErrorActionPreference = "Stop"
Write-Host "== M19.3 Orchestrator Seed =="

Set-Location $GatewayDir

# Create example flow: NewPost → Sentiment → Comment
Write-Host "Creating example flow: NewPost → Sentiment → Comment"
$flowSpec = @{
  id = "flow_newpost_sentiment_comment"
  panel = "user"
  version = 1
  trigger = @{
    type = "Trigger.NewPost"
    match = @{
      panel = "user"
    }
  }
  nodes = @(
    @{
      id = "n1"
      type = "Action.NHA.Invoke"
      params = @{
        agent = "sentiment"
        text = "{{trigger.post.text}}"
      }
    },
    @{
      id = "n2"
      type = "Filter.Expression"
      params = @{
        expr = "{{n1.output.label}} in ['negative','mixed']"
      }
    },
    @{
      id = "n3"
      type = "Action.PostComment"
      if = "n2.passed"
      params = @{
        post_id = "{{trigger.post.id}}"
        text = "Sentiment: {{n1.output.label}} (score {{n1.output.score}})"
        author = "@orchestrator"
      }
    }
  )
  edges = @(
    @{
      from = "n1"
      to = "n2"
    },
    @{
      from = "n2"
      to = "n3"
    }
  )
} | ConvertTo-Json -Depth 10

$flowData = @{
  name = "NewPost Sentiment Comment"
  panel = "user"
  spec = ($flowSpec | ConvertFrom-Jjson)
} | ConvertTo-Json -Depth 10

try {
  $response = Invoke-WebRequest "$ServiceUrl/v1/flows" -Method POST -Body $flowData -ContentType "application/json" -UseBasicParsing -TimeoutSec 10
  Write-Host "[$($response.StatusCode)] Flow created OK"
  $result = $response.Content | ConvertFrom-Json
  $flowId = $result.id
  Write-Host "Flow ID: $flowId"
  
  # Activate flow
  Write-Host "Activating flow..."
  $activateResponse = Invoke-WebRequest "$ServiceUrl/v1/flows/$flowId/activate" -Method POST -UseBasicParsing -TimeoutSec 10
  Write-Host "[$($activateResponse.StatusCode)] Flow activated OK"
  
} catch {
  Write-Host "[ERR] Flow creation failed: $($_.Exception.Message)"
  exit 1
}

# Create business flow: NewPost → RAG → Summarize → Comment
Write-Host "Creating business flow: NewPost → RAG → Summarize → Comment"
$businessFlowSpec = @{
  id = "flow_business_rag_summarize"
  panel = "business"
  version = 1
  trigger = @{
    type = "Trigger.NewPost"
    match = @{
      panel = "business"
    }
  }
  nodes = @(
    @{
      id = "n1"
      type = "Action.RAG.Query"
      params = @{
        panel = "business"
        q = "{{trigger.post.text}}"
        k = 3
      }
    },
    @{
      id = "n2"
      type = "Action.NHA.Invoke"
      params = @{
        agent = "summarize"
        text = "{{n1.output.results}}"
      }
    },
    @{
      id = "n3"
      type = "Action.PostComment"
      params = @{
        post_id = "{{trigger.post.id}}"
        text = "[RAG] Summary: {{n2.output.summary}}"
        author = "@orchestrator"
      }
    }
  )
  edges = @(
    @{
      from = "n1"
      to = "n2"
    },
    @{
      from = "n2"
      to = "n3"
    }
  )
} | ConvertTo-Json -Depth 10

$businessFlowData = @{
  name = "Business RAG Summarize"
  panel = "business"
  spec = ($businessFlowSpec | ConvertFrom-Jjson)
} | ConvertTo-Json -Depth 10

try {
  $response = Invoke-WebRequest "$ServiceUrl/v1/flows" -Method POST -Body $businessFlowData -ContentType "application/json" -UseBasicParsing -TimeoutSec 10
  Write-Host "[$($response.StatusCode)] Business flow created OK"
  $result = $response.Content | ConvertFrom-Json
  $businessFlowId = $result.id
  Write-Host "Business Flow ID: $businessFlowId"
  
  # Activate business flow
  Write-Host "Activating business flow..."
  $activateResponse = Invoke-WebRequest "$ServiceUrl/v1/flows/$businessFlowId/activate" -Method POST -UseBasicParsing -TimeoutSec 10
  Write-Host "[$($activateResponse.StatusCode)] Business flow activated OK"
  
} catch {
  Write-Host "[ERR] Business flow creation failed: $($_.Exception.Message)"
}

# List all flows
Write-Host "Listing all flows..."
try {
  $response = Invoke-WebRequest "$ServiceUrl/v1/flows" -UseBasicParsing -TimeoutSec 10
  Write-Host "[$($response.StatusCode)] List flows OK"
  $flows = $response.Content | ConvertFrom-Json
  Write-Host "Total flows: $($flows.Count)"
  foreach ($flow in $flows) {
    Write-Host "  - $($flow.name) ($($flow.panel)): $($flow.is_active)"
  }
} catch {
  Write-Host "[ERR] List flows failed: $($_.Exception.Message)"
}

Write-Host "== Seed completed =="
Write-Host "Created flows:"
Write-Host "  - NewPost Sentiment Comment (user panel)"
Write-Host "  - Business RAG Summarize (business panel)"
