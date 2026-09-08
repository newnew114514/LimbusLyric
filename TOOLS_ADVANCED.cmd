@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title LimbusLyric v1.8.9.133 - Advanced Tools
:MENU
cls
echo ============================================================
echo   LimbusLyric v1.8.9.133 - ADVANCED TOOLS
echo ============================================================
echo.
echo   [1] Run normal build (NetEase Native default)
echo   [2] Run with an EXISTING BetterNCM Bridge (no installation)
echo   [3] Run Kugou Clock Probe
echo   [4] Open README
echo   [0] Exit
echo.
set "CHOICE="
set /p "CHOICE=Select: "
if "%CHOICE%"=="1" start "LimbusLyric CURRENT" "%ComSpec%" /d /c call "%~dp0RUN_CURRENT.cmd"
if "%CHOICE%"=="2" start "LimbusLyric Bridge Opt-In" "%ComSpec%" /d /c call "%~dp0RUN_WITH_EXISTING_BETTERNCM_BRIDGE.cmd"
if "%CHOICE%"=="3" start "Kugou Clock Probe" "%ComSpec%" /d /c call "%~dp0CHECK_KUGOU_CLOCK_V123.cmd"
if "%CHOICE%"=="4" start "" notepad.exe "%~dp0README_CURRENT_BUILD.txt"
if "%CHOICE%"=="0" exit /b 0
goto MENU
