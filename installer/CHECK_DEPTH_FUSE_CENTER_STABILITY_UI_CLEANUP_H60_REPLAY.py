from pathlib import Path
import ast, sys

if len(sys.argv) < 2:
    raise SystemExit('usage: CHECK_DEPTH_FUSE_CENTER_STABILITY_UI_CLEANUP_H60_REPLAY.py <main.py>')
path=Path(sys.argv[1]); src=path.read_text(encoding='utf-8'); tree=ast.parse(src); lines=src.splitlines()

def fail(msg): raise SystemExit('H60 FAIL: '+msg)
def need(tok, why):
    if tok not in src: fail(f'{why}: missing {tok!r}')
def fn(name):
    for node in ast.walk(tree):
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name==name: return node
    fail('function not found: '+name)
def fsrc(name):
    n=fn(name); return '\n'.join(lines[n.lineno-1:n.end_lineno])

need('+ DEPTH FUSE FALLBACK + CENTER TRANSACTION + UI CLEANUP H60','build tag')
need("if '_h60_activate_runtime' in globals():",'final activation')
if not (src.index("if '_h59_activate_runtime' in globals():") < src.index("if '_h60_activate_runtime' in globals():")):
    fail('H60 must activate after H59')

# Song-level fuse stays intact; a deep active row gets its own styled shared Atlas instead.
build=fsrc('_h60_build_line_shared')
for tok in ('_render_song_atlas_glyph(style_sig, ch)', '_h56_pack_filtered_entries(entries, style_sig)',
            'H60_LINE_ATLAS_MAX_GLYPHS', 'H60行级景深Atlas后备'):
    if tok not in build: fail('row-local depth fallback missing '+tok)
shared=fsrc('h60_shared_song_fragment_atlas')
for tok in ("_song_fragment_atlas_performance_fused", '_h60_fuse_fallback_armed',
            '_h54_active_depth_level', '_h60_build_line_shared(window, text)'):
    if tok not in shared: fail('fuse-aware shared Atlas routing missing '+tok)
if 'SONG_FRAGMENT_ATLAS_BUILD_BUDGET_MS =' in '\n'.join([build,shared]):
    fail('H60 must not weaken the full-song 850ms fuse')
# Cache-before-song lookup is intentional: a visible row must not swap material mid-line.
if shared.index("cached = getattr(window, '_h60_line_shared_cache'") > shared.index('shared = shared_pre(window)'):
    fail('row-local material is not frozen before a late song Atlas can replace it')

# Center correction is transactional and strictly monotonic.
push=fsrc('_h60_push_corridor_outside_center')
for tok in ('H60_CENTER_IMPROVEMENT_EPS', 'if after + float(H60_CENTER_IMPROVEMENT_EPS) >= before:',
            'restore()', 'commit=0', 'commit=1', 'monotonic=1', 'for mul in (1.0, 1.20, 1.45, 1.80)'):
    if tok not in push: fail('transactional center correction missing '+tok)
if 'window.x = int(round(float(original[0]) + float(dx)))' not in push:
    fail('candidate placement is not evaluated transactionally from the original anchor')

# Rich font preview controls must not also display duplicate blocking tooltips.
ui=fsrc('h60_control_init')
for tok in ('panel.findChildren(QFontComboBox)', "combo.setToolTip('')", "str(label.text() or '').strip() == 'Aa 你好'", 'panel.findChildren(DiyStylePreview)'):
    if tok not in ui: fail('preview tooltip cleanup missing '+tok)

# H60 stays presentation-only.
block='\n'.join(fsrc(n) for n in ('_h60_line_shared_key','_h60_build_line_shared','_h60_push_corridor_outside_center','_h60_activate_runtime'))
for bad in ('MediaSessionSync.', '_poll_loop', 'bind_track(', 'requests.', 'urllib.', 'win32com'):
    if bad in block: fail('presentation boundary crossed: '+bad)

print('DEPTH FUSE CENTER STABILITY UI CLEANUP H60 REPLAY: PASS')
print(' - full-song Atlas fuse remains; deep rows get a cached row-local styled Atlas fallback')
print(' - center correction commits only strict overlap improvements and rolls back worse candidates')
print(' - font hover previews no longer have duplicate tooltip overlays blocking their samples')
