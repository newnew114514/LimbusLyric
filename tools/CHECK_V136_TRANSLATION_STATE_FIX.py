from __future__ import annotations

import ast
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / 'LimbusLyric_v1.8.9.133_CROSS_PROVIDER_TRANSLATION_CUSTOM_ADAPTER_FOUNDATION_20260814.py'
PATCHER = ROOT / 'tools' / 'APPLY_V136_TRANSLATION_STATE_FIX.py'


def load_patcher():
    spec = importlib.util.spec_from_file_location('v136_patch', PATCHER)
    if spec is None or spec.loader is None:
        raise SystemExit('V136 CHECK: patcher import unavailable')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def panel_method(text: str, name: str) -> str:
    tree = ast.parse(text)
    panels = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'ControlPanel']
    if not panels:
        raise SystemExit('V136 CHECK: ControlPanel missing')
    panel = panels[-1]
    methods = [n for n in panel.body if isinstance(n, ast.FunctionDef) and n.name == name]
    if len(methods) != 1:
        raise SystemExit(f'V136 CHECK: expected one ControlPanel.{name}, got {len(methods)}')
    method = methods[0]
    lines = text.splitlines(keepends=True)
    return ''.join(lines[method.lineno - 1:method.end_lineno])


def need(cond: bool, message: str) -> None:
    if not cond:
        print('FAIL', message)
        raise SystemExit(1)
    print('PASS', message)


def main() -> None:
    patch = load_patcher()
    text = MAIN.read_text(encoding='utf-8')
    need(patch.MARKER in text, 'candidate patch marker present')
    patch.verify_patched(text)

    start = panel_method(text, 'start')
    keep_at = start.find("if bool(getattr(self, '_limbus_mode_payload_blocked', False)):")
    destructive_at = start.find('self._is_started = False', keep_at)
    need(keep_at >= 0 and destructive_at > keep_at,
         'semantic payload barrier preserves explicit Start before generic failure disarms')
    need("self._auto_armed = bool(self.auto_track_check.isChecked())" in start[keep_at:destructive_at],
         'preserved Start intent follows the user auto-track checkbox')
    need('self.lyric_window.hide()' in start[keep_at:destructive_at],
         'semantic no-payload state stays visually blank while armed')

    stop = panel_method(text, 'stop')
    need('_cancel_auto_jobs(keep_armed=False)' in stop and 'self._is_started = False' in stop,
         'explicit Stop still disarms the session')

    refetch = panel_method(text, '_refetch_loaded_track_for_mode_switch')
    worker_at = refetch.find('def worker():')
    need(worker_at > 0, 'mode-refetch worker exists')
    need("get_qq_ui_duration_hint(self, 'mode-refetch')" not in refetch,
         'mode-refetch no longer mixes loaded identity with mutable QQ UI duration')
    need(refetch.find("provider_duration_ms = int(getattr(self.lyric_window, 'song_duration', 0) or 0)") < worker_at,
         'mode-refetch duration witness is frozen before worker creation')
    need(refetch.find('prefer_precise =') < worker_at and refetch.find('require_translation_pair =') < worker_at,
         'mode-refetch semantic switches are frozen before worker creation')
    need('prefer_precise=prefer_precise' in refetch and 'require_translation_pair=require_translation_pair' in refetch,
         'worker consumes only frozen semantic switches')

    need('V135 TRANSLATION OWNERSHIP HOTFIX' in text,
         'v1.8.9.135 next-track ownership repair retained')
    need('+ QQ MODERN SEARCH + COVER DIRECT-ID R9.2' in text,
         'R9.2 QQ search and cover direct-ID behavior retained')
    compile(text, str(MAIN), 'exec')
    print('V136 TRANSLATION STATE REGRESSION CHECK: PASS')
    print(f'normalized_main_sha256={patch.normalized_sha256_text(text)}')


if __name__ == '__main__':
    main()
