@echo off
title SmartFix AI — Build Installer
color 0A

echo.
echo  ==========================================
echo   SmartFix AI — Installer Builder
echo  ==========================================
echo.

:: Check if Inno Setup is installed
set "ISCC="
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set "ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if exist "C:\Program Files\Inno Setup 6\ISCC.exe"       set "ISCC=C:\Program Files\Inno Setup 6\ISCC.exe"

if "%ISCC%"=="" (
    echo  [ERROR] Inno Setup 6 not found!
    echo.
    echo  Please download and install Inno Setup 6 from:
    echo  https://jrsoftware.org/isdl.php
    echo.
    echo  Then run this script again.
    pause
    exit /b 1
)

echo  [OK] Inno Setup found: %ISCC%
echo.
echo  [*] Creating output directory...
if not exist "dist\installer" mkdir "dist\installer"

echo  [*] Compiling SmartFix_Installer.iss ...
echo.
"%ISCC%" "SmartFix_Installer.iss"

if %ERRORLEVEL%==0 (
    echo.
    echo  ==========================================
    echo   SUCCESS! Installer created at:
    echo   dist\installer\SmartFix_Setup.exe
    echo  ==========================================
    echo.
    echo  Give SmartFix_Setup.exe to your users.
    echo  It will install EVERYTHING automatically:
    echo    - Python 3.11
    echo    - PyQt6, psutil, httpx
    echo    - Ollama AI engine
    echo    - llama3 model (4.7 GB download)
    echo    - SmartFix AI application
    echo.
    start "" "dist\installer"
) else (
    echo.
    echo  [ERROR] Build failed. Check output above.
)
pause
