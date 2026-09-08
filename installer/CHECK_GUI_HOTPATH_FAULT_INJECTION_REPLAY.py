#!/usr/bin/env python3
from __future__ import annotations

import ast
import os
import queue
import sys
import textwrap
import threading
import time
from pathlib import Path

if len(sys.argv) != 2:
    print('usage: CHECK_GUI_HOTPATH_FAULT_INJECTION_REPLAY.py <main.py>')
    raise SystemExit(2)

path = Path(sys.argv[1])
source = path.read_text(encoding='utf-8')
tree = ast.parse(source, filename=str(path))
classes = {n.name: n for n in tree.body if isinstance(n, ast.ClassDef)}


def need(cond, msg):
    if not cond:
        print('GUI HOTPATH FAULT INJECTION REPLAY: FAIL ' + msg)
        raise SystemExit(1)
    print('  ' + msg + ': PASS')


def method_source(cls_name, name):
    cls = classes.get(cls_name)
    if cls is None:
        raise KeyError(cls_name)
    node = next((n for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name), None)
    if node is None:
        raise KeyError(f'{cls_name}.{name}')
    return textwrap.dedent(ast.get_source_segment(source, node) or '')


def compile_method(cls_name, name, globs):
    ns = {}
    exec(method_source(cls_name, name), globs, ns)
    return ns[name]


logs = []
def log_stub(title, exc=None, detail=None):
    logs.append((str(title), '' if detail is None else str(detail)))


class FakeWin32Api:
    state = 0
    cursor = (100, 100)
    @classmethod
    def GetAsyncKeyState(cls, _key):
        return int(cls.state)
    @classmethod
    def GetCursorPos(cls):
        return tuple(cls.cursor)


common = {
    'time': time,
    'threading': threading,
    'os': os,
    'queue': queue,
    'SOURCE_GUARD_ENABLED': True,
    'GUI_CLICK_TARGET_PROBE_DEBOUNCE_MS': 160.0,
    'GUI_CLICK_TARGET_PROBE_STALE_MS': 1800.0,
    'write_error_log': log_stub,
    'win32api': FakeWin32Api,
}
request_probe = compile_method('MediaSessionSync', '_request_click_target_probe', common)
consume_probe = compile_method('MediaSessionSync', '_consume_click_target_probe', common)


class ProbeHarness:
    _request_click_target_probe = request_probe
    _consume_click_target_probe = consume_probe
    def __init__(self, delay_s=0.0, stem='cloudmusic'):
        self.delay_s = float(delay_s)
        self.return_stem = str(stem)
        self._click_target_probe_lock = threading.Lock()
        self._click_target_probe_serial = 0
        self._click_target_probe_inflight = {}
        self._click_target_probe_results = {}
        self._click_target_probe_last_request = {}
    @staticmethod
    def _process_stem(value):
        value = str(value or '').strip().lower()
        if value.endswith('.exe'):
            value = value[:-4]
        return value
    def _process_stem_at_point(self, _cx, _cy):
        time.sleep(self.delay_s)
        return self.return_stem


def wait_result(h, channel, timeout_s):
    deadline = time.perf_counter() + timeout_s
    while time.perf_counter() < deadline:
        with h._click_target_probe_lock:
            if channel in h._click_target_probe_results:
                return True
        time.sleep(0.002)
    return False


# 1) The exact production async verifier is attacked with progressively slower process
# image lookups. GUI-side enqueue latency must not scale with the injected Windows delay.
for delay_ms in (50, 100, 250, 500, 1000):
    logs.clear()
    h = ProbeHarness(delay_ms / 1000.0, 'cloudmusic')
    t0 = time.perf_counter()
    ok = h._request_click_target_probe('fault', 50, 60, 'cloudmusic', context={'delay_ms': delay_ms})
    enqueue_ms = (time.perf_counter() - t0) * 1000.0
    need(ok, f'async process probe accepted at {delay_ms}ms injection')
    need(enqueue_ms < max(30.0, delay_ms * 0.25), f'{delay_ms}ms process delay does not block caller ({enqueue_ms:.1f}ms)')
    need(wait_result(h, 'fault', delay_ms / 1000.0 + 1.0), f'{delay_ms}ms async process probe completes')
    hit = h._consume_click_target_probe('fault', 'cloudmusic')
    need(isinstance(hit, dict) and float(hit.get('elapsed_ms') or 0.0) >= delay_ms * 0.75,
         f'{delay_ms}ms delay occurs on verifier worker')
    if delay_ms >= 50:
        need(any('gui-block=0' in detail for title, detail in logs if title == '点击目标进程异步慢查询'),
             f'{delay_ms}ms slow verifier is diagnosed as gui-block=0')


# 2) NetEase's real page-interaction method must only enqueue the slow verifier.
ncm_globals = dict(common)
ncm_globals.update({'NETEASE_BRIDGE_PRIMARY_SUPPRESS_UIA_EXPERIMENTS': False})
ncm_poll = compile_method('MediaSessionSync', '_netease_poll_page_interaction', ncm_globals)
class NcmHarness(ProbeHarness):
    _netease_poll_page_interaction = ncm_poll
    def __init__(self):
        super().__init__(0.5, 'cloudmusic')
        self._process_hint = 'cloudmusic'
        self._netease_mouse_is_down = False
        self._netease_native_primary = False
    def _netease_click_zone(self, _cx, _cy):
        return 'transport'
    def _netease_apply_verified_page_interaction(self, _hit):
        raise AssertionError('no result should exist synchronously')
    def _netease_bridge_transport_should_suppress_uia(self):
        return False
FakeWin32Api.state = 0x0001
FakeWin32Api.cursor = (600, 900)
ncm = NcmHarness()
t0 = time.perf_counter(); ncm._netease_poll_page_interaction(); ncm_ms = (time.perf_counter() - t0) * 1000.0
need(ncm_ms < 40.0, f'NetEase click hot path survives 500ms process lookup ({ncm_ms:.1f}ms)')
need(wait_result(ncm, 'netease-page', 1.5), 'NetEase verifier completes out of band')


# 3) QQ's real non-rail gesture method gets the same injection.
qq_globals = dict(common)
qq_globals.update({
    'SYNC_AUTHORITY_ENABLED': True,
    'QQ_RAIL_VISUAL_DIRECT_ENABLED': False,
})
qq_poll = compile_method('MediaSessionSync', '_qq_poll_pointer_gesture', qq_globals)
class ReaderStub:
    def set_qq_gesture_candidate_quarantine(self, *_a, **_k): pass
    def request_urgent_scan(self, *_a, **_k): pass
class QqHarness(ProbeHarness):
    _qq_poll_pointer_gesture = qq_poll
    def __init__(self):
        super().__init__(0.5, 'qqmusic')
        self._process_hint = 'qqmusic'
        self._uia_reader = ReaderStub()
        self._qq_track_switch_hold_until_mono = 0.0
        self._qq_mouse_is_down = False
        self._qq_nonrail_mouse_down = False
        self._qq_nonrail_click_mono = -1e12
        self._qq_nonrail_click_until_mono = 0.0
        self._qq_progress_rect = None
        self._qq_gesture_recent_until_mono = 0.0
    def _qq_consume_lyric_click_candidate(self): return False
    def _qq_apply_verified_nonrail_click(self, _hit): raise AssertionError('no synchronous verifier result expected')
    def _qq_nonrail_seek_click_plausible(self, _cx, _cy): return True
FakeWin32Api.state = 0x0001
FakeWin32Api.cursor = (700, 700)
qq = QqHarness()
t0 = time.perf_counter(); qq._qq_poll_pointer_gesture(); qq_ms = (time.perf_counter() - t0) * 1000.0
need(qq_ms < 40.0, f'QQ non-rail click hot path survives 500ms process lookup ({qq_ms:.1f}ms)')
need(wait_result(qq, 'qq-nonrail', 1.5), 'QQ verifier completes out of band')


# 4) KuGou gets a stricter attack: both a real hook event and hook-failure polling are run
# while the old full window discovery primitive is made to sleep for a full second. Neither
# hot path is allowed to call it at all.
kg_globals = dict(common)
kg_globals.update({
    'KUGOU_GESTURE_SEEK_ENABLED': True,
    'KUGOU_GESTURE_LEARNED_Y_TOLERANCE_PX': 18.0,
    'KUGOU_GESTURE_DRAG_MIN_PX': 12.0,
    'KUGOU_GESTURE_VERTICAL_MAX_PX': 42.0,
    'KUGOU_GESTURE_X_MIN': 0.04,
    'KUGOU_GESTURE_X_MAX': 0.96,
    'KUGOU_GESTURE_BOTTOM_Y_MIN': 0.80,
    'KUGOU_GESTURE_BOTTOM_Y_MAX': 0.99,
})
kg_cached = compile_method('MediaSessionSync', '_kugou_hotpath_cached_window_rect', kg_globals)
kg_consume = compile_method('MediaSessionSync', '_kugou_consume_hooked_mouse_events', kg_globals)
kg_poll = compile_method('MediaSessionSync', '_kugou_poll_pointer_gesture', kg_globals)
class KgReaderStub:
    _kugou_last_main_rect = (0, 0, 1000, 800)
    def __init__(self): self.urgent = 0
    def request_urgent_scan(self, *_a, **_k): self.urgent += 1
class KgHarness:
    _kugou_hotpath_cached_window_rect = kg_cached
    _kugou_consume_hooked_mouse_events = kg_consume
    _kugou_poll_pointer_gesture = kg_poll
    def __init__(self, cached=True):
        self._process_hint = 'kgmusic'
        self._uia_reader = KgReaderStub()
        if not cached:
            self._uia_reader._kugou_last_main_rect = None
        self._kugou_physical_rect_cache = ((0, 0, 1000, 800) if cached else None)
        self._kugou_mouse_event_queue = queue.SimpleQueue()
        self._kugou_deferred_mouse_events = []
        self._kugou_mouse_is_down = False
        self._kugou_gesture_start = None
        self._kugou_gesture_last = None
        self._kugou_gesture_candidate = False
        self._kugou_rail_y = None
        self._kugou_mouse_event_last_diag_mono = 0.0
        self._kugou_mouse_diag_last_mono = 0.0
        self._kugou_mouse_hook_ready = True
        self._kugou_mouse_hook_failed = False
        self.slow_rect_calls = 0
    @staticmethod
    def _process_stem(value):
        value = str(value or '').lower()
        return value[:-4] if value.endswith('.exe') else value
    def _kugou_window_rect(self):
        self.slow_rect_calls += 1
        time.sleep(1.0)
        return (0, 0, 1000, 800)
    def _kugou_target_from_cursor(self, *_a, **_k): return None
    def _set_visual_seek_override(self, *_a, **_k): pass
    def _kugou_commit_gesture_seek(self, *_a, **_k): return False
    def _ensure_kugou_mouse_hook(self): return self._kugou_mouse_hook_ready

kg = KgHarness(cached=True)
kg._kugou_mouse_event_queue.put((0x0201, 500, 700, time.monotonic() * 1000.0))
t0 = time.perf_counter(); kg._kugou_consume_hooked_mouse_events(); kg_ms = (time.perf_counter() - t0) * 1000.0
need(kg_ms < 40.0 and kg.slow_rect_calls == 0,
     f'KuGou real hook event never calls 1000ms window discovery ({kg_ms:.1f}ms)')

kg_missing = KgHarness(cached=False)
kg_missing._kugou_mouse_event_queue.put((0x0201, 500, 700, time.monotonic() * 1000.0))
t0 = time.perf_counter(); kg_missing._kugou_consume_hooked_mouse_events(); kg_missing_ms = (time.perf_counter() - t0) * 1000.0
need(kg_missing_ms < 40.0 and kg_missing.slow_rect_calls == 0,
     f'KuGou missing-geometry hook event defers without discovery ({kg_missing_ms:.1f}ms)')
need(len(kg_missing._kugou_deferred_mouse_events) == 1 and kg_missing._uia_reader.urgent >= 1,
     'KuGou lossless hook edge is preserved until background geometry arrives')

FakeWin32Api.state = 0
FakeWin32Api.cursor = (500, 700)
kg_fallback = KgHarness(cached=True)
kg_fallback._kugou_mouse_hook_ready = False
kg_fallback._kugou_mouse_hook_failed = True
t0 = time.perf_counter(); kg_fallback._kugou_poll_pointer_gesture(); kg_fb_ms = (time.perf_counter() - t0) * 1000.0
need(kg_fb_ms < 40.0 and kg_fallback.slow_rect_calls == 0,
     f'KuGou hook-failure fallback never calls 1000ms discovery ({kg_fb_ms:.1f}ms)')


# 5) Atlas fault injection. A nominal 5-second decorative build cooperatively cancels at
# a short test budget and fuses to the existing sprite/fragment path. Scheduling itself must
# return immediately, proving the heavy work is not on the caller/GUI thread.
atlas_globals = {
    'time': time, 'threading': threading, 'os': os,
    'SONG_FRAGMENT_ATLAS_ENABLED': True,
    'SONG_FRAGMENT_ATLAS_BUILD_BUDGET_MS': 250.0,
    'SONG_FRAGMENT_ATLAS_INSTALL_FUSE_MS': 48.0,
    'write_error_log': log_stub,
}

def fake_build(_style_sig, _chars, cancel_check=None):
    started = time.perf_counter()
    while time.perf_counter() - started < 5.0:
        if cancel_check is not None and cancel_check():
            return {'cancelled': True, 'build_ms': (time.perf_counter() - started) * 1000.0}
        time.sleep(0.005)
    return {'cancelled': False, 'build_ms': 5000.0}

atlas_globals['_build_song_fragment_atlas_image'] = fake_build
schedule_atlas = compile_method('LyricWindow', '_schedule_song_fragment_atlas', atlas_globals)
install_globals = dict(atlas_globals)
class FakeTimer:
    @staticmethod
    def singleShot(_ms, _fn): pass
install_globals['QTimer'] = FakeTimer
class FakeRect:
    def __init__(self, *_a): pass
install_globals['QRectF'] = FakeRect
class FakePixmapObj:
    def isNull(self): return False
class FakePixmapFast:
    @staticmethod
    def fromImage(_image): return FakePixmapObj()
install_globals['QPixmap'] = FakePixmapFast
install_atlas = compile_method('LyricWindow', '_install_song_fragment_atlas', install_globals)

class SignalStub:
    def __init__(self): self.payload = None; self.event = threading.Event()
    def emit(self, payload): self.payload = payload; self.event.set()
class AtlasHarness:
    _schedule_song_fragment_atlas = schedule_atlas
    _install_song_fragment_atlas = install_atlas
    def __init__(self):
        self.lyric_timeline = [1]
        self._song_fragment_atlas_performance_fused = False
        self._song_fragment_atlas_fuse_reason = ''
        self._song_fragment_atlas_cache = {}
        self._song_fragment_atlas_key = None
        self._song_fragment_atlas_desired_key = None
        self._song_fragment_atlas_pending_key = None
        self._song_fragment_atlas_pixmap = None
        self._song_fragment_atlas_inflight = set()
        self._song_fragment_atlas_deferred = False
        self._song_fragment_atlas_serial = 0
        self._song_fragment_atlas_failures = 0
        self._song_fragment_atlas_stale_drop_count = 0
        self._song_fragment_atlas_perf_cancel_count = 0
        self.song_fragment_atlas_ready = SignalStub()
    def _song_fragment_chars_and_key(self, _visual_style=None): return ('abcdef', ('style', 'song'))
    def _current_fragment_style_signature(self): return 'style'
    def _reserve_song_fragment_atlas_capacity(self, _key, _pixels): return (0, 0.0)
    def _cache_song_fragment_atlas(self, *_a, **_k): pass
    def _activate_cached_song_fragment_atlas(self, *_a, **_k): pass

atlas = AtlasHarness()
t0 = time.perf_counter(); status = atlas._schedule_song_fragment_atlas(); sched_ms = (time.perf_counter() - t0) * 1000.0
need(status == 'scheduled' and sched_ms < 40.0, f'nominal 5s Atlas build is scheduled off GUI ({sched_ms:.1f}ms)')
need(atlas.song_fragment_atlas_ready.event.wait(1.5), 'Atlas cooperative budget returns worker payload')
payload = atlas.song_fragment_atlas_ready.payload
need(isinstance(payload, dict) and payload.get('cancelled') and payload.get('performance_cancelled'),
     'Atlas nominal 5s build is cancelled by performance budget')
atlas._install_song_fragment_atlas(payload)
need(atlas._song_fragment_atlas_performance_fused and 'build-budget' in atlas._song_fragment_atlas_fuse_reason,
     'slow Atlas build fuses to sprite/fragment fallback')
need(atlas._schedule_song_fragment_atlas() == 'performance-fused-style', 'fused Atlas cannot start another heavy worker for the same style')


# 6) A separate machine can have a fast worker but pathological QPixmap conversion. The
# first unavoidable GUI conversion is detected and permanently fuses subsequent atlas work.
class FakeImage:
    def isNull(self): return False
class FakePixmapSlow:
    @staticmethod
    def fromImage(_image):
        time.sleep(0.12)
        return FakePixmapObj()
slow_install_globals = dict(install_globals)
slow_install_globals['QPixmap'] = FakePixmapSlow
slow_install = compile_method('LyricWindow', '_install_song_fragment_atlas', slow_install_globals)
atlas2 = AtlasHarness()
atlas2._install_song_fragment_atlas = slow_install.__get__(atlas2, AtlasHarness)
key = ('style', 'song')
atlas2._song_fragment_atlas_desired_key = key
atlas2._song_fragment_atlas_inflight.add(key)
t0 = time.perf_counter()
atlas2._install_song_fragment_atlas({'key': key, 'image': FakeImage(), 'pixels': 1, 'meta': {}, 'build_ms': 10.0})
install_ms = (time.perf_counter() - t0) * 1000.0
need(install_ms >= 100.0, 'fault injector actually creates a slow GUI pixmap conversion')
need(atlas2._song_fragment_atlas_performance_fused and 'gui-install:' in atlas2._song_fragment_atlas_fuse_reason,
     'slow GUI Atlas install fuses all later atlas work')
need(atlas2._schedule_song_fragment_atlas() == 'performance-fused-style', 'post-install style fuse prevents repeat GUI stalls')

need('RUNTIME-ISOLATION CLOSURE H8F2' in source, 'H8F2 build tag present')
print('GUI HOTPATH FAULT INJECTION REPLAY: PASS')
print('  injected process lookup delays: 50/100/250/500/1000ms')
print('  injected KuGou window discovery delay: 1000ms (hook + hook-failure fallback)')
print('  injected Atlas nominal build: 5000ms; GUI conversion: 120ms')
