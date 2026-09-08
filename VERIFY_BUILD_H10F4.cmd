@echo off
setlocal
cd /d "%~dp0"
set "MAIN=LimbusLyric_v1.8.9.133_CROSS_PROVIDER_TRANSLATION_CUSTOM_ADAPTER_FOUNDATION_20260814.py"
if not exist "%MAIN%" (
  echo [FAIL] Main runtime source is missing.
  exit /b 1
)
findstr /C:"BURST-DISPLAY UI CLOSURE H10F3 + QQ POST-RAIL TREND RECOVERY H10F4" "%MAIN%" >nul 2>&1
if errorlevel 1 (
  echo [FAIL] This folder is NOT the H10F4 runtime source.
  echo Do not test this folder as H10F4.
  exit /b 1
)
echo [PASS] H10F4 runtime source is present in this folder.
echo Build tag must contain:
echo   QQ POST-RAIL TREND RECOVERY H10F4
exit /b 0
