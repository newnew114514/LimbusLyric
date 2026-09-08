from pathlib import Path
import ast, sys, math

if len(sys.argv) < 2:
    raise SystemExit('usage: CHECK_EXIT_CENTER_SCRIPT_PREVIEW_H59_REPLAY.py <main.py>')
path=Path(sys.argv[1]); src=path.read_text(encoding='utf-8'); tree=ast.parse(src); lines=src.splitlines()

def fail(msg): raise SystemExit('H59 FAIL: '+msg)
def need(tok, why):
    if tok not in src: fail(f'{why}: missing {tok!r}')
def fn(name):
    for node in ast.walk(tree):
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name==name: return node
    fail('function not found: '+name)
def fsrc(name):
    n=fn(name); return '\n'.join(lines[n.lineno-1:n.end_lineno])

def exec_fn(name, ns):
    n=fn(name)
    mod=ast.Module(body=[n], type_ignores=[])
    ast.fix_missing_locations(mod)
    exec(compile(mod, '<h59-replay>', 'exec'), ns)
    return ns[name]

need('+ EXIT CONTINUITY + CENTER CORRIDOR + SCRIPT PREVIEW H59','build tag')
need("if '_h59_activate_runtime' in globals():",'final activation')
if not (src.index("if '_h57_activate_runtime' in globals():") <
        src.index("if '_h58_activate_runtime' in globals():") <
        src.index("if '_h59_activate_runtime' in globals():")):
    fail('H59 must activate after H57 and H58')

# Deterministic quota must make 0 strict, 100 unrestricted, and 15% non-clustered.
class W: pass
quota_ns={'H51_CENTER_FREQ_DEFAULT':100}
quota=exec_fn('_h59_center_quota_allows',quota_ns)
w=W()
if quota(w,0) is not False: fail('0% is not strict-center deny')
if quota(w,100) is not True: fail('100% is not unrestricted')
w=W(); seq=[bool(quota(w,15)) for _ in range(20)]
if sum(seq)!=3: fail(f'15% quota expected 3 admissions/20, got {sum(seq)}: {seq}')
if any(a and b for a,b in zip(seq,seq[1:])): fail('15% quota can cluster adjacent center admissions')

# The corridor must include optical depth, perspective/wrap copies and post-placement push.
for tok in ('_h57_optical_margin(', '_placement_visible_boxes(', 'persp_transform', 'horizontal_wrap'):
    if tok not in fsrc('_h59_center_corridor_margin') + fsrc('_h59_current_corridor_boxes'):
        fail('center visual corridor missing '+tok)
place=fsrc('h59_place_randomly')
for tok in ('_h59_center_quota_allows(window, freq)',
            'window._h51_center_frequency_pct = 100 if allow else 0',
            '_h59_center_corridor_overlap(window, margin)',
            '_h59_push_corridor_outside_center(window, margin)',
            'H59中央走廊约束'):
    if tok not in place: fail('center quota/corridor wiring missing '+tok)

# Script-specific selectors must not use the general multi-script text for their own popup.
preview=fsrc('_h59_script_preview_text')
for tok in ('春風と星空', '노래와 별빛', 'The quick brown fox', '_h51_font_supports_text'):
    if tok not in preview: fail('script preview missing '+tok)
hook=fsrc('h59_font_preview')
for tok in ("h51_font_ja_combo", "h51_font_ko_combo", "h51_font_western_combo",
            "kind = 'ja'", "kind = 'ko'", "kind = 'western'",
            '_h59_script_preview_text(kind, family)'):
    if tok not in hook: fail('script-specific preview routing missing '+tok)

# Hop/drop motion should rise first, fall later, and fade; it must use the H57/H58 birth material.
hop_ns={'math':math, '_h51_smoothstep':lambda x: x*x*(3.0-2.0*x)}
hop=exec_fn('_h59_hop_profile',hop_ns)
dy0,a0=hop(0.0); dy_up,a_up=hop(0.30); dy_down,a_down=hop(0.85); dy1,a1=hop(1.0)
if not (abs(dy0)<1e-6 and dy_up < -20.0 and dy_down > 0.0 and dy1 >= 47.0):
    fail(f'hop/drop trajectory invalid: {(dy0,dy_up,dy_down,dy1)}')
if not (a0 > a_up > a_down > a1-1e-9 and a1 <= 0.001):
    fail(f'hop/drop alpha invalid: {(a0,a_up,a_down,a1)}')
draw=fsrc('h59_fading_draw')
for tok in ("row.exit_effect = 'fade'", 'result = fading_draw_pre(row, painter)',
            'row.y = old_y + float(dy)', 'row.exit_effect = old_effect'):
    if tok not in draw: fail('hop/drop does not reuse mature depth material draw: '+tok)
if 'setClipRect' in draw: fail('hop/drop reintroduced rectangular clipping')

# First visible frame must be guarded for mature effects and the H59-owned timer itself.
upd=fsrc('h59_fading_update')
for tok in ('H59_EXIT_FIRST_FRAME_CATCHUP_MS', 'row._h16_exit_started_mono = now -',
            'row._fade_last_step_mono = now -', 'row._h59_hop_started_mono = started',
            'H59退场首帧未呈现诊断'):
    if tok not in upd: fail('first-frame continuity missing '+tok)
held=fsrc('h59_held_visual_region')
if 'translated(0, -30)' not in held or 'translated(0, 56)' not in held:
    fail('hop/drop dirty region does not reserve both motion tails')

# H59-only selection must survive H51's older combo initialization on restart.
init=fsrc('h59_control_init')
for tok in ("_h59_saved_settings = (load_all_config().get('settings') or {})",
            "_h59_saved_settings.get('h12_exit_effect'",
            '_h59_saved_exit == H59_EXIT_EFFECT_HOP_DROP',
            'panel.lyric_window.exit_effect = H59_EXIT_EFFECT_HOP_DROP',
            "insertItem(insert_at, '轻跃下坠淡出', H59_EXIT_EFFECT_HOP_DROP)"):
    if tok not in init: fail('hop/drop persistence/UI missing '+tok)

# H59 must remain a final presentation layer.
block='\n'.join(fsrc(n) for n in (
    '_h59_script_preview_text','_h59_center_quota_allows','_h59_center_corridor_margin',
    '_h59_current_corridor_boxes','_h59_center_corridor_overlap','_h59_push_corridor_outside_center',
    '_h59_hop_profile','_h59_activate_runtime'))
for bad in ('MediaSessionSync.', '_poll_loop', 'bind_track(', 'requests.', 'urllib.', 'win32com'):
    if bad in block: fail('presentation boundary crossed: '+bad)

print('EXIT CENTER SCRIPT PREVIEW H59 REPLAY: PASS')
print(' - non-instant exits protect the first visible frame; hop/drop has the same guard')
print(' - 15% center admission is quota-based, while avoided rows protect motion/blur/perspective corridors')
print(' - Japanese/Korean/Western selectors preview only the script they control')
print(' - hop/drop reuses the immutable H57/H58 depth/outline/Glow birth material')
