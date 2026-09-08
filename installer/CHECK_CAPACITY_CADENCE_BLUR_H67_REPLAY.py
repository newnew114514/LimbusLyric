from pathlib import Path
import ast, sys, textwrap, time, math, weakref

if len(sys.argv) < 2:
    raise SystemExit('usage: CHECK_CAPACITY_CADENCE_BLUR_H67_REPLAY.py <main.py>')
path=Path(sys.argv[1]); src=path.read_text(encoding='utf-8'); tree=ast.parse(src); lines=src.splitlines()

def fail(msg): raise SystemExit('H67 FAIL: '+msg)
def need(tok, why):
    if tok not in src: fail(f'{why}: missing {tok!r}')
def fn(name):
    for node in ast.walk(tree):
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name==name:
            return node
    fail('function not found: '+name)
def fsrc(name):
    n=fn(name); return textwrap.dedent('\n'.join(lines[n.lineno-1:n.end_lineno]))

need('+ CAPACITY CADENCE BLUR H67','build tag')
need("if '_h67_activate_runtime' in globals():",'final activation')
if not (src.rindex("if '_h66_activate_runtime' in globals():") < src.rindex("if '_h67_activate_runtime' in globals():")):
    fail('H67 must activate after H66')

for name in ('_h67_window_cadence_ms','_h67_history_slots_to_evict','_h67_desired_capacity_speed',
             '_h67_capacity_release_duration','_h67_capacity_cadence_decay_progress'):
    fn(name)

# Resident-rank math: at full capacity the oldest leaves next; newest survives capacity-1 births.
class Row: pass
class Win: pass
slots_ns={}
exec(fsrc('_h67_history_slots_to_evict'),slots_ns)
slots=slots_ns['_h67_history_slots_to_evict']
w3=Win(); rows3=[Row(),Row()]; w3.history_lines=rows3
if slots(w3,rows3[0],3)!=1 or slots(w3,rows3[1],3)!=2:
    fail('capacity=3 resident-rank eviction forecast is wrong')
w6=Win(); rows6=[Row() for _ in range(5)]; w6.history_lines=rows6
if slots(w6,rows6[0],6)!=1 or slots(w6,rows6[-1],6)!=5:
    fail('capacity=6 resident-rank eviction forecast is wrong')
w6u=Win(); w6u.history_lines=[Row(),Row()]
if slots(w6u,w6u.history_lines[0],6)!=4 or slots(w6u,w6u.history_lines[1],6)!=5:
    fail('under-filled capacity forecast does not preserve empty slots')

# Same cadence + same starting blur: smaller configured capacity must request a faster future slope.
speed_ns={
    'H67_CADENCE_MIN_MS':420.0,'H67_CADENCE_MAX_MS':6200.0,
    'H67_ACTIVE_SOFT_LIMIT':0.938,'H67_EVICT_TARGET_PROGRESS':0.875,
    'H67_SPEED_MIN':0.10,'H67_SPEED_MAX':3.80,'H66_BLUR_FADE_START':0.94,
}
exec(fsrc('_h67_desired_capacity_speed'),speed_ns)
desired=speed_ns['_h67_desired_capacity_speed']
s3=desired(Row(),0.20,10000.0,2000.0,2)
s6=desired(Row(),0.20,10000.0,2000.0,5)
if not (s3 > s6 * 2.0):
    fail(f'configured capacity is still effectively lost at saturation: cap3={s3:.3f}, cap6={s6:.3f}')

# Above target there is still positive motion, but the active lane cannot cross into H66 opacity tail.
late=desired(Row(),0.90,10000.0,2000.0,1)
if not (late > 0.0): fail('post-target blur hard-parks instead of continuing')
if not (float(speed_ns['H67_ACTIVE_SOFT_LIMIT']) < float(speed_ns['H66_BLUR_FADE_START'])):
    fail('active soft limit crossed opacity-fade start')

# Full synthetic progress replay: identical elapsed time produces visibly faster progress at cap=3.
class R:
    pass
class W:
    pass

def raw(row,now_mono=None): return float(getattr(row,'seed',0.20))
def state(row):
    win=row._h62_owner_ref(); cap=int(win.max_visible_subtitles); current=bool(win.full_text)
    return win,cap,(1 if current else 0)+len(win.history_lines),current

def reset(row):
    row._h65_capacity_active=False; row._h65_capacity_last_mono=0.0

def rebase(row,now,progress,reason='idle'):
    row._h65_capacity_active=False; row._h65_capacity_progress=float(progress); return float(progress)

ns={
    'time':time,'math':math,'H62_EXIT_EFFECT_BLUR_DECAY':'blur_decay',
    'H67_CADENCE_MIN_MS':420.0,'H67_CADENCE_MAX_MS':6200.0,'H67_DEFAULT_CADENCE_MS':1900.0,
    'H67_ACTIVE_SOFT_LIMIT':0.938,'H67_EVICT_TARGET_PROGRESS':0.875,'H67_SPEED_MIN':0.10,
    'H67_SPEED_MAX':3.80,'H67_SPEED_RESPONSE_MS':420.0,'H66_BLUR_FADE_START':0.94,
    'H59_EXIT_FIRST_FRAME_CATCHUP_MS':120.0,'write_error_log':lambda *a,**k:None,
    '_h67_h66_progress_pre':raw,'_h65_raw_h62_decay_progress':raw,'_h64_blur_residency_state':state,
    '_h65_reset_capacity_integrator':reset,'_h65_rebase_raw_hold_clock':rebase,
}
ns['_h62_decay_durations']=lambda row:(10000.0,3200.0)
ns['_h66_is_blur_decay_row']=lambda row: str(getattr(row,'exit_effect',''))=='blur_decay'
exec(fsrc('_h67_local_timeline_cadence'),ns)
exec(fsrc('_h67_window_cadence_ms'),ns)
exec(fsrc('_h67_history_slots_to_evict'),ns)
exec(fsrc('_h67_desired_capacity_speed'),ns)
# Release helpers are not hit in this active replay.
ns['_h67_release_progress']=lambda row,now: 1.0
exec(fsrc('_h67_reset_capacity_controller'),ns)
exec(fsrc('_h67_capacity_cadence_decay_progress'),ns)
progress=ns['_h67_capacity_cadence_decay_progress']

def make(cap):
    w=W(); w.max_visible_subtitles=cap; w.full_text='current'; w._h67_line_cadence_ema_ms=2000.0
    hist=[R() for _ in range(cap-1)]
    for rr in hist:
        rr.exit_effect='blur_decay'; rr.seed=0.20; rr._h62_decay_release_mono=0.0
        rr._h65_capacity_active=True; rr._h65_capacity_progress=0.20; rr._h65_capacity_last_mono=1000.0
        rr._h67_capacity_speed_smoothed=0.0; rr._h62_owner_ref=weakref.ref(w)
    w.history_lines=hist
    return w,hist[-1]
w3,r3=make(3); w6,r6=make(6)
p3=progress(r3,2000.0); p6=progress(r6,2000.0)
if not (p3 > p6 + 0.08): fail(f'capacity-aware progress slope not materially different: {p3:.4f} vs {p6:.4f}')
if not (p3 < 0.938 and p6 < 0.938): fail('managed rows crossed active soft limit')
p3_late=progress(r3,62000.0)
if not (p3_late > p3 and p3_late < 0.938):
    fail(f'long active residency either hard-stopped or self-retired: {p3:.4f}->{p3_late:.4f}')

# Capacity=1 has no resident history lane, so a clear row must not take the old multi-second full tail.
release_ns={
    'H67_CAPACITY_ONE_TAIL_MIN_MS':520.0,'H67_CAPACITY_ONE_TAIL_MAX_MS':1350.0,
    'H67_CAPACITY_ONE_TAIL_RATIO':0.68,'H67_EARLY_RELEASE_TAIL_MAX_MS':1650.0,
    'H67_EARLY_RELEASE_TAIL_RATIO':0.78,'H67_EVICT_TARGET_PROGRESS':0.875,
    'H66_PRESSURE_MIN_TAIL_MS':360.0,'H66_RELEASE_MIN_TAIL_MS':520.0,
    '_h66_release_duration':lambda row,p0,factor=1.0:3200.0,
    '_h67_window_cadence_ms':lambda win:1800.0,
}
exec(fsrc('_h67_capacity_release_duration'),release_ns)
w1=W(); w1.max_visible_subtitles=1
r1=R(); r1._h62_owner_ref=weakref.ref(w1)
d1=release_ns['_h67_capacity_release_duration'](r1,0.0,1.0)
if not (900.0 < d1 < 1350.0): fail(f'capacity=1 tail was not cadence-scaled: {d1:.1f}ms')

activate=fsrc('_h67_activate_runtime')
for tok in ('_h62_decay_progress = _h67_capacity_cadence_decay_progress',
            'LyricWindow._make_history_line = _h67_make_history_line'):
    if tok not in activate: fail('runtime hook missing '+tok)

# Presentation layer only: no media/provider ownership and no paint-time raster/filter work.
block=src[src.index('# H67 capacity-cadence blur governor'):]
block=block[:block.index('# H69 optical continuity + edge-wrap stability')]
for bad in ('MediaSessionSync.', 'ControlPanel.', 'LyricSearchEngine.', 'QImage(', 'QPixmap.fromImage(', 'threading.Thread('):
    if bad in block: fail('H67 crossed protected/hot-path boundary: '+bad)

print('CAPACITY CADENCE BLUR H67 REPLAY: PASS')
print(' - capacity 3 and capacity 6 no longer collapse to the same speed at full occupancy')
print(' - resident rank predicts births-to-eviction, including under-filled stacks')
print(' - real completed-line cadence scales future blur slope without progress jumps')
print(' - active history approaches a pre-opacity soft limit; capacity overflow owns retirement')
print(' - capacity=1 release tail is cadence-scaled instead of replaying a multi-second full tail')
