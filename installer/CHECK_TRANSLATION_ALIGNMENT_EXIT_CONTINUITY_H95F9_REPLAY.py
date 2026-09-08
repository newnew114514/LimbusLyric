#!/usr/bin/env python3
from __future__ import annotations
import ast, pathlib, sys, bisect, re, threading, time
if len(sys.argv)!=2: raise SystemExit('usage: CHECK_TRANSLATION_ALIGNMENT_EXIT_CONTINUITY_H95F9_REPLAY.py <main.py>')
p=pathlib.Path(sys.argv[1]).resolve(); src=p.read_text(encoding='utf-8'); tree=ast.parse(src)
def need(c,m):
    if not c: raise AssertionError(m)
marker='# H95F9 translation alignment + exit continuity'
need(marker in src,'H95F9 marker missing')
need('+ TRANSLATION ALIGNMENT + EXIT CONTINUITY H95F9' in src,'H95F9 build tag missing')
start=src.index(marker); end=src.index('# H95F10 bilingual source lock + exit dirty closure + shell stability',start); block=src[start:end]
for token in (
    'H95F9_TRANSLATION_MAX_TOLERANCE_MS = 2600',
    'policy=provider-only-no-fabrication',
    'material_p0=', 'effect_p0=0.000', 'direct_drop=0',
    "globals()['_h95f5_align_translation_lines']=_h95f9_align_translation_lines",
    "globals()['_h62_decay_progress']=_h95f9_blur_progress",
    "globals()['_h62_decay_mix']=_h95f9_blur_mix",
): need(token in block,'H95F9 integration missing: '+token)
for bad in ('MediaSessionSync.position','MediaSessionSync.seek','LyricWindow._playback_position =','LyricSearchEngine.search ='):
    need(bad not in block,'H95F9 crossed timing/search authority: '+bad)
funcs={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
def fn(name): need(name in funcs,'function missing: '+name); return funcs[name]
def run(names,ns):
    mod=ast.Module(body=[fn(x) for x in names],type_ignores=[]); exec(compile(mod,'<h95f9>','exec'),ns)

# Alignment replay: old +/-900ms nearest matching misses a coherent +1250ms provider offset.
def old_align(main_lines, timeline, tolerance_ms=900):
    rows=[(int(x[0]),str(x[1])) for x in timeline if str(x[1]).strip()]; times=[x[0] for x in rows]; out=[]
    for line in main_lines:
        at=int(line['start_ms']); pos=bisect.bisect_left(times,at); cand=[rows[i] for i in (pos-1,pos,pos+1) if 0<=i<len(rows)]
        best=min(cand,key=lambda x:abs(x[0]-at)) if cand else None
        out.append(best[1] if best and abs(best[0]-at)<=tolerance_ms else '')
    return out
ns={'bisect':bisect,'re':re,'H95F5_TRANSLATION_ALIGN_TOLERANCE_MS':900,
    'H95F9_TRANSLATION_MAX_TOLERANCE_MS':2600,'H95F9_TRANSLATION_SKIP_COST_MS':1450,
    'H95F9_TRANSLATION_OFFSET_PROBE_MS':3200,'_H95F9_ALIGN_PRE':old_align}
run(['_h95f9_translation_rows','_h95f9_translation_offset','_h95f9_local_translation_tolerance','_h95f9_align_translation_lines'],ns)
align=ns['_h95f9_align_translation_lines']
main=[{'start_ms':0,'text':'a'},{'start_ms':3000,'text':'b'},{'start_ms':6000,'text':'c'},{'start_ms':9000,'text':'d'}]
trans=[(1250,'甲'),(4250,'乙'),(7250,'丙'),(10250,'丁')]
need(old_align(main,trans).count('')>=3,'offset fixture no longer demonstrates old miss')
out=align(main,trans)
need(out==['甲','乙','丙','丁'],'offset-aware monotonic alignment failed')
# Missing source rows are never fabricated/duplicated.
short=[(100,'甲'),(6100,'丙'),(9100,'丁')]
out2=align(main,short)
need(sum(bool(x) for x in out2)<=len(short),'missing provider translation was fabricated')
need(len(out2)==len(main),'alignment result length drifted')
# Same-as-original provider row must not be presented as translation.
same=align([{'start_ms':1000,'text':'hello'}],[(1000,'hello')])
need(same==[''],'identical original text leaked as translation')

# Exit replay: mature material can begin at 0.82, while release visibility must start at 1.0
# and H95F6's exit progress starts from 0 rather than consuming the history blur progress.
class TLS: pass
class Row:
    exit_effect='blur_decay'; _h62_decay_release_mono=1000.0; _h76_blur_release_duration_ms=1800.0; _h62_decay_release_draw_count=1
    _h62_decay_release_progress=0.82
row=Row()
ns2={'time':time,'H95F9_EXIT_VISIBILITY_MIN_MS':900.0,'_h95f9_mix_tls':TLS(),
     '_H95F9_BLUR_MIX_PRE':lambda p:(0.0,0.4,0.6,max(0.0,1.0-p)),
     '_H95F9_EXIT_PROGRESS_PRE':lambda r:0.82,
     '_h70_effect_key':lambda x:x}
run(['_h95f9_release_envelope','_h95f9_blur_mix','_h95f9_exit_progress'],ns2)
env=ns2['_h95f9_release_envelope']; mix=ns2['_h95f9_blur_mix']; xp=ns2['_h95f9_exit_progress']
need(abs(env(row,1000.0)-0.0)<1e-9,'release envelope did not start at zero')
need(0.45<env(row,1900.0)<0.55,'release envelope midpoint is not smooth/continuous')
ns2['_h95f9_mix_tls'].exit_envelope=0.0
need(abs(mix(0.82)[3]-1.0)<1e-9,'material p0 still pre-consumed release visibility')
ns2['_h95f9_mix_tls'].exit_envelope=0.5
need(abs(mix(0.90)[3]-0.5)<1e-9,'independent release visibility envelope failed')
# Monkeypatch monotonic time for exit-progress call.
orig=time.monotonic
try:
    time.monotonic=lambda:1.0
    need(abs(xp(row)-0.0)<1e-9,'blur exit effect progress did not restart at zero')
finally:
    time.monotonic=orig

print('TRANSLATION ALIGNMENT + EXIT CONTINUITY H95F9 REPLAY: PASS')
print('  provider-offset monotonic translation rescue: PASS')
print('  missing translation remains missing (no fabrication): PASS')
print('  residence blur vs real exit envelope separation: PASS')
print('  direct-drop/clock/search authority unchanged: PASS')
