from __future__ import annotations

import ast
import importlib.util
import sys
import time
from pathlib import Path
from types import SimpleNamespace

if len(sys.argv) != 2:
    raise SystemExit('usage: CHECK_NETEASE_CLOCK_IDENTITY_H45_REPLAY.py <main.py>')
main = Path(sys.argv[1]).resolve()
root = main.parent
source = main.read_text(encoding='utf-8')
tree = ast.parse(source, filename=str(main))
fail = []


def fsrc(name):
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return ast.get_source_segment(source, node)
    raise KeyError(name)


def clean_name(value):
    import re
    return re.sub(r'[^a-z0-9\u4e00-\u9fff]+', '', str(value or '').lower())


try:
    native_path = root / 'limbus_netease_native.py'
    spec = importlib.util.spec_from_file_location('_h45_native', native_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    placeholder = SimpleNamespace(id=0, name='', artist_str='', duration=0)
    adapter = mod.NeteaseNativeClockAdapter()
    adapter.available = True
    adapter._cm = SimpleNamespace(state=SimpleNamespace(track=placeholder, position=0, is_playing=False), track=placeholder)
    snap = adapter.snapshot()
    if snap.get('ready') is not False or snap.get('error') != 'track-identity-unavailable':
        fail.append('anonymous detector placeholder still becomes ready: ' + repr(snap))

    valid = SimpleNamespace(id=1830531332, name="World's Smallest Violin", artist_str='AJR', duration=180.793)
    adapter._cm = SimpleNamespace(state=SimpleNamespace(track=valid, position=0, is_playing=False), track=valid)
    snap = adapter.snapshot()
    if not snap.get('ready') or snap.get('status') != 'paused' or snap.get('position_ms') != 0:
        fail.append('legitimate paused-at-zero native track was rejected: ' + repr(snap))
    if str(snap.get('track_id')) != '1830531332' or clean_name(snap.get('title')) != clean_name("World's Smallest Violin"):
        fail.append('valid native identity was not preserved: ' + repr(snap))
except Exception as exc:
    fail.append('native parser replay: ' + repr(exc))


try:
    ns = {'_clean_name': clean_name}
    exec(fsrc('_h45_netease_native_identity_ok'), ns, ns)
    identity_ok = ns['_h45_netease_native_identity_ok']
    sync = SimpleNamespace(
        _track_key='worldssmallestviolin|ajr',
        _netease_bridge_bound_track_id='1830531332',
        _netease_bridge_expected_track_id='1830531332',
    )
    cases = [
        ({'title': '', 'track_id': ''}, False, 'anonymous-native-track'),
        ({'title': "World's Smallest Violin", 'track_id': ''}, True, 'bound-title-match'),
        ({'title': '', 'track_id': '1830531332'}, True, 'bound-track-id-match'),
        ({'title': 'Bones', 'track_id': '1830531332'}, False, 'title-mismatch'),
        ({'title': "World's Smallest Violin", 'track_id': '999'}, False, 'track-id-mismatch'),
    ]
    for snap, expected, reason in cases:
        got, got_reason = identity_ok(sync, snap)
        if got is not expected or got_reason != reason:
            fail.append(f'identity fence mismatch snap={snap!r}: got={(got, got_reason)!r} expected={(expected, reason)!r}')
except Exception as exc:
    fail.append('identity helper replay: ' + repr(exc))


try:
    logs = []

    class FakeSync:
        def __init__(self):
            self._process_hint = 'cloudmusic'
            self._track_key = 'worldssmallestviolin|ajr'
            self._netease_bridge_bound_track_id = '1830531332'
            self._netease_bridge_expected_track_id = '1830531332'
            self._netease_native_primary = True
            self._netease_native_last_position_ms = 0.0
            self._netease_native_last_mono = 1.0
            self._netease_native_last_track_key = '|'
            self._h38_ncm_player_duration_ms = 180793
            self._h38_ncm_player_duration_epoch = 4
            self._h38_ncm_player_duration_track = self._track_key
            self._h38_ncm_player_title = "World's Smallest Violin"
            self._h38_ncm_player_artist = 'AJR'
            self._h35_ncm_native_anchor = {'x': 1}
            self._h35_ncm_native_pending = {'x': 2}
            self._raw_snap = {'clock_ok': True, 'position_ms': 0, 'status': 'paused', 'title': '', 'artist': '', 'track_id': '', 'confidence': 252}

        @staticmethod
        def _process_stem(value):
            return str(value or '').lower().replace('.exe', '')

    class FakeMedia:
        @staticmethod
        def _poll_netease_native_clock(sync, status_hint='unknown'):
            return dict(sync._raw_snap)

        @staticmethod
        def bind_track(sync, song, artist='', duration_ms=0, auto_provisional=False,
                       initial_position_ms=0, netease_track_id=None, startup_existing=False):
            sync._track_key = f'{clean_name(song)}|{clean_name(artist)}'
            sync._netease_bridge_bound_track_id = str(netease_track_id or '')
            sync._netease_bridge_expected_track_id = str(netease_track_id or '')
            return True

    ns = {
        '_clean_name': clean_name,
        'time': time,
        'write_error_log': lambda *a, **k: logs.append((a, k)),
        'H45_NETEASE_INVALID_LOG_INTERVAL_MS': 8000.0,
        'MediaSessionSync': FakeMedia,
    }
    for name in ('_h45_netease_native_identity_ok', '_h45_clear_netease_native_track_witness', '_h45_activate_runtime'):
        exec(fsrc(name), ns, ns)
    ns['_h45_activate_runtime']()

    obj = FakeSync()
    out = FakeMedia._poll_netease_native_clock(obj, 'playing')
    if out.get('clock_ok') is not False or out.get('authority_rejected') != 'anonymous-native-track':
        fail.append('runtime fence did not revoke anonymous native clock: ' + repr(out))
    if obj._netease_native_primary is not False:
        fail.append('anonymous native clock still suppresses fallback via _netease_native_primary')
    if obj._h38_ncm_player_duration_ms != 0 or obj._h38_ncm_player_duration_epoch != -1:
        fail.append('stale H38 NetEase duration witness survived rejection')
    if obj._h35_ncm_native_anchor is not None or obj._h35_ncm_native_pending is not None:
        fail.append('stale H35 NetEase seek witness survived rejection')

    obj = FakeSync()
    obj._raw_snap = {
        'clock_ok': True, 'position_ms': 0, 'status': 'paused',
        'title': "World's Smallest Violin", 'artist': 'AJR', 'track_id': '1830531332', 'confidence': 252,
    }
    out = FakeMedia._poll_netease_native_clock(obj, 'paused')
    if not out.get('clock_ok') or obj._netease_native_primary is not True:
        fail.append('valid exact native clock was altered by H45: ' + repr(out))

    obj._h38_ncm_player_duration_ms = 180793
    obj._h38_ncm_player_duration_epoch = 4
    obj._h38_ncm_player_title = "World's Smallest Violin"
    FakeMedia.bind_track(obj, 'Bones', 'Imagine Dragons', 165264, netease_track_id='1927389937')
    if obj._h38_ncm_player_duration_ms != 0 or obj._h38_ncm_player_duration_epoch != -1 or obj._h38_ncm_player_title:
        fail.append('new NetEase bind did not retire previous native duration identity')
except Exception as exc:
    fail.append('runtime wrapper replay: ' + repr(exc))


required = (
    '+ NETEASE CLOCK IDENTITY RECOVERY H45',
    "MediaSessionSync._poll_netease_native_clock._limbus_layer = 'H45'",
    "MediaSessionSync.bind_track._limbus_layer = 'H45'",
    "if '_h45_activate_runtime' in globals():",
    '_h45_activate_runtime()',
    "native_transport_fast = bool(\n                    proc_hint_pre == 'cloudmusic' and native_ui is not None and native_ui.get('clock_ok')",
)
for token in required:
    if token not in source:
        fail.append('missing H45 integration token: ' + token[:90])

if fail:
    print('NETEASE CLOCK IDENTITY H45 REPLAY: FAIL')
    for row in fail:
        print(' -', row)
    raise SystemExit(1)
print('NETEASE CLOCK IDENTITY H45 REPLAY: PASS')
