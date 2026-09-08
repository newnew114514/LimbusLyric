from __future__ import annotations
import ast, textwrap, sys
from pathlib import Path

if len(sys.argv) != 2:
    print('usage: CHECK_KUGOU_PAUSE_RESUME_CAUSAL_BOOTSTRAP_REPLAY.py <main.py>')
    raise SystemExit(2)
path=Path(sys.argv[1])
source=path.read_text(encoding='utf-8')
lines=source.splitlines()
tree=ast.parse(source, filename=str(path))
cls=None; first_gate=None; matcher=None; probe=None; poll=None
for n in tree.body:
    if isinstance(n, ast.ClassDef) and n.name=='PlayerUiPositionReader':
        cls=n
        for m in n.body:
            if isinstance(m,(ast.FunctionDef,ast.AsyncFunctionDef)):
                if m.name=='_kugou_pause_resume_initial_motion_ok': first_gate=m
                elif m.name=='_kugou_pause_resume_match_candidate': matcher=m
                elif m.name=='_try_kugou_pause_resume_causal_clock': probe=m
                elif m.name=='poll': poll=m
        break
assert cls and first_gate and matcher and probe and poll, 'missing KuGou pause/resume causal bootstrap implementation'
first_gate_src='\n'.join(lines[first_gate.lineno-1:first_gate.end_lineno])
matcher_src='\n'.join(lines[matcher.lineno-1:matcher.end_lineno])
ns={}
exec('class T:\n'+textwrap.indent(first_gate_src+'\n'+matcher_src,'    '),ns)
G=ns['T']._kugou_pause_resume_initial_motion_ok
M=ns['T']._kugou_pause_resume_match_candidate


# 20260816-153250 prefilter regression: paused-B -> first playing sample can be ~4s apart,
# while the worker only observed playing ~2s before C. The real counter must survive; static
# integers and implausible jumps must not.
assert G(5840,5840,6240,2.0,4.0,27100), 'late-C real motion must survive initial gate'
assert not G(5840,5840,5840,2.0,4.0,27100), 'static frozen integers must be removed before hard cap'
assert not G(5840,5840,9000,2.0,4.0,27100), 'oversized resume jump must be rejected'
assert G(0,0,160,1.60,1.60,27100), 'cold start at exactly 0cs must remain eligible after real resume motion'
assert not G(0,0,0,1.60,1.60,27100), 'static zero fields must still be rejected'

# Current host regression: a genuine paused position around 58.4s freezes, then resumes at 1x.
r=M(5840,5842,5855,5920,0.65,27100)
assert r is not None, 'prompt real pause->resume clock was not accepted'
assert r['pause_motion_cs'] <= 8 and abs(r['advance_cs']-r['expected_cs']) <= 48

# 20260816-153250: the first playing sample arrived ~2s after paused-B. The old fixed
# resume-head <=65cs filter rejected the real clock and then filled a 120k static hard-cap.
r=M(5840,5840,6040,6105,0.65,27100,resume_window_sec=2.0)
assert r is not None, 'late first-playing sample must remain eligible under resume epoch window'
assert r['resume_head_cs'] == 200

# 20260816-145221 false field kept moving while paused: 54.93 -> 55.41s in <1s.
assert M(5493,5541,5550,5615,0.65,27100) is None, 'paused-moving false field must be rejected'
# Motion-only A/B/C style evidence is not causal pause proof.
assert M(4946,5011,5020,5085,0.65,27100) is None, 'motion-only field must not satisfy pause-freeze proof'
# Resume head cannot jump by many seconds before the first playing observation.
assert M(5840,5840,7000,7065,0.65,27100) is None, 'large resume-head jump must be rejected'
# Near-zero fields need no memory authority; normal track-start provisional is safer.
assert M(0,0,10,75,0.65,27100) is None, 'near-zero field must not become memory authority'
# Out-of-range values cannot be a playback clock for this duration.
assert M(5840,5840,5850,40000,0.65,27100) is None

probe_src='\n'.join(lines[probe.lineno-1:probe.end_lineno])
poll_src='\n'.join(lines[poll.lineno-1:poll.end_lineno])
for token in (
    'proof=pause-freeze+resume-1x',
    "'source': 'kugou-pause-resume-memory-cs'",
    'KUGOU_PAUSE_RESUME_CAUSAL_BOOTSTRAP_ENABLED',
    'KUGOU_PAUSE_RESUME_ARM_DELAY_SEC',
    "phase':'resume-armed'",
    '_kugou_pause_resume_initial_motion_ok',
    'moving_candidates=',
    'progressive=1',
    'remaining_paired_by_pid',
    '_kugou_pause_resume_match_candidate',
):
    assert token in probe_src, f'missing probe token: {token}'
assert '_try_kugou_pause_resume_causal_clock(process_name, pids)' in poll_src
assert "source': 'kugou-pause-resume-causal-proof'" in poll_src

print('KUGOU PAUSE-RESUME CAUSAL BOOTSTRAP REPLAY: PASS')
print('  zero/late-C initial gate: 0cs cold-start + real motion kept; static/oversized candidates rejected')
print('  paused freeze + prompt/late resume 1x => accepted')
print('  host paused-moving false timer => rejected')
print('  motion-only / resume-jump / near-zero => rejected')
print('  poll integration => present')
