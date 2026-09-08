@echo off
setlocal EnableExtensions
if defined LOCALAPPDATA (
  set "LOGDIR=%LOCALAPPDATA%\LimbusLyric\logs"
) else (
  set "LOGDIR=%TEMP%\LimbusLyric\logs"
)
if not exist "%LOGDIR%" mkdir "%LOGDIR%" >nul 2>nul
start "" explorer.exe "%LOGDIR%"
endlocal
