#!/usr/bin/env python3
from __future__ import annotations

import ast
import asyncio
import importlib.util
import queue
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / 'LimbusLyric_v1.8.9.133_CROSS_PROVIDER_TRANSLATION_CUSTOM_ADAPTER_FOUNDATION_20260814.py'
NATIVE = ROOT / 'limbus_netease_native.py'
src = MAIN.read_text(encoding='utf-8')
tree = ast.parse(src, filename=str(MAIN))

assert 'RUNTIME HARDENING H17' in src.splitlines()[63], 'H17 build tag missing'

# Every tasklist subprocess in the canonical main source must be deadline-bounded.  This
# includes the two historical PID lookup paths that were outside H11's liveness fallback.
tasklist_calls = []
for node in ast.walk(tree):
    if not isinstance(node, ast.Call):
        continue
    try:
        fn = ast.unparse(node.func)
    except Exception:
        continue
    if fn not in {'subprocess.run', 'subprocess.check_output', 'subprocess.Popen'}:
        continue
    arg0 = ast.unparse(node.args[0]) if node.args else ''
    if 'tasklist' not in arg0.lower():
        continue
    kws = {kw.arg for kw in node.keywords if kw.arg}
    tasklist_calls.append((node.lineno, fn, 'timeout' in kws))
assert tasklist_calls, 'no tasklist calls found'
assert all(has_timeout for _line, _fn, has_timeout in tasklist_calls), tasklist_calls

# NetEase native adapter must survive a full Stop -> fresh event loop -> Start.  A fake
# detector avoids any dependency on Windows/CloudMusic and exercises only adapter lifecycle.
spec = importlib.util.spec_from_file_location('limbus_netease_native_h17_test', NATIVE)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)

class FakeCloudMusic:
    def __init__(self):
        self._track_cb = None
        self._state_cb = None
        self._seek_cb = None
    def on_track_change(self, cb): self._track_cb = cb
    def on_state_change(self, cb): self._state_cb = cb
    def on_seek(self, cb): self._seek_cb = cb
    async def start(self):
        await asyncio.sleep(0)
    async def stop(self):
        await asyncio.sleep(0)

mod.AsyncCloudMusic = FakeCloudMusic
adapter = mod.NeteaseNativeClockAdapter()

async def lifecycle_cycle():
    loop = asyncio.get_running_loop()
    assert adapter.start_background() is True
    await asyncio.sleep(0)
    await asyncio.sleep(0)
    assert adapter._cm is not None
    assert adapter._loop is loop
    assert adapter._event is not None
    await adapter.stop_async()
    assert adapter._cm is None
    assert adapter._loop is None
    assert adapter._event is None

asyncio.run(lifecycle_cycle())
asyncio.run(lifecycle_cycle())

# Execute only H16/H17's pure UI-thread cover-result consumer.  Simulate two songs finishing
# out of order and then a stale/new same-song serial pair.  Old completions must never clear or
# overwrite the active newer request, and a non-current track may cache but may not recolor UI.
def function_node(name):
    return next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)

ns = {
    'queue': queue,
    'time': time,
    'H16_COVER_RETRY_SEC': (2.0, 6.0, 18.0),
    '_h12_poll_async': lambda panel: None,
    'write_error_log': lambda *args, **kwargs: None,
}
node = function_node('_h16_poll_runtime')
module = ast.Module(body=[node], type_ignores=[])
ast.fix_missing_locations(module)
exec(compile(module, str(MAIN), 'exec'), ns, ns)
poll = ns['_h16_poll_runtime']

class Panel:
    def __init__(self):
        self._loaded_song = 'B'
        self._loaded_artist = 'artist'
        self._h16_cover_cache = {}
        self._h16_cover_retry = {}
        self._h17_cover_active_requests = {'A|artist': 1, 'B|artist': 2}
        self._h17_cover_results = queue.SimpleQueue()
        self._h12_cover_result = None
        self.live_apply = 0
    def _track_identity(self, song, artist):
        return f'{song}|{artist}'
    def _apply_active_visual_style_live(self, reason=''):
        self.live_apply += 1

p = Panel()
p._h17_cover_results.put(('B|artist', 2, '#222222', ''))
p._h17_cover_results.put(('A|artist', 1, '#111111', ''))
poll(p)
assert p._h16_cover_cache == {'B|artist': '#222222', 'A|artist': '#111111'}, p._h16_cover_cache
assert p._h12_cover_result == ('B|artist', '#222222'), p._h12_cover_result
assert p._h17_cover_active_requests == {}, p._h17_cover_active_requests
assert p.live_apply == 1, p.live_apply

p._h17_cover_active_requests = {'B|artist': 4}
p._h17_cover_results.put(('B|artist', 3, '#oldold', ''))
p._h17_cover_results.put(('B|artist', 4, '#444444', ''))
poll(p)
assert p._h16_cover_cache['B|artist'] == '#444444', p._h16_cover_cache
assert p._h12_cover_result == ('B|artist', '#444444'), p._h12_cover_result
assert p._h17_cover_active_requests == {}, p._h17_cover_active_requests

print('RUNTIME HARDENING H17 REPLAY: PASS')
print(f'  tasklist subprocess deadline audit: PASS ({len(tasklist_calls)} calls)')
print('  NetEase native full Stop -> fresh-loop Start lifecycle: PASS')
print('  cover out-of-order/stale result generation isolation: PASS')
