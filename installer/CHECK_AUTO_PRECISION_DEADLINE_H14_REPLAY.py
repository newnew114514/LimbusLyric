#!/usr/bin/env python3
from pathlib import Path
import re, threading, time

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / 'LimbusLyric_v1.8.9.133_CROSS_PROVIDER_TRANSLATION_CUSTOM_ADAPTER_FOUNDATION_20260814.py'
src = MAIN.read_text(encoding='utf-8')
marker = '# H14 auto-precision deadline / bounded enhancement'
main_guard = '\nif __name__ == "__main__":\n'
assert marker in src, 'H14 marker missing'
assert main_guard in src, 'main guard missing'
assert src.index(marker) < src.index(main_guard), 'H14 runtime closure must install before main guard'
assert 'H14_AUTO_KUGOU_PRECISE_BUDGET_SEC = 22.0' in src
assert 'H14_AUTO_KUGOU_PRECISE_MAX_INFLIGHT = 2' in src
assert 'H14_AUTO_KUGOU_UI_HINT_BUDGET_SEC = 1.25' in src
assert 'LimbusLyric-H14-KuGouDurationHint' in src
assert 'h14_auto_precision_ui_hint_timeout=True' in src
assert "thread_name.startswith('LimbusLyric-AutoLyrics-g')" in src
assert "str(source or '') == '酷狗'" in src
assert 'acquire(blocking=False)' in src
assert 'auto-cache=skip' in src
assert '_LIMBUS_H14_AUTO_RESULT_PRE = ControlPanel._on_auto_lyric_result' in src
assert "patched['progressive_keep_fast'] = False" in src
assert '自动歌词保留快速歌词所有权拒绝' in src

ownership_marker = '# Progressive keep-fast is valid only if the fast stage actually became the'
assert ownership_marker in src, 'H14 ownership marker missing'
block = src[src.index(marker):src.index(ownership_marker)]
logs = []

class FakeEngine:
    last_error = ''
    _cancel_local = threading.local()
    _provider_meta_local = threading.local()
    @classmethod
    def _set_cancel_check(cls, fn=None):
        cls._cancel_local.fn = fn if callable(fn) else None
    @classmethod
    def _is_cancelled(cls):
        fn = getattr(cls._cancel_local, 'fn', None)
        return bool(callable(fn) and fn())
    @classmethod
    def _set_provider_meta(cls, **meta):
        cls._provider_meta_local.value = dict(meta)
    @classmethod
    def last_provider_meta(cls):
        return dict(getattr(cls._provider_meta_local, 'value', {}) or {})

ui_hint_delay = {'value': 0.0}
class FakeFetcher:
    @staticmethod
    def get_kugou_ui_duration_hint(pids, song_name, max_nodes=640):
        delay = float(ui_hint_delay['value'])
        if delay > 0:
            time.sleep(delay)
        return 201000

calls = []
def old_search(song_name, artist='', source='网易云', trans_only=False, provider_track_id=None, provider_duration_ms=0, prefer_precise=True):
    calls.append((song_name, source, bool(prefer_precise), threading.current_thread().name))
    if song_name == 'ui-hint-through-search':
        FakeFetcher.get_kugou_ui_duration_hint([1], song_name)
        FakeEngine._set_provider_meta(source=source, simulated_success=True)
        FakeEngine.last_error = ''
        return '[00:00.00]<0,1>unsafe-without-ui-version-proof', 201000
    # Simulate a provider that remains in bounded network work but cooperatively checks cancel.
    start = time.monotonic()
    while time.monotonic() - start < 2.0:
        if FakeEngine._is_cancelled():
            FakeEngine.last_error = 'cancelled-by-budget'
            FakeEngine._set_provider_meta(source=source, simulated_cancel=True)
            return None, 0
        time.sleep(0.01)
    FakeEngine._set_provider_meta(source=source, simulated_success=True)
    FakeEngine.last_error = ''
    return '[00:00.00]<0,1>ok', 123000

FakeEngine.search = staticmethod(old_search)

def write_error_log(label, *args, **kwargs):
    logs.append((label, kwargs.get('detail', '')))

ns = {
    'threading': threading,
    'time': time,
    'LyricSearchEngine': FakeEngine,
    'LyricFetcher': FakeFetcher,
    'write_error_log': write_error_log,
}
exec(compile(block, str(MAIN), 'exec'), ns, ns)
# Shorten only the replay budget; production source remains 22 seconds.
ns['H14_AUTO_KUGOU_PRECISE_BUDGET_SEC'] = 0.12
ns['H14_AUTO_KUGOU_UI_HINT_BUDGET_SEC'] = 0.05
wrapped = FakeEngine.search

old_name = threading.current_thread().name
try:
    # Non-auto and fast-stage calls must be transparent.
    threading.current_thread().name = 'MainThread'
    t0 = time.monotonic(); lyric, dur = wrapped('normal', source='酷狗', prefer_precise=True)
    assert lyric and dur == 123000 and time.monotonic() - t0 > 1.5, 'non-auto call should pass through untouched'

    # Auto fast LRC must not be budgeted.
    threading.current_thread().name = 'LimbusLyric-AutoLyrics-g7'
    t0 = time.monotonic(); lyric, dur = wrapped('fast', source='酷狗', prefer_precise=False)
    assert lyric and dur == 123000 and time.monotonic() - t0 > 1.5, 'fast stage should pass through untouched'

    # NetEase precise remains untouched by the KuGou-only H14 closure.
    t0 = time.monotonic(); lyric, dur = wrapped('ncm', source='网易云', prefer_precise=True)
    assert lyric and dur == 123000 and time.monotonic() - t0 > 1.5, 'NetEase should pass through untouched'

    # Auto KuGou precise must cooperatively close near the replay deadline and keep fast payload.
    FakeEngine.last_error = ''
    t0 = time.monotonic(); lyric, dur = wrapped('slow-krc', source='酷狗', prefer_precise=True)
    elapsed = time.monotonic() - t0
    assert lyric is None and dur == 0, 'timed-out precise result must be dropped'
    assert 0.10 <= elapsed < 0.6, f'cooperative deadline failed: {elapsed:.3f}s'
    assert '自动精准升级超过0秒预算' in FakeEngine.last_error or '自动精准升级超过' in FakeEngine.last_error
    meta = FakeEngine.last_provider_meta()
    assert meta.get('h14_auto_precision_timeout') is True, meta
    assert any(x[0] == '自动歌词精确升级超时保留快速歌词' for x in logs), logs[-5:]

    # Parent generation cancellation must stay authoritative and be restored after wrapper exit.
    parent_flag = {'cancel': True}
    parent_fn = lambda: parent_flag['cancel']
    FakeEngine._set_cancel_check(parent_fn)
    t0 = time.monotonic(); lyric, dur = wrapped('stale-song', source='酷狗', prefer_precise=True)
    assert lyric is None and dur == 0 and time.monotonic() - t0 < 0.3
    assert getattr(FakeEngine._cancel_local, 'fn', None) is parent_fn, 'parent cancel callback not restored'
    FakeEngine._set_cancel_check(None)

    # The real-world suspect is the KuGou MSAA duration hint.  In auto precise mode it must
    # be bounded independently; a late COM result is ignored and marks the precision pass unsafe.
    ns['_LIMBUS_H14_LOCAL'].auto_precise_active = True
    ns['_LIMBUS_H14_LOCAL'].ui_hint_timeout = False
    ui_hint_delay['value'] = 0.30
    t0 = time.monotonic(); hint = FakeFetcher.get_kugou_ui_duration_hint([1], 'slow-ui-hint')
    elapsed = time.monotonic() - t0
    assert hint == 0 and elapsed < 0.18, f'UI hint budget failed: {elapsed:.3f}s'
    assert ns['_LIMBUS_H14_LOCAL'].ui_hint_timeout is True
    assert any(x[0] == '自动歌词酷狗版本时长证据超时' for x in logs), logs[-8:]
    ns['_LIMBUS_H14_LOCAL'].auto_precise_active = False
    ns['_LIMBUS_H14_LOCAL'].ui_hint_timeout = False
    ui_hint_delay['value'] = 0.0

    # If the precise search itself observes a UI-hint timeout, even a later KRC-like payload
    # must be discarded because the same-title version proof was not obtained.
    ui_hint_delay['value'] = 0.30
    t0 = time.monotonic(); lyric, dur = wrapped('ui-hint-through-search', source='酷狗', prefer_precise=True)
    elapsed = time.monotonic() - t0
    assert lyric is None and dur == 0 and elapsed < 0.22, (lyric, dur, elapsed)
    assert FakeEngine.last_provider_meta().get('h14_auto_precision_ui_hint_timeout') is True
    assert '版本时长证据读取超时' in FakeEngine.last_error
    ui_hint_delay['value'] = 0.0

    # Saturation: two abandoned/slow upgrades occupy the bounded slots; a third skips network instantly.
    sem = ns['_LIMBUS_H14_AUTO_PRECISE_SLOTS']
    assert sem.acquire(blocking=False) and sem.acquire(blocking=False)
    before = len(calls)
    t0 = time.monotonic(); lyric, dur = wrapped('third', source='酷狗', prefer_precise=True)
    elapsed = time.monotonic() - t0
    assert lyric is None and dur == 0 and elapsed < 0.08, f'saturated path blocked: {elapsed:.3f}s'
    assert len(calls) == before, 'saturated path must skip provider network'
    assert FakeEngine.last_provider_meta().get('h14_auto_precision_saturated') is True
    sem.release(); sem.release()
finally:
    threading.current_thread().name = old_name

print('PASS: H14 automatic KuGou precision deadline / bounded enhancement replay')

# Execute the keep-fast ownership guard independently of Qt.
# Review only H14's own ownership closure.  Later generations append independent
# runtime/UI layers before __main__; executing those here with H14's deliberately
# minimal fake namespace turns this replay into an accidental cross-generation test.
ownership_end_marker = '# H27 player-clock epoch / Win10 visual / KuGou Win11 closure'
assert ownership_end_marker in src, 'H14 ownership end marker missing'
ownership_block = src[src.index(ownership_marker):src.index(ownership_end_marker)]
received = []
class FakePanel:
    def __init__(self, loaded_song, loaded_artist):
        self._loaded_song = loaded_song
        self._loaded_artist = loaded_artist
    @staticmethod
    def _same_track(a_song, a_artist, b_song, b_artist):
        return (str(a_song).strip().casefold(), str(a_artist).strip().casefold()) == (str(b_song).strip().casefold(), str(b_artist).strip().casefold())
    def _on_auto_lyric_result(self, result):
        received.append(dict(result))
        return result

ns2 = {'ControlPanel': FakePanel, 'write_error_log': write_error_log}
exec(compile(ownership_block, str(MAIN), 'exec'), ns2, ns2)
p = FakePanel('Shown Song', 'Artist')
p._on_auto_lyric_result({'song':'Shown Song','artist':'Artist','progressive_keep_fast':True,'error':'timeout'})
assert received[-1]['progressive_keep_fast'] is True, 'display-owned fast lyric must remain keep-fast'
p2 = FakePanel('Old Song', 'Artist')
p2._on_auto_lyric_result({'song':'New Song','artist':'Artist','progressive_keep_fast':True,'error':'timeout'})
assert received[-1]['progressive_keep_fast'] is False, 'unshown fast candidate must not be treated as presentation owner'
print('PASS: H14 keep-fast presentation ownership replay')
