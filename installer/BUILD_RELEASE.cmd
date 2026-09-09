@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0\.."
title LimbusLyric Installer + Portable Builder

rem This is the proven Unicode-path workaround from the previous successful
rem installer build. PyQt/PyInstaller discovery can mis-handle non-ASCII build
rem paths, so map the project to a temporary ASCII-only drive letter.
set "REALROOT=%CD%"
set "BUILDDRIVE="
for %%D in (Z Y X W V U T S R Q P O N M L K J I H G F E) do (
  if not defined BUILDDRIVE if not exist %%D:\NUL set "BUILDDRIVE=%%D:"
)
if not defined BUILDDRIVE goto NOSUBST

subst %BUILDDRIVE% "%REALROOT%" >nul 2>&1
if errorlevel 1 goto NOSUBST

set "ROOT=%BUILDDRIVE%"
cd /d "%ROOT%\"
set "BUILDVENV=%ROOT%\.build_installer_venv_ascii"
set "DIST=%ROOT%\dist"
set "RELEASE=%ROOT%\installer\release"
set "PORTABLE=LimbusLyric_Portable_1.8.9.135.zip"
set "SETUPNAME=LimbusLyric_Setup_1.8.9.135.exe"

echo ============================================================
echo   LimbusLyric - Build installer + portable Sandbox package
echo ============================================================
echo Project path : %REALROOT%
echo Build alias  : %ROOT%\
echo BetterNCM    : NOT bundled
echo Native NCM   : bundled via netease-cloudmusic-detector
echo Session logs : %%LOCALAPPDATA%%\LimbusLyric\logs  ^(app-folder fallback only^)
echo.

set "PY="
where py >nul 2>&1
if not errorlevel 1 (
  py -3.12 -c "import sys; raise SystemExit(0 if sys.version_info[:2]==(3,12) else 1)" >nul 2>&1
  if not errorlevel 1 set "PY=py -3.12"
)
if not defined PY (
  where python >nul 2>&1
  if errorlevel 1 goto NOPY
  python -c "import sys; raise SystemExit(0 if sys.version_info[:2]==(3,12) else 1)" >nul 2>&1
  if errorlevel 1 goto BADPY
  set "PY=python"
)

if exist "%BUILDVENV%\Scripts\python.exe" (
  "%BUILDVENV%\Scripts\python.exe" -c "import sys; raise SystemExit(0 if sys.version_info[:2]==(3,12) else 1)" >nul 2>&1
  if errorlevel 1 (
    echo       Existing build venv is not Python 3.12. Recreating it...
    rmdir /s /q "%BUILDVENV%" >nul 2>&1
  )
)

if /i "%LIMBUSLYRIC_RESUME_AFTER_H29_GATE_FIX%"=="1" if not exist "%BUILDVENV%\Scripts\python.exe" goto NORESUMEVENV

if not exist "%BUILDVENV%\Scripts\python.exe" (
  echo [1/10] Creating isolated ASCII-path Python 3.12 build environment...
  %PY% -m venv "%BUILDVENV%" || goto FAIL
) else (
  echo [1/10] Validating reusable ASCII-path Python 3.12 build environment...
  "%BUILDVENV%\Scripts\python.exe" -m pip --version >nul 2>&1
  if errorlevel 1 (
    echo       Existing build venv has no working pip. Attempting ensurepip repair...
    "%BUILDVENV%\Scripts\python.exe" -m ensurepip --upgrade >nul 2>&1
    "%BUILDVENV%\Scripts\python.exe" -m pip --version >nul 2>&1
    if errorlevel 1 (
      echo       Repair failed. Recreating build venv from scratch...
      cd /d "%ROOT%\"
      rmdir /s /q "%BUILDVENV%" >nul 2>&1
      %PY% -m venv "%BUILDVENV%" || goto FAIL
    ) else (
      echo       Build venv pip repair PASSED.
    )
  ) else (
    echo       Reusable build venv validation PASSED.
  )
)

set "BPY=%BUILDVENV%\Scripts\python.exe"

rem Do not let validation/import steps repopulate project-source __pycache__.
set "PYTHONDONTWRITEBYTECODE=1"
rem Gate concurrency must be tuned for the actual Windows build machine.  The old
rem fixed value of 2 was only appropriate for a constrained CI/sandbox and made a
rem 204-gate local release unnecessarily slow.
if not defined LIMBUSLYRIC_GATE_WORKERS (
  set "LIMBUSLYRIC_GATE_WORKERS=2"
  if %NUMBER_OF_PROCESSORS% GEQ 8 set "LIMBUSLYRIC_GATE_WORKERS=4"
  if %NUMBER_OF_PROCESSORS% GEQ 12 set "LIMBUSLYRIC_GATE_WORKERS=6"
  if %NUMBER_OF_PROCESSORS% GEQ 16 set "LIMBUSLYRIC_GATE_WORKERS=8"
)
echo Gate workers : %LIMBUSLYRIC_GATE_WORKERS%  ^(logical CPUs=%NUMBER_OF_PROCESSORS%^)

rem Never depend on Scripts\pip.exe existing. The canonical path is python -m pip.
"%BPY%" -m pip --version >nul 2>&1
if errorlevel 1 (
  echo ERROR: Build venv still has no working pip after validation/rebuild.
  goto FAIL
)

echo [preflight] Cleaning source caches and checking release metadata before dependency install...
"%BPY%" "%ROOT%\installer\CLEAN_PROJECT_PYTHON_CACHE.py" "%ROOT%" || goto FAIL
"%BPY%" "%ROOT%\installer\PREFLIGHT_RELEASE_METADATA.py" "%ROOT%" "%ROOT%\LimbusLyric_v1.8.9.133_CROSS_PROVIDER_TRANSLATION_CUSTOM_ADAPTER_FOUNDATION_20260814.py" || goto FAIL
echo       One-click metadata/structure preflight PASSED.

if /i not "%LIMBUSLYRIC_RESUME_AFTER_H29_GATE_FIX%"=="1" (
  set "GATES_REUSED=0"
  if /i not "%LIMBUSLYRIC_FORCE_GATES%"=="1" (
    "%BPY%" "%ROOT%\installer\BUILD_RELEASE_GATE_CACHE.py" "%ROOT%" --check
    if not errorlevel 1 set "GATES_REUSED=1"
  )
  if "!GATES_REUSED!"=="1" (
    echo [gate-preflight] Verified source is unchanged since the last successful 204-gate run; skipping replay.
  ) else (
    echo [gate-preflight] Running canonical release gates BEFORE dependency install...
    echo       Started at !TIME! with !LIMBUSLYRIC_GATE_WORKERS! worker^(s^).
    "%BPY%" "%ROOT%\installer\RUN_RELEASE_GATE_SUITE.py" "%ROOT%" "%ROOT%\LimbusLyric_v1.8.9.133_CROSS_PROVIDER_TRANSLATION_CUSTOM_ADAPTER_FOUNDATION_20260814.py" || goto FAIL
    "%BPY%" "%ROOT%\installer\BUILD_RELEASE_GATE_CACHE.py" "%ROOT%" --write || goto FAIL
    echo       Canonical release gates PASSED at !TIME!; cache saved for unchanged rebuilds.
  )
  set "LIMBUSLYRIC_RELEASE_GATES_PASSED=1"
)

if /i "%LIMBUSLYRIC_RESUME_AFTER_H29_GATE_FIX%"=="1" (
  echo [2/10] RESUME: Reusing the dependency environment from the failed H42/H42P1 build...
  echo       Dependency reinstall skipped; step [5/10] will re-verify the pinned runtime profile/imports.
) else (
  echo [2/10] Checking reusable build/runtime dependencies...
  set "DEPS_REUSED=0"
  "%BPY%" "%ROOT%\installer\BUILD_DEPENDENCY_CACHE.py" "%ROOT%" --check >nul 2>&1
  if not errorlevel 1 set "DEPS_REUSED=1"
  if "!DEPS_REUSED!"=="1" (
    echo       Dependency fingerprint unchanged and environment healthy; reusing installed environment.
  ) else (
    echo       Dependency cache miss; installing build/runtime dependencies...
if /i "%LIMBUSLYRIC_OFFLINE_BUILD%"=="1" (
  set "WHEELHOUSE=%ROOT%\installer\offline_cache\wheels"
  if not exist "!WHEELHOUSE!" goto NOOFFLINECACHE
  echo       OFFLINE mode: pip is restricted to local wheel cache.
  "%BPY%" -m pip install --no-index --find-links="!WHEELHOUSE!" -r "%ROOT%\installer\requirements_build.txt" || goto FAIL
  "%BPY%" -m pip install --no-index --find-links="!WHEELHOUSE!" -r "%ROOT%\requirements_core.txt" || goto FAIL
  "%BPY%" -m pip install --no-index --find-links="!WHEELHOUSE!" -r "%ROOT%\requirements_optional_sync.txt" || goto FAIL
  "%BPY%" -m pip install --no-index --find-links="!WHEELHOUSE!" -r "%ROOT%\requirements_word_timing_optional.txt" || goto FAIL
  "%BPY%" -m pip install --no-index --find-links="!WHEELHOUSE!" -r "%ROOT%\requirements_audio_emphasis_optional.txt" || goto FAIL
  "%BPY%" -m pip install --no-index --find-links="!WHEELHOUSE!" -r "%ROOT%\requirements_netease_native.txt" || goto FAIL
) else (
  "%BPY%" -m pip install --upgrade pip setuptools wheel || goto FAIL
  "%BPY%" -m pip install -r "%ROOT%\requirements_core.txt" || goto FAIL
  "%BPY%" -m pip install -r "%ROOT%\requirements_optional_sync.txt" || goto FAIL
  "%BPY%" -m pip install -r "%ROOT%\requirements_word_timing_optional.txt" || goto FAIL
  "%BPY%" -m pip install -r "%ROOT%\requirements_audio_emphasis_optional.txt" || goto FAIL
  "%BPY%" -m pip install -r "%ROOT%\requirements_netease_native.txt" || goto FAIL
  "%BPY%" -m pip install -r "%ROOT%\installer\requirements_build.txt" || goto FAIL
)
  "%BPY%" "%ROOT%\installer\BUILD_DEPENDENCY_CACHE.py" "%ROOT%" --write || goto FAIL
  )
)

echo [3/10] Cleaning project Python cache...
"%BPY%" "%ROOT%\installer\CLEAN_PROJECT_PYTHON_CACHE.py" "%ROOT%" || goto FAIL
if /i "%LIMBUSLYRIC_RESUME_AFTER_H29_GATE_FIX%"=="1" (
  echo [4/10] RESUME: Rechecking the bounded H29/H42/H43 compatibility set...
  "%BPY%" "%ROOT%\installer\RUN_RELEASE_RESUME_VALIDATION.py" "%ROOT%" "%ROOT%\LimbusLyric_v1.8.9.133_CROSS_PROVIDER_TRANSLATION_CUSTOM_ADAPTER_FOUNDATION_20260814.py" || goto FAIL
  echo       Resume validation PASSED through the aggregate runner.
) else (
  echo [4/10] Release-gate suite already passed in the cheap pre-dependency stage.
  if not "%LIMBUSLYRIC_RELEASE_GATES_PASSED%"=="1" goto FAIL
)

echo [5/10] Verifying pinned runtime profile, imports, pywin32 MFC, and Qt plugin path...
"%BPY%" "%ROOT%\installer\VERIFY_BUILD_RUNTIME_PROFILE.py" || goto FAIL
"%BPY%" -c "import os,site,PyQt5,win32ui,win32gui,requests,pywinauto,comtypes,cloudmusic_detector; import limbus_netease_native; from pathlib import Path; from PyQt5.QtCore import QLibraryInfo; p=Path(QLibraryInfo.location(QLibraryInfo.PluginsPath)); print('QtPlugins='+str(p)); assert p.is_dir(), 'Qt plugin directory missing: '+str(p); roots=[Path(x) for x in site.getsitepackages()]; mfc=[q for r in roots if r.exists() for q in r.rglob('mfc140u.dll')]; assert mfc, 'pywin32 mfc140u.dll missing - pywin32 312 regression?'; print('MFC='+str(mfc[0])); from Crypto.Cipher import AES,DES3; from pycaw.pycaw import AudioUtilities; import winrt.windows.foundation,winrt.windows.foundation.collections; from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionManager; print('NetEaseDetector='+getattr(cloudmusic_detector,'__file__','?'))" || goto FAIL

echo [6/10] Building self-contained application folder...  !TIME!
if exist "%DIST%\LimbusLyric" rmdir /s /q "%DIST%\LimbusLyric"
set "LIMBUSLYRIC_SOURCE_ROOT=%ROOT%"
set "PYI_CLEAN="
if /i "%LIMBUSLYRIC_CLEAN_BUILD%"=="1" set "PYI_CLEAN=--clean"
if defined PYI_CLEAN (echo       PyInstaller cache policy: CLEAN) else (echo       PyInstaller cache policy: INCREMENTAL ^(set LIMBUSLYRIC_CLEAN_BUILD=1 to force clean^))
"%BPY%" -m PyInstaller --noconfirm %PYI_CLEAN% --distpath "%DIST%" --workpath "%ROOT%\.pyinstaller_work" "%ROOT%\installer\LimbusLyric.spec" || goto FAIL
if not exist "%DIST%\LimbusLyric\LimbusLyric.exe" goto FAIL

echo [7/10] Running frozen-runtime smoke test...  !TIME!
set "SMOKE=%ROOT%\installer\PACKAGING_SMOKE_RESULT.txt"
if exist "%SMOKE%" del /q "%SMOKE%" >nul 2>&1
set "LIMBUSLYRIC_PACKAGING_SMOKE_RESULT=%SMOKE%"
start "" /wait "%DIST%\LimbusLyric\LimbusLyric.exe" --packaging-smoke-test
set "SMOKE_EC=!ERRORLEVEL!"
set "LIMBUSLYRIC_PACKAGING_SMOKE_RESULT="
if not exist "%SMOKE%" (
  echo ERROR: Frozen smoke test did not create a result file.
  goto FAIL
)
type "%SMOKE%"
findstr /b /c:"FAIL " "%SMOKE%" >nul 2>&1
if not errorlevel 1 (
  echo ERROR: Frozen runtime dependency smoke test FAILED.
  goto FAIL
)
if not "!SMOKE_EC!"=="0" (
  echo ERROR: Frozen smoke test exit code !SMOKE_EC!.
  goto FAIL
)
echo Frozen runtime dependency smoke test PASSED.

rem These are convenience/diagnostic files only. The EXE itself does not need them.
copy /y "%ROOT%\OPEN_LOG_FOLDER.cmd" "%DIST%\LimbusLyric\OPEN_LOG_FOLDER.cmd" >nul 2>&1
copy /y "%ROOT%\README_DIAGNOSTIC_RC.txt" "%DIST%\LimbusLyric\README_DIAGNOSTIC_RC.txt" >nul 2>&1

echo [8/10] Writing build manifest...
"%BPY%" -m pip freeze > "%DIST%\LimbusLyric\PYTHON_PACKAGES_BUILD.txt"
> "%DIST%\LimbusLyric\BUILD_INFO.txt" echo LimbusLyric 1.8.9.135 Release
>>"%DIST%\LimbusLyric\BUILD_INFO.txt" echo Built=%DATE% %TIME%
>>"%DIST%\LimbusLyric\BUILD_INFO.txt" echo BetterNCMBundled=0
>>"%DIST%\LimbusLyric\BUILD_INFO.txt" echo NetEaseNativeDefault=1
>>"%DIST%\LimbusLyric\BUILD_INFO.txt" echo SessionLogs=%%LOCALAPPDATA%%\LimbusLyric\logs ^(app-folder fallback only^)
"%BPY%" -c "import sys,platform,cloudmusic_detector; print('Python='+sys.version.replace(chr(10),' ')); print('Platform='+platform.platform()); print('cloudmusic_detector='+str(getattr(cloudmusic_detector,'__file__','?')))" >> "%DIST%\LimbusLyric\BUILD_INFO.txt"
"%BPY%" "%ROOT%\installer\VERIFY_BUILD_RUNTIME_PROFILE.py" >> "%DIST%\LimbusLyric\BUILD_INFO.txt"

set "ISCC="
for %%I in (
  "%ProgramFiles(x86)%\Inno Setup 7\ISCC.exe"
  "%ProgramFiles%\Inno Setup 7\ISCC.exe"
  "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
  "%ProgramFiles%\Inno Setup 6\ISCC.exe"
  "%LOCALAPPDATA%\Programs\Inno Setup 7\ISCC.exe"
  "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
) do if exist %%I set "ISCC=%%~I"
if not defined ISCC goto NOISCC

if exist "%RELEASE%" rmdir /s /q "%RELEASE%"
mkdir "%RELEASE%"

echo [9/10] Building Setup.exe with Inno Setup...  !TIME!
"%ISCC%" "%ROOT%\installer\LimbusLyric_Setup.iss" || goto FAIL
if not exist "%RELEASE%\!SETUPNAME!" goto FAIL

echo [10/10] Creating fast portable ZIP and SHA256 files...  !TIME!
"%BPY%" "%ROOT%\installer\BUILD_PORTABLE_ZIP.py" "%DIST%\LimbusLyric" "%RELEASE%\!PORTABLE!" || goto FAIL
for %%F in ("%RELEASE%\!SETUPNAME!") do (
  powershell.exe -NoLogo -NoProfile -Command "$h=(Get-FileHash -LiteralPath '%%~fF' -Algorithm SHA256).Hash.ToLowerInvariant(); $h + '  ' + '%%~nxF' | Set-Content -LiteralPath '%%~fF.sha256.txt' -Encoding ascii; Write-Host ('SHA256: ' + $h + '  %%~nxF')" || goto FAIL
)
echo       Packaging finished at !TIME!.

set "FINALRELEASE=%REALROOT%\installer\release"
call :UNMAP

echo.
echo SUCCESS.
echo Installer:
echo   !FINALRELEASE!\!SETUPNAME!
echo Portable Sandbox ZIP:
echo   !FINALRELEASE!\!PORTABLE!
echo.
echo Target PCs / Sandbox do NOT need Python or BetterNCM.
echo Logs are written per launch under:
echo   %%LOCALAPPDATA%%\LimbusLyric\logs  ^(app-folder fallback only^)
pause
exit /b 0

:NORESUMEVENV
call :UNMAP
echo ERROR: Resume mode needs the existing .build_installer_venv_ascii from the failed build.
echo Use the fast-resume patch on the SAME project folder that just failed at H29.
pause
exit /b 7

:NOPY
call :UNMAP
echo ERROR: The BUILD machine needs Python 3.12.x. Target machines do NOT.
pause
exit /b 2

:BADPY
call :UNMAP
echo ERROR: LimbusLyric audited builds require Python 3.12.x on the BUILD machine.
echo Install Python 3.12 or make ^"py -3.12^" available, then run this builder again.
pause
exit /b 6

:NOISCC
set "FINALDIST=%REALROOT%\dist\LimbusLyric"
call :UNMAP
echo ERROR: Inno Setup compiler ISCC.exe was not found.
echo The self-contained portable app was still built at:
echo   !FINALDIST!
echo You may copy that whole folder into Windows Sandbox now.
pause
exit /b 3

:NOOFFLINECACHE
call :UNMAP
echo ERROR: Offline build requested but installer\offline_cache\wheels is missing/incomplete.
echo Run PREPARE_OFFLINE_BUILD_CACHE.cmd while online first.
pause
exit /b 4

:NOSUBST
echo ERROR: Could not allocate a temporary ASCII-only drive letter for the build.
pause
exit /b 5

:FAIL
call :UNMAP
echo.
echo BUILD FAILED. See output above. Existing logs/build files were not deleted.
pause
exit /b 1

:UNMAP
if defined BUILDDRIVE subst %BUILDDRIVE% /d >nul 2>&1
exit /b 0
