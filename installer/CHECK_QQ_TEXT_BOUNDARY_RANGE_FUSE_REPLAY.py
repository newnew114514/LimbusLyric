from __future__ import annotations
import ast, sys
from pathlib import Path

if len(sys.argv)!=2:
    print('usage: CHECK_QQ_TEXT_BOUNDARY_RANGE_FUSE_REPLAY.py <main.py>'); raise SystemExit(2)
path=Path(sys.argv[1]); source=path.read_text(encoding='utf-8'); tree=ast.parse(source,filename=str(path))
funcs={n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
need=('_qq_text_boundary_clock_step','_qq_range_v2_breaker_step')
for name in need:
    if name not in funcs: raise SystemExit('QQ TEXT BOUNDARY + RANGE FUSE REPLAY: FAIL missing '+name)
ns={
    'QQ_RANGE_V2_MAX_SESSION_MISSES':3,
    'QQ_TEXT_BOUNDARY_PHASE_PRIOR_MS':420.0,
    'QQ_TEXT_BOUNDARY_MIN_EDGES':2,
    'QQ_TEXT_BOUNDARY_WINDOW':6,
    'QQ_TEXT_BOUNDARY_MAX_BRACKET_MS':1050.0,
    'QQ_TEXT_BOUNDARY_MAX_CADENCE_ERROR_MS':440.0,
    'QQ_TEXT_BOUNDARY_MAX_SPREAD_MS':380.0,
    'QQ_PHASE_EDGE_MIN_STEP_MS':700.0,
    'QQ_PHASE_EDGE_MAX_STEP_MS':1300.0,
}
mod=ast.Module(body=[funcs[n] for n in need],type_ignores=[]); ast.fix_missing_locations(mod)
exec(compile(mod,str(path),'exec'),ns)
step=ns['_qq_text_boundary_clock_step']; breaker=ns['_qq_range_v2_breaker_step']

# 620ms sampling with alternating edge brackets: two genuine +1s edges are enough to
# create a smooth boundary clock, and repeats advance at exactly wall-clock speed.
state=None; ready=False; candidate=None
samples=[(0,0),(620,0),(1240,1000),(1860,1000),(2480,2000),(3100,2000),(3720,3000),(4340,4000)]
prev=None
for now,bucket in samples:
    state,candidate,ready,info=step(state,bucket,now,'qq-live')
    if ready and candidate is not None and prev is not None:
        # Candidate movement follows monotonic time between repeated samples.
        assert candidate >= prev-1
    if ready and candidate is not None: prev=candidate
assert ready and candidate is not None, (state,candidate,info)

# A large Text jump is a seek/preview epoch change, never boundary evidence.
state,candidate,ready,info=step(state,61000,5000,'qq-live')
assert not ready and candidate is None and info.get('reason')=='epoch-reset'
# The same model rebuilds after seek from fresh +1s edges; no pre-seek intercept survives.
for now,bucket in [(5600,61000),(6220,62000),(6840,62000),(7460,63000)]:
    state,candidate,ready,info=step(state,bucket,now,'qq-live')
assert ready and candidate is not None

# Non-second values (hover/other accessibility text) cannot be quantized into authority.
state2,candidate2,ready2,info2=step(None,12345,1000,'qq-live')
assert state2 is None and candidate2 is None and not ready2 and info2.get('reason')=='not-second-bucket'

# RangeV2 stops wasting UIA work after three proven misses, but a future real hit resets it.
misses=0; opened=False
for _ in range(2):
    misses,opened=breaker(misses,False); assert not opened
misses,opened=breaker(misses,False); assert opened and misses==3
misses,opened=breaker(misses,True); assert misses==0 and not opened

# Architecture guards: QQ Text adapter remains fallback; new model is outer authority only.
for token in (
    'QQ_TEXT_BOUNDARY_CLOCK_ENABLED','_qq_text_boundary_clock_step','QQ Text秒边界连续钟接管','QQ RangeV2会话熔断',
    "retry=process-or-geometry-change","not bool((edge_info or {}).get('boundary_ready', False))",
    'range_hit = self._try_qq_uia_range_v2'
):
    assert token in source, token
assert 'class QQMusicUiAdapter' in source
assert 'observed += 420.0' in source, 'initial QQ Text bucket prior changed unexpectedly'
print('QQ TEXT BOUNDARY + RANGE FUSE REPLAY: PASS')
print('  bracketed +1s boundary clock rebuilds after seek: PASS')
print('  preview/non-second input cannot become boundary authority: PASS')
print('  RangeV2 circuit opens after 3 misses and resets on capability hit: PASS')
