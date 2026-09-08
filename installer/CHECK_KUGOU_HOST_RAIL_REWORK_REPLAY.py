from __future__ import annotations
import ast, sys
from pathlib import Path

if len(sys.argv)!=2:
    print('usage: CHECK_KUGOU_HOST_RAIL_REWORK_REPLAY.py <main.py>'); raise SystemExit(2)
path=Path(sys.argv[1]); source=path.read_text(encoding='utf-8'); tree=ast.parse(source,filename=str(path))
funcs={n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
for name in ('_kugou_host_candidate_score','_kugou_progress_proof_step'):
    if name not in funcs:
        raise SystemExit('KUGOU HOST RAIL REWORK REPLAY: FAIL missing '+name)
ns={'KUGOU_HOST_V2_PROGRESS_MIN_SPAN_MS':800.0}
mod=ast.Module(body=[funcs['_kugou_host_candidate_score'],funcs['_kugou_progress_proof_step']],type_ignores=[]); ast.fix_missing_locations(mod)
exec(compile(mod,str(path),'exec'),ns)
score=ns['_kugou_host_candidate_score']; step=ns['_kugou_progress_proof_step']
# Field-observed topology: blank shell, titled content host, and MV. The titled kugou_ui must win.
blank=score('kugou_ui','',(2681,67,3771,817),True,False)
titled=score('kugou_ui','鏡音リン、椎名もた - 少女A - 酷狗音乐',(2696,82,3756,802),True,False)
mv=score('kugou_mv_win','酷狗MV',(2946,176,3716,609),True,False)
assert titled>blank>0 and mv < -10000, (blank,titled,mv)
# Process/PID is deliberately absent from the scorer: class/title discovery must work even when tasklist races.
# A real playback range advances at wall-clock pace and becomes proven.
p=None
for obs,now in [(10000,1000),(10420,1420),(10840,1840)]: p,ok=step(p,obs,now,'playing','rail-a')
assert ok and p['count']==3
# A static volume slider must not become a playing clock.
p=None; oks=[]
for obs,now in [(55000,1000),(55000,1420),(55000,1840),(55000,2260)]: p,ok=step(p,obs,now,'playing','volume'); oks.append(ok)
assert not any(oks)
# A paused real rail is allowed to freeze and prove.
p=None
for obs,now in [(72000,1000),(72020,1420),(72010,1840)]: p,ok=step(p,obs,now,'paused','rail-p')
assert ok
# Wiring: V2 direct EnumWindows host is used by visual path; old locked gesture path gets PID rescue.
for token in (
    "strategy=enumwindows-class-first", "cls == 'kugou_ui'", "rect=self._kugou_host_rect_v2() or self._kugou_window_rect()",
    "host-uia-range-v2", "host-uia-same-track-restart", "if raw_name in ('kgmusic.exe', 'kugou.exe') and win32gui is not None",
):
    assert token in source, token
print('KUGOU HOST RAIL REWORK REPLAY: PASS')
print('  class-first host resolver: PASS (titled kugou_ui > blank shell > MV rejected)')
print('  UIA range transport proof: PASS (playing 1x / paused freeze / volume static rejected)')
print('  tasklist-independent KuGou PID rescue + visual V2 wiring: PASS')
