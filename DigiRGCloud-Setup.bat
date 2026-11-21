@echo off
setlocal
title DigiRG Cloud Setup
echo.
echo   DigiRG Cloud setup shuru ho raha hai...
echo.
set "F=%~dp0install.ps1"
if exist "%F%" goto :run
echo   install.ps1 nahi mila.
goto :end
:run
powershell -NoProfile -ExecutionPolicy Bypass -File "%F%"
:end
echo.
pause
