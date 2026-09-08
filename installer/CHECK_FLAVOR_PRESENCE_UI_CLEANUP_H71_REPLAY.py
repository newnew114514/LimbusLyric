from pathlib import Path
import ast, sys, textwrap, math

if len(sys.argv) < 2:
    raise SystemExit('usage: CHECK_FLAVOR_PRESENCE_UI_CLEANUP_H71_REPLAY.py <main.py>')
path=Path(sys.argv[1]); src=path.read_text(encoding='utf-8'); tree=ast.parse(src); lines=src.splitlines()

def fail(msg): raise SystemExit('H71 FAIL: '+msg)
def need(tok, why):
    if tok not in src: fail(f'{why}: missing {tok!r}')
def fn(name):
    for node in ast.walk(tree):
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name==name:
            return node
    fail('function not found: '+name)
def fsrc(name):
    n=fn(name); return textwrap.dedent('\n'.join(lines[n.lineno-1:n.end_lineno]))

need('+ FLAVOR PRESENCE + INSTANT UI CLEANUP H71','build tag')
need("if '_h71_activate_runtime' in globals():",'activation')
if not (src.rindex("if '_h70_activate_runtime' in globals():") < src.rindex("if '_h71_activate_runtime' in globals():")):
    fail('H71 must activate after H70')
for name in ('_h71_presence','_h71_fragment_exit_draw','_h71_fading_draw','_h71_make_history_line','_h71_sync_profile_ui','_h71_activate_runtime'):
    fn(name)

# Presence curve: exact off remains exact, while the midpoint must be useful rather than subtle.
ns={'H71_PRESENCE_POWER':0.72}
exec(fsrc('_h71_presence'),ns)
pres=ns['_h71_presence']
if pres(0.0) != 0.0 or abs(pres(1.0)-1.0) > 1e-9:
    fail('presence curve changed endpoints')
mid=pres(0.5)
if not (0.58 <= mid <= 0.64):
    fail(f'50% presence not sufficiently readable: {mid}')

frag=fsrc('_h71_fragment_exit_draw')
for tok in (
    'H71_PER_CHAR_DRIFT_GAIN_PX','H71_PER_CHAR_ROT_MAX_DEG','0.32 * flavor',
    'H71_WIPE_GHOST_MAX_ALPHA','H71_WIPE_SECOND_GHOST_MAX_ALPHA','ghost2_opacity',
    'rotation = (_h70_seed_unit','local_rect = QRectF(ox + float(br.left())'):
    if tok not in frag: fail('strong fragment-native flavor missing '+tok)
if "if raw_flavor <= 0.0001 or effect not in ('per_char', 'wipe_ltr', 'wipe_rtl'):" not in frag:
    fail('fragment flavor-zero delegate guard missing')
if '_h71_fragment_draw_pre(row, painter, effect, progress)' not in frag:
    fail('fragment zero/fallback no longer delegates H70')

# Verify useful physical maxima and midpoint magnitudes from the constants committed by H71.
consts={}
for node in tree.body:
    if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and node.targets[0].id.startswith('H71_'):
        try: consts[node.targets[0].id]=ast.literal_eval(node.value)
        except Exception: pass
for key,lo in {
    'H71_PER_CHAR_DRIFT_GAIN_PX':45.0,
    'H71_PER_CHAR_ROT_MAX_DEG':7.0,
    'H71_WIPE_GHOST_MAX_ALPHA':0.30,
    'H71_SHRINK_EXTRA_PRETENSION':0.065,
    'H71_SOFT_EXTRA_GRAVITY_PX':55.0,
    'H71_HOP_EXTRA_DROP_PX':45.0,
    'H71_BLUR_EXTRA_EXPAND':0.055,
}.items():
    if float(consts.get(key,0.0)) < lo: fail(f'{key} still too subtle: {consts.get(key)}')
midp=mid
per_mid=(float(consts['H71_PER_CHAR_DRIFT_BASE_PX'])+float(consts['H71_PER_CHAR_DRIFT_GAIN_PX'])*midp)*midp
if per_mid < 25.0: fail(f'50% per-char drift still too subtle: {per_mid:.1f}px')
if float(consts['H71_BLUR_EXTRA_EXPAND'])*midp < 0.035:
    fail('50% blur depth expansion still too subtle')

whole=fsrc('_h71_fading_draw')
for tok in ('H71_SHRINK_EXTRA_PRETENSION','H71_SOFT_EXTRA_GRAVITY_PX','H71_HOP_EXTRA_UP_PX','H71_HOP_EXTRA_DROP_PX','H71_HOP_EXTRA_ROT_DEG','H71_BLUR_EXTRA_EXPAND'):
    if tok not in whole: fail('whole-row presence layer missing '+tok)
if "if raw_flavor <= 0.0001 or effect in ('fade', 'per_char', 'wipe_ltr', 'wipe_rtl', 'instant'):" not in whole:
    fail('whole-row flavor-zero/classic delegate guard missing')
if '_h71_fading_draw_pre(row, painter)' not in whole:
    fail('whole-row layer no longer composes H70 renderer')

# Enabled fragment-native flavors must request the existing asynchronous H61 material worker;
# no direct QImage/QPixmap conversion is allowed in H71.
prewarm=fsrc('_h71_make_history_line')
for tok in ("effect in ('per_char', 'wipe_ltr', 'wipe_rtl')", "globals().get('_h61_schedule_row_atlas')", "state == 'scheduled'", 'gui_build=0'):
    if tok not in prewarm: fail('fragment material prewarm contract missing '+tok)

ui=fsrc('_h71_sync_profile_ui')
for tok in ("visible = effect != 'instant'", "w.setVisible(visible)", '直接消失命中后立即移除，不存在退场速度或专属风味设置。'):
    if tok not in ui: fail('instant control-row cleanup missing '+tok)
for tok in ('h70_exit_speed_name','h70_exit_speed_slider','h70_exit_speed_value','h70_exit_flavor_name','h70_exit_flavor_slider','h70_exit_flavor_value'):
    if tok not in ui: fail('instant cleanup does not cover '+tok)

activate=fsrc('_h71_activate_runtime')
for tok in (
    "globals()['_h51_fragment_exit_draw'] = _h71_fragment_exit_draw",
    'FadingLine.draw = _h71_fading_draw',
    'LyricWindow._make_history_line = _h71_make_history_line',
    "globals()['_h70_sync_profile_ui'] = _h71_sync_profile_ui"):
    if tok not in activate: fail('runtime hook missing '+tok)

block=src[src.index('# H71 flavor presence + instant UI cleanup'):]
# H72 is a later reviewed presentation/lifecycle layer; H71 owns only its own source block.
if '# H72 exit lifecycle + dirty-region closure' in block:
    block=block[:block.index('# H72 exit lifecycle + dirty-region closure')]
else:
    block=block[:block.index('if __name__ == "__main__":')]
for bad in ('MediaSessionSync.', 'LyricSearchEngine.', '_commit_seek', '_on_seek', 'win32gui.', 'threading.Thread(', 'QImage(', 'QPixmap.fromImage('):
    if bad in block: fail('H71 crossed presentation/material-scheduling boundary: '+bad)

print('FLAVOR PRESENCE + INSTANT UI CLEANUP H71 REPLAY: PASS')
print(' - 0% remains exact H70/H69; 50% is intentionally readable and 100% materially distinct')
print(' - per-char scatter and wipe trails gain stronger glyph-native movement/echoes without edge-wrap topology changes')
print(' - shrink/gravity/hop/depth flavors are amplitude-only overlays; H70 timing/deadline ownership remains intact')
print(' - per-char/wipe material is prewarmed through the existing H61 async worker')
print(' - direct disappear hides both profile rows instead of displaying disabled/none controls')
