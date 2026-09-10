from __future__ import annotations

import argparse
import ast
import hashlib
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / 'LimbusLyric_v1.8.9.133_CROSS_PROVIDER_TRANSLATION_CUSTOM_ADAPTER_FOUNDATION_20260814.py'
BASE_SHA256 = 'fc6dedb8761c7aea81aefc68bb34fa6bdf333b7ff15db7e2a2bc181cd363b53f'
MARKER = 'V136 FIELD REGRESSION CLOSURE'


def normalized_text_sha256(path: Path, encoding: str = 'utf-8') -> str:
    text = path.read_text(encoding=encoding)
    normalized = '\n'.join(text.splitlines()).rstrip() + '\n'
    return hashlib.sha256(normalized.encode(encoding)).hexdigest()


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'V136 PATCH: expected exactly one {label}, found {count}')
    return text.replace(old, new, 1)


def patch_main(text: str) -> str:
    if MARKER in text:
        return text

    text = replace_once(
        text,
        'LIMBUSLYRIC_BUILD_TAG = "v1.8.9.135 RELEASE V135 TRANSLATION OWNERSHIP HOTFIX + ',
        'LIMBUSLYRIC_BUILD_TAG = "v1.8.9.136 RELEASE V136 FIELD REGRESSION CLOSURE + V135 TRANSLATION OWNERSHIP HOTFIX + ',
        'build tag',
    )
    text = replace_once(text, "cur='1.8.9.135 H13'", "cur='1.8.9.136 H14'", 'updater current version')
    text = replace_once(text, "base = m.group(1) if m else '1.8.9.135'", "base = m.group(1) if m else '1.8.9.136'", 'version fallback')
    text = replace_once(text, "QLabel('当前版本  ·  v1.8.9.135', card)", "QLabel('当前版本  ·  v1.8.9.136', card)", 'about version label')

    activation = '_r9_2_activate_network_metadata_routing()'
    block = r'''

# V136 FIELD REGRESSION CLOSURE
# Field logs from 2026-09-10 proved two narrow state-lifetime bugs that are independent
# of player clocks/render formulas: (1) a valid bilingual sidecar can be lost when the
# same main lyric payload is relaunched/restarted; (2) a semantic mode-refetch can mix a
# stale loaded song identity with a newer QQ duration during a track handoff.  Keep this
# layer presentation/transaction-only: no seek, clock, provider parser, or render formula changes.
_V136_LAUNCH_PRE = ControlPanel._launch_current_lyrics
_V136_MODE_REFETCH_PRE = ControlPanel._refetch_loaded_track_for_mode_switch


def _v136_loaded_identity(panel):
    song = str(getattr(panel, '_loaded_song', '') or '').strip()
    artist = str(getattr(panel, '_loaded_artist', '') or '').strip()
    try:
        key = str(panel._track_identity(song, artist) or '')
    except Exception:
        key = ''
    if not key:
        key = str(getattr(panel, '_loaded_track_key', '') or '')
    return key, song, artist


def _v136_mode_refetch_identity_conflict(panel):
    loaded_key, song, artist = _v136_loaded_identity(panel)
    if not loaded_key or not song:
        return ''
    media_key = ''
    try:
        media_key = str(getattr(getattr(panel, 'media_sync', None), '_track_key', '') or '')
    except Exception:
        media_key = ''
    # A bound MediaSync key is transaction evidence, not a duration heuristic.  If it has
    # already moved to another song, never combine that song's duration with the stale UI payload.
    if media_key and media_key != loaded_key:
        return media_key
    try:
        detected_song, detected_artist = panel._detected_player_track()
    except Exception:
        detected_song, detected_artist = '', ''
    detected_song = str(detected_song or '').strip()
    detected_artist = str(detected_artist or '').strip()
    if detected_song:
        try:
            same = bool(panel._same_track(song, artist, detected_song, detected_artist))
        except Exception:
            same = True
        if not same:
            try:
                return str(panel._track_identity(detected_song, detected_artist) or detected_song)
            except Exception:
                return detected_song
    return ''


def _v136_refetch_loaded_track_for_mode_switch(panel, reason='mode-switch', rollback_trans_only=None, rollback_precise=None):
    conflict = _v136_mode_refetch_identity_conflict(panel)
    if conflict:
        loaded_key, song, _artist = _v136_loaded_identity(panel)
        try:
            write_error_log(
                'V136模式切换身份竞态拒绝',
                detail=(
                    f'reason={reason} | loaded={loaded_key or "<none>"} | '
                    f'current={conflict} | song={song or "<none>"} | action=wait-current-track-owner'
                ),
            )
        except Exception:
            pass
        try:
            panel.status.setText('状态：检测到切歌，等待当前歌曲身份稳定后按所选歌词模式自动接管…')
        except Exception:
            pass
        # Returning without emitting a failure result intentionally preserves the user's new
        # mode preference.  The current/new-track automatic transaction remains authoritative.
        return False
    return _V136_MODE_REFETCH_PRE(
        panel,
        reason=reason,
        rollback_trans_only=rollback_trans_only,
        rollback_precise=rollback_precise,
    )


def _v136_rehydrate_bilingual(panel):
    try:
        if _h95f5_norm_mode(getattr(panel, '_h95f5_bilingual_mode', 'original')) != 'bilingual':
            return False
        identity, _song, _artist = _h95f5_panel_identity_key(panel)
        cache = getattr(panel, '_h95f5_translation_cache', {})
        row = cache.get(identity) if identity and isinstance(cache, dict) else None
        if not isinstance(row, dict) or not str(row.get('lyric') or '').strip():
            return False
        # Reuse H95F10's existing provider/duration/identity validation.  This call only
        # reattaches an already-approved translation to the freshly rebuilt unified track.
        _h95f5_apply_cached_translation(panel)
        window = getattr(panel, 'lyric_window', None)
        active_lrc = str(getattr(window, '_h95f5_translation_lrc', '') or '') if window is not None else ''
        if active_lrc:
            try:
                write_error_log(
                    'V136重新载入双语缓存重挂',
                    detail=f'identity={identity} | chars={len(active_lrc)} | authority=display-only',
                )
            except Exception:
                pass
            return True
    except Exception as exc:
        try:
            write_error_log('V136重新载入双语缓存重挂失败', exc)
        except Exception:
            pass
    return False


def _v136_launch_current_lyrics(panel, *args, **kwargs):
    out = _V136_LAUNCH_PRE(panel, *args, **kwargs)
    # _launch_current_lyrics rebuilds the H95 unified track.  Reattach the verified sidecar
    # on the next GUI turn so restart/start/mode relaunch cannot silently drop translation.
    if out is not False and bool(getattr(panel, '_is_started', False)):
        try:
            QTimer.singleShot(0, lambda p=panel: _v136_rehydrate_bilingual(p))
        except Exception:
            _v136_rehydrate_bilingual(panel)
    return out


def _v136_activate_field_regression_closure():
    try:
        ControlPanel._launch_current_lyrics = _v136_launch_current_lyrics
        ControlPanel._launch_current_lyrics._limbus_layer = 'V136'
        ControlPanel._refetch_loaded_track_for_mode_switch = _v136_refetch_loaded_track_for_mode_switch
        ControlPanel._refetch_loaded_track_for_mode_switch._limbus_layer = 'V136'
        try:
            write_error_log(
                'V136现场回归收口激活',
                detail='bilingual-relaunch=cache-reattach | mode-refetch=mixed-identity-veto | clock/seek/render=unchanged',
            )
        except Exception:
            pass
    except Exception as exc:
        try:
            write_error_log('V136现场回归收口激活失败', exc)
        except Exception:
            pass


_v136_activate_field_regression_closure()
'''
    text = replace_once(text, activation, activation + block, 'R9.2 activation anchor')
    ast.parse(text)
    return text


def patch_simple(path: Path, replacements: list[tuple[str, str, str]]) -> None:
    encoding = 'utf-8-sig' if path.suffix.lower() == '.iss' else 'utf-8'
    text = path.read_text(encoding=encoding)
    original = text
    for old, new, label in replacements:
        if old in text:
            text = text.replace(old, new)
        elif new not in text:
            raise SystemExit(f'V136 PATCH: {path}: missing {label}')
    if text != original:
        path.write_text(text, encoding=encoding, newline='\n')


def update_main_source_lock(actual_sha: str) -> None:
    path = ROOT / 'installer' / 'CHECK_MAIN_SOURCE_LOCK.py'
    text = path.read_text(encoding='utf-8')
    new, count = re.subn(r'EXPECTED\s*=\s*[\"\'][0-9a-f]{64}[\"\']', f'EXPECTED = "{actual_sha}"', text, count=1)
    if count != 1:
        raise SystemExit('V136 PATCH: could not update main source lock')
    path.write_text(new, encoding='utf-8', newline='\n')


def apply() -> None:
    if not MAIN.is_file():
        raise SystemExit(f'V136 PATCH: main source missing: {MAIN}')
    text = MAIN.read_text(encoding='utf-8')
    already = MARKER in text
    base_hash = normalized_text_sha256(MAIN)
    if not already and base_hash != BASE_SHA256:
        raise SystemExit(f'V136 PATCH: unexpected normalized base source SHA256 {base_hash}')

    patched = patch_main(text)
    if patched != text:
        MAIN.write_text(patched, encoding='utf-8', newline='\n')

    files: dict[Path, list[tuple[str, str, str]]] = {
        ROOT / 'installer' / 'LimbusLyric_Setup.iss': [
            ('#define MyAppVersion "1.8.9.135"', '#define MyAppVersion "1.8.9.136"', 'Inno version'),
            ('#define MyOutputBase "LimbusLyric_Setup_1.8.9.135"', '#define MyOutputBase "LimbusLyric_Setup_1.8.9.136"', 'Inno output'),
        ],
        ROOT / 'installer' / 'BUILD_RELEASE.cmd': [
            ('LimbusLyric_Portable_1.8.9.135.zip', 'LimbusLyric_Portable_1.8.9.136.zip', 'portable name'),
            ('LimbusLyric_Setup_1.8.9.135.exe', 'LimbusLyric_Setup_1.8.9.136.exe', 'setup name'),
            ('LimbusLyric 1.8.9.135 Release', 'LimbusLyric 1.8.9.136 Test', 'build info'),
        ],
        ROOT / 'REPACKAGE_SETUP_ONLY.cmd': [
            ('LimbusLyric_Setup_1.8.9.135.exe', 'LimbusLyric_Setup_1.8.9.136.exe', 'repackage setup name'),
        ],
        ROOT / 'installer' / 'CHECK_PACKAGING_CONTRACT.py': [
            ('LimbusLyric_Setup_1.8.9.135', 'LimbusLyric_Setup_1.8.9.136', 'packaging contract version'),
        ],
        ROOT / 'installer' / 'CHECK_RELEASE_INVARIANTS.py': [
            ('LimbusLyric_Setup_1.8.9.135', 'LimbusLyric_Setup_1.8.9.136', 'release setup invariant'),
            ('LimbusLyric_Portable_1.8.9.135.zip', 'LimbusLyric_Portable_1.8.9.136.zip', 'release portable invariant'),
            ('Inno output not v1.8.9.135', 'Inno output not v1.8.9.136', 'release invariant message'),
        ],
        ROOT / 'installer' / 'LimbusLyric.spec': [
            ('LimbusLyric 1.8.9.135 hotfix release', 'LimbusLyric 1.8.9.136 field hotfix test', 'spec description'),
        ],
    }
    for path, replacements in files.items():
        patch_simple(path, replacements)

    actual = normalized_text_sha256(MAIN)
    update_main_source_lock(actual)

    sys.path.insert(0, str(ROOT / 'installer'))
    from SOURCE_MANIFEST import regenerate_manifest
    regenerate_manifest(ROOT)
    verify()


def verify() -> None:
    text = MAIN.read_text(encoding='utf-8')
    ast.parse(text)
    required = [
        'v1.8.9.136 RELEASE V136 FIELD REGRESSION CLOSURE',
        'V135 TRANSLATION OWNERSHIP HOTFIX',
        "cur='1.8.9.136 H14'",
        "QLabel('当前版本  ·  v1.8.9.136', card)",
        'V136模式切换身份竞态拒绝',
        'V136重新载入双语缓存重挂',
        '+ QQ MODERN SEARCH + COVER DIRECT-ID R9.2',
    ]
    for token in required:
        if token not in text:
            raise SystemExit(f'V136 PATCH VERIFY: missing token: {token[:100]}')
    actual = normalized_text_sha256(MAIN)
    lock = (ROOT / 'installer' / 'CHECK_MAIN_SOURCE_LOCK.py').read_text(encoding='utf-8')
    if actual not in lock:
        raise SystemExit('V136 PATCH VERIFY: source lock does not match patched main')
    iss = (ROOT / 'installer' / 'LimbusLyric_Setup.iss').read_text(encoding='utf-8-sig')
    if '#define MyAppVersion "1.8.9.136"' not in iss or 'LimbusLyric_Setup_1.8.9.136' not in iss:
        raise SystemExit('V136 PATCH VERIFY: Inno metadata not updated')
    print('V136 FIELD PATCH VERIFY: PASS')
    print(f'  normalized_main_sha256={actual}')
    print('  bilingual relaunch: verified-cache reattach only')
    print('  mode refetch: mixed loaded/current identity veto')
    print('  clock/seek/render formulas: unchanged')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    verify() if args.check else apply()


if __name__ == '__main__':
    main()
