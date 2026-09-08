from pathlib import Path
import ast, math, sys

if len(sys.argv) < 2:
    raise SystemExit('usage: CHECK_PRESENTATION_DEPTH_CENTER_H53_REPLAY.py <main.py>')
path=Path(sys.argv[1]); src=path.read_text(encoding='utf-8'); tree=ast.parse(src); lines=src.splitlines()

def fail(msg):
    raise SystemExit('H53 FAIL: '+msg)
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

need('+ PRESENTATION DEPTH + CENTER AVOIDANCE H53', 'build tag')
need("if '_h53_activate_runtime' in globals():", 'final activation')
if src.index("if '_h53_activate_runtime' in globals():") < src.index("if '_h52_activate_runtime' in globals():"):
    fail('H53 must activate after H52')

frag=func_source('_h51_fragment_exit_draw')
for token in ('scatter_indices = list(range(n))','scatter_rng.shuffle(scatter_indices)','scatter_rank[scatter_idx]',"effect == 'per_char'",'drawPixmapFragments'):
    if token not in frag: fail('staggered per-char exit missing '+token)
if 'float(n - 1 - i)' in frag: fail('per-char exit still aliases right-to-left ordering')
if 'setClipRect' in frag: fail('fragment exit regressed to clipping')

act=func_source('_h53_activate_runtime')
for token in (
    'LyricWindow._placement_obstacles = h53_obstacles', 'LyricWindow.place_randomly = h53_place_randomly',
    'LyricWindow._make_history_line = h53_make_history', 'FadingLine.draw = h53_fading_draw',
    "'literal-center-frequency-full-footprint-avoidance'", "'matrix-only-depth-no-blur-no-rasterization'",
    "'h53_depth_enabled'", "'h53_depth_strength_pct'", "'h53_depth_layers'",
    "_h53_int_setting(st, 'h51_center_frequency_pct'", '_h53_center_overlap_ratio(window)',
    '_h53_push_placement_outside_center(window)', 'painter.scale(scale, scale)',
):
    if token not in act: fail('runtime/config wiring missing '+token)
for forbidden in ('QGraphicsBlurEffect','GaussianBlur','MediaSessionSync.','_poll_loop','bind_track'):
    if forbidden in act: fail('presentation-only H53 contains forbidden runtime coupling '+forbidden)

# Pure helper replay: zero must remain zero, depth must be bounded/monotonic.
env={'math':math}
for name in ('_h53_int_setting','_h53_box_intersection_area','_h53_depth_scale'):
    exec(compile(ast.Module(body=[func_node(name)],type_ignores=[]),'<h53-helper>','exec'),env)
if env['_h53_int_setting']({'x':0},'x',100,0,100) != 0: fail('persisted zero is still coerced to default')
if env['_h53_int_setting']({},'x',55,0,100) != 55: fail('default setting replay invalid')
scales=[env['_h53_depth_scale'](level,4,55) for level in range(4)]
if abs(scales[0]-1.0)>1e-9 or not (scales[0] > scales[1] > scales[2] >= scales[3] >= .72):
    fail('depth scale is not foreground-to-background monotonic')
if env['_h53_depth_scale'](3,4,0) != 1.0: fail('zero depth strength must be neutral')

# Execute the strict center push against a minimal fake window. The line starts fully in
# the exclusion rectangle and must finish with zero footprint intersection.
const={'H51_CENTER_X_MIN':.30,'H51_CENTER_X_MAX':.70,'H51_CENTER_Y_MIN':.28,'H51_CENTER_Y_MAX':.72,
       'H53_CENTER_PUSH_MARGIN_PX':18.0,'math':math}
for name in ('_h53_center_box','_h53_current_placement_box','_h53_box_intersection_area','_h53_center_overlap_ratio','_h53_push_placement_outside_center'):
    const.update(env)
    exec(compile(ast.Module(body=[func_node(name)],type_ignores=[]),'<h53-center>','exec'),const)
class Fake:
    full_text='demo'; x=500; y=500; angle=0; horizontal_wrap=False; _placement_recent=[]
    def width(self): return 1000
    def height(self): return 1000
    def _placement_box(self,text,x,y,angle): return (x-120,y-25,x+120,y+25)
    @staticmethod
    def _placement_box_center(box): return ((box[0]+box[2])*.5,(box[1]+box[3])*.5)
    @staticmethod
    def _placement_visible_boxes(box,sw,wrap): return [box]
    @staticmethod
    def _placement_max_overlap(a,b): return 0.0
    def compute_perspective(self): pass
f=Fake(); f._h53_obstacles_pre=lambda _w: []
if const['_h53_center_overlap_ratio'](f) <= 0: fail('center fixture does not start in exclusion zone')
if not const['_h53_push_placement_outside_center'](f): fail('strict center push did not run')
if const['_h53_center_overlap_ratio'](f) > 1e-9: fail('strict center push left visible footprint in center zone')

need('启用 3D 景深', 'depth control')
need('景深强度：', 'depth strength control')
need('景深层级：', 'depth layer control')
need('逐字消失（错落柔化）', 'distinct per-char label')

print('PRESENTATION DEPTH + CENTER AVOIDANCE H53 REPLAY: PASS')
print(' - persisted 0% remains zero and strict avoidance checks the full lyric footprint')
print(' - per-char exit uses a stable shuffled stagger, distinct from both directional wipes')
print(' - 3D depth is opt-in, bounded and matrix-only; no blur/raster/provider work is added')
