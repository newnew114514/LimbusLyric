@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"
title LimbusLyric - Repackage Existing dist

if not exist "%~dp0dist\LimbusLyric\LimbusLyric.exe" (
  echo ERROR: dist\LimbusLyric\LimbusLyric.exe was not found.
  echo Run BUILD_END_USER_INSTALLER.cmd first.
  pause
  exit /b 2
)

set "ISCC="
for %%I in (
  "%ProgramFiles(x86)%\Inno Setup 7\ISCC.exe"
  "%ProgramFiles%\Inno Setup 7\ISCC.exe"
  "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
  "%ProgramFiles%\Inno Setup 6\ISCC.exe"
  "%LOCALAPPDATA%\Programs\Inno Setup 7\ISCC.exe"
  "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
) do if exist %%I set "ISCC=%%~I"
if not defined ISCC (
  echo ERROR: Inno Setup compiler ISCC.exe was not found.
  pause
  exit /b 3
)

if not exist "%~dp0installer\release" mkdir "%~dp0installer\release"
"%ISCC%" "%~dp0installer\LimbusLyric_Setup.iss" || goto FAIL

echo.
echo SUCCESS: installer\release\LimbusLyric_Setup_1.8.9.135.exe
pause
exit /b 0

:FAIL
echo Inno Setup packaging failed.
pause
exit /b 1
