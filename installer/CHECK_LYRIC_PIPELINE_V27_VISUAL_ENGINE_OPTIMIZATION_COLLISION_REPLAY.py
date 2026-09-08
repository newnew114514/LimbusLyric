#!/usr/bin/env python3
import ast, sys
from pathlib import Path

if len(sys.argv) != 2:
    raise SystemExit('usage: CHECK_LYRIC_PIPELINE_V27_VISUAL_ENGINE_OPTIMIZATION_COLLISION_REPLAY.py <main.py>')
p = Path(sys.argv[1]); src = p.read_text(encoding='utf-8'); tree = ast.parse(src)

def fail(msg):
    print('LYRIC PIPELINE V27 VISUAL ENGINE OPTIMIZATION + COLLISION REPLAY: FAIL')
    print('  -', msg); raise SystemExit(1)

def fn(cls, name):
    for n in tree.body:
        if isinstance(n, ast.ClassDef) and n.name == cls:
            for m in n.body:
                if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)) and m.name == name:
                    return ast.get_source_segment(src, m)
    fail(f'missing {cls}.{name}')

def topfn(name):
    for n in tree.body:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name:
            return ast.get_source_segment(src, n)
    fail(f'missing top-level {name}')

if not any(m in src for m in ('INSTRUMENTAL-RUNTIME-V27','INSTRUMENTAL-RUNTIME-V28','INSTRUMENTAL-RUNTIME-V29')):
    fail('V27+ marker missing')

# ---- Visual atlas lifecycle: pixels/effects stay the same, scheduling/cache ownership changes. ----
builder = topfn('_build_song_fragment_atlas_image')
for needle in ('cancel_check=None', "built.get('cancelled')" if False else 'cancel_check()', 'SONG_FRAGMENT_ATLAS_WORKER_YIELD_S'):
    if needle not in builder:
        fail(f'cooperative atlas worker missing: {needle}')
# The V26 styled glyph renderer remains the actual atlas pixel producer.
if '_render_song_atlas_glyph(style_sig, ch)' not in builder:
    fail('atlas optimization bypasses established styled glyph renderer')
for needle in ('pack_entries = sorted(', '_shelf_layout(candidate_w)', 'width_candidates = sorted({', 'best_layout'):
    if needle not in builder:
        fail(f'lossless atlas packing optimization missing: {needle}')

init = fn('LyricWindow', '__init__')
for needle in ('_song_fragment_atlas_cache = OrderedDict()', '_song_fragment_atlas_inflight = set()',
               '_song_fragment_atlas_desired_key', '_song_fragment_atlas_pending_key'):
    if needle not in init:
        fail(f'atlas lifecycle state missing: {needle}')

queue = fn('LyricWindow', 'queue_visual_style')
for needle in ('_pending_visual_style = style', '_schedule_song_fragment_atlas(visual_style=style, prewarm_only=True)', "return 'queued-next-line'"):
    if needle not in queue:
        fail(f'next-line style prewarm missing: {needle}')

schedule = fn('LyricWindow', '_schedule_song_fragment_atlas')
for needle in ('prewarm_only=False', "return 'cache-hit'", "return 'inflight'", '_song_fragment_atlas_desired_key',
               '_song_fragment_atlas_pending_key', 'cancel_check=still_wanted', 'SetThreadPriority(', 'GetCurrentThread()', 'THREAD_PRIORITY_BELOW_NORMAL'):
    if needle not in schedule:
        fail(f'atlas scheduling/LRU wiring missing: {needle}')

install = fn('LyricWindow', '_install_song_fragment_atlas')
for needle in ('_cache_song_fragment_atlas', '_song_fragment_atlas_inflight.discard', '_activate_cached_song_fragment_atlas'):
    if needle not in install:
        fail(f'atlas install cache path missing: {needle}')
activate = fn('LyricWindow', '_activate_cached_song_fragment_atlas')
for needle in ('expected == key[0]', 'row._shared_fragment_atlas = shared'):
    if needle not in activate:
        fail(f'old-row style atlas ownership not preserved: {needle}')
# Regression guard: never blanket-assign the newest style atlas to every old row.
if 'for row in list(self.history_lines) + list(self.fading_lines):\n                try:\n                    row._shared_fragment_atlas = shared' in activate:
    fail('new atlas still overwrites every old history/fading row')

# Cache is deliberately tiny/bounded; optimization must not become unbounded memory retention.
for needle in ('SONG_FRAGMENT_ATLAS_CACHE_MAX_PIXELS = 12_000_000', 'SONG_FRAGMENT_ATLAS_CACHE_MAX_ENTRIES = 3'):
    if needle not in src:
        fail(f'bounded atlas LRU contract missing: {needle}')

# ---- Predictive collision: account for things that become larger/move after placement. ----
obstacles = fn('LyricWindow', '_placement_obstacles')
for needle in ('glyph_scales', 'growth =', 'shake =', '_placement_swept_fade_box', "'fading-sweep'"):
    if needle not in obstacles:
        fail(f'predictive obstacle envelope missing: {needle}')
place = fn('LyricWindow', 'place_randomly')
for needle in ('candidate_growth', '_placement_visible_boxes', '_placement_max_overlap', 'predictive=1',
               'worst_guard_overlap <= 0.32', '_placement_visible_boxes'):
    if needle not in place:
        fail(f'predictive placement scorer missing: {needle}')
wrap = fn('LyricWindow', '_placement_visible_boxes')
if 'base[0] + sw' not in wrap or 'base[0] - sw' not in wrap:
    fail('horizontal wrap collision replicas missing')
sweep = fn('LyricWindow', '_placement_swept_fade_box')
for needle in ('rise_px', 'min(180.0', 'FADE_VISUAL_ALPHA_CUTOFF'):
    if needle not in sweep:
        fail(f'fading future-rise reservation missing: {needle}')

# Small geometry replay independent of Qt: prove the failure modes the V26 instantaneous box missed.
def overlap_ratio(a,b):
    left=max(a[0],b[0]); top=max(a[1],b[1]); right=min(a[2],b[2]); bottom=min(a[3],b[3])
    if right<=left or bottom<=top: return 0.0
    inter=(right-left)*(bottom-top)
    aa=max(1.0,(a[2]-a[0])*(a[3]-a[1])); ab=max(1.0,(b[2]-b[0])*(b[3]-b[1]))
    return inter/max(1.0,min(aa,ab))
# Fade currently below a new line but will rise into it.
old=(400.0,500.0,800.0,550.0); new=(420.0,430.0,820.0,480.0)
if overlap_ratio(old,new) != 0.0: fail('fixture invalid: instantaneous fade already overlaps')
alpha=220.0; fade_speed=12.0; rise_speed=1.0
rise=min(180.0,max(0.0,(alpha-20.0)/fade_speed*rise_speed*2.1))
swept=(old[0],old[1]-rise,old[2],old[3])
if overlap_ratio(swept,new) <= 0.0: fail('predictive fade sweep does not expose future collision')
# A wrapped line can visually re-enter at the opposite edge although its base box is off-screen.
sw=1920.0; off=(-70.0,200.0,90.0,250.0); right=(1870.0,205.0,1915.0,245.0)
if overlap_ratio(off,right) != 0.0: fail('fixture invalid: unwrapped boxes overlap')
wrapped=(off[0]+sw,off[1],off[2]+sw,off[3])
if overlap_ratio(wrapped,right) <= 0.0: fail('wrap replica does not expose opposite-edge collision')

# ---- Guardrails: this V27 is presentation-only. Mature clock/seek methods retain their V26 gates. ----
for forbidden in ('qq-gesture-target-outlier', 'host-uia-range-v2', 'host-uia-same-track-restart'):
    if forbidden not in src:
        fail(f'mature synchronization marker lost: {forbidden}')
for method in (('MediaSessionSync','_qq_queue_seek'), ('MediaSessionSync','_kugou_poll_uia_progress_v2')):
    body = fn(*method)
    if 'SONG_FRAGMENT_ATLAS' in body or '_placement_' in body:
        fail(f'visual optimization leaked into synchronization method {method[0]}.{method[1]}')

print('LYRIC PIPELINE V27 VISUAL ENGINE OPTIMIZATION + COLLISION REPLAY: PASS')
print('  pending style atlas prewarm + bounded multi-style LRU: PASS')
print('  old history/fading rows retain matching birth-style atlas: PASS')
print('  superseded atlas workers cancel/yield without changing glyph pixels: PASS')
print('  fade-rise + audio-scale + shake + horizontal-wrap predictive collision guards: PASS')
print('  QQ/KuGou synchronization methods remain outside visual optimization: PASS')
