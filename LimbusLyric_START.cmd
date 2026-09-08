@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title LimbusLyric - One Click Start

echo ============================================================
echo   LimbusLyric - ONE CLICK START
echo ============================================================
echo.
echo NetEase 3.x native-log sync is the default no-plugin path.
echo BetterNCM Bridge is optional and is NOT installed/modified automatically.
echo.
echo [1/2] Checking Python runtime...
where py >nul 2>&1
if not errorlevel 1 goto RUNAPP
where python >nul 2>&1
if not errorlevel 1 goto RUNAPP
echo.
echo This source build still requires Python to be installed first.
echo.
pause
exit /b 9009

:RUNAPP
echo [2/2] Starting LimbusLyric...
call "%~dp0RUN_CURRENT.cmd"
exit /b %ERRORLEVEL%
