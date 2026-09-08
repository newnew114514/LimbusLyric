from __future__ import annotations

import hashlib
import sys
import zipfile
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 3:
        print('usage: BUILD_PORTABLE_ZIP.py <source-folder> <output.zip>')
        return 2
    src = Path(sys.argv[1]).resolve()
    out = Path(sys.argv[2]).resolve()
    if not src.is_dir():
        print(f'portable source folder missing: {src}')
        return 3
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(out.suffix + '.tmp')
    try:
        tmp.unlink(missing_ok=True)
        with zipfile.ZipFile(
            tmp,
            'w',
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=1,
            allowZip64=True,
        ) as zf:
            base = src.parent
            for path in sorted(src.rglob('*'), key=lambda p: str(p).casefold()):
                if path.is_file():
                    zf.write(path, path.relative_to(base))
        tmp.replace(out)
    finally:
        tmp.unlink(missing_ok=True)
    h = hashlib.sha256()
    with out.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            h.update(chunk)
    digest = h.hexdigest()
    out.with_name(out.name + '.sha256.txt').write_text(
        f'{digest}  {out.name}\n', encoding='ascii'
    )
    print(f'Portable ZIP: {out}')
    print(f'SHA256: {digest}  {out.name}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
