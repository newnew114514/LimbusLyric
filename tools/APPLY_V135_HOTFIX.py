from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / 'LimbusLyric_v1.8.9.133_CROSS_PROVIDER_TRANSLATION_CUSTOM_ADAPTER_FOUNDATION_20260814.py'
BASE_SHA256 = '1009f109adf579ad49455652bcbbbb02940268667eb83e89dce36f53a9ae48fa'
HOTFIX_MARKER = 'V135 TRANSLATION OWNERSHIP HOTFIX'
PATCHED_MAIN_SHA256 = 'fc6dedb8761c7aea81aefc68bb34fa6bdf333b7ff15db7e2a2bc181cd363b53f'


def normalized_text_sha256(path: Path, encoding: str = 'utf-8') -> str:
    text = path.read_text(encoding=encoding)
    normalized = '\n'.join(text.splitlines()).rstrip() + '\n'
    return hashlib.sha256(normalized.encode(encoding)).hexdigest()


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'V135 HOTFIX: expected exactly one {label}, found {count}')
    return text.replace(old, new, 1)


def patch_main(text: str) -> str:
    if HOTFIX_MARKER in text:
        return text

    text = replace_once(
        text,
        'LIMBUSLYRIC_BUILD_TAG = "v1.8.9.134 RELEASE ',
        f'LIMBUSLYRIC_BUILD_TAG = "v1.8.9.135 RELEASE {HOTFIX_MARKER} + ',
        'build tag',
    )
    text = replace_once(text, "cur='1.8.9.134 H12'", "cur='1.8.9.135 H13'", 'updater current version')
    text = replace_once(text, "base = m.group(1) if m else '1.8.9.134'", "base = m.group(1) if m else '1.8.9.135'", 'version fallback')
    text = replace_once(text, "QLabel('当前版本  ·  v1.8.9.134', card)", "QLabel('当前版本  ·  v1.8.9.135', card)", 'about version label')

    old = '''    # If a previous song had no payload for the user's persistent mode, a later successful\n    # current transaction must release that presentation block *before* the legacy result\n    # handler calls _launch_current_lyrics(). Otherwise the new valid payload is loaded but\n    # our ownership guard would still keep the overlay blank.\n    mode_block_before = bool(getattr(self, '_limbus_mode_payload_blocked', False))\n    mode_reason_before = str(getattr(self, '_limbus_mode_payload_block_reason', '') or '')\n    if was_current and result.get('lyric'):\n        self._limbus_mode_payload_blocked = False\n        self._limbus_mode_payload_block_reason = ''\n    out = _LIMBUS_AUTO_LYRIC_RESULT_PRE_H11(self, result)\n'''
    new = '''    # If a previous song had no payload for the user's persistent mode, a later successful\n    # current transaction must release *all presentation ownership barriers before* the legacy\n    # result handler calls _launch_current_lyrics().  R9.2 only released the semantic-mode\n    # block here; the previous track's failed-key/suspension state was cleared after launch,\n    # so a valid translation payload for the next song could be loaded and immediately hidden.\n    # Snapshot the old ownership state and restore it only when the legacy apply did not bind\n    # the successful payload to the current track.\n    mode_block_before = bool(getattr(self, '_limbus_mode_payload_blocked', False))\n    mode_reason_before = str(getattr(self, '_limbus_mode_payload_block_reason', '') or '')\n    ownership_before = None\n    if was_current and result.get('lyric'):\n        ownership_before = (\n            bool(getattr(self, '_auto_overlay_suspended', False)),\n            str(getattr(self, '_auto_suspended_loaded_key', '') or ''),\n            str(getattr(self, '_auto_failed_track_key', '') or ''),\n            float(getattr(self, '_auto_failed_until', 0.0) or 0.0),\n        )\n        self._limbus_mode_payload_blocked = False\n        self._limbus_mode_payload_block_reason = ''\n        self._auto_overlay_suspended = False\n        self._auto_suspended_loaded_key = ''\n        self._auto_failed_track_key = ''\n        self._auto_failed_until = 0.0\n    out = _LIMBUS_AUTO_LYRIC_RESULT_PRE_H11(self, result)\n'''
    text = replace_once(text, old, new, 'pre-launch ownership release')

    old2 = '''        if not applied_current and mode_block_before:\n            self._limbus_mode_payload_blocked = True\n            self._limbus_mode_payload_block_reason = mode_reason_before\n'''
    new2 = '''        if not applied_current:\n            if mode_block_before:\n                self._limbus_mode_payload_blocked = True\n                self._limbus_mode_payload_block_reason = mode_reason_before\n            if ownership_before is not None:\n                (\n                    self._auto_overlay_suspended,\n                    self._auto_suspended_loaded_key,\n                    self._auto_failed_track_key,\n                    self._auto_failed_until,\n                ) = ownership_before\n'''
    text = replace_once(text, old2, new2, 'failed-apply ownership restoration')
    return text


def patch_simple(path: Path, replacements: list[tuple[str, str, str]]) -> None:
    encoding = 'utf-8-sig' if path.suffix.lower() == '.iss' else 'utf-8'
    text = path.read_text(encoding=encoding)
    original = text
    for old, new, label in replacements:
        if old in text:
            text = text.replace(old, new)
        elif new not in text:
            raise SystemExit(f'V135 HOTFIX: {path}: missing {label}')
    if text != original:
        path.write_text(text, encoding=encoding, newline='\n')


def apply() -> None:
    if not MAIN.is_file():
        raise SystemExit(f'V135 HOTFIX: main source missing: {MAIN}')

    text = MAIN.read_text(encoding='utf-8')
    already = HOTFIX_MARKER in text
    base_hash = normalized_text_sha256(MAIN)
    if not already and base_hash != BASE_SHA256:
        raise SystemExit(f'V135 HOTFIX: unexpected normalized base source SHA256 {base_hash}')

    patched = patch_main(text)
    if patched != text:
        MAIN.write_text(patched, encoding='utf-8', newline='\n')

    files: dict[Path, list[tuple[str, str, str]]] = {
        ROOT / 'installer' / 'LimbusLyric_Setup.iss': [
            ('#define MyAppVersion "1.8.9.134"', '#define MyAppVersion "1.8.9.135"', 'Inno version'),
            ('#define MyOutputBase "LimbusLyric_Setup_1.8.9.134"', '#define MyOutputBase "LimbusLyric_Setup_1.8.9.135"', 'Inno output'),
        ],
        ROOT / 'installer' / 'BUILD_RELEASE.cmd': [
            ('LimbusLyric_Portable_1.8.9.134.zip', 'LimbusLyric_Portable_1.8.9.135.zip', 'portable name'),
            ('LimbusLyric_Setup_1.8.9.134.exe', 'LimbusLyric_Setup_1.8.9.135.exe', 'setup name'),
            ('LimbusLyric 1.8.9.134 Release', 'LimbusLyric 1.8.9.135 Release', 'build info'),
        ],
        ROOT / 'REPACKAGE_SETUP_ONLY.cmd': [
            ('LimbusLyric_Setup_1.8.9.134.exe', 'LimbusLyric_Setup_1.8.9.135.exe', 'repackage setup name'),
        ],
        ROOT / 'installer' / 'CHECK_PACKAGING_CONTRACT.py': [
            ('LimbusLyric_Setup_1.8.9.134', 'LimbusLyric_Setup_1.8.9.135', 'packaging contract version'),
        ],
        ROOT / 'installer' / 'CHECK_RELEASE_INVARIANTS.py': [
            ('LimbusLyric_Setup_1.8.9.134', 'LimbusLyric_Setup_1.8.9.135', 'release setup invariant'),
            ('LimbusLyric_Portable_1.8.9.134.zip', 'LimbusLyric_Portable_1.8.9.135.zip', 'release portable invariant'),
            ('Inno output not v1.8.9.134', 'Inno output not v1.8.9.135', 'release invariant message'),
        ],
        ROOT / 'installer' / 'CHECK_MAIN_SOURCE_LOCK.py': [
            (f'EXPECTED = "{BASE_SHA256}"', f'EXPECTED = "{PATCHED_MAIN_SHA256}"', 'main source lock'),
        ],
        ROOT / 'installer' / 'LimbusLyric.spec': [
            ('LimbusLyric 1.8.9.133 diagnostic RC', 'LimbusLyric 1.8.9.135 hotfix release', 'spec description'),
        ],
    }
    for path, replacements in files.items():
        patch_simple(path, replacements)

    sys.path.insert(0, str(ROOT / 'installer'))
    from SOURCE_MANIFEST import regenerate_manifest
    regenerate_manifest(ROOT)
    verify()


def verify() -> None:
    text = MAIN.read_text(encoding='utf-8')
    required = [
        'v1.8.9.135 RELEASE V135 TRANSLATION OWNERSHIP HOTFIX',
        "cur='1.8.9.135 H13'",
        "QLabel('当前版本  ·  v1.8.9.135', card)",
        'ownership_before = None',
        '+ QQ MODERN SEARCH + COVER DIRECT-ID R9.2',
    ]
    for token in required:
        if token not in text:
            raise SystemExit(f'V135 HOTFIX VERIFY: missing token: {token[:80]}')
    actual = normalized_text_sha256(MAIN)
    if actual != PATCHED_MAIN_SHA256:
        raise SystemExit(f'V135 HOTFIX VERIFY: patched main SHA mismatch {actual}')
    iss = (ROOT / 'installer' / 'LimbusLyric_Setup.iss').read_text(encoding='utf-8-sig')
    if '1.8.9.135' not in iss or 'LimbusLyric_Setup_1.8.9.135' not in iss:
        raise SystemExit('V135 HOTFIX VERIFY: Inno metadata not updated')
    print('V135 HOTFIX VERIFY: PASS')
    print(f'  normalized_main_sha256={actual}')
    print('  R9.2 retained: QQ modern search + cover direct-ID')
    print('  next-track translation ownership barrier released before launch')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    verify() if args.check else apply()


if __name__ == '__main__':
    main()
