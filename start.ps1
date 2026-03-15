# =============================================================================
# start.ps1 — 八卦推演 One-click launcher for Windows (PowerShell)
# =============================================================================
# Usage (open PowerShell in this folder):
#   .\start.ps1           — start both backend + frontend
#   .\start.ps1 backend   — backend only
#   .\start.ps1 frontend  — frontend only
#   .\start.ps1 stop      — stop all running services
#   .\start.ps1 install   — install all dependencies only
#
# First-time only — allow this script to run:
#   Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
# =============================================================================

param(
    [string]$Mode = "all"
)

$ErrorActionPreference = "Stop"

$ScriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir  = $ScriptDir
$FrontendDir = Join-Path $ScriptDir "frontend"
$VenvDir     = Join-Path $ScriptDir ".venv"
$EnvFile     = Join-Path $ScriptDir ".env"
$EnvExample  = Join-Path $ScriptDir ".env.example"

$BackendPort  = 8888
$FrontendPort = 5173

$PidDir          = $env:TEMP
$BackendPidFile  = Join-Path $PidDir "bagua_backend.pid"
$FrontendPidFile = Join-Path $PidDir "bagua_frontend.pid"
$BackendLog      = Join-Path $PidDir "bagua_backend.log"
$FrontendLog     = Join-Path $PidDir "bagua_frontend.log"

# ─── Colours ──────────────────────────────────────────────────
function Write-Green  { param($msg) Write-Host "[✓] $msg" -ForegroundColor Green }
function Write-Yellow { param($msg) Write-Host "[!] $msg" -ForegroundColor Yellow }
function Write-Red    { param($msg) Write-Host "[✗] $msg" -ForegroundColor Red }
function Write-Cyan   { param($msg) Write-Host "[→] $msg" -ForegroundColor Cyan }

function Show-Banner {
    Write-Host ""
    Write-Host "  ╔══════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "  ║          八 卦 推 演  BaGua System           ║" -ForegroundColor Cyan
    Write-Host "  ║  八字 · 六爻 · 奇门遁甲 · 风水 · 择日       ║" -ForegroundColor Cyan
    Write-Host "  ╚══════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

# ─── Dependency checks ────────────────────────────────────────
function Get-PythonExe {
    foreach ($exe in @("python", "python3", "py")) {
        try {
            $ver = & $exe --version 2>&1
            if ($ver -match "Python (\d+\.\d+)") {
                $major, $minor = $Matches[1].Split(".")
                if ([int]$major -ge 3 -and [int]$minor -ge 10) {
                    Write-Cyan "Python $($Matches[1]) found ($exe)"
                    return $exe
                }
            }
        } catch {}
    }
    Write-Red "Python 3.10+ not found. Download from https://www.python.org/downloads/"
    Write-Yellow "Tip: tick 'Add Python to PATH' during install"
    exit 1
}

function Assert-Node {
    try {
        $ver = node --version 2>&1
        Write-Cyan "Node $ver found"
    } catch {
        Write-Red "Node.js 18+ not found. Download from https://nodejs.org/"
        exit 1
    }
}

function Assert-Npm {
    try { npm --version | Out-Null }
    catch {
        Write-Red "npm not found (should come with Node.js)"
        exit 1
    }
}

# ─── Install ─────────────────────────────────────────────────
function Install-Backend {
    $pyExe = Get-PythonExe
    Write-Cyan "Installing Python dependencies..."
    Set-Location $BackendDir

    if (-not (Test-Path $VenvDir)) {
        & $pyExe -m venv .venv
        Write-Green "Created virtual environment at .venv"
    }

    $pip = Join-Path $VenvDir "Scripts\pip.exe"
    & $pip install --upgrade pip -q
    & $pip install -r requirements.txt -q
    Write-Green "Backend dependencies installed"
}

function Install-Frontend {
    Write-Cyan "Installing Node dependencies..."
    Set-Location $FrontendDir
    npm install --silent
    Write-Green "Frontend dependencies installed"
}

function Install-All {
    $null = Get-PythonExe
    Assert-Node
    Assert-Npm
    Install-Backend
    Install-Frontend
    Write-Green "All dependencies ready"
}

# ─── .env setup ──────────────────────────────────────────────
function Setup-Env {
    if (-not (Test-Path $EnvFile)) {
        if (Test-Path $EnvExample) {
            Copy-Item $EnvExample $EnvFile
            Write-Yellow ".env not found — created from .env.example"
            Write-Yellow "Edit $EnvFile to add your ANTHROPIC_API_KEY"
        }
    }
}

# ─── Wait for port ───────────────────────────────────────────
function Wait-ForPort {
    param([int]$Port, [string]$Label, [int]$Retries = 25)
    Write-Cyan "Waiting for $Label on :$Port ..."
    for ($i = 0; $i -lt $Retries; $i++) {
        try {
            $r = Invoke-WebRequest "http://localhost:$Port/health" -TimeoutSec 1 -UseBasicParsing -EA Stop
            Write-Green "$Label is up → http://localhost:$Port"
            return $true
        } catch {
            try {
                $tcp = New-Object System.Net.Sockets.TcpClient
                $tcp.Connect("localhost", $Port)
                $tcp.Close()
                Write-Green "$Label is up → http://localhost:$Port"
                return $true
            } catch {}
        }
        Start-Sleep -Seconds 1
    }
    Write-Yellow "$Label did not respond in ${Retries}s — check logs"
    return $false
}

# ─── Kill by PID file ────────────────────────────────────────
function Stop-ByPidFile {
    param([string]$PidFile, [string]$Label)
    if (Test-Path $PidFile) {
        $pid_ = Get-Content $PidFile -Raw
        $pid_ = $pid_.Trim()
        if ($pid_) {
            try {
                Stop-Process -Id ([int]$pid_) -Force -ErrorAction SilentlyContinue
                Write-Yellow "Stopped $Label (PID $pid_)"
            } catch {}
        }
        Remove-Item $PidFile -Force
    }
}

# ─── Start backend ───────────────────────────────────────────
function Start-Backend {
    $pyExe = Get-PythonExe
    $uvicorn = Join-Path $VenvDir "Scripts\uvicorn.exe"
    if (-not (Test-Path $uvicorn)) { $uvicorn = "uvicorn" }

    Stop-ByPidFile $BackendPidFile "old backend"
    Write-Cyan "Starting FastAPI backend on :$BackendPort ..."
    Set-Location $BackendDir

    $proc = Start-Process -FilePath $uvicorn `
        -ArgumentList "main:app", "--host", "0.0.0.0", "--port", "$BackendPort", "--reload", "--log-level", "info" `
        -WorkingDirectory $BackendDir `
        -RedirectStandardOutput $BackendLog `
        -RedirectStandardError  $BackendLog `
        -PassThru -WindowStyle Hidden

    $proc.Id | Out-File -FilePath $BackendPidFile -Encoding ascii
    Write-Green "Backend PID: $($proc.Id)  |  Log: $BackendLog"
    Wait-ForPort $BackendPort "Backend"
}

# ─── Start frontend ──────────────────────────────────────────
function Start-Frontend {
    Assert-Node
    Assert-Npm
    Stop-ByPidFile $FrontendPidFile "old frontend"

    if (-not (Test-Path (Join-Path $FrontendDir "node_modules"))) {
        Write-Yellow "node_modules missing — running npm install..."
        Set-Location $FrontendDir
        npm install --silent
    }

    Write-Cyan "Starting Vite frontend on :$FrontendPort ..."
    Set-Location $FrontendDir

    $proc = Start-Process -FilePath "npm" `
        -ArgumentList "run", "dev", "--", "--host", "0.0.0.0" `
        -WorkingDirectory $FrontendDir `
        -RedirectStandardOutput $FrontendLog `
        -RedirectStandardError  $FrontendLog `
        -PassThru -WindowStyle Hidden

    $proc.Id | Out-File -FilePath $FrontendPidFile -Encoding ascii
    Write-Green "Frontend PID: $($proc.Id)  |  Log: $FrontendLog"
    Wait-ForPort $FrontendPort "Frontend"
}

# ─── Stop all ────────────────────────────────────────────────
function Stop-All {
    Write-Cyan "Stopping all bagua processes..."
    Stop-ByPidFile $BackendPidFile  "backend"
    Stop-ByPidFile $FrontendPidFile "frontend"
    # Also kill any lingering uvicorn / vite processes
    Get-Process -Name "uvicorn" -ErrorAction SilentlyContinue | Stop-Process -Force
    Get-Process -Name "node"    -ErrorAction SilentlyContinue |
        Where-Object { $_.MainWindowTitle -eq "" } |
        ForEach-Object { $_.Kill() }
    Write-Green "Done"
}

# ─── Summary ─────────────────────────────────────────────────
function Show-Summary {
    Write-Host ""
    Write-Host "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor White
    Write-Host "  Services Running" -ForegroundColor White
    Write-Host "  ● Backend API  →  http://localhost:$BackendPort"  -ForegroundColor Green
    Write-Host "  ● API Docs     →  http://localhost:$BackendPort/docs" -ForegroundColor Green
    Write-Host "  ● Frontend     →  http://localhost:$FrontendPort" -ForegroundColor Green
    Write-Host "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor White
    Write-Host "  Press Ctrl+C or run: .\start.ps1 stop" -ForegroundColor Yellow
    Write-Host ""
    Write-Cyan "Backend log : $BackendLog"
    Write-Cyan "Frontend log: $FrontendLog"
    Write-Host ""
}

# ─── MAIN ─────────────────────────────────────────────────────
Show-Banner

switch ($Mode.ToLower()) {
    "install" {
        Install-All
    }
    "backend" {
        $null = Get-PythonExe
        Setup-Env
        if (-not (Test-Path $VenvDir)) { Install-Backend }
        Start-Backend
        Show-Summary
    }
    "frontend" {
        Assert-Node; Assert-Npm
        Start-Frontend
        Show-Summary
    }
    "stop" {
        Stop-All
    }
    default {
        $null = Get-PythonExe
        Assert-Node; Assert-Npm
        Setup-Env

        if (-not (Test-Path $VenvDir)) { Install-Backend }
        if (-not (Test-Path (Join-Path $FrontendDir "node_modules"))) { Install-Frontend }

        Start-Backend
        Start-Frontend
        Show-Summary

        Write-Green "Both services running. Opening browser..."
        Start-Process "http://localhost:$FrontendPort"

        Write-Cyan "Tailing logs (Ctrl+C to exit — services keep running):"
        Write-Yellow "To stop everything, run:  .\start.ps1 stop"
        Write-Host ""

        # Stream both log files until user hits Ctrl+C
        try {
            while ($true) {
                foreach ($log in @($BackendLog, $FrontendLog)) {
                    if (Test-Path $log) {
                        $lines = Get-Content $log -Tail 5 -ErrorAction SilentlyContinue
                        if ($lines) { $lines | ForEach-Object { Write-Host $_ } }
                    }
                }
                Start-Sleep -Seconds 2
            }
        } finally {
            Write-Host ""
            Write-Yellow "Shell detached. Services are still running."
            Write-Yellow "Run  .\start.ps1 stop  to shut them down."
        }
    }
}
