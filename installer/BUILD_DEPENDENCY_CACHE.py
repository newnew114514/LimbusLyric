from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

REQS = (
    'installer/requirements_build.txt',
    'requirements_core.txt',
    'requirements_optional_sync.txt',
    'requirements_word_timing_optional.txt',
    'requirements_audio_emphasis_optional.txt',
    'requirements_netease_native.txt',
)
STAMP = '.build_installer_venv_ascii/.dependency_fingerprint.json'
REQUIRED_MODULES = ('PyInstaller', 'PyQt5', 'requests', 'cloudmusic_detector')


def fingerprint(root: Path) -> dict:
    h = hashlib.sha256()
    for rel in REQS:
        p = root / rel
        h.update(rel.encode('utf-8')); h.update(b'\0'); h.update(p.read_bytes()); h.update(b'\0')
    return {
        'schema': 1,
        'python': f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}',
        'requirements_sha256': h.hexdigest(),
    }


def main() -> int:
    if len(sys.argv) != 3 or sys.argv[2] not in ('--check','--write'):
        raise SystemExit('usage: BUILD_DEPENDENCY_CACHE.py <root> --check|--write')
    root = Path(sys.argv[1]).resolve(); stamp = root / STAMP
    current = fingerprint(root)
    if sys.argv[2] == '--write':
        stamp.write_text(json.dumps(current, ensure_ascii=True, sort_keys=True) + '\n', encoding='ascii')
        print('BUILD DEPENDENCY CACHE: fingerprint written ' + current['requirements_sha256'][:16])
        return 0
    try:
        saved = json.loads(stamp.read_text(encoding='ascii'))
    except Exception:
        print('BUILD DEPENDENCY CACHE: MISS (no valid fingerprint)')
        return 1
    if saved == current:
        missing = [name for name in REQUIRED_MODULES if importlib.util.find_spec(name) is None]
        if missing:
            print('BUILD DEPENDENCY CACHE: MISS (environment incomplete: ' + ', '.join(missing) + ')')
            return 1
        print('BUILD DEPENDENCY CACHE: HIT ' + current['requirements_sha256'][:16])
        return 0
    print('BUILD DEPENDENCY CACHE: MISS (requirements/Python changed)')
    return 1

if __name__ == '__main__':
    raise SystemExit(main())
