param (
    [string]$InstallDir = "C:\Program Files\SmartFix AI"
)

$ErrorActionPreference = "SilentlyContinue"
$ProgressPreference    = "SilentlyContinue"

function Write-Log($msg) {
    $ts = (Get-Date -Format "HH:mm:ss")
    Add-Content "$InstallDir\install_log.txt" "[$ts] $msg"
    Write-Host "[$ts] $msg"
}

New-Item -ItemType Directory -Force -Path "$InstallDir\data"  | Out-Null
New-Item -ItemType Directory -Force -Path "$InstallDir\logs"  | Out-Null

# STEP 1: Python 3.11
Write-Log "Checking for Python..."
$python = $null
try { $python = (Get-Command python -ErrorAction Stop).Source } catch {}

$needPython = $true
if ($python) {
    $ver = & python --version 2>&1
    if ($ver -match "Python 3\.(1[01])") {
        Write-Log "Python already installed: $ver"
        $needPython = $false
    }
}

if ($needPython) {
    Write-Log "Downloading Python 3.11.9..."
    $pyUrl = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
    $pyInstaller = "$env:TEMP\python-3.11.9-amd64.exe"
    Invoke-WebRequest -Uri $pyUrl -OutFile $pyInstaller -UseBasicParsing
    Write-Log "Installing Python 3.11.9 (silent)..."
    Start-Process -FilePath $pyInstaller -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 Include_pip=1 Include_launcher=0" -Wait -NoNewWindow
    Remove-Item $pyInstaller -Force -ErrorAction SilentlyContinue
    Write-Log "Python 3.11 installed."
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + $env:PATH
}

# STEP 2: pip packages
Write-Log "Installing Python packages..."
$packages = @(
    "PyQt6>=6.6.1",
    "psutil>=5.9.8",
    "httpx>=0.27.0",
    "pywin32>=306",
    "Pillow>=10.3.0"
)
foreach ($pkg in $packages) {
    Write-Log "  pip install $pkg"
    & python -m pip install "$pkg" --quiet --no-warn-script-location 2>&1 | Out-Null
}
Write-Log "Python packages installed."

# STEP 3: Ollama
Write-Log "Checking for Ollama..."
$ollamaExe  = "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"
$ollamaPath = $null
try { $ollamaPath = (Get-Command ollama -ErrorAction Stop).Source } catch {}

if (-not $ollamaPath -and -not (Test-Path $ollamaExe)) {
    Write-Log "Downloading Ollama installer..."
    $ollamaUrl       = "https://ollama.com/download/OllamaSetup.exe"
    $ollamaInstaller = "$env:TEMP\OllamaSetup.exe"
    Invoke-WebRequest -Uri $ollamaUrl -OutFile $ollamaInstaller -UseBasicParsing
    Write-Log "Installing Ollama (silent)..."
    Start-Process -FilePath $ollamaInstaller -ArgumentList "/VERYSILENT /SUPPRESSMSGBOXES /NORESTART" -Wait -NoNewWindow
    Remove-Item $ollamaInstaller -Force -ErrorAction SilentlyContinue
    Write-Log "Ollama installed."
} else {
    Write-Log "Ollama already installed."
}

# STEP 4: Start Ollama and pull llama3
Write-Log "Starting Ollama service..."
$ollamaBin = if (Test-Path $ollamaExe) { $ollamaExe } else { "ollama" }
Start-Process -FilePath $ollamaBin -ArgumentList "serve" -WindowStyle Hidden -ErrorAction SilentlyContinue
Start-Sleep -Seconds 5

try {
    $tags      = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -TimeoutSec 5
    $models    = ($tags.Content | ConvertFrom-Json).models
    $hasLlama3 = $models | Where-Object { $_.name -like "llama3*" }
} catch { $hasLlama3 = $null }

if (-not $hasLlama3) {
    Write-Log "Pulling llama3 model (~4.7 GB). This will take several minutes..."
    & $ollamaBin pull llama3 2>&1 | ForEach-Object { Write-Log "  [ollama] $_" }
    Write-Log "llama3 model ready."
} else {
    Write-Log "llama3 model already present."
}

# STEP 5: Register auto-start
Write-Log "Configuring auto-start with Windows..."
$launcherPath = "$InstallDir\SmartFix AI.exe"
$regPath = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
Set-ItemProperty -Path $regPath -Name "SmartFix AI" -Value "`"$launcherPath`"" -ErrorAction SilentlyContinue

Write-Log "SmartFix AI installation complete!"
exit 0
