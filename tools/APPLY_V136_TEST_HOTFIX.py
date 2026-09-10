from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
MAIN_NAME = 'LimbusLyric_v1.8.9.133_CROSS_PROVIDER_TRANSLATION_CUSTOM_ADAPTER_FOUNDATION_20260814.py'
MAIN = ROOT / MAIN_NAME
BASE_SHA256 = 'fc6dedb8761c7aea81aefc68bb34fa6bdf333b7ff15db7e2a2bc181cd363b53f'
HOTFIX_MARKER = 'V136 TRANSLATION STATE TEST'


def normalized_text_sha256(path: Path, encoding: str = 'utf-8') -> str:
    text = path.read_text(encoding=encoding)
    normalized = '\n'.join(text.splitlines()).rstrip() + '\n'
    return hashlib.sha256(normalized.encode(encoding)).hexdigest()


def write_text_lf(path: Path, text: str, encoding: str = 'utf-8') -> None:
    with path.open('w', encoding=encoding, newline='\n') as fh:
        fh.write(text)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'V136 HOTFIX: expected exactly one {label}, found {count}')
    return text.replace(old, new, 1)


def patch_main(text: str) -> str:
    if HOTFIX_MARKER in text:
        return text

    text = replace_once(
        text,
        'LIMBUSLYRIC_BUILD_TAG = "v1.8.9.135 RELEASE V135 TRANSLATION OWNERSHIP HOTFIX + ',
        'LIMBUSLYRIC_BUILD_TAG = "v1.8.9.136 TEST V136 TRANSLATION STATE TEST + V135 TRANSLATION OWNERSHIP HOTFIX + ',
        'build tag',
    )
    text = replace_once(text, "cur='1.8.9.135 H13'", "cur='1.8.9.136 H14'", 'updater current version')
    text = replace_once(text, "base = m.group(1) if m else '1.8.9.135'", "base = m.group(1) if m else '1.8.9.136'", 'version fallback')
    text = replace_once(text, "QLabel('当前版本  ·  v1.8.9.135', card)", "QLabel('当前版本  ·  v1.8.9.136', card)", 'about version label')

    old_start = '''    def start(self):\n        text = self.text_input.toPlainText().strip()\n        if not text:\n            self.status.setText("状态：请先输入歌词！")\n            return\n\n        if not self._loaded_track_key:\n'''
    new_start = '''    def start(self):\n        _v136_was_started = bool(getattr(self, '_is_started', False))\n        _v136_mode_blocked = bool(getattr(self, '_limbus_mode_payload_blocked', False))\n        _v136_text = self.text_input.toPlainText().strip()\n\n        if _v136_mode_blocked:\n            # A semantic-mode miss means "nothing valid to present for this track", not\n            # "the user asked to stop". Preserve the explicit Start intent so the next\n            # current-track success launches automatically without another click.\n            self._is_started = True\n            self._auto_armed = bool(self.auto_track_check.isChecked())\n            if not _v136_was_started:\n                try:\n                    _v136_player = str(self.player_combo.currentText() or '')\n                    _v136_process = str((self.players.get(_v136_player, {}) or {}).get('process') or '')\n                    if _v136_process:\n                        self.media_sync.start(_v136_process)\n                except Exception as exc:\n                    write_error_log('V136模式空载荷开始同步预热失败', exc)\n            try:\n                self.lyric_window.hide()\n            except Exception:\n                pass\n            try:\n                write_error_log('V136模式空载荷开始保持武装', detail=(\n                    f'loaded={getattr(self, "_loaded_track_key", "") or "<none>"} | '\n                    f'mode_reason={getattr(self, "_limbus_mode_payload_block_reason", "") or "<none>"} | '\n                    f'auto_armed={int(bool(self._auto_armed))} | desired_active=1'))\n            except Exception:\n                pass\n            self.status.setText('状态：当前模式暂无可显示歌词；保持运行，后续有效歌词会自动接管')\n            return True\n\n        _v136_runtime_busy = bool(\n            getattr(self, '_auto_overlay_suspended', False) or\n            getattr(self, '_track_switch_visual_hold', False) or\n            str(getattr(self, '_auto_target_key', '') or '')\n        )\n        _v136_has_bound_timeline = bool(\n            str(getattr(self, '_loaded_track_key', '') or '') and\n            getattr(self.lyric_window, 'lyric_timeline', None)\n        )\n        if _v136_was_started and _v136_text and _v136_has_bound_timeline and not _v136_runtime_busy:\n            # Start is idempotent once a current lyric performance is active. Re-show/check the\n            # existing performance only; do not recreate the timeline/translation sidecar or\n            # restart the player clock. Sync Doctor remains the explicit recalibration control.\n            self._auto_armed = bool(self.auto_track_check.isChecked())\n            try:\n                self.lyric_window.show()\n                self.lyric_window.check_lyric_time()\n            except Exception as exc:\n                write_error_log('V136重复开始轻量刷新失败', exc)\n            try:\n                write_error_log('V136重复开始幂等', detail=(\n                    f'loaded={getattr(self, "_loaded_track_key", "") or "<none>"} | '\n                    'shadow-rebuild=0 | media-restart=0 | bilingual-sidecar=preserve'))\n            except Exception:\n                pass\n            return True\n\n        text = _v136_text\n        if not text:\n            self.status.setText("状态：请先输入歌词！")\n            return\n\n        if not self._loaded_track_key:\n'''
    text = replace_once(text, old_start, new_start, 'ControlPanel.start entry')

    old_mode = '''        source = str(self.source_combo.currentText() or '')\n        trans_only = bool(self.trans_check.isChecked())\n        provider_duration_ms = (\n            LyricFetcher.get_qq_ui_duration_hint(self, 'mode-refetch') if source == 'QQ音乐' else 0\n        )\n        self._mode_refetch_generation = int(getattr(self, '_mode_refetch_generation', 0) or 0) + 1\n'''
    new_mode = '''        source = str(self.source_combo.currentText() or '')\n        trans_only = bool(self.trans_check.isChecked())\n\n        _v136_live_song = ''\n        _v136_live_artist = ''\n        try:\n            _v136_state = self.media_sync.snapshot() or {}\n            _v136_player = str(self.player_combo.currentText() or '')\n            _v136_process = str((self.players.get(_v136_player, {}) or {}).get('process') or '')\n            _v136_media_source = str(_v136_state.get('media_source') or '')\n            _v136_title = str(_v136_state.get('media_title') or '').strip()\n            if (\n                _v136_title and _v136_process and\n                self.media_sync._source_matches_process_hint(_v136_media_source, _v136_process)\n            ):\n                _v136_live_song = _v136_title\n                _v136_live_artist = str(_v136_state.get('media_artist') or '').strip()\n        except Exception as exc:\n            try:\n                write_error_log('V136模式刷新当前身份快照失败', exc)\n            except Exception:\n                pass\n\n        if (\n            _v136_live_song and\n            not self._same_track(song, artist, _v136_live_song, _v136_live_artist)\n        ):\n            self._mode_refetch_generation = int(getattr(self, '_mode_refetch_generation', 0) or 0) + 1\n            try:\n                _v136_failed_key = str(getattr(self, '_auto_failed_track_key', '') or '')\n                if _v136_failed_key and '|' in _v136_failed_key:\n                    _v136_fs, _v136_fa = _v136_failed_key.split('|', 1)\n                    if self._same_track(_v136_live_song, _v136_live_artist, _v136_fs, _v136_fa):\n                        self._auto_failed_track_key = ''\n                        self._auto_failed_until = 0.0\n                self._auto_target_key = ''\n                self._auto_candidate_key = ''\n                self._auto_candidate_hits = 0\n                self._auto_queued_job = None\n                self._auto_fetch_in_progress = False\n                self._auto_generation = int(getattr(self, '_auto_generation', 0) or 0) + 1\n            except Exception:\n                pass\n            try:\n                write_error_log('V136模式刷新旧载荷身份转当前曲目', detail=(\n                    f'loaded={song}|{artist} | live={_v136_live_song}|{_v136_live_artist} | '\n                    f'trans_only={int(trans_only)} | old-duration-query=blocked | route=auto-current-track'))\n            except Exception:\n                pass\n            self.status.setText(\n                f"状态：模式已切换，正在按当前曲目「{_v136_live_song}」重新获取歌词..."\n            )\n            if bool(getattr(self, '_is_started', False)) and bool(self.auto_track_check.isChecked()):\n                self._auto_armed = True\n                QTimer.singleShot(0, lambda s=_v136_live_song, a=_v136_live_artist: self._request_auto_track(s, a))\n            return True\n\n        provider_duration_ms = (\n            LyricFetcher.get_qq_ui_duration_hint(self, 'mode-refetch') if source == 'QQ音乐' else 0\n        )\n        self._mode_refetch_generation = int(getattr(self, '_mode_refetch_generation', 0) or 0) + 1\n'''
    text = replace_once(text, old_mode, new_mode, 'mode-refetch identity snapshot')
    return text


def patch_simple(path: Path, replacements: list[tuple[str, str, str]]) -> None:
    encoding = 'utf-8-sig' if path.suffix.lower() == '.iss' else 'utf-8'
    text = path.read_text(encoding=encoding)
    original = text
    for old, new, label in replacements:
        if old in text:
            text = text.replace(old, new)
        elif new not in text:
            raise SystemExit(f'V136 HOTFIX: {path}: missing {label}')
    if text != original:
        write_text_lf(path, text, encoding=encoding)


def apply() -> None:
    if not MAIN.is_file():
        raise SystemExit(f'V136 HOTFIX: main source missing: {MAIN}')
    text = MAIN.read_text(encoding='utf-8')
    already = HOTFIX_MARKER in text
    base_hash = normalized_text_sha256(MAIN)
    if not already and base_hash != BASE_SHA256:
        raise SystemExit(f'V136 HOTFIX: unexpected normalized base source SHA256 {base_hash}')

    patched = patch_main(text)
    if patched != text:
        write_text_lf(MAIN, patched)

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
            ('LimbusLyric 1.8.9.135 hotfix release', 'LimbusLyric 1.8.9.136 translation state test', 'spec description'),
        ],
    }
    for path, replacements in files.items():
        patch_simple(path, replacements)

    patched_hash = normalized_text_sha256(MAIN)
    lock_path = ROOT / 'installer' / 'CHECK_MAIN_SOURCE_LOCK.py'
    patch_simple(lock_path, [
        (f'EXPECTED = "{BASE_SHA256}"', f'EXPECTED = "{patched_hash}"', 'main source lock'),
    ])

    sys.path.insert(0, str(ROOT / 'installer'))
    from SOURCE_MANIFEST import regenerate_manifest
    regenerate_manifest(ROOT)
    verify()


def verify() -> None:
    text = MAIN.read_text(encoding='utf-8')
    required = [
        'v1.8.9.136 TEST V136 TRANSLATION STATE TEST',
        "cur='1.8.9.136 H14'",
        "QLabel('当前版本  ·  v1.8.9.136', card)",
        'V136模式空载荷开始保持武装',
        'V136重复开始幂等',
        'V136模式刷新旧载荷身份转当前曲目',
        'old-duration-query=blocked',
        '+ QQ MODERN SEARCH + COVER DIRECT-ID R9.2',
    ]
    for token in required:
        if token not in text:
            raise SystemExit(f'V136 HOTFIX VERIFY: missing token: {token[:100]}')
    actual = normalized_text_sha256(MAIN)
    lock = (ROOT / 'installer' / 'CHECK_MAIN_SOURCE_LOCK.py').read_text(encoding='utf-8')
    if f'EXPECTED = "{actual}"' not in lock:
        raise SystemExit('V136 HOTFIX VERIFY: source lock does not match patched normalized hash')
    iss = (ROOT / 'installer' / 'LimbusLyric_Setup.iss').read_text(encoding='utf-8-sig')
    if '1.8.9.136' not in iss or 'LimbusLyric_Setup_1.8.9.136' not in iss:
        raise SystemExit('V136 HOTFIX VERIFY: Inno metadata not updated')
    print('V136 HOTFIX VERIFY: PASS')
    print(f'  normalized_main_sha256={actual}')
    print('  translation-mode miss keeps explicit Start intent armed')
    print('  repeated Start preserves existing timeline/bilingual sidecar and media clock')
    print('  stale loaded-track mode refetch is rerouted to current player identity')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    verify() if args.check else apply()


if __name__ == '__main__':
    main()
