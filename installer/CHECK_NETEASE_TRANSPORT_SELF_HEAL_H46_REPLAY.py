from __future__ import annotations

import ast
import importlib.util
import sys
import time
from pathlib import Path
from types import SimpleNamespace

if len(sys.argv) != 2:
    raise SystemExit('usage: CHECK_NETEASE_TRANSPORT_SELF_HEAL_H46_REPLAY.py <main.py>')
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


try:
    native_path = root / 'limbus_netease_native.py'
    spec = importlib.util.spec_from_file_location('_h46_native', native_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    adapter = mod.NeteaseNativeClockAdapter()
    adapter.available = True
    bad = SimpleNamespace(id=-1, name='', artist_str='', duration=0)
    adapter._cm = SimpleNamespace(state=SimpleNamespace(track=bad, position=0, is_playing=False), track=bad)
    snap = adapter.snapshot()
    if snap.get('ready') is not False or snap.get('error') != 'track-identity-unavailable':
        fail.append('id=-1 placeholder still becomes a ready native clock: ' + repr(snap))

    good = SimpleNamespace(id=1873089339, name='Rescue Me', artist_str='OneRepublic', duration=159.650)
    adapter._cm = SimpleNamespace(state=SimpleNamespace(track=good, position=0, is_playing=False), track=good)
    snap = adapter.snapshot()
    if not snap.get('ready') or snap.get('status') != 'paused' or str(snap.get('track_id')) != '1873089339':
        fail.append('legitimate positive-id paused-at-zero track was damaged: ' + repr(snap))
except Exception as exc:
    fail.append('native -1 sentinel replay: ' + repr(exc))


try:
    import re
    ns = {'_clean_name': lambda v: re.sub(r'[^a-z0-9\u4e00-\u9fff]+', '', str(v or '').lower())}
    exec(fsrc('_h45_netease_native_identity_ok'), ns, ns)
    sync = SimpleNamespace(
        _track_key='rescueme|onerepublic',
        _netease_bridge_bound_track_id='1873089339',
        _netease_bridge_expected_track_id='1873089339',
    )
    ok, reason = ns['_h45_netease_native_identity_ok'](sync, {'title': '', 'track_id': '-1'})
    if ok or reason != 'anonymous-native-track':
        fail.append(f'H45 outer fence accepted -1 sentinel: {(ok, reason)!r}')
except Exception as exc:
    fail.append('H45 -1 outer-fence replay: ' + repr(exc))


try:
    logs = []

    class FakeMedia:
        @staticmethod
        def _poll_netease_native_clock(sync, status_hint='unknown'):
            return dict(sync.raw_native)

        @staticmethod
        def _merge_uia_position(sync, process_name, status, fallback_position, fallback_trusted=False):
            sync.legacy_merge_calls += 1
            return 2210, {'position_ms': 2210, 'source': 'stale-uia'}

    class FakeSync:
        def __init__(self):
            self.raw_native = {
                'clock_ok': False, 'authority_rejected': 'track-id-mismatch',
                'status': 'paused', 'position_ms': 0, 'title': '', 'track_id': '-1'
            }
            self._uia_duration_ms = 159650
            self._uia_position_ms = 2210.0
            self._uia_anchor_mono = 1.0
            self._uia_status = 'paused'
            self._uia_has_lock = True
            self._uia_provisional = True
            self._uia_provisional_started_mono = 1.0
            self._uia_locked_source_key = 'stale'
            self._uia_locked_source_name = 'stale-uia'
            self._uia_initial_pending = {'x': 1}
            self._uia_pending_far = {'x': 1}
            self._playing_seek_pending = {'x': 1}
            self._paused_seek_pending = {'x': 1}
            self._est_position_ms = 2210.0
            self._est_anchor_mono = 1.0
            self._est_status = 'paused'
            self._est_source = 'cloudmusic.exe'
            self._h46_ncm_native_quarantine_until_mono = 0.0
            self._h46_ncm_recovery_log_mono = 0.0
            self.legacy_merge_calls = 0

        @staticmethod
        def _process_stem(value):
            return str(value or '').lower().replace('.exe', '')

    ns = {
        'MediaSessionSync': FakeMedia,
        'time': time,
        'write_error_log': lambda *a, **k: logs.append((a, k)),
        '_h24_netease_win10_frozen_no_accessibility': lambda process_name='cloudmusic.exe': True,
        'H46_NETEASE_NATIVE_QUARANTINE_MS': 12000.0,
        'H46_NETEASE_RECOVERY_LOG_INTERVAL_MS': 8000.0,
    }
    exec(fsrc('_h46_activate_runtime'), ns, ns)
    ns['_h46_activate_runtime']()

    obj = FakeSync()
    rejected = FakeMedia._poll_netease_native_clock(obj, 'playing')
    if rejected.get('status') != 'unknown' or rejected.get('native_status_observed') != 'paused':
        fail.append('rejected native paused state still owns transport: ' + repr(rejected))
    if rejected.get('transport_ok') is not False or not rejected.get('transport_authority_rejected'):
        fail.append('rejected native transport did not fail closed: ' + repr(rejected))

    outputs = []
    for pos in (148781, 150401, 157457, 168761):
        out, ui = FakeMedia._merge_uia_position(obj, 'cloudmusic.exe', 'playing', pos, fallback_trusted=True)
        outputs.append(out)
        if ui.get('source') != 'ncm-win32-gsmtc-safe':
            fail.append('Win10 safe merge did not publish GSMTC recovery source: ' + repr(ui))
            break
    if outputs != sorted(outputs) or outputs[-1] - outputs[0] < 15000:
        fail.append('field-style GSMTC sequence did not remain advancing: ' + repr(outputs))
    if obj._uia_status != 'playing' or obj._est_status != 'playing':
        fail.append(f'stale paused state survived self-heal: uia={obj._uia_status} est={obj._est_status}')
    if int(obj._uia_position_ms) != 168761 or int(obj._est_position_ms) != 168761:
        fail.append('shared anchors were not repaired to GSMTC')
    if obj.legacy_merge_calls != 0:
        fail.append('affected Win10 direct GSMTC path still entered stale legacy UIA merge')

    obj.raw_native = {
        'clock_ok': True, 'status': 'paused', 'position_ms': 0,
        'title': 'Rescue Me', 'track_id': '1873089339'
    }
    good = FakeMedia._poll_netease_native_clock(obj, 'paused')
    if good.get('status') != 'paused' or not good.get('clock_ok'):
        fail.append('valid native paused transport was altered by H46: ' + repr(good))
except Exception as exc:
    fail.append('H46 runtime replay: ' + repr(exc))


try:
    ns = {}
    exec(fsrc('_h46_auto_transition_waiting'), ns, ns)
    waiting = ns['_h46_auto_transition_waiting']

    class Check:
        def __init__(self, value): self.value = value
        def isChecked(self): return self.value

    panel = SimpleNamespace(
        auto_track_check=Check(True), _auto_overlay_suspended=True,
        _auto_fetch_in_progress=True, _auto_target_key='rescueme|onerepublic',
        _loaded_track_key='westcoast|onerepublic'
    )
    if not waiting(panel):
        fail.append('new-track in-flight transaction was not recognized as waiting')
    panel._auto_fetch_in_progress = False
    if waiting(panel):
        fail.append('ordinary launch failure was incorrectly treated as in-flight')

    start_tokens = (
        'if _h46_auto_transition_waiting(self):',
        'self._is_started = True',
        'self._auto_armed = True',
        'H46新曲搜索期间开始保持武装',
    )
    if not all(token in source for token in start_tokens):
        fail.append('ControlPanel.start missing H46 transaction-preservation wiring')
except Exception as exc:
    fail.append('auto transaction replay: ' + repr(exc))


required = (
    '+ NETEASE TRANSPORT SELF-HEAL H46',
    "out['status'] = 'unknown'",
    "MediaSessionSync._poll_netease_native_clock._limbus_layer = 'H46'",
    "MediaSessionSync._merge_uia_position._limbus_layer = 'H46'",
    "'source': 'ncm-win32-gsmtc-safe' if h24_safe else 'ncm-win32-gsmtc-recovery'",
    "if '_h46_activate_runtime' in globals():",
    '_h46_activate_runtime()',
    'if _h46_auto_transition_waiting(self):',
)
for token in required:
    if token not in source:
        fail.append('missing H46 integration token: ' + token[:100])

if fail:
    print('NETEASE TRANSPORT SELF-HEAL H46 REPLAY: FAIL')
    for row in fail:
        print(' -', row)
    raise SystemExit(1)
print('NETEASE TRANSPORT SELF-HEAL H46 REPLAY: PASS')
