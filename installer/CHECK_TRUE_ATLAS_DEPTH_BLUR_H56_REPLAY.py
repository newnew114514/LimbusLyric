from pathlib import Path
import ast, sys

if len(sys.argv) < 2:
    raise SystemExit('usage: CHECK_TRUE_ATLAS_DEPTH_BLUR_H56_REPLAY.py <main.py>')
path = Path(sys.argv[1]); src = path.read_text(encoding='utf-8'); tree = ast.parse(src); lines = src.splitlines()

def fail(msg): raise SystemExit('H56 FAIL: ' + msg)
def need(token, reason):
    if token not in src: fail(f'{reason}: missing {token!r}')
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

need('+ TRUE ATLAS DEPTH BLUR H56', 'build tag')
need("if '_h56_activate_runtime' in globals():", 'final activation')
if src.index("if '_h56_activate_runtime' in globals():") < src.index("if '_h55_activate_runtime' in globals():"):
    fail('H56 must activate after H55')

# H56 must explicitly retire H55/H54 translated-copy haze rather than stacking on it.
act = fn_src('_h56_activate_runtime')
for token in (
    "globals()['_h54_haze_profile'] = _h56_no_legacy_haze_profile",
    "globals()['_h54_haze_offsets'] = _h56_no_legacy_haze_offsets",
    "LyricWindow._draw_active_song_fragment_batch = h56_active_fragment_batch",
    "LyricWindow._make_history_line = h56_make_history",
    "FadingLine.draw = h56_fading_draw",
    "'cached-lowpass-defocus-bloom-no-offset-ghosts'",
    "'held-row-lowpass-atlas-then-authoritative-exit'",
):
    if token not in act: fail('runtime wiring missing ' + token)

low = fn_src('_h56_lowpass_image')
for token in ('Qt.SmoothTransformation', '.scaled(', 'restore_sizes.append', 'reversed(restore_sizes)'):
    if token not in low: fail('true low-pass pyramid missing ' + token)
for forbidden in ('translate(', '_h54_haze_offsets', '_h55_frost_offsets'):
    if forbidden in low: fail('low-pass helper must not be offset-copy haze: ' + forbidden)

build = fn_src('_h56_build_filtered_shared')
for token in (
    'sheet.toImage()', 'QRectF(source).toAlignedRect()', 'source_image.copy(rect)',
    'padded.fill(Qt.transparent)', '_h56_lowpass_image(padded, int(levels))',
    'float(left), float(top), float(lw), float(lh), source_ss',
    'H56_ATLAS_BUILD_BUDGET_MS' if False else 'deadline_perf',
):
    if token not in build: fail('filtered Atlas construction missing ' + token)
if 'float(left) -' in build or 'float(lw) +' in build:
    fail('H56 must not move logical glyph anchors when adding transparent blur padding')

cache = fn_src('_h56_get_depth_atlases')
for token in ('_h56_depth_atlas_cache', "'blur': blur", "'bloom': bloom", 'H56_ATLAS_BUILD_BUDGET_MS'):
    if token not in cache: fail('row-lifetime blur cache missing ' + token)

active = fn_src('h56_active_fragment_batch')
for token in ('bloom_shared', 'blur_shared', 'float(bloom_alpha)', 'float(blur_alpha)', 'float(crisp)'):
    if token not in active: fail('active filtered pass missing ' + token)
for forbidden in ('_h54_haze_offsets(', '_h55_frost_offsets(', 'painter.translate(float(dx)', 'for dx, dy in'):
    if forbidden in active: fail('active H56 must not draw translated sharp copies: ' + forbidden)

hist = fn_src('h56_fading_draw')
for token in ('_h56_draw_history_shared', "progress <= 0.001", '_last_fragment_local_bounds', 'bounds.adjusted'):
    if token not in hist: fail('history blur / sparse-region closure missing ' + token)

# Presentation-only: no provider/transport/thread rewrites and no new optional package dependency.
block = '\n'.join([fn_src('_h56_activate_runtime'), fn_src('_h56_build_filtered_shared'), fn_src('_h56_lowpass_image')])
for forbidden in ('MediaSessionSync.', '_poll_loop', 'bind_track(', 'PyOpenGL', 'OpenGL.', 'PIL.', 'numpy.', 'QOpenGLWidget('):
    if forbidden in block: fail('H56 crossed presentation-only boundary: ' + forbidden)

for token in ('启用随机 3D 镜头景深', '随机景深与字形失焦', '镜头失焦 / 景深强度：'):
    need(token, 'H56 UI copy')

# Execute only the pure optical policy. This makes visual strength/pressure fallback a hard
# release contract without importing PyQt on non-Windows CI.
env = {
    'H56_ATLAS_BLUR_MAX_LEVELS': 4,
    'H56_ATLAS_BLOOM_MAX_LEVELS': 5,
    'H56_PRESSURE_DISABLE': 2,
}
for name in ('_h54_depth_ratio', '_h56_depth_optics', '_h56_no_legacy_haze_profile', '_h56_no_legacy_haze_offsets'):
    exec(compile(ast.Module(body=[top_fn(name)], type_ignores=[]), '<h56-pure>', 'exec'), env)

if env['_h56_no_legacy_haze_profile'](6, 6, 100, 0) != (0.0, 0.0, 0, 1.0):
    fail('legacy haze profile not hard-disabled')
if env['_h56_no_legacy_haze_offsets'](50, 8) != ():
    fail('legacy haze offsets not hard-disabled')
near = env['_h56_depth_optics'](1, 6, 55, 0)
if near != (0, 0.0, 0, 0.0, 1.0):
    fail('focus layer must be untouched')
profiles = [env['_h56_depth_optics'](i, 6, 55, 0) for i in range(1, 7)]
blur_levels = [p[0] for p in profiles]
crisps = [p[4] for p in profiles]
if not all(blur_levels[i] <= blur_levels[i+1] for i in range(5)):
    fail('true blur complexity must be monotonic by depth')
if not all(crisps[i] >= crisps[i+1] - 1e-9 for i in range(5)):
    fail('crisp core must fall monotonically by depth')
far = profiles[-1]
if not (far[0] == 4 and far[2] == 5 and far[4] <= 0.16 and far[1] >= 0.82 and far[3] >= 0.20):
    fail(f'default 55% far layer still too subtle: {far!r}')
far100 = env['_h56_depth_optics'](6, 6, 100, 0)
if not (far100[0] == 4 and far100[2] == 5 and far100[4] <= 0.07 and far100[1] >= 0.90):
    fail(f'100% far layer does not approach optical silhouette: {far100!r}')
p1 = env['_h56_depth_optics'](6, 6, 55, 1)
p2 = env['_h56_depth_optics'](6, 6, 55, 2)
if not (0 < p1[0] <= 2 and p1[2] == 0 and p1[4] >= 0.58):
    fail('pressure-1 downgrade contract broken')
if p2 != (0, 0.0, 0, 0.0, 1.0):
    fail('pressure-2 must remove all H56 overhead')

print('TRUE ATLAS DEPTH BLUR H56 REPLAY: PASS')
print(' - H55 translated-copy haze is retired at final activation')
print(' - glyph pixels are independently padded, smooth-downsampled/reconstructed, cached, and batch-rendered')
print(' - default far layer uses 4-level defocus + 5-level bloom with <=16% crisp core; pressure 2 restores sharp Atlas')
