#!/usr/bin/env python3
from __future__ import annotations
import ast, copy, pathlib, sys
if len(sys.argv)!=2: raise SystemExit('usage: CHECK_RUNTIME_OWNERSHIP_CONSOLIDATION_H95F10F9_REPLAY.py <main.py>')
p=pathlib.Path(sys.argv[1]).resolve(); src=p.read_text(encoding='utf-8'); tree=ast.parse(src)
def need(c,m):
    if not c: raise AssertionError(m)
need('+ RUNTIME OWNERSHIP CONSOLIDATION H95F10F9' in src,'H95F10F9 build tag missing')
marker='# H95F10F9 runtime ownership consolidation + neighbor prewarm'
need(marker in src,'H95F10F9 marker missing')
funcs={n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
required=(
 '_h95f10f9_line_index','_h95f10f9_translation_for_line','_h95f10f9_h95f7_paint_event_safe',
 '_h95f10f9_frame_plan','_h95f10f9_worker_loop','_h95f10f9_ensure_worker','_h95f10f9_enqueue_missing',
 '_h95f10f9_resolve_idle_style','_h95f10f9_neighbor_prewarm','_h95f10f9_schedule_plan',
 '_h95f10f9_install_song_fragment_atlas','_h95f10f9_paint_event','_h95f10f9_translation_prewarm','_h95f10f9_activate')
for name in required: need(name in funcs,'missing '+name)
def fs(name): return ast.get_source_segment(src,funcs[name]) or ''

# Line zero is a real row, not falsy "missing".
node=copy.deepcopy(funcs['_h95f10f9_line_index']); node.decorator_list=[]
ns={}; exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),'<f9-index>','exec'),ns)
class W: displayed_line_index=0
need(ns['_h95f10f9_line_index'](W())==0,'line zero regressed to -1')

# One render-input plan owns the F8 cache/style/translation lookups; final paint must not invoke
# the old double-scan F8 helpers. Any visible miss, even one glyph, selects the cheap fallback.
plan=fs('_h95f10f9_frame_plan'); paint=fs('_h95f10f9_paint_event')
for t in ('primary_missing','translation_missing','primary_visible_missing','translation_visible_missing','_h95f10f9_cold_token'):
    need(t in plan,'frame plan missing '+t)
need('p_visible_missing >= 1 or t_visible_missing >= 1' in plan,'single-glyph cold guard missing')
for bad in ('_h95f10f8_schedule_visible_prewarm','_h95f10f8_cold_cache_state','_render_song_atlas_glyph','_hires_glyph_sprite(','QPainterPath','QPixmap.fromImage'):
    need(bad not in paint,'final paint regressed hot path: '+bad)
for t in ('_h95f10f9_frame_plan','_h95f10f9_schedule_plan','_limbus_plain_glyph_paint','_H95F10F8_PAINT_PRE'):
    need(t in paint,'final frame route missing '+t)

# Prewarm is a single long-lived worker. Enqueue never creates a thread, and work is superseded
# by per-window/lane tokens. Neighbour work is lower priority and resolved outside paint.
ensure=fs('_h95f10f9_ensure_worker'); enqueue=fs('_h95f10f9_enqueue_missing'); loop=fs('_h95f10f9_worker_loop'); neighbor=fs('_h95f10f9_neighbor_prewarm'); schedule=fs('_h95f10f9_schedule_plan')
need('threading.Thread' in ensure and 'LimbusLyric-H95F10F9-Prewarm' in ensure,'single worker bootstrap missing')
need('threading.Thread' not in enqueue,'enqueue still spawns per-job threads')
for t in ('_H95F10F9_PREWARM_LATEST','_H95F10F9_GLYPH_PENDING','work_token','cancelled','_render_song_atlas_glyph'):
    need(t in loop,'stale-cancellable worker missing '+t)
need('_H95F10F9_GLYPH_PENDING' in enqueue and '_HIRES_GLYPH_SPRITE_CACHE' in enqueue,'cross-lane glyph dedup missing')
for t in ('+ 1','next-primary','next-translation','_h95f10f9_resolve_idle_style'):
    need(t in neighbor,'next-line prewarm missing '+t)
need('QTimer.singleShot' in schedule,'neighbor prewarm is not GUI-idle scheduled')
need('_h51_prepare_line_typography' not in paint,'typography resolve moved back into paint')

# H95F7 legacy suppression is window-local. The final H95F8 predecessor edge is rebound once at
# activation; no per-paint process-global lookup replacement is allowed.
safe=fs('_h95f10f9_h95f7_paint_event_safe'); lookup=fs('_h95f10f9_translation_for_line'); activate=fs('_h95f10f9_activate')
for t in ('_h95f10f9_suppress_legacy_translation','_H95F7_PAINT_PRE','_h95f7_draw_active_translation'):
    need(t in safe,'safe H95F7 bridge missing '+t)
for bad in ("globals()['_h95f5_translation_for_line']=lambda", 'saved_lookup'):
    need(bad not in safe,'per-paint global translation mutation survived: '+bad)
need('_h95f10f9_suppress_legacy_translation' in lookup,'window-local suppression not owned by final lookup')
for t in ("globals()['_h95f5_translation_for_line'] = _h95f10f9_translation_for_line", "globals()['_H95F8_PAINT_PRE'] = _h95f10f9_h95f7_paint_event_safe", 'LyricWindow.paintEvent = _h95f10f9_paint_event', 'LyricWindow._install_song_fragment_atlas = _h95f10f9_install_song_fragment_atlas'):
    need(t in activate,'final F9 ownership missing '+t)

# Protected authority remains outside this consolidation layer.
start=src.index(marker); end=src.index('if __name__ == "__main__":',start); block=src[start:end]
for bad in ('LyricSearchEngine.search =','MediaSessionSync.position =','MediaSessionSync.seek =','MediaSessionSync.bind_track =','parse_lrc =','_entrance_motion =','FadingLine.draw ='):
    need(bad not in block,'F9 crossed protected/provider/effect authority: '+bad)
print('RUNTIME OWNERSHIP CONSOLIDATION H95F10F9 REPLAY: PASS')
print('  one frame-plan; one visible missing glyph triggers cold guard: PASS')
print('  single stale-cancellable prewarm worker + idle next-line prewarm: PASS')
print('  final H95F7 translation suppression is window-local, not process-global per paint: PASS')
print('  provider/search/transport/effect formulas unchanged: PASS')
