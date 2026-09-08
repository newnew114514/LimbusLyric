from pathlib import Path
import ast, sys

if len(sys.argv) < 2:
    raise SystemExit('usage: CHECK_STYLE_DEPTH_MATERIAL_COHERENCE_H58_REPLAY.py <main.py>')
path=Path(sys.argv[1]); src=path.read_text(encoding='utf-8'); tree=ast.parse(src); lines=src.splitlines()

def fail(msg): raise SystemExit('H58 FAIL: '+msg)
def need(tok, why):
    if tok not in src: fail(f'{why}: missing {tok!r}')
def fn(name):
    for node in ast.walk(tree):
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name==name: return node
    fail('function not found: '+name)
def fsrc(name):
    n=fn(name); return '\n'.join(lines[n.lineno-1:n.end_lineno])

need('+ STYLE DEPTH MATERIAL COHERENCE H58','build tag')
need("if '_h58_activate_runtime' in globals():",'final activation')
if src.index("if '_h58_activate_runtime' in globals():") < src.index("if '_h57_activate_runtime' in globals():"):
    fail('H58 must activate after H57')

# The authoritative source glyph must contain effects BEFORE H56/H57 filter/composite work.
base=fsrc('_render_song_atlas_glyph')
for tok in ('_draw_soft_glow_path(qp, path, gc, glow_size, glow_alpha)',
            'QPen(stroke_color, stroke_width * 2.0', 'qp.setBrush(text_color); qp.drawPath(path)'):
    if tok not in base: fail('base styled glyph missing '+tok)
low=fsrc('_h56_build_filtered_shared')
if '_h56_lowpass_image(padded, int(levels))' not in low:
    fail('depth low-pass is not downstream of styled source pixels')
comp=fsrc('_h57_build_composite_shared')
if '_h56_build_filtered_shared(shared, text' not in comp:
    fail('H57 composite no longer consumes the styled source Atlas')

act=fsrc('_h58_activate_runtime')
for tok in (
    'LyricWindow._fragment_style_signature_for_visual = h58_fragment_style_signature',
    'LyricWindow._apply_pending_visual_style = h58_apply_pending_visual_style',
    'ControlPanel._apply_edge_style_live = h58_edge_live',
    'ControlPanel._apply_glow_live = h58_glow_live',
    'ControlPanel.pick_color = h58_pick_color',
    "'_limbus_layer', '') == 'H58'",
):
    if tok not in act: fail('runtime wiring missing '+tok)

sig=fsrc('h58_fragment_style_signature')
for tok in ("visual_style.get('_h58_material')", "bool(visual_style['outline_enabled'])",
            "bool(visual_style['shadow_enabled'])", "bool(visual_style['glow_enabled'])",
            "int(visual_style['glow_size'])", "int(visual_style['glow_alpha'])"):
    if tok not in sig: fail('full material signature missing '+tok)

queue=fsrc('_h58_queue_material')
for tok in ('lw._h58_pending_material = material', 'timer.start(int(H58_STYLE_PREWARM_DEBOUNCE_MS))',
            "commit=next-line-after-atlas", 'history=immutable'):
    if tok not in queue: fail('coalesced immutable queue missing '+tok)
if 'edge_pre(' in queue or 'glow_pre(' in queue:
    fail('queue must not mutate live row effects')

edge=fsrc('h58_edge_live'); glow=fsrc('h58_glow_live')
if "return _h58_queue_material(panel, 'edge')" not in edge:
    fail('active outline/shadow edit does not queue material')
if "return _h58_queue_material(panel, 'glow')" not in glow:
    fail('active glow edit does not queue material')
# Active branches must return before old mutating implementations.
if edge.index("return _h58_queue_material(panel, 'edge')") > edge.index('result = edge_pre(panel)'):
    fail('edge old live mutation can run before H58 active guard')
if glow.index("return _h58_queue_material(panel, 'glow')") > glow.index('result = glow_pre(panel)'):
    fail('glow old live mutation can run before H58 active guard')

pending=fsrc('h58_apply_pending_visual_style')
for tok in ('_h58_material_ready(window, material, visual)',
            '_h58_apply_material(window, material)',
            "window._h58_pending_material = None",
            'pending_pre(window)',
            'H58样式景深预热失败保留旧材质'):
    if tok not in pending: fail('atomic boundary commit missing '+tok)

prewarm=fsrc('_h58_prewarm_material')
for tok in ('prewarm_only=True', "_song_fragment_atlas_performance_fused = False",
            "h58-explicit-style-retry"):
    if tok not in prewarm: fail('explicit prewarm/fuse policy missing '+tok)

init=fsrc('h58_control_init')
for tok in ('timer.setSingleShot(True)', 'H58_STYLE_PREWARM_DEBOUNCE_MS',
            'panel.font_combo.currentFontChanged.connect(fixed_font_changed)',
            "reason='h58-fixed-font'"):
    if tok not in init: fail('fixed-font/debounce wiring missing '+tok)
pick=fsrc('h58_pick_color')
if "reason='h58-fixed-color'" not in pick or 'random_color_check.isChecked()' not in pick:
    fail('fixed-color path is not unified with visual Atlas queue')

# H58 is presentation-only.
block='\n'.join(fsrc(n) for n in (
    '_h58_material_snapshot','_h58_visual_payload','_h58_apply_material','_h58_material_key',
    '_h58_material_ready','_h58_prewarm_material','_h58_queue_material','_h58_activate_runtime'))
for bad in ('MediaSessionSync.', '_poll_loop', 'bind_track(', 'requests.', 'OpenGL.', 'QOpenGLWidget('):
    if bad in block: fail('presentation boundary crossed: '+bad)

print('STYLE DEPTH MATERIAL COHERENCE H58 REPLAY: PASS')
print(' - outline/shadow/glow are source pixels before H56/H57 depth filtering')
print(' - active style edits prewarm then commit atomically at a lyric boundary')
print(' - old rows keep birth material; failed prewarm cannot force sharp vector fallback')
print(' - fixed font/color and random style share the same depth-capable Atlas pipeline')
