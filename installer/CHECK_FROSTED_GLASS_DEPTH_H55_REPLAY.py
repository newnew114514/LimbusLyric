from pathlib import Path
import ast, sys

if len(sys.argv) < 2:
    raise SystemExit('usage: CHECK_FROSTED_GLASS_DEPTH_H55_REPLAY.py <main.py>')
path=Path(sys.argv[1]); src=path.read_text(encoding='utf-8'); tree=ast.parse(src); lines=src.splitlines()

def fail(msg): raise SystemExit('H55 FAIL: '+msg)
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

need('+ FROSTED GLASS DEPTH H55', 'build tag')
need("if '_h55_activate_runtime' in globals():", 'final activation')
if src.index("if '_h55_activate_runtime' in globals():") < src.index("if '_h54_activate_runtime' in globals():"):
    fail('H55 must activate after H54')

act=func_source('_h55_activate_runtime')
for token in (
    "globals()['_h54_haze_profile'] = _h55_frost_profile",
    "globals()['_h54_haze_offsets'] = _h55_frost_offsets",
    "row._h55_owner_window_ref = _h55_weakref.ref(window)",
    "owner._render_pressure_level()",
    "LyricWindow._make_history_line = h55_make_history",
    "FadingLine.draw = h55_fading_draw",
    "ControlPanel.__init__ = h55_control_init",
    "'h54-atlas-frost-pressure-aware-history'",
):
    if token not in act: fail('runtime wiring missing '+token)
for forbidden in ('QGraphicsBlurEffect(', 'GaussianBlur(', 'QImage(', 'MediaSessionSync.', '_poll_loop', 'bind_track'):
    if forbidden in act: fail('H55 must remain presentation-only / atlas-only: '+forbidden)

for token in ('启用随机 3D 毛玻璃景深','毛玻璃 / 景深强度：','6 层高强度时最深层设计为只剩模糊轮廓'):
    need(token, 'frosted-depth UI copy')

# Execute only pure optical helpers.
env={
    'H55_FROST_MAX_PASSES':8,
    'H55_FROST_PRESSURE_DISABLE':2,
    '_H55_FROST_PRESSURE_OVERRIDE':0,
}
for name in ('_h54_depth_ratio','_h55_frost_profile','_h55_frost_offsets'):
    exec(compile(ast.Module(body=[func_node(name)],type_ignores=[]),'<h55-helper>','exec'),env)

near=env['_h55_frost_profile'](1,6,55,0)
if near != (0.0,0.0,0,1.0): fail('foreground layer must stay completely sharp')
profiles=[env['_h55_frost_profile'](i,6,55,0) for i in range(1,7)]
radii=[p[0] for p in profiles]; crisps=[p[3] for p in profiles]; passes=[p[2] for p in profiles]
if not all(radii[i] <= radii[i+1]+1e-9 for i in range(5)): fail('frost radius not monotonic by depth')
if not all(crisps[i] >= crisps[i+1]-1e-9 for i in range(5)): fail('crisp core not monotonic by depth')
far=profiles[-1]
if not (far[0] >= 12.0 and far[1] >= 0.07 and far[2] == 8 and far[3] <= 0.20):
    fail('default 55% far layer is still too subtle for frosted-glass intent')
far100=env['_h55_frost_profile'](6,6,100,0)
if not (far100[0] >= 20.0 and far100[2] == 8 and far100[3] <= 0.10):
    fail('100% far layer does not approach near-unreadable frost')
press1=env['_h55_frost_profile'](6,6,55,1)
press2=env['_h55_frost_profile'](6,6,55,2)
if not (0 < press1[2] <= 4 and press1[0] < far[0] and press1[3] >= 0.58):
    fail('pressure level 1 does not cut frost cost / restore readability')
if press2 != (0.0,0.0,0,1.0): fail('pressure level 2 must disable all frost overhead')
if len(env['_h55_frost_offsets'](far[0],8)) != 8: fail('8-pass frost offset field missing')
if len(set(env['_h55_frost_offsets'](far[0],8))) != 8: fail('frost offset field contains duplicates')

print('FROSTED GLASS DEPTH H55 REPLAY: PASS')
print(' - default 55%/layer-6 has >=12px atlas diffusion, 8 passes, and <=20% crisp core')
print(' - 100%/layer-6 reaches >=20px diffusion with <=10% crisp core; layer 1 stays untouched')
print(' - history rows inherit renderer pressure through a weak owner reference; pressure 2 removes all extra frost passes')
