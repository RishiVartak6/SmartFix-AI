@echo off
title SmartFix AI
echo.
echo  =====================================================
echo    SmartFix AI — AI-Powered Windows Error Monitor
echo  =====================================================
echo.

:: Auto-elevate to Administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo  Requesting Administrator privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo  [OK] Running as Administrator
echo  [*] Launching SmartFix AI...
echo.

cd /d "%~dp0"
python smartfix_app.py

if %errorLevel% neq 0 (
    echo.
    echo  [ERROR] SmartFix AI encountered an error.
    echo  Make sure Python and dependencies are installed:
    echo    pip install PyQt6 pystray Pillow psutil pywin32
    pause
)
