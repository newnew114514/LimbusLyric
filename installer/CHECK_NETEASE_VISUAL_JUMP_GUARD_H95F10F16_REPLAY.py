#!/usr/bin/env python3
from __future__ import annotations
import ast, copy, pathlib, sys
if len(sys.argv)!=2: raise SystemExit('usage: CHECK_NETEASE_VISUAL_JUMP_GUARD_H95F10F16_REPLAY.py <main.py>')
p=pathlib.Path(sys.argv[1]); src=p.read_text(encoding='utf-8'); tree=ast.parse(src)
def need(c,m):
    if not c: raise AssertionError(m)
need('+ NETEASE VISUAL JUMP + PRECISION HANDOFF GUARD H95F10F16' in src,'F16 build tag missing')
marker='# H95F10F16 NetEase shared-visual discontinuity guard'
need(marker in src,'F16 marker missing')
funcs={n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
for name in ('_h95f10f16_ncm_visual_jump_step','_h95f10f16_netease_visual_clock','_h95f10f16_precision_upgrade','_h95f10f16_activate'):
    need(name in funcs,'missing '+name)
start=src.index(marker); end=src.index('if __name__ == "__main__":',start); block=src[start:end]
for bad in ('MediaSessionSync.position =','MediaSessionSync.seek =','MediaSessionSync.bind_track =','LyricSearchEngine.search =','LyricWindow.paintEvent =','FadingLine.draw =','requests.','threading.Thread','QPainterPath'):
    need(bad not in block,'F16 crossed protected authority '+bad)
need("MediaSessionSync._h25_poll_netease_safe_visual_clock = _h95f10f16_netease_visual_clock" in block,'final H30 fallback wrapper not installed')
need("source == 'ncm-shared-visual-seek-local'" in block,'explicit seek bypass missing')
need("'ncm-shared-visual-guarded-local'" in block,'guarded continuity source missing')
need('LyricWindow.upgrade_lyric_timeline_preserve_visual = _h95f10f16_precision_upgrade' in block,'NetEase precision freshness wrapper not installed')
need('window._playback_position()' in block and "pos_source.startswith('ncm-')" in block,'precision freshness does not consume existing final NetEase display clock')

node=copy.deepcopy(funcs['_h95f10f16_ncm_visual_jump_step']); node.decorator_list=[]
ns={
 'H95F10F16_NCM_JUMP_MIN_MS':6000.0,
 'H95F10F16_NCM_JUMP_DURATION_RATIO':0.04,
 'H95F10F16_NCM_CONFIRM_MIN_MS':160.0,
 'H95F10F16_NCM_CONFIRM_TTL_MS':2600.0,
 'H95F10F16_NCM_CONFIRM_TOLERANCE_MS':1800.0,
}
exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),'<f16>','exec'),ns)
step=ns['_h95f10f16_ncm_visual_jump_step']
track='anacquiredtaste|portsulphurband'; dur=233361.0
anchor=None; pending=None
# Replay the old log's stable ~7-8 s physical rail.
for t,pos in [(0.0,7101.0),(900.0,7583.0),(1800.0,7556.0),(2700.0,7835.0)]:
    anchor,pending,pub,ok,reason=step(anchor,pending,pos,t,'playing',track,dur,physical=True,explicit_seek=False)
    need(ok,f'stable physical sample rejected: {pos} {reason}')
# Exact failure class: a different horizontal surface appears as 171.339 s once.
anchor_before=dict(anchor)
anchor,pending,pub,ok,reason=step(anchor,pending,171339.0,3600.0,'playing',track,dur,physical=True,explicit_seek=False)
need(not ok and reason=='hold-large-discontinuity','one-sample 171s false rail was not held')
need(pub < 15000.0,'guard published false 171s position')
need(isinstance(pending,dict) and int(pending['position'])==171339,'pending discontinuity not recorded')
# A local lease between physical samples must not erase pending evidence.
anchor,p2,pub2,ok2,reason2=step(anchor,pending,pub+200.0,3800.0,'playing',track,dur,physical=False,explicit_seek=False)
need(ok2 and p2 is pending and reason2=='local-lease','local lease cleared pending discontinuity')
# Next physical sample returns to the real rail; pending false rail is discarded.
anchor,pending,pub,ok,reason=step(anchor,pending,8163.0,4500.0,'playing',track,dur,physical=True,explicit_seek=False)
need(ok and pending is None and pub==8163.0,'return to real 8s rail did not recover immediately')
# A genuine external seek with no mouse evidence is delayed only until a second coherent physical sample.
anchor,pending,pub,ok,reason=step(anchor,pending,90000.0,6000.0,'playing',track,dur,physical=True,explicit_seek=False)
need(not ok and pending is not None,'first implicit large seek did not wait for second proof')
anchor,pending,pub,ok,reason=step(anchor,pending,90850.0,6700.0,'playing',track,dur,physical=True,explicit_seek=False)
need(ok and reason=='confirmed-discontinuity' and pending is None,'second coherent physical seek sample did not confirm')
# Explicit seek remains immediate.
anchor,pending,pub,ok,reason=step(anchor,pending,140000.0,7000.0,'playing',track,dur,physical=True,explicit_seek=True)
need(ok and pub==140000.0 and reason=='explicit-seek-physical','explicit seek was delayed')

# Precision handoff freshness: old renderer had 0 ms while final NetEase display clock was ~7.5 s.
pnode=copy.deepcopy(funcs['_h95f10f16_precision_upgrade']); pnode.decorator_list=[]
seen={}
def pre(window,text):
    seen['last']=window._last_position_ms; return True
pns={'_H95F10F16_PRECISION_PRE':pre,'write_error_log':lambda *a,**k:None}
exec(compile(ast.fix_missing_locations(ast.Module(body=[pnode],type_ignores=[])),'<f16-precision>','exec'),pns)
class W:
    _last_position_ms=0; _last_sync_source=''; _last_sync_position_source=''
    def _playback_position(self):
        self._last_sync_source='cloudmusic'; self._last_sync_position_source='ncm-shared-visual-rail'
        return (7556,True,'playing',0)
w=W(); need(pns['_h95f10f16_precision_upgrade'](w,'x') is True,'precision wrapper did not delegate')
need(seen.get('last')==7556,'precision handoff did not refresh renderer position from existing final NetEase clock')

print('NETEASE VISUAL JUMP GUARD H95F10F16 REPLAY: PASS')
print('  old 7.8s -> 171.3s -> 8.1s false-rail sequence is held/recovered: PASS')
print('  genuine unobserved seek accepts after second coherent physical proof: PASS')
print('  explicit seek remains immediate: PASS')
print('  NetEase precision handoff refreshes stale renderer position from existing final display clock: PASS')
print('  native/Bridge/GSMTC/provider/render authority unchanged: PASS')
