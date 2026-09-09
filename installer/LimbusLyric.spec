# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller one-folder build for LimbusLyric 1.8.9.135 hotfix release.

Build on 64-bit Windows. The resulting dist/LimbusLyric folder contains its
own Python runtime and all ordinary runtime dependencies. Target PCs and
Windows Sandbox do not need Python, pip, BetterNCM, or administrator rights.
"""
from pathlib import Path
import os
import sys
from PyInstaller.utils.hooks import collect_submodules, collect_dynamic_libs, collect_data_files

ROOT = Path(os.environ.get('LIMBUSLYRIC_SOURCE_ROOT') or Path(SPECPATH).parent).resolve()
MAIN = ROOT / 'LimbusLyric_v1.8.9.133_CROSS_PROVIDER_TRANSLATION_CUSTOM_ADAPTER_FOUNDATION_20260814.py'
ICON = ROOT / 'xiaofen.ico'

if not MAIN.is_file():
    raise SystemExit(f'LimbusLyric main script not found: {MAIN}')
if not ICON.is_file():
    raise SystemExit(f'LimbusLyric icon not found: {ICON}')

hiddenimports = [
    'pythoncom', 'pywintypes', 'win32timezone', 'win32ui', 'win32gui', 'win32api',
    'winrt.windows.foundation',
    'winrt.windows.foundation.collections',
    'winrt.windows.media.control',
    'Crypto.Cipher.AES', 'Crypto.Cipher.DES3', 'Crypto.Util.Padding',
    'pycaw.pycaw',
    'limbus_netease_native',
    'cloudmusic_detector',
]

# Packages below load modules conditionally/dynamically. Keep this deliberately
# conservative until the clean-Sandbox regression pass is complete.
for package in ('winrt', 'comtypes', 'pywinauto', 'pycaw', 'Crypto', 'cloudmusic_detector'):
    try:
        hiddenimports += collect_submodules(package)
    except Exception:
        pass

binaries = []
for package in ('winrt', 'pywin32_system32'):
    try:
        binaries += collect_dynamic_libs(package)
    except Exception:
        pass

# pywin32 312 has a published wheel regression that omits pythonwin/mfc140u.dll.
# We pin 311, but still collect MFC explicitly so the frozen app is self-contained
# and the build fails loudly if the dependency disappears again.
mfc_candidates = []
try:
    import site
    roots = [Path(p) for p in site.getsitepackages() if p]
    roots.append(Path(sys.prefix) / 'Lib' / 'site-packages')
except Exception:
    roots = [Path(sys.prefix) / 'Lib' / 'site-packages']
for root in roots:
    if not root.exists():
        continue
    try:
        mfc_candidates.extend(root.rglob('mfc140u.dll'))
    except Exception:
        pass
mfc_candidates = [p for p in mfc_candidates if p.is_file()]
if not mfc_candidates:
    raise SystemExit(
        'Required pywin32 MFC runtime mfc140u.dll was not found. '
        'Use pywin32==311; do not build this RC with pywin32 312.'
    )
binaries.append((str(mfc_candidates[0]), '.'))

datas = [(str(ICON), '.')]
support_dir = ROOT / 'support_assets'
if support_dir.is_dir():
    for asset in sorted(support_dir.iterdir()):
        if asset.is_file():
            datas.append((str(asset), 'support_assets'))
for package in ('comtypes', 'pycaw', 'cloudmusic_detector'):
    try:
        datas += collect_data_files(package)
    except Exception:
        pass

a = Analysis(
    [str(MAIN)],
    pathex=[str(ROOT)],
    binaries=binaries,
    datas=datas,
    hiddenimports=sorted(set(hiddenimports)),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=1,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='LimbusLyric',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ICON),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='LimbusLyric',
)
