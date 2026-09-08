from __future__ import annotations
import ast, textwrap, sys
from pathlib import Path

if len(sys.argv) != 2:
    print('usage: CHECK_KUGOU_POSTSCAN_BASELINE_REPLAY.py <main.py>')
    raise SystemExit(2)
path=Path(sys.argv[1])
source=path.read_text(encoding='utf-8')
lines=source.splitlines()
tree=ast.parse(source, filename=str(path))
matcher=probe=None
for n in tree.body:
    if isinstance(n, ast.ClassDef) and n.name=='PlayerUiPositionReader':
        for m in n.body:
            if isinstance(m,(ast.FunctionDef,ast.AsyncFunctionDef)):
                if m.name=='_kugou_pause_resume_match_candidate': matcher=m
                elif m.name=='_try_kugou_pause_resume_causal_clock': probe=m
        break
assert matcher and probe, 'missing KuGou postscan bootstrap functions'
matcher_src='\n'.join(lines[matcher.lineno-1:matcher.end_lineno])
ns={}
exec('class T:\n'+textwrap.indent(matcher_src,'    '),ns)
M=ns['T']._kugou_pause_resume_match_candidate

# 20260816-154502: the broad C scan spanned seconds. The candidate value itself was sampled
# near the end of that scan, so D must be judged from its per-block C timestamp, not scan start.
# A true 1x C->D step of 100cs over 1.0s is valid even when B->C already accumulated 3.1s.
r=M(5840,5840,6150,6250,1.0,27100,resume_head_prevalidated=True)
assert r is not None and abs(r['advance_cs']-100) <= 1, 'per-block C->D 1x must survive postscan timing'
# Reusing the broad scan-start time (3s) would incorrectly demand ~300cs and reject the same field.
assert M(5840,5840,6150,6250,3.0,27100,resume_head_prevalidated=True) is None, 'inflated scan-start elapsed must not be treated as sample elapsed'
# The special bypass is only legal after C already passed the causal B->C gate.
assert M(5840,5840,6150,6250,1.0,27100) is None, 'unvalidated large resume head must remain rejected'
# Previous false field: moved during pause, so it stays rejected even with follow-up head prevalidated.
assert M(5493,5541,5650,5750,1.0,27100,resume_head_prevalidated=True) is None, 'paused-moving false timer must remain rejected'

probe_src='\n'.join(lines[probe.lineno-1:probe.end_lineno])
for token in (
    'c_sample_mono = time.monotonic()',
    'groups.append((int(base), n4, rows, float(c_sample_mono)))',
    "'c_ready_mono':c_ready_mono",
    'd_sample_mono=time.monotonic()',
    'sample_elapsed=max(0.001,float(d_sample_mono)-float(c_sample_mono))',
    'resume_head_prevalidated=True',
    'e_sample_mono=time.monotonic()',
    'elapsed=max(0.001,float(e_sample_mono)-float(d_sample_mono))',
    'timestamp=per-block',
):
    assert token in probe_src, f'missing per-sample timestamp guard: {token}'

print('KUGOU POSTSCAN BASELINE REPLAY: PASS')
print('  154502 broad-scan timestamp inflation => reproduced and blocked')
print('  per-block C/D/E sample timestamps => required')
print('  paused-moving false timer => still rejected')
