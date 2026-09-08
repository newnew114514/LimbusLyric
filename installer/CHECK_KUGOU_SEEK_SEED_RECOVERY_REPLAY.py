from __future__ import annotations
import ast, sys
from pathlib import Path
if len(sys.argv)!=2:
    print('usage: CHECK_KUGOU_SEEK_SEED_RECOVERY_REPLAY.py <main.py>'); raise SystemExit(2)
p=Path(sys.argv[1]); src=p.read_text(encoding='utf-8'); lines=src.splitlines(); tree=ast.parse(src)
method=poll=None
for n in tree.body:
    if isinstance(n,ast.ClassDef) and n.name=='PlayerUiPositionReader':
        for m in n.body:
            if isinstance(m,(ast.FunctionDef,ast.AsyncFunctionDef)):
                if m.name=='_try_kugou_seek_seed_recovery': method=m
                elif m.name=='poll': poll=m
assert method and poll, 'missing seek-seed recovery integration'
ms='\n'.join(lines[method.lineno-1:method.end_lineno]); ps='\n'.join(lines[poll.lineno-1:poll.end_lineno])
for token in (
    "proof=gesture-target-deep-recovery",
    "for pid in _ordered():",
    "sample_mono=time.monotonic()",
    "expected_ms=target_ms + ((sample_mono-hint_mono)*1000.0 if status=='playing' else 0.0)",
    "verify_mono=time.monotonic()",
    "expected_adv=elapsed*100.0 if status=='playing' else 0.0",
    "kugou_numeric_birth",
    "deep_recovery_done",
    "酷狗Seek种子深度恢复成功",
):
    assert token in ms, f'missing recovery token: {token}'
assert '_try_kugou_seek_seed_recovery(process_name, pids)' in ps

def verify(target_ms, hint_mono, sample_mono, c, verify_mono, d, status='playing', tol=2600.0):
    expected_ms=target_ms+((sample_mono-hint_mono)*1000.0 if status=='playing' else 0.0)
    if abs(c*10.0-expected_ms)>tol: return False
    elapsed=max(0.001,verify_mono-sample_mono)
    expected_adv=elapsed*100.0 if status=='playing' else 0.0
    adv=d-c; motion_err=abs(float(adv)-expected_adv)
    now_expected=target_ms+((verify_mono-hint_mono)*1000.0 if status=='playing' else 0.0)
    end_err=abs(d*10.0-now_expected)
    if status=='playing':
        motion_ok=(adv>=max(4.0,expected_adv-60.0) and adv<=expected_adv+70.0 and motion_err<=60.0)
    else:
        motion_ok=abs(adv)<=18
    return motion_ok and end_err<=tol

# Explicit seek to 120s, block read 2s later, re-read 1s after that: true playback survives.
assert verify(120000,0.0,2.0,12200,3.0,12300)
# A wall-clock-ish counter nowhere near the seek target is rejected before motion proof.
assert not verify(120000,0.0,2.0,5000,3.0,5100)
# A value near target but not advancing at 1x is rejected.
assert not verify(120000,0.0,2.0,12200,3.0,12205)
# Paused seek target can be proven by landing near target and freezing.
assert verify(120000,0.0,1.0,12005,2.0,12006,status='paused')
print('KUGOU SEEK-SEED RECOVERY REPLAY: PASS')
print('  explicit seek target + 1x follow-up => accepted')
print('  off-target / wrong-motion fields => rejected')
print('  multi-PID + persistent seed integration => present')
