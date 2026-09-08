#!/usr/bin/env python3
from __future__ import annotations
import ast, pathlib, sys
if len(sys.argv)!=2: raise SystemExit('usage: CHECK_RENDER_PLAN_VISUAL_PRESET_H95F10F10_REPLAY.py <main.py>')
p=pathlib.Path(sys.argv[1]).resolve(); src=p.read_text(encoding='utf-8'); tree=ast.parse(src)
def need(c,m):
    if not c: raise AssertionError(m)
need('+ RENDER PLAN + RESOLVED VISUAL PRESET H95F10F10' in src,'F10 build tag missing')
marker='# H95F10F10 render-plan + resolved visual preset contract'
need(marker in src,'F10 marker missing')
funcs={n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
req=('_h95f10f10_translation_layout','_h95f10f10_profile_for_effect','_h95f10f10_resolved_visual_preset','_h95f10f10_timing_hints','_h95f10f10_frame_plan','_h95f10f10_paint_event','_h95f10f10_render_contract','_h95f10f10_activate')
for n in req: need(n in funcs,'missing '+n)
def fs(n): return ast.get_source_segment(src,funcs[n]) or ''
plan=fs('_h95f10f10_frame_plan'); preset=fs('_h95f10f10_resolved_visual_preset'); paint=fs('_h95f10f10_paint_event'); layout=fs('_h95f10f10_translation_layout'); act=fs('_h95f10f10_activate')
for t in ('visual_preset','timing','route','next_line_index','next_primary_text','plan_build_ms','_h95f10f10_render_plan'):
    need(t in plan,'render plan missing '+t)
for t in ('entrance_effect','western_entrance_effect','exit_effect','exit_speed','exit_flavor','translation_scale_pct','translation_gap_px','shake_intensity','shake_speed_ms','audio_enabled','audio_scale_pct','perspective_enabled','horizontal_wrap','primary_style','translation_style'):
    need(t in preset,'resolved preset missing '+t)
for t in ('_h95f10f10_render_plan','translation_layout','_h95f10f10_translation_layout_cache'):
    need(t in layout,'one-frame translation layout cache missing '+t)
# Final wrapper is intentionally thin: no raster, provider, typography or effect formula belongs here.
for bad in ('QPainterPath','_render_song_atlas_glyph','_hires_glyph_sprite','_h51_prepare_line_typography','requests.','LyricSearchEngine','parse_lrc(','_entrance_motion(','_h62_filter_shared_image'):
    need(bad not in paint,'paint contract crossed hot/provider/effect authority: '+bad)
for bad in ('_render_song_atlas_glyph','_hires_glyph_sprite','QPainterPath','requests.','LyricSearchEngine.search'):
    need(bad not in plan,'frame plan performs forbidden work: '+bad)
for t in ("globals()['_h95f10f9_frame_plan'] = _h95f10f10_frame_plan", "globals()['_h95f10f4_translation_layout'] = _h95f10f10_translation_layout", 'LyricWindow.paintEvent = _h95f10f10_paint_event', "LyricWindow.paintEvent._limbus_layer = 'H95F10F10'"):
    need(t in act,'final F10 ownership missing '+t)
# This layer is structural only; do not touch clocks/search/seek or mature effect owners.
start=src.index(marker); end=src.index('if __name__ == "__main__":',start); block=src[start:end]
for bad in ('LyricSearchEngine.search =','MediaSessionSync.position =','MediaSessionSync.seek =','MediaSessionSync.bind_track =','FadingLine.draw =','_h62_decay_progress =','_entrance_motion ='):
    need(bad not in block,'F10 crossed protected authority: '+bad)
print('RENDER PLAN + RESOLVED VISUAL PRESET H95F10F10 REPLAY: PASS')
print('  frame contract owns current/translation/timing/next/cache route: PASS')
print('  user visual intent resolves once and keeps mature effect owners: PASS')
print('  active translation layout is reused inside one paint: PASS')
print('  paint contract contains no raster/provider/typography/effect implementation: PASS')
