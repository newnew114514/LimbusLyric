from __future__ import annotations
import ast, textwrap, sys
from pathlib import Path

if len(sys.argv) != 2:
    print('usage: CHECK_KUGOU_CAUSAL_CLOCK_GUARD_REPLAY.py <main.py>')
    raise SystemExit(2)
path = Path(sys.argv[1])
source = path.read_text(encoding='utf-8')
lines = source.splitlines()
tree = ast.parse(source, filename=str(path))
node = None
for n in tree.body:
    if isinstance(n, ast.ClassDef) and n.name == 'AsyncPlayerUiPositionReader':
        for m in n.body:
            if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)) and m.name == '_guard_kugou_numeric_causal_result':
                node = m
                break
if node is None:
    raise SystemExit('missing AsyncPlayerUiPositionReader._guard_kugou_numeric_causal_result')
method_src = '\n'.join(lines[node.lineno-1:node.end_lineno])

class FakeTime:
    def __init__(self, t=100.0): self.t=float(t)
    def monotonic(self): return self.t
    def advance(self, dt): self.t += float(dt)

class FakeReader:
    def __init__(self):
        self.rejected=[]
        self._kugou_numeric_seed_rejected=set()
        self._locator_cache={'kgmusic.exe': {
            'kugou_numeric_pid':23376,
            'kugou_numeric_addr':int('26681EB9F88',16),
            'kugou_numeric_birth':123,
            'kugou_numeric_type':'i32-cs',
            'kugou_numeric_learned_at':1,
        }}
        self.saved=0
    def reject_kugou_numeric_anchor(self, reason=''):
        self.rejected.append(str(reason))
    def _save_locator_cache(self): self.saved += 1

class FakeOSPath:
    @staticmethod
    def basename(s): return str(s).replace('\\','/').split('/')[-1]
class FakeOS:
    path=FakeOSPath()

logs=[]
def write_error_log(name, exc=None, detail=None):
    logs.append((name, detail if detail is not None else exc))

clock=FakeTime()
ns={'time':clock,'os':FakeOS(),'write_error_log':write_error_log}
exec('class Guard:\n'+textwrap.indent(method_src,'    '), ns)
Guard=ns['Guard']

KEY='kgnum:23376:26681EB9F88:i32-cs'
def hit(pos, detail):
    return {'position_ms':int(pos),'duration_ms':271000,'confidence':250,
            'source':'kugou-numeric-memory-cs','source_key':KEY,'detail':detail}

# Host log regression: motion-only proof must not become public authority.
g=Guard(); g._transport_status='playing'; r=FakeReader()
out=g._guard_kugou_numeric_causal_result(r,'kgmusic.exe', hit(49460,'proof_age=13.38s proof=continuous-no-wrap candidates=1 status=playing'))
assert out['position_ms'] is None and out['source']=='kugou-numeric-causal-quarantine'
assert out['_kugou_numeric_candidate_position_ms']==49460

# Subsequent fast-anchor reads from the same motion-only address stay quarantined.
clock.advance(.3)
out=g._guard_kugou_numeric_causal_result(r,'kgmusic.exe', hit(50010,'raw=5001 fast-anchor=1 guarded=1 status=playing'))
assert out['position_ms'] is None

# 20260816-145221 pause behavior: 54.93 -> 55.41 -> 55.83 keeps moving ~1x while paused.
# This must ban the field and clear its persisted seed instead of trusting it.
g._transport_status='paused'
clock.advance(.1); out=g._guard_kugou_numeric_causal_result(r,'kgmusic.exe', hit(54930,'raw=5493 fast-anchor=1 guarded=1 status=paused'))
assert out['position_ms'] is None
clock.advance(.4); out=g._guard_kugou_numeric_causal_result(r,'kgmusic.exe', hit(55410,'raw=5541 fast-anchor=1 guarded=1 status=paused'))
assert out['position_ms'] is None
clock.advance(.4); out=g._guard_kugou_numeric_causal_result(r,'kgmusic.exe', hit(55830,'raw=5583 fast-anchor=1 guarded=1 status=paused'))
assert out['position_ms'] is None
assert KEY in g._kugou_numeric_causal_bad_keys
assert r.rejected, 'bad paused field was not rejected'
assert r.saved >= 1, 'persisted false seed was not cleared'
loc=r._locator_cache['kgmusic.exe']
assert 'kugou_numeric_addr' not in loc and 'kugou_numeric_pid' not in loc

# Once banned in this LimbusLyric process, it can never regain authority from motion alone.
clock.advance(.2); g._transport_status='playing'
out=g._guard_kugou_numeric_causal_result(r,'kgmusic.exe', hit(57000,'proof=continuous-no-wrap status=playing'))
assert out['position_ms'] is None

# A genuinely frozen value while paused is causal playback evidence and may be published.
g2=Guard(); g2._transport_status='playing'; r2=FakeReader(); clock.t=200.0
out=g2._guard_kugou_numeric_causal_result(r2,'kgmusic.exe', hit(49460,'proof=continuous-no-wrap status=playing'))
assert out['position_ms'] is None
g2._transport_status='paused'; clock.advance(.1)
out=g2._guard_kugou_numeric_causal_result(r2,'kgmusic.exe', hit(50000,'fast-anchor=1 status=paused'))
assert out['position_ms'] is None
clock.advance(.82)
out=g2._guard_kugou_numeric_causal_result(r2,'kgmusic.exe', hit(50040,'fast-anchor=1 status=paused'))
assert out['position_ms']==50040 and out['source']=='kugou-numeric-memory-cs'
assert out.get('_kugou_numeric_causal_trust')=='pause-freeze-observed'

# 20260816-162757 regression: the multipid A scan can consume ~0.5s, so the first
# paused numeric sample arrives too late for the old two-paused-sample gate.  Extrapolate the
# already motion-proven sample only to the observed Pause edge; suppressed motion during the scan
# is causal evidence, while a wall timer still advances by the full scan interval.
g_short=Guard(); g_short._transport_status='playing'; r_short=FakeReader(); clock.t=250.0
out=g_short._guard_kugou_numeric_causal_result(r_short,'kgmusic.exe', hit(52500,'raw=5250 fast-anchor=1 guarded=1 status=playing'))
assert out['position_ms'] is None
clock.advance(.70); g_short._transport_status='paused'
r_short._kugou_pause_resume_probe={'pause_seen_mono':clock.monotonic()}
clock.advance(.48)  # expensive multipid A scan
out=g_short._guard_kugou_numeric_causal_result(r_short,'kgmusic.exe', hit(53210,'raw=5321 fast-anchor=1 guarded=1 status=paused'))
assert out['position_ms']==53210 and out.get('_kugou_numeric_causal_trust')=='pause-entry-suppressed-motion'
clock.advance(.18); g_short._transport_status='playing'; r_short._kugou_pause_resume_probe=None
out=g_short._guard_kugou_numeric_causal_result(r_short,'kgmusic.exe', hit(53390,'raw=5339 fast-anchor=1 guarded=1 status=playing'))
assert out['position_ms']==53390

# Same timing, but a wall-clock-like field includes the entire 480ms paused scan and cannot pass.
g_wall=Guard(); g_wall._transport_status='playing'; r_wall=FakeReader(); clock.t=275.0
out=g_wall._guard_kugou_numeric_causal_result(r_wall,'kgmusic.exe', hit(50000,'proof=continuous-no-wrap status=playing'))
assert out['position_ms'] is None
clock.advance(.70); g_wall._transport_status='paused'
r_wall._kugou_pause_resume_probe={'pause_seen_mono':clock.monotonic()}
clock.advance(.48)
out=g_wall._guard_kugou_numeric_causal_result(r_wall,'kgmusic.exe', hit(51180,'fast-anchor=1 status=paused'))
assert out['position_ms'] is None
clock.advance(.18); g_wall._transport_status='playing'; r_wall._kugou_pause_resume_probe=None
out=g_wall._guard_kugou_numeric_causal_result(r_wall,'kgmusic.exe', hit(51360,'fast-anchor=1 status=playing'))
assert out['position_ms'] is None and out['source']=='kugou-numeric-causal-quarantine'

# An explicit seek target is also causal proof. Capture is before golden reader clears the hint.
g3=Guard(); g3._transport_status='playing'; r3=FakeReader(); clock.t=300.0
hint={'target_ms':120000.0,'mono':299.4}
out=g3._guard_kugou_numeric_causal_result(r3,'kgmusic.exe', hit(120500,'fast-anchor=1 status=playing'), pre_seek_hint=hint)
assert out['position_ms']==120500 and out.get('_kugou_numeric_causal_trust')=='explicit-seek-target'

# Persisted/fast seed without causal proof must not bypass the guard in a fresh app session.
g4=Guard(); g4._transport_status='playing'; r4=FakeReader(); clock.t=400.0
out=g4._guard_kugou_numeric_causal_result(r4,'kgmusic.exe', hit(61000,'raw=6100 fast-anchor=1 guarded=1 status=playing'))
assert out['position_ms'] is None and out['source']=='kugou-numeric-causal-quarantine'

print('KUGOU CAUSAL CLOCK GUARD REPLAY: PASS')
print('  continuous-no-wrap => quarantine')
print('  paused advancing false field => ban + persistent-seed removal')
print('  pause freeze => causal trust')
print('  short-pause entry suppression => causal trust; wall-like motion => quarantine')
print('  explicit seek target => causal trust')
