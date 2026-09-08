@echo off
setlocal EnableExtensions
cd /d "%~dp0"
set "LIMBUSLYRIC_OFFLINE_BUILD=1"
call "%~dp0installer\BUILD_RELEASE.cmd"
exit /b %ERRORLEVEL%
