from __future__ import annotations
import ast, sys
from pathlib import Path

if len(sys.argv) != 2:
    print('usage: CHECK_H22_FUSE_NEXT_CALL_H33F1_REPLAY.py <main.py>')
    raise SystemExit(2)
main=Path(sys.argv[1]).resolve()
source=main.read_text(encoding='utf-8')
fail=[]
for token in (
    'H22 FUSE NEXT-CALL HARDENING H33F1',
    "_h22_kugou_host_uia_mandatory_skip",
    "self._h22_kugou_host_uia_mandatory_skip = 1",
    "self._h22_kugou_host_uia_mandatory_skip = 0",
):
    if token not in source:
        fail.append('missing source token: '+token)

tree=ast.parse(source,filename=str(main))
fn=next((n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_h22_kugou_progress_guard'),None)
if fn is None:
    fail.append('missing _h22_kugou_progress_guard')
else:
    class Clock:
        def __init__(self): self.t=100.0
        def monotonic(self): return self.t
    clock=Clock()
    class TimeShim:
        @staticmethod
        def monotonic(): return clock.monotonic()
    ns={'time':TimeShim}
    exec(ast.get_source_segment(source,fn),ns,ns)
    guard=ns['_h22_kugou_progress_guard']
    ns['_h22_kugou_win10_frozen_safe_mode']=lambda:False
    ns['_h22_windows_build_number']=lambda:26100
    ns['write_error_log']=lambda *a,**k:None
    ns['H22_KUGOU_HOST_UIA_SLOW_MS']=5.0
    ns['H22_KUGOU_HOST_UIA_SLOW_FUSE_SEC']=30.0
    ns['H22_KUGOU_HOST_UIA_MISS_FUSE_SEC']=30.0
    ns['H22_KUGOU_HOST_UIA_MISS_LIMIT']=3
    calls={'n':0}
    def slow_pre(self,status,local_position_hint=None):
        calls['n']+=1
        clock.t+=0.012
        return None
    ns['_LIMBUS_H22_KUGOU_PROGRESS_PRE']=slow_pre
    class Fake:
        def _kugou_resolve_host_v2(self): return {'hwnd':1234}
    fake=Fake()
    guard(fake,'playing',0)
    if calls['n']!=1:
        fail.append(f'first slow call count unexpected: {calls["n"]}')
    # Simulate extreme scheduler starvation / VM suspend beyond the 30s test fuse.
    clock.t += 45.0
    guard(fake,'playing',0)
    if calls['n']!=1:
        fail.append(f'wall-clock jump bypassed mandatory next-call suppression: calls={calls["n"]}')
    if int(getattr(fake,'_h22_kugou_host_uia_mandatory_skip',-1))!=0:
        fail.append('mandatory skip was not consumed exactly once')
    # The following call is allowed because both the time fuse and one-shot barrier have elapsed.
    guard(fake,'playing',0)
    if calls['n']!=2:
        fail.append(f'provider did not re-open after one-shot barrier: calls={calls["n"]}')
    # A new HWND must clear any outstanding barrier because it is a new provider instance.
    fake._h22_kugou_host_uia_mandatory_skip=1
    fake._h22_kugou_host_uia_fused_until_mono=clock.t+100.0
    fake._h22_kugou_host_uia_hwnd=1234
    fake._kugou_resolve_host_v2=lambda:{'hwnd':5678}
    # Changed HWND clears both time fuse and one-shot barrier; provider may be probed once.
    before=calls['n']
    guard(fake,'playing',0)
    if calls['n']!=before+1:
        fail.append('new HWND did not receive a fresh capability attempt')

if fail:
    print('H22 FUSE NEXT-CALL H33F1 REPLAY: FAIL')
    for x in fail: print(' -',x)
    raise SystemExit(1)
print('H22 FUSE NEXT-CALL H33F1 REPLAY: PASS')
print(' - slow/no-range fuse suppresses the next logical re-entry even after a scheduler wall-clock jump')
print(' - the one-shot barrier is consumed once and a genuinely new HWND gets a fresh capability attempt')
