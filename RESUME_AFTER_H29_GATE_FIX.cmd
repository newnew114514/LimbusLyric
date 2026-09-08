@echo off
setlocal EnableExtensions
cd /d "%~dp0"
if not exist "%~dp0.build_installer_venv_ascii\Scripts\python.exe" (
  echo ERROR: This resume entry is only for the SAME project directory that already ran BUILD_END_USER_INSTALLER.cmd
  echo and failed at CHECK_NETEASE_TEMPORAL_RAIL_CACHED_WITNESS_H29_REPLAY.py after 103/104 PASS.
  echo.
  echo The existing .build_installer_venv_ascii is missing, so a safe resume is not possible here.
  pause
  exit /b 7
)
set "LIMBUSLYRIC_RESUME_AFTER_H29_GATE_FIX=1"
call "%~dp0installer\BUILD_RELEASE.cmd"
exit /b %ERRORLEVEL%
