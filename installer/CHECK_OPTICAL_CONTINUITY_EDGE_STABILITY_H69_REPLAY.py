from pathlib import Path
import ast, sys, textwrap, time

if len(sys.argv) < 2:
    raise SystemExit('usage: CHECK_OPTICAL_CONTINUITY_EDGE_STABILITY_H69_REPLAY.py <main.py>')
path=Path(sys.argv[1]); src=path.read_text(encoding='utf-8'); tree=ast.parse(src); lines=src.splitlines()

def fail(msg): raise SystemExit('H69 FAIL: '+msg)
def need(tok, why):
    if tok not in src: fail(f'{why}: missing {tok!r}')
def fn(name):
    for node in ast.walk(tree):
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name==name:
            return node
    fail('function not found: '+name)
def fsrc(name):
    n=fn(name); return textwrap.dedent('\n'.join(lines[n.lineno-1:n.end_lineno]))

need('+ OPTICAL CONTINUITY + EDGE WRAP STABILITY H69','build tag')
need("if '_h69_activate_runtime' in globals():",'activation')
if not (src.rindex("if '_h68_activate_runtime' in globals():") < src.rindex("if '_h69_activate_runtime' in globals():")):
    fail('H69 must activate after H68')
for name in ('_h69_monotonic_decay_progress','_h69_schedule_decay_atlases','_h69_prewarm_future_rows',
             '_h69_install_song_fragment_atlas','_h69_make_history_line','_h69_activate_runtime'):
    fn(name)

# Same row must never become optically sharper even if an upstream planner/fallback retargets lower.
vals=iter((0.62,0.41,0.70,0.66,0.94))
class R: pass
r=R(); r.exit_effect='blur_decay'; r._h62_owner_ref=None; r._h65_capacity_progress=0.0
ns={
    '_h69_h68_progress_pre':lambda row,now=None:next(vals),
    '_h66_is_blur_decay_row':lambda row:True,
    'H69_PROGRESS_REGRESSION_EPS':0.002,'H69_REGRESSION_LOG_MS':1600.0,
    'time':time,'write_error_log':lambda *a,**k:None,
}
exec(fsrc('_h69_monotonic_decay_progress'),ns)
out=[ns['_h69_monotonic_decay_progress'](r,1000+i) for i in range(5)]
expected=(0.62,0.62,0.70,0.70,0.94)
if any(abs(a-b)>1e-9 for a,b in zip(out,expected)):
    fail(f'per-row optical progress regressed: {out}')
if abs(float(getattr(r,'_h65_capacity_progress',0))-0.94)>1e-9:
    fail('visible monotonic floor was not reflected into upstream capacity state')

sched=fsrc('_h69_schedule_decay_atlases')
mid_emit=sched.find("_emit('mid', mid")
max_filter=sched.find('int(H62_BLUR_MAX_LEVELS)')
if mid_emit < 0 or max_filter < 0 or not (mid_emit < max_filter):
    fail('mid blur is still withheld until after max blur work')
for tok in ("'h69_progressive_stage': stage_name", 'H69_BLUR_MAX_TOTAL_BUDGET_MS', 'LimbusLyric-H69BlurStages'):
    if tok not in sched: fail('progressive blur worker missing '+tok)

# Late H61 row material must be adopted by already-resident history/fading rows, then requeue blur.
install=fsrc('_h69_install_song_fragment_atlas')
for tok in ("payload.get('h61_row_fallback')", "getattr(window, 'history_lines'", "getattr(window, 'fading_lines'",
            "row._shared_fragment_atlas = shared", '_h62_queue_decay_build(row)', '_h69_prewarm_future_rows(window)'):
    if tok not in install: fail('late material adoption/prewarm missing '+tok)
prewarm=fsrc('_h69_prewarm_future_rows')
for tok in ('H69_FUTURE_ROW_PREWARM', '_h61_schedule_row_atlas(window, text)', "getattr(window, 'lyric_timeline'"):
    if tok not in prewarm: fail('future row prewarm missing '+tok)

# Wrap topology must be based on stable geometry. Shake remains in actual draw positions, but not
# in the local rect/baseline fed into _device_space_staggered_wrap_adjust.
for bad in ('ox + sx + float(br.left()), oy + sy + th / 3.0 + float(br.top())',
            'baseline_x = float(ox) + float(sx) + fx_dx',
            'baseline_y = float(oy) + float(sy) + fx_dy + float(th) / 3.0'):
    if bad in src: fail('shake still controls wrap topology: '+bad)
if src.count('baseline_x = float(ox) + fx_dx') < 3:
    fail('active-row stable wrap baseline not applied to every draw lane')
if src.count('ox + float(br.left()), oy + th / 3.0 + float(br.top())') < 5:
    fail('history/fading stable wrap rect not applied to every draw lane')
# Ensure shake was not disabled as a workaround; it must still affect the final glyph position.
if src.count('ox + sx') < 5 or src.count('oy + sy') < 5:
    fail('shake appears to have been removed from actual drawing')

activate=fsrc('_h69_activate_runtime')
for tok in ('_h62_decay_progress = _h69_monotonic_decay_progress',
            '_h62_schedule_decay_atlases = _h69_schedule_decay_atlases',
            'LyricWindow._install_song_fragment_atlas = _h69_install_song_fragment_atlas',
            'LyricWindow._make_history_line = _h69_make_history_line'):
    if tok not in activate: fail('runtime hook missing '+tok)

block=src[src.index('# H69 optical continuity + edge-wrap stability'):]
if '# H70 per-effect exit profiles + optional flavor layer' in block:
    block=block[:block.index('# H70 per-effect exit profiles + optional flavor layer')]
else:
    block=block[:block.index('if __name__ == "__main__":')]
for bad in ('MediaSessionSync.', 'ControlPanel.', 'LyricSearchEngine.', '_commit_seek', '_on_seek', 'win32gui.'):
    if bad in block: fail('H69 crossed presentation-only authority boundary: '+bad)

print('OPTICAL CONTINUITY EDGE STABILITY H69 REPLAY: PASS')
print(' - per-row visible blur progress is monotonic across H68 retarget/fallback transitions')
print(' - mid blur publishes before max blur finishes, and late H61 row material is adopted')
print(' - fused song-atlas mode prewarms a bounded future lyric window')
print(' - random shake remains visual-only and cannot flip horizontal wrap topology')
