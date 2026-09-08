from __future__ import annotations
import ast, asyncio, importlib.util, sys, time
from pathlib import Path
from types import SimpleNamespace

if len(sys.argv) != 2:
    print('usage: CHECK_TRANSPORT_OWNERSHIP_WIN10_H26_REPLAY.py <main.py>')
    raise SystemExit(2)
main=Path(sys.argv[1]).resolve(); source=main.read_text(encoding='utf-8'); tree=ast.parse(source)
funcs={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
fail=[]
for token in (
    'TRANSPORT OWNERSHIP + WIN10 EVIDENCE CLOSURE H26',
    'H26网易云Win10临时时钟无证据禁用','H26网易云UNKNOWN端到端保持',
    'H26跨播放器UIA时钟探测已拒绝','H26跨播放器QQ时长探测已拒绝',
    'H26自动切歌采用播放器真实位置','H26网易云Win32视觉时钟已锁定',
    'static-line-lock=forbidden','win11-path=unchanged',
):
    if token not in source: fail.append('missing token: '+token)

# H26 is a post-H25 layer and must not be spliced into older protected method bodies.
h25=source.find('# H25 clock / seek / evidence closure')
h26=source.find('# H26 transport ownership / Win10 evidence closure')
h16=source.find('# H16 UX runtime wiring / real-machine closure')
if not (0 <= h25 < h26 < h16): fail.append('H26 layer placement is not after H25/before historical H16 extraction boundary')

def fsrc(name):
    n=funcs.get(name)
    if n is None: raise KeyError(name)
    return ast.get_source_segment(source,n)

# Win10 UNKNOWN suppression; Win11 exact delegation.
try:
    ns={'_LIMBUS_H26_SNAPSHOT_PRE':lambda self: {'position_ms':0,'connected':True,'sync_waiting':False,'position_source':'auto-track-local-provisional','visual_seek':{'target':0}},
        '_h26_netease_win10_safe_profile':lambda self=None:True,'H26_NETEASE_UNKNOWN_SOURCES':{'auto-track-local-provisional'},
        'time':time,'write_error_log':lambda *a,**k:None}
    exec(fsrc('_h26_snapshot'),ns,ns)
    fake=SimpleNamespace(_process_hint='cloudmusic.exe',_h26_snapshot_unknown_log_mono=0.0,_process_stem=lambda v:'cloudmusic')
    got=ns['_h26_snapshot'](fake)
    if got.get('position_ms','x') is not None or got.get('connected') is not False or got.get('position_source')!='h26-ncm-unknown-no-player-evidence':
        fail.append('Win10 UNKNOWN was not kept None end-to-end')
    ns['_h26_netease_win10_safe_profile']=lambda self=None:False
    legacy=ns['_h26_snapshot'](fake)
    if legacy.get('position_ms')!=0 or legacy.get('connected') is not True or legacy.get('visual_seek')!={'target':0}:
        fail.append('Win11 snapshot did not delegate exact legacy result')
except Exception as e: fail.append('snapshot replay: '+repr(e))

try:
    calls=[]
    ns={'_LIMBUS_H26_AUTO_LOCAL_START_PRE':lambda self,pos=0:calls.append(pos) or ('legacy',pos),
        '_h26_netease_win10_safe_profile':lambda self=None:True,'time':time,'write_error_log':lambda *a,**k:None}
    exec(fsrc('_h26_start_auto_local_clock'),ns,ns)
    class F:
        _process_hint='cloudmusic.exe'; _h26_netease_unknown_log_mono=0
        def _process_stem(self,v): return 'cloudmusic'
        def _reset_auto_local_clock(self): self.reset=True
    f=F(); f.reset=False
    if ns['_h26_start_auto_local_clock'](f,625) is not False or calls or not f.reset: fail.append('Win10 auto-local fake clock still starts')
    ns['_h26_netease_win10_safe_profile']=lambda self=None:False
    if ns['_h26_start_auto_local_clock'](f,625)!=('legacy',625) or calls!=[625]: fail.append('Win11 auto-local path changed')
except Exception as e: fail.append('auto-local replay: '+repr(e))

# Desktop ownership boundaries.
try:
    state={'active':'网易云音乐'}; calls=[]
    ns={'_h26_active_player':lambda:state['active'],'_h26_player_process_stems':lambda n:{'QQ音乐':{'qqmusic'},'网易云音乐':{'cloudmusic'},'酷狗音乐':{'kgmusic','kugou'}}.get(n,set()),
        '_h26_log_ownership_once':lambda *a,**k:None,'_LIMBUS_H26_GET_PLAYER_PIDS_PRE':lambda p,players=None:calls.append(p) or [123]}
    exec(fsrc('_h26_get_player_pids_player_owned'),ns,ns)
    if ns['_h26_get_player_pids_player_owned']('酷狗音乐',{})!=[] or calls: fail.append('cross-player KuGou PID probe was not blocked')
    state['active']='酷狗音乐'
    if ns['_h26_get_player_pids_player_owned']('酷狗音乐',{})!=[123] or calls!=['酷狗音乐']: fail.append('actual KuGou PID path changed')
except Exception as e: fail.append('PID ownership replay: '+repr(e))

try:
    state={'active':'网易云音乐'}; calls=[]
    ns={'_h26_active_player':lambda:state['active'],'_h26_process_stem':lambda p:str(p).lower().replace('.exe',''),
        '_h26_player_process_stems':lambda n:{'QQ音乐':{'qqmusic'},'网易云音乐':{'cloudmusic'}}.get(n,set()),
        '_h26_log_ownership_once':lambda *a,**k:None,
        '_LIMBUS_H26_UIA_POLL_PRE':lambda self,p,force=False:calls.append((p,force)) or {'source':'legacy','position_ms':123}}
    exec(fsrc('_h26_uia_poll_player_owned'),ns,ns)
    blocked=ns['_h26_uia_poll_player_owned'](object(),'qqmusic.exe')
    if blocked.get('source')!='h26-cross-player-uia-blocked' or calls: fail.append('cross-player QQ UIA poll was not blocked')
    state['active']='QQ音乐'; ok=ns['_h26_uia_poll_player_owned'](object(),'qqmusic.exe',True)
    if ok.get('position_ms')!=123 or calls!=[('qqmusic.exe',True)]: fail.append('actual QQ UIA path changed')
except Exception as e: fail.append('UIA ownership replay: '+repr(e))

# QQ duration evidence belongs to QQ player, regardless of lyric provider.
try:
    calls=[]
    ns={'_h26_active_player':lambda:'','_h26_log_ownership_once':lambda *a,**k:None,
        '_LIMBUS_H26_QQ_DURATION_HINT_PRE':lambda panel,purpose='manual-fetch':calls.append(purpose) or 221500}
    exec(fsrc('_h26_qq_duration_hint_player_owned'),ns,ns)
    class C:
        def __init__(self,v): self.v=v
        def currentText(self): return self.v
    if ns['_h26_qq_duration_hint_player_owned'](SimpleNamespace(player_combo=C('网易云音乐')),'x')!=0 or calls: fail.append('NetEase player could read QQ duration')
    if ns['_h26_qq_duration_hint_player_owned'](SimpleNamespace(player_combo=C('QQ音乐')),'x')!=221500 or calls!=['x']: fail.append('QQ player lost QQ duration path')
except Exception as e: fail.append('QQ duration replay: '+repr(e))

# Bind wrapper: foreign NetEase ID is stripped; strong same-track position can refine transition;
# Win10 NetEase safe profile never seeds generic provisional position.
try:
    calls=[]
    ns={'_h26_netease_win10_safe_profile':lambda self=None:False,'_h26_refine_provisional_origin':lambda self,s,a,p:4321,
        '_h26_log_ownership_once':lambda *a,**k:None,
        '_LIMBUS_H26_BIND_TRACK_PRE':lambda self,*a,**k:calls.append((a,k)) or True}
    exec(fsrc('_h26_bind_track_player_owned'),ns,ns)
    q=SimpleNamespace(_process_hint='qqmusic.exe',_process_stem=lambda v:'qqmusic')
    ns['_h26_bind_track_player_owned'](q,'Song','Artist',200000,True,625,'33516239',False)
    a,k=calls[-1]
    if k.get('netease_track_id') is not None or k.get('initial_position_ms')!=4321: fail.append('bind ownership/refined origin failed on non-NetEase')
    calls.clear(); ns['_h26_netease_win10_safe_profile']=lambda self=None:True
    n=SimpleNamespace(_process_hint='cloudmusic.exe',_process_stem=lambda v:'cloudmusic')
    ns['_h26_bind_track_player_owned'](n,'Song','Artist',200000,True,625,'33516239',False)
    a,k=calls[-1]
    if k.get('initial_position_ms')!=0 or k.get('netease_track_id')!='33516239': fail.append('Win10 NetEase provisional bind did not fail closed')
except Exception as e: fail.append('bind wrapper replay: '+repr(e))

# Static rail cannot become authority; coherent forward motion eventually can; stale gaps reset proof.
try:
    ns={'H26_NETEASE_VISUAL_STALE_PROOF_MS':2600.0,'H26_NETEASE_VISUAL_MIN_HITS':3,'H26_NETEASE_VISUAL_MIN_SPAN_MS':900.0}
    exec(fsrc('_h26_netease_visual_proof_step'),ns,ns); step=ns['_h26_netease_visual_proof_step']
    p=None; oks=[]
    for obs,mono in ((10000,1000),(10430,1450),(10920,1950),(11370,2400)):
        p,ok=step(p,obs,mono,100,900,600,221500); oks.append(ok)
    if not any(oks[-2:]): fail.append('coherent visual rail never acquired authority')
    p=None; oks=[]
    for mono in (1000,1450,1950,2400,2850):
        p,ok=step(p,10000,mono,100,900,600,221500); oks.append(ok)
    if any(oks): fail.append('static horizontal line incorrectly acquired authority')
    p,_=step(None,10000,1000,100,900,600,221500); p,ok=step(p,14000,5000,100,900,600,221500)
    if ok or int(p.get('hits') or 0)!=1: fail.append('stale visual samples were stitched together')
except Exception as e: fail.append('visual proof replay: '+repr(e))

# Visual Win11/non-safe path must explicitly call the H25 implementation and never accessibility.
try:
    body=fsrc('_h26_poll_netease_safe_visual_clock')
    if 'return _LIMBUS_H26_H25_VISUAL_PRE(self, status_hint)' not in body: fail.append('visual wrapper lacks H25 delegation')
    for x in ('pywinauto','comtypes','AccessibleObjectFromWindow'):
        if x in body: fail.append('visual wrapper references accessibility: '+x)
except Exception as e: fail.append('visual structural replay: '+repr(e))

# Native detector lifecycle runtime replay.
native=main.parent/'limbus_netease_native.py'
try:
    spec=importlib.util.spec_from_file_location('_h26_native_gate',native); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    class Hang:
        last=None
        def __init__(self): type(self).last=self; self.stop_calls=0
        def on_track_change(self,cb): pass
        def on_state_change(self,cb): pass
        def on_seek(self,cb): pass
        async def start(self): await asyncio.sleep(3600)
        async def stop(self): self.stop_calls+=1
    async def timeout_case():
        mod.AsyncCloudMusic=Hang; a=mod.NeteaseNativeClockAdapter(); a.available=True; a._start_timeout_sec=.04; a._stop_timeout_sec=.04
        if not a.start_background(): raise AssertionError('schedule')
        await asyncio.sleep(.08); s=a.snapshot()
        if s.get('start_state')!='timeout' or not str(s.get('error') or '').startswith('start-timeout:'): raise AssertionError(s)
        if not Hang.last or Hang.last.stop_calls<1: raise AssertionError('no bounded stop')
        await a.stop_async()
    class Ready:
        last=None
        def __init__(self):
            type(self).last=self; self.stop_calls=0; self.track=SimpleNamespace(id=33516239,name='少女A',artist_str='椎名もた',duration=221.5); self.state=SimpleNamespace(track=self.track,position=43.21,is_playing=True)
        def on_track_change(self,cb): pass
        def on_state_change(self,cb): pass
        def on_seek(self,cb): pass
        async def start(self): return None
        async def stop(self): self.stop_calls+=1
    async def ready_case():
        mod.AsyncCloudMusic=Ready; a=mod.NeteaseNativeClockAdapter(); a.available=True; a._start_timeout_sec=.1; a._stop_timeout_sec=.1
        if not a.start_background(): raise AssertionError('schedule-ready')
        await asyncio.sleep(0); await asyncio.sleep(0); s=a.snapshot()
        if not s.get('ready') or s.get('start_state')!='ready' or abs(float(s.get('position_ms') or 0)-43210)>1: raise AssertionError(s)
        await a.stop_async()
    asyncio.run(timeout_case()); asyncio.run(ready_case())
except Exception as e: fail.append('native lifecycle replay: '+repr(e))

if fail:
    print('TRANSPORT OWNERSHIP + WIN10 EVIDENCE H26 REPLAY: FAIL')
    for x in fail: print(' -',x)
    raise SystemExit(1)
print('TRANSPORT OWNERSHIP + WIN10 EVIDENCE H26 REPLAY: PASS')
print(' - H25 protected methods remain external to the H26 layer')
print(' - Win10 NetEase keeps absent evidence as None and suppresses generic provisional 0ms')
print(' - Win11/non-safe paths delegate H25 snapshot/auto-local/visual behavior unchanged')
print(' - desktop transport probes are selected-player-owned, independent of lyric provider')
print(' - strong same-track player evidence may correct transition latency; weak evidence cannot')
print(' - static/stale visual rails cannot gain time authority')
print(' - native detector start/stop is bounded; healthy detector position is preserved')
