param([string]$cmd="")

function Get-PortProcess([int]$port) {
  $c = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
  if ($c) { return (Get-Process -Id $c.OwningProcess -ErrorAction SilentlyContinue) }
  return $null
}

switch ($cmd) {
  "up" {
    $env:PORT = $env:PORT -as [int]
    if (-not $env:PORT) { $env:PORT = 3001 }
    
    $p = Get-PortProcess $env:PORT
    if ($p) {
      Write-Host "Port $($env:PORT) ocupat de PID $($p.Id) ($($p.ProcessName)). Skip start." -ForegroundColor Yellow
      break
    }
    
    Write-Host "Starting server pe port $env:PORT" -ForegroundColor Cyan
    pnpm start
  }
  "down" {
    $ports = @(3001,3002,3003,3004,3005)
    foreach ($port in $ports) {
      $p = Get-PortProcess $port
      if ($p) {
        Write-Host "Killing PID $($p.Id) on port $port" -ForegroundColor Red
        taskkill /PID $p.Id /F | Out-Null
      }
    }
    Write-Host "Down complet." -ForegroundColor Green
  }
  "status" {
    $ports = @(3001,3002,3003,3004,3005)
    $active = @()
    foreach ($port in $ports) {
      $p = Get-PortProcess $port
      if ($p) {
        $active += "Port $port`: PID $($p.Id) ($($p.ProcessName))"
      }
    }
    if ($active.Count -eq 0) {
      Write-Host "No active servers found" -ForegroundColor Yellow
    } else {
      Write-Host "Active servers:" -ForegroundColor Green
      $active | ForEach-Object { Write-Host "  $_" -ForegroundColor Green }
    }
  }
  default {
    Write-Host "Usage: ./dev.ps1 [up|down|status]" -ForegroundColor Cyan
    Write-Host "  up     - Start server with port protection" -ForegroundColor White
    Write-Host "  down   - Stop all servers on ports 3001-3005" -ForegroundColor White
    Write-Host "  status - Show active servers" -ForegroundColor White
  }
}