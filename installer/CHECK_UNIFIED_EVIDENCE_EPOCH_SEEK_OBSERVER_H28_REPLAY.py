from pathlib import Path
import ast, sys, threading, time
from collections import OrderedDict

if len(sys.argv) != 2:
    raise SystemExit(2)
path = Path(sys.argv[1])
s = path.read_text(encoding='utf-8')

need = [
    'UNIFIED EVIDENCE EPOCH + SEEK OBSERVER H28',
    'H28酷狗歌词显示时钟代际隔离',
    'H28酷狗未知时长缓存已撤权',
    'H28酷狗Win10进度条观察几何就绪',
    'H28酷狗真实Seek观察已接管',
    'H28播放器存活PSAPI快路',
    'H28网易云时序物理Rail兜底已接管',
    "ControlPanel._record_loaded_track = _h28_record_loaded_track",
    "LyricWindow.upgrade_lyric_timeline_preserve_visual = _h28_precision_upgrade",
    "ControlPanel._load_auto_lyric_cache_from_disk = _h28_cache_load",
    "ControlPanel._start_auto_search_job = _h28_start_auto_search_job",
    "MediaSessionSync._kugou_window_rect = _h28_kugou_window_rect",
    "MediaSessionSync._kugou_commit_gesture_seek = _h28_kugou_commit_gesture_seek",
    "MediaSessionSync._h25_poll_netease_safe_visual_clock = _h28_netease_visual_clock",
    "_limbus_bounded_player_liveness_probe = _h28_bounded_player_liveness_probe",
]
for token in need:
    if token not in s:
        raise AssertionError('missing ' + token)

p27 = s.index('# H27 player-clock epoch')
p28 = s.index('# H28 unified evidence epoch')
pmain = s.index('if __name__ == "__main__":')
assert p27 < p28 < pmain
h28 = s[p28:pmain]

# Runtime ownership must be explicit: source presence is insufficient after H27's install-order bug.
for owner in (
    "MediaSessionSync._kugou_window_rect._limbus_layer = 'H28'",
    "MediaSessionSync._kugou_commit_gesture_seek._limbus_layer = 'H28'",
    "MediaSessionSync._h25_poll_netease_safe_visual_clock._limbus_layer = 'H28'",
    "ControlPanel._record_loaded_track._limbus_layer = 'H28'",
    "LyricWindow.upgrade_lyric_timeline_preserve_visual._limbus_layer = 'H28'",
):
    assert owner in h28

# Win10 KuGou geometry recovery is pure Win32/DWM and must not reintroduce accessibility/tasklist.
rect_src = h28[h28.index('def _h28_win32_kugou_host_rect'):h28.index('def _h28_publish_kugou_seek_geometry')]
for bad in ('pywinauto', 'Desktop(', 'WM_GETOBJECT', 'comtypes'):
    assert bad not in rect_src
for good in ('EnumWindows', 'GetClassNameW', 'DwmGetWindowAttribute', "clsname.lower() != 'kugou_ui'"):
    assert good in rect_src
assert 'H28_KUGOU_SAFE_RAIL_Y_RATIO = 0.895' in h28
assert 'authority=geometry-only' in h28

# Liveness fast path is positive-only and bypasses the old bounded Toolhelp/tasklist chain only on a hit.
psapi_src = h28[h28.index('def _h28_psapi_positive_process_alive'):h28.index('def _h28_bounded_player_liveness_probe')]
assert 'EnumProcesses' in psapi_src and 'QueryFullProcessImageNameW' in psapi_src
assert 'return False' not in psapi_src
probe_src = h28[h28.index('def _h28_bounded_player_liveness_probe'):h28.index('_limbus_bounded_player_liveness_probe = _h28_bounded_player_liveness_probe')]
assert "return True,'psapi-positive'" in probe_src
assert '_LIMBUS_H28_LIVENESS_PRE(self,stem)' in probe_src

# NetEase fallback can run only after H26 has remained proof-pending for a dwell period.
visual_src = h28[h28.index('def _h28_netease_visual_clock'):h28.index('MediaSessionSync._h25_poll_netease_safe_visual_clock = _h28_netease_visual_clock')]
assert '_LIMBUS_H28_NCM_VISUAL_PRE(self,status_hint)' in visual_src
assert "pending=bool(getattr(self,'_h26_netease_visual_pending_map',{}) or {})" in visual_src
assert 'H28_NETEASE_H26_PENDING_FALLBACK_MS' in visual_src
assert '_LIMBUS_H26_H25_VISUAL_PRE(self,status_hint)' in visual_src

# Pull selected H28 functions from the real AST and execute focused state replays.
tree = ast.parse(s)
func_nodes = {}
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith('_h28_'):
        func_nodes[node.name] = node

def load_func(name, env):
    node = func_nodes[name]
    mod = ast.Module(body=[node], type_ignores=[])
    ast.fix_missing_locations(mod)
    ns = dict(env)
    exec(compile(mod, str(path), 'exec'), ns, ns)
    return ns[name], ns

noop = lambda *a, **k: None

# Field regression: a new KuGou track must erase renderer-side 9152ms evidence and seed only
# the current MediaSync position (202ms in the observed log).
reset, _ = load_func('_h28_reset_lyric_epoch', {'time': time, 'write_error_log': noop})
class LW: pass
class Sync:
    _track_key = '少女a|鏡音リン'
    def snapshot(self): return {'position_ms': 202, 'position_source': 'kugou-rail-local-master'}
class Panel:
    lyric_window = LW(); media_sync = Sync()
    def _track_identity(self, s, a): return '少女a|鏡音リン'
panel = Panel()
panel.lyric_window._last_position_ms = 9152
panel.lyric_window._precision_handoff_pending = {'boundary_ms': 10000}
panel.lyric_window.history_lines = [1,2]
assert reset(panel, '少女A', '鏡音リン', reason='gate') is True
assert panel.lyric_window._last_position_ms == 202
assert panel.lyric_window._precision_handoff_pending is None
assert panel.lyric_window.history_lines == []

# Precision upgrade must refresh position from the same current epoch immediately before handoff.
def precise_pre(self, text):
    self._gate_seen_position = self._last_position_ms
    self._gate_seen_pending = self._precision_handoff_pending
    return True
upgrade, _ = load_func('_h28_precision_upgrade', {
    'time': time, 'H28_KUGOU_EPOCH_FRESH_MS': 4200.0,
    '_LIMBUS_H28_PRECISE_UPGRADE_PRE': precise_pre,
})
lw = LW(); lw._h28_epoch_started_mono = time.monotonic()*1000.0; lw._h28_media_sync_ref = Sync()
lw._last_position_ms = 9152; lw._precision_handoff_pending = {'old':1}; lw._precision_handoff_visible_floor = {'line':2}
assert upgrade(lw, '[00:00.00]x') is True
assert lw._gate_seen_position == 202 and lw._gate_seen_pending is None

# Unknown-duration KuGou cache entries are version-unsafe and must be removed; duration-keyed rows remain.
purge, _ = load_func('_h28_purge_unsafe_kugou_zero_duration_cache', {'write_error_log': noop})
class CacheObj:
    def __init__(self):
        self._auto_lyric_cache_lock = threading.Lock()
        self._auto_lyric_cache = OrderedDict()
c = CacheObj()
k0=('酷狗',False,True,'少女a|鏡音リン','鏡音リン',0)
k221=('酷狗',False,True,'少女a|鏡音リン','鏡音リン',221)
kqq=('QQ音乐',False,True,'少女a|鏡音リン','鏡音リン',0)
c._auto_lyric_cache[k0]={'duration':81000}; c._auto_lyric_cache[k221]={'duration':221000}; c._auto_lyric_cache[kqq]={'duration':81000}
assert purge(c, '少女a|鏡音リン') == 1
assert k0 not in c._auto_lyric_cache and k221 in c._auto_lyric_cache and kqq in c._auto_lyric_cache

# A committed real player rail event records an observation transaction; no mouse injection is added.
def commit_pre(self, target, now=None, reason='rail-gesture'): return True
commit, _ = load_func('_h28_kugou_commit_gesture_seek', {
    'time': time, 'write_error_log': noop, '_LIMBUS_H28_KUGOU_COMMIT_PRE': commit_pre,
})
class S: _track_key='track|artist'
ss=S(); assert commit(ss, 43000, now=1234.0, reason='hook-learned-click') is True
assert ss._h28_kugou_seek_observation['target_ms'] == 43000
assert ss._h28_kugou_seek_observation['track_key'] == 'track|artist'
assert 'SendInput' not in h28 and 'mouse_event(' not in h28

print('UNIFIED EVIDENCE EPOCH + SEEK OBSERVER H28 REPLAY: PASS')
print(' - KuGou transport and lyric-renderer clocks share a hard new-track epoch')
print(' - unknown-duration KuGou cache entries cannot select a same-name version')
print(' - Win10 KuGou seek observation gets pure Win32/DWM geometry without mouse injection')
print(' - PSAPI positive liveness bypasses slow tasklist; absence remains non-authoritative')
print(' - Win10 NetEase may use H25 temporal physical-rail proof only after H26 proof-pending dwell')
print(' - final runtime method ownership is explicitly H28-locked')
