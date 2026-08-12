# SmartFix AI - Automated Setup and Launch Script for Windows
# B.Tech Computer Engineering Major Project

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "       SmartFix AI — Windows Diagnostic System           " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

$WorkspaceRoot = Split-Path -Parent $PSScriptRoot
Set-Location $WorkspaceRoot

# 1. Check Python
Write-Host "`n[1/5] Checking Python environment..." -ForegroundColor Yellow
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pyVer = python --version
    Write-Host "Found: $pyVer" -ForegroundColor Green
} else {
    Write-Host "ERROR: Python is not found in PATH. Please install Python 3.10+." -ForegroundColor Red
    Exit 1
}

# 2. Check Node & NPM
Write-Host "`n[2/5] Checking Node.js & NPM..." -ForegroundColor Yellow
if (Get-Command node -ErrorAction SilentlyContinue) {
    $nodeVer = node --version
    Write-Host "Found Node: $nodeVer" -ForegroundColor Green
} else {
    Write-Host "ERROR: Node.js is not found in PATH. Please install Node.js." -ForegroundColor Red
    Exit 1
}

# 3. Install Python requirements
Write-Host "`n[3/5] Installing backend dependencies..." -ForegroundColor Yellow
python -m pip install -r requirements.txt --quiet
Write-Host "Python dependencies verified." -ForegroundColor Green

# 4. Install & Build Frontend
Write-Host "`n[4/5] Building Desktop Frontend..." -ForegroundColor Yellow
Set-Location "$WorkspaceRoot\frontend"
npm install --silent
npm run build
Set-Location $WorkspaceRoot
Write-Host "Frontend build complete." -ForegroundColor Green

# 5. Check Ollama (Optional)
Write-Host "`n[5/5] Checking Ollama Status..." -ForegroundColor Yellow
try {
    $ollamaCheck = Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 2 -ErrorAction SilentlyContinue
    if ($ollamaCheck) {
        Write-Host "Ollama server is active on localhost:11434" -ForegroundColor Green
    }
} catch {
    Write-Host "Notice: Ollama is not running. SmartFix will run in offline Heuristic Rule Engine fallback mode." -ForegroundColor Yellow
}

Write-Host "`n========================================================" -ForegroundColor Cyan
Write-Host " Setup complete! Starting SmartFix AI System..." -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan

# Launch Backend in new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$WorkspaceRoot'; python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"

# Launch Frontend in dev/Electron mode
Set-Location "$WorkspaceRoot\frontend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$WorkspaceRoot\frontend'; npm run dev"
