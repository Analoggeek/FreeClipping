@echo off
setlocal
title FreeClipping Setup
echo.
echo   FreeClipping setup shuru ho raha hai...
echo.
set "DIR=%~dp0"
set "F=%DIR%install.ps1"
if exist "%F%" goto :run
echo   install.ps1 nahi mila. GitHub se download ho raha hai...
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Invoke-WebRequest -UseBasicParsing -Uri 'https://raw.githubusercontent.com/Analoggeek/FreeClipping/main/install.ps1' -OutFile '%F%' -TimeoutSec 120 } catch { Write-Host 'Download failed: ' $_.Exception.Message; exit 1 }"
if not exist "%F%" goto :fail
:run
powershell -NoProfile -ExecutionPolicy Bypass -File "%F%"
goto :end
:fail
echo.
echo   install.ps1 nahi mila ya download nahi ho paya.
echo   Internet connected hai ya nahi, check karke dobara try karo.
:end
echo.
pause
