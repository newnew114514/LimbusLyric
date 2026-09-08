#!/usr/bin/env python3
import ast, pathlib, sys, threading, time, types

if len(sys.argv) != 2:
    raise SystemExit('usage: CHECK_PLAYER_LIVENESS_CLOSURE_REPLAY.py <main.py>')
path = pathlib.Path(sys.argv[1])
source = path.read_text(encoding='utf-8')
tree = ast.parse(source)

def fn(name):
    hits=[n for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name]
    if not hits: raise AssertionError(f'missing function {name}')
    return hits[0]

def text(name):
    n=fn(name); return '\n'.join(source.splitlines()[n.lineno-1:n.end_lineno])

def check(label, cond):
    if not cond: raise AssertionError(label)
    print(f'  {label}: PASS')

probe=text('_probe_builtin_process_alive')
check('liveness uses Toolhelp process snapshot', 'CreateToolhelp32Snapshot' in probe and 'Process32FirstW' in probe)
check('liveness probe contains no subprocess/OpenProcess', 'subprocess.' not in probe and 'OpenProcess(' not in probe)
worker=text('_player_liveness_worker')
check('liveness worker requires bounded multi-sample death proof', 'PLAYER_LIVENESS_DEAD_CONFIRMATIONS' in worker and '_player_liveness_dead_streak' in worker)
poll=text('_poll_loop')
check('confirmed death is checked before GSMTC session selection', poll.index('_player_liveness_snapshot') < poll.index('_choose_session'))
check('confirmed death hard-retires and skips stale clocks', '_retire_confirmed_dead_player' in poll and 'continue' in poll[poll.index('_retire_confirmed_dead_player'):poll.index('_choose_session')])
snap=text('snapshot')
check('GUI snapshot never runs process liveness discovery', '_probe_builtin_process_alive' not in snap and 'CreateToolhelp32Snapshot' not in snap)

# Dynamic retirement replay from the actual production method.
node=fn('_retire_confirmed_dead_player')
mod=ast.Module(body=[node], type_ignores=[]); ast.fix_missing_locations(mod)
ns={'time':time,'write_error_log':lambda *a,**k:None}
exec(compile(mod, str(path), 'exec'), ns)
retire=ns['_retire_confirmed_dead_player']
class DummySync:
    def __init__(self):
        self._player_liveness_retired_serial=-1; self._auto=False; self._qq_loop=True; self._kg=True
        self._uia_position_ms=123; self._uia_anchor_mono=1; self._uia_observed_ms=123; self._uia_status='playing'; self._uia_has_lock=True
        self._uia_last_seen_mono=1; self._uia_last_observed_ms=123; self._uia_initial_pending={}; self._duration_pending_ui_sample={}; self._track_duration_pending=True
        self._qq_seek_pending={}; self._paused_seek_pending={}; self._playing_seek_pending={}; self._qq_gsmtc_good_streak=3; self._qq_gsmtc_primary=True
        self._kugou_gsmtc_good_streak=3; self._kugou_gsmtc_primary=True; self._netease_bridge_primary=True; self._netease_native_primary=True
        self._track_key='song|artist'; self._track_identity_epoch=9; self._media_player_epoch=2; self._track_identity_player_epoch=2; self._track_bound_mono=0
        self._last_explicit_transport_status='playing'; self._last_explicit_transport_mono=1; self._last_explicit_transport_process='qqmusic'; self._last_explicit_transport_identity_epoch=9
        self._state={}; self._uia_reader=types.SimpleNamespace(invalidate_sample=lambda:None,set_expected_duration=lambda x:None,set_startup_late_attach=lambda x:None)
    def _process_stem(self,x): return str(x).lower().removesuffix('.exe')
    def _reset_auto_local_clock(self): self._auto=True
    def _qq_reset_loop_transport(self,reason=''): self._qq_loop=False
    def _reset_kugou_rail_local_master(self): self._kg=False
    def _kugou_clear_inactive_mouse_events(self,reason=''): self.kg_events=reason
    def _clear_visual_seek_override(self): self.visual_cleared=True
    def _reset_estimator(self,stem): self.est_reset=stem
    def _qq_reset_clock_authority(self,preserve_phase_baseline=False): self.qq_clock_reset=True
    def _set_state(self,**kw): self._state.update(kw)
d=DummySync(); check('confirmed death retirement executes', retire(d,'qqmusic',77) is True)
check('death clears provisional/QQ-loop/KuGou-rail clocks', d._auto and not d._qq_loop and not d._kg)
check('death publishes stopped with no position', d._state.get('status')=='stopped' and d._state.get('position_ms') is None and d._state.get('connected') is False)
check('death invalidates old track identity', d._track_key=='' and d._track_identity_epoch==10)
check('same liveness serial retires only once', retire(d,'qqmusic',77) is False)

# Dynamic worker sequence: one live sample then three misses => confirmed dead.
wnode=fn('_player_liveness_worker'); wmod=ast.Module(body=[wnode], type_ignores=[]); ast.fix_missing_locations(wmod)
wns={'time':time,'write_error_log':lambda *a,**k:None,'PLAYER_LIVENESS_DEAD_CONFIRMATIONS':3,'PLAYER_LIVENESS_POLL_MS':1.0,'PLAYER_LIVENESS_SLOW_PROBE_MS':999999.0}
exec(compile(wmod,str(path),'exec'),wns); wfn=wns['_player_liveness_worker']
class E:
    def __init__(self): self.e=threading.Event()
    def is_set(self): return self.e.is_set()
    def set(self): self.e.set()
    def wait(self,t): return self.e.wait(t)
    def clear(self): self.e.clear()
class Worker:
    def __init__(self):
        self._process_hint='qqmusic'; self._player_liveness_stop_event=E(); self._player_liveness_wake_event=E(); self._player_liveness_lock=threading.Lock(); self._lock=threading.Lock(); self._state={'sync_requested':True}
        self._player_liveness_stem='qqmusic'; self._player_liveness_confirmed=None; self._player_liveness_dead_streak=0; self._player_liveness_serial=1
        self._player_liveness_last_probe_mono=0.; self._player_liveness_last_probe_ms=0.; self._player_liveness_slow_log_mono=0.; self.seq=[True,False,False,False]
    def _process_stem(self,x): return str(x).lower().removesuffix('.exe')
    def _probe_builtin_process_alive(self,stem):
        v=self.seq.pop(0)
        if not self.seq: self._player_liveness_stop_event.set()
        return v
w=Worker(); wfn(w)
check('single disappearance cannot kill a live player', w._player_liveness_dead_streak==3)
check('three consecutive missing-process samples confirm death', w._player_liveness_confirmed is False)

# A transient one-sample disappearance followed by recovery must never retire playback.
w2=Worker(); w2.seq=[True,False,True]
def probe2(stem):
    v=w2.seq.pop(0)
    if not w2.seq: w2._player_liveness_stop_event.set()
    return v
w2._probe_builtin_process_alive=probe2
wfn(w2)
check('one missing sample followed by recovery remains alive', w2._player_liveness_confirmed is True and w2._player_liveness_dead_streak==0)

ui_dead=text('_handle_selected_player_dead'); ui_restore=text('_restore_reopened_player_if_cached')
check('UI death path stops lyrics but keeps application armed', 'stop_lyric' in ui_dead and '_is_started = False' not in ui_dead and '_auto_armed = False' not in ui_dead)
check('reopen restore requires real position and transport', "pos is None or status not in ('playing', 'paused')" in ui_restore)
check('reopen cached bind is late-attach safe', 'startup_existing=True' in ui_restore)
check('H9 unknown carry remains display-only', 'authority=display-only' in source and 'AUTO_TRACK_UNKNOWN_PLAY_CARRY_MAX_MS' in source)
check('H10 build tag present', 'PLAYER-LIVENESS CLOSURE H10' in source)
print('PLAYER LIVENESS CLOSURE REPLAY: PASS')
