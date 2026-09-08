from pathlib import Path
import ast, sys, textwrap, math

if len(sys.argv) < 2:
    raise SystemExit('usage: CHECK_PER_EFFECT_EXIT_PROFILES_H70_REPLAY.py <main.py>')
path=Path(sys.argv[1]); src=path.read_text(encoding='utf-8'); tree=ast.parse(src); lines=src.splitlines()

def fail(msg): raise SystemExit('H70 FAIL: '+msg)
def need(tok, why):
    if tok not in src: fail(f'{why}: missing {tok!r}')
def fn(name):
    for node in ast.walk(tree):
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name==name:
            return node
    fail('function not found: '+name)
def fsrc(name):
    n=fn(name); return textwrap.dedent('\n'.join(lines[n.lineno-1:n.end_lineno]))

need('+ PER-EFFECT EXIT PROFILES + FLAVOR H70','build tag')
need("if '_h70_activate_runtime' in globals():",'activation')
if not (src.rindex("if '_h69_activate_runtime' in globals():") < src.rindex("if '_h70_activate_runtime' in globals():")):
    fail('H70 must activate after H69')
for name in (
    '_h70_normalize_profiles','_h70_apply_profile_to_row','_h70_release_budget_ms','_h70_soft_adapt_duration',
    '_h70_h16_exit_duration_ms','_h70_h51_exit_duration_ms','_h70_h68_plan_for_row','_h70_h68_release_duration',
    '_h70_fragment_exit_draw','_h70_fading_update','_h70_fading_draw','_h70_sync_profile_ui',
    '_h70_profile_slider_changed','_h70_control_init','_h70_capture_style_preset','_h70_load_style_preset',
    '_h70_save_all_config','_h70_activate_runtime'):
    fn(name)

# Profile normalization: every effect owns its own speed/flavor; legacy fade/rise migrates only
# into the classic fade flavor while all other flavor dimensions start at zero.
ns={
    'H70_EXIT_EFFECTS':('fade','per_char','wipe_ltr','wipe_rtl','shrink','soft_drift','hop_drop','blur_decay','instant'),
    'H70_SPEED_DEFAULT':12,'H70_SPEED_MIN':1,'H70_SPEED_MAX':15,
    'H70_FLAVOR_MIN':0,'H70_FLAVOR_MAX':100,'H70_FADE_RISE_MAX_PX':120.0,
}
exec(fsrc('_h70_clamp'),ns); exec(fsrc('_h70_normalize_profiles'),ns)
profiles=ns['_h70_normalize_profiles']({'fade_speed':12,'rise_speed':1})
if tuple(profiles) != ns['H70_EXIT_EFFECTS']:
    fail('profile set/order does not cover every public exit effect')
if profiles['fade']['speed'] != 12 or not (10 <= profiles['fade']['flavor'] <= 25):
    fail('legacy fade/rise migration is not preserving the classic default neighborhood')
if any(profiles[k]['flavor'] != 0 for k in profiles if k not in ('fade','instant')):
    fail('new flavors must default off for pre-H70 users')
if profiles['instant']['flavor'] != 0:
    fail('instant must never acquire a flavor')

# Row snapshot contract: changing UI later must not retarget a running row; old per-frame rise is
# zeroed because H70 owns it as a progress/total-distance flavor layer.
apply=fsrc('_h70_apply_profile_to_row')
for tok in ("row._h70_exit_speed = int(profile['speed'])", "row._h70_exit_flavor = int(profile['flavor'])",
            'row.fade_speed = int(profile[\'speed\'])', 'row.rise_speed = 0.0', 'row._h70_deadline_budget_ms = 0.0'):
    if tok not in apply: fail('row profile snapshot missing '+tok)

# flavor=0 must delegate the exact H51 mature fragment path. New scatter/trail code is entered only
# above zero, so users can always recover the H69 appearance.
frag=fsrc('_h70_fragment_exit_draw')
if "if flavor <= 0.0001 or effect not in ('per_char', 'wipe_ltr', 'wipe_rtl'):" not in frag:
    fail('fragment flavor-zero delegate guard missing')
if '_h70_fragment_draw_pre(row, painter, effect, progress)' not in frag:
    fail('fragment flavor-zero does not delegate mature renderer')
for tok in ('jitter = (_h70_seed_unit', 'drift = (10.0 + 18.0 * flavor)', 'ghost_opacity =', 'ghost_shift_x ='):
    if tok not in frag: fail('per-char scatter/wipe trail mechanism missing '+tok)
if 'min(1.0 - window, per_char_order * 0.58 + jitter)' not in frag:
    fail('per-char scatter may start too late to complete by final frame')
if 'local_rect = QRectF(ox + float(br.left()), oy + th / 3.0 + float(br.top())' not in frag:
    fail('H69 stable wrap topology was not preserved in H70 fragment path')

# Whole-row flavors are distinct and additive rather than one recycled rise transform.
draw=fsrc('_h70_fading_draw')
for tok in (
    'H70_FADE_RISE_MAX_PX', 'H70_SHRINK_PRETENSION_MAX', 'H70_SOFT_GRAVITY_EXTRA_PX',
    'H70_HOP_EXTRA_UP_PX', 'H70_HOP_EXTRA_DROP_PX', 'rot_strength =', 'H70_BLUR_DEPTH_EXPAND_MAX'):
    if tok not in draw: fail('named whole-row flavor missing '+tok)
if "if flavor <= 0.0001 or effect in ('per_char', 'wipe_ltr', 'wipe_rtl', 'instant'):" not in draw:
    fail('whole-row flavor-zero exact delegate guard missing')

# Dense-song adaptation must preserve relative user speed. The budget is allowed to compress an
# impractically slow preference, but faster preferences remain faster and no result becomes instant.
ns2={
    'H70_EXIT_EFFECTS':ns['H70_EXIT_EFFECTS'], 'H70_SPEED_DEFAULT':12,'H70_SPEED_MIN':1,'H70_SPEED_MAX':15,
    'H70_FLAVOR_MIN':0,'H70_FLAVOR_MAX':100,'H70_ADAPT_EXCESS_KEEP':0.24,
    'H70_ADAPT_HARD_MULT':1.45,'H70_ADAPT_HARD_PAD_MS':180.0,
}
for name in ('_h70_clamp','_h70_effect_key','_h70_effect_min_duration'):
    exec(fsrc(name),ns2)
ns2['_h70_row_speed']=lambda r:int(getattr(r,'_h70_exit_speed',12))
ns2['_h70_row_flavor']=lambda r:float(getattr(r,'_h70_exit_flavor',0))/100.0
ns2['write_error_log']=lambda *a,**k:None
exec(fsrc('_h70_soft_adapt_duration'),ns2)
class R: pass
r=R(); r._h70_deadline_budget_ms=570.0; r._h70_adapt_log_key=None; r._h70_exit_flavor=88
fast=ns2['_h70_soft_adapt_duration'](r,'fade',520.0)
normal=ns2['_h70_soft_adapt_duration'](r,'fade',620.0)
slow=ns2['_h70_soft_adapt_duration'](r,'fade',1200.0)
if not (380.0 <= fast < normal < slow <= 1200.0):
    fail(f'adaptive timing erased relative preference: fast={fast} normal={normal} slow={slow}')
if int(getattr(r,'_h70_exit_flavor',0)) != 88:
    fail('deadline adaptation mutated artistic flavor')
per=ns2['_h70_soft_adapt_duration'](r,'per_char',1200.0)
if per < 620.0:
    fail('per-char visible minimum was violated')

# Fixed-timer/planner effects receive the same speed intent without replacing their native engines.
scale_ns={'H70_SPEED_DEFAULT':12,'H70_SPEED_MIN':1,'H70_SPEED_MAX':15}
exec(fsrc('_h70_clamp'),scale_ns); exec(fsrc('_h70_time_scale_from_speed'),scale_ns)
scales=[scale_ns['_h70_time_scale_from_speed'](x) for x in (5,12,15)]
if not (scales[0] > scales[1] > scales[2]):
    fail('unified speed intent is not monotonic for hop/blur fixed timers')
shrink_src=fsrc('_h70_h51_exit_duration_ms')
for tok in ('420.0 * _h70_time_scale_from_speed(_h70_row_speed(row))', 'max(320.0, min(1200.0, preferred))'):
    if tok not in shrink_src: fail('shrink full-range speed calibration missing '+tok)
update_src=fsrc('_h70_fading_update')
for tok in ("if effect == 'soft_drift':", '620.0 * _h70_time_scale_from_speed(_h70_row_speed(row))', 'max(460.0, min(2200.0, preferred))'):
    if tok not in update_src: fail('soft-drift full-range speed calibration missing '+tok)
plan=fsrc('_h70_h68_plan_for_row'); release=fsrc('_h70_h68_release_duration')
for tok in ('_h70_time_scale_from_speed(_h70_row_speed(row))','H70_BLUR_TAIL_MIN_MS','H70_BLUR_TAIL_MAX_MS'):
    if tok not in plan+release: fail('blur speed preference missing '+tok)

# UI/config memory: one dynamic speed name plus one effect-specific flavor name. Instant disables
# both. Profiles are also included in full style presets and ordinary config autosave.
ui=fsrc('_h70_sync_profile_ui')+fsrc('_h70_control_init')
for label in ('上升距离','离散度','拖尾','蓄力','重力感','弹性','景深扩散'):
    if label not in src: fail('flavor label missing '+label)
for tok in ('h70_exit_speed_slider','h70_exit_flavor_slider', "enabled = effect != 'instant'", 'panel.h12_exit_combo'):
    if tok not in ui: fail('dynamic profile UI missing '+tok)
for tok in ("data['h70_exit_profiles']", "st['h70_exit_profiles']", '_h70_sync_profile_ui(panel)'):
    if tok not in fsrc('_h70_capture_style_preset')+fsrc('_h70_load_style_preset')+fsrc('_h70_save_all_config'):
        fail('profile persistence/preset memory missing '+tok)

activate=fsrc('_h70_activate_runtime')
for tok in (
    "globals()['_h16_exit_duration_ms'] = _h70_h16_exit_duration_ms",
    "globals()['_h51_exit_duration_ms'] = _h70_h51_exit_duration_ms",
    "globals()['_h51_fragment_exit_draw'] = _h70_fragment_exit_draw",
    "globals()['_h68_plan_for_row'] = _h70_h68_plan_for_row",
    'LyricWindow._make_history_line = _h70_make_history_line',
    'FadingLine.begin_fade = _h70_begin_fade','FadingLine.update = _h70_fading_update','FadingLine.draw = _h70_fading_draw',
    'ControlPanel.__init__ = _h70_control_init'):
    if tok not in activate: fail('runtime hook missing '+tok)

block_start=src.index('# H70 per-effect exit profiles + optional flavor layer')
block_end=src.index('# H71 flavor presence + instant UI cleanup', block_start)
block=src[block_start:block_end]
for bad in ('MediaSessionSync.', 'LyricSearchEngine.', '_commit_seek', '_on_seek', 'win32gui.', 'QImage(', 'QPixmap.fromImage('):
    if bad in block: fail('H70 crossed presentation/timing authority boundary: '+bad)

print('PER-EFFECT EXIT PROFILES H70 REPLAY: PASS')
print(' - every exit remembers its own speed and optional named flavor; instant stays parameter-free')
print(' - flavor=0 delegates the mature H69/H59/H51 renderer')
print(' - dense-song soft deadlines preserve relative fast/normal/slow preferences')
print(' - scatter, trail, pretension, gravity, elasticity and depth-spread are effect-native layers')
print(' - blur keeps H68/H69 planner continuity while accepting the same user speed intent')
