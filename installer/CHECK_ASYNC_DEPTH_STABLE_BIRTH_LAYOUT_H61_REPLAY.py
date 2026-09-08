from pathlib import Path
import ast, sys, math, random, hashlib

if len(sys.argv) < 2:
    raise SystemExit('usage: CHECK_ASYNC_DEPTH_STABLE_BIRTH_LAYOUT_H61_REPLAY.py <main.py>')
path=Path(sys.argv[1]); src=path.read_text(encoding='utf-8'); tree=ast.parse(src); lines=src.splitlines()

def fail(msg): raise SystemExit('H61 FAIL: '+msg)
def need(tok, why):
    if tok not in src: fail(f'{why}: missing {tok!r}')
def fn(name):
    for node in ast.walk(tree):
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name==name: return node
    fail('function not found: '+name)
def fsrc(name):
    n=fn(name); return '\n'.join(lines[n.lineno-1:n.end_lineno])

need('+ ASYNC DEPTH FALLBACK + STABLE BIRTH LAYOUT H61','build tag')
need("if '_h61_activate_runtime' in globals():",'final activation')
if not (src.index("if '_h60_activate_runtime' in globals():") < src.index("if '_h61_activate_runtime' in globals():")):
    fail('H61 must activate after H60')

# The H60 row fallback may remain for historical replay, but the final H61 shared-Atlas
# callback must never build/rasterize synchronously from paint.
shared=fsrc('h61_shared_song_fragment_atlas')
for bad in ('_h60_build_line_shared(', '_render_song_atlas_glyph(', '_build_song_fragment_atlas_image('):
    if bad in shared: fail('paint-time shared Atlas still performs raster work: '+bad)
for tok in ('_h61_schedule_row_atlas(window, text)', '_h61_current_row_shared',
            'H61_ROW_EARLY_COMMIT_MS', '_h61_current_row_sharp_locked'):
    if tok not in shared: fail('async/frozen row material routing missing '+tok)

worker=fsrc('_h61_kick_row_worker')
for tok in ("threading.Thread(target=worker, name='LimbusLyric-H61RowAtlas', daemon=True).start()",
            '_build_song_fragment_atlas_image(style_sig, chars, cancel_check=cancel_check)',
            'window.song_fragment_atlas_ready.emit(payload)', 'H61_ROW_WORKER_BUDGET_MS'):
    if tok not in worker: fail('row Atlas worker missing '+tok)
install=fsrc('h61_install_song_fragment_atlas')
for tok in ("payload.get('h61_row_fallback')", 'QPixmap.fromImage(image)',
            '_h61_cache_row_shared(window, key, shared)', 'gui_build=0'):
    if tok not in install: fail('queued GUI install/cache missing '+tok)

# A measured paint emergency is transient. The old build-budget fuse remains unchanged.
arm=fsrc('h61_arm_render_emergency'); active=fsrc('h61_render_emergency_active')
for tok in ('H61_EMERGENCY_BASE_RECOVERY_MS', '_h61_hard_emergency_until', 'paint-hard-budget'):
    if tok not in arm+active: fail('bounded paint emergency missing '+tok)
for tok in ("window._limbus_render_emergency_fused = False", 'H61硬渲染降级自动恢复',
            '_limbus_restore_visual_timer_cadence(window)'):
    if tok not in active: fail('automatic presentation recovery missing '+tok)
if 'SONG_FRAGMENT_ATLAS_BUILD_BUDGET_MS =' in '\n'.join([shared,worker,install,arm,active]):
    fail('H61 must not weaken the established full-song Atlas fuse')

# Center avoidance is birth-only. Existing rows are obstacles, never mutation targets.
place=fsrc('_h61_stable_birth_place'); score=fsrc('_h61_candidate_center_score'); points=fsrc('_h61_poisson_points')
for tok in ('_h61_poisson_points(window)', '_h61_candidate_center_score(', 'existing_rows=immutable',
            'window._placement_obstacles()', '_placement_recent'):
    if tok not in place: fail('stable birth placement missing '+tok)
for bad in ('history_lines[', 'fading_lines[', '.x +=', '.y +='):
    if bad in place: fail('birth placer appears to mutate existing rows: '+bad)
for tok in ('vertical_out > 0.5', 'corridor_overlap > float(H61_CENTER_EPS)',
            '_placement_max_overlap', 'return None'):
    if tok not in score: fail('hard visibility/center collision constraint missing '+tok)
for tok in ('min_dist', 'grid', 'active', 'H61_CENTER_POINT_COUNT', 'random.Random'):
    if tok not in points: fail('deterministic blue-noise candidate generator missing '+tok)

# The outer final placement method must be H61, not H59/H60 post-push.
activate=fsrc('_h61_activate_runtime')
for tok in ("LyricWindow.place_randomly = h61_place_randomly",
            "LyricWindow.place_randomly._limbus_layer = 'H61'",
            'birth-only-blue-noise-greedy-center-safe-existing-rows-immutable'):
    if tok not in activate: fail('final placement authority missing '+tok)
if "globals()['_h59_center_quota_allows'] = lambda _w, _f: True" not in place:
    fail('H59 post-push bypass is missing from H61 birth placement')

# Pure quota replay: 0 never admits; 100 always admits; 15% does not cluster.
quota_src=fsrc('_h61_center_quota_allows')
ns={}
exec(quota_src, ns)
q=ns['_h61_center_quota_allows']
class W: pass
w=W()
if any(q(w,0) for _ in range(20)): fail('0% quota admitted center')
if not all(q(w,100) for _ in range(20)): fail('100% quota rejected center')
w=W(); seq=[q(w,15) for _ in range(20)]
# 15% accumulator should produce exactly 3 admissions in 20 rows, never adjacent.
if sum(seq) != 3: fail(f'15% quota count unexpected: {sum(seq)} seq={seq}')
if any(seq[i] and seq[i+1] for i in range(len(seq)-1)): fail('15% quota clustered adjacent center admissions')

# Presentation boundary.
block='\n'.join(fsrc(n) for n in (
    '_h61_row_key','_h61_kick_row_worker','_h61_schedule_row_atlas',
    '_h61_poisson_points','_h61_candidate_center_score','_h61_stable_birth_place','_h61_activate_runtime'))
for bad in ('MediaSessionSync.', '_poll_loop', 'requests.', 'urllib.', 'win32com'):
    if bad in block: fail('presentation boundary crossed: '+bad)

print('ASYNC DEPTH + STABLE BIRTH LAYOUT H61 REPLAY: PASS')
print(' - row-local styled Atlas rasterization is off the paint path and installed through Qt queued signal')
print(' - one hard-paint emergency is time-bounded; normal outline/glow/depth/history presentation can recover')
print(' - center avoidance uses deterministic blue-noise candidates and one birth-time greedy commit')
print(' - existing subtitles are read-only obstacles and 0% center quota never admits the protected region')
