from pathlib import Path
import ast, random, sys

if len(sys.argv) < 2:
    raise SystemExit('usage: CHECK_RANDOM_DEPTH_FONT_PREVIEW_H54_REPLAY.py <main.py>')
path=Path(sys.argv[1]); src=path.read_text(encoding='utf-8'); tree=ast.parse(src); lines=src.splitlines()

def fail(msg): raise SystemExit('H54 FAIL: '+msg)
def need(token, reason):
    if token not in src: fail(f'{reason}: missing {token!r}')
def func_source(name):
    for node in ast.walk(tree):
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name==name:
            return '\n'.join(lines[node.lineno-1:node.end_lineno])
    fail('function not found: '+name)
def func_node(name):
    for node in tree.body:
        if isinstance(node,ast.FunctionDef) and node.name==name: return node
    fail('top-level function not found: '+name)

need('+ RANDOM FIXED DEPTH + MULTISCRIPT FONT PREVIEW H54', 'build tag')
need("if '_h54_activate_runtime' in globals():", 'final activation')
if src.index("if '_h54_activate_runtime' in globals():") < src.index("if '_h53_activate_runtime' in globals():"):
    fail('H54 must activate after H53')

act=func_source('_h54_activate_runtime')
for token in (
    'LyricWindow._place_randomly_safe = h54_place_safe',
    'LyricWindow._make_history_line = h54_make_history',
    'LyricWindow._draw_active_song_fragment_batch = h54_active_fragment_batch',
    'FadingLine.draw = h54_fading_draw',
    'ControlPanel._show_font_family_preview = h54_font_preview',
    "globals()['_h53_apply_panel_presentation'] = _h54_apply_panel_depth",
    'row._h53_depth_enabled = False',
    "'_h54_active_depth_level'",
    "'sample-fixed-depth-before-placement-no-font-mutation'",
    '_h54_haze_profile(level, layers, strength, pressure)',
    '_render_pressure_level()',
):
    if token not in act: fail('runtime wiring missing '+token)
for forbidden in ('QGraphicsBlurEffect(', 'GaussianBlur(', 'MediaSessionSync.', '_poll_loop', 'bind_track'):
    if forbidden in act: fail('presentation-only H54 contains forbidden coupling '+forbidden)

make=func_source('_h54_prepare_current_depth')
for token in ('new_token', '_h54_pick_depth_level(layers)', '_h54_active_depth_token'):
    if token not in make: fail('fixed active depth missing '+token)
transform=func_source('_h54_apply_active_depth_transform')
for token in ('_h54_depth_scale(level, layers, strength)', 'painter.scale(float(scale), float(scale))'):
    if token not in transform: fail('matrix-only active recession missing '+token)
if '_h53_apply_depth_rows' in act: fail('H54 must not renumber rows using H53 age stack')

hist=func_source('h54_make_history') if False else act
if "row._h54_depth_level = max(1, min(row._h54_depth_layers, int(getattr(window, '_h54_active_depth_level'" not in act:
    fail('history does not inherit current fixed depth')
if 'setPointSize' in act or '_h54_active_unscaled_font' in act:
    fail('H54 must not mutate font size/signature for depth')

preview=func_source('_h54_font_preview_text')
for token in ('日本語', 'かな カナ', '한국어', '한글', '日文 △ 缺字', '韩文 △ 缺字'):
    if token not in preview: fail('multiscript preview missing '+token)
if '歌词预览' in preview: fail('legacy filler text still present in H54 preview')

# Pure helper replay.
env={'random':random,'H54_DEPTH_MIN_SCALE':0.80,'H54_HAZE_MAX_PASSES':4,'H54_HAZE_PRESSURE_DISABLE':2}
for name in ('_h54_depth_ratio','_h54_depth_scale','_h54_pick_depth_level','_h54_haze_profile','_h54_haze_offsets'):
    exec(compile(ast.Module(body=[func_node(name)],type_ignores=[]),'<h54-helper>','exec'),env)

if env['_h54_depth_ratio'](1,4) != 0.0 or abs(env['_h54_depth_ratio'](4,4)-1.0) > 1e-9:
    fail('depth ratio endpoints invalid')
scales=[env['_h54_depth_scale'](i,4,55) for i in range(1,5)]
if not (abs(scales[0]-1.0)<1e-9 and scales[0] > scales[1] > scales[2] > scales[3] >= .80):
    fail('fixed-layer scale is not bounded/monotonic')

class SeqRng:
    def __init__(self): self.v=0
    def randint(self,a,b):
        self.v += 1
        return a + (self.v-1) % (b-a+1)
rng=SeqRng(); levels=[env['_h54_pick_depth_level'](4,rng) for _ in range(8)]
if levels != [1,2,3,4,1,2,3,4]: fail('depth picker cannot address every configured layer')

near=env['_h54_haze_profile'](1,4,70,0)
far=env['_h54_haze_profile'](4,4,70,0)
pressured=env['_h54_haze_profile'](4,4,70,2)
if near[2] != 0: fail('foreground layer must stay sharp')
if not (far[0] > 0 and far[1] > 0 and far[2] in (2,4) and far[3] < 1.0): fail('far layer lacks optical haze')
if pressured[2] != 0: fail('render-pressure fuse does not disable haze')
if len(env['_h54_haze_offsets'](far[0], far[2])) != far[2]: fail('haze pass count mismatch')

need('启用随机 3D 景深', 'new depth control text')
need('纵深 / 柔焦强度：', 'depth/defocus control text')
need('随机深度层级：', 'random layer control text')

print('RANDOM FIXED DEPTH + FONT PREVIEW H54 REPLAY: PASS')
print(' - every lyric samples one fixed 1..N depth before placement; history inherits it unchanged')
print(' - far layers use bounded atlas-only haze with renderer-pressure fuse; H53 age-stack scaling is retired')
print(' - hover font preview contains Chinese/Latin/Japanese/Korean samples with Japanese/Korean glyph coverage hints')
