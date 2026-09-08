from pathlib import Path
import ast, sys, textwrap, time, weakref

if len(sys.argv) < 2:
    raise SystemExit('usage: CHECK_UNINTERRUPTED_BLUR_EXIT_H66_REPLAY.py <main.py>')
path=Path(sys.argv[1]); src=path.read_text(encoding='utf-8'); tree=ast.parse(src); lines=src.splitlines()

def fail(msg): raise SystemExit('H66 FAIL: '+msg)
def need(tok, why):
    if tok not in src: fail(f'{why}: missing {tok!r}')
def fn(name):
    for node in ast.walk(tree):
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name==name:
            return node
    fail('function not found: '+name)
def fsrc(name):
    n=fn(name); return textwrap.dedent('\n'.join(lines[n.lineno-1:n.end_lineno]))

need('+ UNINTERRUPTED BLUR EXIT H66','build tag')
need("if '_h66_activate_runtime' in globals():",'final activation')
if not (src.rindex("if '_h65_activate_runtime' in globals():") < src.rindex("if '_h66_activate_runtime' in globals():")):
    fail('H66 must activate after H65')

progress_src=fsrc('_h66_uninterrupted_decay_progress')
for tok in ('p = min(1.0, p)', '_h66_release_progress(row, now)', '_h65_rebase_raw_hold_clock',
            'capacity-integrated-to-natural-retirement'):
    if tok not in progress_src and tok not in fsrc('_h66_activate_runtime'):
        fail('uninterrupted lifecycle missing '+tok)
if 'H64_BLUR_ACTIVE_PARK_PROGRESS' in progress_src:
    fail('H66 still parks active progress at H64 0.88')

# Synthetic capacity replay: an already-old held row must progress through 0.88 instead of parking.
class Row: pass
class Win: pass
r=Row(); r.exit_effect='blur_decay'; r._h62_decay_release_mono=0.0; r._h62_decay_hold_mono=1000.0
r._h65_capacity_active=True; r._h65_capacity_progress=0.875; r._h65_capacity_last_mono=5000.0
w=Win(); w.max_visible_subtitles=6; w.full_text='current'; w.history_lines=[r,object(),object(),object(),object()]
r._h62_owner_ref=weakref.ref(w)

ns={
    'time':time, 'H62_EXIT_EFFECT_BLUR_DECAY':'blur_decay', 'H64_BLUR_FILL_SPEED_MIN':0.34,
    'H59_EXIT_FIRST_FRAME_CATCHUP_MS':120.0, 'H66_RELEASE_MIN_TAIL_MS':520.0,
    'H66_PRESSURE_MIN_TAIL_MS':360.0, 'write_error_log':lambda *a,**k:None,
}
ns['_h62_decay_durations']=lambda row:(10000.0,4200.0)
def raw(row,now_mono=None):
    now=float(now_mono); start=float(getattr(row,'_h62_decay_hold_mono',now) or now)
    return min(1.0,max(0.0,(now-start)/10000.0))
def state(row):
    win=row._h62_owner_ref(); cap=max(1,min(6,int(win.max_visible_subtitles)))
    current=bool(str(win.full_text or '').strip()); live=(1 if current else 0)+len(win.history_lines)
    return win,cap,live,current
ns['_h64_blur_residency_state']=state
ns['_h65_raw_h62_decay_progress']=raw
ns['_h66_h65_progress_pre']=raw

def reset(row):
    row._h65_capacity_active=False; row._h65_capacity_last_mono=0.0
ns['_h65_reset_capacity_integrator']=reset
def rebase(row,now,progress,reason='idle'):
    row._h62_decay_hold_mono=float(now)-float(progress)*10000.0
    row._h65_capacity_active=False; row._h65_capacity_progress=float(progress); return float(progress)
ns['_h65_rebase_raw_hold_clock']=rebase
exec(fsrc('_h66_is_blur_decay_row'),ns)
exec(fsrc('_h66_release_duration'),ns)
exec(fsrc('_h66_release_progress'),ns)
exec(progress_src,ns)
progress=ns['_h66_uninterrupted_decay_progress']
p1=progress(r,5500.0)
if not (0.91 < p1 < 0.94): fail(f'active row did not continue beyond old 0.88 park: {p1:.4f}')
p2=progress(r,6300.0)
if not (p2 > p1): fail(f'active blur stopped/reversed: {p1:.4f}->{p2:.4f}')
p3=progress(r,7000.0)
if p3 < 0.999: fail(f'capacity age no longer reaches natural retirement: {p3:.4f}')

# Release scaling: 12% remaining must not restart a multi-second full release.
r2=Row(); r2.exit_effect='blur_decay'; r2._h62_decay_release_mono=10000.0; r2._h62_decay_release_progress=0.88
r2._h62_decay_release_draw_count=1; r2._h66_pressure_release_factor=1.0
q1=ns['_h66_release_progress'](r2,10260.0)
q2=ns['_h66_release_progress'](r2,10530.0)
if q1 < 0.93: fail(f'high-progress release still crawls: p@260ms={q1:.4f}')
if q2 < 0.999: fail(f'remaining-distance release did not complete promptly: {q2:.4f}')

# Optical curve must keep increasing blur after the old H65 0.82 maximum and keep it visible late.
curve_ns={'H66_BLUR_FADE_START':0.94,'H66_BLUR_OPTICAL_POWER':1.12,'H66_BLUR_CROSSFADE_GAIN':0.24}
exec(fsrc('_h65_smootherstep'),curve_ns)
exec(fsrc('_h66_decay_mix'),curve_ns)
mix=curve_ns['_h66_decay_mix']
b,m,x82,v82=mix(0.82); b,m,x94,v94=mix(0.94); b,m,x97,v97=mix(0.97); b,m,x1,v1=mix(1.0)
if x82 >= 0.995: fail('blur still reaches a hard maximum at the old 0.82 shelf')
if not (x94 > x82 and x97 > x94): fail(f'blur does not keep increasing late: {x82:.4f},{x94:.4f},{x97:.4f}')
if v94 < 0.999: fail(f'opacity starts too early: {v94:.4f}')
if v97 < 0.80: fail(f'late blur is hidden by opacity too early: {v97:.4f}')
if not (x1 > 0.999 and v1 < 0.001): fail('p=1 must be max-blur/invisible')

# Pressure valve: blur rows may be accelerated but never discarded by budget pressure.
class DummyRow:
    def __init__(self,effect='blur_decay',alpha=255): self.exit_effect=effect; self.alpha=alpha; self.discarded=False
    def release_render_resources(self): self.discarded=True
    def expedite_fade(self): pass
class DummyWin:
    def __init__(self):
        self.max_visible_subtitles=6; self.history_lines=[object()]*5; self.fading_lines=[]; self._last_fade_budget_log_mono=0; self._h66_last_pressure_log_mono=0
    def _render_pressure_level(self): return 2
    def _effective_fade_exit_budget(self): return 0
    def _discard_fading_item(self,item): item.discarded=True
w2=DummyWin(); a=DummyRow(); b=DummyRow(); n=DummyRow('fade'); w2.fading_lines=[a,b,n]
pressure_ns={
    'time':time,'H62_EXIT_EFFECT_BLUR_DECAY':'blur_decay','FADE_VISUAL_ALPHA_CUTOFF':20,
    'NETEASE_FADE_EXIT_EMERGENCY_MAX':12,'H66_PRESSURE_RELEASE_FACTOR_SOFT':0.76,
    'H66_PRESSURE_RELEASE_FACTOR_HIGH':0.56,'H66_PRESSURE_RELEASE_FACTOR_SEVERE':0.40,
    'write_error_log':lambda *a,**k:None,'_h66_fade_limit_pre':None,
}
exec(fsrc('_h66_is_blur_decay_row'),pressure_ns); exec(fsrc('_h66_pressure_factor'),pressure_ns); exec(fsrc('_h66_enforce_fade_exit_limit'),pressure_ns)
dropped=pressure_ns['_h66_enforce_fade_exit_limit'](w2)
if a.discarded or b.discarded: fail('render-pressure valve still directly drops blur-decay rows')
if not n.discarded or dropped != 1: fail('legacy non-blur pressure valve semantics were not retained')
if not (getattr(a,'_h66_pressure_release_factor',1.0)<1.0 and getattr(b,'_h66_pressure_release_factor',1.0)<1.0):
    fail('pressure did not accelerate protected blur rows')

activate=fsrc('_h66_activate_runtime')
for tok in ('_h62_decay_progress = _h66_uninterrupted_decay_progress','_h62_decay_mix = _h66_decay_mix',
            'LyricWindow._enforce_fade_exit_limit = _h66_enforce_fade_exit_limit'):
    if tok not in activate: fail('runtime hook missing '+tok)

# No media/provider ownership changes and no paint-time raster/filter work in H66.
block=src[src.index('# H66 uninterrupted blur exit'):]
block=block[:block.index('# H69 optical continuity + edge-wrap stability')]
for bad in ('MediaSessionSync.', 'ControlPanel.', 'LyricSearchEngine.', 'QImage(', 'QPixmap.fromImage(', 'threading.Thread('):
    if bad in block: fail('H66 crossed protected/hot-path boundary: '+bad)

print('UNINTERRUPTED BLUR EXIT H66 REPLAY: PASS')
print(' - capacity-managed blur progresses through the old 0.88 shelf to natural retirement')
print(' - release time scales with remaining progress, eliminating the second slow shelf')
print(' - blur continues increasing through the late visible tail before disappearance')
print(' - render pressure accelerates blur exits instead of deleting them mid-animation')
