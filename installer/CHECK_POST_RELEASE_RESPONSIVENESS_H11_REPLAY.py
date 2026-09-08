#!/usr/bin/env python3
from __future__ import annotations
import ast
import re
import sys
import threading
import time
from pathlib import Path
from types import SimpleNamespace

if len(sys.argv) != 2:
    raise SystemExit('usage: CHECK_POST_RELEASE_RESPONSIVENESS_H11_REPLAY.py <main.py>')
main = Path(sys.argv[1]).resolve()
src = main.read_text(encoding='utf-8')
tree = ast.parse(src, filename=str(main))


def fail(msg):
    print('POST-RELEASE RESPONSIVENESS H11 REPLAY: FAIL')
    print('  -', msg)
    raise SystemExit(1)


def need(cond, msg):
    if not cond:
        fail(msg)


def fn(name):
    matches = [node for node in ast.walk(tree)
               if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        fail('function missing: ' + name)
    fail(f'function ambiguous: {name} ({len(matches)})')


def fn_src(name):
    return ast.get_source_segment(src, fn(name)) or ''


def compile_fn(name, ns):
    node = fn(name)
    mod = ast.Module(body=[node], type_ignores=[])
    ast.fix_missing_locations(mod)
    exec(compile(mod, str(main), 'exec'), ns)
    return ns[name]

need('POST-RELEASE RESPONSIVENESS H11' in src, 'H11 build marker missing')

# -------------------------------------------------------------------------
# 1. GUI-side QQ/NetEase control operations must be fire-and-forget.
for token in (
    'MediaSessionSync._qq_poll_pointer_gesture = _limbus_qq_poll_pointer_gesture_nonblocking',
    'MediaSessionSync._netease_poll_page_interaction = _limbus_netease_poll_page_interaction_nonblocking',
    'MediaSessionSync._netease_poll_hover_refresh = _limbus_netease_poll_hover_refresh_nonblocking',
    "name=f'LimbusLyric-Control-{channel}'",
    'daemon=True',
    'CALL_WATCHDOG',
):
    need(token in src, 'GUI control isolation wiring missing: ' + token)

logs = []
ns = {
    'threading': threading, 'time': time,
    'write_error_log': lambda *a, **k: logs.append((a, k)),
    '_LIMBUS_GUI_CONTROL_INIT_LOCK': threading.Lock(),
}
for name in ('_limbus_gui_control_state', '_limbus_gui_control_watchdog',
             '_limbus_ensure_gui_control_worker', '_limbus_request_gui_control_poll'):
    compile_fn(name, ns)

class ControlObj: pass
obj = ControlObj()
slow_started = threading.Event()
slow_done = threading.Event()
def slow_call(_self):
    slow_started.set(); time.sleep(0.24); slow_done.set()
t0 = time.perf_counter()
need(ns['_limbus_request_gui_control_poll'](obj, 'fault', 'fault-op', slow_call) is True,
     'GUI control request failed')
elapsed = (time.perf_counter() - t0) * 1000.0
need(elapsed < 60.0, f'GUI control request waited for injected slow call: {elapsed:.1f}ms')
need(slow_started.wait(0.12), 'GUI control worker did not start injected call')
t1 = time.perf_counter()
ns['_limbus_request_gui_control_poll'](obj, 'fault', 'fault-op', slow_call)
need((time.perf_counter() - t1) * 1000.0 < 60.0, 'coalesced GUI request blocked')
need(len(getattr(obj, '_limbus_gui_control_poll_state')['threads']) == 1,
     'slow GUI control spawned replacement/unbounded worker')
need(slow_done.wait(0.6), 'injected GUI control did not finish in replay')

# -------------------------------------------------------------------------
# 2. A stuck Toolhelp helper is disposable; late native answers are stale-dropped.
class MediaStub:
    @staticmethod
    def _process_stem(v): return str(v or '').lower().replace('.exe','')

native_calls = []
fallback_calls = []
def slow_native(stem):
    native_calls.append(stem); time.sleep(0.13); return True
fallback_values = [False, False, False]
def fallback(stem):
    fallback_calls.append(stem)
    return fallback_values[min(len(fallback_calls)-1, len(fallback_values)-1)]

ns2 = {
    'threading': threading, 'time': time,
    'MediaSessionSync': MediaStub,
    '_LIMBUS_GUI_CONTROL_INIT_LOCK': threading.Lock(),
    '_LIMBUS_PROBE_BUILTIN_PROCESS_ALIVE_LOCKED': slow_native,
    '_LIMBUS_LIVENESS_NATIVE_BUDGET_MS': 20.0,
    '_limbus_liveness_tasklist_probe': fallback,
    'write_error_log': lambda *a, **k: None,
}
compile_fn('_limbus_liveness_native_slot', ns2)
compile_fn('_limbus_bounded_player_liveness_probe', ns2)
lobj = SimpleNamespace()
t0 = time.perf_counter()
r1, source1 = ns2['_limbus_bounded_player_liveness_probe'](lobj, 'kgmusic')
ms = (time.perf_counter() - t0) * 1000.0
need(ms < 100.0 and r1 is False and source1 == 'tasklist',
     f'bounded liveness failed to escape native sleep: {ms:.1f}ms {r1=} {source1=}')
time.sleep(0.16)  # native True arrives late and must not be published
r2, source2 = ns2['_limbus_bounded_player_liveness_probe'](lobj, 'kgmusic')
need(r2 is False and source2 == 'tasklist-after-stale-toolhelp',
     f'late Toolhelp answer was not stale-dropped: {r2=} {source2=}')
need(len(native_calls) == 1, 'quarantined helper unexpectedly spawned replacement before retirement')

# tasklist fallback must fail unknown rather than publish false-dead on command failure/blank output.
class FakeTimeoutExpired(Exception): pass
class FakeSubprocess:
    CREATE_NO_WINDOW = 0
    TimeoutExpired = FakeTimeoutExpired
    def __init__(self, rows): self.rows = list(rows)
    def run(self, *a, **k): return self.rows.pop(0)
class FakeOS: name = 'nt'
class TaskMediaStub:
    @staticmethod
    def _process_stem(v): return str(v or '').lower().replace('.exe','')
rows = [
    SimpleNamespace(returncode=1, stdout=''),
    SimpleNamespace(returncode=0, stdout='   '),
    SimpleNamespace(returncode=0, stdout='\"KuGou.exe\",\"123\",\"Console\",\"1\",\"1,234 K\"\n'),
    SimpleNamespace(returncode=0, stdout='\"explorer.exe\",\"321\",\"Console\",\"1\",\"2,345 K\"\n'),
]
ns2b = {
    'os': FakeOS(), 'subprocess': FakeSubprocess(rows), 'MediaSessionSync': TaskMediaStub,
    '_LIMBUS_LIVENESS_TASKLIST_TIMEOUT_S': 0.8,
}
task_probe = compile_fn('_limbus_liveness_tasklist_probe', ns2b)
need(task_probe('kgmusic') is None, 'tasklist nonzero exit was published as player-dead')
need(task_probe('kgmusic') is None, 'tasklist blank stdout was published as player-dead')
need(task_probe('kgmusic') is True, 'tasklist valid KuGou row was not recognized')
need(task_probe('kgmusic') is False, 'tasklist valid non-KuGou listing did not publish player-dead')

# -------------------------------------------------------------------------
# 3. QQ status=unknown may bootstrap only from a strict validated advancing stream.
ns3 = {'_LIMBUS_QQ_INITIAL_ANCHOR_STREAM_STEP_LOCKED': lambda *a, **k: ('legacy', True)}
step = compile_fn('_limbus_qq_initial_anchor_stream_step_unknown_safe', ns3)
p = None
proof = False
for i in range(4):
    p, proof = step(p, i * 350.0, i * 350.0, 'unknown',
                    'qq-time-pair-validated', 'same', 180)
need(proof is True and int(p.get('samples',0)) >= 4, 'validated unknown advancing stream did not prove playback')
p, proof = step(None, 5000, 0, 'unknown', 'qq-time-pair-validated', 'same', 180)
p, proof = step(p, 5000, 350, 'unknown', 'qq-time-pair-validated', 'same', 180)
need(proof is False, 'static unknown/hover-like value incorrectly proved playback')
p, proof = step(None, 0, 0, 'unknown', 'qq-time-pair-candidate', 'same', 220)
need(p is None and proof is False, 'candidate QQ time was accepted in unknown fallback')
need(step(None, 0, 0, 'playing', 'x', 'x', 0) == ('legacy', True),
     'explicit playing path no longer delegates to source-locked baseline')

# -------------------------------------------------------------------------
# 4. Manual precise fetch: fast ordinary payload arrives before injected slow precision.
class EngineStub:
    last_error = ''
    local = threading.local()
    @classmethod
    def _set_cancel_check(cls, f=None): cls.local.cancel = f
    @classmethod
    def last_provider_meta(cls): return {'test': True}
    @classmethod
    def search(cls, song, artist, source, trans_only, provider_duration_ms=0, prefer_precise=False, **_policy):
        if prefer_precise:
            time.sleep(0.25)
            return '[00:00.00]<0,500>precise', 1000
        return '[00:00.00]fast', 1000

manual_events=[]
ns4 = {
    'time': time, 'LyricSearchEngine': EngineStub,
    'write_error_log': lambda *a, **k: None,
    '_lyric_clock_quality': lambda text: 2 if '<' in str(text) else 1,
}
manual_worker = compile_fn('_manual_fetch_search_worker', ns4)
class ManualObj:
    _manual_fetch_generation = 7; _quitting = False
    def _manual_fetch_emit(self, row): manual_events.append(dict(row))
    def _manual_validate_qq_result(self, req, lyric, duration, error): return lyric, duration, error
mobj=ManualObj()
req={'generation':7,'source':'酷狗','trans_only':False,'prefer_precise':True,'song':'S','artist':'A','provider_duration_ms':1000}
th=threading.Thread(target=manual_worker,args=(mobj,req),daemon=True); th.start()
limit=time.monotonic()+0.12
while time.monotonic()<limit and not manual_events: time.sleep(0.005)
need(manual_events and manual_events[0].get('stage') == 'fast',
     'manual precise transaction did not emit ordinary fast payload before slow precision')
mobj._manual_fetch_generation = 8  # cancel old precision transaction
th.join(0.5)
need(not th.is_alive(), 'manual precision worker ignored generation cancellation after injected delay')
need('QTimer.singleShot(18000' in fn_src('_start_manual_fetch_search'), 'manual transaction total UI budget missing')
need('daemon=True' in fn_src('_start_manual_fetch_search'), 'manual search worker is not daemon')

# -------------------------------------------------------------------------
# 5. trans_only failure preserves user setting and presentation remains blank.
locked_calls=[]
class Toggle:
    def __init__(self,v): self.v=v
    def isChecked(self): return self.v
class Combo:
    def __init__(self,v): self.v=v
    def currentText(self): return self.v
class Status:
    def setText(self,t): self.text=t
class LW:
    def stop_lyric(self): self.stopped=True
    def hide(self): self.hidden=True

ns5={
    '_LIMBUS_MODE_LYRIC_RESULT_LOCKED': lambda self,result: locked_calls.append(result),
    'write_error_log': lambda *a,**k: None,
}
mode_result=compile_fn('_limbus_mode_lyric_result_persistent',ns5)
mode_obj=SimpleNamespace(
    _mode_refetch_generation=3,_loaded_song='S',_loaded_artist='A',
    source_combo=Combo('酷狗'),trans_check=Toggle(True),status=Status(),lyric_window=LW(),
    _same_track=lambda *a: True,_settings_loaded=True,
    _schedule_config_save=lambda : None,
)
mode_result(mode_obj,{'generation':3,'song':'S','artist':'A','source':'酷狗','trans_only':True,
                      'reason':'translation-toggle','lyric':None,'error':'none'})
need(mode_obj.trans_check.isChecked() is True, 'trans_only preference was changed on per-track failure')
need(mode_obj._limbus_mode_payload_blocked is True and not locked_calls,
     'failed trans_only payload fell into legacy rollback/display path')

# 6. Failed new track retains presentation ownership; old payload launch is denied.
ns6={'time':time,'write_error_log':lambda *a,**k:None,
     '_LIMBUS_AUTO_LYRIC_RESULT_PRE_H11':lambda self,result:'old-handler'}
auto_result=compile_fn('_limbus_auto_lyric_result_ownership',ns6)
class AutoCheck:
    def isChecked(self): return True
class AutoObj:
    _is_started=True; _auto_armed=True; _auto_generation=9; _auto_target_key='new|a'
    _auto_overlay_suspended=True; _auto_fetch_in_progress=True
    _auto_candidate_key='x'; _auto_candidate_hits=2; _auto_queued_job=None
    _loaded_song='Old'; _loaded_artist='B'
    auto_track_check=AutoCheck(); trans_check=Toggle(False); source_combo=Combo('酷狗'); player_combo=Combo('酷狗音乐')
    lyric_window=LW()
    def _same_track(self,*a): return False
aobj=AutoObj()
auto_result(aobj,{'generation':9,'key':'new|a','song':'New','artist':'A','source':'酷狗','trans_only':False,
                  'lyric':None,'error':'no lyrics','precision_upgrade_pending':False,'progressive_keep_fast':False})
need(aobj._auto_overlay_suspended is True and aobj._auto_target_key == '' and aobj._auto_failed_track_key == 'new|a',
     'failed new-track ownership was released or not recorded')
launch_calls=[]
ns7={'write_error_log':lambda *a,**k:None,
     '_LIMBUS_LAUNCH_CURRENT_LYRICS_PRE_H11':lambda self,start_delay=0: launch_calls.append(1) or True}
launch_guard=compile_fn('_limbus_launch_current_lyrics_ownership_guard',ns7)
aobj._loaded_track_key='old|b'; aobj._limbus_mode_payload_blocked=False
need(launch_guard(aobj,0) is False and not launch_calls,
     'old cached payload relaunched while failed new track owns presentation')

# A persistent-mode miss on one song must not keep the *next* successful song blank.
success_seen=[]
def auto_success_pre(self,result):
    success_seen.append(bool(getattr(self, '_limbus_mode_payload_blocked', False)))
    self._loaded_song=result.get('song',''); self._loaded_artist=result.get('artist','')
    return 'applied'
ns6b={'time':time,'write_error_log':lambda *a,**k:None,
      '_LIMBUS_AUTO_LYRIC_RESULT_PRE_H11':auto_success_pre}
auto_success=compile_fn('_limbus_auto_lyric_result_ownership',ns6b)
sobj=AutoObj(); sobj._auto_target_key='next|a'; sobj._auto_generation=10
sobj._same_track=lambda s1,a1,s2,a2: str(s1)==str(s2) and str(a1)==str(a2)
sobj._limbus_mode_payload_blocked=True; sobj._limbus_mode_payload_block_reason='translation-toggle-no-payload'
auto_success(sobj,{'generation':10,'key':'next|a','song':'Next','artist':'A','source':'酷狗','trans_only':False,
                   'lyric':'[00:00.00]ok','precision_upgrade_pending':False,'progressive_keep_fast':False})
need(success_seen == [False] and sobj._limbus_mode_payload_blocked is False,
     'persistent-mode blank state leaked into the next successful track')

# -------------------------------------------------------------------------
# 7. KuGou malformed HostV2 title is rejected while canonical shell is accepted.
class CPStub:
    @staticmethod
    def _kugou_window_probe_identity_credible(song, artist): return bool(song)
ns8={'re':re,'ControlPanel':CPStub}
credible=compile_fn('_limbus_kugou_host_title_credible',ns8)
need(not credible('！ - 酷狗音乐 ゆこぴ - 将棋一番','将棋一番','ゆこぴ'),
     'known malformed KuGou title accepted')
need(not credible('酷狗音乐','',''), 'shell-only KuGou title accepted')
need(credible('ゆこぴ - 将棋一番！ - 酷狗音乐','将棋一番！','ゆこぴ'),
     'canonical KuGou shell rejected')

# 8. KuGou HostV2 misses have a real negative backoff; force still bypasses it.
host_calls=[]
ns9={'time':time,'write_error_log':lambda *a,**k:None,
     '_LIMBUS_KUGOU_RESOLVE_HOST_V2_PRE_H11':lambda self,force=False: host_calls.append(force) or None}
host_fn=compile_fn('_limbus_kugou_resolve_host_v2_backoff',ns9)
hobj=SimpleNamespace(_kugou_host_v2_cache=None)
host_fn(hobj,False); host_fn(hobj,False)
need(len(host_calls)==1, 'KuGou negative-cache backoff did not suppress immediate repeated miss')
host_fn(hobj,True)
need(len(host_calls)==2 and host_calls[-1] is True, 'force KuGou host discovery did not bypass backoff')

# -------------------------------------------------------------------------
# 9. Measured render fuse chooses the cheap lane; ordinary Atlas warmup keeps glow.
class Pix:
    def __init__(self,null=True): self.null=null
    def isNull(self): return self.null
ns10={}
render_active=compile_fn('_limbus_render_emergency_active',ns10)
r=SimpleNamespace(_limbus_render_emergency_fused=False,_song_fragment_atlas_pixmap=None,
                  _song_fragment_atlas_performance_fused=True,_song_fragment_atlas_inflight=set())
need(render_active(r) is True, 'Atlas performance fuse does not enter cheap renderer')
r._song_fragment_atlas_performance_fused=False; r._song_fragment_atlas_inflight={'x'}
need(render_active(r) is False, 'ordinary Atlas warmup incorrectly removes glow before overload is measured')
r._song_fragment_atlas_pixmap=Pix(False)
need(render_active(r) is False, 'ready Atlas incorrectly forced cheap renderer')
for token in ('renderer=plain-glyph','history=skip','glow/vector=skip','cadence<=60Hz','_LIMBUS_RENDER_EMERGENCY_PAINT_MS = 120.0'):
    need(token in src, 'render emergency contract missing: '+token)

# 10. Exit/close are bounded and a global aboutToQuit watchdog covers non-tray quit paths.
exit_src=fn_src('_limbus_control_panel_exit_app_bounded')
need('target=_limbus_shutdown_media_worker' in exit_src and 'daemon=True' in exit_src,
     'MediaSync.stop is not isolated from Qt shutdown')
worker_src=fn_src('_limbus_shutdown_media_worker')
need('QApplication.quit()' not in exit_src and 'self.media_sync.stop()' not in exit_src and
     'native_clean' in worker_src and 'QApplication.quit()' in worker_src,
     'Qt teardown is not gated by completed off-GUI native cleanup')
close_src=fn_src('_limbus_control_panel_close_event_bounded')
need('_LIMBUS_CONTROL_PANEL_CLOSE_EVENT_PRE_H11' in close_src and 'self._exit_app()' in close_src,
     'true close does not route through bounded exit while close-to-tray is preserved')
init_src=fn_src('_limbus_control_panel_init_exit_guard')
need('aboutToQuit.connect(_limbus_arm_global_exit_watchdog)' in init_src,
     'non-tray QApplication quit path lacks hard-exit watchdog')
need('os._exit(0)' in fn_src('_limbus_shutdown_hard_watchdog'), 'hard exit fallback missing')

# Source-locked implementation remains in place; H11 must be an outer closure, not a hash rewrite.
for assign in (
    'ControlPanel.fetch_lyric = _limbus_control_panel_fetch_lyric_async',
    'ControlPanel._on_translation_only_changed = _limbus_translation_only_changed_persistent',
    'ControlPanel._detected_player_track = _limbus_detected_player_track_host_sanitized',
    'MediaSessionSync._kugou_resolve_host_v2 = _limbus_kugou_resolve_host_v2_backoff',
    'LyricWindow.paintEvent = _limbus_lyric_paint_event_emergency',
):
    need(assign in src, 'H11 runtime closure assignment missing: '+assign)

print('POST-RELEASE RESPONSIVENESS H11 REPLAY: PASS')
print('  QQ/NetEase control: injected slow call cannot block requester')
print('  liveness: hung Toolhelp bounded + late native stale-drop')
print('  QQ unknown: validated advancing-only cold-start proof')
print('  manual precise: fast payload precedes injected slow precision')
print('  ownership/preferences/KuGou title/backoff/render/exit: PASS')
