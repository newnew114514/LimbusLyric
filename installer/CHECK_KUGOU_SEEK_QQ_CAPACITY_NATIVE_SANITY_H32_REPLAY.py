from __future__ import annotations
import importlib.util, sys, types
from pathlib import Path

if len(sys.argv)!=2:
    raise SystemExit('usage: CHECK_KUGOU_SEEK_QQ_CAPACITY_NATIVE_SANITY_H32_REPLAY.py <main.py>')
main=Path(sys.argv[1]).resolve(); root=main.parent
src=main.read_text(encoding='utf-8')
assert 'KUGOU SEEK OBSERVER + QQ CAPACITY + NATIVE POSITION SANITY H32' in src
start=src.index('# H32 KuGou seek observer / QQ capacity / native position sanity closure')
end=src.index('# H31 legacy-reference native + continuity clock closure',start)
block=src[start:end]
assert "source=GetAsyncKeyState+cached-rail" in block
assert 'injection=0' in block
for forbidden in ('SendInput(', 'mouse_event(', 'SetCursorPos('):
    assert forbidden not in block, f'H32 must observe, never inject: {forbidden}'
assert "LyricWindow._netease_renderer_active=_h32_renderer_active" in block
assert "LyricWindow._release_provider_idle_visual=_h32_provider_idle_release" in block
assert "MediaSessionSync._kugou_poll_pointer_gesture=_h32_kugou_pointer" in block
assert "MediaSessionSync.snapshot=_h32_snapshot" in block
# H32 definitions must stay outside the H31 replay extraction; only guarded activation follows H31.
h31=src.index('# H31 legacy-reference native + continuity clock closure')
guard=src.index("if '_h32_activate_runtime' in globals():",h31)
main_guard=src.index('\nif __name__ == "__main__":',h31)
assert h31 < guard < main_guard

# Native adapter position-unit/range normalization: seconds, milliseconds, and epoch-like garbage.
fake_mod=types.ModuleType('cloudmusic_detector')
class DummyAsyncCloudMusic: pass
fake_mod.AsyncCloudMusic=DummyAsyncCloudMusic
sys.modules['cloudmusic_detector']=fake_mod
spec=importlib.util.spec_from_file_location('_h32_native',root/'limbus_netease_native.py')
native=importlib.util.module_from_spec(spec); spec.loader.exec_module(native)
class Track:
    name='Song'; artist='Artist'; duration=221.5; id=7
class State:
    track=Track(); is_playing=True
class CM: pass
def native_snapshot(position):
    State.position=position; cm=CM(); cm.state=State()
    ad=native.NeteaseNativeClockAdapter(); ad._cm=cm
    return ad.snapshot()
a=native_snapshot(42.5); assert a['ready'] and int(a['position_ms'])==42500, a
b=native_snapshot(112518.0); assert b['ready'] and int(b['position_ms'])==112518, b
c=native_snapshot(1788096637.457); assert not c['ready'] and c.get('error')=='invalid-position-range', c

# Runtime replay for final ownership, QQ capacity and geometry-only KuGou seed.
class FakeTime:
    def __init__(self): self.ms=10000.0
    def monotonic(self): return self.ms/1000.0
ft=FakeTime(); logs=[]
def write_error_log(*a,**kw): logs.append((a,kw))
class FakeOS: name='nt'
class Reader:
    _kugou_last_main_rect=None
class MediaSessionSync:
    def __init__(self):
        self._process_hint='kgmusic'; self._track_key='song|artist'; self._uia_reader=Reader()
        self._kugou_host_v2_cache={'rect':(100,50,1100,650)}; self._kugou_host_v2_cache_mono=10000.0
        self._kugou_physical_rect_cache=None; self._kugou_visual_rail_bounds=None; self._kugou_rail_y=None
        self._kugou_gesture_id=0; self._kugou_last_gesture_mono=0.0; self._uia_duration_ms=200000
        self._state={'duration_ms':200000}; self._fixture={}
        self._netease_native_transition_started_mono=0.0; self._h31_ncm_continuity={'x':1}
    @staticmethod
    def _process_stem(v): return str(v).lower().replace('.exe','')
    def snapshot(self): return dict(self._fixture)
    def _kugou_poll_pointer_gesture(self): return None
    def _kugou_target_from_cursor(self,cx,rect=None):
        x0,x1=self._kugou_visual_rail_bounds; return max(0,min(1,(cx-x0)/(x1-x0)))*self._uia_duration_ms
    def _kugou_commit_gesture_seek(self,target,now=None,reason='x'): self._committed=(target,reason); self._kugou_last_gesture_mono=float(now or 0); return True
class LyricWindow:
    def __init__(self):
        self._last_sync_source='QQMusic.exe'; self._last_sync_position_source='qq-gsmtc'; self.max_visible_subtitles=3
        self.history_lines=['h1','h2']; self._h32_qq_capacity_logged=False; self.updated=0
    def _netease_renderer_active(self): return False
    def _release_provider_idle_visual(self,*a): self.history_lines=[]; return True
    def _enforce_visual_stack_limit(self): return 0
    def update(self): self.updated+=1

def _h31_ncm_reset_continuity(sync,reason='x'): sync._h31_ncm_continuity=None
ns={'MediaSessionSync':MediaSessionSync,'LyricWindow':LyricWindow,'time':ft,'os':FakeOS(),
    'write_error_log':write_error_log,'win32api':None,'ctypes':types.SimpleNamespace(),
    'wintypes':types.SimpleNamespace(),'KUGOU_GESTURE_LEARNED_Y_TOLERANCE_PX':22.0,
    'KUGOU_GESTURE_DRAG_MIN_PX':18.0,'KUGOU_GESTURE_VERTICAL_MAX_PX':34.0,
    'H28_KUGOU_SAFE_RAIL_Y_RATIO':0.895,'H28_KUGOU_SAFE_RAIL_X0_RATIO':0.035,'H28_KUGOU_SAFE_RAIL_X1_RATIO':0.965,
    '_h31_ncm_reset_continuity':_h31_ncm_reset_continuity}
exec(compile(block,'<h32>','exec'),ns,ns)
ns['_h32_activate_runtime']()
assert getattr(MediaSessionSync.snapshot,'_limbus_layer','')=='H32'
assert getattr(MediaSessionSync._kugou_poll_pointer_gesture,'_limbus_layer','')=='H32'
# Cached HostV2 is enough to publish a direct-click rail; no visual lock required.
s=MediaSessionSync(); rect=ns['_h32_seed_kugou_seek_geometry'](s)
assert rect==(100,50,1100,650), rect
x0,x1=s._kugou_visual_rail_bounds; assert 130 < x0 < 140 and 1060 < x1 < 1070, (x0,x1)
assert 580 < s._kugou_rail_y < 590, s._kugou_rail_y
assert ns['_h32_kugou_point_on_rail'](s,(x0+x1)/2,s._kugou_rail_y,rect)
target=s._kugou_target_from_cursor((x0+x1)/2,rect); assert 99000 <= target <= 101000, target
# QQ opts into capacity semantics and provider-idle release preserves held history.
w=LyricWindow(); assert w._netease_renderer_active() is True
assert w._release_provider_idle_visual(2,5000,(5000,4500,9000)) is True
assert w.history_lines==['h1','h2'], w.history_lines
# NetEase detector track edge revokes an H31 continuity frame before new ControlPanel bind.
s2=MediaSessionSync(); s2._process_hint='cloudmusic'; s2._fixture={'position_ms':72226,'position_source':'ncm-trusted-continuity-local','status':'playing','continuity_clock':True}
s2._netease_native_transition_started_mono=9500.0
out=s2.snapshot(); assert out['position_ms'] is None and out['position_source']=='ncm-native-track-transition-wait', out
assert s2._h31_ncm_continuity is None
print('KUGOU SEEK + QQ CAPACITY + NATIVE SANITY H32 REPLAY: PASS')
print(' - native 2.0.6 position is normalized against duration; wall-clock values are rejected')
print(' - cached KuGou HostV2 geometry enables direct seek observation without a visual lock')
print(' - KuGou H32 observer is hook+poll and contains no mouse injection')
print(' - QQ uses capacity residency and preserves held history across provider-idle release')
print(' - a NetEase detector track edge revokes old H31 presentation continuity immediately')
