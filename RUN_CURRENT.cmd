@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title LimbusLyric v1.8.9.133 - KUGOU HOST RAIL REWORK TEST
set "LOG=startup_console.log"
set "MAIN=LimbusLyric_v1.8.9.133_CROSS_PROVIDER_TRANSLATION_CUSTOM_ADAPTER_FOUNDATION_20260814.py"
>"%LOG%" echo ===== LimbusLyric v1.8.9.133 AUDITED RC6 20260815 =====

echo [1/8] Checking Python...
where py >nul 2>&1
if not errorlevel 1 (
  set "PY=py"
) else (
  where python >nul 2>&1
  if errorlevel 1 goto NOPY
  set "PY=python"
)
%PY% -c "import sys,platform; print('exe=',sys.executable); print('version=',sys.version); print('platform=',platform.platform())" >>"%LOG%" 2>&1
if errorlevel 1 goto FAIL

echo [2/8] Checking core dependencies...
%PY% -c "import PyQt5,win32gui,requests,pywinauto,comtypes; print('Core imports: OK')" >>"%LOG%" 2>&1
if errorlevel 1 (
  echo Installing missing core dependencies...
  %PY% -m pip install -r requirements_core.txt >>"%LOG%" 2>&1
  if errorlevel 1 goto FAIL
)

echo [3/8] Checking word timing dependency...
%PY% -c "from Crypto.Cipher import AES,DES3; print('PyCryptodome: OK')" >>"%LOG%" 2>&1
if errorlevel 1 %PY% -m pip install -r requirements_word_timing_optional.txt >>"%LOG%" 2>&1

echo [4/8] Checking NetEase native detector...
%PY% -c "import cloudmusic_detector; print('CloudMusic detector: OK')" >>"%LOG%" 2>&1
if errorlevel 1 (
  echo Installing NetEase native detector...
  %PY% -m pip install -r requirements_netease_native.txt >>"%LOG%" 2>&1
  if errorlevel 1 echo WARNING: Native detector unavailable; NetEase will fall back to UIA/GSMTC.>>"%LOG%"
)

echo [5/8] Checking Windows media sync...
%PY% -c "import winrt.windows.foundation; import winrt.windows.foundation.collections; from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionManager; print('PyWinRT: OK')" >>"%LOG%" 2>&1
if errorlevel 1 (
  %PY% -m pip install -r requirements_optional_sync.txt >>"%LOG%" 2>&1
  if errorlevel 1 echo WARNING: PyWinRT unavailable; GSMTC will be disabled and player-specific fallbacks remain.>>"%LOG%"
)

echo [6/8] Checking optional audio emphasis...
%PY% -c "from pycaw.pycaw import AudioUtilities,IAudioMeterInformation; print('Pycaw audio emphasis: OK')" >>"%LOG%" 2>&1
if errorlevel 1 (
  %PY% -m pip install -r requirements_audio_emphasis_optional.txt >>"%LOG%" 2>&1
  if errorlevel 1 echo WARNING: Optional audio emphasis unavailable.>>"%LOG%"
)

echo [7/8] Verifying CURRENT build...
if not exist "%MAIN%" goto NOMAIN
%PY% -m py_compile "%MAIN%" "limbus_netease_native.py" >>"%LOG%" 2>&1
if errorlevel 1 goto FAIL

echo [8/8] Starting CURRENT build...
%PY% -u "%MAIN%" >>"%LOG%" 2>&1
set "EC=%ERRORLEVEL%"
echo Program exit code: %EC%>>"%LOG%"
if "%EC%"=="0" goto END_OK
goto FAIL_RUNTIME

:NOMAIN
echo Main file was not found: %MAIN%>>"%LOG%"
echo Main file was not found: %MAIN%
goto SHOWFAIL
:NOPY
echo Python was not found.>>"%LOG%"
echo Python was not found. This source build still requires Python.
goto SHOWFAIL
:FAIL
echo Required setup step failed.>>"%LOG%"
echo Required setup step failed.
goto SHOWFAIL
:FAIL_RUNTIME
echo LimbusLyric exited unexpectedly with code %EC%.
goto SHOWFAIL
:SHOWFAIL
echo.
echo ===== startup_console.log =====
type "%LOG%"
echo.
echo Send startup_console.log and LimbusLyric_error.log if the program still fails.
pause
exit /b 1
:END_OK
endlocal
exit /b 0
