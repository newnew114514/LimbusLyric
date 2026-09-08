from pathlib import Path
import ast, sys

if len(sys.argv) < 2:
    raise SystemExit('usage: CHECK_DEPTH_CONTINUITY_COMPOSITE_H57_REPLAY.py <main.py>')
path = Path(sys.argv[1])
src = path.read_text(encoding='utf-8')
tree = ast.parse(src)
lines = src.splitlines()

def fail(msg):
    raise SystemExit('H57 FAIL: ' + msg)

def need(token, reason):
    if token not in src:
        fail(f'{reason}: missing {token!r}')

def fn(name):
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node
    fail('function not found: ' + name)

def fn_src(name):
    node = fn(name)
    return '\n'.join(lines[node.lineno-1:node.end_lineno])

def top_fn(name):
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    fail('top-level function not found: ' + name)

need('+ DEPTH CONTINUITY COMPOSITE H57', 'build tag')
need("if '_h57_activate_runtime' in globals():", 'final activation')
if src.index("if '_h57_activate_runtime' in globals():") < src.index("if '_h56_activate_runtime' in globals():"):
    fail('H57 must activate after H56')

act = fn_src('_h57_activate_runtime')
for token in (
    'LyricWindow._draw_active_song_fragment_batch = h57_active_fragment_batch',
    'LyricWindow._make_history_line = h57_make_history',
    'FadingLine.draw = h57_fading_draw',
    "'one-composited-depth-atlas-per-row-no-pressure-sharpen'",
    "'active-order-transform-and-same-material-through-exit'",
):
    if token not in act:
        fail('runtime wiring missing ' + token)

# H57 must build an actual single material from H56's filtered pixels rather than draw
# Bloom/Defocus/crisp as separate live passes.
build = fn_src('_h57_build_composite_shared')
for token in (
    '_h56_build_filtered_shared(shared, text, int(blur_levels), deadline_perf)',
    '_h56_build_filtered_shared(shared, text, int(bloom_levels), deadline_perf)',
    'qp.drawImage(target, crop)',
    '_h56_pack_filtered_entries(entries, style_sig)',
):
    if token not in build:
        fail('composite Atlas construction missing ' + token)
for forbidden in (
    '_draw_active_song_fragment_batch(',
    '_h56_draw_history_shared(',
    '_h54_haze_offsets(',
    '_h55_frost_offsets(',
):
    if forbidden in build:
        fail('composite construction contains live multi-pass renderer: ' + forbidden)

# Pressure is deliberately excluded from the H57 material identity/policy: an already visible
# row must never become sharp only because runtime pressure changes.
optics = fn_src('_h57_depth_optics')
if '_h56_depth_optics(level, layers, strength_pct, 0)' not in optics:
    fail('H57 optics must pin H56 material policy to pressure=0')
if 'pressure' in optics.replace('render pressure', ''):
    fail('H57 optics unexpectedly accepts runtime pressure')
key = fn_src('_h57_composite_cache_key')
if 'pressure' in key:
    fail('H57 material cache key must not vary with render pressure')

active = fn_src('h57_active_fragment_batch')
for token in (
    '_h57_get_composite_shared(',
    'final_shared = composite if composite is not None else shared',
    'window._h54_depth_enabled = False',
    'active_pre(',
):
    if token not in active:
        fail('active single-material path missing ' + token)
# There must be only one mature fragment call site in the depth-enabled final branch. The
# disabled/fallback branch is one other call; H57 must not add bloom/blur/crisp live calls.
if active.count('active_pre(') != 2:
    fail(f'active H57 should have one normal fallback + one composite draw, got {active.count("active_pre(")} call sites')
for forbidden in ('bloom_shared', 'blur_shared', 'float(bloom_alpha)', 'float(blur_alpha)', 'float(crisp)'):
    if forbidden in active:
        fail('active H57 still exposes H56 multi-pass material: ' + forbidden)

# History/fading must use the exact active transform order. This specifically protects the
# real-machine jump caused by scaling before projective perspective in H54/H56.
xf = fn_src('_h57_draw_row_with_active_order')
tokens = (
    'painter.setTransform(old_persp, True)',
    'painter.translate(old_x, old_y)',
    'painter.scale(float(scale), float(scale))',
)
positions = [xf.find(t) for t in tokens]
if any(p < 0 for p in positions):
    fail('history transform closure missing active-order step')
if not positions[0] < positions[1] < positions[2]:
    fail('history must apply perspective -> translate(anchor) -> Z scale')
for token in (
    'row.x = 0.0',
    'row.y = 0.0',
    'row.persp_transform = QTransform()',
    'row._h54_depth_enabled = False',
    'row._shared_fragment_atlas = shared_override',
    'return draw_callable(row, painter)',
):
    if token not in xf:
        fail('mature exit renderer neutralization missing ' + token)

hist = fn_src('h57_fading_draw')
for token in (
    '_h57_get_composite_shared(',
    '_h57_draw_row_with_active_order(',
    'final_shared = composite if composite is not None else shared',
):
    if token not in hist:
        fail('history/exit composite continuity missing ' + token)
for forbidden in (
    'progress <= 0.001',
    '_render_pressure_level',
    '_H55_FROST_PRESSURE_OVERRIDE',
    '_h56_draw_history_shared',
    'row.alpha = max(1, min(255, int(round(float(old_alpha) * float(crisp))))',
):
    if forbidden in hist:
        fail('history H57 can still switch material mid-lifetime: ' + forbidden)

mk = fn_src('h57_make_history')
for token in ('_h57_depth_composite_cache', '_h57_birth_anchor'):
    if token not in mk:
        fail('current->history material/anchor transfer missing ' + token)

# The H57 layer is presentation-only.
block = '\n'.join((
    fn_src('_h57_build_composite_shared'),
    fn_src('_h57_get_composite_shared'),
    fn_src('_h57_draw_row_with_active_order'),
    fn_src('_h57_activate_runtime'),
))
for forbidden in (
    'MediaSessionSync.', '_poll_loop', 'bind_track(', 'PyOpenGL', 'OpenGL.',
    'PIL.', 'numpy.', 'QOpenGLWidget(', 'QQuickWidget(', 'requests.',
):
    if forbidden in block:
        fail('H57 crossed presentation-only boundary: ' + forbidden)

# Pure policy replay: H57 must keep exactly the same optical profile regardless of any outside
# pressure state, while retaining H56's established depth curve.
env = {
    'H56_ATLAS_BLUR_MAX_LEVELS': 4,
    'H56_ATLAS_BLOOM_MAX_LEVELS': 5,
    'H56_PRESSURE_DISABLE': 2,
}
for name in ('_h54_depth_ratio', '_h56_depth_optics', '_h57_depth_optics'):
    exec(compile(ast.Module(body=[top_fn(name)], type_ignores=[]), '<h57-pure>', 'exec'), env)
far = env['_h57_depth_optics'](6, 6, 55)
if not (far[0] == 4 and far[2] == 5 and far[4] <= 0.16):
    fail(f'H57 lost H56 far-depth optical profile: {far!r}')
near = env['_h57_depth_optics'](1, 6, 55)
if near != (0, 0.0, 0, 0.0, 1.0):
    fail('focus layer must remain untouched')

print('DEPTH CONTINUITY COMPOSITE H57 REPLAY: PASS')
print(' - current/history/exit share one immutable composite depth material')
print(' - history uses active transform order: perspective -> anchor -> fixed Z scale')
print(' - runtime pressure/exit progress can no longer sharpen an already-visible deep row')
print(' - Bloom + Defocus + crisp are baked once, then one fragment batch is used per row/frame')
