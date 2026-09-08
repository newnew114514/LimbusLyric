from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

STAMP_REL = Path('.build_installer_venv_ascii') / '.release_gate_fingerprint.json'
MANIFEST = 'SHA256_FILES.txt'
SUITE = Path('installer') / 'RELEASE_GATE_SUITE.tsv'


def fingerprint(root: Path) -> dict[str, object]:
    manifest = root / MANIFEST
    suite = root / SUITE
    if not manifest.is_file() or not suite.is_file():
        raise FileNotFoundError('release manifest/gate suite missing')
    h = hashlib.sha256()
    # PREFLIGHT_RELEASE_METADATA verifies SHA256_FILES.txt against the full source
    # payload before this helper runs.  Therefore hashing the verified manifest is
    # equivalent to keying the cache on every audited source file, while being fast.
    h.update(manifest.read_bytes())
    h.update(b'\0release-suite\0')
    h.update(suite.read_bytes())
    return {
        'schema': 1,
        'python': f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}',
        'verified_source_sha256': h.hexdigest(),
    }


def main() -> int:
    if len(sys.argv) != 3 or sys.argv[2] not in ('--check', '--write'):
        print('usage: BUILD_RELEASE_GATE_CACHE.py <root> --check|--write')
        return 2
    root = Path(sys.argv[1]).resolve()
    stamp = root / STAMP_REL
    current = fingerprint(root)
    if sys.argv[2] == '--write':
        stamp.parent.mkdir(parents=True, exist_ok=True)
        stamp.write_text(json.dumps(current, sort_keys=True) + '\n', encoding='ascii')
        print('RELEASE GATE CACHE: fingerprint written ' + str(current['verified_source_sha256'])[:16])
        return 0
    try:
        saved = json.loads(stamp.read_text(encoding='ascii'))
    except Exception:
        print('RELEASE GATE CACHE: MISS (no prior successful full gate run)')
        return 1
    if saved == current:
        print('RELEASE GATE CACHE: HIT ' + str(current['verified_source_sha256'])[:16])
        return 0
    print('RELEASE GATE CACHE: MISS (audited source/gates/Python changed)')
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
