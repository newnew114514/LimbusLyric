@echo off
setlocal EnableExtensions
cd /d "%~dp0"
where py >nul 2>&1
if not errorlevel 1 (set "PY=py") else (set "PY=python")
%PY% CHECK_KUGOU_CLOCK_V123.py --seconds 16
set "EC=%ERRORLEVEL%"
echo.
echo Exit code: %EC%
echo Send KUGOU_CLOCK_PROBE_*.log together with LimbusLyric_error.log.
pause
exit /b %EC%
