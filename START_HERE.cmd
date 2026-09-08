@echo off
setlocal EnableExtensions
cd /d "%~dp0"
call "%~dp0LimbusLyric_START.cmd"
exit /b %ERRORLEVEL%
