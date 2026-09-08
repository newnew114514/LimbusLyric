from __future__ import annotations
import ast, sys, types
from pathlib import Path

if len(sys.argv) != 2:
    print('usage: CHECK_KUGOU_RAIL_LOCAL_MASTER_REPLAY.py <main.py>')
    raise SystemExit(2)

path = Path(sys.argv[1])
source = path.read_text(encoding='utf-8')
tree = ast.parse(source, filename=str(path))
cls = next((n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'MediaSessionSync'), None)
if cls is None:
    raise SystemExit('MediaSessionSync missing')
need = {
    '_reset_kugou_rail_local_master',
    '_kugou_seed_rail_local_master',
    '_kugou_sync_rail_gesture_anchor',
    '_kugou_rail_local_position',
}
funcs = {n.name: n for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name in need}
missing = need - set(funcs)
if missing:
    print('KUGOU RAIL LOCAL MASTER REPLAY: FAIL')
    print('  missing:', sorted(missing))
    raise SystemExit(31)

# Ensure the default build no longer runs the memory authority paths.
for token in (
    "LIMBUSLYRIC_KUGOU_UIA_FAST_PROBE', '0'",
    "LIMBUSLYRIC_KUGOU_WIN32_CLOCK_PROBE', '0'",
    "LIMBUSLYRIC_KUGOU_MSAA_CLOCK_PROBE', '0'",
    "LIMBUSLYRIC_KUGOU_NUMERIC_CLOCK', '0'",
    "LIMBUSLYRIC_KUGOU_SEEK_SEED_RECOVERY', '0'",
    "LIMBUSLYRIC_KUGOU_PAUSE_RESUME_CAUSAL_BOOTSTRAP', '0'",
):
    if token not in source:
        print('KUGOU RAIL LOCAL MASTER REPLAY: FAIL')
        print('  memory path still default-on:', token)
        raise SystemExit(32)

class FakeTime:
    def __init__(self): self.s = 0.0
    def monotonic(self): return float(self.s)
clock = FakeTime()
logs=[]
ns = {
    'time': clock,
    'KUGOU_RAIL_LOCAL_MASTER_ENABLED': True,
    'KUGOU_RAIL_LOCAL_MASTER_LOG_SEC': 8.0,
    'write_error_log': lambda *a, **k: logs.append((a,k)),
}
helper = next((n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == '_kugou_same_identity_end_continuation_step'), None)
if helper is None:
    raise SystemExit('V29 KuGou end-continuation helper missing')
mod = ast.Module(body=[helper] + [funcs[n] for n in sorted(funcs)], type_ignores=[])
ast.fix_missing_locations(mod)
exec(compile(mod, str(path), 'exec'), ns)

class Dummy:
    pass
for name in need:
    setattr(Dummy, name, ns[name])

def _process_stem(self, x):
    s = str(x or '').lower()
    if s.endswith('.exe'): s=s[:-4]
    return s

def _set_state(self, **kwargs):
    self._state.update(kwargs)

Dummy._process_stem = _process_stem
Dummy._set_state = _set_state

d=Dummy()
d._uia_duration_ms=120000
d._state={'duration_ms':120000, 'status':'paused'}
d._track_key='song-a'
d._process_hint='kgmusic'
d._est_position_ms=None
d._est_anchor_mono=None
d._est_status='unknown'
d._est_source=''
d._kugou_last_gesture_mono=0.0
d._reset_kugou_rail_local_master()

assert d._kugou_seed_rail_local_master(0, status='paused', reason='manual-zero-bootstrap', absolute=True, now_ms=0)
clock.s=0.9
assert d._kugou_rail_local_position('paused') == 0
clock.s=1.0
assert d._kugou_rail_local_position('playing') == 0
clock.s=3.0
assert 1990 <= d._kugou_rail_local_position('playing') <= 2010
clock.s=3.2
paused = d._kugou_rail_local_position('paused')
assert 2190 <= paused <= 2210
clock.s=5.0
assert d._kugou_rail_local_position('paused') == paused
clock.s=5.1
assert d._kugou_rail_local_position('playing') == paused
clock.s=6.1
resumed = d._kugou_rail_local_position('playing')
assert paused + 990 <= resumed <= paused + 1010

# Existing source-locked gesture commit writes its target into _est_position_ms and
# _kugou_last_gesture_mono. The new bridge must immediately promote that to the master.
d._est_position_ms=90000.0
d._est_status='playing'
d._kugou_last_gesture_mono=6100.0
assert d._kugou_sync_rail_gesture_anchor()
assert d._kugou_rail_master_absolute is True
assert abs(d._kugou_rail_master_position_ms - 90000.0) < 0.1
clock.s=7.1
assert 90990 <= d._kugou_rail_local_position('playing') <= 91010

# A transient unknown GSMTC state must not stall a previously-playing local master.
clock.s=8.1
assert 91990 <= d._kugou_rail_local_position('unknown') <= 92010
assert d._kugou_rail_master_status == 'playing'

# Track identity mismatch retires the old master rather than leaking position across songs.
d._track_key='song-b'
clock.s=8.2
assert d._kugou_rail_local_position('playing') is None
assert not d._kugou_rail_master_active

# Wiring checks: KuGou arbitration must explicitly dominate generic UIA/auto-local handoff.
for token in (
    "position_source = 'kugou-rail-local-master'",
    'if kugou_rail_master_public:',
    'sync_waiting=(ui_position_ms is None and not kugou_rail_master_public)',
):
    assert token in source, token

print('KUGOU RAIL LOCAL MASTER REPLAY: PASS')
print('  zero bootstrap -> play -> pause -> resume monotonic continuity: PASS')
print('  source-locked rail gesture -> absolute master re-anchor: PASS')
print('  transient unknown state keeps running; track mismatch retires anchor: PASS')
print('  UIA/Win32/MSAA/numeric/pause-resume/seek-seed position probes default-off: PASS')
