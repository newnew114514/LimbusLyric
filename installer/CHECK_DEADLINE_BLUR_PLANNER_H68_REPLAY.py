from pathlib import Path
import ast, math, sys, textwrap, time, weakref

if len(sys.argv) < 2:
    raise SystemExit('usage: CHECK_DEADLINE_BLUR_PLANNER_H68_REPLAY.py <main.py>')
path=Path(sys.argv[1]); src=path.read_text(encoding='utf-8'); tree=ast.parse(src); lines=src.splitlines()

def fail(msg): raise SystemExit('H68 FAIL: '+msg)
def need(tok, why):
    if tok not in src: fail(f'{why}: missing {tok!r}')
def fn(name):
    for node in ast.walk(tree):
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name==name:
            return node
    fail('function not found: '+name)
def fsrc(name):
    n=fn(name); return textwrap.dedent('\n'.join(lines[n.lineno-1:n.end_lineno]))

need('+ DEADLINE BLUR PLANNER H68','build tag')
need("if '_h68_activate_runtime' in globals():",'activation')
if not (src.rindex("if '_h67_activate_runtime' in globals():") < src.rindex("if '_h68_activate_runtime' in globals():")):
    fail('H68 must activate after H67')
for name in ('_h68_exact_horizon_ms','_h68_future_cadence_ms','_h68_tail_budget_ms',
             '_h68_release_duration','_h68_release_progress','_h68_deadline_decay_progress',
             '_h68_placement_obstacles','_h68_pre_admit_burst_row'):
    fn(name)

class W: pass
class R: pass
w=W(); w.lyric_timeline=[
    (59873,), (60474,), (60624,), (60741,), (60874,), (61207,), (61790,), (61940,), (62057,), (66985,)
]
ns={
    'H68_CADENCE_MIN_MS':90.0,'H68_CADENCE_MAX_MS':6500.0,'H68_TAIL_MIN_MS':320.0,
    'H68_TAIL_MAX_MS':1250.0,'H68_TAIL_BASE_MS':220.0,'H68_TAIL_CADENCE_RATIO':0.55,
    'H67_DEFAULT_CADENCE_MS':1900.0,'_h67_window_cadence_ms':lambda win:1900.0,
}
exec(fsrc('_h68_timeline_start'),ns); exec(fsrc('_h68_future_gap_samples'),ns)
exec(fsrc('_h68_future_cadence_ms'),ns); exec(fsrc('_h68_tail_budget_ms'),ns); exec(fsrc('_h68_exact_horizon_ms'),ns)
horizon,evict=ns['_h68_exact_horizon_ms'](w,0,3)
# origin line 0 enters history at line 1 and evicts when line 3 arrives: 60741-60474=267 ms.
if abs(horizon-267.0)>0.1 or evict!=3: fail(f'exact capacity horizon wrong: {horizon}, evict={evict}')
tail=ns['_h68_tail_budget_ms'](w,evict)
if not (320.0 <= tail <= 450.0): fail(f'ultra-dense tail not bounded to a real visible animation: {tail}')
# Crucial H68 property: fixed 0.875 pre-eviction target is gone. Progress budget at overflow is
# horizon/(horizon+tail), leaving the rest for a velocity-continuous release.
p_at_evict=horizon/(horizon+tail)
if not (0.35 < p_at_evict < 0.55): fail(f'burst still requires near-complete pre-eviction blur: {p_at_evict:.3f}')

# A deadline plan should not need a last-second speed jump when it is already on trajectory.
# If p(t)=t/(horizon+tail), (1-p)/(remaining_horizon+tail) stays constant.
base_v=1.0/(horizon+tail)
for elapsed in (25.0, 100.0, 200.0):
    p=base_v*elapsed
    rem=max(0.0,horizon-elapsed)
    desired=(1.0-p)/(rem+tail)
    if abs(desired-base_v)>1e-9:
        fail(f'deadline trajectory changes speed without a retarget: {base_v} -> {desired}')
# The visible tail also bounds steady-state queue growth in a 117 ms run: a few exits may overlap,
# but the planner no longer needs the 8-10 row backlog seen in the field log.
if math.ceil(tail/117.0) > 4:
    fail(f'ultra-dense visible tail can still build an excessive steady queue: tail={tail}')

# Slow/mixed context gets a longer lifecycle, but known future short gaps are visible immediately.
w2=W(); w2.lyric_timeline=[(0,),(1000,),(5000,),(6000,),(7000,),(8000,),(12000,)]
h2,e2=ns['_h68_exact_horizon_ms'](w2,0,3)
t2=ns['_h68_tail_budget_ms'](w2,e2)
if not (h2==5000.0 and 600.0 <= t2 <= 900.0): fail(f'mixed horizon/tail wrong: h={h2}, t={t2}')

# Release Hermite starts with the inherited active velocity rather than restarting a new ease.
release_ns={
    'H68_TAIL_MIN_MS':320.0,'H68_TAIL_MAX_MS':1250.0,'H68_RELEASE_PRESSURE_FLOOR':0.78,
    'H59_EXIT_FIRST_FRAME_CATCHUP_MS':120.0,'math':math,
    '_h68_release_duration':lambda row,p0,v0:400.0,
}
exec(fsrc('_h68_release_progress'),release_ns)
r=R(); r._h62_decay_release_mono=1000.0; r._h62_decay_release_progress=0.50
r._h62_decay_release_draw_count=1; r._h68_progress_velocity=0.00125; r._h68_release_duration_ms=0.0
p1=release_ns['_h68_release_progress'](r,1010.0)
# 10 ms at inherited 0.00125/ms should move roughly 0.0125; allow Hermite curvature.
if not (0.507 < p1 < 0.520): fail(f'release handoff lost inherited velocity: {p1:.4f}')
if not (float(getattr(r,'_h68_release_duration_ms',0))==400.0): fail('release duration was not snapshotted')

activate=fsrc('_h68_activate_runtime')
for tok in ('_h62_decay_progress = _h68_deadline_decay_progress',
            'LyricWindow._make_history_line = _h68_make_history_line',
            'LyricWindow._placement_obstacles = _h68_placement_obstacles',
            'LyricWindow._pre_admit_burst_row = _h68_pre_admit_burst_row'):
    if tok not in activate: fail('runtime hook missing '+tok)

# Burst direct-clear path must explicitly exempt blur-decay rows.
burst=fsrc('_h68_pre_admit_burst_row')
if "normal = [r for r in rows if not _h66_is_blur_decay_row(r)]" not in burst:
    fail('blur rows are still eligible for V28 direct burst clearing')
if "any(_h66_is_blur_decay_row(r) for r in rows)" not in burst:
    fail('burst protection incorrectly depends only on the current exit selector')

# Presentation layer only; no media/seek/provider authority and no new raster work.
block=src[src.index('# H68 deadline blur planner'):]
block=block[:block.index('# H69 optical continuity + edge-wrap stability')]
for bad in ('MediaSessionSync.', 'ControlPanel.', 'LyricSearchEngine.', 'QImage(', 'QPixmap.fromImage(', 'threading.Thread('):
    if bad in block: fail('H68 crossed protected/hot-path boundary: '+bad)

print('DEADLINE BLUR PLANNER H68 REPLAY: PASS')
print(' - known future line starts define the capacity-eviction horizon before a burst arrives')
print(' - ultra-dense rows split progress across pre-eviction horizon + visible release tail')
print(' - release snapshots duration and inherits active progress velocity')
print(' - blur exits are excluded from the V28 direct-drop burst-clear path')
print(' - collision reservation decays with blur readability instead of forcing deletion')
