@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title LimbusLyric - Prepare Offline Build Cache

where py >nul 2>&1
if not errorlevel 1 (set "PY=py") else (
  where python >nul 2>&1
  if errorlevel 1 goto NOPY
  set "PY=python"
)

set "CACHE=%~dp0installer\offline_cache\wheels"
if not exist "%CACHE%" mkdir "%CACHE%"

echo Downloading all build/runtime wheels for this Windows build machine...
%PY% -m pip download --dest "%CACHE%" -r "%~dp0installer\requirements_build.txt" || goto FAIL
%PY% -m pip download --dest "%CACHE%" -r "%~dp0requirements_core.txt" || goto FAIL
%PY% -m pip download --dest "%CACHE%" -r "%~dp0requirements_optional_sync.txt" || goto FAIL
%PY% -m pip download --dest "%CACHE%" -r "%~dp0requirements_word_timing_optional.txt" || goto FAIL
%PY% -m pip download --dest "%CACHE%" -r "%~dp0requirements_audio_emphasis_optional.txt" || goto FAIL
%PY% -m pip download --dest "%CACHE%" -r "%~dp0requirements_netease_native.txt" || goto FAIL

echo.
echo SUCCESS. Offline wheel cache is ready:
echo   %CACHE%
echo.
echo You can now run BUILD_OFFLINE_FROM_CACHE.cmd.
pause
exit /b 0

:NOPY
echo ERROR: Python is required only on the build PC.
pause
exit /b 2

:FAIL
echo ERROR: Could not prepare the offline wheel cache.
pause
exit /b 1
