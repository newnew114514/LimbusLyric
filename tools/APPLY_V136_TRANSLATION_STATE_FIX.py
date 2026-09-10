from __future__ import annotations

import argparse
import ast
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / 'LimbusLyric_v1.8.9.133_CROSS_PROVIDER_TRANSLATION_CUSTOM_ADAPTER_FOUNDATION_20260814.py'
BASE_SHA256 = 'fc6dedb8761c7aea81aefc68bb34fa6bdf333b7ff15db7e2a2bc181cd363b53f'
MARKER = 'V136 TRANSLATION STATE CANDIDATE'


def normalized_text(text: str) -> str:
    return '\n'.join(text.splitlines()).rstrip() + '\n'


def normalized_sha256_text(text: str) -> str:
    return hashlib.sha256(normalized_text(text).encode('utf-8')).hexdigest()


def _panel_method_segment(text: str, method_name: str) -> tuple[int, int, str]:
    tree = ast.parse(text)
    panels = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'ControlPanel']
    if not panels:
        raise SystemExit('V136 PATCH: ControlPanel class not found')
    panel = panels[-1]
    methods = [
        n for n in panel.body
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == method_name
    ]
    if len(methods) != 1:
        raise SystemExit(f'V136 PATCH: expected one ControlPanel.{method_name}, found {len(methods)}')
    method = methods[0]
    lines = text.splitlines(keepends=True)
    starts = [0]
    total = 0
    for line in lines:
        total += len(line)
        starts.append(total)
    start = starts[method.lineno - 1]
    end = starts[method.end_lineno]
    return start, end, text[start:end]


def _replace_in_method(text: str, method_name: str, old: str, new: str, label: str) -> str:
    start, end, segment = _panel_method_segment(text, method_name)
    count = segment.count(old)
    if count != 1:
        raise SystemExit(f'V136 PATCH: expected one {label} in ControlPanel.{method_name}, found {count}')
    segment = segment.replace(old, new, 1)
    return text[:start] + segment + text[end:]


def patch_main_text(text: str) -> str:
    text = normalized_text(text)
    if MARKER in text:
        compile(text, str(MAIN), 'exec')
        return text

    actual = normalized_sha256_text(text)
    if actual != BASE_SHA256:
        raise SystemExit(f'V136 PATCH: unexpected normalized base source SHA256 {actual}')

    old_refetch = '''        source = str(self.source_combo.currentText() or '')
        trans_only = bool(self.trans_check.isChecked())
        provider_duration_ms = (
            LyricFetcher.get_qq_ui_duration_hint(self, 'mode-refetch') if source == 'QQ音乐' else 0
        )
        self._mode_refetch_generation = int(getattr(self, '_mode_refetch_generation', 0) or 0) + 1
'''
    new_refetch = '''        source = str(self.source_combo.currentText() or '')
        trans_only = bool(self.trans_check.isChecked())
        # V136 TRANSLATION STATE CANDIDATE: freeze every semantic/search input at
        # transaction creation. The old path captured loaded title/artist first but
        # then sampled QQ's current UI duration; a track handoff in between could
        # create an impossible old-title/new-duration request. Prefer the duration
        # already bound to the loaded payload, and only borrow a live playback duration
        # when that snapshot still proves the same track identity.
        prefer_precise = bool(self.precise_tracking_check.isChecked()) if hasattr(self, 'precise_tracking_check') else True
        require_translation_pair = bool(
            (not trans_only) and
            str(getattr(self, '_h95f5_bilingual_mode', 'original') or 'original') == 'bilingual'
        )
        try:
            provider_duration_ms = int(getattr(self.lyric_window, 'song_duration', 0) or 0)
        except Exception:
            provider_duration_ms = 0
        if provider_duration_ms <= 0:
            try:
                snap = dict(self.media_sync.snapshot() or {})
                snap_song = str(snap.get('media_title') or '').strip()
                snap_artist = str(snap.get('media_artist') or '').strip()
                if snap_song and self._same_track(song, artist, snap_song, snap_artist):
                    provider_duration_ms = int(snap.get('duration_ms') or 0)
            except Exception:
                provider_duration_ms = 0
        self._mode_refetch_generation = int(getattr(self, '_mode_refetch_generation', 0) or 0) + 1
'''
    text = _replace_in_method(
        text, '_refetch_loaded_track_for_mode_switch',
        old_refetch, new_refetch, 'immutable mode-refetch input block'
    )

    old_search = '''                    song, artist, source, trans_only, provider_duration_ms=provider_duration_ms,
                    prefer_precise=bool(self.precise_tracking_check.isChecked()) if hasattr(self, 'precise_tracking_check') else True,
                    require_translation_pair=bool((not trans_only) and str(getattr(self, '_h95f5_bilingual_mode', 'original') or 'original') == 'bilingual')
'''
    new_search = '''                    song, artist, source, trans_only, provider_duration_ms=provider_duration_ms,
                    prefer_precise=prefer_precise,
                    require_translation_pair=require_translation_pair
'''
    text = _replace_in_method(
        text, '_refetch_loaded_track_for_mode_switch',
        old_search, new_search, 'mode-refetch worker snapshot use'
    )

    old_start = '''                return
            self._is_started = False
            self._auto_armed = False
            self.lyric_window.hide()
            return
'''
    new_start = '''                return
            # V136 TRANSLATION STATE CANDIDATE: a semantic payload barrier means
            # "the requested mode has nothing displayable yet", not "the user pressed
            # Stop". Preserve the explicit Start intent while keeping presentation
            # blank. A later current-track payload can then launch normally; a real
            # Stop still clears the armed state through stop()/_cancel_auto_jobs().
            if bool(getattr(self, '_limbus_mode_payload_blocked', False)):
                self._is_started = True
                self._auto_armed = bool(self.auto_track_check.isChecked())
                self.lyric_window.hide()
                try:
                    reason = str(getattr(self, '_limbus_mode_payload_block_reason', '') or 'payload-mismatch')
                    self.status.setText('状态：当前模式歌词暂不可用；已保持开始状态，等待有效歌词…')
                    write_error_log('模式载荷等待期间开始保持武装', detail=(
                        f'reason={reason} | auto_armed={int(self._auto_armed)} | '
                        f'loaded={getattr(self, "_loaded_track_key", "") or "<manual>"} | presentation=blank'
                    ))
                except Exception:
                    pass
                return
            self._is_started = False
            self._auto_armed = False
            self.lyric_window.hide()
            return
'''
    text = _replace_in_method(
        text, 'start', old_start, new_start, 'semantic-block Start intent preservation'
    )

    compile(text, str(MAIN), 'exec')
    return normalized_text(text)


def verify_patched(text: str) -> None:
    text = normalized_text(text)
    required = (
        MARKER,
        '模式载荷等待期间开始保持武装',
        "provider_duration_ms = int(getattr(self.lyric_window, 'song_duration', 0) or 0)",
        'prefer_precise=prefer_precise',
        'require_translation_pair=require_translation_pair',
        'V135 TRANSLATION OWNERSHIP HOTFIX',
        '+ QQ MODERN SEARCH + COVER DIRECT-ID R9.2',
    )
    for token in required:
        if token not in text:
            raise SystemExit(f'V136 VERIFY: missing token: {token}')
    _, _, refetch = _panel_method_segment(text, '_refetch_loaded_track_for_mode_switch')
    if "get_qq_ui_duration_hint(self, 'mode-refetch')" in refetch:
        raise SystemExit('V136 VERIFY: mutable QQ UI duration still used by mode-refetch')
    if refetch.find('prefer_precise =') > refetch.find('def worker():'):
        raise SystemExit('V136 VERIFY: prefer_precise is not frozen before worker creation')
    if refetch.find('require_translation_pair =') > refetch.find('def worker():'):
        raise SystemExit('V136 VERIFY: bilingual requirement is not frozen before worker creation')
    _, _, start = _panel_method_segment(text, 'start')
    keep = start.find("if bool(getattr(self, '_limbus_mode_payload_blocked', False)):")
    clear = start.find('self._is_started = False', keep)
    if keep < 0 or clear < 0 or keep > clear:
        raise SystemExit('V136 VERIFY: semantic Start-intent guard is not before destructive clear')
    compile(text, str(MAIN), 'exec')


def apply() -> None:
    if not MAIN.is_file():
        raise SystemExit(f'V136 PATCH: main source missing: {MAIN}')
    original = MAIN.read_text(encoding='utf-8')
    patched = patch_main_text(original)
    MAIN.write_text(patched, encoding='utf-8', newline='\n')
    verify_patched(patched)
    print('V136 TRANSLATION STATE PATCH: PASS')
    print(f'  normalized_main_sha256={normalized_sha256_text(patched)}')


def check() -> None:
    text = MAIN.read_text(encoding='utf-8')
    if MARKER in text:
        verify_patched(text)
        print('V136 TRANSLATION STATE VERIFY: PATCHED PASS')
        print(f'  normalized_main_sha256={normalized_sha256_text(text)}')
        return
    actual = normalized_sha256_text(text)
    if actual != BASE_SHA256:
        raise SystemExit(f'V136 VERIFY: unexpected base hash {actual}')
    patched = patch_main_text(text)
    verify_patched(patched)
    print('V136 TRANSLATION STATE VERIFY: DRY-RUN PASS')
    print(f'  base_sha256={BASE_SHA256}')
    print(f'  would_patch_sha256={normalized_sha256_text(patched)}')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    check() if args.check else apply()


if __name__ == '__main__':
    main()
