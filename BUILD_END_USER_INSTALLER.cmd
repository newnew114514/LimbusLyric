@echo off
setlocal EnableExtensions
cd /d "%~dp0"
call "%~dp0installer\BUILD_RELEASE.cmd"
exit /b %ERRORLEVEL%
