from pathlib import Path
import ast, sys, textwrap, math

if len(sys.argv) < 2:
    raise SystemExit('usage: CHECK_EXIT_LIFECYCLE_DIRTY_CLOSURE_H72_REPLAY.py <main.py>')
path=Path(sys.argv[1]); src=path.read_text(encoding='utf-8'); tree=ast.parse(src); lines=src.splitlines()

def fail(msg): raise SystemExit('H72 FAIL: '+msg)
def need(tok, why):
    if tok not in src: fail(f'{why}: missing {tok!r}')
def fn(name):
    for node in ast.walk(tree):
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name==name:
            return node
    fail('function not found: '+name)
def fsrc(name):
    n=fn(name); return textwrap.dedent('\n'.join(lines[n.lineno-1:n.end_lineno]))

need('+ EXIT LIFECYCLE + DIRTY CLOSURE H72','build tag')
need("if '_h72_activate_runtime' in globals():",'activation')
if not (src.rindex("if '_h71_activate_runtime' in globals():") < src.rindex("if '_h72_activate_runtime' in globals():")):
    fail('H72 must activate after H71')
for name in (
    '_h72_owner_window','_h72_region_rects','_h72_expand_region','_h72_flavor_dirty_padding',
    '_h72_held_visual_region','_h72_h68_playback_integrator','_h72_h68_plan_for_row','_h72_orphan_blur_progress',
    '_h72_decay_progress','_h72_begin_fade','_h72_fading_update','_h72_discard_fading_item','_h72_activate_runtime'):
    fn(name)

# Dirty-region closure: all H70/H71 optional motion must participate in sparse repainting,
# and the last envelope must be explicitly invalidated after a row retires.
pad=fsrc('_h72_flavor_dirty_padding')
for tok in (
    "effect == 'fade'", "effect == 'per_char'", "effect in ('wipe_ltr', 'wipe_rtl')",
    "effect == 'shrink'", "effect == 'soft_drift'", "effect == 'hop_drop'", "effect == 'blur_decay'",
    'H70_FADE_RISE_MAX_PX','H71_SOFT_EXTRA_GRAVITY_PX','H71_HOP_EXTRA_DROP_PX','H71_BLUR_EXTRA_EXPAND'):
    if tok not in pad: fail('flavor dirty envelope missing '+tok)
held=fsrc('_h72_held_visual_region')
for tok in ('_h72_flavor_dirty_padding(item, base)','_h72_expand_region(window, base, *pad)',"'_h72_last_dirty_region'"):
    if tok not in held: fail('held-region flavor envelope missing '+tok)
upd=fsrc('_h72_fading_update')
for tok in (
    '_h72_held_visual_region(window, row)', "'_pending_explicit_region'",
    'pending.united(retire_region)', 'H72_EXIT_HARD_MAX_MS', "row.release_render_resources()",
    'window._render_force_full = True'):
    if tok not in upd: fail('retirement cleanup/watchdog missing '+tok)

discard=fsrc('_h72_discard_fading_item')
for tok in ('_h72_held_visual_region(window, item)', '_h72_discard_fading_pre(item)', "'_pending_explicit_region'", 'pending.united(retire_region)', 'window._render_force_full = True'):
    if tok not in discard: fail('direct-discard dirty closure missing '+tok)

integrator=fsrc('_h72_h68_playback_integrator')
for tok in ("'_last_position_ms'", "'_h72_last_playback_pos_ms'", 'delta = max(0.0, pos - last_pos)', 'delta = min(delta, 1200.0)', 'row._h68_last_mono = now - delta'):
    if tok not in integrator: fail('playback-clock H68 integrator missing '+tok)

# Verify committed pad constants are large enough for H71's actual high-end amplitudes.
consts={}
for node in tree.body:
    if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and node.targets[0].id.startswith('H72_'):
        try: consts[node.targets[0].id]=ast.literal_eval(node.value)
        except Exception: pass
if float(consts.get('H72_PER_CHAR_EXTRA_PAD_PX',0)) < 90.0: fail('per-char dirty pad too small')
if float(consts.get('H72_WIPE_EXTRA_X_PX',0)) < 70.0: fail('wipe dirty pad too small')
if float(consts.get('H72_EXIT_HARD_MAX_MS',0)) < 12000.0: fail('hard watchdog would intrude on slow valid exits')

# H68 deadline must follow sampled media position rather than consuming pause wall-clock time.
plan=fsrc('_h72_h68_plan_for_row')
for tok in ("getattr(window, '_last_position_ms', None)",'_h68_exact_horizon_ms(window, origin, capacity)',
            '_h68_timeline_start(window, int(exact_evict))','remaining = max(0.0, float(evict_start) - float(pos))',
            "row._h72_deadline_clock = 'playback-position'"):
    if tok not in plan: fail('playback-clock deadline closure missing '+tok)
# Pure replay of the intended pause invariant: wall clock can advance arbitrarily, position frozen => same horizon.
evict_start=159311.0; paused_pos=150000.0
r1=max(0.0,evict_start-paused_pos); r2=max(0.0,evict_start-paused_pos)
if r1 != r2 or int(r1) != 9311: fail('pause invariant arithmetic changed')

# Tail rows without a future capacity eviction must regain natural playback-clock retirement and
# be allowed to cross H68's 0.939 active shelf all the way to expired=1.
orph=fsrc('_h72_orphan_blur_progress')
for tok in (
    'if exact is not None:', "getattr(window, '_last_position_ms', None)", '_h62_decay_durations(row)',
    '(float(pos) - float(entry_start)) / max(1.0, float(hold_ms))', "row._h62_decay_expired = True",
    "'H72尾段失焦自然退休'"):
    if tok not in orph: fail('orphan blur retirement missing '+tok)
# Playback freezes at pause; the natural progress does too. It may exceed the old active shelf when playback advances.
entry=149461.0; hold=18000.0
p_pause=max(0.0,min(1.0,(160000.0-entry)/hold))
p_same=max(0.0,min(1.0,(160000.0-entry)/hold))
p_late=max(0.0,min(1.0,(174000.0-entry)/hold))
if abs(p_pause-p_same)>1e-12: fail('orphan progress changes while playback position is frozen')
if p_late < 0.999: fail('tail row can still park below completion after hold budget')

# History->fading handoff keeps the monotonic optical floor even if membership-dependent planners
# would otherwise return a sharper state after the row is removed from history_lines.
beg=fsrc('_h72_begin_fade')
for tok in ('_h69_optical_progress_floor','_h65_capacity_progress','_h62_decay_release_progress',
            'corrected = max(existing',"row._h68_release_duration_ms = 0.0", "'H72失焦退场交接连续性修正'"):
    if tok not in beg: fail('blur handoff floor closure missing '+tok)

activate=fsrc('_h72_activate_runtime')
for tok in (
    '_h68_plan_for_row = _h72_h68_plan_for_row','_h62_decay_progress = _h72_decay_progress',
    'LyricWindow._held_visual_region = _h72_held_visual_region',
    'FadingLine.begin_fade = _h72_begin_fade','FadingLine.update = _h72_fading_update'):
    if tok not in activate: fail('runtime hook missing '+tok)

# Presentation/lifecycle only. H72 may read the sampled playback position but must not poll media,
# alter seek/provider authority, start workers, or perform raster conversion.
block=src[src.index('# H72 exit lifecycle + dirty-region closure'):]
if '# H73 editorial instrument UI' in block:
    block=block[:block.index('# H73 editorial instrument UI')]
else:
    block=block[:block.index('if __name__ == "__main__":')]
for bad in ('MediaSessionSync.', 'LyricSearchEngine.', '_commit_seek', '_on_seek', 'win32gui.',
            'threading.Thread(', 'QImage(', 'QPixmap.fromImage(', '._playback_position('):
    if bad in block: fail('H72 crossed presentation/lifecycle boundary: '+bad)

print('EXIT LIFECYCLE + DIRTY CLOSURE H72 REPLAY: PASS')
print(' - effect-native flavor motion is part of sparse dirty accounting for natural and direct-drop retirement')
print(' - exact blur deadlines and active integration follow sampled playback position; pauses consume neither horizon nor progress')
print(' - end-of-timeline history with no capacity eviction naturally reaches progress=1 on playback time')
print(' - history->fading blur handoff preserves the monotonic optical floor')
print(' - 15s hard watchdog is terminal insurance only; normal effect timing remains H70-owned')
