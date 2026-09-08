from pathlib import Path
import ast, sys as _real_sys, types, time

if len(_real_sys.argv) != 2:
    raise SystemExit(2)
source_path=Path(_real_sys.argv[1]); text=source_path.read_text(encoding='utf-8')

def need(cond,msg):
    if not cond:
        print('FROZEN KUGOU CAPABILITY SAFETY H42 REPLAY: FAIL')
        print(' - '+msg); raise SystemExit(1)

markers=[
    '+ FROZEN KUGOU CAPABILITY SAFETY H42',
    'H42酷狗同曲Host假零隔离',
    'H42酷狗Host假零Transport代际拒绝',
    'H42酷狗HostV2时长升级为播放器权威',
    'H42 Windows frozen兼容安全层',
    "_limbus_scope='windows-frozen-kugou-capability-safe'",
    "_limbus_frozen_policy='psapi-no-tasklist-qq-kugou'",
    "_limbus_frozen_policy='psapi-no-subprocess'",
    "_limbus_host_zero_policy='same-track-zero-needs-independent-restart-proof'",
]
for m in markers: need(m in text,'missing H42 marker: '+m)

tree=ast.parse(text)
wanted_assign={
    'H42_KUGOU_HOST_ZERO_MAX_MS','H42_KUGOU_HOST_ZERO_PRIOR_MIN_MS','H42_KUGOU_RESTART_PROOF_TTL_MS',
    'H42_KUGOU_NEAR_ZERO_RATIO_MAX','H42_FROZEN_NEGATIVE_LIVENESS_BACKOFF_MS','H42_FROZEN_PID_CACHE_MS',
    'H42_PROCESS_GC_GUARD_ENV'
}
wanted_funcs={'_h42_windows_frozen','_h42_kugou_frozen_safe','_h42_should_quarantine_host_zero','_h42_psapi_process_pids','_h42_activate_runtime'}
nodes=[]
for n in tree.body:
    if isinstance(n,ast.Assign):
        if {t.id for t in n.targets if isinstance(t,ast.Name)} & wanted_assign: nodes.append(n)
    elif isinstance(n,ast.FunctionDef) and n.name in wanted_funcs: nodes.append(n)

# Pure replay of the exact field failure: 163.163s -> HostV2 0ms is not a replay proof.
ns={}
exec(compile(ast.Module(body=[n for n in nodes if not (isinstance(n,ast.FunctionDef) and n.name=='_h42_activate_runtime')],type_ignores=[]),str(source_path),'exec'),ns)
q=ns['_h42_should_quarantine_host_zero']
need(q(163163,0,'host-uia-same-track-restart',False),'field 163s->0ms Host collapse was not quarantined')
need(not q(163163,0,'host-uia-same-track-restart',True),'independently proven real restart was incorrectly blocked')
need(not q(1200,0,'host-uia-same-track-restart',False),'legitimate initial near-zero attach was blocked')
need(not q(163163,0,'host-uia-range-v2',False),'ordinary Host range update was mislabeled as same-track restart')

# Runtime stubs verify H42 changes callable behavior, not only source strings.
class FakeGC:
    def __init__(self): self.enabled=True
    def isenabled(self): return self.enabled
    def disable(self): self.enabled=False
fake_gc=FakeGC()
fake_sys=types.SimpleNamespace(platform='win32',frozen=True)
logs=[]
def write_error_log(*a,**k): logs.append((a,k))

class MediaSessionSync:
    def __init__(self):
        self._process_hint='kgmusic.exe'; self._track_key='party|teminite'; self._media_player_epoch=2
        self._kugou_rail_master_position_ms=163163.0; self._kugou_transport_generation=7
        self._uia_duration_ms=0; self._state={'duration_ms':0,'status':'paused'}
    def _process_stem(self,v): return str(v or '').lower().replace('.exe','')
    def _kugou_seed_rail_local_master(self,position_ms,status='unknown',reason='bootstrap',absolute=False,now_ms=None):
        self.base_seed_calls=getattr(self,'base_seed_calls',0)+1; self._kugou_rail_master_position_ms=float(position_ms); return True
    def _kugou_advance_transport_generation(self,reason,position_ms=None,evidence=''):
        self.base_gen_calls=getattr(self,'base_gen_calls',0)+1; self._kugou_transport_generation+=1; return self._kugou_transport_generation
    def _kugou_poll_uia_progress_v2(self,status,local_position_hint=None):
        self._kugou_host_v2_progress_trusted_key='slider-key'; self._uia_duration_ms=208000; self._state['duration_ms']=208000; return 99020

class ControlPanel:
    def __init__(self,*a,**k): pass
class LyricFetcher:
    @staticmethod
    def get_player_pids(player_name=None,players=None): return [999]
class PlayerUiPositionReader:
    @staticmethod
    def _process_pids(process_name): return {999}
class AsyncPlayerUiPositionReader:
    def _process_pids(self,process_name): return {999}

def old_safe(sync=None): return False
def old_live(sync,stem): return (False,'slow-negative')
def _h37_windows_build_number(): return 26200
def _h38_kugou_owned_duration(sync): return int(getattr(sync,'owned',0) or 0)
def _h38_accept_kugou_player_duration(sync,duration_ms,source='x',position_ratio=None,now_ms=None): sync.owned=int(duration_ms); return True
def _h30_visual_state(sync,provider): return {'proofs':[]}
def _h40_near_zero_proof_rows(*a,**k): return False
def _h28_psapi_positive_process_alive(stem): return None

runtime=dict(sys=fake_sys,os=__import__('os'),ctypes=__import__('ctypes'),time=time,_py_gc=fake_gc,
             MediaSessionSync=MediaSessionSync,ControlPanel=ControlPanel,LyricFetcher=LyricFetcher,
             PlayerUiPositionReader=PlayerUiPositionReader,AsyncPlayerUiPositionReader=AsyncPlayerUiPositionReader,
             _h37_kugou_win10_safe=old_safe,_limbus_bounded_player_liveness_probe=old_live,
             _h37_windows_build_number=_h37_windows_build_number,_h38_kugou_owned_duration=_h38_kugou_owned_duration,
             _h38_accept_kugou_player_duration=_h38_accept_kugou_player_duration,_h30_visual_state=_h30_visual_state,
             _h40_near_zero_proof_rows=_h40_near_zero_proof_rows,_h28_psapi_positive_process_alive=_h28_psapi_positive_process_alive,
             write_error_log=write_error_log,_H39_WIN10_PROCESS_GC_GUARD_ACTIVE=False)
act=[n for n in nodes if isinstance(n,ast.FunctionDef) and n.name=='_h42_activate_runtime'][0]
pre=[n for n in nodes if n is not act]
exec(compile(ast.Module(body=pre+[act],type_ignores=[]),str(source_path),'exec'),runtime)
runtime['_h42_activate_runtime']()
need(runtime['_H39_WIN10_PROCESS_GC_GUARD_ACTIVE'] is True and not fake_gc.isenabled(),
     'build 26200 frozen startup did not enter process cyclic-GC guard')
s=MediaSessionSync()
need(runtime['MediaSessionSync']._kugou_seed_rail_local_master(s,0,status='paused',reason='host-uia-same-track-restart',absolute=True) is False,
     'runtime seed still accepted 163s->0ms Host same-track collapse')
need(getattr(s,'base_seed_calls',0)==0 and int(s._kugou_rail_master_position_ms)==163163,
     'blocked Host zero still mutated the rail-local master')
need(runtime['MediaSessionSync']._kugou_advance_transport_generation(s,'host-v2-position-collapse',position_ms=0,evidence='proven-range')==7,
     'false Host zero still advanced transport generation')
need(getattr(s,'base_gen_calls',0)==0,'false Host zero reached legacy transport generation')

# A genuine explicit user seek to the beginning remains allowed.
s._h28_kugou_seek_observation={'target_ms':0,'mono':time.monotonic()*1000.0,'track_key':s._track_key}
need(runtime['MediaSessionSync']._kugou_seed_rail_local_master(s,0,status='paused',reason='host-uia-same-track-restart',absolute=True) is True,
     'real recent user seek to zero was blocked')

# Proven HostV2 duration remains useful on high Windows builds even though zero-position authority is separate.
s2=MediaSessionSync(); s2._kugou_rail_master_position_ms=99020
runtime['MediaSessionSync']._kugou_poll_uia_progress_v2(s2,'paused',local_position_hint=99020)
need(int(getattr(s2,'owned',0) or 0)==208000,'proven HostV2 duration was not promoted to player-owned authority')
need(runtime['_h37_kugou_win10_safe'](s2) is True,'packaged build 26200 KuGou did not inherit H37-H41 safety wrappers')

# Historical H39 pure helper remains source-stable; H42 generalization happens only at final runtime binding.
need("def _h39_should_hold_process_gc_disabled" in text and "0 < build < 22000" in text,
     'H39 historical contract was rewritten instead of being superseded by H42')
need(text.index("if '_h42_activate_runtime' in globals():") < text.index('if __name__ == "__main__":'),
     'H42 startup guard activates after QApplication/native dispatch')

print('FROZEN KUGOU CAPABILITY SAFETY H42 REPLAY: PASS')
print(' - packaged Windows build 26200 receives the same KuGou authority safety boundary as 19045')
print(' - progressed same-track HostV2 zero is quarantined unless user/physical restart proof exists')
print(' - proven HostV2 duration stays available as player-owned evidence')
print(' - frozen Windows cyclic-GC guard activates before Qt startup animation')
print(' - QQ/KuGou PID probes are routed to PSAPI instead of tasklist/subprocess')
