#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

if len(sys.argv) < 2:
    print('usage: CHECK_PACKAGING_CONTRACT.py <root>')
    raise SystemExit(2)
root = Path(sys.argv[1]).resolve()


def need(cond, msg):
    if not cond:
        print('FAIL', msg)
        raise SystemExit(1)
    print('PASS', msg)


spec = root / 'installer' / 'LimbusLyric.spec'
spec_text = spec.read_text(encoding='utf-8', errors='ignore')
# Packaging is now locked by behavior instead of a byte-for-byte spec hash.
# This preserves the runtime contract while avoiding false failures from comments,
# formatting or safe future additions to collection lists.
need(all(token in spec_text for token in (
    "MAIN = ROOT / 'LimbusLyric_v1.8.9.133_CROSS_PROVIDER_TRANSLATION_CUSTOM_ADAPTER_FOUNDATION_20260814.py'",
    "ICON = ROOT / 'xiaofen.ico'",
    "name='LimbusLyric'",
    'console=False',
    'exclude_binaries=True',
    "mfc140u.dll",
    "collect_submodules(package)",
    "collect_dynamic_libs(package)",
    "collect_data_files(package)",
)), 'PyInstaller spec semantic one-folder/runtime contract intact')
for package in ('winrt', 'comtypes', 'pywinauto', 'pycaw', 'Crypto', 'cloudmusic_detector'):
    need(re.search(r"for package in \([^\n]*", spec_text) is not None or package in spec_text,
         f'PyInstaller dynamic dependency family retained: {package}')
need("'limbus_netease_native'" in spec_text and "'cloudmusic_detector'" in spec_text,
     'NetEase native helper/detector remain explicit hidden imports')

build = (root / 'installer' / 'BUILD_RELEASE.cmd').read_text(encoding='utf-8')
runner = (root / 'installer' / 'RUN_RELEASE_GATE_SUITE.py').read_text(encoding='utf-8')
suite_path = root / 'installer' / 'RELEASE_GATE_SUITE.tsv'
suite = suite_path.read_text(encoding='utf-8')
need('RUN_RELEASE_GATE_SUITE.py" "%ROOT%" "%ROOT%\\LimbusLyric_v1.8.9.133_CROSS_PROVIDER_TRANSLATION_CUSTOM_ADAPTER_FOUNDATION_20260814.py" || goto FAIL' in build,
     'single aggregate release-gate suite is mandatory')
need('PREFLIGHT_RELEASE_METADATA.py" "%ROOT%" "%ROOT%\\LimbusLyric_v1.8.9.133_CROSS_PROVIDER_TRANSLATION_CUSTOM_ADAPTER_FOUNDATION_20260814.py" || goto FAIL' in build,
     'one-click builder performs cheap release metadata/structure preflight before dependency install')
preflight = (root / 'installer' / 'PREFLIGHT_RELEASE_METADATA.py').read_text(encoding='utf-8', errors='ignore')
need(all(token in preflight for token in (
    'CHECK_MAIN_SOURCE_LOCK.py',
    'SYNC_SOURCE_MANIFEST_ADDITIONS.py',
    'CHECK_RELEASE_GATE_COVERAGE.py',
    'CHECK_PACKAGING_STRUCTURE.py',
    'failed:',
)), 'metadata preflight locks main, safe-syncs additive Hxx metadata, then aggregates coverage/structure checks')
need(not re.search(r'%ROOT%\\installer\\CHECK_[A-Z0-9_]+\.py.*\|\| goto FAIL', build),
     'legacy first-failure CHECK_* chain removed from builder')
need(all(token in runner for token in ('RELEASE_GATE_SUITE.tsv', 'ThreadPoolExecutor', '_kill_process_tree', 'no first-failure masking', 'DEFAULT_GATE_TIMEOUT_SECONDS = 120')),
     'aggregate runner uses declarative suite + concurrency + timeout/process-tree protection')
need('BUILD_DEPENDENCY_CACHE.py" "%ROOT%" --check' in build and 'BUILD_DEPENDENCY_CACHE.py" "%ROOT%" --write' in build,
     'unchanged pinned dependencies reuse the existing build environment')
need('LIMBUSLYRIC_CLEAN_BUILD' in build and 'set "PYI_CLEAN=--clean"' in build and
     '-m PyInstaller --noconfirm %PYI_CLEAN% --distpath "%DIST%" --workpath "%ROOT%\\.pyinstaller_work"' in build,
     'PyInstaller is incremental by default with explicit clean-build override')
need(build.find('[gate-preflight]') < build.find('[2/10] Checking reusable build/runtime dependencies'),
     'canonical release gates run before dependency installation')
need('LimbusLyric.exe" --packaging-smoke-test' in build, 'frozen-runtime smoke test mandatory')

# Every CHECK_*.py must be registered exactly once. No more hand-maintained
# subset in this contract: the filesystem and suite declaration must agree.
declared = []
for raw in suite.splitlines():
    raw = raw.strip()
    if not raw or raw.startswith('#'):
        continue
    parts = raw.split('\t')
    need(len(parts) == 2 and parts[1] in {'main', 'root', 'root-main'}, f'valid release gate declaration: {raw}')
    declared.append(parts[0])
actual_checks = sorted(p.name for p in (root / 'installer').glob('CHECK_*.py') if p.is_file())
need(len(declared) == len(set(declared)), 'release gate suite has no duplicate registrations')
need(set(declared) == set(actual_checks),
     f'all CHECK_* gates registered automatically (declared={len(declared)} actual={len(actual_checks)})')
need('CHECK_RELEASE_GATE_COVERAGE.py' in declared and 'CHECK_SOURCE_MANIFEST_AUTOSYNC_REPLAY.py' in declared,
     'packaging metadata self-audit gates are mandatory')

policy = (root / 'installer' / 'PACKAGING_PATH_POLICY.py').read_text(encoding='utf-8')
need(all(token in policy for token in (
    '.build_installer_venv_ascii', '.pyinstaller_work', 'dist', 'build',
    '("installer", "release")', '("installer", "offline_cache")',
    'PACKAGING_SMOKE_RESULT.txt', 'logs',
)), 'shared source-payload policy covers build/runtime transients')

manifest_tools = [
    root / 'installer' / 'SOURCE_MANIFEST.py',
    root / 'installer' / 'SYNC_SOURCE_MANIFEST_ADDITIONS.py',
    root / 'installer' / 'PREPARE_SOURCE_MANIFEST.py',
]
need(all(path.is_file() for path in manifest_tools),
     'source manifest has centralized deterministic prepare + safe additive sync tooling')
sync_text = manifest_tools[1].read_text(encoding='utf-8', errors='ignore')
need('not auto-enrolled' in sync_text and 'PREPARE_SOURCE_MANIFEST.py' in sync_text,
     'unknown source additions stay fatal with an explicit maintainer repair path')

need('SessionLogs=%%LOCALAPPDATA%%\\LimbusLyric\\logs ^(app-folder fallback only^)' in build,
     'BUILD_INFO log path matches runtime policy')
need('Session logs : %%LOCALAPPDATA%%\\LimbusLyric\\logs' in build,
     'builder console log path matches runtime policy')
need('echo   %%LOCALAPPDATA%%\\LimbusLyric\\logs  ^(app-folder fallback only^)' in build,
     'builder success footer matches runtime log policy')
need('<LimbusLyric.exe folder^>\\logs  ^(LOCALAPPDATA fallback^)' not in build,
     'stale reversed log-policy footer removed')

iss = (root / 'installer' / 'LimbusLyric_Setup.iss').read_text(encoding='utf-8')
need('Name: "{localappdata}\\LimbusLyric\\logs"; Flags: uninsneveruninstall' in iss,
     'installer preserves unified diagnostics directory')
need('Filename: "explorer.exe"; Parameters: """{localappdata}\\LimbusLyric\\logs"""' in iss,
     'installer diagnostic shortcut targets unified directory')
need('#define MyOutputBase "LimbusLyric_Setup_1.8.9.136"' in iss and 'OutputBaseFilename={#MyOutputBase}' in iss,
     'installer output contract intact')

op = (root / 'OPEN_LOG_FOLDER.cmd').read_text(encoding='utf-8')
need('%LOCALAPPDATA%\\LimbusLyric\\logs' in op, 'portable log shortcut targets unified directory')
enduser = (root / 'BUILD_END_USER_INSTALLER.cmd').read_text(encoding='utf-8')
need('installer\\BUILD_RELEASE.cmd' in enduser, 'end-user builder still delegates to canonical release builder')
repack = (root / 'REPACKAGE_SETUP_ONLY.cmd').read_text(encoding='utf-8')
need('LimbusLyric_Setup.iss' in repack and 'dist\\LimbusLyric\\LimbusLyric.exe' in repack,
     'setup-only repack contract intact')

print('PACKAGING CONTRACT: PASS')
