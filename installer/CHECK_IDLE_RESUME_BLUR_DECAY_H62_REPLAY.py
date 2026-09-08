from pathlib import Path
import ast, sys, time

if len(sys.argv) < 2:
    raise SystemExit('usage: CHECK_IDLE_RESUME_BLUR_DECAY_H62_REPLAY.py <main.py>')
path=Path(sys.argv[1]); src=path.read_text(encoding='utf-8'); tree=ast.parse(src); lines=src.splitlines()

def fail(msg): raise SystemExit('H62 FAIL: '+msg)
def need(tok, why):
    if tok not in src: fail(f'{why}: missing {tok!r}')
def fn(name):
    for node in ast.walk(tree):
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name==name: return node
    fail('function not found: '+name)
def fsrc(name):
    n=fn(name); return '\n'.join(lines[n.lineno-1:n.end_lineno])

need('+ IDLE RESUME CONTINUITY + BLUR DECAY EXIT H62','build tag')
need("if '_h62_activate_runtime' in globals():",'final activation')
if not (src.rindex("if '_h61_activate_runtime' in globals():") < src.rindex("if '_h62_activate_runtime' in globals():")):
    fail('H62 must activate after H61')

# Field replay contract: suppressed current row -> next normal lyric must preserve held/fading rows.
for tok in (
    "_h62_idle_resume_from = int(getattr(self, '_provider_idle_suppressed_line', -1))",
    '_h62_idle_resume_from >= 0',
    'target == _h62_idle_resume_from + 1',
    "write_error_log('H62空白段恢复保留驻留字幕'",
    'resume=preserve-then-capacity-release',
): need(tok,'idle-resume ownership')
resume_pos=src.index('_h62_idle_resume = bool(')
clear_pos=src.index('self.fading_lines = []', resume_pos)
branch=src[resume_pos:clear_pos]
if 'self.history_lines = []' in branch or 'self.fading_lines = []' in branch:
    fail('idle-resume preserve branch still clears visual residents')
# Ordinary first-locate/reload clearing remains after the H62 exception.
reload_slice=src[clear_pos:clear_pos+260]
if 'self.history_lines = []' not in reload_slice:
    fail('ordinary reload history clear was accidentally removed')

# New effect and UI persistence.
for tok in (
    "H62_EXIT_EFFECT_BLUR_DECAY = 'blur_decay'",
    "combo.insertItem(insert_at, '渐进失焦 / 模糊退场', H62_EXIT_EFFECT_BLUR_DECAY)",
    "saved == H62_EXIT_EFFECT_BLUR_DECAY",
    "panel.lyric_window.exit_effect = H62_EXIT_EFFECT_BLUR_DECAY",
): need(tok,'blur-decay UI/persistence')

# Optical source is H57's final immutable birth material; no depth replacement.
source=fsrc('_h62_final_source_shared')
for tok in ("'_h57_depth_composite_cache'", "cached.get('shared')", "'_shared_fragment_atlas'"):
    if tok not in source: fail('birth/depth material source missing '+tok)
for bad in ('_h54_assign_depth', '_h54_depth_level =', 'random.randint'):
    if bad in source: fail('H62 must not reassign fixed depth: '+bad)

draw=fsrc('h62_draw')
for bad in ('_h56_lowpass_image(', '_h62_filter_shared_image(', '_h57_build_composite_shared('):
    if bad in draw: fail('paint-time blur/composite raster work found: '+bad)
for tok in ('_h62_final_source_shared(row)', '_h62_queue_decay_build(row)', '_h62_decay_mix(p)', '_h57_draw_row_with_active_order'):
    if tok not in draw and tok != '_h57_draw_row_with_active_order':
        fail('draw continuity path missing '+tok)
# _h57 draw helper is used by the nested pass function, not directly h62_draw.
if '_h57_draw_row_with_active_order' not in fsrc('_h62_activate_runtime'):
    fail('active/history transform continuity helper is not used')

worker=fsrc('_h62_schedule_decay_atlases')
for tok in (
    "threading.Thread(target=worker, name='LimbusLyric-H62BlurDecay', daemon=True).start()",
    '_h62_filter_shared_image(',
    "'h62_blur_decay': True",
    'window.song_fragment_atlas_ready.emit(payload)',
    'H62_BLUR_WORKER_BUDGET_MS',
):
    if tok not in worker: fail('async blur worker missing '+tok)
if 'QPixmap.fromImage' in worker:
    fail('worker must not create QPixmap')
install=fsrc('h62_install')
for tok in ("payload.get('h62_blur_decay')", 'QPixmap.fromImage(image)', '_h62_decay_mid_shared', '_h62_decay_max_shared', 'gui_filter=0'):
    if tok not in install: fail('GUI blur install missing '+tok)

# H59 first-visible-frame contract extends to H62's own release clock.
progress_src=fsrc('_h62_decay_progress')
for tok in ('_h62_decay_release_draw_count', "H59_EXIT_FIRST_FRAME_CATCHUP_MS", 'elapsed = min('):
    if tok not in progress_src: fail('release first-frame catch-up missing '+tok)
activate=fsrc('_h62_activate_runtime')
for tok in (
    'row._h62_decay_release_draw_count = 0',
    "previous != H62_EXIT_EFFECT_BLUR_DECAY",
    'row._h62_decay_hold_mono = now',
    'row._h62_decay_release_mono = 0.0',
    "FadingLine.draw._limbus_policy = 'birth-depth-material-plus-async-residence-lowpass-no-paint-raster'",
):
    if tok not in activate: fail('runtime continuity/switch reset missing '+tok)

# Pure optical curve replay.
mix_src=fsrc('_h62_smoothstep')+'\n'+fsrc('_h62_decay_mix')
ns={'H62_BLUR_FADE_START':0.58}
exec(mix_src,ns)
mix=ns['_h62_decay_mix']
def approx(a,b,eps=1e-6): return abs(float(a)-float(b)) <= eps
b,m,x,v=mix(0.0)
if not (approx(b,1) and approx(m,0) and approx(x,0) and approx(v,1)): fail('p=0 is not sharp/visible')
b,m,x,v=mix(0.5)
if not (m > 0.999 and b < 0.001 and x < 0.001 and approx(v,1)): fail('p=0.5 is not medium-defocus dominant')
b,m,x,v=mix(1.0)
if not (x > 0.999 and b < 0.001 and m < 0.001 and v < 0.001): fail('p=1 is not max-defocus/invisible')

# Pure release-stall replay: before one release draw, a multi-second GUI stall is capped;
# after one visible release frame, the same elapsed time may complete normally.
smooth=ns['_h62_smoothstep']
progress_code=fsrc('_h62_decay_progress')
ns2={
    'time':time,
    '_h62_decay_durations':lambda row:(10000.0,2000.0),
    '_h62_smoothstep':smooth,
    'H59_EXIT_FIRST_FRAME_CATCHUP_MS':120.0,
}
exec(progress_code,ns2)
progress=ns2['_h62_decay_progress']
class R: pass
r=R(); r._h62_decay_release_mono=1000.0; r._h62_decay_release_progress=0.0; r._h62_decay_release_draw_count=0; r._h62_decay_hold_mono=1.0
p_capped=progress(r,6000.0)
if not (0.0 < p_capped < 0.10): fail(f'pre-first-release-frame catchup not capped: {p_capped}')
r._h62_decay_release_draw_count=1
p_after=progress(r,6000.0)
if p_after < 0.999: fail(f'post-visible-release progression did not complete normally: {p_after}')

# Presentation boundary: only the narrow check_lyric_time source edit may touch timeline state.
h62_start=src.index('# H62 idle-resume continuity + progressive blur-decay exit')
h62_end=src.index('# H63 blur-decay release + KuGou same-track restart display closure', h62_start)
h62_block=src[h62_start:h62_end]
for bad in ('MediaSessionSync.', 'requests.', 'urllib.', 'win32com', '_auto_fetch_in_progress'):
    if bad in h62_block: fail('H62 presentation block crossed protected boundary: '+bad)

print('IDLE RESUME + BLUR DECAY H62 REPLAY: PASS')
print(' - provider-idle held history survives the first lyric after an instrumental gap')
print(' - progressive blur exit low-passes H57 birth-depth/style material asynchronously, never in paint')
print(' - fixed Z depth and residence-age defocus stack instead of overriding each other')
print(' - H62 release clock preserves a first visible frame and mid-session selection restarts age cleanly')
