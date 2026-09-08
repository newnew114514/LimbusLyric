@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title LimbusLyric - QQ Baseline Isolation A/B

echo ============================================================
echo   QQ Baseline Isolation A/B
echo ============================================================
echo.
echo NetEase Native Log = OFF for this launch
echo BetterNCM Bridge   = OFF for this launch
echo QQ code/clock path remains enabled.
echo.
set "LIMBUSLYRIC_NETEASE_NATIVE_LOG=0"
set "LIMBUSLYRIC_NETEASE_INTERNAL_BRIDGE=0"
call "%~dp0RUN_CURRENT.cmd"
set "EC=%ERRORLEVEL%"
endlocal & exit /b %EC%
