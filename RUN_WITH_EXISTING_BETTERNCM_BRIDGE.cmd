@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title LimbusLyric - Existing BetterNCM Bridge Opt-In
set "LIMBUSLYRIC_NETEASE_INTERNAL_BRIDGE=1"
set "LIMBUSLYRIC_NETEASE_NATIVE_LOG=1"
call "%~dp0RUN_CURRENT.cmd"
set "EC=%ERRORLEVEL%"
endlocal & exit /b %EC%
