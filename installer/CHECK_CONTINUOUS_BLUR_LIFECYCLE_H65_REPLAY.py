from pathlib import Path
import ast, sys, textwrap, time, weakref

if len(sys.argv) < 2:
    raise SystemExit('usage: CHECK_CONTINUOUS_BLUR_LIFECYCLE_H65_REPLAY.py <main.py>')
path=Path(sys.argv[1]); src=path.read_text(encoding='utf-8'); tree=ast.parse(src); lines=src.splitlines()

def fail(msg): raise SystemExit('H65 FAIL: '+msg)
def need(tok, why):
    if tok not in src: fail(f'{why}: missing {tok!r}')
def fn(name):
    for node in ast.walk(tree):
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name==name:
            return node
    fail('function not found: '+name)
def fsrc(name):
    n=fn(name); return textwrap.dedent('\n'.join(lines[n.lineno-1:n.end_lineno]))

need('+ CONTINUOUS BLUR LIFECYCLE H65','build tag')
need("if '_h65_activate_runtime' in globals():",'final activation')
if not (src.rindex("if '_h64_activate_runtime' in globals():") < src.rindex("if '_h65_activate_runtime' in globals():")):
    fail('H65 must activate after H64')

progress_src=fsrc('_h65_continuous_capacity_decay_progress')
for tok in (
    '_h65_capacity_progress',
    '_h65_capacity_last_mono',
    'elapsed / max(1.0, float(hold_ms))',
    '_h65_rebase_raw_hold_clock',
    "reason = 'provider-idle' if not current_present else 'capacity-one'",
    '_h65_raw_h62_decay_progress(row, now)',
):
    if tok not in progress_src: fail('continuous integrator missing '+tok)

rebase_src=fsrc('_h65_rebase_raw_hold_clock')
for tok in ('row._h62_decay_hold_mono = now - p *', 'hidden-age-payback=0', 'release-authority=unchanged'):
    if tok not in rebase_src: fail('idle rebase missing '+tok)

# Synthetic continuity replay. H64's old age*speed formula jumps when fill changes; H65 must not.
class Row: pass
class Win: pass
r=Row(); r.exit_effect='blur_decay'; r._h62_decay_release_mono=0.0; r._h62_decay_hold_mono=1000.0
w=Win(); w.max_visible_subtitles=6; w.full_text='current lyric'; w.history_lines=[r]
r._h62_owner_ref=weakref.ref(w)

ns={
    'time':time,
    'H62_EXIT_EFFECT_BLUR_DECAY':'blur_decay',
    'H64_BLUR_FILL_SPEED_MIN':0.34,
    'H64_BLUR_ACTIVE_PARK_PROGRESS':0.88,
    'write_error_log':lambda *a,**k:None,
}
ns['_h62_decay_durations']=lambda row:(10000.0,2000.0)
def raw(row,now_mono=None):
    now=float(now_mono); start=float(getattr(row,'_h62_decay_hold_mono',now) or now)
    return min(1.0,max(0.0,(now-start)/10000.0))
def state(row):
    win=row._h62_owner_ref(); cap=max(1,min(6,int(win.max_visible_subtitles)))
    current=bool(str(win.full_text or '').strip()); live=(1 if current else 0)+len(win.history_lines)
    return win,cap,live,current
def h64_seed(row,now_mono=None):
    win,cap,live,current=state(row)
    if cap<=1 or not current: return raw(row,now_mono)
    fill=float(live)/float(cap); speed=0.34+(1.0-0.34)*fill
    return min(0.88,raw(row,now_mono)*speed)
ns['_h64_blur_residency_state']=state
ns['_h65_h64_decay_progress_pre']=h64_seed
ns['_h65_raw_h62_decay_progress']=raw
exec(fsrc('_h65_reset_capacity_integrator'),ns)
exec(rebase_src,ns)
exec(progress_src,ns)
progress=ns['_h65_continuous_capacity_decay_progress']

p1=progress(r,5000.0)  # 2/6 live fill
w.history_lines=[r,object(),object(),object()]  # 5/6 live fill
p2=progress(r,5100.0)
if not (p2 >= p1 and (p2-p1) < 0.03):
    fail(f'fill increase caused a whole-age jump: {p1:.4f}->{p2:.4f}')
w.history_lines=[r]
p3=progress(r,5200.0)
if not (p3 >= p2 and (p3-p2) < 0.03):
    fail(f'fill decrease reversed/jumped progress: {p2:.4f}->{p3:.4f}')

# Provider idle at the same optical instant must continue from p3, not expose raw hidden age.
w.full_text=''
p_idle=progress(r,5200.0)
if abs(p_idle-p3) > 0.002:
    fail(f'idle transition was discontinuous: active={p3:.4f} idle={p_idle:.4f}')
if p_idle >= 0.999:
    fail('idle transition still paid back hidden age to invisible')
# Raw H62 remains authoritative after the rebase and eventually completes naturally.
p_later=progress(r,5200.0+(1.0-p_idle)*10000.0+5.0)
if p_later < 0.999:
    fail(f'idle natural retirement no longer completes: {p_later:.4f}')

# Capacity-one disengage has the same no-jump contract.
r2=Row(); r2.exit_effect='blur_decay'; r2._h62_decay_release_mono=0.0; r2._h62_decay_hold_mono=1000.0
w2=Win(); w2.max_visible_subtitles=6; w2.full_text='current'; w2.history_lines=[r2]; r2._h62_owner_ref=weakref.ref(w2)
p21=progress(r2,5000.0); w2.max_visible_subtitles=1; p22=progress(r2,5000.0)
if abs(p22-p21)>0.002: fail(f'capacity-one transition jumped: {p21:.4f}->{p22:.4f}')

# Explicit release remains on raw H62/H63 timing and is not integrated/parked by H65.
r3=Row(); r3.exit_effect='blur_decay'; r3._h62_decay_hold_mono=1000.0; r3._h62_decay_release_mono=4500.0
w3=Win(); w3.max_visible_subtitles=6; w3.full_text='current'; w3.history_lines=[r3]; r3._h62_owner_ref=weakref.ref(w3)
p_release=progress(r3,9000.0)
if p_release < 0.79: fail(f'release phase was unexpectedly stretched: {p_release:.4f}')

# Optical curve: max blur must be fully reached before any opacity loss.
curve_ns={
    'H65_BLUR_REACH_MAX_AT':0.82,
    'H65_BLUR_FADE_START':0.90,
    'H65_BLUR_CROSSFADE_GAIN':0.30,
}
exec(fsrc('_h65_smootherstep'),curve_ns); exec(fsrc('_h65_decay_mix'),curve_ns)
mix=curve_ns['_h65_decay_mix']
b,m,x,v=mix(0.0)
if not (b>0.999 and m<0.001 and x<0.001 and v>0.999): fail('p=0 not sharp/visible')
b,m,x,v=mix(0.82)
if not (x>0.999 and v>0.999): fail(f'max blur not complete before fade: max={x:.4f} vis={v:.4f}')
b,m,x,v=mix(0.88)
if not (x>0.999 and v>0.999): fail(f'parked active row should hold max blur fully visible: max={x:.4f} vis={v:.4f}')
b,m,x,v=mix(0.95)
if not (x>0.999 and 0.05<v<0.95): fail(f'final tail does not hold max blur while fading: max={x:.4f} vis={v:.4f}')
b,m,x,v=mix(1.0)
if not (x>0.999 and v<0.001): fail('p=1 not max-blur/invisible')
# Midpoint compensation should reduce SourceOver brightness pumping without adding raster stages.
b,m,x,v=mix(0.29)
if not ((b+m+x) > 1.15 and max(b,m,x) <= 1.0): fail(f'crossfade compensation missing: {b,m,x}')

activate=fsrc('_h65_activate_runtime')
for tok in ('_h62_decay_progress = _h65_continuous_capacity_decay_progress', '_h62_decay_mix = _h65_decay_mix', "'_limbus_layer'", 'cached-atlas-only-no-paint-raster'):
    if tok not in activate: fail('runtime hook missing '+tok)

# Presentation-only boundary: do not mutate media/provider/capacity ownership from H65.
block=src[src.index('# H65 continuous blur lifecycle + perceptual exit curve'):]
block=block[:block.index('# H69 optical continuity + edge-wrap stability')]
for bad in ('MediaSessionSync.', 'ControlPanel.', 'LyricSearchEngine.', 'LyricWindow._release_history_lines =', 'FadingLine.begin_fade =', '_enforce_visual_stack_limit ='):
    if bad in block: fail('H65 crossed protected ownership boundary: '+bad)
for bad in ('_h56_lowpass_image(', 'QImage(', 'QPixmap.fromImage(', 'threading.Thread('):
    if bad in fsrc('_h65_decay_mix')+progress_src: fail('H65 added raster/worker work to hot optical path: '+bad)

print('CONTINUOUS BLUR LIFECYCLE H65 REPLAY: PASS')
print(' - stack-fill changes alter future blur slope without progress jumps or reversals')
print(' - idle/capacity-one transition rebases raw H62 age to the visible optical state')
print(' - max cached defocus is reached before opacity decay and held through the final fade tail')
print(' - no media/provider/capacity-release ownership or paint-time raster work is introduced')
