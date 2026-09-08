@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title LimbusLyric Audio Emphasis Optional Dependency
where py >nul 2>&1
if not errorlevel 1 (
  set "PY=py"
) else (
  where python >nul 2>&1
  if errorlevel 1 goto NOPY
  set "PY=python"
)
echo Installing optional Windows Core Audio support (pycaw)...
%PY% -m pip install -r requirements_audio_emphasis_optional.txt
if errorlevel 1 (
  echo.
  echo Install failed. Normal lyric playback is NOT affected.
) else (
  echo.
  echo Audio emphasis dependency installed.
)
goto END
:NOPY
echo Python was not found.
:END
pause
endlocal
