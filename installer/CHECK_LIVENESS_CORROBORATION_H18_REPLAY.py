#!/usr/bin/env python3
from __future__ import annotations
import ast
import threading
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / 'LimbusLyric_v1.8.9.133_CROSS_PROVIDER_TRANSLATION_CUSTOM_ADAPTER_FOUNDATION_20260814.py'
src = MAIN.read_text(encoding='utf-8')
tree = ast.parse(src, filename=str(MAIN))
assert 'LIVENESS CORROBORATION H18' in src.splitlines()[63]

def fn(name):
    hits=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name]
    assert len(hits)==1,(name,len(hits))
    return hits[0]

def compile_fn(name, ns):
    node=fn(name); mod=ast.Module(body=[node],type_ignores=[]); ast.fix_missing_locations(mod)
    exec(compile(mod,str(MAIN),'exec'),ns,ns); return ns[name]

class MediaStub:
    @staticmethod
    def _process_stem(v): return str(v or '').lower().replace('.exe','')
    @staticmethod
    def _source_matches_process_hint(source,hint):
        s=str(source or '').lower(); h=MediaStub._process_stem(hint)
        return (h=='cloudmusic' and 'cloudmusic' in s) or (h=='qqmusic' and 'qqmusic' in s) or (h=='kgmusic' and ('kgmusic' in s or 'kugou' in s))
    @staticmethod
    def _status_name(v): return str(v or '').lower()

clock={'now':10000.0}
class FakeTime:
    @staticmethod
    def monotonic(): return clock['now']/1000.0

logs=[]
ns={
    'time':FakeTime,
    'MediaSessionSync':MediaStub,
    'H18_GSMTC_PRESENCE_TTL_MS':1800.0,
    'H18_LIVENESS_EPOCH_NEGATIVE_GRACE_MS':9000.0,
    'H18_LIVENESS_NEGATIVE_DWELL_MS':1800.0,
    'write_error_log':lambda *a,**k: logs.append((a,k)),
}
for name in ('_limbus_h18_gsmtc_presence_snapshot','_limbus_h18_negative_gate'):
    compile_fn(name,ns)

# Fast Toolhelp false must be corroborated; tasklist positive repairs the false negative.
base_values=[]
def base_probe(_self,_stem): return base_values.pop(0)
task_values=[]
def task_probe(_stem): return task_values.pop(0)
ns.update({
    '_LIMBUS_H18_BOUNDED_PROBE_PRE':base_probe,
    '_limbus_liveness_tasklist_probe':task_probe,
})
probe=compile_fn('_limbus_h18_bounded_player_liveness_probe',ns)
obj=SimpleNamespace(_process_stem=MediaStub._process_stem,_player_liveness_lock=threading.Lock(),
                    _h18_gsmtc_presence=None,_h18_liveness_epoch_mono=0.0,
                    _h18_liveness_negative_since_mono=0.0,_h18_liveness_negative_stem='cloudmusic')
base_values.append((False,'toolhelp')); task_values.append(True)
r,source=probe(obj,'cloudmusic')
assert r is True and source=='tasklist-corroborates-alive',(r,source)

# A corroborated negative during a fresh epoch is UNKNOWN, not death evidence.
obj._h18_liveness_epoch_mono=clock['now']
base_values.append((False,'toolhelp')); task_values.append(False)
r,source=probe(obj,'cloudmusic')
assert r is None and 'negative-grace' in source,(r,source)

# After epoch grace, first corroborated negative starts dwell; only persistent evidence becomes False.
# The field log recovered from false to true after ~8s; that whole window must remain UNKNOWN.
clock['now'] += 8000.0
base_values.append((False,'toolhelp')); task_values.append(False)
r,_=probe(obj,'cloudmusic')
assert r is None
# After the 9s epoch grace expires, a fresh persistent-negative dwell must still complete.
clock['now'] += 1500.0
base_values.append((False,'toolhelp')); task_values.append(False)
r,_=probe(obj,'cloudmusic')
assert r is None
clock['now'] += 1900.0
base_values.append((False,'toolhelp')); task_values.append(False)
r,source=probe(obj,'cloudmusic')
assert r is False and 'corroborated-dwell' in source,(r,source)

# A fresh strict active GSMTC witness vetoes even a corroborated negative.
obj._h18_gsmtc_presence={'stem':'cloudmusic','source':'cloudmusic.exe','status':'playing','mono':clock['now']}
base_values.append((False,'toolhelp')); task_values.append(False)
r,source=probe(obj,'cloudmusic')
assert r is None and 'negative-grace' in source,(r,source)

# Inconclusive secondary probe can never publish death.
obj._h18_gsmtc_presence=None
clock['now'] += 5000.0
base_values.append((False,'toolhelp')); task_values.append(None)
r,source=probe(obj,'cloudmusic')
assert r is None and source=='unknown-after-toolhelp-false',(r,source)

# Strict source-affine playing/paused sessions create short-lived presence; Edge/current fallback cannot.
ns2={
    'time':FakeTime,'MediaSessionSync':MediaStub,
    '_LIMBUS_H18_CHOOSE_SESSION_PRE':lambda self,manager: manager.session,
}
note=compile_fn('_limbus_h18_note_gsmtc_presence',ns2)
ns2['_limbus_h18_note_gsmtc_presence']=note
choose=compile_fn('_limbus_h18_choose_session',ns2)
class Session:
    def __init__(self,source,status): self.source_app_user_model_id=source; self.status=status
    def get_playback_info(self): return SimpleNamespace(playback_status=self.status)
class Obj:
    _process_hint='cloudmusic.exe'; _player_liveness_lock=threading.Lock(); _lock=threading.Lock(); _state={'status':'playing'}
    _process_stem=staticmethod(MediaStub._process_stem)
    _source_matches_process_hint=staticmethod(MediaStub._source_matches_process_hint)
    _status_name=staticmethod(MediaStub._status_name)
o=Obj(); choose(o,SimpleNamespace(session=Session('cloudmusic.exe','playing')))
assert getattr(o,'_h18_gsmtc_presence',{}).get('status')=='playing'
o._h18_gsmtc_presence=None; choose(o,SimpleNamespace(session=Session('msedge.exe','playing')))
assert o._h18_gsmtc_presence is None

# UNKNOWN may be positively rescued by fresh strict-active presence; explicit False is untouched.
ns3={
    'H18_GSMTC_PRESENCE_TTL_MS':1800.0,
    '_LIMBUS_H18_LIVENESS_SNAPSHOT_PRE':lambda self,process_stem=None: {'alive':None,'serial':7},
    '_limbus_h18_gsmtc_presence_snapshot':lambda self,stem:{'fresh':True,'age_ms':120.0},
}
snapshot=compile_fn('_limbus_h18_player_liveness_snapshot',ns3)
class SnapObj:
    _process_hint='cloudmusic'; _process_stem=staticmethod(MediaStub._process_stem)
snap=snapshot(SnapObj(),'cloudmusic')
assert snap['alive'] is True and snap['presence_rescue']=='strict-active-gsmtc',snap
ns4={
    '_LIMBUS_H18_LIVENESS_SNAPSHOT_PRE':lambda self,process_stem=None: {'alive':False,'serial':8},
    '_limbus_h18_gsmtc_presence_snapshot':lambda self,stem:{'fresh':True,'age_ms':50.0},
}
snapshot2=compile_fn('_limbus_h18_player_liveness_snapshot',ns4)
snap2=snapshot2(SnapObj(),'cloudmusic')
assert snap2['alive'] is False and 'presence_rescue' not in snap2,snap2

# Static wiring / safety assertions.
assert 'MediaSessionSync._reset_player_liveness_epoch = _limbus_h18_reset_liveness_epoch' in src
assert 'MediaSessionSync._choose_session = _limbus_h18_choose_session' in src
assert '_limbus_bounded_player_liveness_probe = _limbus_h18_bounded_player_liveness_probe' in src
assert 'MediaSessionSync._player_liveness_snapshot = _limbus_h18_player_liveness_snapshot' in src
assert "if str(source) == 'toolhelp':" in src
assert 'unknown-after-toolhelp-false' in src
print('LIVENESS CORROBORATION H18 REPLAY: PASS')
print('  fast Toolhelp false requires bounded independent corroboration: PASS')
print('  startup grace + persistent-negative dwell: PASS')
print('  strict active GSMTC false-dead veto / UNKNOWN positive rescue: PASS')
