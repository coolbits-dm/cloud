# scripts/runner_m18.ps1 - M18 Pipeline Runner
# Non-interactive execution only

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

Write-Host "M18 Runner: Starting pipeline..." -ForegroundColor Green

try {
    # 1. Create directory structure
    Write-Host "Creating M18 directory structure..." -ForegroundColor Yellow
    $dirs = @(
        "artifacts/dev/walls",
        "artifacts/dev/boards", 
        "artifacts/dev/bits",
        "artifacts/dev/tokens",
        "cblm/rag/store"
    )
    
    foreach ($dir in $dirs) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
    }
    
    # 2. Seed demo content if missing
    Write-Host "Seeding demo content..." -ForegroundColor Yellow
    python scripts/seed_demo_content.py
    
    # 3. Validate schemas
    Write-Host "Validating JSON schemas..." -ForegroundColor Yellow
    python -c "
import json
import os
from pathlib import Path
import andrei

# Validate all wall files
for panel in andrei.PANELS:
    wall_path = andrei.get_wall_path(panel)
    if os.path.exists(wall_path):
        with open(wall_path, 'r') as f:
            data = json.load(f)
        print(f'✓ Wall {panel} validated')
    
    board_path = andrei.get_board_path(panel)
    if os.path.exists(board_path):
        with open(board_path, 'r') as f:
            data = json.load(f)
        print(f'✓ Board {panel} validated')

# Validate bits graph
if os.path.exists(andrei.BITS_FILE):
    with open(andrei.BITS_FILE, 'r') as f:
        data = json.load(f)
    print('✓ Bits graph validated')

# Validate tokens ledger
if os.path.exists(andrei.TOKENS_LEDGER):
    with open(andrei.TOKENS_LEDGER, 'r') as f:
        data = json.load(f)
    print('✓ Tokens ledger validated')
"
    
    # 4. Build RAG local
    Write-Host "Building RAG local index..." -ForegroundColor Yellow
    python cblm/rag/build_index.py
    
    # 5. Update panel state
    Write-Host "Updating panel state..." -ForegroundColor Yellow
    python -c "
import json
from str import s_json_load, s_json_dump_atomic
import andrei

# Load current state
state = s_json_load('panel/state.json')

# Update with M18 info
state['milestone'] = 'M18'
state['m18_status'] = 'completed'
state['m18_answers'] = andrei.M18_ANSWERS
state['updated_at'] = '$(Get-Date -Format \"yyyy-MM-ddTHH:mm:ss.fffZ\")'

# Save
s_json_dump_atomic('panel/state.json', state)
print('✓ Panel state updated')
"
    
    Write-Host "M18 Runner: COMPLETED SUCCESSFULLY" -ForegroundColor Green
    
} catch {
    Write-Host "M18 Runner: FAILED - $($_.Exception.Message)" -ForegroundColor Red
    throw
}
