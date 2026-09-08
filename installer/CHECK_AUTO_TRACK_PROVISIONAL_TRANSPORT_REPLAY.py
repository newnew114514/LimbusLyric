from pathlib import Path
import ast, sys, textwrap

if len(sys.argv) != 2:
    raise SystemExit('usage: CHECK_AUTO_TRACK_PROVISIONAL_TRANSPORT_REPLAY.py <main.py>')
path = Path(sys.argv[1])
source = path.read_text(encoding='utf-8')
tree = ast.parse(source)

def method_source(cls_name, method):
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == cls_name:
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == method:
                    return ast.get_source_segment(source, item)
    raise AssertionError(f'missing {cls_name}.{method}')

def const(name):
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError(f'missing const {name}')

class FakeTime:
    def __init__(self): self.ms = 500000.0
    def monotonic(self): return self.ms / 1000.0
    def step(self, ms): self.ms += float(ms)

T = FakeTime(); logs = []
def write_error_log(label, *a, detail=None, **k): logs.append((label, detail))

ns = {
    'time': T,
    'write_error_log': write_error_log,
    'AUTO_TRACK_UNKNOWN_PLAY_CARRY_EVIDENCE_MAX_AGE_MS': const('AUTO_TRACK_UNKNOWN_PLAY_CARRY_EVIDENCE_MAX_AGE_MS'),
    'AUTO_TRACK_UNKNOWN_PLAY_CARRY_MAX_MS': const('AUTO_TRACK_UNKNOWN_PLAY_CARRY_MAX_MS'),
}
methods = ['_start_auto_local_clock', '_arm_auto_local_unknown_play_carry', '_auto_local_position', '_reset_auto_local_clock']
body = '\n\n'.join(textwrap.indent(method_source('MediaSessionSync', m), '    ') for m in methods)
exec('class H:\n' + body, ns)
H = ns['H']
H._process_stem = staticmethod(lambda p: str(p or '').lower().replace('.exe',''))

def make(proc='qqmusic', current='unknown', last='playing', age=120.0):
    h = H()
    h._state = {'status': current}
    h._process_hint = proc
    h._uia_duration_ms = None
    h._last_explicit_transport_status = last
    h._last_explicit_transport_process = proc
    h._last_explicit_transport_mono = T.ms - float(age)
    h._track_identity_epoch = 7
    h._last_explicit_transport_identity_epoch = 6
    h._auto_local_active = False
    h._auto_local_position_ms = 0.0
    h._auto_local_anchor_mono = None
    h._auto_local_status = 'unknown'
    h._auto_local_started_mono = None
    h._auto_local_unknown_play_carry = False
    h._auto_local_unknown_play_carry_until_mono = 0.0
    h._auto_local_unknown_play_carry_process = ''
    h._auto_local_unknown_play_carry_logged = False
    h._auto_handoff_pending = None
    h._qq_auto_anchor_pending = None
    return h

# A. Exact regression from the friend's log: previous QQ was explicitly playing, the
# new identity is confirmed, but GSMTC status is transiently unknown for ~8.4s.
h = make()
h._start_auto_local_clock(0)
assert h._arm_auto_local_unknown_play_carry(startup_existing=False)
for _ in range(42):
    T.step(200)
    value = h._auto_local_position('unknown')
assert 8350 <= value <= 8450, value
assert h._auto_local_status == 'playing'
assert any(label == '新曲临时时钟沿用最近播放态' and 'authority=display-only' in (detail or '') for label, detail in logs)
print(f'  QQ unknown-status 8.4s gap keeps provisional display moving ({value}ms): PASS')

# B. A real playing observation retires the special carry without changing continuity.
T.step(200); before = h._auto_local_position('playing')
assert not h._auto_local_unknown_play_carry and h._auto_local_status == 'playing'
T.step(300); after = h._auto_local_position('playing')
assert 450 <= after - value <= 550
print('  real PLAYING observation retires special carry and preserves continuity: PASS')

# C. Explicit PAUSED is a hard veto. The display freezes on subsequent paused polls.
h = make(); h._start_auto_local_clock(50); assert h._arm_auto_local_unknown_play_carry(False)
T.step(600); paused_at = h._auto_local_position('paused')
assert not h._auto_local_unknown_play_carry and h._auto_local_status == 'paused'
T.step(1400); paused_later = h._auto_local_position('paused')
assert paused_later == paused_at
print('  explicit PAUSED veto freezes provisional display: PASS')

# D. STOPPED is equally explicit and must never inherit prior PLAYING.
h = make(current='stopped'); h._start_auto_local_clock(0)
assert not h._arm_auto_local_unknown_play_carry(False)
T.step(1000); assert h._auto_local_position('stopped') == 0
print('  explicit STOPPED veto prevents fabricated playback: PASS')

# E. Startup late-attach cannot pretend an already-running song started at zero.
h = make(); h._start_auto_local_clock(0)
assert not h._arm_auto_local_unknown_play_carry(startup_existing=True)
T.step(1500); assert h._auto_local_position('unknown') == 0
print('  startup late-attach remains real-anchor-only: PASS')

# F. Old or cross-player evidence is not allowed to carry.
h = make(age=const('AUTO_TRACK_UNKNOWN_PLAY_CARRY_EVIDENCE_MAX_AGE_MS') + 1); h._start_auto_local_clock(0)
assert not h._arm_auto_local_unknown_play_carry(False)
h = make(proc='qqmusic'); h._last_explicit_transport_process = 'cloudmusic'; h._start_auto_local_clock(0)
assert not h._arm_auto_local_unknown_play_carry(False)
h = make(proc='qqmusic'); h._last_explicit_transport_identity_epoch = 5; h._start_auto_local_clock(0)
assert not h._arm_auto_local_unknown_play_carry(False)
print('  stale/cross-player/cross-epoch PLAYING evidence is rejected: PASS')

# G. NetEase shares the same protection; KuGou remains on its dedicated H7 rail clock.
h = make(proc='cloudmusic'); h._start_auto_local_clock(120); assert h._arm_auto_local_unknown_play_carry(False)
T.step(900); assert h._auto_local_position('unknown') >= 1000
h = make(proc='kgmusic'); h._start_auto_local_clock(0); assert not h._arm_auto_local_unknown_play_carry(False)
print('  NetEase protected; KuGou dedicated transport logic untouched: PASS')

# H. Carry has a hard lifetime. A delayed poll cannot extend it beyond the configured cap.
h = make(); h._start_auto_local_clock(0); assert h._arm_auto_local_unknown_play_carry(False)
T.step(const('AUTO_TRACK_UNKNOWN_PLAY_CARRY_MAX_MS') + 3000)
value = h._auto_local_position('unknown')
assert int(const('AUTO_TRACK_UNKNOWN_PLAY_CARRY_MAX_MS')) - 2 <= value <= int(const('AUTO_TRACK_UNKNOWN_PLAY_CARRY_MAX_MS')) + 2, value
T.step(1000); assert h._auto_local_position('unknown') == value
print('  display-only carry expires at hard budget without runaway clock: PASS')

# I. Static production wiring: only explicit transport observations feed the carry evidence;
# bind_track arms it only in the auto-provisional non-KuGou lane.
poll = method_source('MediaSessionSync', '_poll_loop')
bind = method_source('MediaSessionSync', 'bind_track')
assert "explicit_transport_status = None" in poll
assert "explicit_transport_status = status" in poll
assert "self._last_explicit_transport_status = str(explicit_transport_status)" in poll
assert "self._last_explicit_transport_identity_epoch = int(explicit_transport_identity_epoch)" in poll
assert "self._arm_auto_local_unknown_play_carry(startup_existing=startup_existing)" in bind
assert "if _auto_proc == 'kgmusic' and KUGOU_RAIL_LOCAL_MASTER_ENABLED" in bind
assert 'AUTO-TRACK PROVISIONAL-TRANSPORT H9' in source
print('  production wiring + H9 build tag present: PASS')

print('AUTO TRACK PROVISIONAL TRANSPORT REPLAY: PASS')
